# Preguntas libres — `preguntas_comunidad`

33 preguntas; con gold: 21 (explícito 21, por `gold_cypher` 0). Scorer: `score()` de `05_evaluate.py`; modelo `gemini-2.5-flash`.

| Sistema | n | F1 citas | Precisión | Recall | Recall contexto | Fidelidad (n def.) | Sin citas |
|---|---|---|---|---|---|---|---|
| vectorial | 21 | 0,81 | 0,86 | 0,81 | 0,90 | 1,00 (20) | 1 |
| vectorial + relaciones | 21 | 0,88 | 0,91 | 0,87 | 0,90 | 1,00 (20) | 1 |
| KG-RAG | 21 | 0,73 | 0,75 | 0,87 | 0,98 | 1,00 (19) | 2 |
| text-to-Cypher | 21 | 0,69 | 0,68 | 0,74 | 0,71 | 1,00 (16) | 5 |
| text-to-Cypher (filas directas) | 21 | 0,68 | 0,68 | 0,71 | 0,71 | 1,00 (16) | 5 |

Estado de las consultas text-to-Cypher (preguntas con gold): ok 16, empty 5

Por pregunta: `metrics_per_question.csv`.

| Sistema | Tokens entrada | Tokens salida | US$ (sin caché) |
|---|---|---|---|
| vectorial | 95326 | 2023 | 0,0337 |
| vectorial + relaciones | 114661 | 2206 | 0,0399 |
| KG-RAG | 125000 | 2942 | 0,0449 |
| text-to-Cypher | 120432 | 6398 | 0,0521 |
