"""Paso 1: HTML del directorio -> cache/texts.jsonl (un documento por plugin).

Documento = cabecera (nombre, component, tipo) + og:description +
#pdp-description-content, truncado a DOC_CHARS. No se usa ningun dato del
grafo salvo nombre/tipo para la cabecera.
"""
import json
import re

from bs4 import BeautifulSoup

import config as C


def clean(s):
    return re.sub(r"\s+", " ", s or "").strip()


def main():
    with C.driver() as d, d.session() as s:
        meta = {r["c"]: (r["name"], r["t"]) for r in s.run(
            "MATCH (p:Plugin) RETURN p.component AS c, p.name AS name, p.plugin_type AS t")}
    files = sorted(C.HTML_DIR.glob("*.html"))
    stats = {"n": 0, "sin_desc_larga": 0, "sin_og": 0, "truncados": 0, "sin_nodo": 0}
    with C.TEXTS.open("w") as out:
        for f in files:
            comp = f.stem
            if comp not in meta:
                stats["sin_nodo"] += 1
                continue
            soup = BeautifulSoup(f.read_text(errors="ignore"), "lxml")
            og = soup.find("meta", property="og:description")
            og = clean(og["content"]) if og and og.get("content") else ""
            dd = soup.find(id="pdp-description-content")
            desc = clean(dd.get_text(" ", strip=True)) if dd else ""
            stats["sin_og"] += not og
            stats["sin_desc_larga"] += not desc
            # evita duplicar cuando og:description es el inicio de la larga
            body = desc if og and desc.startswith(og[:80]) else clean(f"{og} {desc}")
            name, ptype = meta[comp]
            text = f"{name} ({comp}). Tipo de plugin: {ptype}.\n{body}"
            if len(text) > C.DOC_CHARS:
                stats["truncados"] += 1
                text = text[:C.DOC_CHARS]
            out.write(json.dumps({"component": comp, "text": text, "body": body,
                                  "n_chars": len(text)}, ensure_ascii=False) + "\n")
            stats["n"] += 1
    print(stats)


if __name__ == "__main__":
    main()
