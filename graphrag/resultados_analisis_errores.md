<!-- No editar a mano: generado por 12_analisis_errores.py -->

# Análisis de errores: preguntas de la comunidad

Causa principal de cada respuesta no aceptable (parcial, incorrecta o abstención incorrecta), asignada con reglas deterministas en orden de prioridad (docstring de `12_analisis_errores.py`). Detalle por respuesta en `results/libres/preguntas_comunidad/analisis_errores.csv`.

| Causa principal | RAG vectorial | Vectorial + relaciones | KG-RAG | Text-to-Cypher | Total |
|---|---|---|---|---|---|
| Plugin ausente del directorio | 1 | 1 | 1 | 1 | 4 |
| Dirección de la relación invertida | 0 | 0 | 0 | 5 | 5 |
| Compatibilidad con versiones (dato ausente del contexto) | 15 | 14 | 14 | 0 | 43 |
| Consulta sin filas (nombre o filtro inventado) | 0 | 0 | 0 | 4 | 4 |
| Idioma: enrutado por intención solo en español | 0 | 0 | 3 | 0 | 3 |
| Otra (enlazado erróneo, inferencia incorrecta) | 2 | 3 | 0 | 4 | 9 |
| **Respuestas no aceptables** | 18 | 18 | 18 | 14 | 68 |

Preguntas en inglés: 30 de 33. Preguntas cuya referencia necesita las versiones soportadas (regla 3): 17. Preguntas con plugin ausente (regla 1): 5.

- `plugin_ausente`: P02
- `direccion_relacion`: C01, C02, P01, P04, P08
- `compatibilidad`: C01, C03, C04, C09, C10, C12, C13, C14, C15, C16, C17, C18, C19, P01, P03
- `consulta_vacia`: C03, C13, C16, C19
- `idioma_enrutado`: C05, C11, N05
- `otra`: C04, C05, C07, C11, N05, P06

## Text-to-Cypher frente a cada sistema RAG: respuestas aceptables (33 preguntas, pareado)

| Contraste | Solo text-to-Cypher aceptable | Solo el RAG aceptable | p (McNemar exacto) |
|---|---|---|---|
| Text-to-Cypher − RAG vectorial | 9 | 5 | 0,424 |
| Text-to-Cypher − Vectorial + relaciones | 10 | 6 | 0,454 |
| Text-to-Cypher − KG-RAG | 10 | 6 | 0,454 |
