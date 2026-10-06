# Prototipo KG-RAG — cómo reconstruir y cómo deshacer

> **Nombre.** En la memoria este prototipo se llama **KG-RAG**: recupera sobre un grafo analítico ya construido, a diferencia del GraphRAG de Edge et al. (2024), que construye el grafo a partir de texto con un modelo de lenguaje. El directorio, el código, la etiqueta de sistema `graphrag` y los primeros informes (`PLAN.md`, `RESULTS.md`, `resultados_text2cypher.md`) conservan el nombre «GraphRAG»; se refieren al mismo sistema.

Especificación: [`PLAN.md`](PLAN.md). Resultados: [`RESULTS.md`](RESULTS.md). Línea base text-to-Cypher: [`resultados_text2cypher.md`](resultados_text2cypher.md). Preguntas reales de la comunidad: [`resultados_preguntas_comunidad.md`](resultados_preguntas_comunidad.md).

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
../.venv/bin/python 06_text2cypher.py           # línea base text-to-Cypher: results/text2cypher/answers_{t2c,t2c_directo}.jsonl
../.venv/bin/python 07_evaluate_t2c.py          # los 5 sistemas con el mismo scorer: results/text2cypher/metrics.md
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

## Línea base text-to-Cypher (`text2cypher.py`, `06`, `07`)

El LLM (mismo `gemini-2.5-flash`, temperature 0, thinkingBudget 0) recibe el esquema congelado en `cache/t2c_schema.txt` (etiquetas, relaciones, propiedades con tres valores de ejemplo y una descripción breve; `06_text2cypher.py --schema` lo imprime) y la pregunta, y genera **una** consulta Cypher. Salvaguardas: sesión y transacción de solo lectura (`execute_read`, modo `READ`; Neo4j rechaza cualquier escritura con `Neo.ClientError.Statement.AccessMode`), filtro previo de `CREATE/MERGE/DELETE/SET/REMOVE/DROP/LOAD CSV/FOREACH` y de cualquier `CALL` a procedimientos fuera de una lista blanca de lectura (`apoc.*`, `dbms.*`, `gds.*` rechazados), timeout de transacción de 20 s, `LIMIT 100` añadido si falta y tope de 200 filas en el cliente. Si Neo4j rechaza la consulta (sintaxis o semántica) hay **un** reintento con el error en el prompt. Las filas se convierten en respuesta de dos formas: `t2c` (mismo prompt de sistema y plantilla que `04_answer.py`, con las filas como contexto) y `t2c_directo` (sin LLM: cita todos los plugins de las filas). Caché propia en `cache/llm_t2c/` y gasto en `cache/usage_t2c.jsonl`; `T2C_OFFLINE=1` aborta ante un fallo de caché, lo que garantiza que una re-ejecución no llama a la API. `07_evaluate_t2c.py` puntúa con `score()` de `05_evaluate.py` y lee las respuestas de `results/full/` sin modificarlas.

## Preguntas libres (`08_preguntas_libres.py`)

Para pasar preguntas redactadas por otra persona por los cuatro sistemas:

```bash
../.venv/bin/python 08_preguntas_libres.py preguntas_libres.yaml            # también .csv o .jsonl
../.venv/bin/python 08_preguntas_libres.py preguntas_libres.yaml --systems graphrag,t2c
```

Formato (`preguntas_libres.yaml` es la plantilla vacía con dos ejemplos comentados). Una entrada por pregunta; solo `pregunta` es obligatoria:

| Campo | Contenido |
|---|---|
| `id` | identificador corto (por defecto `L01`, `L02`…) |
| `pregunta` | texto literal, tal como lo escribió la persona |
| `autor` | quién la redactó (opcional) |
| `seed` | `component` del plugin nombrado, si lo hay; se excluye del gold y de las citas, como en T1–T5 |
| `gold` | lista de `component` correctos (opcional) |
| `gold_cypher` | consulta Cypher de solo lectura, escrita a mano, que devuelve una columna `component`; se ejecuta con las mismas salvaguardas y da el gold si no hay `gold` explícito (si hay ambos, manda el explícito y se avisa si difieren) |
| `notas` | criterio usado para el gold, ambigüedades |

En CSV: columnas `id,pregunta,autor,seed,gold,gold_cypher,notas`, con `gold` separado por `;`. Las preguntas con gold se puntúan con `score()` de `05_evaluate.py` (tipo `L`, F1 de citas); las que no lo tienen solo se guardan para revisión manual. Salida en `results/libres/<nombre del fichero>/` (`gold_resuelto.jsonl` con su sha256, `answers_<sistema>.jsonl`, `metrics.md`, `metrics_per_question.csv`). Caché separada (`cache/llm_libres/`, `cache/qemb_libres/`, `cache/usage_libres.jsonl`): la del experimento T1–T6 no se toca. Recomendación: fijar el gold (o la `gold_cypher`) **antes** de ejecutar ningún sistema y no reformular las preguntas.

## Preguntas reales de la comunidad (`preguntas_comunidad.yaml`, `09_eval_comunidad.py`)

33 preguntas publicadas entre 2019 y 2026 por miembros de la comunidad Moodle (foros de moodle.org vía copias de la Wayback Machine, Moodle Tracker e issues de GitHub de los plugins), con su URL, autor y fecha. Para cada una, `preguntas_comunidad.yaml` fija una consulta Cypher de referencia, la respuesta de referencia derivada de ella, las citas esperadas y el criterio de juicio; el fichero se congeló con su sha256 (`preguntas_comunidad.sha256`) antes de ejecutar ningún sistema. Orden de ejecución (el orden es lo que hace honesta la evaluación):

```bash
../.venv/bin/python 09_eval_comunidad.py gold                          # verifica el sha256 y ejecuta en solo lectura las consultas de referencia
../.venv/bin/python 08_preguntas_libres.py preguntas_comunidad.yaml    # los cuatro sistemas (desde la caché, sin llamar a la API)
../.venv/bin/python 09_eval_comunidad.py blind                         # baraja las 4 respuestas de cada pregunta (semilla 20261004)
# juicio sobre results/libres/preguntas_comunidad/juicio_ciego.md -> etiquetas_ciego.csv, sin abrir la clave
../.venv/bin/python 09_eval_comunidad.py report                        # desciega y escribe resultados_preguntas_comunidad.md
```

Las etiquetas del juicio están versionadas (`etiquetas_ciego.csv`, `etiquetas_descegadas.csv`), de modo que `report` reproduce las tablas sin repetir el juicio. El juicio lo hizo un único evaluador, un agente basado en un LLM, que también redactó las respuestas de referencia y los criterios; las limitaciones de esta evaluación están en `resultados_preguntas_comunidad.md`.
