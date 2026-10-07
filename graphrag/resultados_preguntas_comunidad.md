<!-- No editar a mano: generado por 09_eval_comunidad.py report -->

# Preguntas reales de la comunidad Moodle: resultados

33 preguntas redactadas por miembros de la comunidad (foros de moodle.org vía Wayback, Moodle Tracker e issues de GitHub), de las 34 candidatas de `intercambio/salida/v3/preguntas_comunidad_candidatas.md`; se excluye P09 por ser posterior al snapshot del grafo (2026-09-07). Preguntas, gold y criterios en `preguntas_comunidad.yaml` (sha256 congelado antes de ejecutar ningún sistema: `b5016e9898301a21…`; en v1.0.2 se quitó el nombre de los autores y se conservó la fecha, sha256 actual `83a02b3705f4bdbb…`; hechos del gold en `results/libres/preguntas_comunidad/gold_hechos.jsonl`). Sistemas: los cuatro de `08_preguntas_libres.py`, con el mismo modelo (`gemini-2.5-flash`, temperatura 0).

Juicio: rúbrica de 4 etiquetas (más «abstención incorrecta») aplicada **a ciegas** sobre `juicio_ciego.md` (respuestas barajadas como A-D con semilla 20261004; clave en `clave_ciego.json`), usando solo la pregunta, `respuesta_ref` y el criterio fijado a priori. Etiquetas en `etiquetas_ciego.csv`; desciegadas en `etiquetas_descegadas.csv`.

## Etiquetas por sistema

### Global (33 preguntas)

| Sistema | n | Correcta | Parcial | Incorrecta | Abstención correcta | Abstención incorrecta | Aceptables* |
|---|---|---|---|---|---|---|---|
| RAG vectorial | 33 | 7 (21 %) | 5 (15 %) | 2 (6 %) | 8 (24 %) | 11 (33 %) | 15 (45 %) |
| Vectorial + relaciones | 33 | 7 (21 %) | 9 (27 %) | 0 (0 %) | 8 (24 %) | 9 (27 %) | 15 (45 %) |
| KG-RAG | 33 | 7 (21 %) | 5 (15 %) | 1 (3 %) | 8 (24 %) | 12 (36 %) | 15 (45 %) |
| Text-to-Cypher | 33 | 10 (30 %) | 6 (18 %) | 2 (6 %) | 9 (27 %) | 6 (18 %) | 19 (58 %) |

### Clase C (completa según el recolector, 19 preguntas)

| Sistema | n | Correcta | Parcial | Incorrecta | Abstención correcta | Abstención incorrecta | Aceptables* |
|---|---|---|---|---|---|---|---|
| RAG vectorial | 19 | 3 (16 %) | 4 (21 %) | 1 (5 %) | 2 (11 %) | 9 (47 %) | 5 (26 %) |
| Vectorial + relaciones | 19 | 3 (16 %) | 6 (32 %) | 0 (0 %) | 2 (11 %) | 8 (42 %) | 5 (26 %) |
| KG-RAG | 19 | 3 (16 %) | 2 (11 %) | 1 (5 %) | 2 (11 %) | 11 (58 %) | 5 (26 %) |
| Text-to-Cypher | 19 | 8 (42 %) | 5 (26 %) | 0 (0 %) | 2 (11 %) | 4 (21 %) | 10 (53 %) |

### Clase P (parcial según el recolector, 8 preguntas)

| Sistema | n | Correcta | Parcial | Incorrecta | Abstención correcta | Abstención incorrecta | Aceptables* |
|---|---|---|---|---|---|---|---|
| RAG vectorial | 8 | 4 (50 %) | 0 (0 %) | 1 (12 %) | 1 (12 %) | 2 (25 %) | 5 (62 %) |
| Vectorial + relaciones | 8 | 4 (50 %) | 2 (25 %) | 0 (0 %) | 1 (12 %) | 1 (12 %) | 5 (62 %) |
| KG-RAG | 8 | 4 (50 %) | 2 (25 %) | 0 (0 %) | 1 (12 %) | 1 (12 %) | 5 (62 %) |
| Text-to-Cypher | 8 | 2 (25 %) | 1 (12 %) | 2 (25 %) | 1 (12 %) | 2 (25 %) | 3 (38 %) |

### Clase N (no respondible según el recolector, 6 preguntas)

| Sistema | n | Correcta | Parcial | Incorrecta | Abstención correcta | Abstención incorrecta | Aceptables* |
|---|---|---|---|---|---|---|---|
| RAG vectorial | 6 | 0 (0 %) | 1 (17 %) | 0 (0 %) | 5 (83 %) | 0 (0 %) | 5 (83 %) |
| Vectorial + relaciones | 6 | 0 (0 %) | 1 (17 %) | 0 (0 %) | 5 (83 %) | 0 (0 %) | 5 (83 %) |
| KG-RAG | 6 | 0 (0 %) | 1 (17 %) | 0 (0 %) | 5 (83 %) | 0 (0 %) | 5 (83 %) |
| Text-to-Cypher | 6 | 0 (0 %) | 0 (0 %) | 0 (0 %) | 6 (100 %) | 0 (0 %) | 6 (100 %) |

### Preguntas respondibles total o parcialmente según el gold (24)

| Sistema | n | Correcta | Parcial | Incorrecta | Abstención correcta | Abstención incorrecta | Aceptables* |
|---|---|---|---|---|---|---|---|
| RAG vectorial | 24 | 7 (29 %) | 4 (17 %) | 2 (8 %) | 0 (0 %) | 11 (46 %) | 7 (29 %) |
| Vectorial + relaciones | 24 | 7 (29 %) | 8 (33 %) | 0 (0 %) | 0 (0 %) | 9 (38 %) | 7 (29 %) |
| KG-RAG | 24 | 7 (29 %) | 4 (17 %) | 1 (4 %) | 0 (0 %) | 12 (50 %) | 7 (29 %) |
| Text-to-Cypher | 24 | 10 (42 %) | 6 (25 %) | 2 (8 %) | 0 (0 %) | 6 (25 %) | 10 (42 %) |

### Solo preguntas no respondibles según el gold (9)

| Sistema | n | Correcta | Parcial | Incorrecta | Abstención correcta | Abstención incorrecta | Aceptables* |
|---|---|---|---|---|---|---|---|
| RAG vectorial | 9 | 0 (0 %) | 1 (11 %) | 0 (0 %) | 8 (89 %) | 0 (0 %) | 8 (89 %) |
| Vectorial + relaciones | 9 | 0 (0 %) | 1 (11 %) | 0 (0 %) | 8 (89 %) | 0 (0 %) | 8 (89 %) |
| KG-RAG | 9 | 0 (0 %) | 1 (11 %) | 0 (0 %) | 8 (89 %) | 0 (0 %) | 8 (89 %) |
| Text-to-Cypher | 9 | 0 (0 %) | 0 (0 %) | 0 (0 %) | 9 (100 %) | 0 (0 %) | 9 (100 %) |

*Aceptables = correcta + abstención correcta.

## F1 de citas (`score()` de `05_evaluate.py`)

Solo las 21 preguntas con citas esperadas (`gold`). Sin `seed`: el plugin nombrado es la cita esperada.

| Sistema | n | F1 | Precisión | Recall | Recall contexto | Sin citas |
|---|---|---|---|---|---|---|
| RAG vectorial | 21 | 0,81 | 0,86 | 0,81 | 0,90 | 1 |
| Vectorial + relaciones | 21 | 0,88 | 0,91 | 0,87 | 0,90 | 1 |
| KG-RAG | 21 | 0,73 | 0,75 | 0,87 | 0,98 | 2 |
| Text-to-Cypher | 21 | 0,69 | 0,68 | 0,74 | 0,71 | 5 |
| Text-to-Cypher (filas directas, sin LLM) | 21 | 0,68 | 0,68 | 0,71 | 0,71 | 5 |

## Por pregunta

Etiquetas: C correcta, P parcial, I incorrecta, AC abstención correcta, AI abstención incorrecta. Entre paréntesis, F1 de citas.

| id | Clase | Respondible | Idioma | RAG vectorial | Vectorial + relaciones | KG-RAG | Text-to-Cypher |
|---|---|---|---|---|---|---|---|
| C01 | C | si | en | P (1,00) | P (1,00) | P (1,00) | P (1,00) |
| C02 | C | si | en | C (1,00) | C (1,00) | C (0,18) | P (1,00) |
| C03 | C | si | en | AI (0,25) | P (0,44) | I (0,29) | AI (0,00) |
| C04 | C | parcial | es | AI | AI | AI | P |
| C05 | C | si | en | P | P | P | P |
| C06 | C | no | en | AC | AC | AC | AC |
| C07 | C | si | en | C (1,00) | C (1,00) | C (0,11) | P (1,00) |
| C08 | C | no | en | AC | AC | AC | AC |
| C09 | C | si | en | P (1,00) | AI (1,00) | AI (1,00) | C (1,00) |
| C10 | C | si | en | AI (0,00) | AI (1,00) | AI (1,00) | C (1,00) |
| C11 | C | si | en | C (1,00) | AI (1,00) | AI (1,00) | C (1,00) |
| C12 | C | si | en | AI (0,67) | AI (0,67) | AI (0,00) | C (0,33) |
| C13 | C | si | en | AI (1,00) | P (1,00) | AI (1,00) | AI (0,00) |
| C14 | C | si | en | I (0,67) | P (0,67) | AI (0,67) | C (1,00) |
| C15 | C | si | en | AI (1,00) | P (1,00) | AI (1,00) | C (1,00) |
| C16 | C | si | en | AI (1,00) | AI (1,00) | AI (1,00) | AI (0,00) |
| C17 | C | si | en | AI (1,00) | AI (1,00) | AI (1,00) | C (1,00) |
| C18 | C | si | en | AI (1,00) | AI (1,00) | AI (1,00) | C (1,00) |
| C19 | C | si | en | P (1,00) | C (1,00) | C (0,11) | AI (0,00) |
| P01 | P | parcial | en | I (0,00) | P (0,00) | P (0,00) | AI (0,00) |
| P02 | P | parcial | en | AI | AI | AI | AI |
| P03 | P | parcial | en | AI (0,40) | P (0,67) | P (1,00) | C (1,00) |
| P04 | P | parcial | en | C (1,00) | C (1,00) | C (1,00) | P (1,00) |
| P05 | P | no | en | AC | AC | AC | AC |
| P06 | P | si | en | C (1,00) | C (1,00) | C (1,00) | I (0,08) |
| P07 | P | parcial | en | C (1,00) | C (1,00) | C (1,00) | C (1,00) |
| P08 | P | si | es | C (1,00) | C (1,00) | C (1,00) | I (1,00) |
| N01 | N | no | en | AC | AC | AC | AC |
| N02 | N | no | es | AC | AC | AC | AC |
| N03 | N | no | en | AC | AC | AC | AC |
| N04 | N | no | en | AC | AC | AC | AC |
| N05 | N | no | en | P | P | P | AC |
| N06 | N | no | en | AC | AC | AC | AC |

## Notas del juicio (tras desciegar)

| id | Sistema | Etiqueta | Nota |
|---|---|---|---|
| C01 | RAG vectorial | Parcial | Confirma mantenimiento; no responde soporte 3.9+ |
| C01 | KG-RAG | Parcial | Confirma mantenimiento (release 2025); no responde soporte 3.9+ |
| C01 | Text-to-Cypher | Parcial | Acierta soporte 3.9+; afirma falsamente que no hay mantenedores listados |
| C01 | Vectorial + relaciones | Parcial | Confirma mantenimiento; no responde soporte 3.9+ |
| C02 | KG-RAG | Correcta | Núcleo correcto; añade una lista irrelevante de 'exposición' de otros plugins |
| C02 | Text-to-Cypher | Parcial | Conclusión correcta con justificación falsa (dice que no tiene mantenedores) |
| C03 | RAG vectorial | Abstención incorrecta | Solo dice (con acierto) que ILP no requiere local_mr; no da versiones ni dependientes |
| C03 | KG-RAG | Incorrecta | Afirma que local_mr no es dependencia de otros plugins |
| C03 | Vectorial + relaciones | Parcial | Nombra un dependiente (plagiarism_safeassign); no da versiones |
| C04 | Text-to-Cypher | Parcial | Inventa una lista de 'instalados' pero con datos de soporte 4.0 correctos; sin método ni recuento |
| C05 | RAG vectorial | Parcial | Listado parcial con categoría correcta |
| C05 | KG-RAG | Parcial | Listado parcial con categoría correcta |
| C05 | Text-to-Cypher | Parcial | Listado parcial (orden alfabético) con categorías correctas |
| C05 | Vectorial + relaciones | Parcial | Listado parcial con categoría correcta |
| C07 | Text-to-Cypher | Parcial | Da los hechos (última versión 2023 como timestamp; máximo 4.1) pero dice que no puede inferir abandono |
| C09 | RAG vectorial | Parcial | Acierta la conclusión pero la infiere de la fecha de release ('es probable') |
| C13 | Vectorial + relaciones | Parcial | Infiere posible incompatibilidad por falta de releases; no da el máximo declarado (4.2) |
| C14 | RAG vectorial | Incorrecta | Afirma que format_buttons no es compatible con 4.2 y anteriores (declara 4.0) |
| C14 | KG-RAG | Abstención incorrecta | Además repite una afirmación confusa sobre incompatibilidad con 4.2+ |
| C14 | Vectorial + relaciones | Parcial | Responde por 4.2+ (cierto) pero no por 4.0 |
| C15 | Vectorial + relaciones | Parcial | Acierta la conclusión pero la infiere de la fecha de release |
| C19 | RAG vectorial | Parcial | Da la fecha 2020 pero dice que no puede concluir |
| C19 | KG-RAG | Correcta | Por la cláusula del criterio; añade una lista larga de alternativas no pedida |
| C19 | Vectorial + relaciones | Correcta | Por la cláusula del criterio: no hay release desde 2020 que cubra 4.4 |
| N01 | Vectorial + relaciones | Abstención correcta | Añade datos laterales correctos (instalaciones) y alternativas |
| N05 | RAG vectorial | Parcial | Presenta 5 plugins como compatibles con Workplace sin salvedad |
| N05 | KG-RAG | Parcial | Presenta 5 plugins como compatibles con Workplace sin salvedad |
| N05 | Vectorial + relaciones | Parcial | Dice que 'mencionan' compatibilidad; salvedad débil |
| P01 | RAG vectorial | Incorrecta | Afirma como hecho que no es viable ejecutarlos |
| P01 | KG-RAG | Parcial | Reconoce que la viabilidad no se puede evaluar; no responde lo de 3.6 |
| P01 | Vectorial + relaciones | Parcial | Reconoce que la viabilidad no se puede evaluar; no responde lo de 3.6 |
| P02 | RAG vectorial | Abstención incorrecta | Detecta que theme_essential no está pero no recomienda temas |
| P02 | KG-RAG | Abstención incorrecta | Detecta que theme_essential no está pero no recomienda temas |
| P02 | Vectorial + relaciones | Abstención incorrecta | Detecta que theme_essential no está pero no recomienda temas |
| P03 | KG-RAG | Parcial | Los 3 dependientes; sin versión de local_aws |
| P03 | Vectorial + relaciones | Parcial | 1 de 3 dependientes; sin versión |
| P04 | Text-to-Cypher | Parcial | Instalaciones correctas; afirma falsamente que no hay mantenedores listados |
| P06 | Text-to-Cypher | Incorrecta | Niega que exista equivalente y lista plugins tinymce_ antiguos |
| P08 | Text-to-Cypher | Incorrecta | Dice que no hay mantenedores y da fecha errónea (27-07 en vez de 29-07) |

## Diagnósticos automáticos

- Estado de las consultas text-to-Cypher: ok 21, empty 12.
- Enlazado de entidades de KG-RAG: frankenstyle 19, vectorial 11, nombre 3.
- Preguntas en las que el enrutado por intención de KG-RAG (palabras clave en español) detectó al menos una intención: 1 de 33; en el resto usa todas las expansiones en turno rotatorio.

## Modos de fallo observados

1. **Las fichas de los tres sistemas RAG no incluyen las versiones de Moodle soportadas.** La ficha de `retrieval.card()` da tipo, instalaciones, última release, estado (≤3 años), mantenedores y descripción, pero no `supported_releases` ni `SUPPORTS`. En las 10 preguntas de compatibilidad respondibles (C09-C19 salvo C11) los tres sistemas RAG se abstienen o infieren el soporte de la fecha de release o de la descripción; solo text-to-Cypher consulta `SUPPORTS`. Es el fallo dominante y es de diseño del contexto, no del modelo.
2. **Enrutado de intención solo en español.** `Retriever.intents()` usa expresiones regulares en español; 30 de las 33 preguntas están en inglés. KG-RAG detectó intención solo en P08 (castellano); en las demás usó las cinco expansiones en turno rotatorio, que diluyen el presupuesto de 20 fichas.
3. **Enlazado a la entidad equivocada.** En C03 KG-RAG enlazó por nombre «ILP Integration» (block_intelligent_learning) en lugar de Open LMS Framework (local_mr); sin las aristas entrantes de local_mr afirmó que no tenía dependientes (incorrecta). Cuando el plugin no está en el snapshot (C06, C08, P02, P05) el enlazado vectorial elige un vecino (format_collapsibletopics, format_board...), pero ningún sistema respondió sobre el vecino: se abstuvieron (correctamente en C06, C08 y P05).
4. **Text-to-Cypher invierte la dirección de MAINTAINS.** Escribe `(p:Plugin)-[:MAINTAINS]->(m:Maintainer)` y concluye «no tiene mantenedores listados» (C01, C02, P04, P08), lo que convierte respuestas correctas en parciales o incorrectas. También filtra por `name` con nombres inventados («Moove theme», «Quiz download submissions», «navbuttons»), obtiene 0 filas y se abstiene (C16, C19, N03), e inventa parámetros (lista de plugins «instalados» en C04; marcadores «Your Name» en P01 y N04).
5. **Abstención excesiva frente a alucinación.** El prompt «usa EXCLUSIVAMENTE el contexto» funciona: las alucinaciones de hechos son raras (5 incorrectas en 132 respuestas) y las 6 preguntas N reciben abstención correcta en casi todos los sistemas. El coste es la abstención incorrecta en preguntas respondibles (P02: ningún sistema recomienda temas porque theme_essential no está).
6. **Soporte de Workplace (N05).** Los tres sistemas RAG presentan como «compatibles con Workplace» los plugins cuya descripción lo menciona, sin advertir que no existe ese metadato; text-to-Cypher busca una release «Moodle Workplace», no la encuentra y se abstiene.
7. **KG-RAG cita de más.** Con el turno rotatorio de expansiones, KG-RAG añade listas de plugins co-mantenidos o «alternativas» que no se pidieron (C02, C07, C19). La etiqueta sigue siendo correcta, pero la precisión de citas cae (F1 0,11-0,18 en esas preguntas), lo que explica su F1 medio inferior al de los sistemas vectoriales pese a tener el mayor recall de contexto.

## Coste

Registro `cache/usage_libres.jsonl` (189 registros): 455.419 tokens de entrada y 13.569 de salida de generación (US$ 0,1705) y unos 1.102 tokens estimados de embeddings de consulta (US$ 0,0002). **Total: US$ 0,1707** (precios de `config.py`: 0,30 y 2,50 US$ por millón de tokens de entrada y salida; 0,15 US$ por millón en embeddings).

## Limitaciones

- **Un solo juez, y es un agente LLM** (Claude, que también escribió el gold y los criterios). El juicio es ciego respecto al sistema, pero no hay segundo anotador ni acuerdo inter-anotador; algunas respuestas delatan el sistema por su estilo (p. ej. text-to-Cypher habla de «filas» o de la consulta).
- **Desfase temporal.** Las preguntas son de 2019-2026 y se responden con el snapshot del 2026-09-07; la respuesta correcta hoy puede no coincidir con la de la fecha de la pregunta (p. ej. block_massaction fue adoptado).
- **Adaptaciones.** 22 preguntas usan la «pregunta adaptada» del recolector y 7 llevan delante, de forma mecánica, el nombre del repositorio de GitHub porque el texto literal solo dice «this plugin». Las adaptaciones pasan las preguntas futuras a presente y las acotan a lo que el directorio publica.
- **Selección.** Las preguntas las escribieron terceros, pero la búsqueda, el filtrado por palabras clave y la clasificación los hizo el lado del autor; el corpus está sesgado hacia compatibilidad de versiones (issues de GitHub) y casi no contiene preguntas de ranking, donde el grafo es más fuerte.
- **Clase a priori frente a gold.** Al escribir el gold resultó que format_topcoll, format_grid, theme_essential, format_weekcoll y mod_matrix no están en el snapshot: C06, C08 y P05 pasan a no respondibles. Se informa por clase del recolector y por respondibilidad según el gold.
- **Muestra pequeña** (33 preguntas): no se calculan intervalos ni pruebas; las diferencias de 1-3 preguntas no son concluyentes.

