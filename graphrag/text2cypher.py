"""Linea base text-to-Cypher (peticion del tutor, octubre 2026).

El LLM (mismo gemini-2.5-flash, temperature 0, thinkingBudget 0 que los otros
tres sistemas) recibe el esquema del grafo (etiquetas, tipos de relacion,
propiedades con valores de ejemplo y una descripcion breve) y la pregunta, y
genera UNA consulta Cypher de solo lectura. La consulta se ejecuta contra
Neo4j y las filas se convierten en la respuesta final de dos formas:

  t2c          paso de formato con el LLM: mismo prompt de sistema y misma
               plantilla que 04_answer.py, con las filas como contexto
  t2c_directo  sin LLM: se citan como [component] todos los plugins que
               aparecen en las filas (cota de lo que la consulta trae)

Salvaguardas: sesion y transaccion de solo lectura (execute_read, modo READ),
filtro de clausulas de escritura y de procedimientos fuera de una lista
blanca, timeout de transaccion, LIMIT anadido si falta y tope de filas en el
cliente. Un unico reintento si Neo4j rechaza la consulta (error de sintaxis o
semantico), devolviendo el error al LLM.

Cache propia (cache/llm_t2c/, cache/usage_t2c.jsonl) con la misma clave que
config.generate: las re-ejecuciones no llaman a la API y los ficheros de los
otros sistemas no se tocan. El esquema se congela en cache/t2c_schema.txt.
"""
import hashlib
import importlib
import json
import os
import re

import neo4j
from neo4j.exceptions import ClientError, Neo4jError

import config as C

T2C_CACHE = C.CACHE / "llm_t2c"
T2C_USAGE = C.CACHE / "usage_t2c.jsonl"
SCHEMA_TXT = C.CACHE / "t2c_schema.txt"
T2C_CACHE.mkdir(parents=True, exist_ok=True)

TIMEOUT_S = 20          # timeout de transaccion en el servidor
MAX_ROWS = 200          # filas leidas como maximo (tope en el cliente)
DEFAULT_LIMIT = 100     # LIMIT que se anade si la consulta no trae ninguno
CTX_ROWS = 100          # filas que ve el paso de formato
CTX_CHARS = 12000       # y caracteres como maximo
TEXT_CHARS = 300        # recorte de cadenas largas (PluginText.text) en el contexto
REF_DATE = "2026-09-10"  # fecha de referencia del analisis (corte de 3 anios)

# Mismo prompt de sistema y plantilla que los otros tres sistemas
_ans = importlib.import_module("04_answer")
ANSWER_SYSTEM, ANSWER_TEMPLATE = _ans.SYSTEM, _ans.TEMPLATE

GEN_SYSTEM = (
    "Eres un experto en Cypher para Neo4j 5. Traduce la pregunta del usuario a UNA única "
    "consulta Cypher de solo lectura sobre el esquema dado. Reglas: usa solo MATCH, OPTIONAL "
    "MATCH, WHERE, WITH, UNWIND, RETURN, ORDER BY, LIMIT, subconsultas y funciones; nunca "
    "CREATE, MERGE, DELETE, SET, REMOVE, LOAD CSV ni procedimientos. Devuelve siempre la "
    "propiedad `component` de cada plugin pertinente para la respuesta, junto con las columnas "
    "que ayuden a responder (nombre, mantenedores, fechas…). Usa solo etiquetas, relaciones y "
    "propiedades del esquema. Termina con LIMIT 100 como máximo. Responde solo con la consulta "
    "dentro de un bloque ```cypher```, sin explicación.")

GEN_TEMPLATE = "ESQUEMA DEL GRAFO:\n{schema}\n\nPREGUNTA: {q}\n\nConsulta Cypher:"
RETRY_SUFFIX = ("\n\nTu consulta anterior:\n```cypher\n{prev}\n```\nfalló en Neo4j con este "
                "error:\n{err}\n\nCorrígela. Responde solo con la consulta corregida dentro de "
                "un bloque ```cypher```.")

# ----------------------------------------------------------------- esquema
# Descripciones breves (las que tendria cualquier documentacion del esquema).
DESCR = {
    "Plugin": "plugin o componente de Moodle (2.963; 75 del núcleo con in_directory=false)",
    "Plugin.component": "identificador frankenstyle único, p. ej. mod_customcert",
    "Plugin.name": "nombre visible en el directorio",
    "Plugin.plugin_type": "tipo de plugin (prefijo frankenstyle)",
    "Plugin.in_directory": "true si tiene página en el directorio oficial; false = núcleo de Moodle",
    "Plugin.installations": "nº de sitios que declaran tenerlo instalado",
    "Plugin.last_release_ts": "fecha de la última versión publicada (Unix, segundos)",
    "Plugin.first_release_ts": "fecha de la primera versión publicada (Unix, segundos)",
    "Plugin.louvain_soc": ("comunidad Louvain en el grafo social (plugins unidos por "
                           "co-mantenimiento); es la «comunidad» del análisis de riesgo"),
    "Plugin.louvain_full": "comunidad Louvain en el grafo completo (dependencias + co-mantenimiento + categoría)",
    "Plugin.pagerank_dep": "PageRank en el grafo de dependencias",
    "Plugin.degree_dep": "grado en el grafo de dependencias",
    "Maintainer": "persona que mantiene plugins",
    "Maintainer.display_name": "nombre de la persona",
    "Maintainer.n_plugins": "nº de plugins que mantiene",
    "Category": "categoría del directorio de plugins",
    "PluginText": "texto público de la página del plugin en el directorio (uno por plugin)",
    "PluginText.text": "descripción pública del plugin (texto libre, casi siempre en inglés)",
    "DEPENDS_ON": "(a:Plugin)-[:DEPENDS_ON]->(b:Plugin): a declara que requiere b",
    "MAINTAINS": "(m:Maintainer)-[:MAINTAINS]->(p:Plugin)",
    "CO_MAINTAINED": "(a:Plugin)-[:CO_MAINTAINED]->(b:Plugin): comparten al menos un mantenedor (derivada; una arista por par, sin dirección significativa: consúltala sin flecha)",
    "CO_MAINTAINS": "(m1:Maintainer)-[:CO_MAINTAINS]->(m2:Maintainer): mantienen juntos algún plugin (derivada; una arista por par, sin dirección significativa)",
    "SAME_CATEGORY": "(a:Plugin)-[:SAME_CATEGORY]->(b:Plugin): misma categoría (derivada, muy densa; una arista por par, sin dirección significativa)",
    "IN_CATEGORY": "(p:Plugin)-[:IN_CATEGORY]->(c:Category)",
    "SUPPORTS": "(p:Plugin)-[:SUPPORTS]->(r:MoodleRelease): versión de Moodle soportada",
    "PART_OF": "(p:Plugin)-[:PART_OF]->(s:Set): conjunto de plugins publicado junto",
    "DESCRIBES": "(t:PluginText)-[:DESCRIBES]->(p:Plugin)",
}
SKIP_PROPS = {("PluginText", "embedding"), ("PluginText", "model"),
              ("Plugin", "latest_downloadurl"), ("Plugin", "latest_downloadmd5"),
              ("Plugin", "dep_source_ref"), ("Plugin", "zip_note"), ("Plugin", "http_status_zip")}


def _ex(v):
    s = " ".join(str(v).split())
    return (s[:60] + "…") if len(s) > 60 else s


def build_schema(drv):
    """Esquema textual determinista a partir del catalogo de Neo4j."""
    with drv.session(default_access_mode=neo4j.READ_ACCESS) as s:
        nprops = s.run("CALL db.schema.nodeTypeProperties()").data()
        rprops = s.run("CALL db.schema.relTypeProperties()").data()
        pats = s.run("MATCH (a)-[r]->(b) RETURN labels(a)[0] AS a, type(r) AS r, "
                     "labels(b)[0] AS b, count(*) AS n ORDER BY a, r, b").data()
        counts = {r["l"]: r["n"] for r in s.run(
            "MATCH (n) RETURN labels(n)[0] AS l, count(*) AS n").data()}
        L = [f"Fecha de referencia del análisis: {REF_DATE} (úsala en lugar de la fecha actual "
             "para expresiones como «en los últimos N años»).", "", "NODOS"]
        by_label = {}
        for p in nprops:
            by_label.setdefault(p["nodeLabels"][0], []).append(p)
        for lab in sorted(by_label):
            L.append(f"(:{lab}) — {counts.get(lab, '?')} nodos" +
                     (f"; {DESCR[lab]}" if lab in DESCR else ""))
            for p in sorted(by_label[lab], key=lambda x: x["propertyName"]):
                name = p["propertyName"]
                if (lab, name) in SKIP_PROPS:
                    continue
                ex = s.run(f"MATCH (n:`{lab}`) WHERE n.`{name}` IS NOT NULL "
                           f"WITH DISTINCT n.`{name}` AS v ORDER BY v LIMIT 3 RETURN v").value()
                d = DESCR.get(f"{lab}.{name}")
                L.append(f"  .{name}: {'/'.join(p['propertyTypes'] or [])}"
                         f"{'' if p['mandatory'] else ' (puede faltar)'}"
                         f"{' — ' + d if d else ''}; ej.: {', '.join(_ex(v) for v in ex)}")
        L += ["", "RELACIONES"]
        for r in pats:
            L.append(f"(:{r['a']})-[:{r['r']}]->(:{r['b']}) — {r['n']} aristas"
                     + (f"; {DESCR[r['r']]}" if r["r"] in DESCR else ""))
        rp = {}
        for p in rprops:
            if p["propertyName"]:
                rp.setdefault(p["relType"].strip(":`"), []).append(
                    f"{p['propertyName']}: {'/'.join(p['propertyTypes'] or [])}")
        for t in sorted(rp):
            L.append(f"  propiedades de {t}: {', '.join(sorted(rp[t]))}")
    return "\n".join(L)


def schema(drv, rebuild=False):
    if SCHEMA_TXT.exists() and not rebuild:
        return SCHEMA_TXT.read_text()
    txt = build_schema(drv)
    SCHEMA_TXT.write_text(txt)
    return txt


# --------------------------------------------------------------- LLM + cache
def generate(system, prompt):
    """Igual que config.generate (misma clave de cache, mismo registro de uso),
    pero en cache/llm_t2c y cache/usage_t2c.jsonl. Con T2C_OFFLINE=1 un fallo
    de cache aborta en lugar de llamar a la API."""
    cfg = json.dumps(C.GEN_CONFIG, sort_keys=True)
    key = hashlib.sha256(f"{C.GEN_MODEL}|{cfg}|{system}|{prompt}".encode()).hexdigest()[:24]
    p = T2C_CACHE / f"{key}.json"
    if p.exists():
        return json.loads(p.read_text())
    if os.environ.get("T2C_OFFLINE") == "1":
        raise RuntimeError(f"T2C_OFFLINE=1 y no hay respuesta cacheada ({key})")
    body = {"systemInstruction": {"parts": [{"text": system}]},
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": C.GEN_CONFIG}
    out = C._post(f"{C.API}/{C.GEN_MODEL}:generateContent", body)
    cand = out.get("candidates", [{}])[0]
    text = "".join(pt.get("text", "") for pt in cand.get("content", {}).get("parts", []))
    um = out.get("usageMetadata", {})
    rec = {"model": C.GEN_MODEL, "model_version": out.get("modelVersion"),
           "text": text, "finish_reason": cand.get("finishReason"), "usage": um}
    with T2C_USAGE.open("a") as f:
        f.write(json.dumps({"ts": __import__("time").time(), "kind": "gen", "model": C.GEN_MODEL,
                            "key": key, "prompt_tokens": um.get("promptTokenCount", 0),
                            "out_tokens": um.get("candidatesTokenCount", 0)
                            + um.get("thoughtsTokenCount", 0)}) + "\n")
    p.write_text(json.dumps(rec, ensure_ascii=False, indent=1))
    return rec


def cost(usages):
    """US$ con los precios de config (mismo metodo que config.spend)."""
    pin = sum((u or {}).get("promptTokenCount", 0) for u in usages)
    pout = sum((u or {}).get("candidatesTokenCount", 0) + (u or {}).get("thoughtsTokenCount", 0)
               for u in usages)
    return pin, pout, pin / 1e6 * C.PRICE_GEN_IN + pout / 1e6 * C.PRICE_GEN_OUT


# ------------------------------------------------------------- salvaguardas
FENCE = re.compile(r"```(?:cypher)?\s*(.*?)```", re.S | re.I)
WRITE_KW = re.compile(r"\b(CREATE|MERGE|DELETE|DETACH|SET|REMOVE|DROP|FOREACH|LOAD\s+CSV|"
                      r"GRANT|REVOKE|DENY|ALTER|RENAME|TERMINATE|ENABLE|DISABLE|USE)\b", re.I)
CALL_PROC = re.compile(r"\bCALL\s+([A-Za-z_][\w.]*)", re.I)
ALLOWED_PROCS = {"db.index.fulltext.querynodes", "db.index.vector.querynodes",
                 "db.labels", "db.relationshiptypes", "db.propertykeys"}


def extract_cypher(text):
    m = FENCE.search(text or "")
    q = (m.group(1) if m else text or "").strip()
    return q.rstrip().rstrip(";").strip()


def _strip_noise(q):
    """Quita literales, comentarios, identificadores entre comillas invertidas,
    etiquetas/tipos (:Set) y accesos a propiedad (.set_id) antes de buscar
    palabras clave, para no rechazar p. ej. `(:Set)` o `CONTAINS 'set up'`."""
    q = re.sub(r"//[^\n]*|/\*.*?\*/", " ", q, flags=re.S)
    q = re.sub(r"'(?:\\.|[^'\\])*'|\"(?:\\.|[^\"\\])*\"", "''", q)
    q = re.sub(r"`[^`]*`", "x", q)
    q = re.sub(r":\s*[A-Za-z_]\w*", ":x", q)
    q = re.sub(r"\.\s*[A-Za-z_]\w*", ".x", q)
    return q


def check(q):
    """None si la consulta es aceptable; si no, el motivo del rechazo."""
    if not q:
        return "consulta vacía"
    clean = _strip_noise(q)
    m = WRITE_KW.search(clean)
    if m:
        return f"cláusula no permitida: {m.group(1).upper()}"
    for pm in CALL_PROC.finditer(re.sub(r"'(?:\\.|[^'\\])*'", "''", q)):
        proc = pm.group(1).lower()
        if proc.startswith(("apoc.", "dbms.", "gds.")) or proc not in ALLOWED_PROCS:
            return f"procedimiento no permitido: {pm.group(1)}"
    if ";" in clean:
        return "más de una sentencia"
    return None


def add_limit(q):
    return q if re.search(r"\bLIMIT\b", _strip_noise(q), re.I) else f"{q}\nLIMIT {DEFAULT_LIMIT}"


def execute(drv, q):
    """Ejecuta en transaccion de solo lectura con timeout. Devuelve
    (filas, columnas, truncado). Lanza Neo4jError si Neo4j la rechaza."""
    @neo4j.unit_of_work(timeout=TIMEOUT_S)
    def work(tx):
        res = tx.run(q)
        rows, trunc = [], False
        for i, rec in enumerate(res):
            if i >= MAX_ROWS:
                trunc = True
                break
            rows.append(rec.data())
        return rows, list(res.keys()), trunc
    with drv.session(default_access_mode=neo4j.READ_ACCESS) as s:
        return s.execute_read(work)


def _clean(v):
    if isinstance(v, dict):
        return {k: _clean(x) for k, x in v.items() if k != "embedding"}
    if isinstance(v, (list, tuple)):
        return [_clean(x) for x in v]
    if isinstance(v, str) and len(v) > TEXT_CHARS:
        return v[:TEXT_CHARS] + "…"
    if isinstance(v, (int, float, bool)) or v is None or isinstance(v, str):
        return v
    return str(v)


def components_in(rows, known):
    """Plugins presentes en las filas: cadenas que coinciden exactamente con un
    component del grafo (no se extraen menciones dentro de textos libres)."""
    out = []

    def walk(v):
        if isinstance(v, dict):
            for x in v.values():
                walk(x)
        elif isinstance(v, (list, tuple)):
            for x in v:
                walk(x)
        elif isinstance(v, str) and v in known:
            out.append(v)
    for r in rows:
        walk(r)
    return list(dict.fromkeys(out))


def rows_context(q, rows, trunc):
    lines = [json.dumps(_clean(r), ensure_ascii=False, default=str) for r in rows[:CTX_ROWS]]
    body, n = [], 0
    for ln in lines:
        if n + len(ln) > CTX_CHARS:
            break
        body.append(ln)
        n += len(ln) + 1
    note = "" if len(body) == len(rows) and not trunc else \
        f" (se muestran {len(body)} de {len(rows)}{'+' if trunc else ''})"
    return (f"CONSULTA CYPHER EJECUTADA SOBRE EL GRAFO:\n{q}\n\n"
            f"RESULTADO ({len(rows)}{'+' if trunc else ''} filas{note}):\n" + "\n".join(body))


# ------------------------------------------------------------------ sistema
class Text2Cypher:
    def __init__(self, drv=None):
        self.own = drv is None
        self.drv = drv or C.driver()
        self.schema = schema(self.drv)
        with self.drv.session(default_access_mode=neo4j.READ_ACCESS) as s:
            self.components = {r["c"] for r in s.run("MATCH (p:Plugin) RETURN p.component AS c")}

    def close(self):
        if self.own:
            self.drv.close()

    def query(self, question):
        """Genera y ejecuta la consulta (con un reintento). Devuelve un dict
        con la traza completa; nunca lanza por errores de la consulta."""
        base = GEN_TEMPLATE.format(schema=self.schema, q=question)
        trace = {"attempts": [], "usage_gen": []}
        prompt = base
        for attempt in (1, 2):
            resp = generate(GEN_SYSTEM, prompt)
            trace["usage_gen"].append(resp["usage"])
            q = extract_cypher(resp["text"])
            att = {"cypher": q}
            trace["attempts"].append(att)
            why = check(q)
            if why:
                att["status"], att["error"] = "rejected", why
                break                       # rechazo de seguridad: sin reintento
            q = add_limit(q)
            att["cypher_run"] = q
            try:
                rows, cols, trunc = execute(self.drv, q)
            except Neo4jError as e:
                msg = f"{e.code}: {e.message}" if getattr(e, "code", None) else str(e)
                low = f"{getattr(e, 'code', '') or ''} {msg}".lower()
                timeout = "timedout" in low or "timed out" in low or "timeout" in low
                att["status"], att["error"] = ("timeout" if timeout else "error"), msg[:600]
                if attempt == 1 and isinstance(e, ClientError) and not timeout:
                    prompt = base + RETRY_SUFFIX.format(prev=q, err=msg[:600])
                    continue
                break
            att["status"] = "ok" if rows else "empty"
            trace.update(rows=rows, columns=cols, truncated=trunc, cypher=q)
            break
        last = trace["attempts"][-1]
        trace["status"] = last["status"]
        trace["retried"] = len(trace["attempts"]) > 1
        trace.setdefault("rows", [])
        trace.setdefault("truncated", False)
        trace.setdefault("cypher", last.get("cypher_run", last["cypher"]))
        trace["components"] = components_in(trace["rows"], self.components)
        return trace

    def answer(self, question):
        """Devuelve (registro t2c, registro t2c_directo) en el formato de 04_answer."""
        t = self.query(question)
        comps = t["components"]
        common = {"question": question, "components": comps, "relations": [], "seeds": [],
                  "link_method": None, "cypher": t["cypher"], "status": t["status"],
                  "retried": t["retried"], "attempts": t["attempts"], "n_rows": len(t["rows"]),
                  "truncated": t["truncated"], "model": C.GEN_MODEL, "usage_gen": t["usage_gen"]}
        if t["status"] == "ok":
            ctx = rows_context(t["cypher"], t["rows"], t["truncated"])
            resp = generate(ANSWER_SYSTEM, ANSWER_TEMPLATE.format(ctx=ctx, q=question))
            fmt = {"context_chars": len(ctx), "answer": resp["text"],
                   "finish_reason": resp["finish_reason"],
                   "model_version": resp["model_version"], "usage": resp["usage"]}
        else:
            msg = ("La consulta no devolvió resultados: el contexto no permite responder."
                   if t["status"] == "empty" else
                   "No se pudo obtener una consulta válida: el contexto no permite responder.")
            fmt = {"context_chars": 0, "answer": msg, "finish_reason": None,
                   "model_version": None, "usage": {}}
        direct = ("Plugins devueltos por la consulta: " + ", ".join(f"[{c}]" for c in comps)
                  if comps else "La consulta no devolvió ningún plugin.")
        a = {"system": "t2c", **common, **fmt}
        b = {"system": "t2c_directo", **common, "context_chars": 0, "answer": direct,
             "finish_reason": None, "model_version": None, "usage": {}}
        return a, b
