# moodle-plugins-graph

Trabajo Fin de Máster, Máster en Inteligencia Artificial y Big Data (Structuralia / UCAM).
**Análisis del ecosistema de plugins de Moodle mediante teoría de grafos: identificación de nodos críticos y comunidades.**
Autor: David Antonio Castro Martínez.

El repositorio contiene todo lo necesario para reproducir los resultados de la memoria: el código de recolección, carga y análisis, los datos crudos y procesados del snapshot usado (7 de septiembre de 2026) y los documentos generados con cada cifra que cita la memoria.

- Modelo: grafo multi-relación en Neo4j 5.26 (GDS + APOC) con plugins, mantenedores, categorías y versiones de Moodle, y relaciones observadas (dependencias declaradas en `version.php`, mantenimiento, compatibilidad) y derivadas (co-mantenimiento, co-categoría, ponderadas).
- Análisis: centralidad (PageRank, intermediación, grado) validada contra networkx, comunidades (Louvain) contrastadas con la taxonomía oficial frente a una línea base nula, índice de exposición al riesgo con análisis de sensibilidad, simulación de retirada de mantenedores, series temporales de instalaciones, un modelo supervisado de inactividad de publicación con validación fuera de tiempo y un prototipo GraphRAG evaluado frente a RAG solo vectorial.

## Estructura

```
data/raw/          Datos crudos del snapshot: feed pluglist.php (+ sha256), páginas del directorio en caché
                   (html/, html_stats/, html_translations/), version.php descargados, manifiestos de los ZIP
data/processed/    Tablas derivadas (CSV/JSONL) que leen los análisis y que cita la memoria
src/collect/       Recolección desde fuentes públicas (feed oficial, páginas del directorio, GitHub)
src/build/         Carga del grafo en Neo4j y derivación de aristas
src/analyze/       Análisis numerados; cada uno escribe sus salidas en data/processed/, docs/ o figures/
graphrag/          Prototipo GraphRAG (plan, código, preguntas gold congeladas, resultados, caché de la API)
cypher/            Esquema (restricciones e índices)
docs/              Documentos generados por los scripts (no editar a mano) y bitácora de decisiones
figures/           Figuras de la memoria (300 dpi, a tamaño de página)
```

## Requisitos

- Docker (para Neo4j) y Python 3.12.
- Graphviz (programa del sistema, usado por la figura de comunidades): `sudo apt install graphviz`.
- 8 GB de RAM son suficientes (el grafo tiene unos 4.500 nodos y 465.000 relaciones).
- Solo para el prototipo GraphRAG: una clave de la API de Gemini (coste total registrado: unos 0,25 US$; las respuestas están en caché, así que reproducir los números no llama a la API).

## Puesta en marcha

```bash
# 1. Neo4j 5.26 + GDS + APOC
mkdir -p /srv/neo4j/{data,logs,import,plugins}
docker run -d --name neo4j-moodle --restart unless-stopped \
  -p 7474:7474 -p 7687:7687 \
  -v /srv/neo4j/data:/data -v /srv/neo4j/logs:/logs \
  -v /srv/neo4j/import:/var/lib/neo4j/import -v /srv/neo4j/plugins:/plugins \
  -e NEO4J_AUTH=neo4j/CAMBIAR_PASSWORD \
  -e NEO4J_PLUGINS='["graph-data-science","apoc"]' \
  -e NEO4J_dbms_security_procedures_unrestricted='gds.*,apoc.*' \
  -e NEO4J_dbms_security_procedures_allowlist='gds.*,apoc.*' \
  -e NEO4J_server_memory_heap_initial__size=2G \
  -e NEO4J_server_memory_heap_max__size=4G \
  -e NEO4J_server_memory_pagecache_size=1G \
  neo4j:5.26
# Comprobar en http://<ip>:7474:  RETURN gds.version()

# 2. Entorno Python
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 3. Credenciales: nunca en el código. .env está en .gitignore.
cat > .env <<'EOF'
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=la_misma_de_NEO4J_AUTH
# GEMINI_API_KEY=...   (solo para regenerar embeddings de graphrag/)
EOF
chmod 600 .env
```

## Reproducir los resultados

Hay dos caminos. El **camino corto** parte de los datos incluidos en el repositorio y reproduce las cifras de la memoria sin volver a descargar nada. El **camino completo** vuelve a descargar los datos de las fuentes públicas; tarda muchas horas porque respeta el `Crawl-delay: 10` del `robots.txt` del directorio, y produce un snapshot nuevo (con cifras ligeramente distintas, porque el directorio cambia).

### Camino corto: desde los datos incluidos

```bash
# Carga del grafo (a partir de data/raw y data/processed)
python3 src/build/06_load_neo4j.py          # Plugin, Category, MoodleRelease, IN_CATEGORY, SUPPORTS
python3 src/build/07_load_relations.py      # MAINTAINS, DEPENDS_ON (fuente GitHub), PART_OF
python3 src/build/08_fix_provenance.py      # coincidencia de versión (fuente GitHub)
python3 src/build/09_merge_zip_residual.py  # completa versiones y DEPENDS_ON con la segunda fuente (ZIP)
python3 src/build/10_derive_edges.py        # CO_MAINTAINED, CO_MAINTAINS, SAME_CATEGORY (ponderada)

# Análisis (en este orden: los primeros escriben propiedades en el grafo que usan los siguientes)
python3 src/analyze/01_centrality.py            # PageRank, intermediación y grado en G_dep, G_soc, G_full y G_maint; validación networkx
python3 src/analyze/02_communities.py           # Louvain en G_soc y G_full, estabilidad, NMI frente a la categoría
python3 src/analyze/03_community_figure.py      # figura de composición de las 15 comunidades mayores
python3 src/analyze/03_risk.py                  # señales de riesgo (mantenedor único, inactividad) y riesgo por mantenedor
python3 src/analyze/_candidate_figures.py       # figuras de la cascada STACK, ego-red y clúster de colaboración
python3 src/analyze/05_series_descriptivo.py    # series temporales de instalaciones (cuota relativa)
python3 src/analyze/06_pipeline_figures.py      # diagramas del pipeline de recolección y carga
python3 src/analyze/07_attack_simulation.py     # simulación de retirada dirigida frente a aleatoria
python3 src/analyze/08_sensibilidad_sin_moodlehq.py
python3 src/analyze/09_pagerank_vs_instalaciones.py
python3 src/analyze/10_poblacion_sin_moodlehq.py
python3 src/analyze/11_poblaciones.py           # docs/tabla_poblaciones.md (Tabla 2 de la memoria)
python3 src/analyze/12_riesgo_sensibilidad.py   # docs/riesgo_sensibilidad.md: índice de exposición y sensibilidad 2/3/5 años
python3 src/analyze/13_prediccion_inactividad.py  # docs/prediccion_inactividad.md: modelo supervisado, validación fuera de tiempo
python3 src/analyze/14_nmi_linea_base.py        # docs/nmi_linea_base.md: línea base nula del NMI (1.000 permutaciones)

# Prototipo GraphRAG: ver graphrag/README.md (reconstrucción y cómo deshacer lo añadido a Neo4j)
```

Los pasos aleatorios usan semilla fija, indicada en cada script (Louvain en Neo4j GDS no admite semilla en la versión usada y resultó determinista; su estabilidad se comprueba con python-louvain y 10 semillas).

Este repositorio es la versión de entrega, publicada como un único commit. La bitácora cronológica de decisiones metodológicas y correcciones que citan algunos comentarios del código (`docs/decisions.md`) y los borradores de la memoria se conservan en el repositorio histórico del proyecto.

### Qué se reproduce exactamente (comprobado el 29 de septiembre de 2026)

El camino corto se ejecutó de principio a fin desde un clon limpio de este repositorio, con un entorno Python nuevo instalado desde `requirements.txt` y una base Neo4j vacía:

- **Idénticos:** el grafo completo (mismos nodos y relaciones por tipo), las poblaciones de análisis, la centralidad (diferencias del orden de 1e-15), las comunidades de Louvain sobre G_soc (modularidad 0,9275, 853 comunidades) y su NMI frente a la categoría (0,3333), la línea base nula del NMI, el índice de riesgo y su sensibilidad, la simulación de retirada de mantenedores y el modelo de inactividad. Los documentos de `docs/` se regeneran sin ningún cambio.
- **Con variaciones menores:** Louvain sobre el grafo completo (G_full) da entre 53 y 58 comunidades según la ejecución (modularidad entre 0,8783 y 0,8787; la memoria cita la ejecución original, 57 y 0,8787), la estabilidad con python-louvain varía en la tercera cifra decimal (NMI entre 0,9938 y 0,9942) y el análisis sin Moodle HQ da 330 o 331 comunidades. Estas cifras dependen del orden interno de los nodos al cargar la base desde cero, no de los datos: sobre una misma base cargada, Louvain en Neo4j GDS es determinista. Los identificadores numéricos de las comunidades también cambian entre cargas, aunque la partición de G_soc es la misma.
- **No ejecutado en la prueba:** el prototipo GraphRAG, porque regenerar los embeddings requiere la API de Gemini. Sus respuestas y métricas se reproducen desde la caché incluida (`graphrag/cache/`), sin llamadas a la API.

### Camino completo: volver a recolectar

```bash
python3 src/collect/01_pluglist.py                          # feed oficial pluglist.php (con sha256)
python3 src/collect/02_marketplace_scrape.py --delay 10     # mantenedores e instalaciones (~8 h)
python3 src/collect/03_version_php.py --delay 0.5           # version.php desde GitHub (~25 min)
python3 src/collect/04_marketplace_stats_scrape.py          # series mensuales de instalaciones
python3 src/collect/05_marketplace_translations_scrape.py   # porcentaje de traducción por idioma
```

Para los plugins cuyo `version.php` no se pudo obtener de GitHub con coincidencia exacta (979, población P5b en `docs/tabla_poblaciones.md`), la versión y las dependencias se leyeron del ZIP publicado en el propio directorio. El script de esa descarga no forma parte de este repositorio; se incluyen sus resultados (`data/processed/version_php_zip_residual979.jsonl`) y sus manifiestos con sumas de verificación (`data/raw/zips/`).

## Dónde está cada cifra de la memoria

| Documento | Contenido |
| :-- | :-- |
| `docs/tabla_poblaciones.md` | Todas las poblaciones de análisis (2.963, 2.888, 2.876, 2.590, 979, 2.365, 2.145, 292...) con su definición y filtro |
| `docs/riesgo_sensibilidad.md` | Índice de exposición (versión principal y variantes), sensibilidad al umbral de inactividad, núcleo robusto, robustez sin plugins ex-núcleo |
| `docs/prediccion_inactividad.md` | Cohortes, resultados con IC 95 % bootstrap, coeficientes, deriva entre cohortes, evidencia de la fuga en `supportedmoodles` |
| `docs/nmi_linea_base.md` | NMI real frente a la distribución nula |
| `graphrag/RESULTS.md` | Evaluación del prototipo GraphRAG frente a RAG solo vectorial |
| `docs/figuras.md` | Cada figura, su script, su tamaño y su pie |

## Datos y ética

Todos los datos proceden de fuentes públicas: el feed oficial `pluglist.php`, las páginas públicas del directorio de plugins de Moodle y los repositorios públicos de GitHub declarados por cada plugin. La recolección respetó el `robots.txt` del directorio (`Crawl-delay: 10`). Los nombres de mantenedores son los que el propio directorio publica. Las direcciones de correo personales que aparecían en las páginas cacheadas del directorio y en las cabeceras de los `version.php` se sustituyeron por `[email]` en la versión publicada: ningún análisis las usa y los parsers dan el mismo resultado con y sin ellas. Por el mismo motivo se quitó el nombre de usuario incrustado en una URL de repositorio de Google Code del feed `pluglist_20260907.json`, cuya suma `.sha256` corresponde por tanto al fichero publicado; la del feed original descargado es `9e4f8c52675b2ea9f2b32687b7d45aa29c05f13109091a345e0d83d20bc1fe35`. El snapshot es del 7 de septiembre de 2026 y no se actualiza.

## Seguridad

Las credenciales viven en `.env` (en `.gitignore`), nunca en el código ni en el historial. Si aparece una contraseña escrita en un script, es un error: se corrige y se rota la contraseña (`ALTER CURRENT USER SET PASSWORD`).
