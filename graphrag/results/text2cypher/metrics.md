# Métricas — línea base text-to-Cypher frente a los tres sistemas

Gold: `gold/questions.jsonl` (sha256 `95cf7b4a51bece06…`), 30 preguntas. Mismo scorer (`score()` de `05_evaluate.py`), mismo modelo `gemini-2.5-flash` (temperature 0, thinkingBudget 0). Las respuestas de los tres sistemas previos se leen de `results/full/` sin modificarlas. Para text-to-Cypher, el «contexto» del scorer son los plugins que aparecen en las filas devueltas (hasta 200; no hay K = 20), de modo que su recall de contexto no es un recall@20 estricto.

## Titular: T1–T4 (n = 20)

| Sistema | F1 citas | Recall contexto | Precisión citas | Recall citas |
|---|---|---|---|---|
| vectorial | 0,32 | 0,44 | 0,38 | 0,30 |
| vectorial + relaciones | 0,47 | 0,44 | 0,55 | 0,44 |
| GraphRAG | 0,96 | 0,93 | 1,00 | 0,93 |
| text-to-Cypher | 0,71 | 0,66 | 0,74 | 0,69 |
| text-to-Cypher (filas directas) | 0,68 | 0,66 | 0,70 | 0,66 |

## F1 de citas por tipo (T5: cumplimiento de la restricción, no comparable)

| Tipo | n | vectorial | vectorial + relaciones | GraphRAG | text-to-Cypher | text-to-Cypher (filas directas) |
|---|---|---|---|---|---|---|
| T1 Dependientes | 5 | 0,45 | 0,96 | 1,00 | 1,00 | 1,00 |
| T2 Dependencias | 5 | 0,67 | 0,70 | 0,93 | 0,90 | 0,90 |
| T3 Co-mantenimiento | 5 | 0,15 | 0,15 | 1,00 | 0,94 | 0,80 |
| T4 Comunidad frágil | 5 | 0,00 | 0,07 | 0,89 | 0,00 | 0,00 |
| T5 Alternativas | 5 | 0,52 | 0,80 | 1,00 | 0,08 | 0,20 |
| T6 Semántica (control) | 5 | 0,67 | 0,66 | 0,61 | 0,00 | 0,00 |
| T1–T4 | 20 | 0,32 | 0,47 | 0,96 | 0,71 | 0,68 |
| T1–T4 + T6 | 25 | 0,39 | 0,51 | 0,89 | 0,57 | 0,54 |

## Contrastes pareados en T1–T4 (F1; Δ = segundo − primero)

| Contraste | Δ | IC pareado | IC estratificado | IC conglomerados | Wilcoxon exacto p | G/E/P |
|---|---|---|---|---|---|---|
| text-to-Cypher − GraphRAG | −0,25 | [−0,43; −0,09] | [−0,28; −0,21] | [−0,68; +0,00] | 0,016 | 0/13/7 |
| text-to-Cypher − vectorial | +0,39 | [+0,20; +0,60] | [+0,25; +0,54] | [+0,07; +0,72] | 0,002 | 10/10/0 |
| text-to-Cypher − vectorial + relaciones | +0,24 | [+0,08; +0,42] | [+0,15; +0,33] | [−0,03; +0,62] | 0,027 | 8/11/1 |
| text-to-Cypher (filas directas) − text-to-Cypher | −0,04 | [−0,11; +0,00] | [−0,11; +0,00] | [−0,14; +0,00] | 1,000 | 0/19/1 |

Control T6, text-to-Cypher − vectorial: Δ −0,67 [−0,78; −0,61], G/E/P 0/0/5.

## Fiabilidad de la consulta generada (30 preguntas)

| Indicador | Valor |
|---|---|
| Consultas ejecutadas con filas | 19/30 |
| Consultas válidas sin filas | 10/30 |
| Fallo tras el reintento (error/rechazo/timeout) | 1/30 (3 %) |
| Preguntas que usaron el reintento | 6/30 |
| Rechazadas por el filtro de seguridad | 0 |
| Timeouts | 0 |
| Plugins en las filas (mediana; máx.) | 2; 100 |

Estado por tipo: T1: ok 5; T2: ok 5; T3: ok 5; T4: empty 4, error 1; T5: empty 3, ok 2; T6: empty 3, ok 2

## Diagnóstico post hoc: dirección de las aristas (no es un sistema evaluado)

Consultas que recorren `MAINTAINS` o `DESCRIBES` en sentido contrario al esquema. Se re-ejecutan sin LLM tras invertir solo esa flecha y se puntúan las filas como en «filas directas». Mide cuánto del fallo se debe a ese error concreto.

| Pregunta | Estado original | Estado corregido | Plugins | Métrica original | Métrica corregida |
|---|---|---|---|---|---|
| T4_1 | error | error (CypherSyntaxError) | 0 | 0,00 | 0,00 |
| T4_2 | empty | empty | 0 | 0,00 | 0,00 |
| T4_3 | empty | error (CypherTypeError) | 0 | 0,00 | 0,00 |
| T4_4 | empty | empty | 0 | 0,00 | 0,00 |
| T4_5 | empty | error (CypherTypeError) | 0 | 0,00 | 0,00 |
| T5_1 | empty | ok | 48 | 0,00 | 0,27 |
| T5_2 | empty | ok | 100 | 0,00 | 0,57 |
| T5_4 | ok | ok | 48 | 0,60 | 0,60 |
| T5_5 | empty | ok | 48 | 0,00 | 0,60 |
| T6_4 | empty | ok | 9 | 0,00 | 0,32 |

(Métrica: F1 de citas; en T5, cumplimiento de la restricción.)

## Coste API (tokens de `usageMetadata` × precios de `config.py`)

| Paso | Llamadas | Tokens entrada | Tokens salida | US$ |
|---|---|---|---|---|
| Generación de Cypher (incl. reintentos) | 36 | 104.395 | 4.672 | 0,0430 |
| Formato de la respuesta | 19 | 10.587 | 2.267 | 0,0088 |
| **Total text-to-Cypher** | 55 | 114.982 | 6.939 | **0,0518** |

Tokens de entrada por pregunta: text-to-Cypher 3.833 (dos llamadas o más), sistemas RAG 3.160 (una llamada). Las re-ejecuciones leen `cache/llm_t2c/` y cuestan 0.
