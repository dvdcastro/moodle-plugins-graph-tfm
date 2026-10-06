# Resultados — prototipo GraphRAG sobre el grafo de plugins de Moodle

> En la memoria este prototipo se llama **KG-RAG** (ver la nota de nombre en `README.md`); «GraphRAG» en este informe designa el mismo sistema.

Estado: **plan completo** (PLAN.md §3), revisado tras una revisión independiente: titular restringido a T1–T4, T5 aparte, ablación «vectorial + relaciones» y desviaciones documentadas. 30 preguntas en 6 tipos, tres sistemas. La versión de línea de corte (15 preguntas) se conserva en `results/cutline/`.

Figura: `../figures/graphrag_resultados.png` (14,6 cm, 300 dpi). Tablas generadas: `results/full/metrics.md`; por pregunta: `results/full/metrics_per_question.csv`; respuestas: `results/full/answers_{baseline,vecrel,graphrag}.jsonl`.

## Configuración

| Elemento | Valor |
|---|---|
| Documentos | 2.888 páginas del directorio → un documento por plugin (nombre + component + tipo + `og:description` + descripción larga), truncado a 6.000 caracteres (76 truncados, 103 sin descripción larga, 12 sin `og:description`) |
| Embeddings | `gemini-embedding-001`, 768 d, normalizados L2, `RETRIEVAL_DOCUMENT` / `RETRIEVAL_QUERY` |
| Índice | índice vectorial nativo de Neo4j 5.26 `plugintext_embedding` (coseno) sobre nodos `:PluginText` separados |
| Generación | `gemini-2.5-flash`, temperature 0, thinkingBudget 0, 1 ejecución por pregunta y sistema; mismo prompt de sistema y plantilla en los tres |
| Fichas | K = 20 fichas en los tres sistemas, mismo formato (nombre, tipo, instalaciones, última release y si supera 3 años, mantenedores, descripción recortada a 400 caracteres) |
| **Vectorial** (baseline) | top-20 del índice vectorial |
| **Vectorial + relaciones** (ablación) | *exactamente* las 20 fichas del baseline + un bloque «RELACIONES DEL GRAFO» con los hechos del grafo restringidos a S = fichas recuperadas ∪ semilla: aristas `DEPENDS_ON` entre plugins de S; `Mantenedor -MAINTAINS->` para los mantenedores de la semilla y los que mantienen ≥2 plugins de S; `MISMA_COMUNIDAD_LOUVAIN` con la semilla, con banderas un-solo-mantenedor / sin-release y exposición; `MISMA_CATEGORÍA` con la semilla (etiqueta neutra). Sin expansión (no puede añadir ningún plugin que el vector no devolvió) y sin enrutador (todos los tipos de hecho). Semilla por el mismo enlazado determinista que GraphRAG (25/25) |
| **GraphRAG** | enlazado de entidades (frankenstyle → nombre exacto → top-1 vectorial) + enrutado por palabras clave a la expansión Cypher pertinente (DEPENDS_ON entrantes/salientes, MAINTAINS, comunidad Louvain ordenada por exposición, categoría + mantenido ordenado por similitud) + turno rotatorio + relleno vectorial hasta 20; líneas de relación de las fichas elegidas |
| Gold | 30 preguntas por plantilla con semilla fija; verdad-terreno Cypher/pandas congelada con sha256 (`95cf7b4a51bece06…`; las 15 de la línea de corte, `db35e94f…`). T6 etiquetado a mano desde las descripciones. Ver «Desviaciones» sobre el momento de congelación |
| Métricas | deterministas, sin LLM-juez: recall@20 del contexto; precisión/recall/F1 de las citas `[component]` (regex), excluida la semilla; T5: cumplimiento de la restricción; fidelidad (citas que existen y estaban en el contexto) |

## Titular: preguntas relacionales con lista gold (T1–T4, n = 20)

| Sistema | F1 citas | Recall@20 | Precisión citas | Recall citas |
|---|---|---|---|---|
| Vectorial | 0,32 | 0,44 | 0,38 | 0,30 |
| Vectorial + relaciones | 0,47 | 0,44 | 0,55 | 0,44 |
| GraphRAG | **0,96** | 0,93 | 1,00 | 0,93 |

Contrastes pareados (Δ = segundo − primero). IC 95 % con 10.000 remuestreos: **pareado** (preguntas i.i.d.), **estratificado** (remuestreo dentro de cada tipo, 5 por tipo) y **por conglomerados** en dos etapas (se remuestrean las 4 plantillas y luego sus 5 semillas; con 4 conglomerados es tosco y conservador). Wilcoxon **exacto** de rangos con signo sobre las diferencias no nulas. G/E/P = preguntas ganadas / empatadas / perdidas por el segundo sistema.

| Contraste | Métrica | Δ | IC pareado | IC estratificado | IC conglomerados | Wilcoxon p | G/E/P |
|---|---|---|---|---|---|---|---|
| GraphRAG − vectorial | F1 | **+0,64** | [+0,45; +0,82] | [+0,49; +0,79] | [+0,34; +0,90] | 3,1·10⁻⁵ | 16/4/0 |
| | Recall@20 | +0,49 | [+0,32; +0,67] | [+0,40; +0,58] | [+0,14; +0,84] | 1,2·10⁻⁴ | 14/6/0 |
| | Precisión | +0,62 | [+0,40; +0,82] | [+0,47; +0,78] | [+0,30; +0,95] | 2,4·10⁻⁴ | 13/7/0 |
| Vect. + relaciones − vectorial | F1 | +0,15 | [+0,01; +0,32] | [+0,03; +0,28] | [−0,04; +0,42] | 0,094 | 5/14/1 |
| | Recall@20 | 0 (por construcción) | — | — | — | — | 0/20/0 |
| | Precisión | +0,17 | [+0,00; +0,38] | [+0,00; +0,35] | [−0,03; +0,42] | 0,125 | 4/15/1 |
| GraphRAG − vect. + relaciones | F1 | **+0,49** | [+0,31; +0,67] | [+0,39; +0,58] | [+0,11; +0,85] | 1,2·10⁻⁴ | 14/6/0 |
| | Recall@20 | +0,49 | [+0,32; +0,66] | [+0,40; +0,58] | [+0,14; +0,84] | 1,2·10⁻⁴ | 14/6/0 |
| | Precisión | +0,45 | [+0,25; +0,65] | [+0,30; +0,60] | [+0,10; +0,85] | 0,004 | 9/11/0 |

(El p exacto con 16 diferencias no nulas, todas positivas, es 2·2⁻¹⁶ = 3,1·10⁻⁵.)

### Por tipo (F1 de citas, n = 5 por tipo; exploratorio: el p exacto no puede bajar de 0,0625)

| Tipo | Vectorial | Vect. + relaciones | GraphRAG | Recall@20 vect. / GraphRAG |
|---|---|---|---|---|
| T1 Dependientes | 0,45 | 0,96 | 1,00 | 0,93 / 1,00 |
| T2 Dependencias + estado | 0,67 | 0,70 | 0,93 | 0,65 / 0,90 |
| T3 Co-mantenimiento | 0,15 | 0,15 | 1,00 | 0,12 / 1,00 |
| T4 Comunidad frágil | 0,00 | 0,07 | 0,89 | 0,04 / 0,82 |
| **T6 Semántica (control)** | 0,67 | 0,66 | 0,61 | 0,86 / 0,80 |

Control T6: GraphRAG − vectorial −0,06 [−0,15; +0,01], 1/1/3; vectorial + relaciones − vectorial −0,01 [−0,06; +0,04], 1/2/2. Las anotaciones relacionales no perjudican la búsqueda semántica; la expansión de GraphRAG sí la perjudica ligeramente (desplaza candidatos semánticos del contexto).

### Qué separa la ablación: recuperación frente a contexto

- **La mayor parte de la ganancia viene de la recuperación por grafo.** De los +0,64 de F1 en T1–T4, las anotaciones relacionales sobre las fichas vectoriales aportan +0,15 (IC pareado [+0,01; +0,32], el de conglomerados cruza 0); la expansión por el grafo aporta los +0,49 restantes (IC [+0,31; +0,67], 14/6/0).
- **T1 es la excepción que señaló el revisor:** el vector ya recuperaba el 93 % de los dependientes (se llaman `dataformfield_*`, `block_aulaplaneta_*`…), y basta con decirle al LLM qué aristas `DEPENDS_ON` hay entre ellas: 0,45 → 0,96, frente a 1,00 de GraphRAG. En T1_2 ambos sistemas veían las mismas 20 fichas y el F1 pasa de 0 a 1 con las líneas de relación. En T1 la ganancia es de **contexto**, no de recuperación.
- **T3 y T4 son de recuperación pura:** los co-mantenidos y los frágiles de la comunidad no son semánticamente similares a la pregunta, no entran en el top-20 (recall 0,12 y 0,04), y ninguna anotación los puede traer: vectorial + relaciones = vectorial (0,15; 0,07). GraphRAG llega a 1,00 y 0,89.
- **T2** es mixto: anotar no ayuda (0,67 → 0,70) porque faltan dependencias en el contexto (recall 0,65); GraphRAG las trae (0,90).
- La ablación usa **más** tokens que GraphRAG (ver abajo), así que su menor rendimiento no se explica por un contexto más pobre en volumen.

## T5 — alternativas mantenidas (aparte; no es evidencia de pertinencia funcional)

| Sistema | Cumplimiento de la restricción (misma categoría ∧ release en los últimos 3 años) |
|---|---|
| Vectorial | 0,52 |
| Vectorial + relaciones | 0,80 |
| GraphRAG | 1,00 |

El 1,00 de GraphRAG es **por construcción**: su expansión para T5 *es* la restricción (misma categoría ∧ mantenida, ordenada por similitud) y la etiqueta de relación `ALTERNATIVA_MANTENIDA` presupone la respuesta. El cumplimiento no mide si lo propuesto es una alternativa real: en T5_2 GraphRAG propone como «alternativas» a `mod_moodlenet` 19 módulos de actividad entre los que están `mod_whatsappmb`, `mod_accredible` y `mod_msteams`. La ablación, con la etiqueta neutra `MISMA_CATEGORÍA`, sube a 0,80 sin expansión. **T5 no se usa en ningún agregado ni en el titular**; evaluar la pertinencia funcional requeriría un juez humano.

## Longitud del contexto (tokens de prompt, `usageMetadata`)

| Sistema | Media 30 preguntas | Media T1–T4 | Exceso por pregunta vs. vectorial (T1–T4) |
|---|---|---|---|
| Vectorial | 2.768 | 2.747 | — |
| Vectorial + relaciones | 3.482 | 3.497 | mediana +27 %, rango [+11 %; +58 %] |
| GraphRAG | 3.230 | 3.116 | mediana +5 %, rango [−1 %; +60 %] |

Mismo número de fichas (20) en los tres; la diferencia son las líneas de relación. GraphRAG no gana por tener más contexto: la ablación tiene más y rinde menos.

## Fidelidad

Fracción de citas (sin contar la semilla) que existen en el grafo y estaban en el contexto. **No está definida** cuando la respuesta no cita ningún plugin aparte de la semilla (abstenciones como «el contexto no permite responder»). Definida en: vectorial 17/30 (9/20 en T1–T4), vectorial + relaciones 21/30 (12/20), GraphRAG 30/30. Donde está definida: vectorial 0,97 (0,94 en T1–T4; T2: 0,88), los otros dos 1,00. Ninguna respuesta de GraphRAG ni del baseline quedó sin citas; una de la ablación (T4_1) sí. Enlazado de entidades: 25/25 en ambos sistemas que lo usan.

## Ejemplos ilustrativos (respuestas literales, recortadas)

**1. T3 — «¿Quién mantiene Roles Category Sitemap (report_rolessitemap) y qué otros plugins mantiene?»** Gold: 6 plugins de Andreas Schenkel.
- Vectorial (F1 = 0): «Andreas Schenkel mantiene [report_rolessitemap]. **No mantiene otros plugins.**» — falso, pero coherente con su contexto.
- Vectorial + relaciones (F1 = 0): «… No se especifica que mantenga otros plugins.» — la anotación no puede mencionar plugins que no se recuperaron.
- GraphRAG (F1 = 1): cita los 6 (`report_sphorphanedfiles`, `block_overviewmyrolesincourses`, …).

**2. T1 — «¿Qué plugins dependen de AulaPlaneta (mod_aulaplaneta)?»** Gold: 4 plugins, los 4 en el top-20 vectorial.
- Vectorial (F1 = 0): se abstiene.
- Vectorial + relaciones (F1 = 1) y GraphRAG (F1 = 1): citan los 4. Aquí el valor está en las aristas verbalizadas, no en la recuperación.

**3. T4 — «¿Qué plugins de la misma comunidad que Custom certificate (mod_customcert) son frágiles…?»** Gold: 5 por exposición.
- Vectorial (F1 = 0): «No hay plugins… que cumplan con las condiciones».
- Vectorial + relaciones (F1 = 0,33): solo [mod_certificate], el único frágil de la comunidad que el vector recuperó.
- GraphRAG (F1 = 0,89): cita 4 de 5.

## Casos de fallo

1. **T5 sobrevalora a GraphRAG** (ver sección T5).
2. **Enrutado por palabras clave.** En T4 la plantilla dice «un solo *mantenedor*», lo que activa también la expansión MAINTAINS; las 20 fichas se reparten entre co-mantenidos y comunidad, y en `paygw_paymob` (T4_2) entran 6 de 10 frágiles.
3. **Artefacto del grafo.** `block_user_preferences` tiene una arista `DEPENDS_ON` hacia sí mismo (T2_3); al excluir la semilla de las citas, GraphRAG queda en recall 0,5 y la ablación, que solo verbaliza la autodependencia, en 0.

## Desviaciones respecto a PLAN.md

Horas en UTC del 2026-09-28, tomadas de los commits, de `cache/usage.jsonl` (marca de tiempo de cada llamada a la API) y de los mtimes de los ficheros en LXC 126. Todas las ejecuciones ocurrieron entre el commit del plan y el checkpoint 2.

| Hora | Evento |
|---|---|
| 21:51:42 | Commit del plan (`a8e970a`) |
| 21:56:05 | Primer lote de embeddings de documentos |
| 22:00:38 / 22:00:59 | Última modificación de `03_build_gold.py` / `retrieval.py` (enrutador y regla K//2 incluidos) |
| 22:01:02–22:01:33 | Respuestas de la línea de corte (T1/T3/T6, 15 preguntas, 2 sistemas) |
| 22:03:00 | Checkpoint 1 (`ab283e8`): gold de 15 preguntas, sha256 `db35e94f…` |
| **22:03:14** | **Gold de T2/T4/T5 generado y congelado** (sha256 `95cf7b4a…`), **después** de haber visto las salidas de la línea de corte |
| 22:03:23–22:04:34 | Respuestas del plan completo |
| 22:07:05 | Checkpoint 2 (`b49b38c`) |
| 22:13 | Ablación «vectorial + relaciones» (30 llamadas; tras la revisión independiente) |

1. **Congelación tardía del gold de T2/T4/T5.** El plan (§3.1, §4.1) exige congelar todo el gold antes de ejecutar cualquier sistema. T1/T3/T6 se congelaron antes; T2/T4/T5 se generaron 1:41 min después de producir las salidas de la línea de corte. Las plantillas y la verdad-terreno son deterministas (Cypher con semilla fija) y ninguna salida entra en su cálculo, pero los umbrales de los pools (punto 4) se fijaron sabiendo cómo se comportaba el sistema en T1/T3.
2. **Enrutador de intención y regla de presupuesto K//2** (no estaban en el plan). Palabras clave → expansión, turno rotatorio entre expansiones; presupuesto de fichas de grafo = 20 si la entidad se nombra, 10 (K//2) si viene del enlazado vectorial, lo que en la práctica solo afecta a T6. El enrutador comparte vocabulario con las plantillas: es una cota superior para preguntas libres. La ablación no usa enrutador.
3. **T3: se abandonó la regla «top-10 por instalaciones».** El plan limitaba el gold a los 10 co-mantenidos más instalados; en su lugar se estrechó el pool de semillas (≤2 mantenedores, 2–15 otros plugins) para que el gold completo quepa en K = 20. T1 (3–19 dependientes) y T2 (2–19 dependencias, al menos una sin release >3 años) se acotaron igual.
4. **T4: umbral de fragilidad de la comunidad cambiado de ≥2 (plan) a ≥3 frágiles.** Ya figura como ≥3 en la primera versión versionada de `03_build_gold.py`; el gold es el top-10 por exposición como en el plan.
5. **Longitud del contexto.** El plan prometía el «mismo presupuesto de contexto»; es el mismo número de fichas, pero las líneas de relación hacen el prompt de GraphRAG entre −1 % y +60 % más largo (mediana +5 % en T1–T4, +15 % en las 30). Medias por sistema en la tabla de tokens.
6. **Fidelidad.** Se excluye la semilla (aparece en la pregunta); la definición se fijó tras ver que el baseline citaba la semilla fuera de su contexto, y se aplica igual a los tres sistemas. En las abstenciones la fidelidad del baseline no está definida (n en la sección Fidelidad).
7. **Métrica titular.** La versión anterior de este documento daba «F1 0,36 → 0,97 en T1–T5», mezclando F1 (T1–T4) con el cumplimiento de T5; se sustituye por el F1 de T1–T4.
8. **Menores.** Gemini por REST con `requests` (alternativa prevista en §4.3); la ficha común incluye mantenedores y fecha/estado de la última release en todos los sistemas (hace el baseline más fuerte); 76 documentos truncados (plan: 68); 1 ejecución por pregunta, sin medir varianza.

## Limitaciones para la memoria

- n = 20 en el titular (4 plantillas × 5 semillas), plantillas y T6 hechos por el propio autor: evidencia **exploratoria**. El IC por conglomerados, con solo 4 plantillas, es el más honesto y el más ancho ([+0,34; +0,90] para GraphRAG − vectorial).
- La verdad-terreno sale del mismo grafo que usa GraphRAG: se mide la capacidad de *recuperar y verbalizar* el grafo, no su veracidad. Las plantillas nombran el `component`, lo que hace trivial el enlazado (25/25).
- Un solo LLM, un solo modelo de embeddings, sin ajuste de K ni de la expansión; reglas fijas, no text-to-Cypher. La ablación es una de varias formas posibles de dar contexto relacional sin expansión.
- T5 solo tiene cumplimiento estructural; T2 evalúa la lista de dependencias, no si la respuesta clasifica bien las obsoletas.
- Dependencia de una API comercial; las respuestas cacheadas reproducen los números sin coste.

## Gasto API

≈ **0,28 US$** en total (`cache/usage.jsonl`): embeddings de documentos ≈ 0,17 US$ (estimado caracteres/4), generación del plan completo y línea de corte ≈ 0,07 US$, ablación «vectorial + relaciones» 0,036 US$ (30 llamadas, tokens reales). Las re-ejecuciones usan la caché y cuestan 0.
