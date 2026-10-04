# Resultados — línea base text-to-Cypher

Estado: **ejecutada** el 2026-10-04 sobre las mismas 30 preguntas T1–T6 (`gold/questions.jsonl`, sha256 `95cf7b4a51bece06…`, sin cambios) y puntuada con el **mismo scorer** (`score()` de `05_evaluate.py`) que los tres sistemas de [`RESULTS.md`](RESULTS.md). Responde a la sugerencia del tutor de añadir «una línea base que genere consultas Cypher». Las preguntas libres de una tercera persona se ejecutarán con `08_preguntas_libres.py` (formato en `README.md`).

Tablas generadas: `results/text2cypher/metrics.md`; por pregunta: `results/text2cypher/metrics_per_question.csv`; respuestas, consultas y trazas de reintento: `results/text2cypher/answers_{t2c,t2c_directo}.jsonl`. Las respuestas de los otros tres sistemas se leen de `results/full/` sin modificarlas.

## Configuración

| Elemento | Valor |
|---|---|
| Modelo | `gemini-2.5-flash`, temperature 0, thinkingBudget 0, 1 ejecución por pregunta (igual que los otros tres sistemas) |
| Entrada del LLM | esquema del grafo generado del catálogo de Neo4j y congelado en `cache/t2c_schema.txt` (≈2.700 tokens con la instrucción): etiquetas con nº de nodos, propiedades con tipo y tres valores de ejemplo, patrones de relación con nº de aristas, propiedades de las relaciones, una descripción breve de las propiedades clave (p. ej. `louvain_soc` = «comunidad» del análisis de riesgo) y la fecha de referencia del análisis (2026-09-10). Sin ejemplos *few-shot*: ninguna consulta de ejemplo reproduce las plantillas |
| Salida del LLM | **una** consulta Cypher en un bloque ```` ```cypher ```` |
| Salvaguardas | sesión y transacción de solo lectura (`execute_read`, `READ_ACCESS`; comprobado: un `CREATE` falla con `Neo.ClientError.Statement.AccessMode`); filtro previo de cláusulas de escritura (`CREATE`, `MERGE`, `DELETE`, `SET`, `REMOVE`, `DROP`, `LOAD CSV`, `FOREACH`…) y de cualquier `CALL` a un procedimiento fuera de una lista blanca de lectura (`apoc.*`, `dbms.*`, `gds.*` rechazados); timeout de transacción de 20 s (comprobado con una consulta combinatoria); `LIMIT 100` si falta; tope de 200 filas en el cliente |
| Reintento | uno, solo si Neo4j rechaza la consulta (sintaxis o semántica), con el mensaje de error en el prompt; un rechazo del filtro de seguridad no se reintenta |
| De filas a respuesta | **text-to-Cypher**: mismo prompt de sistema y misma plantilla que `04_answer.py`, con la consulta y las filas (JSON, hasta 100 filas / 12.000 caracteres) como contexto; si la consulta falla o no devuelve filas, la respuesta es una abstención fija sin llamada al LLM. **Filas directas** (variante sin LLM): se citan como `[component]` todos los plugins que aparecen en las filas |
| «Contexto» para el scorer | plugins cuyo `component` aparece literalmente en las filas (no hay K = 20; el «recall de contexto» no es un recall@20 estricto) |
| Caché | `cache/llm_t2c/` (55 respuestas) y `cache/usage_t2c.jsonl`; `T2C_OFFLINE=1 python 06_text2cypher.py` reproduce los ficheros sin llamar a la API (verificado) |

## Titular: preguntas relacionales con lista gold (T1–T4, n = 20)

| Sistema | F1 citas | Recall contexto | Precisión citas | Recall citas |
|---|---|---|---|---|
| Vectorial | 0,32 | 0,44 | 0,38 | 0,30 |
| Vectorial + relaciones | 0,47 | 0,44 | 0,55 | 0,44 |
| **Text-to-Cypher** | **0,71** | 0,66 | 0,74 | 0,69 |
| Text-to-Cypher (filas directas) | 0,68 | 0,66 | 0,70 | 0,66 |
| GraphRAG | **0,96** | 0,93 | 1,00 | 0,93 |

Contrastes pareados en T1–T4 (mismo procedimiento que `RESULTS.md`: 10.000 remuestreos, Wilcoxon exacto):

| Contraste | Δ F1 | IC pareado | IC estratificado | IC conglomerados | Wilcoxon p | G/E/P |
|---|---|---|---|---|---|---|
| Text-to-Cypher − vectorial | +0,39 | [+0,20; +0,60] | [+0,25; +0,54] | [+0,07; +0,72] | 0,002 | 10/10/0 |
| Text-to-Cypher − vect. + relaciones | +0,24 | [+0,08; +0,42] | [+0,15; +0,33] | [−0,03; +0,62] | 0,027 | 8/11/1 |
| Text-to-Cypher − GraphRAG | −0,25 | [−0,43; −0,09] | [−0,28; −0,21] | [−0,68; +0,00] | 0,016 | 0/13/7 |

### Por tipo (F1 de citas; T5: cumplimiento, no comparable)

| Tipo | Vectorial | Vect. + relaciones | GraphRAG | Text-to-Cypher | Filas directas |
|---|---|---|---|---|---|
| T1 Dependientes | 0,45 | 0,96 | 1,00 | **1,00** | 1,00 |
| T2 Dependencias + estado | 0,67 | 0,70 | 0,93 | 0,90 | 0,90 |
| T3 Co-mantenimiento | 0,15 | 0,15 | 1,00 | 0,94 | 0,80 |
| T4 Comunidad frágil | 0,00 | 0,07 | 0,89 | **0,00** | 0,00 |
| T5 Alternativas (cumplimiento) | 0,52 | 0,80 | 1,00 | 0,08 | 0,20 |
| **T6 Semántica (control)** | 0,67 | 0,66 | 0,61 | **0,00** | 0,00 |

## Fiabilidad de la consulta generada

| Indicador | Valor |
|---|---|
| Consultas ejecutadas con filas | 19/30 |
| Consultas válidas sin filas | 10/30 |
| **Fallo de ejecución tras el reintento** (error, rechazo o timeout) | **1/30 (3 %)** |
| Consulta sin resultado útil (fallo o 0 filas) | 11/30 (37 %); en T1–T4, 5/20, todas de T4 |
| Preguntas que necesitaron el reintento | 6/30 (5 pasan a ejecutarse sin error; 4 con filas) |
| Rechazos del filtro de seguridad / timeouts | 0 / 0 |

El error sintáctico apenas pesa (tras el reintento, 5 de 6 consultas se ejecutan sin error); lo que falla es la **semántica** de consultas que se ejecutan sin error:

1. **Dirección de las aristas.** El esquema dice `(:Maintainer)-[:MAINTAINS]->(:Plugin)`, pero en las cinco consultas de T4 (y en cuatro de T5) el modelo escribe `(p:Plugin)-[:MAINTAINS]->(m:Maintainer)`: la consulta es válida y devuelve 0 filas. En T3, partiendo del mismo nodo, escribe la flecha bien (`<-[:MAINTAINS]-`). Lo mismo con `DESCRIBES` en T6_4.
2. **Interpretación de la pregunta.** En T4, tres consultas restringen la comunidad a los vecinos `CO_MAINTAINED` de la semilla en lugar de usar solo `louvain_soc`; en T5 ninguna consulta traduce «mantenidas» como release reciente (lo interpreta como «tiene mantenedor»).
3. **Preguntas temáticas (T6).** Cuatro de cinco consultas filtran por un código de categoría inventado o mal elegido (`c.code = 'mod_certificate'`, `'antivirus'` para plagio); la única que busca en `PluginText.text` (T6_4) lo combina con un filtro de categoría y recorre `DESCRIBES` al revés. Sin similitud semántica, text-to-Cypher no tiene forma natural de responder.
4. **Fidelidad.** En T3_3 la consulta devolvió los nombres y no los `component`; el paso de formato los «tradujo» a identificadores, 4 de ellos inexistentes en el grafo (precisión 0,88, fidelidad 0). Es la única respuesta con citas fuera del contexto.

**Diagnóstico post hoc** (no es un sistema evaluado; `07_evaluate_t2c.py` lo recalcula sin API): invertir solo la flecha de `MAINTAINS`/`DESCRIBES` en las consultas afectadas no recupera **ninguna** de T4 (siguen vacías por la restricción `CO_MAINTAINED` o fallan por tipos de fecha), pero sí T5_1, T5_2, T5_5 y T6_4. El 0,00 de T4 no es un único error tipográfico, sino la acumulación de tres.

## Interpretación

- **Text-to-Cypher es una línea base fuerte en preguntas de un salto con el plugin nombrado**: iguala a GraphRAG en T1 (1,00), casi en T2 (0,90 frente a 0,93; mismo artefacto de autodependencia en T2_3) y en T3 (0,94 frente a 1,00). En esos tipos la consulta exacta es la herramienta natural y no necesita enrutador ni plantillas.
- **GraphRAG gana en el agregado** (0,96 frente a 0,71; 0/13/7, sin ninguna pregunta en que text-to-Cypher sea mejor) por T4, la pregunta de varios pasos (comunidad → filtro por nº de mantenedores y fecha), donde un único error de dirección o de interpretación deja la respuesta vacía. GraphRAG no puede equivocarse ahí porque la expansión es código fijo: es exactamente la ventaja (y la limitación) de su enrutador por palabras clave, que comparte vocabulario con las plantillas.
- **Los fallos son binarios**: text-to-Cypher acierta de pleno o devuelve 0 filas (13 empates y 7 derrotas frente a GraphRAG; solo T2_2, T2_3 y T3_3 quedan en valores intermedios). El IC por conglomerados, con solo 4 plantillas, cruza el 0 ([−0,68; +0,00]): la diferencia con GraphRAG depende casi entera de una plantilla.
- **En el control semántico (T6) text-to-Cypher fracasa** (0,00 frente a 0,61–0,67): el grafo no tiene similitud semántica accesible desde Cypher sin el vector de la pregunta. Es el argumento a favor de la arquitectura híbrida: el vector para enlazar y la estructura para recorrer.
- **El paso de formato con LLM apenas añade** (0,71 frente a 0,68 de las filas directas; la diferencia es T3_3, donde el LLM corrige la consulta… con identificadores en parte inventados).
- **Coste**: ≈ 3.800 tokens de entrada por pregunta (dos llamadas o más) frente a ≈ 3.200 de los sistemas RAG (una llamada): text-to-Cypher no es más barato aquí, porque el esquema (≈2.700 tokens con la instrucción) se envía en cada pregunta.
- Con preguntas libres cabe esperar que **ambos** sistemas bajen: GraphRAG pierde el enrutador alineado con las plantillas y text-to-Cypher pierde el `component` literal en la pregunta (en una prueba de humo con «el plugin de Dataform» la consulta filtró por `name` y volvió a invertir la flecha).

## Limitaciones

- Mismas que `RESULTS.md` (n = 20 en el titular, plantillas del propio autor, verdad-terreno del mismo grafo, una ejecución por pregunta sin medir varianza), más: un único diseño de prompt, sin *few-shot*, sin autocorrección ante 0 filas (solo ante error de Neo4j). Un sistema text-to-Cypher afinado (ejemplos de consulta, validación de dirección contra el esquema, reintento ante resultado vacío) probablemente cerraría parte de la distancia en T4 y T5; no se ha hecho para no ajustar la línea base sobre el conjunto de evaluación.
- Las descripciones del esquema las escribió el autor conociendo las plantillas (p. ej. que `louvain_soc` es la «comunidad»); es información que tendría cualquier documentación del grafo, pero favorece a text-to-Cypher.
- El «recall de contexto» de text-to-Cypher no es comparable al recall@20 de los otros tres sistemas (no hay K fijo: hasta 100 plugins en T5).

## Gasto API

| Paso | Llamadas | Tokens entrada | Tokens salida | US$ |
|---|---|---|---|---|
| Generación de Cypher (incl. 6 reintentos) | 36 | 104.395 | 4.672 | 0,043 |
| Formato de la respuesta | 19 | 10.587 | 2.267 | 0,009 |
| **Total** | 55 | 114.982 | 6.939 | **0,052** |

Mismo método que el prototipo: tokens de `usageMetadata` × precios de `config.py` (0,30 / 2,50 US$ por M tokens). Una prueba de humo de `08_preguntas_libres.py` con dos preguntas de ensayo costó ≈ 0,01 US$ adicionales; sus ficheros se borraron. Las re-ejecuciones leen la caché y cuestan 0.
