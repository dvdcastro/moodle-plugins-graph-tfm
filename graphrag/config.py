"""Configuracion comun del prototipo GraphRAG (ver PLAN.md).

Fija nombres de modelo, dimensiones, presupuesto de contexto y rutas; expone
clientes REST de Gemini con cache en disco y reintentos con backoff, y el
driver de Neo4j. La clave API se lee de .env (gitignored) y nunca se escribe
en disco ni en logs.
"""
import hashlib
import json
import os
import sys
import time
from pathlib import Path

import numpy as np
import requests

GR = Path(__file__).resolve().parent
ROOT = GR.parent
sys.path.insert(0, str(ROOT / "src" / "analyze"))
from _gds_utils import STALE_CUTOFF_UNIX, load_env  # noqa: E402

load_env()

# --- Modelos (fijados; PLAN.md §2) ---------------------------------------
EMBED_MODEL = "gemini-embedding-001"
EMBED_DIM = 768
GEN_MODEL = "gemini-2.5-flash"
GEN_CONFIG = {"temperature": 0, "thinkingConfig": {"thinkingBudget": 0},
              "maxOutputTokens": 2048}
# Precios (US$/M tokens) para la contabilidad de gasto
PRICE_EMBED = 0.15
PRICE_GEN_IN, PRICE_GEN_OUT = 0.30, 2.50

# --- Recuperacion ----------------------------------------------------------
K = 20                 # fichas de plugin por pregunta (ambos sistemas)
DESC_CHARS = 400       # descripcion recortada por ficha
DOC_CHARS = 6000       # truncado del documento a embeber (~1.500 tokens)
VECTOR_INDEX = "plugintext_embedding"

# --- Rutas -------------------------------------------------------------------
HTML_DIR = ROOT / "data" / "raw" / "html"
RISK_CSV = ROOT / "data" / "processed" / "riesgo_exposicion_T3.csv"
CACHE = GR / "cache"
TEXTS = CACHE / "texts.jsonl"
EMB_NPY = CACHE / "embeddings.npy"
EMB_IDX = CACHE / "embeddings_index.json"
LLM_CACHE = CACHE / "llm"
QEMB_CACHE = CACHE / "qemb"
USAGE_LOG = CACHE / "usage.jsonl"
GOLD = GR / "gold" / "questions.jsonl"
RESULTS = GR / "results"
FIG = ROOT / "figures" / "graphrag_resultados.png"
for d in (CACHE, LLM_CACHE, QEMB_CACHE, GOLD.parent, RESULTS):
    d.mkdir(parents=True, exist_ok=True)

API = "https://generativelanguage.googleapis.com/v1beta/models"


def driver():
    from neo4j import GraphDatabase
    return GraphDatabase.driver(
        os.environ["NEO4J_URI"],
        auth=(os.environ["NEO4J_USER"], os.environ["NEO4J_PASSWORD"]))


def _post(url, body, max_tries=8):
    """POST con backoff exponencial ante 429/5xx. La clave va en cabecera."""
    headers = {"x-goog-api-key": os.environ["GEMINI_API_KEY"],
               "Content-Type": "application/json"}
    wait = 5.0
    for attempt in range(max_tries):
        try:
            r = requests.post(url, headers=headers, json=body, timeout=120)
        except requests.RequestException as e:
            print(f"  red: {type(e).__name__}, reintento en {wait:.0f}s", flush=True)
            time.sleep(wait); wait = min(wait * 2, 120); continue
        if r.status_code == 200:
            return r.json()
        if r.status_code in (429, 500, 502, 503, 504):
            print(f"  HTTP {r.status_code}, reintento en {wait:.0f}s", flush=True)
            time.sleep(wait); wait = min(wait * 2, 120); continue
        raise RuntimeError(f"HTTP {r.status_code}: {r.text[:500]}")
    raise RuntimeError("demasiados reintentos")


def log_usage(kind, **kw):
    with USAGE_LOG.open("a") as f:
        f.write(json.dumps({"ts": time.time(), "kind": kind, **kw}) + "\n")


def _normalize(v):
    v = np.asarray(v, dtype=np.float32)
    return v / np.linalg.norm(v, axis=-1, keepdims=True)


def embed_batch(texts, task_type):
    """Embeddings sin cache (lo gestiona el llamador). Normalizados (L2):
    con outputDimensionality < 3072 Google recomienda normalizar."""
    body = {"requests": [{"model": f"models/{EMBED_MODEL}",
                          "content": {"parts": [{"text": t}]},
                          "taskType": task_type,
                          "outputDimensionality": EMBED_DIM} for t in texts]}
    out = _post(f"{API}/{EMBED_MODEL}:batchEmbedContents", body)
    # La API de embeddings no devuelve uso de tokens: se estima como chars/4.
    log_usage("embed", model=EMBED_MODEL, n=len(texts),
              est_tokens=sum(len(t) for t in texts) / 4)
    return _normalize([e["values"] for e in out["embeddings"]])


def embed_query(q):
    key = hashlib.sha256(f"{EMBED_MODEL}|{EMBED_DIM}|RETRIEVAL_QUERY|{q}".encode()).hexdigest()[:24]
    p = QEMB_CACHE / f"{key}.json"
    if p.exists():
        return np.asarray(json.loads(p.read_text())["v"], dtype=np.float32)
    v = embed_batch([q], "RETRIEVAL_QUERY")[0]
    p.write_text(json.dumps({"q": q, "model": EMBED_MODEL, "v": [round(float(x), 7) for x in v]}))
    return v


def generate(system, prompt):
    """Llamada a gemini-2.5-flash con cache por hash(modelo+config+prompt)."""
    cfg = json.dumps(GEN_CONFIG, sort_keys=True)
    key = hashlib.sha256(f"{GEN_MODEL}|{cfg}|{system}|{prompt}".encode()).hexdigest()[:24]
    p = LLM_CACHE / f"{key}.json"
    if p.exists():
        return json.loads(p.read_text())
    body = {"systemInstruction": {"parts": [{"text": system}]},
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": GEN_CONFIG}
    out = _post(f"{API}/{GEN_MODEL}:generateContent", body)
    cand = out.get("candidates", [{}])[0]
    text = "".join(pt.get("text", "") for pt in cand.get("content", {}).get("parts", []))
    um = out.get("usageMetadata", {})
    rec = {"model": GEN_MODEL, "model_version": out.get("modelVersion"),
           "text": text, "finish_reason": cand.get("finishReason"),
           "usage": um}
    log_usage("gen", model=GEN_MODEL, prompt_tokens=um.get("promptTokenCount", 0),
              out_tokens=um.get("candidatesTokenCount", 0) + um.get("thoughtsTokenCount", 0))
    p.write_text(json.dumps(rec, ensure_ascii=False, indent=1))
    return rec


def spend():
    """Gasto acumulado estimado (US$) a partir de cache/usage.jsonl."""
    tot = 0.0
    if USAGE_LOG.exists():
        for line in USAGE_LOG.read_text().splitlines():
            r = json.loads(line)
            if r["kind"] == "embed":
                tot += r["est_tokens"] / 1e6 * PRICE_EMBED
            else:
                tot += r["prompt_tokens"] / 1e6 * PRICE_GEN_IN + r["out_tokens"] / 1e6 * PRICE_GEN_OUT
    return tot
