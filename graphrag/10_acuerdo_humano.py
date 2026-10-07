"""Paso 10: segundo evaluador humano sobre una submuestra de las preguntas de la comunidad.

Responde al feedback del tutor sobre el borrador 3 de la memoria: el juicio de 09 lo hizo
un unico evaluador (un agente LLM, claude-opus-5-5, que tambien redacto la referencia y los
criterios). Una persona juzga a ciegas una submuestra y se reporta el acuerdo (kappa de Cohen).

Uso (en este orden):
  python 10_acuerdo_humano.py muestra   elige 15 de las 33 preguntas, estratificadas por
                                        `respondible` (si/parcial/no), semilla fija, SIN mirar
                                        etiquetas ni respuestas -> muestra_humana.json y
                                        hoja_humana.json (pregunta, referencia, criterio y las
                                        4 respuestas con las MISMAS letras A-D del juicio ciego;
                                        sin sistema ni etiqueta del LLM)
  (la persona etiqueta con la misma rubrica -> etiquetas_humano.csv: id, letra, etiqueta, nota)
  python 10_acuerdo_humano.py kappa     cruza con etiquetas_ciego.csv y la clave
                                        -> resultados_acuerdo_humano.md

Etiquetas: correcta, parcial, incorrecta, abstencion_correcta, abstencion_incorrecta.
"Aceptable" = correcta o abstencion_correcta (igual que en 09).
"""
import csv
import json
import random
import sys

import numpy as np
import pandas as pd
import yaml

import config as C

QFILE = C.GR / "preguntas_comunidad.yaml"
OUT = C.RESULTS / "libres" / "preguntas_comunidad"
SEED = 20261007
N_SAMPLE = 15
LABELS = ["correcta", "parcial", "incorrecta", "abstencion_correcta", "abstencion_incorrecta"]
ACCEPT = {"correcta", "abstencion_correcta"}
SYSTEMS = ("baseline", "vecrel", "graphrag", "t2c")
SYS_LABEL = {"baseline": "RAG vectorial", "vecrel": "Vectorial + relaciones", "graphrag": "KG-RAG",
             "t2c": "Text-to-Cypher"}
N_BOOT = 10000


def questions():
    return yaml.safe_load(QFILE.read_text())["preguntas"]


def allocate(counts, n):
    """Asignacion proporcional por restos mayores."""
    tot = sum(counts.values())
    raw = {k: n * v / tot for k, v in counts.items()}
    alloc = {k: int(np.floor(x)) for k, x in raw.items()}
    rest = sorted(raw, key=lambda k: (-(raw[k] - alloc[k]), k))
    for k in rest[: n - sum(alloc.values())]:
        alloc[k] += 1
    return alloc


def cmd_muestra():
    qs = questions()
    strata = {}
    for q in qs:
        strata.setdefault(q["respondible"], []).append(q["id"])
    alloc = allocate({k: len(v) for k, v in strata.items()}, N_SAMPLE)
    rng = random.Random(SEED)
    sample = []
    for k in sorted(strata):
        sample += rng.sample(sorted(strata[k]), alloc[k])
    sample.sort()
    (OUT / "muestra_humana.json").write_text(json.dumps(
        {"semilla": SEED, "n": N_SAMPLE, "asignacion": alloc, "ids": sample}, indent=1))
    # hoja: mismas letras que el juicio ciego del LLM, sin sistema ni etiqueta
    key = json.loads((OUT / "clave_ciego.json").read_text())["clave"]
    ans = {}
    for s in SYSTEMS:
        for line in (OUT / f"answers_{s}.jsonl").read_text().splitlines():
            r = json.loads(line)
            ans[(r["id"], s)] = r["answer"].strip()
    byid = {q["id"]: q for q in qs}
    hoja = []
    for i in sample:
        q = byid[i]
        hoja.append({"id": i, "pregunta": q["pregunta"], "referencia": q["respuesta_ref"],
                     "criterio": q.get("criterio", ""),
                     "respuestas": [{"letra": L, "texto": ans[(i, key[i][L])]} for L in "ABCD"]})
    (OUT / "hoja_humana.json").write_text(json.dumps(hoja, ensure_ascii=False, indent=1))
    print("asignacion", alloc, "muestra", sample)


def cohen_kappa(a, b, cats):
    a, b = list(a), list(b)
    n = len(a)
    po = sum(x == y for x, y in zip(a, b)) / n
    pe = sum((a.count(c) / n) * (b.count(c) / n) for c in cats)
    return (po - pe) / (1 - pe) if pe < 1 else float("nan"), po


def boot_kappa(df, col_a, col_b, cats, rng):
    ids = df.id.unique()
    ks = []
    for _ in range(N_BOOT):
        pick = rng.choice(ids, size=len(ids), replace=True)
        d = pd.concat([df[df.id == i] for i in pick])
        k, _ = cohen_kappa(d[col_a], d[col_b], cats)
        ks.append(k)
    return np.nanpercentile(ks, [2.5, 97.5])


def es(x, nd=2):
    return f"{x:.{nd}f}".replace(".", ",")


def cmd_kappa():
    smp = json.loads((OUT / "muestra_humana.json").read_text())["ids"]
    key = json.loads((OUT / "clave_ciego.json").read_text())["clave"]
    llm = pd.read_csv(OUT / "etiquetas_ciego.csv")[["id", "letra", "etiqueta"]].rename(columns={"etiqueta": "llm"})
    hum = pd.read_csv(OUT / "etiquetas_humano.csv")[["id", "letra", "etiqueta"]].rename(columns={"etiqueta": "humano"})
    assert set(hum.id) == set(smp) and len(hum) == 4 * len(smp), "la hoja humana no cubre la muestra"
    assert hum.humano.isin(LABELS).all(), set(hum.humano) - set(LABELS)
    df = hum.merge(llm, on=["id", "letra"], how="left")
    assert df.llm.notna().all()
    df["system"] = [key[i][L] for i, L in zip(df.id, df.letra)]
    df["acc_h"] = df.humano.isin(ACCEPT)
    df["acc_l"] = df.llm.isin(ACCEPT)
    rng = np.random.default_rng(SEED)
    k5, po5 = cohen_kappa(df.humano, df.llm, LABELS)
    k2, po2 = cohen_kappa(df.acc_h, df.acc_l, [True, False])
    ci5 = boot_kappa(df, "humano", "llm", LABELS, rng)
    ci2 = boot_kappa(df, "acc_h", "acc_l", [True, False], rng)
    conf = pd.crosstab(pd.Categorical(df.humano, LABELS), pd.Categorical(df.llm, LABELS),
                       rownames=["humano"], colnames=["LLM"], dropna=False)
    L = ["<!-- No editar a mano: generado por 10_acuerdo_humano.py kappa -->", "",
         "# Acuerdo entre el juez LLM y un evaluador humano (preguntas de la comunidad)", "",
         f"Submuestra de {len(smp)} de las 33 preguntas, estratificada por `respondible` "
         f"(semilla {SEED}; `muestra_humana.json`), elegida antes de ver ninguna etiqueta. "
         f"{len(df)} respuestas (4 por pregunta) juzgadas a ciegas por una persona con la misma rúbrica, "
         "la misma referencia y el mismo criterio que el juez LLM (`claude-opus-5-5`), con las mismas letras "
         "A-D y sin acceso a la clave ni a las etiquetas del LLM. Preguntas: " + ", ".join(smp) + ".", "",
         "## Acuerdo", "",
         "| Escala | Acuerdo observado | Kappa de Cohen | IC 95% (bootstrap por pregunta) |",
         "|---|---|---|---|",
         f"| Cinco etiquetas | {es(100 * po5, 1)}% | {es(k5)} | [{es(ci5[0])}; {es(ci5[1])}] |",
         f"| Aceptable / no aceptable | {es(100 * po2, 1)}% | {es(k2)} | [{es(ci2[0])}; {es(ci2[1])}] |", "",
         f"Bootstrap: {N_BOOT} remuestreos de preguntas (las 4 respuestas de una pregunta van juntas).", "",
         "## Matriz de confusión (filas: humano; columnas: LLM)", "",
         "| humano \\ LLM | " + " | ".join(LABELS) + " |", "|---" * (len(LABELS) + 1) + "|"]
    for r in LABELS:
        L.append(f"| {r} | " + " | ".join(str(int(conf.loc[r, c])) for c in LABELS) + " |")
    L += ["", "## Respuestas aceptables por sistema en la submuestra", "",
          "| Sistema | n | Aceptables según el LLM | Aceptables según el humano | Desacuerdos |", "|---|---|---|---|---|"]
    for s in SYSTEMS:
        g = df[df.system == s]
        L.append(f"| {SYS_LABEL[s]} | {len(g)} | {int(g.acc_l.sum())} ({es(100 * g.acc_l.mean(), 0)}%) | "
                 f"{int(g.acc_h.sum())} ({es(100 * g.acc_h.mean(), 0)}%) | {int((g.humano != g.llm).sum())} |")
    order_l = sorted(SYSTEMS, key=lambda s: -df[df.system == s].acc_l.mean())
    order_h = sorted(SYSTEMS, key=lambda s: -df[df.system == s].acc_h.mean())
    L += ["", f"Orden por aceptables, LLM: {' > '.join(SYS_LABEL[s] for s in order_l)}; "
          f"humano: {' > '.join(SYS_LABEL[s] for s in order_h)}.", "",
          "## Desacuerdos", "", "| Pregunta | Letra | Sistema | Humano | LLM |", "|---|---|---|---|---|"]
    for _, r in df[df.humano != df.llm].sort_values(["id", "letra"]).iterrows():
        L.append(f"| {r.id} | {r.letra} | {SYS_LABEL[r.system]} | {r.humano} | {r.llm} |")
    (C.GR / "resultados_acuerdo_humano.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    {"muestra": cmd_muestra, "kappa": cmd_kappa}.get(cmd, lambda: sys.exit(__doc__))()
