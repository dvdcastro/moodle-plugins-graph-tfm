"""Paso 7: evalua text-to-Cypher junto a los tres sistemas con el MISMO scorer.

Uso: python 07_evaluate_t2c.py
Lee results/full/answers_{baseline,vecrel,graphrag}.jsonl (sin modificarlos) y
results/text2cypher/answers_{t2c,t2c_directo}.jsonl; puntua todo con
score() de 05_evaluate.py y escribe results/text2cypher/metrics.md y
metrics_per_question.csv. No toca results/full/.
"""
import hashlib
import importlib
import json
import re

import numpy as np
import pandas as pd

import config as C
import text2cypher as T

ev = importlib.import_module("05_evaluate")
OUT = C.RESULTS / "text2cypher"
SYSTEMS = ("baseline", "vecrel", "graphrag", "t2c", "t2c_directo")
LABEL = {**ev.SYS_LABEL, "t2c": "text-to-Cypher", "t2c_directo": "text-to-Cypher (filas directas)"}
SRC = {"baseline": C.RESULTS / "full", "vecrel": C.RESULTS / "full", "graphrag": C.RESULTS / "full",
       "t2c": OUT, "t2c_directo": OUT}
PAIRS = (("graphrag", "t2c"), ("baseline", "t2c"), ("vecrel", "t2c"), ("t2c", "t2c_directo"))
fmt = ev.fmt


def th(x):
    return f"{x:,}".replace(",", ".")


def usd(x):
    return f"{x:.4f}".replace(".", ",")


FLIPS = ((re.compile(r"\)-\[(\w*):MAINTAINS\]->\((\w*):Maintainer\)"), r")<-[\1:MAINTAINS]-(\2:Maintainer)"),
         (re.compile(r"\)-\[(\w*):DESCRIBES\]->\((\w*):PluginText\)"), r")<-[\1:DESCRIBES]-(\2:PluginText)"))


def flip_directions(q):
    """Diagnostico post hoc (no es un sistema): invierte las aristas MAINTAINS
    y DESCRIBES escritas al reves respecto al esquema."""
    for rx, rep in FLIPS:
        q = rx.sub(rep, q)
    return q


def direction_diagnostic(ans, gold, comps):
    """Re-ejecuta (sin LLM) las consultas con aristas invertidas tras corregir
    la direccion y puntua las filas como t2c_directo."""
    out = []
    with C.driver() as d:
        for (sy, qid), a in sorted(ans.items()):
            if sy != "t2c":
                continue
            q = a["attempts"][-1].get("cypher_run") or a["attempts"][-1]["cypher"]
            fq = flip_directions(q)
            if fq == q:
                continue
            try:
                rows, _, _ = T.execute(d, T.add_limit(fq))
                st = "ok" if rows else "empty"
            except Exception as e:  # noqa: BLE001
                rows, st = [], f"error ({type(e).__name__})"
            cs = T.components_in(rows, comps)
            fake = {"system": "flip", "components": cs, "seeds": [],
                    "answer": " ".join(f"[{c}]" for c in cs)}
            r = ev.score(gold[qid], fake, comps)
            out.append((qid, a["status"], st, len(cs), r["primary"],
                        ans[("t2c_directo", qid)] and ev.score(gold[qid], ans[("t2c_directo", qid)], comps)["primary"]))
    return out


def load_components():
    with C.driver() as d, d.session() as s:
        return {r["c"] for r in s.run("MATCH (p:Plugin) RETURN p.component AS c")}


def main():
    sha = hashlib.sha256(C.GOLD.read_bytes()).hexdigest()
    assert sha == (C.GOLD.parent / "questions.sha256").read_text().split()[0], "gold alterado"
    gold = {q["id"]: q for q in map(json.loads, C.GOLD.read_text().splitlines())}
    comps = load_components()
    rows, ans = [], {}
    for sy in SYSTEMS:
        for line in (SRC[sy] / f"answers_{sy}.jsonl").read_text().splitlines():
            a = json.loads(line)
            ans[(sy, a["id"])] = a
            r = ev.score(gold[a["id"]], a, comps)
            if sy.startswith("t2c"):
                r["status"], r["retried"] = a["status"], int(a["retried"])
                r["n_ctx"] = len(a["components"])
            rows.append(r)
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "metrics_per_question.csv", index=False)
    rel = df[df.type.isin(ev.REL)]
    rng = np.random.default_rng(20261004)

    L = ["# Métricas — línea base text-to-Cypher frente a los tres sistemas", "",
         f"Gold: `gold/questions.jsonl` (sha256 `{sha[:16]}…`), {df.id.nunique()} preguntas. "
         f"Mismo scorer (`score()` de `05_evaluate.py`), mismo modelo `{C.GEN_MODEL}` (temperature 0, "
         "thinkingBudget 0). Las respuestas de los tres sistemas previos se leen de `results/full/` sin "
         "modificarlas. Para text-to-Cypher, el «contexto» del scorer son los plugins que aparecen en las "
         f"filas devueltas (hasta {T.MAX_ROWS}; no hay K = 20), de modo que su recall de contexto no es "
         "un recall@20 estricto.", "",
         f"## Titular: T1–T4 (n = {rel.id.nunique()})", "",
         "| Sistema | F1 citas | Recall contexto | Precisión citas | Recall citas |", "|---|---|---|---|---|"]
    for sy in SYSTEMS:
        g = rel[rel.system == sy]
        L.append(f"| {LABEL[sy]} | {fmt(g.f1.mean())} | {fmt(g.recall_at_k.mean())} | "
                 f"{fmt(g.precision.mean())} | {fmt(g.recall.mean())} |")

    L += ["", "## F1 de citas por tipo (T5: cumplimiento de la restricción, no comparable)", "",
          "| Tipo | n | " + " | ".join(LABEL[s] for s in SYSTEMS) + " |",
          "|---|---|" + "---|" * len(SYSTEMS)]
    types = sorted(df.type.unique())
    for t in types + ["T1–T4", "T1–T4 + T6"]:
        sub = (rel if t == "T1–T4" else df[df.type.isin(list(ev.REL) + ["T6"])] if t == "T1–T4 + T6"
               else df[df.type == t])
        vals = [sub[sub.system == s].primary.mean() for s in SYSTEMS]
        L.append(f"| {ev.TYPE_LABEL.get(t, t)} | {sub.id.nunique()} | " +
                 " | ".join(fmt(v) for v in vals) + " |")

    L += ["", "## Contrastes pareados en T1–T4 (F1; Δ = segundo − primero)", "",
          "| Contraste | Δ | IC pareado | IC estratificado | IC conglomerados | Wilcoxon exacto p | G/E/P |",
          "|---|---|---|---|---|---|---|"]
    for a, b in PAIRS:
        r = ev.paired(rel, "f1", a, b, rng)
        L.append(f"| {LABEL[b]} − {LABEL[a]} | {fmt(r['diff'], 2, True)} | {ev.ci_s(r['ci']['paired'])} | "
                 f"{ev.ci_s(r['ci']['stratified'])} | {ev.ci_s(r['ci']['cluster'])} | "
                 f"{ev.pfmt(r['p'])} | {r['wins']}/{r['ties']}/{r['losses']} |")
    t6 = df[df.type == "T6"]
    r = ev.paired(t6, "f1", "baseline", "t2c", rng)
    L.append(f"\nControl T6, text-to-Cypher − vectorial: Δ {fmt(r['diff'], 2, True)} "
             f"{ev.ci_s(r['ci']['paired'])}, G/E/P {r['wins']}/{r['ties']}/{r['losses']}.")

    # --- fiabilidad de la consulta
    t = df[df.system == "t2c"]
    n = len(t)
    st = t.status.value_counts().to_dict()
    fail = st.get("error", 0) + st.get("rejected", 0) + st.get("timeout", 0)
    L += ["", "## Fiabilidad de la consulta generada (30 preguntas)", "",
          "| Indicador | Valor |", "|---|---|",
          f"| Consultas ejecutadas con filas | {st.get('ok', 0)}/{n} |",
          f"| Consultas válidas sin filas | {st.get('empty', 0)}/{n} |",
          f"| Fallo tras el reintento (error/rechazo/timeout) | {fail}/{n} ({100 * fail / n:.0f} %) |",
          f"| Preguntas que usaron el reintento | {int(t.retried.sum())}/{n} |",
          f"| Rechazadas por el filtro de seguridad | {st.get('rejected', 0)} |",
          f"| Timeouts | {st.get('timeout', 0)} |",
          f"| Plugins en las filas (mediana; máx.) | {int(t.n_ctx.median())}; {int(t.n_ctx.max())} |", ""]
    bytype = t.groupby("type").status.apply(lambda s: ", ".join(f"{k} {v}" for k, v in s.value_counts().items()))
    L += ["Estado por tipo: " + "; ".join(f"{k}: {v}" for k, v in bytype.items()), ""]

    # --- diagnostico de direccion
    diag = direction_diagnostic(ans, gold, comps)
    if diag:
        L += ["## Diagnóstico post hoc: dirección de las aristas (no es un sistema evaluado)", "",
              "Consultas que recorren `MAINTAINS` o `DESCRIBES` en sentido contrario al esquema. Se "
              "re-ejecutan sin LLM tras invertir solo esa flecha y se puntúan las filas como en "
              "«filas directas». Mide cuánto del fallo se debe a ese error concreto.", "",
              "| Pregunta | Estado original | Estado corregido | Plugins | Métrica original | Métrica corregida |",
              "|---|---|---|---|---|---|"]
        for qid, st0, st1, n_c, f1, f0 in diag:
            L.append(f"| {qid} | {st0} | {st1} | {n_c} | {fmt(f0)} | {fmt(f1)} |")
        L += ["", "(Métrica: F1 de citas; en T5, cumplimiento de la restricción.)", ""]

    # --- coste
    usages_gen, usages_fmt = [], []
    for (sy, _), a in ans.items():
        if sy == "t2c":
            usages_gen += a["usage_gen"]
            usages_fmt.append(a["usage"])
    gi, go, gu = T.cost(usages_gen)
    fi, fo, fu = T.cost(usages_fmt)
    calls = len(usages_gen) + sum(1 for u in usages_fmt if u)
    prev = [ans[(s, i)]["usage"].get("promptTokenCount", 0) for s in ("baseline", "vecrel", "graphrag")
            for i in gold]
    L += ["## Coste API (tokens de `usageMetadata` × precios de `config.py`)", "",
          "| Paso | Llamadas | Tokens entrada | Tokens salida | US$ |", "|---|---|---|---|---|",
          f"| Generación de Cypher (incl. reintentos) | {len(usages_gen)} | {th(gi)} | {th(go)} | {usd(gu)} |",
          f"| Formato de la respuesta | {sum(1 for u in usages_fmt if u)} | {th(fi)} | {th(fo)} | {usd(fu)} |",
          f"| **Total text-to-Cypher** | {calls} | {th(gi + fi)} | {th(go + fo)} | **{usd(gu + fu)}** |",
          "", f"Tokens de entrada por pregunta: text-to-Cypher {th(round((gi + fi) / n))} (dos llamadas o más), "
          f"sistemas RAG {th(round(np.mean(prev)))} (una llamada). Las re-ejecuciones leen `cache/llm_t2c/` y cuestan 0.", ""]
    (OUT / "metrics.md").write_text("\n".join(L))
    print("\n".join(L))


if __name__ == "__main__":
    main()
