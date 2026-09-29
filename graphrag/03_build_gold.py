"""Paso 3: preguntas gold con verdad-terreno calculada por Cypher/pandas.

Se ejecuta ANTES de cualquier sistema. Congela gold/questions.jsonl: los tipos
ya presentes nunca se reescriben (solo se anaden tipos nuevos), y se guarda el
sha256 del fichero en gold/questions.sha256.

Uso: python 03_build_gold.py T1 T3 T6        (linea de corte)
     python 03_build_gold.py T2 T4 T5        (extension al plan completo)
"""
import hashlib
import json
import random
import sys

import pandas as pd

import config as C

N = 5
SEED = 20260928


def rng(t):
    return random.Random(f"{SEED}-{t}")


def name_of(s, c):
    return s.run("MATCH (p:Plugin {component:$c}) RETURN p.name AS n", c=c).single()["n"]


def t1(s):
    pool = s.run("""MATCH (q:Plugin)-[:DEPENDS_ON]->(p:Plugin {in_directory:true})
                    WITH p, count(DISTINCT q) AS n WHERE 3 <= n <= $mx
                    RETURN p.component AS c ORDER BY c""", mx=C.K - 1).data()
    out = []
    for c in rng("T1").sample([r["c"] for r in pool], N):
        gold = sorted(r["c"] for r in s.run(
            "MATCH (q:Plugin)-[:DEPENDS_ON]->(:Plugin {component:$c}) RETURN DISTINCT q.component AS c", c=c))
        out.append({"type": "T1", "seed": c,
                    "question": f"¿Qué plugins dependen de {name_of(s, c)} ({c})?",
                    "gold": gold})
    return out


def t2(s):
    pool = s.run("""MATCH (p:Plugin {in_directory:true})-[:DEPENDS_ON]->(q:Plugin)
                    WITH p, collect(DISTINCT q) AS qs
                    WHERE 2 <= size(qs) <= $mx
                      AND any(x IN qs WHERE x.last_release_ts < $cut)
                    RETURN p.component AS c ORDER BY c""", mx=C.K - 1, cut=C.STALE_CUTOFF_UNIX).data()
    out = []
    for c in rng("T2").sample([r["c"] for r in pool], N):
        rows = s.run("""MATCH (:Plugin {component:$c})-[:DEPENDS_ON]->(q:Plugin)
                        RETURN DISTINCT q.component AS c, q.last_release_ts AS lr""", c=c).data()
        out.append({"type": "T2", "seed": c,
                    "question": (f"¿De qué plugins depende {name_of(s, c)} ({c}) y cuáles de esas "
                                 f"dependencias llevan más de 3 años sin publicar una versión?"),
                    "gold": sorted(r["c"] for r in rows),
                    "gold_stale": sorted(r["c"] for r in rows
                                         if r["lr"] is not None and r["lr"] < C.STALE_CUTOFF_UNIX)})
    return out


def t3(s):
    pool = s.run("""MATCH (m:Maintainer)-[:MAINTAINS]->(p:Plugin {in_directory:true})
                    WITH p, collect(m) AS ms WHERE size(ms) <= 2
                    UNWIND ms AS m
                    MATCH (m)-[:MAINTAINS]->(o:Plugin) WHERE o <> p
                    WITH p, collect(DISTINCT o) AS os WHERE 2 <= size(os) <= 15
                    RETURN p.component AS c ORDER BY c""").data()
    out = []
    for c in rng("T3").sample([r["c"] for r in pool], N):
        rows = s.run("""MATCH (m:Maintainer)-[:MAINTAINS]->(p:Plugin {component:$c})
                        OPTIONAL MATCH (m)-[:MAINTAINS]->(o:Plugin) WHERE o <> p
                        RETURN m.display_name AS m, collect(DISTINCT o.component) AS os""", c=c).data()
        out.append({"type": "T3", "seed": c,
                    "question": f"¿Quién mantiene {name_of(s, c)} ({c}) y qué otros plugins mantiene?",
                    "gold": sorted({o for r in rows for o in r["os"]}),
                    "gold_maintainers": sorted(r["m"] for r in rows)})
    return out


def t4(s):
    risk = pd.read_csv(C.RISK_CSV)
    frag = risk[(risk.SM == 1) & (risk.ST == 1)].set_index("component")["E_exposicion"].to_dict()
    rows = s.run("""MATCH (p:Plugin {in_directory:true}) WHERE p.louvain_soc IS NOT NULL
                    RETURN p.component AS c, p.louvain_soc AS k""").data()
    comm = {}
    for r in rows:
        comm.setdefault(r["k"], []).append(r["c"])
    ok = sorted(k for k, cs in comm.items()
                if 10 <= len(cs) <= 150 and sum(c in frag for c in cs) >= 3)
    out = []
    r = rng("T4")
    for k in r.sample(ok, N):          # una semilla por comunidad distinta
        c = r.choice(sorted(comm[k]))
        fr = sorted((x for x in comm[k] if x in frag and x != c), key=lambda x: (-frag[x], x))
        out.append({"type": "T4", "seed": c, "community": int(k),
                    "question": (f"¿Qué plugins de la misma comunidad que {name_of(s, c)} ({c}) son "
                                 f"frágiles (un solo mantenedor y sin release en más de 3 años)?"),
                    "gold": fr[:10], "gold_all_fragile": fr})
    return out


def t5(s):
    pool = s.run("""MATCH (p:Plugin {in_directory:true})
                    WHERE p.last_release_ts < $cut AND p.installations >= 5
                    RETURN p.component AS c ORDER BY c""", cut=C.STALE_CUTOFF_UNIX).data()
    out = []
    for c in rng("T5").sample([r["c"] for r in pool], N):
        rows = s.run("""MATCH (p:Plugin {component:$c})-[:IN_CATEGORY]->(k:Category)<-[:IN_CATEGORY]-(o:Plugin)
                        WHERE o <> p AND o.last_release_ts >= $cut
                        RETURN k.code AS k, o.component AS o""", c=c, cut=C.STALE_CUTOFF_UNIX).data()
        out.append({"type": "T5", "seed": c,
                    "question": f"¿Qué alternativas mantenidas hay a {name_of(s, c)} ({c})?",
                    "category": rows[0]["k"] if rows else None,
                    "gold_constraint": "misma categoría ∧ last_release_ts >= STALE_CUTOFF_UNIX ∧ ≠ semilla",
                    "gold": [],       # T5 es una restricción, no una lista
                    "gold_satisfying": sorted(r["o"] for r in rows)})
    return out


# T6: control semántico. Conjuntos etiquetados a mano el 2026-09-28 a partir
# de las descripciones (cache/texts.jsonl), ANTES de ejecutar ningún sistema.
T6 = [
    ("¿Qué plugin sirve para generar certificados en PDF para los estudiantes al terminar un curso?",
     ["mod_certificate", "mod_customcert", "mod_simplecertificate", "mod_coursecertificate",
      "tool_certificate", "mod_easycertificate", "mod_certificatebeautiful", "mod_certifygen",
      "mod_certstudio", "mod_linkedincert"]),
    ("¿Qué plugin sirve para registrar la asistencia de los estudiantes a las clases?",
     ["mod_attendance", "block_attendance", "mod_attendancecontrol", "mod_subjectattendance",
      "block_autoattend", "mod_autoattendmod", "block_signinsheet", "local_attendance",
      "block_student_attendance"]),
    ("¿Qué plugin sirve para detectar plagio en las tareas entregadas por los estudiantes?",
     ["plagiarism_turnitin", "plagiarism_turnitinsim", "plagiarism_urkund", "plagiarism_compilatio",
      "plagiarism_unicheck", "plagiarism_unplag", "plagiarism_copyleaks", "plagiarism_originality",
      "plagiarism_plagiarismsearch", "plagiarism_crot", "plagiarism_crotpro", "plagiarism_vericite",
      "plagiarism_safeassign", "plagiarism_advacheck", "plagiarism_drillbit", "plagiarism_pchkorg",
      "plagiarism_copycheck", "plagiarism_strike", "plagiarism_plagium", "plagiarism_dupli",
      "plagiarism_sst", "plagiarism_edfast", "plagiarism_origai", "plagiarism_pd",
      "plagiarism_plagiarisma", "plagiarism_programming"]),
    ("¿Qué plugin sirve para hacer videoconferencias en vivo dentro de un curso?",
     ["mod_bigbluebuttonbn", "mod_zoom", "mod_jitsi", "mod_edumeet", "mod_alfaview",
      "mod_clickmeeting", "mod_teamviewerclassroom", "mod_videoconference", "mod_lessonspace",
      "block_zoomonline"]),
    ("¿Qué plugin sirve para que los estudiantes conversen con un chatbot de inteligencia artificial?",
     ["block_ai_chat", "mod_aichat", "block_openai_chat", "block_openai_chatbot", "block_moochat",
      "block_uteluqchatbot", "block_ube_ta", "block_openaiagent", "local_asyntai", "local_ulibot",
      "block_terusrag"]),
]


def t6(s):
    comps = {r["c"] for r in s.run("MATCH (p:Plugin) RETURN p.component AS c")}
    out = []
    for q, gold in T6:
        missing = [g for g in gold if g not in comps]
        assert not missing, missing
        out.append({"type": "T6", "seed": None, "question": q, "gold": sorted(gold)})
    return out


BUILDERS = {"T1": t1, "T2": t2, "T3": t3, "T4": t4, "T5": t5, "T6": t6}


def main():
    want = sys.argv[1:] or list(BUILDERS)
    existing = [json.loads(l) for l in C.GOLD.read_text().splitlines()] if C.GOLD.exists() else []
    have = {q["type"] for q in existing}
    new = []
    with C.driver() as d, d.session() as s:
        for t in want:
            if t in have:
                print(f"{t}: ya congelado, no se toca")
                continue
            qs = BUILDERS[t](s)
            print(f"{t}: {len(qs)} preguntas")
            new += qs
    allq = existing + new
    for i, q in enumerate(allq):
        q.setdefault("id", f"{q['type']}_{sum(1 for x in allq[:i] if x['type'] == q['type']) + 1}")
    with C.GOLD.open("w") as f:
        for q in allq:
            f.write(json.dumps(q, ensure_ascii=False) + "\n")
    h = hashlib.sha256(C.GOLD.read_bytes()).hexdigest()
    (C.GOLD.parent / "questions.sha256").write_text(f"{h}  questions.jsonl\n")
    print(f"{len(allq)} preguntas congeladas, sha256 {h[:16]}")


if __name__ == "__main__":
    main()
