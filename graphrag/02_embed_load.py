"""Paso 2: embeddings de documentos (cache .npy reanudable) + carga en Neo4j.

Crea (:PluginText {component, text, embedding})-[:DESCRIBES]->(:Plugin) y el
indice vectorial `plugintext_embedding` (cosine, 768). No toca :Plugin.
Borrado: ver README.md.
"""
import hashlib
import json
import sys

import numpy as np

import config as C

BATCH = 100


def main():
    docs = [json.loads(l) for l in C.TEXTS.read_text().splitlines()]
    hashes = [hashlib.sha256(d["text"].encode()).hexdigest()[:16] for d in docs]
    # cache: embeddings_index.json = [hash,...] alineado con embeddings.npy
    have = {}
    if C.EMB_NPY.exists():
        old = np.load(C.EMB_NPY)
        for h, v in zip(json.loads(C.EMB_IDX.read_text()), old):
            have[h] = v
    todo = [i for i, h in enumerate(hashes) if h not in have]
    print(f"{len(docs)} docs, {len(todo)} por embeber")
    for b in range(0, len(todo), BATCH):
        idx = todo[b:b + BATCH]
        vecs = C.embed_batch([docs[i]["text"] for i in idx], "RETRIEVAL_DOCUMENT")
        for i, v in zip(idx, vecs):
            have[hashes[i]] = v
        # guardado incremental (reanudable)
        ks = list(have)
        np.save(C.EMB_NPY, np.stack([have[k] for k in ks]))
        C.EMB_IDX.write_text(json.dumps(ks))
        print(f"  lote {b // BATCH + 1}: {len(have)}/{len(docs)}", flush=True)
    E = np.stack([have[h] for h in hashes])

    if "--no-load" in sys.argv:
        return
    rows = [{"c": d["component"], "t": d["text"], "e": E[i].tolist()} for i, d in enumerate(docs)]
    with C.driver() as drv, drv.session() as s:
        s.run("CREATE CONSTRAINT plugintext_component IF NOT EXISTS "
              "FOR (t:PluginText) REQUIRE t.component IS UNIQUE")
        for b in range(0, len(rows), 500):
            s.run("""UNWIND $rows AS r
                     MATCH (p:Plugin {component: r.c})
                     MERGE (t:PluginText {component: r.c})
                     SET t.text = r.t, t.model = $m
                     WITH t, p, r
                     CALL db.create.setNodeVectorProperty(t, 'embedding', r.e)
                     MERGE (t)-[:DESCRIBES]->(p)""", rows=rows[b:b + 500], m=C.EMBED_MODEL)
        s.run(f"""CREATE VECTOR INDEX {C.VECTOR_INDEX} IF NOT EXISTS
                  FOR (t:PluginText) ON (t.embedding)
                  OPTIONS {{indexConfig: {{`vector.dimensions`: {C.EMBED_DIM},
                                          `vector.similarity_function`: 'cosine'}}}}""")
        s.run("CALL db.awaitIndexes(300)")
        n = s.run("MATCH (t:PluginText)-[:DESCRIBES]->(:Plugin) RETURN count(t) AS n").single()["n"]
        print(f"PluginText cargados: {n}")
        # prueba de humo
        q = C.embed_query("plugin para generar certificados en PDF")
        res = s.run(f"CALL db.index.vector.queryNodes('{C.VECTOR_INDEX}', 5, $v) "
                    "YIELD node, score RETURN node.component AS c, score", v=q.tolist())
        print("humo 'certificados PDF':", [(r["c"], round(r["score"], 3)) for r in res])
    print(f"gasto acumulado estimado: US$ {C.spend():.4f}")


if __name__ == "__main__":
    main()
