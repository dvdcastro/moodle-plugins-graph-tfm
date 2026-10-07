<!-- No editar a mano: generado por 13_enrutador_bilingue.py report -->

# KG-RAG con enrutador bilingüe (ejecución exploratoria)

Las 33 preguntas ya se conocían cuando se escribió la variante: el resultado es exploratorio y no sustituye a los resultados principales (`resultados_preguntas_comunidad.md`). Expresiones inglesas traducidas de las españolas y validadas con las plantillas T1-T5 traducidas (docstring).

| Medida | Enrutador original | Enrutador bilingüe |
|---|---|---|
| Preguntas con alguna intención detectada | 1 de 33 | 7 de 33 |
| Respuestas aceptables (de 33) | 15 (45%) | 15 (45%) |
| F1 de citas (n = 21) | 0,73 | 0,73 |

Respuestas que cambian: 6. Juicio ciego por pares (original frente a bilingüe, barajadas), con la misma rúbrica; en las que no cambian se mantiene la etiqueta del juicio principal. Consistencia del juez al volver a juzgar la respuesta original: 1,00 (6 respuestas).

Llamadas nuevas a la API registradas en `cache/usage_bilingue.jsonl`: 6.
