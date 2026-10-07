# Juicio ciego: enrutador bilingüe (exploratorio)

Para cada pregunta cuya respuesta de KG-RAG cambia con el enrutador bilingüe, dos respuestas (X, Y) barajadas con semilla fija: la original y la nueva. Misma rúbrica, referencia y criterio que el juicio principal.

## C02

**Pregunta:** Has block_massaction been abandoned (single maintainer, no release in 3 years)? How exposed are the sites that use it?

**Referencia:** No, en el snapshot no está abandonado: block_massaction tiene release del 2026-07-28 (v8.0.1), soporta hasta 5.2 y tiene un único mantenedor (Matt Davidson); 2.313 instalaciones. Hubo adopción: el riesgo actual es de mantenedor único, no de estancamiento.

**Criterio:** Correcta si dice que tiene release reciente (2026) y por tanto no está abandonado; mencionar el mantenedor único o las instalaciones es un plus. Incorrecta si afirma que está abandonado o sin releases.

### C02-X

No, [block_massaction] no ha sido abandonado. Tiene un único mantenedor, Matt Davidson, pero su última release fue el 28-07-2026, lo que significa que ha tenido releases en los últimos 3 años.

La exposición de los sitios que usan [block_massaction] es la siguiente:
* [tool_coursearchiver]: 0.165
* [tinymce_sketch]: 0.194
* [atto_sketch]: 0.160
* [report_siteoutcomes]: 0.170
* [tiny_sketch]: 0.150
* [filter_sectionnames]: 0.120
* [filter_bookchapters]: 0.102
* [local_externalzip]: 0.111
* [local_mahara]: 0.103

### C02-Y

No, [block_massaction] no ha sido abandonado. Su última release fue el 28 de julio de 2026, lo que significa que ha tenido una release en los últimos 3 años.

El mantenedor de [block_massaction] es Davidson, Matt. Davidson, Matt también mantiene otros plugins como [tool_coursearchiver], [atto_sketch], [tiny_sketch], [block_custom_course_menu], [filter_sectionnames], [filter_bookchapters], [tinymce_sketch] y [report_siteoutcomes].

## C03

**Pregunta:** Blackboard ILP Integration requires the Open LMS Framework plugin. Which Moodle versions does Open LMS Framework support, and is it a dependency of other plugins?

**Referencia:** Open LMS Framework es local_mr: declara 2.3, 2.8, 3.0-3.2, 3.7, 3.9-3.11, 4.0, 4.1, 4.3-4.5 y 5.1 (release 5.1.4, 2026-07-23). Sí es dependencia de 5 plugins: format_flexpage, block_flexpagenav, format_folderview, plagiarism_safeassign y block_internships. La última versión de ILP Integration (block_intelligent_learning) ya NO declara dependencia de local_mr (solo de mod_lesson, mod_assign y mod_quiz).

**Criterio:** Correcta si identifica local_mr, da versiones soportadas recientes (hasta 5.1) y nombra al menos parte de sus dependientes. Parcial si solo da una de las dos partes. Incorrecta si atribuye dependientes o versiones falsas.

### C03-X

No se puede responder a la pregunta con la información proporcionada. El plugin [block_intelligent_learning] no tiene ninguna relación de dependencia con [local_mr].

### C03-Y

No se puede responder a la pregunta sobre las versiones de Moodle que soporta [local_mr] con la información proporcionada.

[local_mr] no es una dependencia de otros plugins en el contexto dado.

## N04

**Pregunta:** How to change/add maintainers to a plugin. I have a plugin for which I want to grant write permissions to other developers (I'm not sure whether it can have more than one maintainer), but I'm not seeing such option […] Is this something I can do myself, or should I contact someone to ask for it?

**Referencia:** El grafo no contiene el procedimiento administrativo; lo correcto es decirlo. Solo puede confirmar que hay plugins con varios mantenedores.

**Criterio:** Abstención correcta si dice que no conoce el procedimiento (confirmar que existen plugins con varios mantenedores es aceptable). Incorrecta si describe un procedimiento como hecho.

### N04-X

El contexto proporcionado no contiene información sobre cómo cambiar o añadir mantenedores a un plugin.

### N04-Y

No se puede responder a esta pregunta con la información proporcionada. La información del contexto describe los plugins y sus mantenedores, pero no detalla el proceso para cambiar o añadir mantenedores a un plugin.

## P02

**Pregunta:** Which actively maintained, widely installed themes could replace theme_essential on a recent Moodle version?

**Referencia:** theme_essential no está en el snapshot (ni su mantenedor, Gareth Barnard, aparece en el grafo). Temas que declaran 5.0 con release desde julio de 2024, por instalaciones: theme_moove (27.596), theme_academi (12.450), theme_boost_union (8.896), theme_trema (4.462), theme_almondb (3.566), theme_mb2nl, theme_lambda2... «Smoothest, least error-prone» no es observable.

**Criterio:** Sin conjunto de citas (recomendación abierta). Correcta si recomienda al menos uno de los temas mantenidos y muy instalados (p. ej. theme_moove, theme_academi, theme_boost_union) con datos del grafo. Parcial si recomienda temas poco instalados o sin indicar mantenimiento. Incorrecta si inventa datos sobre theme_essential o recomienda temas abandonados como si estuvieran activos.

### P02-X

El contexto proporcionado no incluye información sobre el plugin [theme_essential], por lo que no puedo responder a la pregunta.

### P02-Y

No se puede responder a esta pregunta con la información proporcionada, ya que el plugin [theme_essential] no se encuentra en el contexto.

## P04

**Pregunta:** How widely installed are mod_customcert and tool_certificate, who maintains each one, and do they share maintainers?

**Referencia:** mod_customcert: 31.808 instalaciones, mantenido por Mark Nelson. tool_certificate: 9.953 instalaciones, mantenido por «Moodle Workplace plugins». No comparten mantenedores (sin arista CO_MAINTAINED; comunidades Louvain distintas).

**Criterio:** Correcta si da instalaciones y mantenedores de ambos y dice que no comparten. Parcial si falta un elemento. Incorrecta si da cifras o mantenedores falsos o dice que comparten.

### P04-X

[mod_customcert] tiene 31808 instalaciones y es mantenido por Mark Nelson.
[tool_certificate] tiene 9953 instalaciones y es mantenido por Moodle Workplace plugins.
No comparten mantenedores.

### P04-Y

[mod_customcert] tiene 31808 instalaciones y es mantenido por Mark Nelson. [tool_certificate] tiene 9953 instalaciones y es mantenido por Moodle Workplace plugins. No comparten mantenedores.

## P06

**Pregunta:** Is there a TinyMCE (tiny_*) equivalent of atto_molstructure, by the same maintainers or otherwise?

**Referencia:** Sí: tiny_molstructure («Chemical substance»), de los mismos mantenedores (Céline Pervès y Louis Plyer); declara 3.10-5.1, última release 2025-02-27. atto_molstructure solo llega a 4.1. (Otros tiny_ relacionados con química por texto: tiny_ketcher, tiny_wiris.)

**Criterio:** Correcta si nombra tiny_molstructure como equivalente. Parcial si propone otro tiny_ químico (tiny_ketcher, tiny_wiris) sin tiny_molstructure. Incorrecta si inventa uno.

### P06-X

Sí, existe un equivalente TinyMCE de [atto_molstructure]. El plugin [tiny_molstructure] es un plugin TinyMCE que permite dibujar una molécula o reacción usando el editor web ChemDoodle e insertarla en un editor de texto.

Los mantenedores de [tiny_molstructure] son Céline Pervès y Louis Plyer, quienes también son mantenedores de [atto_molstructure].

### P06-Y

Sí, existe un equivalente TinyMCE de [atto_molstructure]. El plugin [tiny_molstructure] es un editor de sustancias químicas para TinyMCE con los mismos mantenedores: Céline Pervès y Louis Plyer.

