"""Paso 12: tabla de analisis de errores de las preguntas de la comunidad (memoria v4, 5.10).

Uso: python 12_analisis_errores.py
Lee preguntas_comunidad.yaml, las respuestas de results/libres/preguntas_comunidad/ y las
etiquetas descegadas del juicio (09_eval_comunidad.py). Asigna a cada respuesta NO aceptable
(parcial, incorrecta o abstencion_incorrecta) una causa principal con reglas deterministas,
aplicadas en este orden (la primera que se cumple gana):

  1. plugin_ausente     la respuesta de referencia dice que el plugin por el que se pregunta no
                        esta en el directorio en la fecha de la fotografia;
  2. direccion_relacion (text-to-Cypher) alguna consulta generada recorre MAINTAINS al reves
                        del esquema: (Plugin)-[:MAINTAINS]->(Maintainer);
  3. compatibilidad     la respuesta de referencia necesita las versiones de Moodle soportadas
                        (su consulta gold_cypher/ref_cypher usa supported_releases o SUPPORTS) y
                        el sistema es uno de los tres RAG, cuyas fichas no incluyen ese dato;
  4. consulta_vacia     (text-to-Cypher) la consulta final no devuelve filas;
  5. idioma_enrutado    (KG-RAG) pregunta en ingles (campo `idioma`) y el enrutado por intencion
                        no detecto ninguna (uso las cinco expansiones);
  6. otra.

Las reglas no miran el texto de las respuestas ni la etiqueta mas alla de "aceptable o no".
Salida: analisis_errores.csv (una fila por respuesta no aceptable) y la seccion de tabla en
resultados_analisis_errores.md. No llama a la API ni a Neo4j.
"""
import json
import re
from collections import Counter

import pandas as pd
import yaml

import config as C

OUT = C.RESULTS / "libres" / "preguntas_comunidad"
SYSTEMS = ("baseline", "vecrel", "graphrag", "t2c")
SYS_LABEL = {"baseline": "RAG vectorial", "vecrel": "Vectorial + relaciones", "graphrag": "KG-RAG",
             "t2c": "Text-to-Cypher"}
ACCEPT = {"correcta", "abstencion_correcta"}
CAUSES = [("plugin_ausente", "Plugin ausente del directorio"),
          ("direccion_relacion", "Dirección de la relación invertida"),
          ("compatibilidad", "Compatibilidad con versiones (dato ausente del contexto)"),
          ("consulta_vacia", "Consulta sin filas (nombre o filtro inventado)"),
          ("idioma_enrutado", "Idioma: enrutado por intención solo en español"),
          ("otra", "Otra (enlazado erróneo, inferencia incorrecta)")]
ABSENT = re.compile(r"no (está|figura|aparece|existe)[^.;]{0,40}(snapshot|directorio)", re.I)
COMPAT = re.compile(r"supported_releases|SUPPORTS")
FLIP = re.compile(r"\(\w*(:Plugin)?[^)]*\)\s*-\s*\[\w*:MAINTAINS\]\s*->\s*\(\w*:Maintainer", re.I)


def load(s):
    return {json.loads(l)["id"]: json.loads(l) for l in (OUT / f"answers_{s}.jsonl").read_text().splitlines()}


def main():
    qs = {q["id"]: q for q in yaml.safe_load((C.GR / "preguntas_comunidad.yaml").read_text())["preguntas"]}
    lab = pd.read_csv(OUT / "etiquetas_descegadas.csv")
    ans = {s: load(s) for s in SYSTEMS}
    rows = []
    for _, r in lab.iterrows():
        if r.etiqueta in ACCEPT:
            continue
        q, s = qs[r.id], r.system
        a = ans[s][r.id]
        english = q["idioma"] == "en"
        gq = str(q.get("gold_cypher") or "") + str(q.get("ref_cypher") or "")
        cyphers = [x.get("cypher_run") or x.get("cypher") or "" for x in a.get("attempts", [])] + [a.get("cypher") or ""]
        if ABSENT.search(q["respuesta_ref"]):
            cause = "plugin_ausente"
        elif s == "t2c" and any(FLIP.search(c) for c in cyphers):
            cause = "direccion_relacion"
        elif s != "t2c" and COMPAT.search(gq):
            cause = "compatibilidad"
        elif s == "t2c" and a.get("status") == "empty":
            cause = "consulta_vacia"
        elif s == "graphrag" and english and len(a.get("intents") or []) >= 5:
            cause = "idioma_enrutado"
        else:
            cause = "otra"
        rows.append(dict(id=r.id, system=s, etiqueta=r.etiqueta, causa=cause, ingles=english))
    df = pd.DataFrame(rows).sort_values(["id", "system"])
    df.to_csv(OUT / "analisis_errores.csv", index=False)
    tab = Counter(zip(df.causa, df.system))
    L = ["<!-- No editar a mano: generado por 12_analisis_errores.py -->", "",
         "# Análisis de errores: preguntas de la comunidad", "",
         "Causa principal de cada respuesta no aceptable (parcial, incorrecta o abstención incorrecta), "
         "asignada con reglas deterministas en orden de prioridad (docstring de `12_analisis_errores.py`). "
         "Detalle por respuesta en `results/libres/preguntas_comunidad/analisis_errores.csv`.", "",
         "| Causa principal | " + " | ".join(SYS_LABEL[s] for s in SYSTEMS) + " | Total |",
         "|---" * (len(SYSTEMS) + 2) + "|"]
    for k, name in CAUSES:
        vals = [tab.get((k, s), 0) for s in SYSTEMS]
        L.append(f"| {name} | " + " | ".join(map(str, vals)) + f" | {sum(vals)} |")
    tot = [int((df.system == s).sum()) for s in SYSTEMS]
    L.append("| **Respuestas no aceptables** | " + " | ".join(map(str, tot)) + f" | {sum(tot)} |")
    L += ["", f"Preguntas en inglés: {sum(1 for q in qs.values() if q['idioma'] == 'en')} de {len(qs)}. "
          f"Preguntas cuya referencia necesita las versiones soportadas (regla 3): "
          f"{sum(1 for q in qs.values() if COMPAT.search(str(q.get('gold_cypher') or '') + str(q.get('ref_cypher') or '')))}. "
          f"Preguntas con plugin ausente (regla 1): {sum(1 for q in qs.values() if ABSENT.search(q['respuesta_ref']))}.", ""]
    for k, _ in CAUSES:
        ids = sorted(set(df[df.causa == k].id))
        L.append(f"- `{k}`: {', '.join(ids) if ids else '—'}")
    # contraste pareado de "aceptable" (McNemar exacto, binomial bilateral sobre los discordantes)
    from math import comb
    acc = lab.assign(ok=lab.etiqueta.isin(ACCEPT)).pivot(index="id", columns="system", values="ok")
    L += ["", "## Text-to-Cypher frente a cada sistema RAG: respuestas aceptables (33 preguntas, pareado)", "",
          "| Contraste | Solo text-to-Cypher aceptable | Solo el RAG aceptable | p (McNemar exacto) |",
          "|---|---|---|---|"]
    for s in SYSTEMS[:3]:
        b = int((acc["t2c"] & ~acc[s]).sum())
        c = int((~acc["t2c"] & acc[s]).sum())
        n = b + c
        p = min(1.0, 2 * sum(comb(n, k) for k in range(0, min(b, c) + 1)) / 2 ** n) if n else 1.0
        L.append(f"| Text-to-Cypher − {SYS_LABEL[s]} | {b} | {c} | {p:.3f}".replace(".", ",") + " |")
    (C.GR / "resultados_analisis_errores.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
