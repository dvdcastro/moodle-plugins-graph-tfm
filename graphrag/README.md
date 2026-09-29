# Prototipo GraphRAG — cómo reconstruir y cómo deshacer

Especificación: [`PLAN.md`](PLAN.md). Resultados: [`RESULTS.md`](RESULTS.md).

## Requisitos

- `.venv` del repo (bs4, lxml, neo4j, pandas, scipy, matplotlib, requests). **No** se añadió ninguna dependencia: Gemini se llama por REST con `requests`.
- `.env` en la raíz (gitignored) con `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`, `GEMINI_API_KEY`.
- Neo4j 5.26 con el grafo de plugins ya cargado (`:Plugin {component}`).

## Reconstrucción (desde la raíz del repo, `cd graphrag`)

```bash
../.venv/bin/python 01_extract_text.py          # HTML -> cache/texts.jsonl (≈45 s, sin API)
../.venv/bin/python 02_embed_load.py            # embeddings (cache/embeddings.npy) + :PluginText + índice vectorial
../.venv/bin/python 03_build_gold.py T1 T3 T6   # gold de la línea de corte (NO reescribe tipos ya congelados)
../.venv/bin/python 03_build_gold.py T2 T4 T5   # extensión al plan completo
../.venv/bin/python 04_answer.py cutline        # results/cutline/answers_*.jsonl
../.venv/bin/python 04_answer.py full           # results/full/answers_{baseline,graphrag}.jsonl
../.venv/bin/python 04_answer.py full vecrel    # ablación «vectorial + relaciones»: results/full/answers_vecrel.jsonl
../.venv/bin/python 05_evaluate.py full --figure  # metrics.md, metrics_per_question.csv, ../figures/graphrag_resultados.png
```

Las respuestas de Gemini están cacheadas en `cache/llm/` y los embeddings de consulta en `cache/qemb/` (ambos versionados): `05_evaluate.py` reproduce exactamente los números a partir de las respuestas versionadas en `results/`. Una re-ejecución de `04` también sale de la caché salvo en 12 de las 120 respuestas: en la versión publicada los correos de las páginas del directorio se sustituyeron por `[email]`, lo que cambia la ficha de 12 plugins (y el texto embebido de 171) y, con ella, la instrucción enviada al modelo; esas respuestas se regenerarían con la API. `cache/texts.jsonl` y `cache/embeddings.npy` (≈11 MB) no se versionan; `02_embed_load.py` los regenera (coste ≈0,17 US$). Gasto registrado en `cache/usage.jsonl` (el de embeddings es una estimación chars/4, la API no devuelve tokens).

El gold (`gold/questions.jsonl`) se congela con su sha256 en `gold/questions.sha256`; `05_evaluate.py` aborta si no coincide.

## Qué se añadió a Neo4j (y nada más)

- Nodos `:PluginText {component, text, embedding (768 floats), model}` — 2.888.
- Relaciones `(:PluginText)-[:DESCRIBES]->(:Plugin)` — 2.888.
- Restricción de unicidad `plugintext_component` e índice vectorial `plugintext_embedding` (coseno, 768).

No se escribe ninguna propiedad en `:Plugin` ni se toca ninguna relación existente. Los índices de riesgo (`riesgo_exposicion_T3.csv`) se leen con pandas, no se escriben en el grafo.

## Cómo borrarlo todo

```cypher
DROP INDEX plugintext_embedding IF EXISTS;
DROP CONSTRAINT plugintext_component IF EXISTS;
MATCH (t:PluginText) DETACH DELETE t;
```
