# Plan — Prototipo GraphRAG sobre el grafo de plugins de Moodle

Fecha: 2026-09-28 · Entrega 2º borrador: 2026-09-30 · Presupuesto: ~1 jornada (8 h)
Estado: **plan** (sin código de implementación todavía). Solo se hicieron sondeos de lectura para validar la viabilidad (§8).

---

## 1. Objetivo y valor para la tesis

**Pregunta de investigación del prototipo.** ¿Mejora la recuperación aumentada con el grafo (GraphRAG) la calidad de las respuestas sobre el ecosistema de plugins respecto a una RAG vectorial pura, en preguntas que requieren información *relacional* (dependencias, co-mantenimiento, comunidad, riesgo)?

**Por qué ni RAG vectorial ni Cypher por separado bastan.**

| Enfoque | Qué resuelve | Qué no resuelve |
|---|---|---|
| RAG vectorial (solo descripciones) | "¿Qué plugin genera certificados PDF?" — similitud semántica sobre texto libre | Quién depende de `mod_certificate`, quién lo mantiene, si su comunidad es frágil: esa información **no está en el texto** de la página, está en las aristas del grafo |
| Cypher puro | Consultas exactas si el usuario sabe el esquema, el `component` y las propiedades | Preguntas en lenguaje natural, con nombres aproximados ("el plugin de certificados") y con criterios semánticos ("alternativas", "de evaluación") |
| **GraphRAG** | Enlaza la pregunta con nodos por similitud semántica y luego **expande por el grafo** (DEPENDS_ON, MAINTAINS, `louvain_soc`, índice de exposición) para dar al LLM un contexto relacional verificable | — |

**Vínculo con los objetivos de la tesis.** El prototipo convierte los productos analíticos de la tesis (nodos críticos por PageRank/intermediación, comunidades Louvain, índice de exposición T3) en **contexto consultable en lenguaje natural** para un administrador de Moodle. Es la respuesta directa a la observación del tutor ("reforzar el encaje con IA/Big Data"): combina embeddings, índice vectorial, LLM y el grafo ya construido, y se evalúa cuantitativamente contra un baseline.

Preguntas objetivo (ejemplos):
- "¿Qué alternativas mantenidas hay a `mod_certificate` y qué depende de él?"
- "¿Qué plugins de la misma comunidad que `block_xp` son frágiles (un solo mantenedor y sin release en >3 años)?"
- "¿Quién mantiene `mod_hvp` y qué otros plugins mantiene?"

## 2. Arquitectura

```
data/raw/html/<component>.html (2.888, caché ya existente)
   │  01_extract_text.py  (BeautifulSoup: og:description + #pdp-description-content)
   ▼
graphrag/cache/texts.jsonl   {component, text, n_chars}
   │  02_embed_load.py  (Gemini embeddings, lotes de 100, caché en disco)
   ▼
Neo4j: (:PluginText {component, text, embedding[768]})-[:DESCRIBES]->(:Plugin)
       VECTOR INDEX plugintext_embedding (cosine, 768)
   │
   │  retrieval.py
   ├── baseline_vector(q):  embed(q) → top-K PluginText → K fichas de plugin
   └── graphrag(q):         entity linking + top-k semilla → expansión Cypher:
   │                          · DEPENDS_ON entrantes/salientes
   │                          · Maintainer-[:MAINTAINS]→ otros plugins (top por instalaciones)
   │                          · misma louvain_soc, ordenados por exposición
   │                          · misma categoría + mantenidos, ordenados por similitud a la semilla
   │                        → fichas + líneas de relación, recortado a K fichas
   ▼
04_answer.py: prompt (español, "cita cada plugin como [component]", solo usar el contexto)
   → gemini-2.5-flash (temperature 0, thinkingBudget 0) → respuesta con citas
   ▼
05_evaluate.py: métricas deterministas vs verdad-terreno Cypher → tabla + figura
```

**Decisiones de diseño (justificadas por los sondeos, §8):**

1. **Unidad de recuperación = plugin, no fragmento.** Mediana de la descripción = ~1.100 caracteres (~280 tokens); solo 68 de 2.888 superan 6.000 caracteres. Un documento por plugin (nombre + component + tipo + categoría + descripción, truncado a ~6.000 caracteres ≈ 1.500 tokens, dentro del límite de 2.048 tokens de `gemini-embedding-001`) evita la complejidad de fusionar fragmentos. El "chunking" queda reducido a truncado; los 68 largos pierden la cola (limitación declarada). Mejora opcional si sobra tiempo: partir esos 68 en fragmentos de ~4.000 caracteres (varios `PluginText` por plugin).
2. **Nodo separado `:PluginText` en lugar de propiedad en `:Plugin`.** No toca las propiedades de análisis de `:Plugin` (centralidades, Louvain) ni el export `g_soc.graphml`; se borra de forma reversible con `MATCH (t:PluginText) DETACH DELETE t` + `DROP INDEX`. Se comprobó que ningún script de `src/` usa consultas sin etiqueta (`MATCH (n)`), así que la etiqueta nueva no contamina los análisis existentes.
3. **Join por `p.component`.** El sondeo muestra que `:Plugin` **sí tiene** la propiedad `component` en los 2.963 nodos, con índice RANGE `plugin_component`. No hace falta pasar por `pluglist_id` ↔ `plugins_raw.csv` (eso aplica a `p.name`, que es el nombre visible). Los 75 componentes del núcleo (`in_directory=false`) no tienen HTML: entran en el contexto solo vía expansión de grafo, con ficha mínima.
4. **Riesgo:** el índice de exposición (`E_exposicion`, `rank`, `SM`, `ST`, `ex_core`) vive en `data/processed/riesgo_exposicion_T3.csv` (2.876 filas), no en Neo4j. Se carga en memoria con pandas y se une por `component` al construir las fichas (no se escribe en el grafo).
5. **Equidad de la comparación:** ambos sistemas reciben el **mismo presupuesto de contexto** (K = 20 fichas de plugin, mismo formato, misma descripción recortada a 400 caracteres por ficha, mismo prompt y modelo). La única diferencia es *cómo* se eligen las fichas y que GraphRAG añade líneas de relación explícitas (`A -DEPENDS_ON-> B`).
6. **Entity linking** (solo GraphRAG, determinista): (a) regex de frankenstyle `[a-z]+_[a-z0-9_]+` contra el conjunto de 2.963 componentes; (b) si no, coincidencia exacta sin mayúsculas con `p.name`; (c) si no, top-1 vectorial. Se reporta la precisión del enlazado.

**Modelos (verificados 2026-09-28 contra `GET /v1beta/models` con la clave real y la página oficial de precios):**

| Uso | Modelo | Notas |
|---|---|---|
| Embeddings | `gemini-embedding-001` | 768 dims vía `outputDimensionality`, `taskType` RETRIEVAL_DOCUMENT / RETRIEVAL_QUERY, límite 2.048 tokens, soporta `batchEmbedContents`. Probado OK. Misma familia que el precedente Moodle Oracle. |
| Embeddings (alternativa) | `gemini-embedding-2` | Límite 8.192 tokens (evitaría truncar), 0,20 US$/M tokens. Probado OK. Usar si se quiere eliminar el truncado. |
| Generación | `gemini-2.5-flash` | Estable, 0,30 / 2,50 US$ por M tokens (entrada/salida). Probado OK. **Poner `thinkingBudget: 0`**: en el sondeo gastó 91 tokens de "thinking" para responder "OK". |
| Generación (fallback barato) | `gemini-2.5-flash-lite` | 0,10 / 0,40 US$. |

Se descartan los modelos `-preview` y los 3.x (más caros: `gemini-3.5-flash` 1,50 / 9,00 US$) para reproducibilidad y coste; se fija el nombre exacto del modelo en `config.py` y se registra en los resultados.

## 3. Evaluación

### 3.1 Conjunto de preguntas gold (30 preguntas, generadas por plantilla)

Las preguntas se generan **programáticamente** en `03_build_gold.py` a partir de plantillas + plugins semilla muestreados con semilla aleatoria fija, y la respuesta correcta se calcula **en el mismo script con Cypher/pandas**. Así la verdad-terreno es reproducible y no la escribe nadie a mano ni la juzga un LLM. Se congelan en `graphrag/gold/questions.jsonl` (versionado) **antes** de ejecutar cualquier sistema.

| Tipo | n | Plantilla (ejemplo) | Verdad-terreno | Pool de semillas |
|---|---|---|---|---|
| T1 Dependientes | 5 | "¿Qué plugins dependen de {name} ({component})?" | `MATCH (q:Plugin)-[:DEPENDS_ON]->(p {component:$c}) RETURN q.component` | 49 plugins con ≥3 dependientes (292 con ≥1) |
| T2 Dependencias + estado | 5 | "¿De qué plugins depende {c} y cuáles llevan >3 años sin release?" | DEPENDS_ON salientes + `last_release_ts < STALE_CUTOFF_UNIX` (constante de `_gds_utils.py`) | plugins con ≥2 dependencias salientes |
| T3 Co-mantenimiento | 5 | "¿Quién mantiene {c} y qué otros plugins mantiene?" | `(m)-[:MAINTAINS]->(p)`, `(m)-[:MAINTAINS]->(o)` (top-10 por instalaciones si hay muchos) | mantenedores con 3–15 plugins |
| T4 Comunidad frágil | 5 | "¿Qué plugins de la misma comunidad que {c} son frágiles (un mantenedor y sin release en >3 años)?" | misma `louvain_soc` ∩ `SM=1 ∧ ST=1` en `riesgo_exposicion_T3.csv` (top-10 por exposición) | comunidades de 10–150 plugins con ≥2 frágiles |
| T5 Alternativas mantenidas | 5 | "¿Qué alternativas mantenidas hay a {c}?" | **restricción**, no lista: misma categoría ∧ `last_release_ts ≥ STALE_CUTOFF_UNIX` ∧ ≠ semilla | plugins stale con ≥5 instalaciones |
| T6 Semántica pura (control) | 5 | "¿Qué plugin sirve para {función}?" (p. ej. "generar certificados PDF") | conjunto de components etiquetado a mano **antes** de ejecutar, a partir de las descripciones | — |

T6 es el **control honesto**: preguntas donde el baseline vectorial debería rendir igual o mejor. Si GraphRAG solo gana en T1–T5, eso es exactamente la afirmación de la tesis (el valor está en la estructura relacional), y se reporta así.

### 3.2 Métricas (todas deterministas, sin LLM-juez)

- **Recall@K de recuperación:** fracción de los components gold presentes en las K fichas de contexto. Aísla la recuperación del LLM.
- **Precisión / recall / F1 de citas:** se extraen los `[component]` citados en la respuesta con regex, se validan contra los 2.963 componentes existentes y se comparan con el conjunto gold. Para T5 (restricción) se reporta **tasa de cumplimiento**: fracción de alternativas citadas que cumplen misma categoría ∧ mantenida (verificado con Cypher).
- **Fidelidad de citas (faithfulness):** fracción de components citados que (a) existen en el grafo y (b) estaban en el contexto entregado. Lo contrario = tasa de alucinación.
- **Precisión del enlazado de entidades** (GraphRAG): la semilla enlazada == la semilla de la plantilla.
- **Contraste estadístico:** diferencia pareada GraphRAG − baseline por pregunta, con IC 95 % por bootstrap (10.000 remuestreos) y Wilcoxon pareado (`scipy` 1.18 ya está en el venv). Con n=30 se presenta como **exploratorio**, desglosado por tipo.

Reproducibilidad: temperatura 0, `thinkingBudget` 0, 1 ejecución por pregunta y sistema; respuestas cacheadas en `graphrag/cache/llm/` (clave = hash de prompt+modelo). Si hay tiempo: 3 ejecuciones para medir varianza.

## 4. Pasos, estimación y estructura de ficheros

### 4.1 Pasos

| # | Paso | Horas |
|---|---|---|
| 0 | Clave Gemini en `.env` de LXC 126, `pip install google-genai`, `graphrag/.gitignore`, `config.py` | 0,25 |
| 1 | `01_extract_text.py`: HTML → `texts.jsonl` (og:description + descripción; fallback a metadatos) | 0,5 |
| 2 | `02_embed_load.py`: embeddings por lotes con caché `.npy` + carga de `:PluginText` + `CREATE VECTOR INDEX` + prueba de humo (`mod_certificate` → top-5 plausible) | 1,0 |
| 3 | `retrieval.py`: baseline vectorial, entity linking, expansión Cypher, formato de fichas común | 1,5 |
| 4 | `03_build_gold.py`: plantillas T1–T5 + verdad Cypher; T6 etiquetado a mano; congelar `questions.jsonl` | 1,5 |
| 5 | `04_answer.py`: prompt, llamadas Gemini con reintentos (tenacity), caché | 0,75 |
| 6 | `05_evaluate.py`: métricas, bootstrap/Wilcoxon, `metrics.csv`, `metrics.md`, figura | 1,0 |
| 7 | Redacción de la subsección de la memoria + ejemplo cualitativo | 1,5 |
| | **Total** | **8,0 h** |

Orden crítico: 0→1→2→3 y 4 en paralelo conceptual (el gold no depende del sistema). El gold **debe** congelarse antes del paso 5.

### 4.2 Estructura

```
graphrag/
├── PLAN.md                  # este documento
├── .gitignore               # cache/
├── config.py                # modelos, dims=768, K=20, rutas, carga de .env (reutiliza _gds_utils.load_env)
├── 01_extract_text.py
├── 02_embed_load.py
├── 03_build_gold.py
├── retrieval.py
├── 04_answer.py
├── 05_evaluate.py
├── gold/questions.jsonl     # versionado: preguntas + verdad-terreno
├── results/
│   ├── answers_baseline.jsonl, answers_graphrag.jsonl   # versionados (pequeños)
│   ├── metrics.csv, metrics.md
│   └── fig_graphrag_eval.png
└── cache/                   # NO versionado: texts.jsonl, embeddings.npy, llm/
```

Solo se hace commit/push de `graphrag/` (las figuras de la memoria las copia después quien integre el `.docx`).

### 4.3 Dependencias

- `pip install google-genai` en `.venv` (SDK oficial; `tenacity` 9.1, `requests`, `bs4` 4.15, `lxml`, `neo4j` 6.3, `pandas`, `scipy`, `matplotlib` ya están). Alternativa sin dependencia nueva: REST con `requests` (los sondeos se hicieron así).
- Nada que instalar en Neo4j: 5.26.30 Community ya expone `db.index.vector.*` y `vector.similarity.cosine`.

### 4.4 La clave API en LXC 126 (sin exponerla)

Desde masters-ai-bot (192.168.1.144), sin que la clave aparezca en argumentos de proceso ni en el historial:

```bash
printf 'GEMINI_API_KEY=%s\n' "$GEMINI_API_KEY" | \
  ssh -i ~/.ssh/id_ed25519_masters-ai-bigdata homelab@192.168.1.126 \
  'cd ~/work/moodle-plugins-graph && cat >> .env && chmod 600 .env && git check-ignore -q .env && echo ignored-ok'
```

`.env` ya está en `.gitignore` (verificado). Nunca se escribe la clave en `graphrag/`, en logs ni en `results/`. `config.py` la lee con `load_env()`. Se verificó que LXC 126 tiene salida HTTPS a `generativelanguage.googleapis.com`.

### 4.5 Coste API

| Concepto | Tokens aprox. | Coste |
|---|---|---|
| Embeddings de documentos (4,18 M caracteres deduplicados ≈ 1,05 M tokens) | 1,05 M | ~0,16 US$ (`embedding-001`) / ~0,21 US$ (`embedding-2`) |
| Embeddings de consultas (30 + pruebas) | <0,01 M | ~0 |
| Generación: 30 preguntas × 2 sistemas × ~5k tokens de entrada + ~400 de salida | 0,3 M in / 0,025 M out | ~0,15 US$ |
| **Total** (incluyendo repeticiones y depuración ×3) | | **< 1 US$** |

Número de peticiones: ~29 lotes de embeddings (100 textos/lote) + ~60–180 generaciones. Compatible con el nivel gratuito si la clave lo es, pero con reintentos por 429.

## 5. Riesgos y mitigaciones

| Riesgo | Mitigación / fallback |
|---|---|
| Límites de tasa (429) o cuota | `batchEmbedContents` de 100, tenacity con backoff exponencial, caché en disco reanudable; bajar a `gemini-2.5-flash-lite` para generación |
| Caída/bloqueo de la API de Gemini | **Fallback sin API** para la parte de recuperación: TF-IDF + TruncatedSVD (LSA, 256 dims, sklearn) almacenado en el mismo índice vectorial. Permite reportar recall@K baseline vs GraphRAG aunque no haya generación |
| Texto HTML pobre | 102 páginas sin bloque de descripción → se usa `og:description`; 12 sin nada → ficha con nombre + tipo + categoría; 135 con <200 caracteres. Se reporta la cobertura |
| Descripciones en inglés, preguntas en español | Modelos de embedding multilingües; si la prueba de humo falla, se traduce la consulta al inglés con una llamada extra (documentado) |
| Sesgo del gold a favor del grafo | Control semántico T6; plantillas fijadas antes de ejecutar; la afirmación se limita a "preguntas relacionales" |
| El LLM no cita en el formato pedido | Prompt con ejemplo de formato; regex tolerante (`[component]`, `` `component` ``); se reporta la tasa de respuestas sin citas |
| Contaminar el grafo de análisis | Etiqueta separada `:PluginText`, borrado reversible; no se escribe ninguna propiedad en `:Plugin` |
| Memoria del contenedor | 2.888 × 768 floats ≈ 9 MB; irrelevante frente a 5,7 GB libres |

## 6. Qué entra en la memoria

**Ubicación propuesta:** nueva subsección **5.7 "Prototipo GraphRAG: consulta en lenguaje natural sobre el grafo"** (tras la regresión logística), con un párrafo de método en 4.x si el formato lo exige. Extensión 1–2 páginas.

Esquema:
1. **Motivación** (3–4 frases): los resultados de centralidad, comunidades y riesgo solo son útiles si un administrador puede consultarlos; RAG vectorial no ve las aristas.
2. **Método**: extracción de 2.888 descripciones, embeddings `gemini-embedding-001` (768 d), índice vectorial nativo de Neo4j, recuperación híbrida (top-k + expansión por DEPENDS_ON / MAINTAINS / Louvain / índice de exposición), generación con `gemini-2.5-flash` y citas obligatorias. Baseline: RAG vectorial con el mismo presupuesto de contexto.
3. **Evaluación**: 30 preguntas en 6 tipos con verdad-terreno Cypher; métricas deterministas (recall@K, F1 de citas, fidelidad, cumplimiento de restricciones); sin LLM-juez.
4. **Resultados**: tabla por tipo (baseline vs GraphRAG, IC bootstrap) + **Figura**: barras agrupadas de F1 de citas y recall@K por tipo de pregunta (T1–T6), baseline vs GraphRAG.
5. **Ejemplo cualitativo**: la pregunta de `mod_certificate` con ambas respuestas, recortadas.
6. **Limitaciones** (honestas):
   - n=30, plantillas generadas por el propio autor → evidencia exploratoria, no generalizable;
   - la verdad-terreno procede del mismo grafo: se mide la capacidad de **recuperar y verbalizar** el grafo, no la veracidad del grafo frente al mundo real;
   - un solo LLM y un solo modelo de embeddings, sin ajuste de hiperparámetros (K, profundidad de expansión);
   - descripciones truncadas en 68 plugins y sin descripción en 12;
   - dependencia de una API comercial externa (coste bajo pero no reproducible offline; se publican respuestas cacheadas);
   - expansión de grafo con reglas fijas, no aprendidas (no hay text-to-Cypher).

## 7. Línea de corte (versión mínima viable, ~4 h)

Si el tiempo se acorta, se entrega **solo esto**:
- Documento por plugin con truncado (sin fragmentación), `gemini-embedding-001`, índice vectorial.
- Expansión de grafo **solo** por DEPENDS_ON y MAINTAINS (sin comunidad ni categoría).
- **15 preguntas**: T1, T3 y T6 (5 cada una).
- Métricas: recall@K + F1 de citas + fidelidad. Sin bootstrap (tabla de medias por tipo).
- En la memoria: media página + tabla (sin figura).

Segundo nivel de corte (si la API falla): solo recuperación (recall@K) con el fallback LSA local, sin generación, presentado como "evaluación de la recuperación".

## 8. Hallazgos de los sondeos de viabilidad (2026-09-28, solo lectura)

- **HTML:** 2.888 páginas (51 MB). El texto útil está en `<meta property="og:description">` (resumen corto, mediana 148 caracteres; vacío en 12) y en `<div id="pdp-description-content">` (descripción larga; ausente en 102 páginas). Combinando ambos: mediana 1.091 caracteres, p10 = 338, p90 = 3.462, máx. 16.932; **<50 caracteres: 20; <200: 135; <500: 554**. Total deduplicado ≈ 4,18 M caracteres. La página también trae "Maintained by", "Supports Moodle", instalaciones, que ya están en el grafo y no se extraen del HTML.
- **Menciones cruzadas:** 396 descripciones mencionan otro component (p. ej. `mod_certificate` recomienda `mod_customcert`): señal útil para T5, no se modela como arista (posible mejora futura).
- **Neo4j:** 5.26.30 Community, GDS 2.13.12, APOC 5.26.30. Existen `db.index.vector.createNodeIndex`, `db.index.vector.queryNodes`, `vector.similarity.cosine`. No hay índices vectoriales todavía (solo RANGE/LOOKUP). No se creó ningún índice (sondeo de solo lectura).
- **`p.component`** existe en los 2.963 `:Plugin` con índice RANGE `plugin_component` → join directo, sin pasar por `pluglist_id`.
- `Category` solo tiene `code` y `n_plugins` (sin nombre legible); `SAME_CATEGORY` tiene `weight`; `MAINTAINS` tiene `is_lead`.
- Semillas disponibles: 292 plugins del directorio con ≥1 dependiente, 49 con ≥3; 853 comunidades `louvain_soc`.
- **Gemini:** la clave de masters-ai-bot funciona; `gemini-embedding-001` y `gemini-embedding-2` devuelven 768 dims con `outputDimensionality`; `gemini-2.5-flash` responde (consume "thinking" si no se desactiva). LXC 126 tiene salida HTTPS a la API. La clave **aún no** está en LXC 126.
- **venv de 126:** bs4 4.15, lxml, neo4j 6.3, pandas 3.0, sklearn 1.9, scipy 1.18, requests, tenacity presentes; falta `google-genai` (opcional).
- Hay ficheros sin versionar de la regresión logística (`13_prediccion_abandono.py`, `docs/prediccion_abandono.md`, figuras) en el working tree: **no** se incluyen en los commits de `graphrag/`.

**Bloqueadores:** ninguno. Único prerrequisito: copiar la clave a `.env` de LXC 126 (§4.4).
