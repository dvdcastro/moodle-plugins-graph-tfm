"""Paso 6: linea base text-to-Cypher sobre las 30 preguntas gold (T1-T6).

Uso: python 06_text2cypher.py            -> results/text2cypher/answers_{t2c,t2c_directo}.jsonl
     T2C_OFFLINE=1 python 06_text2cypher.py   (solo cache; aborta si falta una respuesta)
     python 06_text2cypher.py --schema   (imprime el esquema que ve el LLM y sale)
El sistema solo ve la pregunta (nunca el gold). Ver text2cypher.py.
"""
import json
import sys

import config as C
import text2cypher as T

OUT = C.RESULTS / "text2cypher"


def main():
    t2c = T.Text2Cypher()
    if "--schema" in sys.argv:
        print(t2c.schema)
        return
    OUT.mkdir(parents=True, exist_ok=True)
    qs = [json.loads(l) for l in C.GOLD.read_text().splitlines()]
    try:
        with (OUT / "answers_t2c.jsonl").open("w") as fa, \
                (OUT / "answers_t2c_directo.jsonl").open("w") as fb:
            for q in qs:
                a, b = t2c.answer(q["question"])
                for rec, f in ((a, fa), (b, fb)):
                    f.write(json.dumps({"id": q["id"], "type": q["type"], **rec},
                                       ensure_ascii=False, default=str) + "\n")
                print(f"{q['id']:5s} {a['status']:8s} retry={int(a['retried'])} "
                      f"filas={a['n_rows']:3d} plugins={len(a['components']):3d}", flush=True)
    finally:
        t2c.close()
    usages = []
    for line in (OUT / "answers_t2c.jsonl").read_text().splitlines():
        r = json.loads(line)
        usages += r["usage_gen"] + [r["usage"]]
    pin, pout, usd = T.cost(usages)
    print(f"tokens entrada {pin}, salida {pout}; coste de esta ejecución (sin caché): US$ {usd:.4f}")


if __name__ == "__main__":
    main()
