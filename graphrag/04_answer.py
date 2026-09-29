"""Paso 4: recuperar contexto y generar respuestas con ambos sistemas.

Uso: python 04_answer.py cutline   -> expansiones DEPENDS_ON + MAINTAINS, results/cutline/
     python 04_answer.py full      -> todas las expansiones, results/full/
     python 04_answer.py full vecrel  -> solo la ablacion "vectorial + relaciones"
                                         (results/full/answers_vecrel.jsonl)
Requiere gold/questions.jsonl congelado (el gold no se lee aqui salvo la
pregunta: el sistema nunca ve la verdad-terreno).
"""
import json
import sys

import config as C
from retrieval import ALL_EXPANSIONS, Retriever

SYSTEM = (
    "Eres un asistente para administradores de Moodle. Responde en español, de forma "
    "concisa, usando EXCLUSIVAMENTE la información del contexto proporcionado (fichas de "
    "plugins y, si las hay, relaciones del grafo). Cada vez que menciones un plugin, cítalo "
    "con su identificador exacto entre corchetes, por ejemplo [mod_customcert]. No cites "
    "plugins que no aparezcan en el contexto. Si el contexto no permite responder, dilo.")

TEMPLATE = "CONTEXTO:\n{ctx}\n\nPREGUNTA: {q}\n\nRespuesta (cita cada plugin como [component]):"


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "cutline"
    exps = ("in", "out", "maint") if mode == "cutline" else ALL_EXPANSIONS
    types = {"T1", "T3", "T6"} if mode == "cutline" else None
    outdir = C.RESULTS / mode
    outdir.mkdir(parents=True, exist_ok=True)
    qs = [json.loads(l) for l in C.GOLD.read_text().splitlines()]
    qs = [q for q in qs if types is None or q["type"] in types]
    R = Retriever(exps)
    try:
        systems = sys.argv[2:] or ["baseline", "graphrag"]
        fetch = {"baseline": R.baseline, "graphrag": R.graphrag, "vecrel": R.vector_rel}
        for system in systems:
            with (outdir / f"answers_{system}.jsonl").open("w") as f:
                for q in qs:
                    ret = fetch[system](q["question"])
                    ctx = R.context(ret)
                    resp = C.generate(SYSTEM, TEMPLATE.format(ctx=ctx, q=q["question"]))
                    rec = {"id": q["id"], "type": q["type"], "system": system,
                           "question": q["question"], **ret,
                           "context_chars": len(ctx), "answer": resp["text"],
                           "finish_reason": resp["finish_reason"],
                           "model": resp["model"], "model_version": resp["model_version"],
                           "usage": resp["usage"]}
                    f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                    print(f"{system:8s} {q['id']:5s} ctx={len(ctx):5d} "
                          f"link={ret.get('link_method')} {ret.get('seeds')}", flush=True)
    finally:
        R.close()
    print(f"gasto acumulado estimado: US$ {C.spend():.4f}")


if __name__ == "__main__":
    main()
