"""Paso 9: evaluación con preguntas reales de la comunidad Moodle.

Uso (en este orden; el orden es lo que hace honesta la evaluación):
  python 09_eval_comunidad.py gold     congela preguntas_comunidad.yaml (sha256) y ejecuta,
                                       en solo lectura, cada gold_cypher / ref_cypher
                                       -> results/libres/preguntas_comunidad/gold_hechos.jsonl
  python 08_preguntas_libres.py preguntas_comunidad.yaml     (los 4 sistemas)
  python 09_eval_comunidad.py blind    baraja las 4 respuestas de cada pregunta (semilla fija)
                                       -> juicio_ciego.md, clave_ciego.json,
                                          etiquetas_ciego.csv (plantilla vacía)
  (juicio a mano sobre juicio_ciego.md: se rellena etiquetas_ciego.csv SIN abrir la clave)
  python 09_eval_comunidad.py report   desciega, cruza con F1 de citas y coste
                                       -> resultados_preguntas_comunidad.md

Etiquetas: correcta, parcial, incorrecta, abstencion_correcta, abstencion_incorrecta.
"""
import csv
import hashlib
import json
import random
import sys
from pathlib import Path

import pandas as pd
import yaml

import config as C

QFILE = C.GR / "preguntas_comunidad.yaml"
SHAFILE = C.GR / "preguntas_comunidad.sha256"
OUT = C.RESULTS / "libres" / "preguntas_comunidad"
REPORT = C.GR / "resultados_preguntas_comunidad.md"
USAGE = C.CACHE / "usage_libres.jsonl"
SYSTEMS = ("baseline", "vecrel", "graphrag", "t2c")
NAME = {"baseline": "RAG vectorial", "vecrel": "Vectorial + relaciones",
        "graphrag": "KG-RAG", "t2c": "Text-to-Cypher"}
LABELS = ("correcta", "parcial", "incorrecta", "abstencion_correcta", "abstencion_incorrecta")
LNAME = {"correcta": "Correcta", "parcial": "Parcial", "incorrecta": "Incorrecta",
         "abstencion_correcta": "Abstención correcta", "abstencion_incorrecta": "Abstención incorrecta"}
SEED = 20261004
CLASS = {"C": "Completa", "P": "Parcial", "N": "No respondible"}

# Modos de fallo observados: redactados tras desciegar, a partir de las notas del juicio
# (etiquetas_descegadas.csv) y de los campos link_method / intents / cypher / status de
# answers_*.jsonl. Es texto interpretativo, no una cifra calculada.
MODOS_FALLO = [
    "## Modos de fallo observados", "",
    "1. **Las fichas de los tres sistemas RAG no incluyen las versiones de Moodle soportadas.** "
    "La ficha de `retrieval.card()` da tipo, instalaciones, última release, estado (≤3 años), mantenedores "
    "y descripción, pero no `supported_releases` ni `SUPPORTS`. En las 10 preguntas de compatibilidad "
    "respondibles (C09-C19 salvo C11) los tres sistemas RAG se abstienen o infieren el soporte de la "
    "fecha de release o de la descripción; solo text-to-Cypher consulta `SUPPORTS`. Es el fallo dominante y es de "
    "diseño del contexto, no del modelo.",
    "2. **Enrutado de intención solo en español.** `Retriever.intents()` usa expresiones regulares en "
    "español; 30 de las 33 preguntas están en inglés. KG-RAG detectó intención solo en P08 (castellano); en "
    "las demás usó las cinco expansiones en turno rotatorio, que diluyen el presupuesto de 20 fichas.",
    "3. **Enlazado a la entidad equivocada.** En C03 KG-RAG enlazó por nombre «ILP Integration» "
    "(block_intelligent_learning) en lugar de Open LMS Framework (local_mr); sin las aristas entrantes de "
    "local_mr afirmó que no tenía dependientes (incorrecta). Cuando el plugin no está en el snapshot "
    "(C06, C08, P02, P05) el enlazado vectorial elige un vecino (format_collapsibletopics, format_board...), "
    "pero ningún sistema respondió sobre el vecino: se abstuvieron (correctamente en C06, C08 y P05).",
    "4. **Text-to-Cypher invierte la dirección de MAINTAINS.** Escribe `(p:Plugin)-[:MAINTAINS]->(m:Maintainer)` "
    "y concluye «no tiene mantenedores listados» (C01, C02, P04, P08), lo que convierte respuestas correctas "
    "en parciales o incorrectas. También filtra por `name` con nombres inventados («Moove theme», "
    "«Quiz download submissions», «navbuttons»), obtiene 0 filas y se abstiene (C16, C19, N03), e inventa "
    "parámetros (lista de plugins «instalados» en C04; marcadores «Your Name» en P01 y N04).",
    "5. **Abstención excesiva frente a alucinación.** El prompt «usa EXCLUSIVAMENTE el contexto» funciona: "
    "las alucinaciones de hechos son raras (5 incorrectas en 132 respuestas) y las 6 preguntas N reciben "
    "abstención correcta en casi todos los sistemas. El coste es la abstención incorrecta en preguntas "
    "respondibles (P02: ningún sistema recomienda temas porque theme_essential no está).",
    "6. **Soporte de Workplace (N05).** Los tres sistemas RAG presentan como «compatibles con Workplace» los "
    "plugins cuya descripción lo menciona, sin advertir que no existe ese metadato; text-to-Cypher busca una "
    "release «Moodle Workplace», no la encuentra y se abstiene.",
    "7. **KG-RAG cita de más.** Con el turno rotatorio de expansiones, KG-RAG añade listas de plugins "
    "co-mantenidos o «alternativas» que no se pidieron (C02, C07, C19). La etiqueta sigue siendo correcta, "
    "pero la precisión de citas cae (F1 0,11-0,18 en esas preguntas), lo que explica su F1 medio inferior al "
    "de los sistemas vectoriales pese a tener el mayor recall de contexto.",
    "",
]


def questions():
    return yaml.safe_load(QFILE.read_text())["preguntas"]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def check_frozen():
    frozen = SHAFILE.read_text().split()[0]
    if sha(QFILE) != frozen:
        sys.exit("preguntas_comunidad.yaml no coincide con su sha256 congelado: abortado")
    return frozen


def cmd_gold():
    import text2cypher as T
    if SHAFILE.exists():
        check_frozen()
    else:
        SHAFILE.write_text(f"{sha(QFILE)}  {QFILE.name}\n")
    OUT.mkdir(parents=True, exist_ok=True)
    drv = C.driver()
    comps = {r["c"] for r in drv.session().run("MATCH (p:Plugin) RETURN p.component AS c").data()}
    recs = []
    try:
        for q in questions():
            for key in ("gold_cypher", "ref_cypher"):
                cy = (q.get(key) or "").strip()
                if not cy:
                    continue
                why = T.check(cy)
                assert why is None, f"{q['id']}: {why}"
                rows, cols, trunc = T.execute(drv, cy)
                rec = {"id": q["id"], "consulta": key, "filas": rows, "truncado": trunc}
                if key == "gold_cypher":
                    got = sorted(set(T.components_in(rows, comps)))
                    rec["citas_cypher"] = got
                    assert set(got) == set(q["gold"]), f"{q['id']}: gold {q['gold']} != cypher {got}"
                recs.append(rec)
                print(q["id"], key, json.dumps(rows, ensure_ascii=False, default=str)[:300])
    finally:
        drv.close()
    p = OUT / "gold_hechos.jsonl"
    p.write_text("".join(json.dumps(r, ensure_ascii=False, default=str) + "\n" for r in recs))
    print(f"\n{len(recs)} consultas de gold ejecutadas -> {p}\nsha256 yaml: {SHAFILE.read_text().strip()}")


def answers():
    out = {}
    for s in SYSTEMS:
        for line in (OUT / f"answers_{s}.jsonl").read_text().splitlines():
            a = json.loads(line)
            out[(a["id"], s)] = a
    return out


def cmd_blind():
    check_frozen()
    qs, ans = questions(), answers()
    rng = random.Random(SEED)
    key, L = {}, ["# Juicio ciego — preguntas de la comunidad", "",
                  "Cada pregunta tiene 4 respuestas (A-D) de 4 sistemas, barajadas con semilla fija. "
                  "Juzgar solo con la pregunta, la respuesta de referencia y el criterio fijados antes "
                  "de ejecutar. Etiquetas: correcta, parcial, incorrecta, abstencion_correcta, "
                  "abstencion_incorrecta.", ""]
    rows = []
    for q in qs:
        order = list(SYSTEMS)
        rng.shuffle(order)
        key[q["id"]] = dict(zip("ABCD", order))
        L += [f"## {q['id']}", "", f"**Pregunta:** {q['pregunta']}", "",
              f"**Referencia:** {q['respuesta_ref']}", "", f"**Criterio:** {q.get('criterio', '')}", ""]
        for letter, s in zip("ABCD", order):
            text = ans[(q["id"], s)]["answer"].strip()
            L += [f"### {q['id']}-{letter}", "", text, ""]
            rows.append({"id": q["id"], "letra": letter, "etiqueta": "", "nota": ""})
    (OUT / "juicio_ciego.md").write_text("\n".join(L) + "\n")
    (OUT / "clave_ciego.json").write_text(json.dumps({"semilla": SEED, "clave": key}, indent=1))
    lab = OUT / "etiquetas_ciego.csv"
    if lab.exists():
        print(f"{lab} ya existe: no se sobrescribe")
    else:
        with lab.open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["id", "letra", "etiqueta", "nota"])
            w.writeheader()
            w.writerows(rows)
    print(f"juicio_ciego.md, clave_ciego.json, etiquetas_ciego.csv en {OUT}")


def pct(n, d):
    return f"{n} ({100 * n / d:.0f} %)".replace(".", ",") if d else "—"


def fnum(x, nd=2):
    return "—" if pd.isna(x) else f"{x:.{nd}f}".replace(".", ",")


def es(x, nd=0):
    """Número en formato español: punto de millares y coma decimal."""
    return f"{x:,.{nd}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def cost():
    pin = pout = emb = 0
    for line in USAGE.read_text().splitlines():
        r = json.loads(line)
        if r["kind"] == "embed":
            emb += r.get("est_tokens", 0)
        else:
            pin += r["prompt_tokens"]
            pout += r["out_tokens"]
    usd_g = pin / 1e6 * C.PRICE_GEN_IN + pout / 1e6 * C.PRICE_GEN_OUT
    usd_e = emb / 1e6 * C.PRICE_EMBED
    n = len(USAGE.read_text().splitlines())
    return n, pin, pout, emb, usd_g, usd_e


def cmd_report():
    frozen = check_frozen()
    qs = {q["id"]: q for q in questions()}
    key = json.loads((OUT / "clave_ciego.json").read_text())["clave"]
    lab = pd.read_csv(OUT / "etiquetas_ciego.csv", dtype=str).fillna("")
    bad = lab[~lab.etiqueta.isin(LABELS)]
    assert bad.empty, f"etiquetas vacías o no válidas:\n{bad}"
    lab["system"] = [key[i][l] for i, l in zip(lab.id, lab.letra)]
    lab["clase"] = lab.id.map(lambda i: qs[i]["clase"])
    lab["respondible"] = lab.id.map(lambda i: str(qs[i]["respondible"]))
    lab.to_csv(OUT / "etiquetas_descegadas.csv", index=False)
    f1 = pd.read_csv(OUT / "metrics_per_question.csv")
    ans = answers()
    nq = len(qs)

    L = ["<!-- No editar a mano: generado por 09_eval_comunidad.py report -->", "",
         "# Preguntas reales de la comunidad Moodle: resultados", "",
         f"{nq} preguntas redactadas por miembros de la comunidad (foros de moodle.org vía Wayback, "
         "Moodle Tracker e issues de GitHub), de las 34 candidatas de "
         "`intercambio/salida/v3/preguntas_comunidad_candidatas.md`; se excluye P09 por ser posterior "
         "al snapshot del grafo (2026-09-07). Preguntas, gold y criterios en `preguntas_comunidad.yaml` "
         f"(sha256 `{frozen[:16]}…`, congelado antes de ejecutar ningún sistema; hechos del gold en "
         "`results/libres/preguntas_comunidad/gold_hechos.jsonl`). Sistemas: los cuatro de "
         "`08_preguntas_libres.py`, con el mismo modelo (`gemini-2.5-flash`, temperatura 0).", "",
         "Juicio: rúbrica de 4 etiquetas (más «abstención incorrecta») aplicada **a ciegas** sobre "
         "`juicio_ciego.md` (respuestas barajadas como A-D con semilla "
         f"{SEED}; clave en `clave_ciego.json`), usando solo la pregunta, `respuesta_ref` y el criterio "
         "fijado a priori. Etiquetas en `etiquetas_ciego.csv`; desciegadas en `etiquetas_descegadas.csv`.", ""]

    def table(df, title):
        out = [f"### {title}", "", "| Sistema | n | " + " | ".join(LNAME[x] for x in LABELS) +
               " | Aceptables* |", "|---" * (len(LABELS) + 3) + "|"]
        for s in SYSTEMS:
            g = df[df.system == s]
            c = g.etiqueta.value_counts()
            acc = int(c.get("correcta", 0) + c.get("abstencion_correcta", 0))
            out.append(f"| {NAME[s]} | {len(g)} | " + " | ".join(pct(int(c.get(x, 0)), len(g)) for x in LABELS)
                       + f" | {pct(acc, len(g))} |")
        return out + [""]

    L += ["## Etiquetas por sistema", ""]
    L += table(lab, f"Global ({nq} preguntas)")
    for k in ("C", "P", "N"):
        sub = lab[lab.clase == k]
        L += table(sub, f"Clase {k} ({CLASS[k].lower()} según el recolector, {sub.id.nunique()} preguntas)")
    sub = lab[lab.respondible != "no"]
    L += table(sub, f"Preguntas respondibles total o parcialmente según el gold ({sub.id.nunique()})")
    sub = lab[lab.respondible == "no"]
    L += table(sub, f"Solo preguntas no respondibles según el gold ({sub.id.nunique()})")
    L += ["*Aceptables = correcta + abstención correcta.", ""]

    # F1 de citas
    L += ["## F1 de citas (`score()` de `05_evaluate.py`)", "",
          f"Solo las {f1.id.nunique()} preguntas con citas esperadas (`gold`). Sin `seed`: el plugin "
          "nombrado es la cita esperada.", "",
          "| Sistema | n | F1 | Precisión | Recall | Recall contexto | Sin citas |", "|---|---|---|---|---|---|---|"]
    for s in SYSTEMS + ("t2c_directo",):
        g = f1[f1.system == s]
        nm = NAME.get(s, "Text-to-Cypher (filas directas, sin LLM)")
        L.append(f"| {nm} | {len(g)} | {fnum(g.f1.mean())} | {fnum(g.precision.mean())} | "
                 f"{fnum(g.recall.mean())} | {fnum(g.recall_at_k.mean())} | {int(g.no_citations.sum())} |")
    L += [""]

    # por pregunta
    ab = {"correcta": "C", "parcial": "P", "incorrecta": "I", "abstencion_correcta": "AC",
          "abstencion_incorrecta": "AI"}
    piv = lab.pivot(index="id", columns="system", values="etiqueta")
    f1p = f1.pivot(index="id", columns="system", values="f1")
    L += ["## Por pregunta", "",
          "Etiquetas: C correcta, P parcial, I incorrecta, AC abstención correcta, AI abstención incorrecta. "
          "Entre paréntesis, F1 de citas.", "",
          "| id | Clase | Respondible | Idioma | " + " | ".join(NAME[s] for s in SYSTEMS) + " |",
          "|---|---|---|---|---|---|---|---|"]
    for i in qs:
        cells = []
        for s in SYSTEMS:
            v = ab[piv.loc[i, s]]
            if i in f1p.index:
                v += f" ({fnum(f1p.loc[i, s])})"
            cells.append(v)
        L.append(f"| {i} | {qs[i]['clase']} | {qs[i]['respondible']} | {qs[i]['idioma']} | " + " | ".join(cells) + " |")
    L += [""]

    # notas del juez
    notes = lab[lab.nota.str.strip() != ""].sort_values(["id", "system"])
    L += ["## Notas del juicio (tras desciegar)", "", "| id | Sistema | Etiqueta | Nota |", "|---|---|---|---|"]
    for _, r in notes.iterrows():
        L.append(f"| {r.id} | {NAME[r.system]} | {LNAME[r.etiqueta]} | {r.nota} |")
    L += [""]

    # diagnósticos automáticos
    st = pd.Series([ans[(i, "t2c")].get("status") for i in qs]).value_counts().to_dict()
    lk = pd.Series([ans[(i, "graphrag")].get("link_method") for i in qs]).value_counts().to_dict()
    it = sum(1 for i in qs if ans[(i, "graphrag")].get("intents") and
             len(ans[(i, "graphrag")]["intents"]) < 5)
    L += ["## Diagnósticos automáticos", "",
          f"- Estado de las consultas text-to-Cypher: " + ", ".join(f"{k} {v}" for k, v in st.items()) + ".",
          f"- Enlazado de entidades de KG-RAG: " + ", ".join(f"{k} {v}" for k, v in lk.items()) + ".",
          f"- Preguntas en las que el enrutado por intención de KG-RAG (palabras clave en español) "
          f"detectó al menos una intención: {it} de {nq}; en el resto usa todas las expansiones en turno rotatorio.",
          ""]
    L += MODOS_FALLO

    n, pin, pout, emb, ug, ue = cost()
    L += ["## Coste", "",
          f"Registro `cache/usage_libres.jsonl` ({n} registros): {es(pin)} tokens de entrada y {es(pout)} de salida "
          f"de generación (US$ {es(ug, 4)}) y unos {es(emb)} tokens estimados de embeddings de consulta "
          f"(US$ {es(ue, 4)}). **Total: US$ {es(ug + ue, 4)}** (precios de `config.py`: "
          f"{es(C.PRICE_GEN_IN, 2)} y {es(C.PRICE_GEN_OUT, 2)} US$ por millón de tokens de entrada y salida; "
          f"{es(C.PRICE_EMBED, 2)} US$ por millón en embeddings).", ""]

    L += ["## Limitaciones", "",
          "- **Un solo juez, y es un agente LLM** (Claude, que también escribió el gold y los criterios). "
          "El juicio es ciego respecto al sistema, pero no hay segundo anotador ni acuerdo inter-anotador; "
          "algunas respuestas delatan el sistema por su estilo (p. ej. text-to-Cypher habla de «filas» o de la consulta).",
          "- **Desfase temporal.** Las preguntas son de 2019-2026 y se responden con el snapshot del 2026-09-07; "
          "la respuesta correcta hoy puede no coincidir con la de la fecha de la pregunta (p. ej. block_massaction fue adoptado).",
          "- **Adaptaciones.** 22 preguntas usan la «pregunta adaptada» del recolector y 7 llevan delante, de forma "
          "mecánica, el nombre del repositorio de GitHub porque el texto literal solo dice «this plugin». "
          "Las adaptaciones pasan las preguntas futuras a presente y las acotan a lo que el directorio publica.",
          "- **Selección.** Las preguntas las escribieron terceros, pero la búsqueda, el filtrado por palabras clave "
          "y la clasificación los hizo el lado del autor; el corpus está sesgado hacia compatibilidad de versiones "
          "(issues de GitHub) y casi no contiene preguntas de ranking, donde el grafo es más fuerte.",
          "- **Clase a priori frente a gold.** Al escribir el gold resultó que format_topcoll, format_grid, "
          "theme_essential, format_weekcoll y mod_matrix no están en el snapshot: C06, C08 y P05 pasan a no respondibles. "
          "Se informa por clase del recolector y por respondibilidad según el gold.",
          "- **Muestra pequeña** (33 preguntas): no se calculan intervalos ni pruebas; las diferencias de 1-3 preguntas no son concluyentes.",
          ""]
    REPORT.write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    {"gold": cmd_gold, "blind": cmd_blind, "report": cmd_report}.get(cmd, lambda: sys.exit(__doc__))()
