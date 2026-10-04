"""Paso 8: preguntas libres externas por los cuatro sistemas.

Uso: python 08_preguntas_libres.py preguntas_libres.yaml [--systems baseline,vecrel,graphrag,t2c]
     (también .csv o .jsonl; formato en README.md, sección «Preguntas libres»)

Para cada pregunta ejecuta RAG vectorial, vectorial + relaciones, GraphRAG
(mismo código, prompt y modelo que 04_answer.py) y text-to-Cypher (t2c y
t2c_directo). Si la pregunta trae `gold` o `gold_cypher`, la puntúa con
score() de 05_evaluate.py (tipo «L»: lista de plugins, F1 de citas).
Sin gold, solo guarda las respuestas para revisión manual.

Salida: results/libres/<nombre del fichero>/
  gold_resuelto.jsonl (+ .sha256)   preguntas con el gold ya calculado
  answers_<sistema>.jsonl           respuestas en el formato de 04_answer.py
  metrics.md, metrics_per_question.csv
Las respuestas del LLM (los cuatro sistemas) se cachean en cache/llm_libres/
y los embeddings de consulta en cache/qemb_libres/ (uso en
cache/usage_libres.jsonl), para no tocar la caché del experimento T1-T6.
"""
import csv
import hashlib
import importlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

import config as C

# caché separada (config.generate / embed_query leen estas globales en cada llamada)
C.LLM_CACHE = C.CACHE / "llm_libres"
C.QEMB_CACHE = C.CACHE / "qemb_libres"
C.USAGE_LOG = C.CACHE / "usage_libres.jsonl"
for _d in (C.LLM_CACHE, C.QEMB_CACHE):
    _d.mkdir(parents=True, exist_ok=True)

import text2cypher as T  # noqa: E402
T.T2C_CACHE = C.CACHE / "llm_libres"
T.T2C_USAGE = C.CACHE / "usage_libres.jsonl"
from retrieval import Retriever  # noqa: E402

ans04 = importlib.import_module("04_answer")
ev = importlib.import_module("05_evaluate")
ALL = ("baseline", "vecrel", "graphrag", "t2c")
LABEL = {**ev.SYS_LABEL, "t2c": "text-to-Cypher", "t2c_directo": "text-to-Cypher (filas directas)"}


def _list(v):
    if v is None or v == "":
        return None
    if isinstance(v, list):
        return [str(x).strip() for x in v if str(x).strip()]
    return [x.strip() for x in str(v).replace(";", ",").split(",") if x.strip()]


def load_questions(path):
    p = Path(path)
    if p.suffix in (".yaml", ".yml"):
        raw = yaml.safe_load(p.read_text()) or []
        if isinstance(raw, dict):
            raw = raw.get("preguntas") or []
    elif p.suffix == ".csv":
        with p.open(newline="") as f:
            raw = list(csv.DictReader(f))
    elif p.suffix == ".jsonl":
        raw = [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
    else:
        sys.exit(f"formato no soportado: {p.suffix} (usa .yaml, .csv o .jsonl)")
    out = []
    for i, r in enumerate(raw, 1):
        q = (r.get("pregunta") or r.get("question") or "").strip()
        if not q:
            continue
        out.append({"id": str(r.get("id") or f"L{i:02d}"), "type": "L", "question": q,
                    "seed": (r.get("seed") or r.get("plugin") or None),
                    "gold": _list(r.get("gold")),
                    "gold_cypher": (r.get("gold_cypher") or "").strip() or None,
                    "autor": r.get("autor"), "notas": r.get("notas")})
    ids = [q["id"] for q in out]
    assert len(ids) == len(set(ids)), f"ids repetidos: {ids}"
    return out


def resolve_gold(qs, drv, components):
    """gold explícito tiene prioridad; si solo hay gold_cypher se ejecuta en
    modo solo lectura y se toman los components de las filas."""
    for q in qs:
        if q["gold_cypher"]:
            why = T.check(q["gold_cypher"])
            if why:
                sys.exit(f"{q['id']}: gold_cypher rechazada ({why})")
            rows, _, trunc = T.execute(drv, q["gold_cypher"])
            assert not trunc, f"{q['id']}: gold_cypher devuelve más de {T.MAX_ROWS} filas"
            from_cypher = sorted(set(T.components_in(rows, components)))
            if q["gold"] is None:
                q["gold"], q["gold_source"] = from_cypher, "gold_cypher"
            else:
                q["gold_source"] = "explícito"
                if set(q["gold"]) != set(from_cypher):
                    print(f"AVISO {q['id']}: gold explícito ≠ gold_cypher; se usa el explícito")
        elif q["gold"] is not None:
            q["gold_source"] = "explícito"
        if q["gold"] is not None:
            bad = [c for c in q["gold"] if c not in components]
            assert not bad, f"{q['id']}: components de gold inexistentes en el grafo: {bad}"
            if q["seed"]:
                q["gold"] = [c for c in q["gold"] if c != q["seed"]]
    return qs


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    path = Path(sys.argv[1])
    systems = ALL
    if "--systems" in sys.argv:
        systems = tuple(sys.argv[sys.argv.index("--systems") + 1].split(","))
    qs = load_questions(path)
    if not qs:
        print(f"{path}: no hay preguntas (solo comentarios). Nada que hacer.")
        return
    out = C.RESULTS / "libres" / path.stem
    out.mkdir(parents=True, exist_ok=True)
    R = Retriever()
    t2c = T.Text2Cypher(R.drv) if "t2c" in systems else None
    try:
        qs = resolve_gold(qs, R.drv, R.components)
        g = out / "gold_resuelto.jsonl"
        g.write_text("".join(json.dumps(q, ensure_ascii=False) + "\n" for q in qs))
        (out / "gold_resuelto.sha256").write_text(
            f"{hashlib.sha256(g.read_bytes()).hexdigest()}  gold_resuelto.jsonl\n")
        files = {s: (out / f"answers_{s}.jsonl").open("w")
                 for s in systems if s != "t2c"}
        if t2c:
            files["t2c"] = (out / "answers_t2c.jsonl").open("w")
            files["t2c_directo"] = (out / "answers_t2c_directo.jsonl").open("w")
        fetch = {"baseline": R.baseline, "graphrag": R.graphrag, "vecrel": R.vector_rel}
        for q in qs:
            head = {"id": q["id"], "type": "L"}
            for s in systems:
                if s == "t2c":
                    for rec in t2c.answer(q["question"]):
                        files[rec["system"]].write(json.dumps({**head, **rec}, ensure_ascii=False,
                                                              default=str) + "\n")
                    continue
                ret = fetch[s](q["question"])
                ctx = R.context(ret)
                resp = C.generate(ans04.SYSTEM, ans04.TEMPLATE.format(ctx=ctx, q=q["question"]))
                files[s].write(json.dumps({**head, "system": s, "question": q["question"], **ret,
                                           "context_chars": len(ctx), "answer": resp["text"],
                                           "finish_reason": resp["finish_reason"],
                                           "model": resp["model"],
                                           "model_version": resp["model_version"],
                                           "usage": resp["usage"]}, ensure_ascii=False) + "\n")
            print(f"{q['id']}: hecho", flush=True)
        for f in files.values():
            f.close()
    finally:
        R.close()
    report(out, qs, R.components, list(files))


def report(out, qs, components, systems):
    gold = {q["id"]: q for q in qs}
    rows, usages = [], {s: [] for s in systems}
    for s in systems:
        for line in (out / f"answers_{s}.jsonl").read_text().splitlines():
            a = json.loads(line)
            usages[s] += a.get("usage_gen", []) + [a.get("usage") or {}]
            q = gold[a["id"]]
            if q["gold"] is None:
                continue
            r = ev.score(q, a, components)
            if s.startswith("t2c"):
                r["status"] = a["status"]
            rows.append(r)
    L = [f"# Preguntas libres — `{out.name}`", "",
         f"{len(qs)} preguntas; con gold: {sum(q['gold'] is not None for q in qs)} "
         f"(explícito {sum(q.get('gold_source') == 'explícito' for q in qs)}, "
         f"por `gold_cypher` {sum(q.get('gold_source') == 'gold_cypher' for q in qs)}). "
         f"Scorer: `score()` de `05_evaluate.py`; modelo `{C.GEN_MODEL}`.", ""]
    if rows:
        df = pd.DataFrame(rows)
        df.to_csv(out / "metrics_per_question.csv", index=False)
        L += ["| Sistema | n | F1 citas | Precisión | Recall | Recall contexto | Fidelidad (n def.) | Sin citas |",
              "|---|---|---|---|---|---|---|---|"]
        for s in systems:
            g = df[df.system == s]
            L.append(f"| {LABEL[s]} | {len(g)} | {ev.fmt(g.f1.mean())} | {ev.fmt(g.precision.mean())} | "
                     f"{ev.fmt(g.recall.mean())} | {ev.fmt(g.recall_at_k.mean())} | "
                     f"{ev.fmt(g.faithfulness.mean())} ({int(g.faithfulness.notna().sum())}) | "
                     f"{int(g.no_citations.sum())} |")
        if "t2c" in systems:
            st = df[df.system == "t2c"].status.value_counts().to_dict()
            L += ["", "Estado de las consultas text-to-Cypher (preguntas con gold): " +
                  ", ".join(f"{k} {v}" for k, v in st.items())]
        L += ["", "Por pregunta: `metrics_per_question.csv`."]
    else:
        L.append("Ninguna pregunta tiene gold: solo se guardan las respuestas para revisión manual.")
    L += ["", "| Sistema | Tokens entrada | Tokens salida | US$ (sin caché) |", "|---|---|---|---|"]
    for s in systems:
        if s == "t2c_directo":
            continue
        i, o, usd = T.cost(usages[s])
        L.append(f"| {LABEL[s]} | {i} | {o} | {usd:.4f} |".replace(".", ","))
    (out / "metrics.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
