"""Paso 13: ejecucion EXPLORATORIA de KG-RAG con un enrutador de intencion bilingue.

Responde al feedback del tutor sobre el borrador 3: el enrutado por intencion de KG-RAG
(`Retriever.intents`) solo reconoce expresiones en espanol y 30 de las 33 preguntas de la
comunidad estan en ingles. Aqui se anade una variante bilingue y se repite SOLO KG-RAG.

Para no ajustar el enrutador sobre los datos de evaluacion:
  - las expresiones inglesas son la traduccion de las espanolas existentes (no se han
    escrito mirando las 33 preguntas);
  - se validan contra el conjunto de desarrollo: las cinco plantillas T1-T5 de
    03_build_gold.py traducidas al ingles deben activar la misma intencion que en espanol;
  - aun asi, las 33 preguntas ya se conocian: el resultado se presenta como exploratorio.

Uso:
  python 13_enrutador_bilingue.py run     ejecuta KG-RAG bilingue (cache propia de respuestas:
                                          las llamadas con prompt identico al original se
                                          reutilizan de cache/llm_libres) y puntua F1 de citas
                                          -> results/libres/preguntas_comunidad_bilingue/
  python 13_enrutador_bilingue.py blind   para las preguntas cuya respuesta cambia, baraja la
                                          respuesta original y la nueva (semilla fija) para el
                                          mismo juicio ciego con la misma rubrica
                                          -> juicio_ciego_bilingue.md, clave_bilingue.json,
                                             etiquetas_bilingue.csv (plantilla)
  python 13_enrutador_bilingue.py report  -> resultados_enrutador_bilingue.md
"""
import csv
import importlib
import json
import random
import re
import sys

import pandas as pd

import config as C

# misma cache y registro de uso que 08 (las llamadas repetidas no cuestan)
C.LLM_CACHE = C.CACHE / "llm_libres"
C.QEMB_CACHE = C.CACHE / "qemb_libres"
C.USAGE_LOG = C.CACHE / "usage_bilingue.jsonl"

from retrieval import Retriever  # noqa: E402

ans04 = importlib.import_module("04_answer")
ev = importlib.import_module("05_evaluate")
SRC = C.RESULTS / "libres" / "preguntas_comunidad"
OUT = C.RESULTS / "libres" / "preguntas_comunidad_bilingue"
SEED = 20261008
ACCEPT = {"correcta", "abstencion_correcta"}

# Traduccion de las expresiones de Retriever.intents (espanol), sin mirar las 33 preguntas.
EN = {
    "in": r"\b(which|what) (plugins |components )?depend on\b|\bdepends? on (it|this)\b|\bwho depends on\b"
          r"|\bdependents of\b|\brequired by\b",
    "out": r"\bwhat (plugins |components )?does .{1,80} depend on\b|\bdependencies of\b|\brequire(s|d)?\b(?! by)",
    "maint": r"\bmaintains?\b|\bmaintainers?\b|\bdevelop",  # como "mantien": no casa "maintained"
    "comm": r"\bcommunity\b|\bfragile\b",
    "alt": r"\balternative|\breplac|\bsubstitut",
}
ORIG_INTENTS = Retriever.intents


def intents_bilingue(q):
    it = ORIG_INTENTS(q)
    ql = q.lower()
    for k in ("in", "out", "maint", "comm", "alt"):
        if k not in it and re.search(EN[k], ql):
            it.append(k)
    return it


# conjunto de desarrollo: plantillas T1-T5 de 03_build_gold.py, en espanol y traducidas
DEV = [
    ("¿Qué plugins dependen de Foo (local_foo)?", "Which plugins depend on Foo (local_foo)?", ["in"]),
    ("¿De qué plugins depende Foo (local_foo) y cuáles de esas dependencias siguen mantenidas?",
     "What plugins does Foo (local_foo) depend on, and which of those dependencies are still maintained?",
     ["out"]),
    ("¿Quién mantiene Foo (local_foo) y qué otros plugins mantiene?",
     "Who maintains Foo (local_foo) and what other plugins do they maintain?", ["maint"]),
    ("¿Qué plugins de la misma comunidad que Foo (local_foo) son frágiles?",
     "Which plugins in the same community as Foo (local_foo) are fragile?", ["comm"]),
    ("¿Qué alternativas mantenidas hay a Foo (local_foo)?",
     "What maintained alternatives are there to Foo (local_foo)?", ["alt"]),
]


def check_dev():
    for es, en, want in DEV:
        a, b = sorted(intents_bilingue(es)), sorted(intents_bilingue(en))
        assert a == b, (es, a, en, b)
        assert set(want) <= set(b), (en, b, want)
    print("conjunto de desarrollo: las 5 plantillas traducidas activan las mismas intenciones")


def cmd_run():
    check_dev()
    OUT.mkdir(parents=True, exist_ok=True)
    gold = {json.loads(l)["id"]: json.loads(l) for l in (SRC / "gold_resuelto.jsonl").read_text().splitlines()}
    orig = {json.loads(l)["id"]: json.loads(l) for l in (SRC / "answers_graphrag.jsonl").read_text().splitlines()}
    Retriever.intents = staticmethod(intents_bilingue)
    R = Retriever()
    rows = []
    try:
        with (OUT / "answers_graphrag_bil.jsonl").open("w") as f:
            for i, q in gold.items():
                ret = R.graphrag(q["question"])
                ctx = R.context(ret)
                resp = C.generate(ans04.SYSTEM, ans04.TEMPLATE.format(ctx=ctx, q=q["question"]))
                rec = {"id": i, "type": "L", "system": "graphrag_bil", "question": q["question"], **ret,
                       "context_chars": len(ctx), "answer": resp["text"], "model": resp["model"],
                       "usage": resp["usage"],
                       "intents_original": orig[i].get("intents"),
                       "cambia_respuesta": resp["text"].strip() != orig[i]["answer"].strip()}
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                if q["gold"] is not None:
                    rows.append(ev.score(q, rec, R.components))
                print(i, ret["intents"], "cambia" if rec["cambia_respuesta"] else "igual", flush=True)
    finally:
        R.close()
    pd.DataFrame(rows).to_csv(OUT / "metrics_per_question.csv", index=False)


def load(p):
    return {json.loads(l)["id"]: json.loads(l) for l in p.read_text().splitlines()}


def cmd_blind():
    new, old = load(OUT / "answers_graphrag_bil.jsonl"), load(SRC / "answers_graphrag.jsonl")
    qs = {q["id"]: q for q in __import__("yaml").safe_load((C.GR / "preguntas_comunidad.yaml").read_text())["preguntas"]}
    rng = random.Random(SEED)
    key, L, rows = {}, ["# Juicio ciego: enrutador bilingüe (exploratorio)", "",
                        "Para cada pregunta cuya respuesta de KG-RAG cambia con el enrutador bilingüe, dos "
                        "respuestas (X, Y) barajadas con semilla fija: la original y la nueva. Misma rúbrica, "
                        "referencia y criterio que el juicio principal.", ""], []
    for i in sorted(new):
        if not new[i]["cambia_respuesta"]:
            continue
        pair = [("original", old[i]["answer"]), ("bilingue", new[i]["answer"])]
        rng.shuffle(pair)
        key[i] = {"X": pair[0][0], "Y": pair[1][0]}
        q = qs[i]
        L += [f"## {i}", "", f"**Pregunta:** {q['pregunta']}", "", f"**Referencia:** {q['respuesta_ref']}", "",
              f"**Criterio:** {q.get('criterio', '')}", ""]
        for letter, (_, text) in zip("XY", pair):
            L += [f"### {i}-{letter}", "", text.strip(), ""]
            rows.append({"id": i, "letra": letter, "etiqueta": "", "nota": ""})
    (OUT / "juicio_ciego_bilingue.md").write_text("\n".join(L) + "\n")
    (OUT / "clave_bilingue.json").write_text(json.dumps({"semilla": SEED, "clave": key}, indent=1))
    lab = OUT / "etiquetas_bilingue.csv"
    if not lab.exists():
        with lab.open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["id", "letra", "etiqueta", "nota"])
            w.writeheader()
            w.writerows(rows)
    print(f"{len(key)} preguntas con respuesta distinta")


def cmd_report():
    new = load(OUT / "answers_graphrag_bil.jsonl")
    key = json.loads((OUT / "clave_bilingue.json").read_text())["clave"]
    lab = pd.read_csv(OUT / "etiquetas_bilingue.csv")
    assert lab.etiqueta.notna().all() and (lab.etiqueta != "").all(), "faltan etiquetas"
    lab["version"] = [key[i][L] for i, L in zip(lab.id, lab.letra)]
    main = pd.read_csv(SRC / "etiquetas_descegadas.csv")
    main = main[main.system == "graphrag"].set_index("id").etiqueta
    final = main.copy()
    for _, r in lab[lab.version == "bilingue"].iterrows():
        final[r.id] = r.etiqueta
    rejudged = lab[lab.version == "original"].set_index("id").etiqueta
    consist = (rejudged == main[rejudged.index]).mean() if len(rejudged) else float("nan")
    f1o = pd.read_csv(SRC / "metrics_per_question.csv")
    f1o = f1o[f1o.system == "graphrag"].f1.mean()
    f1n = pd.read_csv(OUT / "metrics_per_question.csv").f1.mean()
    n_int = sum(1 for a in new.values() if len(a["intents"]) < 5)
    n_int_o = sum(1 for a in new.values() if len(a.get("intents_original") or []) < 5)
    acc_o, acc_n = int(main.isin(ACCEPT).sum()), int(final.isin(ACCEPT).sum())
    usage = [json.loads(l) for l in (C.CACHE / "usage_bilingue.jsonl").read_text().splitlines()] \
        if (C.CACHE / "usage_bilingue.jsonl").exists() else []
    L = ["<!-- No editar a mano: generado por 13_enrutador_bilingue.py report -->", "",
         "# KG-RAG con enrutador bilingüe (ejecución exploratoria)", "",
         "Las 33 preguntas ya se conocían cuando se escribió la variante: el resultado es exploratorio y no "
         "sustituye a los resultados principales (`resultados_preguntas_comunidad.md`). Expresiones inglesas "
         "traducidas de las españolas y validadas con las plantillas T1-T5 traducidas (docstring).", "",
         "| Medida | Enrutador original | Enrutador bilingüe |", "|---|---|---|",
         f"| Preguntas con alguna intención detectada | {n_int_o} de 33 | {n_int} de 33 |",
         f"| Respuestas aceptables (de 33) | {acc_o} ({round(100 * acc_o / 33)}%) | {acc_n} ({round(100 * acc_n / 33)}%) |",
         f"| F1 de citas (n = 21) | {ev.fmt(f1o)} | {ev.fmt(f1n)} |", "",
         f"Respuestas que cambian: {len(key)}. Juicio ciego por pares (original frente a bilingüe, barajadas), "
         f"con la misma rúbrica; en las que no cambian se mantiene la etiqueta del juicio principal. "
         f"Consistencia del juez al volver a juzgar la respuesta original: "
         f"{ev.fmt(consist) if consist == consist else 'n/a'} ({len(rejudged)} respuestas).", "",
         f"Llamadas nuevas a la API registradas en `cache/usage_bilingue.jsonl`: {len(usage)}."]
    (C.GR / "resultados_enrutador_bilingue.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    {"run": cmd_run, "blind": cmd_blind, "report": cmd_report, "dev": check_dev}.get(cmd, lambda: sys.exit(__doc__))()
