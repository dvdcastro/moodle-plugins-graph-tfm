# Figuras de la memoria: tamaño, legibilidad y pies de figura propuestos

Pase de legibilidad del 2do borrador (2026-09-28). Regla común en `src/analyze/_fig_style.py`:
cada figura se dibuja a su **ancho final en página** (`TEXT_WIDTH_CM = 15,0` cm, el ancho útil
real de `docs/plantilla-structuralia.docx`: A4 con márgenes de 3 cm), a 300 dpi, de modo que los
puntos del código son los puntos impresos. Mínimo 9 pt (8 pt solo para rótulos de nodo densos,
declarado). `fs.save()` verifica al guardar que el PNG no supera 15 cm de ancho (1.772 px) ni
20 cm de alto y que ningún texto baja del mínimo.

**Cómo insertar:** al ancho natural del PNG (px / 300 dpi), nunca más ancho que 15 cm. Si se
inserta a 15 cm una figura que mide menos (p. ej. `series_cobertura.png`, 11,7 cm), la letra solo
crece. Los números de figura los asigna el documento: ninguna imagen lleva "Figura N".

Las notas que antes iban incrustadas en la imagen (a 7,6-8,6 pt, en ámbar o gris) se quitaron y
su contenido está en el pie propuesto. Ningún dato cambió: los CSV que escriben los scripts
(`series_descriptivo_trend.csv`, `attack_simulation_summary.csv`) son idénticos byte a byte
antes y después (sha256).

"Mín. antes" = tamaño mínimo del código × (15 cm / ancho del PNG anterior), es decir, el tamaño
efectivo al colocar la figura anterior a todo el ancho de texto.

| Archivo | Script | Tamaño final (cm) | Mín. ahora | Mín. antes (a 15 cm) |
|---|---|---|---|---|
| pipeline_recoleccion.png | 06_pipeline_figures.py | 15,0 × 8,6 | 9 pt | 5,0 pt (subtítulos 8,3 pt en 25,1 cm) |
| pipeline_etl.png | 06_pipeline_figures.py | 15,0 × 10,4 | 9 pt | 4,5 pt (nota ámbar 7,6 pt en 25,1 cm) |
| comunidades_top15_donut_grid.png | 03_community_figure.py | 15,0 × 18,1 | 9 pt | 2,9 pt ("plugins" 6,2 pt en 31,9 cm) |
| comunidades_top15_donut_graphviz.png (= comunidades_top15_meta.png) | 03_community_figure.py | 15,0 × 14,9 | 9 pt | 2,9 pt (ídem) |
| series_cobertura.png | 05_series_descriptivo.py | 11,7 × 8,5 | 9 pt | 5,7 pt (nota 7,6 pt en 20,1 cm) |
| series_declive_agregado.png | 05_series_descriptivo.py | 14,5 × 10,7 | 9 pt | 5,3 pt (nota 7,6 pt en 21,3 cm) |
| simulacion_ataque_dirigido.png | 07_attack_simulation.py | 14,5 × 9,8 | 9 pt | 3,6 pt (nota 7,8 pt en 32,7 cm) |
| cascada_stack.png | _candidate_figures.py | 15,0 × 15,7 | 9 pt | 3,6 pt (mantenedores 7,2 pt en 30,2 cm) |
| ego_mantenedor_justin_hunt.png | _candidate_figures.py | 15,0 × 11,7 | 9 pt | 3,1 pt (rótulos 6,6 pt en 31,9 cm) |
| cluster_colaboracion.png | _candidate_figures.py | 15,0 × 17,9 | **8 pt** (rótulos de nodo densos) | 1,9 pt (rótulos 7,4 pt en 56,9 cm) |
| inactividad_roc.png | 13_prediccion_inactividad.py | (lo gestiona el coordinador) | pendiente | 8,7 pt (leyenda 11 pt en 20,3 cm, versión abandono_roc) |
| inactividad_coeficientes.png | 13_prediccion_inactividad.py | (lo gestiona el coordinador) | pendiente | 9,8 pt (versión abandono_coeficientes) |

## Pies de figura propuestos

**pipeline_recoleccion.png.** Etapas de la recolección de datos: (1) feed oficial `pluglist.php`
(una sola petición: 2.888 plugins y 21.734 versiones con checksum), (2) scraping del Marketplace
por componente (mantenedores e instalaciones, 1 petición/s respetando `Crawl-delay: 10`),
(3) lectura de `version.php` desde dos fuentes independientes (GitHub y ZIP) para las
dependencias declaradas y (4) el endpoint `/stats` del Marketplace con las series mensuales de
instalaciones 2012-2026. Todas las etapas escriben en una caché local con checksum por archivo,
de modo que cada script es reanudable. Fuente: elaboración propia.
*Antes/después:* 5,0 pt → 9 pt; recuadros re-envueltos a mano para 15 cm; se quitaron las
referencias internas de fase del título y del recuadro 4.

**pipeline_etl.png.** Proceso ETL de carga del grafo. *Extract:* lectura de los JSONL/CSV crudos
de cada fuente. *Transform:* parseo de `version.php`, corrección de tres errores propios del
parser (constante `ANY_VERSION`, sintaxis heredada `$module->` y subdirectorio en la URL del
repositorio), conversión de tipos texto↔entero y deduplicación. *Load:* `MERGE` en Cypher de los
nodos Plugin, Maintainer, Category, MoodleRelease y Set y de las relaciones observadas
(MAINTAINS 4.111, DEPENDS_ON 741, SUPPORTS 25.710, IN_CATEGORY 2.888, PART_OF 383). *Derive:*
relaciones ponderadas calculadas sobre el grafo ya cargado, sin nuevas descargas
(CO_MAINTAINED 15.123, CO_MAINTAINS 838, SAME_CATEGORY 419.831). Fuente: elaboración propia.
*Antes/después:* 4,5 pt → 9 pt; la nota ámbar sobre los tres errores corregidos pasa al pie.

**comunidades_top15_donut_grid.png / comunidades_top15_donut_graphviz.png.** Composición de
categorías oficiales de las 15 comunidades más grandes de G_soc (Louvain). Cada dona es una
comunidad: el número central es su nº de plugins y el área es proporcional a él; los sectores
muestran la mezcla real de categorías oficiales (las seis más frecuentes y "otras", que agrupa
46 categorías) y la etiqueta en cursiva es la categoría dominante. Las líneas representan la
colaboración agregada entre comunidades (co-mantenimiento más dependencias entre sus plugins;
el grosor es proporcional al peso). Ninguna comunidad es monocategoría: todas mezclan entre 9 y
19 categorías oficiales. Fuente: elaboración propia sobre la partición de Louvain calculada en
Neo4j GDS.
*Antes/después:* 2,9 pt → 9 pt. Se quitó la palabra "plugins" del centro de cada dona (6,2 pt; lo
explica el pie), el subtítulo incrustado y el sufijo "layout A/B" del título; el hueco de cada
dona se rellenó de blanco para que las líneas no crucen el número. **Atención:** `decisions.md`
(2026-09-13) registra que David eligió la variante Graphviz (copiada a
`comunidades_top15_meta.png`), pero `04_build_memoria.py` inserta `donut_grid`; conviene
confirmar cuál va en el documento.

**series_cobertura.png.** Cobertura de la serie temporal de instalaciones: de los 2.888 plugins
del directorio oficial, 2.833 (98,1 %) tienen una serie no vacía y 2.145 (74,3 %) cuentan con al
menos 24 meses de historia. Los plugins con menos de 24 meses se describen, pero se excluyen del
cálculo de tendencia para evitar el sesgo de censura. La serie mide sitios registrados que
reportan el plugin al Marketplace de Moodle (telemetría), no instalaciones activas verificadas;
el análisis es descriptivo, no causal. Fuente: elaboración propia sobre las estadísticas públicas
del Marketplace.
*Antes/después:* 5,7 pt → 9 pt; nota incrustada al pie; "Numero" → "Número"; porcentajes con
coma decimal y separador de miles con punto.

**series_declive_agregado.png.** Función de distribución acumulada empírica (ECDF) de la
diferencia, para cada plugin, entre la mediana de su cuota de instalaciones en los últimos 12
meses y la mediana en los 12 meses centrados en su pico histórico (N = 2.145 plugins con al menos
24 meses de serie; eje horizontal en escala symlog). La cuota es instalaciones del plugin / total
mensual del ecosistema, nunca el valor absoluto. El 91,9 % de los plugins presenta una diferencia
negativa (mediana −0,006 pp, línea discontinua). El caso más extremo, mod_hotpot (−5,35 pp), es
real y no ruido: su cuota se diluye por el crecimiento del ecosistema, no por una caída de su uso
propio. Se usa la ECDF, sin intervalos, para evitar artefactos de agrupamiento. La serie es
telemetría, no instalaciones activas verificadas; distribución agregada, sin inferencia causal.
Fuente: elaboración propia.
*Antes/después:* 5,3 pt → 9 pt; la explicación del caso extremo y la nota metodológica pasan al
pie (en la imagen solo queda "mod_hotpot (−5,35 pp)"); acentos corregidos (Variación, Fracción,
últimos); coma decimal en ejes y leyenda.

**simulacion_ataque_dirigido.png.** Simulación de remoción de mantenedores sobre el grafo
mantenedor-plugin con dependencias (4.377 nodos). Izquierda: porcentaje de plugins que quedan
sin ningún mantenedor; derecha: porcentaje de instalaciones expuestas (las de esos plugins),
ambos en función de la fracción de mantenedores removidos. Se compara la remoción dirigida por
grado y por betweenness con la remoción aleatoria (mediana y rango intercuartílico de 100
réplicas). La simulación es estática: mide la exposición estructural inmediata al remover
mantenedores, no modela la reacción de la comunidad (relevo de mantenedores, forks, migración de
usuarios) ni predice lo que ocurriría. Fuente: elaboración propia, siguiendo la metodología de
Albert, Jeong y Barabási (2000).
*Antes/después:* 3,6 pt → 9 pt; una sola leyenda compartida bajo los paneles; la nota de
simulación estática pasa al pie; "bipartito" corregido (el grafo incluye aristas
Plugin-Plugin DEPENDS_ON); eje horizontal con coma decimal y marcas cada 0,2.

**cascada_stack.png.** Cascada de dependencias de la familia STACK: qtype_stack (centro), los
cuatro plugins que dependen de él (izquierda: local_quizanalytics, qformat_stack,
local_stackmatheditor, quiz_stack) y los cuatro de los que depende (derecha:
qbank_importasversion, qbehaviour_dfcbmexplicitvaildate, qbehaviour_dfexplicitvaildate,
qbehaviour_adaptivemultipart). Una flecha A → B indica que A depende de B (DEPENDS_ON). El
número dentro de cada nodo es su nº de instalaciones y el texto en cursiva, sus mantenedores
declarados. En ámbar, los plugins mantenidos solo por Tim Hunt y/o Chris Sangwin, el mismo dúo que
mantiene qtype_stack: 3 de las 4 dependencias (qbank_importasversion suma a Andreas Steiger) y 2
de los 4 dependientes (qformat_stack y quiz_stack). Fuente: elaboración propia sobre Neo4j
(relaciones DEPENDS_ON y MAINTAINS).
*Antes/después:* 3,6 pt → 9 pt; círculos reales (antes elipses); aristas con tramos horizontales
para no cruzar los rótulos; separador de miles en las instalaciones. **Correcciones de
contenido:** (a) la flecha de la leyenda "dirección de DEPENDS_ON" apuntaba en sentido contrario
a las aristas; ahora es la entrada "A → B: A depende de B", coherente con ellas. (b) El subtítulo
incrustado anterior afirmaba que el dúo mantenía las 4 dependencias y que los 4 dependientes
tenían mantenedores propios distintos: falso según Neo4j (3 de 4 y 2 de 4); el pie de arriba
usa las cifras verificadas. (c) qtype_preg no forma parte de la figura (no tiene arista
DEPENDS_ON con estos 9 plugins); el pie actual del documento no debe citarlo.

**ego_mantenedor_justin_hunt.png** (no usada en el documento; reemplazada por la Tabla A5).
Red de mantenimiento de Justin Hunt: los 32 plugins que mantiene, 32 de 32 (100 %) con él como
único mantenedor, 15.963 instalaciones en total. El tamaño del nodo es proporcional a las
instalaciones del plugin (escala logarítmica). Solo se rotulan los 10 plugins más instalados
(borde oscuro); el listado completo está en la Tabla A5. Cada arista es una relación MAINTAINS
leída de Neo4j. Fuente: elaboración propia.
*Antes/después:* 3,1 pt → 9 pt. **Simplificada:** 10 rótulos en vez de 32 (a 15 cm no caben 32
rótulos radiales a 9 pt), con los rotulados repartidos de forma equiespaciada en el anillo.

**cluster_colaboracion.png** (no usada en el documento; reemplazada por la Tabla A6).
Clúster real de colaboración: componente conexo de 47 nodos (9 mantenedores y 38 plugins) del
grafo bipartito Mantenedor-Plugin (relación MAINTAINS) filtrado a mantenedores con 2 o más
plugins; es el quinto componente por tamaño (el mayor, de 193 nodos, es ilegible impreso). Entre
paréntesis: instalaciones de cada plugin y nº total de plugins de cada mantenedor. El orden de
cada columna se optimizó (barycenter, 4 pasadas) para reducir cruces. Fuente: elaboración propia
sobre Neo4j.
*Antes/después:* 1,9 pt → 8 pt (excepción declarada de rótulos densos: a 9 pt el rótulo más largo,
"qbehaviour_regexpadaptivewithhelpnopenalty (1.113)", no dejaba hueco para las aristas en 15 cm);
los dos rótulos más largos se parten tras el prefijo de tipo; título, cabeceras y resto a ≥ 9 pt.

**inactividad_roc.png / inactividad_coeficientes.png.** *Pie pendiente: script y figuras a cargo
del coordinador (`13_prediccion_inactividad.py`), que migrará a `_fig_style.py`.*
