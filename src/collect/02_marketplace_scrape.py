#!/usr/bin/env python3
"""
Fase 1 - Scrapea marketplace.moodle.com por cada component del feed pluglist,
para sacar: marketplace_id, mantenedores (con lead), instalaciones, descargas
90 dias, tipo de plugin, set ("Part of"), precio.

Respeta robots.txt (Crawl-delay: 10, confirmado en vivo el 2026-09-07 -> ~2.900
plugins * 10s = ~8h). Resumible: cachea cada HTML crudo en data/raw/html/ y
salta los ya descargados; escribe resultados incrementalmente a
data/processed/maintainers_raw.jsonl (una linea por plugin) para poder cortar
y retomar sin perder trabajo.

Uso: python3 02_marketplace_scrape.py [--limit N] [--delay 10]
"""
import argparse
import json
import re
import sys
import time
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_fixed

ROOT = Path(__file__).resolve().parents[2]
RAW_HTML_DIR = ROOT / "data" / "raw" / "html"
PROCESSED_DIR = ROOT / "data" / "processed"
OUT_PATH = PROCESSED_DIR / "maintainers_raw.jsonl"
BASE_URL = "https://marketplace.moodle.com/plugins/"
HEADERS = {
    "User-Agent": "moodle-plugins-graph-tfm/1.0 (proyecto academico UCAM/Structuralia; "
                  "contacto via forgejo david/moodle-plugins-graph)"
}


@retry(stop=stop_after_attempt(3), wait=wait_fixed(15))
def fetch(url: str) -> str:
    resp = requests.get(url, headers=HEADERS, timeout=30)
    if resp.status_code == 404:
        return ""  # plugin retirado del marketplace, tratar como ausente
    resp.raise_for_status()
    return resp.text


def parse_plugin_page(html: str, component: str) -> dict:
    soup = BeautifulSoup(html, "lxml")
    result = {"component": component, "marketplace_id": None, "maintainers": [],
              "installations": None, "downloads_90d": None, "plugin_type": None,
              "plugin_type_id": None, "set_name": None, "set_id": None,
              "price_type": None, "found": True}

    icon = soup.select_one("img.pgp-plugin-icon")
    if icon and icon.get("src"):
        m = re.search(r"/plugins/(\d+)/", icon["src"])
        if m:
            result["marketplace_id"] = int(m.group(1))

    maint_label = soup.find(string=lambda t: t and t.strip() == "Maintained by")
    if maint_label:
        links = maint_label.parent.parent.find_all("a")
        result["maintainers"] = [
            {"user_id": (re.search(r"/user/(\d+)", a.get("href", "")) or [None, None])[1],
             "name": a.get_text(strip=True), "is_lead": i == 0}
            for i, a in enumerate(links)
        ]

    installs_node = soup.find(string=lambda t: t and "Installations:" in t)
    if installs_node:
        m = re.search(r"Installations:\s*([\d,]+)", installs_node)
        if m:
            result["installations"] = int(m.group(1).replace(",", ""))

    downloads_node = soup.find(string=lambda t: t and "Downloads (last 90 days):" in t)
    if downloads_node:
        m = re.search(r"Downloads \(last 90 days\):\s*([\d,]+)", downloads_node)
        if m:
            result["downloads_90d"] = int(m.group(1).replace(",", ""))

    type_label = soup.find(string=lambda t: t and t.strip() == "Plugin type:")
    if type_label:
        a = type_label.parent.parent.find("a")
        if a:
            result["plugin_type"] = a.get_text(strip=True)
            m = re.search(r"type=(\d+)", a.get("href", ""))
            result["plugin_type_id"] = int(m.group(1)) if m else None

    set_label = soup.find(string=lambda t: t and t.strip() == "Part of:")
    if set_label:
        a = set_label.parent.parent.find("a")
        if a:
            result["set_name"] = a.get_text(strip=True)
            m = re.search(r"/sets/(\d+)", a.get("href", ""))
            result["set_id"] = int(m.group(1)) if m else None

    price_node = soup.select_one("div.fs-3")
    if price_node:
        result["price_type"] = re.sub(r"^Price option:\s*", "", price_node.get_text(strip=True)).strip()

    return result


def load_done_components() -> set[str]:
    if not OUT_PATH.exists():
        return set()
    done = set()
    with open(OUT_PATH) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                done.add(json.loads(line)["component"])
            except (json.JSONDecodeError, KeyError):
                continue
    return done


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--delay", type=float, default=10.0,
                     help="segundos entre requests (robots.txt exige Crawl-delay: 10)")
    args = ap.parse_args()

    RAW_HTML_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    plugins_df = pd.read_csv(PROCESSED_DIR / "plugins_raw.csv")
    components = plugins_df["component"].dropna().tolist()
    if args.limit:
        components = components[: args.limit]

    done = load_done_components()
    todo = [c for c in components if c not in done]
    print(f"[plan] {len(components)} plugins totales, {len(done)} ya hechos, {len(todo)} pendientes, "
          f"delay={args.delay}s -> ETA {len(todo) * args.delay / 3600:.1f}h")

    out_f = open(OUT_PATH, "a")
    n_ok, n_missing, n_err = 0, 0, 0
    for i, component in enumerate(todo, 1):
        cache_path = RAW_HTML_DIR / f"{component}.html"
        try:
            if cache_path.exists():
                html = cache_path.read_text()
            else:
                html = fetch(BASE_URL + component)
                cache_path.write_text(html)
                time.sleep(args.delay)  # solo dormir cuando de verdad pegamos a la red

            if not html:
                out_f.write(json.dumps({"component": component, "found": False}) + "\n")
                n_missing += 1
            else:
                row = parse_plugin_page(html, component)
                out_f.write(json.dumps(row, ensure_ascii=False) + "\n")
                n_ok += 1
            out_f.flush()
        except Exception as exc:  # noqa: BLE001 - loguear y seguir, no perder la corrida por un plugin
            print(f"[error] {component}: {exc}", file=sys.stderr)
            out_f.write(json.dumps({"component": component, "found": None, "error": str(exc)}) + "\n")
            out_f.flush()
            n_err += 1

        if i % 25 == 0 or i == len(todo):
            print(f"[progress] {i}/{len(todo)} -- ok={n_ok} missing={n_missing} err={n_err}")

    out_f.close()
    print(f"[done] ok={n_ok} missing={n_missing} err={n_err} -> {OUT_PATH}")


if __name__ == "__main__":
    main()
