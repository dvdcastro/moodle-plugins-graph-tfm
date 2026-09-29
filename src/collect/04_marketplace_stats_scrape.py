#!/usr/bin/env python3
"""
Fase 7 - Scrapea marketplace.moodle.com/plugins/{component}/stats por cada
component del feed pluglist, para obtener series temporales que la pagina de
producto normal no trae: instalaciones mensuales (historico completo, cada
plugin arranca en su propia fecha de primer tracking -- verificado que NO hay
un corte global: mod_attendance arranca en 2012-09, mod_livepoll en 2018-12),
desglose de instalaciones por version de Moodle soportada, y descargas
mensuales por version del plugin. Ninguno de estos tres esta en la pagina de
producto que ya scrapea 02_marketplace_scrape.py (esa solo trae el snapshot
actual: installations, downloads_90d).

Los datos vienen embebidos server-side en atributos data-chartjs-labels-value
/ data-chartjs-datasets-value de cada <canvas> (JSON con entities HTML
escapadas) -- no requiere navegador ni ejecutar JS. Verificado en un piloto de
45 componentes (30 mas fragiles de Fase 5 + 15 representantes de comunidades
de Fase 4, 2026-09-13): 45/45 paginas resueltas, hallazgo real de declive de
adopcion en varios plugins ya marcados como fragiles (ej. mod_certificate
paso de 11.360 instalaciones en pico, ene-2021, a 4.084 hoy, -64%).

Respeta robots.txt (Crawl-delay: 10, confirmado en vivo el 2026-09-13 -- sin
Disallow, sin excepcion para /stats). Resumible: cachea cada HTML crudo en
data/raw/html_stats/ y salta los ya descargados; escribe resultados
incrementalmente a data/processed/stats_series_raw.jsonl (una linea por
plugin) para poder cortar y retomar sin perder trabajo. ETA para las 2.888:
~8h a 10s/peticion.

Uso: python3 04_marketplace_stats_scrape.py [--limit N] [--delay 10]
"""
import argparse
import html as html_module
import json
import sys
import time
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_fixed

ROOT = Path(__file__).resolve().parents[2]
RAW_HTML_DIR = ROOT / "data" / "raw" / "html_stats"
PROCESSED_DIR = ROOT / "data" / "processed"
OUT_PATH = PROCESSED_DIR / "stats_series_raw.jsonl"
BASE_URL = "https://marketplace.moodle.com/plugins/"
HEADERS = {
    "User-Agent": "moodle-plugins-graph-tfm/1.0 (proyecto academico UCAM/Structuralia; "
                  "contacto via forgejo david/moodle-plugins-graph)"
}


@retry(stop=stop_after_attempt(3), wait=wait_fixed(15))
def fetch(url: str) -> tuple[int, str]:
    resp = requests.get(url, headers=HEADERS, timeout=30)
    if resp.status_code == 404:
        return 404, ""
    resp.raise_for_status()
    return resp.status_code, resp.text


def extract_chart(canvas) -> dict | None:
    labels_raw = canvas.get("data-chartjs-labels-value")
    datasets_raw = canvas.get("data-chartjs-datasets-value")
    if not labels_raw and not datasets_raw:
        return None
    labels = json.loads(html_module.unescape(labels_raw)) if labels_raw else None
    datasets = json.loads(html_module.unescape(datasets_raw)) if datasets_raw else None
    return {"labels": labels, "datasets": datasets}


def parse_stats_page(html_text: str) -> dict:
    soup = BeautifulSoup(html_text, "lxml")
    canvases = soup.find_all("canvas")
    result = {"installs_series": None, "installs_by_moodle_version": None,
              "downloads_series": None, "downloads_by_plugin_version": None}
    for c in canvases:
        datasets_raw = c.get("data-chartjs-datasets-value", "")
        decoded = html_module.unescape(datasets_raw)
        labels_raw = html_module.unescape(c.get("data-chartjs-labels-value", ""))
        chart_type = c.get("data-chartjs-type-value")
        if '"label":"Number of sites"' in decoded:
            result["installs_series"] = extract_chart(c)
        elif '"label":"Downloads"' in decoded:
            result["downloads_series"] = extract_chart(c)
        elif chart_type == "doughnut" and result["installs_by_moodle_version"] is None:
            result["installs_by_moodle_version"] = extract_chart(c)
        elif chart_type == "line":
            result["downloads_by_plugin_version"] = extract_chart(c)
    return result


def load_done() -> set[str]:
    if not OUT_PATH.exists():
        return set()
    done = set()
    with open(OUT_PATH) as f:
        for line in f:
            try:
                done.add(json.loads(line)["component"])
            except (json.JSONDecodeError, KeyError):
                continue
    return done


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--delay", type=float, default=10.0)
    args = ap.parse_args()

    RAW_HTML_DIR.mkdir(parents=True, exist_ok=True)
    plugins_df = pd.read_csv(PROCESSED_DIR / "plugins_raw.csv")
    components = plugins_df["component"].tolist()
    if args.limit:
        components = components[: args.limit]

    done = load_done()
    todo = [c for c in components if c not in done]
    print(f"[plan] {len(components)} plugins totales, {len(done)} ya hechos, "
          f"{len(todo)} pendientes, delay={args.delay}s -> ETA {len(todo) * args.delay / 3600:.2f}h")

    out_f = open(OUT_PATH, "a")
    n_ok, n_404, n_fail = 0, 0, 0
    for i, component in enumerate(todo, 1):
        cache_path = RAW_HTML_DIR / f"{component}.html"
        result = {"component": component, "found": False, **{
            k: None for k in ("installs_series", "installs_by_moodle_version",
                               "downloads_series", "downloads_by_plugin_version")
        }}
        try:
            if cache_path.exists():
                html_text = cache_path.read_text()
                status = 200
            else:
                status, html_text = fetch(BASE_URL + component + "/stats")
                if status == 200:
                    cache_path.write_text(html_text)
                time.sleep(args.delay)

            if status == 404:
                n_404 += 1
            else:
                result["found"] = True
                result.update(parse_stats_page(html_text))
                n_ok += 1

            out_f.write(json.dumps(result, ensure_ascii=False) + "\n")
            out_f.flush()
        except Exception as exc:  # noqa: BLE001
            print(f"[error] {component}: {exc}", file=sys.stderr)
            result["error"] = str(exc)
            out_f.write(json.dumps(result, ensure_ascii=False) + "\n")
            out_f.flush()
            n_fail += 1

        if i % 25 == 0 or i == len(todo):
            print(f"[progress] {i}/{len(todo)} -- ok={n_ok} 404={n_404} fail={n_fail}")

    out_f.close()
    print(f"[done] ok={n_ok} 404={n_404} fail={n_fail} -> {OUT_PATH}")


if __name__ == "__main__":
    main()
