<!-- No editar a mano: generado por 10_acuerdo_humano.py kappa -->

# Acuerdo entre el juez LLM y un evaluador humano (preguntas de la comunidad)

Submuestra de 15 de las 33 preguntas, estratificada por `respondible` (semilla 20261007; `muestra_humana.json`), elegida antes de ver ninguna etiqueta. 60 respuestas (4 por pregunta) juzgadas a ciegas por una persona con la misma rúbrica, la misma referencia y el mismo criterio que el juez LLM (`claude-opus-5-5`), con las mismas letras A-D y sin acceso a la clave ni a las etiquetas del LLM. Preguntas: C01, C02, C04, C05, C06, C07, C11, C12, C14, C17, N01, N02, N04, P04, P07.

## Acuerdo

| Escala | Acuerdo observado | Kappa de Cohen | IC 95% (bootstrap por pregunta) |
|---|---|---|---|
| Cinco etiquetas | 33,3% | 0,13 | [-0,00; 0,26] |
| Aceptable / no aceptable | 86,7% | 0,72 | [0,43; 0,93] |

Bootstrap: 10000 remuestreos de preguntas (las 4 respuestas de una pregunta van juntas).

## Matriz de confusión (filas: humano; columnas: LLM)

| humano \ LLM | correcta | parcial | incorrecta | abstencion_correcta | abstencion_incorrecta |
|---|---|---|---|---|---|
| correcta | 16 | 6 | 0 | 16 | 1 |
| parcial | 1 | 3 | 1 | 0 | 3 |
| incorrecta | 0 | 3 | 0 | 0 | 7 |
| abstencion_correcta | 1 | 0 | 0 | 0 | 0 |
| abstencion_incorrecta | 0 | 1 | 0 | 0 | 1 |

## Respuestas aceptables por sistema en la submuestra

| Sistema | n | Aceptables según el LLM | Aceptables según el humano | Desacuerdos |
|---|---|---|---|---|
| RAG vectorial | 15 | 9 (60%) | 9 (60%) | 10 |
| Vectorial + relaciones | 15 | 8 (53%) | 9 (60%) | 9 |
| KG-RAG | 15 | 8 (53%) | 11 (73%) | 11 |
| Text-to-Cypher | 15 | 9 (60%) | 11 (73%) | 10 |

Orden por aceptables, LLM: RAG vectorial > Text-to-Cypher > Vectorial + relaciones > KG-RAG; humano: KG-RAG > Text-to-Cypher > RAG vectorial > Vectorial + relaciones.

## Desacuerdos

| Pregunta | Letra | Sistema | Humano | LLM |
|---|---|---|---|---|
| C01 | A | KG-RAG | correcta | parcial |
| C01 | B | Text-to-Cypher | incorrecta | parcial |
| C02 | A | KG-RAG | abstencion_correcta | correcta |
| C02 | B | RAG vectorial | parcial | correcta |
| C02 | D | Text-to-Cypher | incorrecta | parcial |
| C04 | A | RAG vectorial | parcial | abstencion_incorrecta |
| C04 | B | Vectorial + relaciones | parcial | abstencion_incorrecta |
| C04 | D | Text-to-Cypher | abstencion_incorrecta | parcial |
| C05 | A | Text-to-Cypher | correcta | parcial |
| C05 | B | KG-RAG | correcta | parcial |
| C05 | C | RAG vectorial | correcta | parcial |
| C05 | D | Vectorial + relaciones | correcta | parcial |
| C06 | A | KG-RAG | correcta | abstencion_correcta |
| C06 | B | Text-to-Cypher | correcta | abstencion_correcta |
| C06 | C | RAG vectorial | correcta | abstencion_correcta |
| C06 | D | Vectorial + relaciones | correcta | abstencion_correcta |
| C07 | D | Text-to-Cypher | incorrecta | parcial |
| C11 | A | KG-RAG | incorrecta | abstencion_incorrecta |
| C11 | B | Vectorial + relaciones | incorrecta | abstencion_incorrecta |
| C12 | A | RAG vectorial | incorrecta | abstencion_incorrecta |
| C12 | B | Vectorial + relaciones | incorrecta | abstencion_incorrecta |
| C12 | C | KG-RAG | correcta | abstencion_incorrecta |
| C14 | A | KG-RAG | parcial | abstencion_incorrecta |
| C14 | D | RAG vectorial | parcial | incorrecta |
| C17 | A | RAG vectorial | incorrecta | abstencion_incorrecta |
| C17 | B | KG-RAG | incorrecta | abstencion_incorrecta |
| C17 | D | Vectorial + relaciones | incorrecta | abstencion_incorrecta |
| N01 | A | RAG vectorial | correcta | abstencion_correcta |
| N01 | B | Vectorial + relaciones | correcta | abstencion_correcta |
| N01 | C | Text-to-Cypher | correcta | abstencion_correcta |
| N01 | D | KG-RAG | correcta | abstencion_correcta |
| N02 | A | RAG vectorial | correcta | abstencion_correcta |
| N02 | B | Text-to-Cypher | correcta | abstencion_correcta |
| N02 | C | Vectorial + relaciones | correcta | abstencion_correcta |
| N02 | D | KG-RAG | correcta | abstencion_correcta |
| N04 | A | RAG vectorial | correcta | abstencion_correcta |
| N04 | B | Text-to-Cypher | correcta | abstencion_correcta |
| N04 | C | KG-RAG | correcta | abstencion_correcta |
| N04 | D | Vectorial + relaciones | correcta | abstencion_correcta |
| P04 | D | Text-to-Cypher | correcta | parcial |
