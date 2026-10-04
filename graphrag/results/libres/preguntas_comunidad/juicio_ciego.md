# Juicio ciego — preguntas de la comunidad

Cada pregunta tiene 4 respuestas (A-D) de 4 sistemas, barajadas con semilla fija. Juzgar solo con la pregunta, la respuesta de referencia y el criterio fijados antes de ejecutar. Etiquetas: correcta, parcial, incorrecta, abstencion_correcta, abstencion_incorrecta.

## C01

**Pregunta:** Is the Dialogue plugin (mod_dialogue) still maintained, and does it support Moodle 3.9 or later?

**Referencia:** Sí: mod_dialogue tuvo release el 2025-03-19 (versión 2025032000), declara soporte para 3.9 y de 3.10 a 4.5, y tiene un único mantenedor (Dan Marsden). No está estancado (índice de riesgo: mantenedor único, sin estancamiento).

**Criterio:** Correcta si afirma que sigue con releases recientes (2025) Y que soporta 3.9 o posteriores. Parcial si solo responde una de las dos partes.

### C01-A

Sí, el plugin [mod_dialogue] sigue siendo mantenido, con su última release el 2025-03-19, lo que indica que ha tenido una release en los últimos 3 años. El contexto no proporciona información específica sobre la compatibilidad con Moodle 3.9 o versiones posteriores.

### C01-B

El plugin [mod_dialogue] no tiene mantenedores listados. Soporta Moodle 3.9 y versiones posteriores.

### C01-C

Sí, el plugin [mod_dialogue] sigue siendo mantenido, con su última release el 19 de marzo de 2025, lo que indica que ha tenido una release en los últimos 3 años. El contexto no proporciona información específica sobre la compatibilidad con Moodle 3.9 o versiones posteriores.

### C01-D

Sí, el plugin [mod_dialogue] sigue siendo mantenido. Su última release fue el 19 de marzo de 2025, lo que indica que ha tenido una release en los últimos 3 años. El contexto proporcionado no especifica si es compatible con Moodle 3.9 o versiones posteriores.

## C02

**Pregunta:** Has block_massaction been abandoned (single maintainer, no release in 3 years)? How exposed are the sites that use it?

**Referencia:** No, en el snapshot no está abandonado: block_massaction tiene release del 2026-07-28 (v8.0.1), soporta hasta 5.2 y tiene un único mantenedor (Matt Davidson); 2.313 instalaciones. Hubo adopción: el riesgo actual es de mantenedor único, no de estancamiento.

**Criterio:** Correcta si dice que tiene release reciente (2026) y por tanto no está abandonado; mencionar el mantenedor único o las instalaciones es un plus. Incorrecta si afirma que está abandonado o sin releases.

### C02-A

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

### C02-B

No, [block_massaction] no ha sido abandonado. Tiene un único mantenedor, Matt Davidson, pero su última release fue el 28 de julio de 2026, lo que significa que ha tenido una release en los últimos 3 años. Por lo tanto, los sitios que lo usan no están expuestos por falta de mantenimiento reciente.

### C02-C

No, [block_massaction] no ha sido abandonado. Su última release fue el 28 de julio de 2026, lo que significa que ha tenido una release en los últimos 3 años. Tiene un único mantenedor, Davidson, Matt.

### C02-D

El plugin [block_massaction] no ha sido abandonado, ya que no tiene mantenedores. Hay 2313 sitios expuestos que lo utilizan.

## C03

**Pregunta:** Blackboard ILP Integration requires the Open LMS Framework plugin. Which Moodle versions does Open LMS Framework support, and is it a dependency of other plugins?

**Referencia:** Open LMS Framework es local_mr: declara 2.3, 2.8, 3.0-3.2, 3.7, 3.9-3.11, 4.0, 4.1, 4.3-4.5 y 5.1 (release 5.1.4, 2026-07-23). Sí es dependencia de 5 plugins: format_flexpage, block_flexpagenav, format_folderview, plagiarism_safeassign y block_internships. La última versión de ILP Integration (block_intelligent_learning) ya NO declara dependencia de local_mr (solo de mod_lesson, mod_assign y mod_quiz).

**Criterio:** Correcta si identifica local_mr, da versiones soportadas recientes (hasta 5.1) y nombra al menos parte de sus dependientes. Parcial si solo da una de las dos partes. Incorrecta si atribuye dependientes o versiones falsas.

### C03-A

No se puede responder a la pregunta sobre las versiones de Moodle que soporta [local_mr] con la información proporcionada.

[local_mr] no es una dependencia de otros plugins en el contexto dado.

### C03-B

No se puede responder a esta pregunta con la información proporcionada. El plugin [block_intelligent_learning] no requiere el plugin [local_mr].

### C03-C

La consulta no devolvió resultados: el contexto no permite responder.

### C03-D

No se puede determinar si [block_intelligent_learning] requiere [local_mr] basándose en la información proporcionada.

El plugin [local_mr] no especifica las versiones de Moodle que soporta.

Sí, [local_mr] es una dependencia de otros plugins, específicamente de [plagiarism_safeassign].

## C04

**Pregunta:** Dada una lista de plugins instalados, ¿cuáles declaran soporte para Moodle 4.0 y cuáles no?

**Referencia:** La pregunta adaptada no incluye la lista. El grafo lo resuelve por plugin con las versiones soportadas declaradas (relación SUPPORTS / supported_releases): en el snapshot, 1.082 de los 2.888 plugins del directorio declaran soporte para 4.0.

**Criterio:** Fijado a priori: correcta si explica que se comprueba con las versiones declaradas por plugin y da el recuento o una clasificación correcta; parcial si pide la lista o da ejemplos sin método; abstención incorrecta si solo dice que no puede; incorrecta si da datos de soporte falsos.

### C04-A

El contexto proporcionado no contiene información sobre el soporte de los plugins para Moodle 4.0. Solo se menciona el soporte para Moodle 4.1 en adelante para [report_upgradelog] y Moodle 4.5+ para [block_dimensions], así como Moodle 4.x para [tool_skills].

### C04-B

El contexto proporcionado no contiene información sobre el soporte de los plugins para Moodle 4.0. Solo se menciona el soporte para Moodle 4.1 en adelante para [report_upgradelog] y Moodle 4.5+ para [block_dimensions], Moodle 4.x para [tool_skills] y Moodle 3.3.5, 3.3.6, 3.3.7, 3.4.2, 3.4.3 o 3.4.4 para [tool_policy].

### C04-C

El contexto proporcionado no contiene información sobre la compatibilidad de los plugins con versiones específicas de Moodle (como Moodle 4.0). Por lo tanto, no puedo responder a la pregunta.

### C04-D

De los plugins instalados:

Declaran soporte para Moodle 4.0:
* [mod_attendance]
* [mod_customcert]

No declaran soporte para Moodle 4.0:
* [mod_bigbluebuttonbn]

## C05

**Pregunta:** List all plugins in the directory with the category each one belongs to.

**Referencia:** El grafo tiene la relación IN_CATEGORY para los 2.888 plugins del directorio, en 52 categorías. Una respuesta completa es un listado de 2.888 filas; ningún contexto de 20 fichas ni 100 filas lo cubre.

**Criterio:** Fijado a priori: correcta solo si entrega el listado completo; parcial si da un listado parcial con categorías correctas o explica que el dato existe pero solo muestra una parte; abstención incorrecta si solo dice que no puede; incorrecta si asigna categorías falsas.

### C05-A

Aquí tienes la lista de plugins en el directorio con su categoría:

*   [aiplacement_airesourceguide] (aiplacement)
*   [aiplacement_exaaichat] (aiplacement)
*   [aiplacement_textinsights] (aiplacement)
*   [aiprovider_anthropic] (aiprovider)
*   [aiprovider_bedrock] (aiprovider)
*   [aiprovider_claude] (aiprovider)
*   [aiprovider_datacurso] (aiprovider)
*   [aiprovider_gemini] (aiprovider)
*   [aiprovider_groq] (aiprovider)
*   [aiprovider_jokes] (aiprovider)
*   [aiprovider_mistral] (aiprovider)
*   [aiprovider_openaicompatible] (aiprovider)
*   [aiprovider_openrouter] (aiprovider)
*   [aiprovider_openwebui] (aiprovider)
*   [aiprovider_pollinations] (aiprovider)
*   [aiprovider_schooleesopenrouter] (aiprovider)
*   [aiprovider_yandexai] (aiprovider)
*   [antivirus_mimeblocker] (antivirus)
*   [antivirus_savdi] (antivirus)
*   [assignfeedback_aifeedback] (assignfeedback)
*   [assignfeedback_airubric] (assignfeedback)
*   [assignfeedback_cloudpoodll] (assignfeedback)
*   [assignfeedback_editpdfplus] (assignfeedback)
*   [assignfeedback_grades_chart] (assignfeedback)
*   [assignfeedback_helixfeedback] (assignfeedback)
*   [assignfeedback_mahara] (assignfeedback)
*   [assignfeedback_onenote] (assignfeedback)
*   [assignfeedback_pdf] (assignfeedback)
*   [assignfeedback_poodll] (assignfeedback)
*   [assignfeedback_recitannotation] (assignfeedback)
*   [assignfeedback_solutionsheet] (assignfeedback)
*   [assignfeedback_structured] (assignfeedback)
*   [assignment_onlineaudio] (assignment)
*   [assignment_poodllonline] (assignment)
*   [assignment_random] (assignment)
*   [assignment_team] (assignment)
*   [assignment_uploadcode] (assignment)
*   [assignment_uploadpdf] (assignment)
*   [assignsubmission_atmegacode] (assignsubmission)
*   [assignsubmission_automaticextension] (assignsubmission)
*   [assignsubmission_beetleblocks] (assignsubmission)
*   [assignsubmission_changes] (assignsubmission)
*   [assignsubmission_cincopa] (assignsubmission)
*   [assignsubmission_cloudpoodll] (assignsubmission)
*   [assignsubmission_collabora] (assignsubmission)
*   [assignsubmission_comparativejudgement] (assignsubmission)
*   [assignsubmission_edulegit] (assignsubmission)
*   [assignsubmission_edusharing] (assignsubmission)
*   [assignsubmission_estream] (assignsubmission)
*   [assignsubmission_geogebra] (assignsubmission)
*   [assignsubmission_helixassign] (assignsubmission)
*   [assignsubmission_mahara] (assignsubmission)
*   [assignsubmission_maharaws] (assignsubmission)
*   [assignsubmission_mediagallery] (assignsubmission)
*   [assignsubmission_metadata] (assignsubmission)
*   [assignsubmission_mojec] (assignsubmission)
*   [assignsubmission_onenote] (assignsubmission)
*   [assignsubmission_onlineaudio] (assignsubmission)
*   [assignsubmission_onlinepoodll] (assignsubmission)
*   [assignsubmission_onlyoffice] (assignsubmission)
*   [assignsubmission_pdf] (assignsubmission)
*   [assignsubmission_physical] (assignsubmission)
*   [assignsubmission_random] (assignsubmission)
*   [assignsubmission_recording] (assignsubmission)
*   [assignsubmission_responsetemplate] (assignsubmission)
*   [assignsubmission_snap] (assignsubmission)
*   [assignsubmission_snap4arduino] (assignsubmission)
*   [assignsubmission_submarker] (assignsubmission)
*   [assignsubmission_turtlestitch] (assignsubmission)
*   [assignsubmission_wordcount] (assignsubmission)
*   [assignsubmission_youtube] (assignsubmission)
*   [atto_aceinlineassistant] (atto)
*   [atto_aic] (atto)
*   [atto_applink] (atto)
*   [atto_bsgrid] (atto)
*   [atto_c4l] (atto)
*   [atto_chemistry] (atto)
*   [atto_chemrender] (atto)
*   [atto_cincopa] (atto)
*   [atto_clickview] (atto)
*   [atto_cloudpoodll] (atto)
*   [atto_cloze] (atto)
*   [atto_code] (atto)
*   [atto_computing] (atto)
*   [atto_corrections] (atto)
*   [atto_count] (atto)
*   [atto_easychem] (atto)
*   [atto_edusharing] (atto)
*   [atto_eexcesseditor] (atto)
*   [atto_embedquestion] (atto)
*   [atto_etitle] (atto)
*   [atto_fenomiostream] (atto)
*   [atto_filedragdrop] (atto)
*   [atto_filterws] (atto)
*   [atto_fontawesomepicker] (atto)
*   [atto_fontsize] (atto)
*   [atto_fullscreen] (atto)
*   [atto_generico] (atto)
*   [atto_helixatto] (atto)
*   [atto_hr] (atto)

### C05-B

Aquí tienes la lista de plugins y sus categorías:

*   [local_coursecatalog] (tipo local)
*   [theme_liquid] (tipo theme)
*   [mod_certificate] (tipo mod)
*   [local_courselist] (tipo local)
*   [block_faq_list] (tipo block)
*   [mod_customcert] (tipo mod)
*   [local_smartsearch] (tipo local)
*   [block_my_certificates] (tipo block)
*   [aiprovider_datacurso] (tipo aiprovider)
*   [local_coursefilters] (tipo local)
*   [tool_category_backup] (tipo tool)
*   [local_catdup] (tipo local)
*   [local_pluginsfetcher] (tipo local)
*   [block_catalogue] (tipo block)
*   [report_rolessitemap] (tipo report)
*   [report_allbackups] (tipo report)
*   [report_payments] (tipo report)
*   [tool_moodledt] (tipo tool)
*   [block_cam_mycourses] (tipo block)
*   [local_plugininstalltimer] (tipo local)

### C05-C

No puedo listar los plugins por "directorio" ya que esa información no está disponible en el contexto proporcionado. Sin embargo, puedo listar los plugins con su tipo:

*   [local_coursecatalog] — tipo local
*   [tool_category_backup] — tipo tool
*   [local_catdup] — tipo local
*   [block_catalogue] — tipo block
*   [report_rolessitemap] — tipo report
*   [report_allbackups] — tipo report
*   [report_payments] — tipo report
*   [tool_moodledt] — tipo tool
*   [local_courselist] — tipo local
*   [block_cam_mycourses] — tipo block
*   [local_category_reset] — tipo local
*   [local_categorybanner] — tipo local
*   [report_rubric_list] — tipo report
*   [local_listcoursefiles] — tipo local
*   [block_search_course_category] — tipo block
*   [local_enrolstats] — tipo local
*   [block_tb_top_cats] — tipo block
*   [block_course_tree_list] — tipo block
*   [qbank_purgecategory] — tipo qbank
*   [mod_myeducationpath] — tipo mod

### C05-D

Aquí tienes la lista de plugins y sus categorías:

*   [local_coursecatalog] (tipo local)
*   [tool_category_backup] (tipo tool)
*   [local_catdup] (tipo local)
*   [block_catalogue] (tipo block)
*   [report_rolessitemap] (tipo report)
*   [report_allbackups] (tipo report)
*   [report_payments] (tipo report)
*   [tool_moodledt] (tipo tool)
*   [local_courselist] (tipo local)
*   [block_cam_mycourses] (tipo block)
*   [local_category_reset] (tipo local)
*   [local_categorybanner] (tipo local)
*   [report_rubric_list] (tipo report)
*   [local_listcoursefiles] (tipo local)
*   [block_search_course_category] (tipo block)
*   [local_enrolstats] (tipo local)
*   [block_tb_top_cats] (tipo block)
*   [block_course_tree_list] (tipo block)
*   [qbank_purgecategory] (tipo qbank)
*   [mod_myeducationpath] (tipo mod)

## C06

**Pregunta:** Is there a version of format_topcoll marked as compatible with Moodle 4.5?

**Referencia:** format_topcoll (Collapsed Topics) NO está en el snapshot del 2026-09-07 (ni en el grafo ni en pluglist_20260907.json), así que el grafo no puede decir qué versiones declara. Lo correcto es decir que no consta. (El recolector la clasificó como completa; la comprobación del gold la deja en no respondible.)

**Criterio:** Abstención correcta si dice que no encuentra format_topcoll / no tiene información. Incorrecta si afirma o niega soporte para 4.5 o lo atribuye a otro plugin.

### C06-A

No se puede determinar si existe una versión de format_topcoll compatible con Moodle 4.5 con la información proporcionada.

### C06-B

La consulta no devolvió resultados: el contexto no permite responder.

### C06-C

No se puede responder a esta pregunta con la información proporcionada. No hay ningún plugin llamado `format_topcoll` en el contexto.

### C06-D

No se puede responder a esta pregunta con la información proporcionada. No hay ningún plugin llamado "format_topcoll" en el contexto.

## C07

**Pregunta:** [GitHub issue in repository call-learning/moodle-block_rss_thumbnails] clarifying the status of this plugin. To this day, it is tagged as not compatible with Moodle>4.2 and there is not recent release. Is it clearly abandoned ? Thx for clarifying.

**Referencia:** Hay señales claras de abandono: la última release de block_rss_thumbnails es del 2023-02-02 (versión 1.3), declara soporte solo hasta 4.1 y tiene 39 instalaciones. Tiene 3 mantenedores (Camille Carlier, Martin Cornu-Mansuy, Laurent David); en el índice de riesgo cuenta como estancado, no como mantenedor único. Declararlo «abandonado» es una inferencia: no hay campo de archivado.

**Criterio:** Correcta si señala la falta de releases desde 2023 (sin release en más de 3 años) y/o soporte máximo 4.1 como indicio de abandono. Parcial si solo menciona mantenedores o instalaciones. Incorrecta si afirma que está activo.

### C07-A

El plugin [block_rss_thumbnails] no ha tenido una release en más de 3 años (la última fue el 2023-02-02). Además, comparte mantenedores (Camille Carlier, Laurent David, Martin Cornu-Mansuy) con otros plugins que tampoco han tenido releases recientes, como [customfield_multiselect], [block_featured_courses], [tool_gdpr_plus], [block_enhanced_myoverview], [block_thumblinks_action], [block_group_members] y [block_forum_groups].

Existen alternativas mantenidas en la misma categoría, como [block_newsslider], [block_selectrss], [block_accessibility_filescan], [block_section], [block_coursenews], [block_qrcode], [block_qr], [block_actvtmodal], [block_featuredcourses] y [block_eportfolio].

Basado en la falta de releases recientes y la existencia de alternativas mantenidas, se puede inferir que el plugin [block_rss_thumbnails] está abandonado.

### C07-B

El plugin [block_rss_thumbnails] no ha tenido una release en más de 3 años (última release 2023-02-02), lo que sugiere que podría estar abandonado.

### C07-C

El plugin [block_rss_thumbnails] no ha tenido una release en más de 3 años, lo que sugiere que podría estar abandonado.

### C07-D

El plugin [block_rss_thumbnails] no es compatible con Moodle 4.2 o superior. Su última versión fue lanzada el 1675322222 y soporta hasta Moodle 4.1. No hay información en el contexto que indique si está abandonado.

## C08

**Pregunta:** Does the Grid course format (format_grid) support Moodle 4.5.x?

**Referencia:** format_grid NO está en el snapshot del 2026-09-07 (ni en el grafo ni en pluglist_20260907.json); el grafo no puede responder. Lo correcto es decir que no consta. (Clasificada como completa por el recolector; el gold la deja en no respondible.)

**Criterio:** Abstención correcta si dice que no encuentra format_grid / no tiene información. Incorrecta si afirma o niega soporte o lo atribuye a otro formato.

### C08-A

La consulta no devolvió resultados: el contexto no permite responder.

### C08-B

No se puede determinar si el formato de curso Grid (format_grid) es compatible con Moodle 4.5.x con la información proporcionada, ya que [format_grid] no aparece en el contexto.

### C08-C

No se puede determinar si el formato de curso Grid (format_grid) es compatible con Moodle 4.5.x con la información proporcionada, ya que [format_grid] no aparece en el contexto.

### C08-D

El contexto proporcionado no contiene información sobre un plugin llamado "Grid course format" o [format_grid], por lo que no puedo responder si es compatible con Moodle 4.5.x.

## C09

**Pregunta:** [GitHub issue in repository catalyst/moodle-webservice_restful] Will be supported by moodle 4.5? This plugin is supported by moodle 4.5 LTS ?

**Referencia:** Sí: webservice_restful declara soporte para 4.5 (máximo declarado; versión 2024050604, publicada el 2025-05-27).

**Criterio:** Correcta si dice que sí declara 4.5. Abstención incorrecta si dice que no puede saberlo.

### C09-A

El plugin [webservice_restful] es mantenido por Catalyst IT y su última release fue el 27 de mayo de 2025, lo que indica que ha tenido una release en los últimos 3 años. Sin embargo, el contexto proporcionado no especifica si es compatible con Moodle 4.5 LTS.

### C09-B

El plugin [webservice_restful] es mantenido por Catalyst IT y su última release fue el 27 de mayo de 2025, lo que indica que tiene soporte activo. Sin embargo, la información proporcionada no especifica si es compatible con Moodle 4.5 LTS.

### C09-C

Sí, el plugin [webservice_restful] es compatible con Moodle 4.5. El contexto proporcionado no indica si Moodle 4.5 es una versión LTS.

### C09-D

El plugin [webservice_restful] tuvo su última release el 27 de mayo de 2025, lo que indica que está siendo mantenido activamente y es probable que sea compatible con Moodle 4.5 LTS.

## C10

**Pregunta:** [GitHub issue in repository moodleou/moodle-qtype_pmatch] Is this plugin compatible with Moodle 4.5 LTS? Is there a version of this plugin compatible with Moodle 4.5 LTS? From the Moodle plugins directory it is unclear whether tag v.3.2 version is compatible much beyond Moodle 4.0 […]

**Referencia:** Sí: la última versión de qtype_pmatch («3.4 for Moodle 4.4+», 2025-07-17) declara soporte para 4.4, 4.5 y 5.0.

**Criterio:** Correcta si dice que hay versión que declara 4.5. Abstención incorrecta si dice que no puede saberlo.

### C10-A

La información proporcionada no permite determinar la compatibilidad del plugin [qtype_pmatch] con Moodle 4.5 LTS. Solo se indica que su última release fue el 17-07-2025.

### C10-B

El contexto proporcionado no contiene información sobre la compatibilidad de los plugins con versiones específicas de Moodle, como Moodle 4.5 LTS. Por lo tanto, no puedo responder si [qtype_pmatch] o alguna de sus versiones es compatible con Moodle 4.5 LTS.

### C10-C

El contexto proporcionado no contiene información sobre la compatibilidad de los plugins con versiones específicas de Moodle, como Moodle 4.5 LTS. Solo se indica la fecha de la última release y si ha habido una release en los últimos 3 años.

### C10-D

Sí, el plugin [qtype_pmatch] es compatible con Moodle 4.5. La versión más reciente es "3.4 for Moodle 4.4+".

## C11

**Pregunta:** Is quiz_answersheets available in the Moodle plugins directory?

**Referencia:** Sí: quiz_answersheets («Export quiz attempts») está en el directorio; última release «v1.7 for Moodle 5.2+» del 2026-07-21, 1.035 instalaciones.

**Criterio:** Correcta si confirma que está en el directorio.

### C11-A

El contexto proporcionado no permite responder si [quiz_answersheets] está disponible en el directorio de plugins de Moodle.

### C11-B

El contexto proporcionado no contiene información sobre si [quiz_answersheets] está disponible en el directorio de plugins de Moodle.

### C11-C

Sí, [quiz_answersheets] está disponible en el directorio de plugins de Moodle.

### C11-D

Sí, [quiz_answersheets] está disponible en el directorio de plugins de Moodle.

## C12

**Pregunta:** Do the Microsoft 365 plugins (especially auth_oidc) support Moodle 5.0?

**Referencia:** Sí: auth_oidc y local_o365 declaran 4.5, 5.0, 5.1 y 5.2 (release 5.2.1, 2026-09-02); local_o365 depende de auth_oidc. El resto del set «Microsoft 365» (block_microsoft, repository_office365, local_office365, theme_boost_o365teams, tiny_teamsmeeting) también declara 5.0.

**Criterio:** Correcta si dice que auth_oidc (y/o el resto) declara 5.0. Parcial si solo dice que están mantenidos sin hablar de 5.0. Abstención incorrecta si dice que no puede saberlo.

### C12-A

No se puede determinar si los plugins de Microsoft 365, incluido [auth_oidc], son compatibles con Moodle 5.0 basándose únicamente en la información proporcionada. La información de la ficha de los plugins no especifica las versiones de Moodle compatibles.

### C12-B

El contexto proporcionado no especifica las versiones de Moodle soportadas por los plugins. Por lo tanto, no es posible determinar si los plugins de Microsoft 365, incluyendo [auth_oidc], soportan Moodle 5.0.

### C12-C

El contexto proporcionado no contiene información sobre la compatibilidad de los plugins con versiones específicas de Moodle, incluyendo Moodle 5.0.

### C12-D

Sí, los siguientes plugins de Microsoft 365 soportan Moodle 5.0:

*   [auth_oidc] (OpenID Connect Authentication)
*   [block_microsoft] (Microsoft Block)
*   [local_copilot] (Microsoft 365 Copilot)
*   [local_o365] (Microsoft 365 Integration)
*   [local_office365] (Microsoft 365 Integration (shell plugin))
*   [repository_office365] (Microsoft 365 Repository)
*   [theme_boost_o365teams] (Microsoft 365 Teams Theme)
*   [tiny_teamsmeeting] (Teams Meeting (TinyMCE editor))

Los plugins [atto_teamsmeeting] (Teams Meeting (atto editor)) y [filter_oembed] (oEmbed Filter) no tienen soporte para Moodle 5.0 según la información proporcionada.

## C13

**Pregunta:** [GitHub issue in repository corvus-albus/moodle-local_wsmanagesections] Does this plugin support moodle 4.4? I wanted to confirm if your plugin works well with moodle 4.4?

**Referencia:** No consta: local_wsmanagesections declara soporte hasta 4.2 (3.3-4.2); última release 2023-08-20. No declara 4.4.

**Criterio:** Correcta si dice que no declara 4.4 (máximo 4.2). Incorrecta si dice que sí. Abstención incorrecta si dice que no puede saberlo.

### C13-A

El plugin [local_wsmanagesections] no tiene una release en los últimos 3 años, por lo que no se puede confirmar su compatibilidad con Moodle 4.4 basándose únicamente en la información proporcionada.

### C13-B

La consulta no devolvió resultados: el contexto no permite responder.

### C13-C

El plugin [local_wsmanagesections] no tiene una release en más de 3 años (última release 2023-08-20), lo que sugiere que podría no ser compatible con Moodle 4.4. Su mantenedor es corvus albus.

### C13-D

El contexto proporcionado no contiene información sobre la compatibilidad de [local_wsmanagesections] con Moodle 4.4.

## C14

**Pregunta:** [GitHub issue in repository jrangelardila/moodle-format_buttons] Moodle 4.0 Support? Does this plugin have support for Moodle 4.0?

**Referencia:** Sí: format_buttons declara 4.0 (y de 2.8 a 5.2; release «5.x», 2026-06-03).

**Criterio:** Correcta si dice que declara 4.0. Abstención incorrecta si dice que no puede saberlo.

### C14-A

El plugin [format_buttons] tuvo su última release el 2026-06-03, lo que indica que ha tenido releases en los últimos 3 años. El plugin [format_btns] indica que fue desarrollado para Moodle 4.2 y superior, y que [format_buttons] no es compatible con Moodle 4.2 y superior. Sin embargo, [format_btns] ya no recibirá actualizaciones ni soporte, y se recomienda migrar a [format_buttons]. El contexto no proporciona información directa sobre la compatibilidad específica de [format_buttons] con Moodle 4.0.

### C14-B

El plugin [format_buttons] es compatible con Moodle 4.2 y versiones superiores. Su mantenedor, Jhon Rangel Ardila, también mantiene [format_btns], que no recibirá más actualizaciones y recomienda migrar a [format_buttons] para mantener la funcionalidad.

### C14-C

Sí, el plugin [format_buttons] tiene soporte para Moodle 4.0.

### C14-D

El plugin [format_buttons] es compatible con Moodle 4.2 y superior. Su mantenedor, Jhon Rangel Ardila, también mantiene [format_btns], que indica que [format_buttons] no es compatible con Moodle 4.2 y versiones anteriores.

## C15

**Pregunta:** Is there a version of OU wiki (mod_ouwiki) for Moodle 4.x?

**Referencia:** Sí: la última versión de mod_ouwiki («4.4 r1», 2024-11-21) declara soporte para Moodle 4.4 (la única 4.x declarada).

**Criterio:** Correcta si dice que hay versión para 4.x (4.4). Abstención incorrecta si dice que no puede saberlo.

### C15-A

El contexto proporcionado no contiene información sobre la compatibilidad de [mod_ouwiki] con Moodle 4.x.

### C15-B

Sí, existe una versión de OU wiki [mod_ouwiki] para Moodle 4.x. Es compatible con Moodle 4.4.

### C15-C

No se puede determinar si existe una versión de [mod_ouwiki] para Moodle 4.x con la información proporcionada.

### C15-D

Sí, [mod_ouwiki] tuvo una release el 21-11-2024, lo que indica que es compatible con versiones recientes de Moodle, incluyendo Moodle 4.x.

## C16

**Pregunta:** Does the Moove theme support Moodle 4.0?

**Referencia:** Sí: theme_moove declara 4.0 (y hasta 5.2; release 5.2.1, 2026-06-21).

**Criterio:** Correcta si dice que declara 4.0. Abstención incorrecta si dice que no puede saberlo.

### C16-A

El contexto proporcionado no especifica si el tema [theme_moove] es compatible con Moodle 4.0.

### C16-B

El contexto proporcionado no contiene información sobre la compatibilidad de [theme_moove] con Moodle 4.0.

### C16-C

El contexto proporcionado no especifica si el tema [theme_moove] es compatible con Moodle 4.0.

### C16-D

La consulta no devolvió resultados: el contexto no permite responder.

## C17

**Pregunta:** Does quizaccess_announcements officially support Moodle 4.5?

**Referencia:** Sí: quizaccess_announcements declara 4.0-4.5 (v1.0.2, publicada el 2023-07-04).

**Criterio:** Correcta si dice que declara 4.5. Abstención incorrecta si dice que no puede saberlo.

### C17-A

El contexto proporcionado no contiene información sobre la compatibilidad de [quizaccess_announcements] con Moodle 4.5.

### C17-B

El contexto proporcionado no contiene información sobre la compatibilidad de [quizaccess_announcements] con Moodle 4.5.

### C17-C

Sí, [quizaccess_announcements] soporta oficialmente Moodle 4.5.

### C17-D

El contexto proporcionado no contiene información sobre la compatibilidad de [quizaccess_announcements] con Moodle 4.5.

## C18

**Pregunta:** Does tool_migratehvp2h5p support Moodle 3.11 and 4.0?

**Referencia:** Sí: tool_migratehvp2h5p declara 3.11 y 4.0 (y de 3.9 a 5.1; release 0.2.0, 2025-09-30; mantenido por Moodle HQ).

**Criterio:** Correcta si dice que declara ambas. Parcial si solo confirma una. Abstención incorrecta si dice que no puede saberlo.

### C18-A

El contexto proporcionado no contiene información sobre las versiones de Moodle soportadas por [tool_migratehvp2h5p].

### C18-B

El contexto proporcionado no contiene información sobre las versiones de Moodle soportadas por [tool_migratehvp2h5p].

### C18-C

El contexto proporcionado no contiene información sobre las versiones de Moodle soportadas por [tool_migratehvp2h5p].

### C18-D

Sí, [tool_migratehvp2h5p] es compatible con Moodle 3.11 y 4.0.

## C19

**Pregunta:** [GitHub issue in repository IITBombayWeb/moodle-quiz_downloadsubmissions] Moodle 4.4 support? Is this plugin compatible with moodle 4.4? There is an unmerged PR for compatibility with moodle 4.2 could you merge?

**Referencia:** No consta: quiz_downloadsubmissions declara solo 3.3-3.9; última release 2020-10-06 (madurez beta). No declara 4.4. La petición de merge no es respondible.

**Criterio:** Correcta si dice que no declara 4.4 (máximo 3.9) o que no hay release desde 2020 que lo cubra. Incorrecta si dice que sí. Abstención incorrecta si dice que no puede saberlo.

### C19-A

El plugin [quiz_downloadsubmissions] es mantenido por IIT Bombay y Kashmira Nagwekar. Su última release fue el 2020-10-06, sin releases en más de 3 años, lo que sugiere que podría no ser compatible con Moodle 4.4. El contexto no proporciona información sobre la compatibilidad específica con Moodle 4.4 ni sobre la fusión de PRs.

### C19-B

El plugin [quiz_downloadsubmissions] no tiene releases en los últimos 3 años, lo que sugiere que podría no ser compatible con Moodle 4.4.

Existen alternativas mantenidas que ofrecen funcionalidades similares:
*   [quiz_essaydownload]: Permite la descarga masiva de respuestas y adjuntos a preguntas de ensayo.
*   [quiz_filedownloader]: Permite descargar archivos adjuntos a preguntas dentro de un cuestionario.
*   [quiz_downloadquiz]: Permite exportar un cuestionario, incluyendo las respuestas correctas, como PDF cifrado.
*   [quiz_exportattemptscsv]: Permite exportar el historial de intentos de un cuestionario como archivo CSV.
*   [quiz_export]: Permite exportar intentos de cuestionarios como PDF.
*   [quiz_archive]: Permite archivar un cuestionario imprimiendo todos los intentos a la vez.
*   [quiz_answersheets]: Permite obtener una vista de un intento de cuestionario formateada para impresión.
*   [quiz_feedback]: Permite exportar datos de retroalimentación de estudiantes.
*   [quiz_group]: Añade la noción de grupo a los cuestionarios.
*   [quiz_autograde]: Permite la calificación manual de preguntas de ensayo a través del subsistema de IA de Moodle.
*   [quiz_archiver]: Archiva intentos de cuestionarios como archivos PDF y HTML de forma automatizada.
*   [quiz_certainty]: Permite exportar datos de certeza y retroalimentación de estudiantes.
*   [quiz_randomsummary]: Permite el análisis de preguntas aleatorias dentro de un cuestionario.
*   [quiz_markspersection]: Muestra las calificaciones por sección de un cuestionario (solo para Moodle 4.3 y anteriores).
*   [quiz_editquizsettings]: Permite editar ciertas configuraciones de un cuestionario, como las fechas de apertura y cierre.
*   [quiz_heartbeat]: Ofrece una visión general del tiempo transcurrido desde la última interacción entre un estudiante y el servidor Moodle durante los intentos de cuestionario.

### C19-C

La consulta no devolvió resultados: el contexto no permite responder.

### C19-D

El plugin [quiz_downloadsubmissions] no tiene una release en más de 3 años (última release 2020-10-06). Sus mantenedores son IIT Bombay y Kashmira Nagwekar. El contexto no permite determinar si es compatible con Moodle 4.4 ni si se fusionará el PR para la compatibilidad con Moodle 4.2.

## P01

**Pregunta:** Which of my plugins (e.g. mod_attendanceregister) do not declare support for Moodle 3.6, and is it viable to run them anyway?

**Referencia:** mod_attendanceregister NO declara 3.6 (declara 2.1-3.3, 4.0, 4.1 y 4.5). La viabilidad de usarlo igualmente no está en el grafo.

**Criterio:** Correcta si dice que no declara 3.6 y reconoce que la viabilidad no se puede afirmar con los datos. Parcial si solo una de las dos. Incorrecta si dice que sí declara 3.6 o afirma viabilidad como hecho.

### P01-A

No se puede determinar qué plugins no declaran soporte para Moodle 3.6 con la información proporcionada, ya que las fichas de plugins solo indican la versión de Moodle soportada a partir de la 4.1 en el caso de [report_upgradelog].

No es viable ejecutar plugins que no declaren soporte para una versión específica de Moodle, ya que podrían causar problemas de compatibilidad o seguridad.

### P01-B

No se puede determinar qué plugins no declaran soporte para Moodle 3.6 con la información proporcionada. La viabilidad de ejecutarlos no puede ser evaluada.

### P01-C

La consulta no devolvió resultados: el contexto no permite responder.

### P01-D

El contexto proporcionado no contiene información sobre la compatibilidad de los plugins con versiones específicas de Moodle (como Moodle 3.6). Por lo tanto, no es posible responder qué plugins no declaran soporte para Moodle 3.6 ni si es viable ejecutarlos.

## P02

**Pregunta:** Which actively maintained, widely installed themes could replace theme_essential on a recent Moodle version?

**Referencia:** theme_essential no está en el snapshot (ni su mantenedor, Gareth Barnard, aparece en el grafo). Temas que declaran 5.0 con release desde julio de 2024, por instalaciones: theme_moove (27.596), theme_academi (12.450), theme_boost_union (8.896), theme_trema (4.462), theme_almondb (3.566), theme_mb2nl, theme_lambda2... «Smoothest, least error-prone» no es observable.

**Criterio:** Sin conjunto de citas (recomendación abierta). Correcta si recomienda al menos uno de los temas mantenidos y muy instalados (p. ej. theme_moove, theme_academi, theme_boost_union) con datos del grafo. Parcial si recomienda temas poco instalados o sin indicar mantenimiento. Incorrecta si inventa datos sobre theme_essential o recomienda temas abandonados como si estuvieran activos.

### P02-A

El contexto proporcionado no incluye información sobre el plugin [theme_essential], por lo que no puedo determinar qué temas podrían reemplazarlo.

### P02-B

El contexto proporcionado no incluye información sobre el plugin `theme_essential`, por lo que no puedo responder a la pregunta.

### P02-C

La consulta no devolvió resultados: el contexto no permite responder.

### P02-D

No se puede responder a esta pregunta con la información proporcionada, ya que el plugin [theme_essential] no se encuentra en el contexto.

## P03

**Pregunta:** Which published plugins declare a dependency on local_aws, and what versions of local_aws exist?

**Referencia:** Declaran dependencia de local_aws: local_session_dynamodb, tool_emailutils y tool_s3logs. De local_aws el grafo guarda solo la última versión (2024050801, 2024-05-08; soporte 2.6-4.3), no el historial.

**Criterio:** Correcta si nombra los 3 dependientes (o al menos 2 sin inventar otros) y la última versión de local_aws o que solo consta la última. Parcial si nombra 1-2 dependientes o solo la versión. Incorrecta si inventa dependientes.

### P03-A

No se puede responder a la pregunta con la información proporcionada. El contexto no incluye información sobre las dependencias de los plugins ni las versiones de [local_aws].

### P03-B

Los plugins publicados que declaran una dependencia en [local_aws] son:

*   [tool_s3logs]
*   [tool_emailutils]
*   [local_session_dynamodb]

El contexto proporcionado no incluye información sobre las versiones específicas de [local_aws].

### P03-C

Los plugins publicados que declaran una dependencia de [local_aws] son:

*   [local_session_dynamodb]

No se proporciona información sobre las versiones de [local_aws].

### P03-D

Los plugins publicados que declaran una dependencia en [local_aws] son:

*   [tool_s3logs] (S3 Log Archiver)
*   [tool_emailutils] (Email utilities)
*   [local_session_dynamodb] (DynamoDB Sessions)

La versión existente de [local_aws] es 2024050801.

## P04

**Pregunta:** How widely installed are mod_customcert and tool_certificate, who maintains each one, and do they share maintainers?

**Referencia:** mod_customcert: 31.808 instalaciones, mantenido por Mark Nelson. tool_certificate: 9.953 instalaciones, mantenido por «Moodle Workplace plugins». No comparten mantenedores (sin arista CO_MAINTAINED; comunidades Louvain distintas).

**Criterio:** Correcta si da instalaciones y mantenedores de ambos y dice que no comparten. Parcial si falta un elemento. Incorrecta si da cifras o mantenedores falsos o dice que comparten.

### P04-A

[mod_customcert] tiene 31808 instalaciones y es mantenido por Mark Nelson.
[tool_certificate] tiene 9953 instalaciones y es mantenido por Moodle Workplace plugins.
No comparten mantenedores.

### P04-B

[mod_customcert] tiene 31808 instalaciones y es mantenido por Mark Nelson. [tool_certificate] tiene 9953 instalaciones y es mantenido por Moodle Workplace plugins. No comparten mantenedores.

### P04-C

[mod_customcert] tiene 31808 instalaciones y es mantenido por Mark Nelson. [tool_certificate] tiene 9953 instalaciones y es mantenido por Moodle Workplace plugins. No comparten mantenedores.

### P04-D

[mod_customcert] tiene 31808 instalaciones. No tiene mantenedores listados.
[tool_certificate] tiene 9953 instalaciones. No tiene mantenedores listados.
No comparten mantenedores.

## P05

**Pregunta:** Which of Gareth Barnard's plugins (e.g. format_weekcoll) are no longer actively maintained?

**Referencia:** En el snapshot del 2026-09-07 no hay ningún mantenedor «Gareth Barnard» ni está format_weekcoll (tampoco format_topcoll, format_grid ni theme_essential): sus plugins ya no figuran en el directorio. El grafo no puede listar cuáles están sin mantener; lo correcto es decir que no constan.

**Criterio:** Abstención correcta si dice que no encuentra plugins de Gareth Barnard / format_weekcoll. Incorrecta si atribuye a Barnard plugins de otros mantenedores.

### P05-A

La consulta no devolvió resultados: el contexto no permite responder.

### P05-B

No se puede responder a esta pregunta con la información proporcionada, ya que Gareth Barnard no aparece como mantenedor de ninguno de los plugins listados.

### P05-C

No se puede responder a esta pregunta con la información proporcionada. No hay plugins de Gareth Barnard en el contexto.

### P05-D

No se puede responder a esta pregunta con la información proporcionada, ya que Gareth Barnard no aparece como mantenedor de ninguno de los plugins en el contexto.

## P06

**Pregunta:** Is there a TinyMCE (tiny_*) equivalent of atto_molstructure, by the same maintainers or otherwise?

**Referencia:** Sí: tiny_molstructure («Chemical substance»), de los mismos mantenedores (Céline Pervès y Louis Plyer); declara 3.10-5.1, última release 2025-02-27. atto_molstructure solo llega a 4.1. (Otros tiny_ relacionados con química por texto: tiny_ketcher, tiny_wiris.)

**Criterio:** Correcta si nombra tiny_molstructure como equivalente. Parcial si propone otro tiny_ químico (tiny_ketcher, tiny_wiris) sin tiny_molstructure. Incorrecta si inventa uno.

### P06-A

No hay un plugin TinyMCE (tinymce_*) equivalente a [atto_molstructure] mantenido por los mismos desarrolladores. Sin embargo, existen varios plugins TinyMCE con diferentes mantenedores, como [tinymce_cincopa], [tinymce_clickview], [tinymce_cloudpoodll], [tinymce_clozeeditor], [tinymce_glatex], [tinymce_h5p], [tinymce_helixmedia], [tinymce_html_components], [tinymce_iassign], [tinymce_managefiles], [tinymce_mathslate], [tinymce_mediagallery], [tinymce_panoptobutton], [tinymce_planetestream], [tinymce_poodll], [tinymce_recordrtc], [tinymce_sketch], [tinymce_skim], [tinymce_tiny_mce_wiris], [tinymce_virtualkeyboard], [tinymce_wordcount] y [tinymce_youtube].

### P06-B

Sí, existe un equivalente TinyMCE de [atto_molstructure]. El plugin [tiny_molstructure] es un editor de sustancias químicas para TinyMCE, mantenido por Céline Pervès y Louis Plyer, quienes también mantienen [atto_molstructure].

### P06-C

Sí, existe un equivalente TinyMCE de [atto_molstructure]. El plugin [tiny_molstructure] es un plugin TinyMCE que permite dibujar una molécula o reacción usando el editor web ChemDoodle e insertarla en un editor de texto.

Los mantenedores de [tiny_molstructure] son Céline Pervès y Louis Plyer, quienes también son mantenedores de [atto_molstructure].

### P06-D

Sí, existe un equivalente TinyMCE de [atto_molstructure]. El plugin es [tiny_molstructure]. Ambos plugins tienen a Céline Pervès y Louis Plyer como mantenedores.

## P07

**Pregunta:** Is mod_choicegroup still listed in the plugins directory, and when was its last release?

**Referencia:** Sí, en el snapshot del 2026-09-07 mod_choicegroup está en el directorio; última release del 2026-02-05 (soporte hasta 5.1), mantenido por Nicolas Dunand y CSE Université de Lausanne; ningún plugin declara depender de él. El motivo de la retirada temporal no es observable.

**Criterio:** Correcta si confirma que está listado y da la fecha 2026-02-05. Parcial si solo una de las dos.

### P07-A

Sí, [mod_choicegroup] sigue listado en el directorio de plugins. Su última release fue el 2026-02-05.

### P07-B

Sí, [mod_choicegroup] sigue listado en el directorio de plugins. Su última versión fue lanzada el 5 de febrero de 2026 a las 17:15:12 UTC.

### P07-C

Sí, [mod_choicegroup] sigue en el directorio de plugins. Su última release fue el 2026-02-05.

### P07-D

Sí, [mod_choicegroup] sigue en el directorio de plugins. Su última release fue el 2026-02-05.

## P08

**Pregunta:** ¿Está local_notificationsagent en el directorio de plugins y, si está, quién lo mantiene y cuándo fue su última versión?

**Referencia:** Sí: local_notificationsagent está en el directorio; mantenedores Juan Pablo de Castro, UNIMOODLE Consortium e ISYC Soporte; última versión del 2025-07-29 (madurez beta); 281 instalaciones.

**Criterio:** Correcta si confirma presencia, mantenedores y fecha. Parcial si falta uno de los tres.

### P08-A

Sí, [local_notificationsagent] está en el directorio de plugins. Es mantenido por ISYC Soporte, Juan Pablo de Castro y UNIMOODLE Consortium. Su última versión fue el 29 de julio de 2025.

### P08-B

Sí, [local_notificationsagent] está en el directorio de plugins. Lo mantienen ISYC Soporte, Juan Pablo de Castro y UNIMOODLE Consortium. Su última versión fue el 29 de julio de 2025.

### P08-C

Sí, [local_notificationsagent] está en el directorio de plugins. No tiene mantenedores listados y su última versión fue el 27 de julio de 2025.

### P08-D

Sí, [local_notificationsagent] está en el directorio de plugins. Lo mantienen ISYC Soporte, Juan Pablo de Castro y UNIMOODLE Consortium. Su última versión fue el 29 de julio de 2025.

## N01

**Pregunta:** BigBlueButton experiences? What are your experiences using BBB in a Moodle environment? Is it reliable and stable enough? How about sound and video quality? Same as Zoom or lacking behind? How many users can I safely teach in a BBB classroom?

**Referencia:** El grafo no contiene esta información (fiabilidad, calidad, capacidad); lo correcto es decirlo. Como mucho: mod_bigbluebuttonbn 3.466 instalaciones (soporte hasta 3.9, integrado en el núcleo desde 4.0) frente a mod_zoom 10.413.

**Criterio:** Abstención correcta si dice que no puede responder sobre fiabilidad/calidad/capacidad (dar instalaciones como dato lateral es aceptable). Incorrecta si afirma fiabilidad, calidad o un número de usuarios.

### N01-A

El contexto proporcionado no contiene información sobre experiencias de usuario, fiabilidad, estabilidad, calidad de sonido/video, ni el número máximo de usuarios que se pueden enseñar de forma segura en un aula de BigBlueButton.

Sin embargo, puedo proporcionarte información sobre plugins relacionados con BigBlueButton:

*   [mod_bigbluebuttonbn] integra BigBlueButton en Moodle, incluyendo la grabación y reproducción de sesiones. Es una característica central de Moodle desde la versión 4.0 (deshabilitada por defecto).
*   [bbbext_bnx] mejora la experiencia de BigBlueButton en Moodle con una interfaz más pulida, flujos de trabajo de sesión mejorados y capacidades diseñadas por los creadores de BigBlueButton.
*   [bbbext_bnreminders] es una extensión de BigBlueButton que ayuda a mejorar la asistencia y el compromiso enviando recordatorios de correo electrónico antes de las sesiones. Este plugin está siendo reemplazado por [bbbext_bnx] y no tendrá una versión compatible con Moodle 5.2 en adelante.
*   [local_bbb_lad] recopila información del panel de análisis de aprendizaje de BigBlueButton a través de una devolución de llamada, visible para los profesores en la actividad de BigBlueButton. Requiere el plugin [bbbext_lad] (no proporcionado en el contexto).
*   [mod_recordingsbn] permitía acceder y gestionar grabaciones de BigBlueButton, pero ha sido eliminado. Se recomienda usar [mod_bigbluebuttonbn] para crear instancias de "Solo grabaciones".

### N01-B

El contexto proporcionado no contiene experiencias de usuario ni opiniones sobre la fiabilidad, estabilidad, calidad de audio/video o capacidad de usuarios de BigBlueButton en un entorno Moodle.

Sin embargo, puedo indicar que [mod_bigbluebuttonbn] es un plugin de tipo módulo con 3466 instalaciones y su última versión fue lanzada el 2024-07-09. Se integra con BigBlueButton para incluir la grabación y reproducción de sesiones. BigBlueButton es una característica central de Moodle desde la versión 4.0 (deshabilitada por defecto). Para mejorar la experiencia, se puede considerar instalar [bbbext_bnx], que complementa la funcionalidad principal.

Otros plugins relacionados con BigBlueButton son:
*   [bbbext_bnx]: Mejora la experiencia de BigBlueButton en Moodle con una interfaz más pulida y flujos de trabajo mejorados.
*   [mod_recordingsbn]: Permite acceder y gestionar las grabaciones de BigBlueButton, aunque este plugin ha sido descontinuado y se recomienda usar [mod_bigbluebuttonbn] para crear instancias de "Solo grabaciones".
*   [bbbext_bnreminders]: Ayuda a mejorar la asistencia y el compromiso enviando recordatorios por correo electrónico antes de las sesiones. Este plugin está siendo reemplazado por [bbbext_bnx].
*   [local_bbb_lad]: Recopila información del panel de análisis de aprendizaje de BigBlueButton.

En cuanto a alternativas de videoconferencia, existen otros plugins como:
*   [mod_jitsi]: Permite crear sesiones de videoconferencia Jitsi Meet.
*   [mod_plugnmeet]: Integra un aula de video de código abierto en Moodle.
*   [mod_zoom]: Ofrece una integración con la plataforma Zoom, soportando la creación de reuniones/webinars, sincronización, calificación y copia de seguridad/restauración.
*   [block_zoomonline]: Simplifica la gestión de reuniones de Zoom dentro de los cursos de Moodle.
*   [mod_openmeetings]: Software basado en navegador para conferencias web.
*   [mod_clickmeeting]: Plataforma de videoconferencia para organizar reuniones y webinars online.

### N01-C

El contexto proporcionado no contiene información sobre experiencias de uso, fiabilidad, estabilidad, calidad de sonido/video, ni el número máximo de usuarios en aulas de BigBlueButton. Solo se listan los siguientes plugins relacionados con BigBlueButton:

*   [mod_bigbluebuttonbn]
*   [mod_recordingsbn]
*   [bbbext_bnx]
*   [local_bbb_lad]
*   [bbbext_bnreminders]

### N01-D

El contexto proporcionado no contiene información sobre experiencias de usuario, fiabilidad, estabilidad, calidad de sonido/video, ni el número máximo de usuarios que se pueden enseñar de forma segura en una clase de BigBlueButton.

Sin embargo, puedo proporcionar información sobre plugins relacionados con BigBlueButton:

*   [mod_bigbluebuttonbn] es el plugin principal para integrar BigBlueButton en Moodle, incluyendo la grabación y reproducción de sesiones. Es una característica central de Moodle desde la versión 4.0 (deshabilitada por defecto).
*   Para mejorar la experiencia con [mod_bigbluebuttonbn], se puede considerar instalar [bbbext_bnx], que complementa la funcionalidad principal con una interfaz más pulida y flujos de trabajo mejorados.
*   [mod_recordingsbn] era un plugin para acceder y gestionar grabaciones de BigBlueButton, pero ha sido descontinuado. Se recomienda usar [mod_bigbluebuttonbn] para crear instancias de "Solo grabaciones".
*   [bbbext_bnreminders] es una extensión de BigBlueButton para Moodle que envía recordatorios por correo electrónico antes de las sesiones, aunque está siendo reemplazado por [bbbext_bnx] y no tendrá una versión compatible con Moodle 5.2 en adelante.
*   [local_bbb_lad] es un plugin que recopila información del panel de análisis de aprendizaje de BigBlueButton.

Existen alternativas a BigBlueButton para videoconferencias en Moodle, como [mod_jitsi], [mod_plugnmeet], [mod_openmeetings], [mod_vitero] y [mod_zoom].

## N02

**Pregunta:** Compartibilidad de plugins. Tengo la duda de que es lo que cambia con las versiones de moodle, para que no exista compatibilidad entre las versiones para el uso de plugins.

**Referencia:** El grafo no contiene esta información (cambios de API del núcleo); lo correcto es decirlo.

**Criterio:** Abstención correcta si dice que el contexto no lo explica. Incorrecta si explica causas como hechos no presentes en el contexto.

### N02-A

El contexto proporcionado no contiene información sobre los cambios entre versiones de Moodle que afectan la compatibilidad de los plugins.

### N02-B

El contexto proporcionado no contiene información sobre los motivos por los que los plugins no son compatibles entre diferentes versiones de Moodle. Solo muestra qué versiones de Moodle son compatibles con cada plugin.

### N02-C

El contexto proporcionado no contiene información que explique por qué no existe compatibilidad entre las versiones de Moodle para el uso de plugins.

### N02-D

El contexto proporcionado no contiene información sobre los cambios en las versiones de Moodle que afectan la compatibilidad de los plugins.

## N03

**Pregunta:** Unable to uninstall plugins. I have a plugin I need to uninstall in this case it's the navbuttons plugin. When I initiate an uninstall via Admin>plugins>plugin overview I get this error: Forbidden You don't have permission to access this resource. […] Is this a server-side issue - if so what do I need to look at changing?

**Referencia:** El grafo no contiene esta información (configuración del servidor); lo correcto es decirlo. Dato lateral: ningún plugin declara depender de block_navbuttons.

**Criterio:** Abstención correcta si dice que no puede diagnosticar el error. Incorrecta si da un diagnóstico de servidor como hecho.

### N03-A

El contexto proporcionado no contiene información sobre el plugin "navbuttons" ni sobre errores de permisos al desinstalar plugins. Por lo tanto, no puedo responder a tu pregunta.

### N03-B

El contexto proporcionado no contiene información sobre el plugin "navbuttons" ni sobre errores de permisos al desinstalar plugins. Por lo tanto, no puedo responder a tu pregunta.

### N03-C

La consulta no devolvió resultados: el contexto no permite responder.

### N03-D

El contexto proporcionado no contiene información sobre un plugin llamado "navbuttons" ni sobre errores de permisos al desinstalar plugins. Por lo tanto, no puedo responder a tu pregunta.

## N04

**Pregunta:** How to change/add maintainers to a plugin. I have a plugin for which I want to grant write permissions to other developers (I'm not sure whether it can have more than one maintainer), but I'm not seeing such option […] Is this something I can do myself, or should I contact someone to ask for it?

**Referencia:** El grafo no contiene el procedimiento administrativo; lo correcto es decirlo. Solo puede confirmar que hay plugins con varios mantenedores.

**Criterio:** Abstención correcta si dice que no conoce el procedimiento (confirmar que existen plugins con varios mantenedores es aceptable). Incorrecta si describe un procedimiento como hecho.

### N04-A

El contexto proporcionado no contiene información sobre cómo cambiar o añadir mantenedores a un plugin.

### N04-B

La consulta no devolvió resultados: el contexto no permite responder.

### N04-C

El contexto proporcionado no contiene información sobre cómo cambiar o añadir mantenedores a un plugin.

### N04-D

El contexto proporcionado no contiene información sobre cómo cambiar o añadir mantenedores a un plugin.

## N05

**Pregunta:** Which plugins support Moodle Workplace?

**Referencia:** No hay metadato de soporte para Workplace; lo correcto es decirlo. Proxy débil: el set «Moodle Workplace» (tool_certificate, mod_coursecertificate, tool_datewatch, block_rbreport).

**Criterio:** Abstención correcta si dice que no hay dato de soporte para Workplace, aunque mencione el set como indicio con esa salvedad. Parcial si presenta el set (o plugins «Workplace») como la lista de soporte sin salvedad. Incorrecta si inventa plugins con soporte declarado.

### N05-A

Los siguientes plugins son compatibles con Moodle Workplace:

*   [format_wplist]
*   [tool_certificate]
*   [mod_coursecertificate]
*   [block_mylearning]
*   [block_rbreport]

### N05-B

Los siguientes plugins son compatibles con Moodle Workplace:

*   [format_wplist]
*   [tool_certificate]
*   [mod_coursecertificate]
*   [block_mylearning]
*   [block_rbreport]

### N05-C

Los siguientes plugins mencionan compatibilidad con Moodle Workplace:

*   [format_wplist]
*   [tool_certificate]
*   [mod_coursecertificate]
*   [block_mylearning]
*   [block_rbreport]

### N05-D

La consulta no devolvió resultados: el contexto no permite responder.

## N06

**Pregunta:** [GitHub issue in repository matrix-org/moodle-mod_matrix] Future of this plugin in the course of the new moodle message system. I have the feeling that this might be discontinued in the favour of the new modular messaging system in module with matrix/synapse as a reference implementation

**Referencia:** El grafo no contiene la hoja de ruta del núcleo; además mod_matrix no está en el snapshot. Lo correcto es decirlo.

**Criterio:** Abstención correcta si dice que no puede responder / no encuentra mod_matrix. Incorrecta si afirma el futuro del plugin o le atribuye datos de otro.

### N06-A

El contexto no proporciona información sobre un plugin llamado "mod_matrix" ni sobre su futuro en relación con el sistema de mensajería de Moodle. Solo se mencionan los plugins [qtype_matrix] y [atto_matrix].

### N06-B

El contexto proporcionado no contiene información sobre un plugin llamado "matrix-org/moodle-mod_matrix" ni sobre un "nuevo sistema de mensajes modular en Moodle con matrix/synapse como implementación de referencia". Por lo tanto, no puedo responder sobre el futuro de ese plugin en relación con un nuevo sistema de mensajes.

Sin embargo, el contexto menciona varios plugins de tipo "message":
*   [message_jabber]: Un plugin de mensaje que usa el protocolo XMPP, pero ha sido eliminado de nuevas instalaciones de Moodle 4.0.
*   [message_msgraph]: Utiliza la API REST de Graph (Outlook) para enviar mensajes y notificaciones de Moodle.
*   [message_slack]: Proporciona una salida de mensajes de Moodle para Slack.

También se menciona [mod_dialogue], que permite diálogos entre dos usuarios y, aunque la funcionalidad oficial ha sido reemplazada por el sistema de mensajería, algunos usuarios aún lo encuentran útil como actividad del curso.

### N06-C

El contexto proporcionado no contiene información sobre un plugin llamado "matrix-org/moodle-mod_matrix" ni sobre un "nuevo sistema de mensajería modular en Moodle con matrix/synapse como implementación de referencia". Por lo tanto, no puedo responder a la pregunta.

### N06-D

No se puede responder a esta pregunta con la información proporcionada, ya que el plugin [mod_matrix] no se encuentra en el contexto.

