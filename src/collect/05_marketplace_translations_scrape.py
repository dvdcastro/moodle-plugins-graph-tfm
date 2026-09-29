#!/usr/bin/env python3
"""
Fase 8 - Scrapea marketplace.moodle.com/plugins/{component}/translations por
cada component del feed pluglist, para obtener el % de cadenas de texto
traducidas a cada idioma por plugin -- un angulo de "esfuerzo comunitario" que
complementa el analisis de mantenedores (no esta en la pagina de producto que
scrapea 02_marketplace_scrape.py ni en /stats que scrapea
04_marketplace_stats_scrape.py).

Patron identico al de 04_marketplace_stats_scrape.py: los datos vienen
embebidos server-side en atributos data-chartjs-labels-value /
data-chartjs-datasets-value de un <div data-controller="chartjs"> (JSON con
entities HTML escapadas) -- no requiere navegador ni ejecutar JS. Verificado
en vivo el 2026-09-14 sobre 11 componentes variados en tamano/tipo:
  - 8 con seccion de traducciones completa y bien formada (labels tipo
    "Nombre [codigo]", datasets con % por idioma), incluyendo el plugin
    1939/mod_livepoll ya verificado manualmente antes de este script, mas
    theme_aardvark, block_simple_clock, block_unanswered_discussions,
    local_examnotice (caso de 1 solo idioma), mod_easycastms (155 idiomas,
    incluye porcentajes <100%, ej. Greek 47%), mod_lightboxgallery,
    aiprovider_pollinations, local_readaloud.
  - 2 casos de "Total strings in this plugin: 0" (auth_igovt,
    datapreset_national_education_network_resources): el <h3>/<p> de la
    seccion esta presente pero SIN el <div data-controller="chartjs"> (no hay
    grafico que renderizar con 0 cadenas) -- se trata como found=True,
    total_strings=0, languages=[].
  - 1 caso de plugin con pagina redirigida a login.moodle.org (SSO authentik)
    incluso para la pagina de producto normal, no solo /translations
    (block_use_stats) -- plugin no accesible sin autenticacion, mismo
    comportamiento que ya encontro 04 para esos 55 componentes (found=True
    pero sin datos, porque no hay nada que parsear en el HTML de login). No
    es un caso de "sin traducciones", es un caso de plugin no accesible.

Respeta robots.txt (Crawl-delay: 10, confirmado en vivo el 2026-09-14 --
sin Disallow, sin excepcion para /translations, mismo comportamiento que ya
usan 02 y 04). Resumible: cachea cada HTML crudo en
data/raw/html_translations/ y salta los ya descargados; escribe resultados
incrementalmente a data/processed/translations_raw.jsonl (una linea por
plugin) para poder cortar y retomar sin perder trabajo. ETA para las 2.888:
~8h a 10s/peticion.

Uso: python3 05_marketplace_translations_scrape.py [--limit N] [--delay 10]
"""
import argparse
import html as html_module
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
RAW_HTML_DIR = ROOT / "data" / "raw" / "html_translations"
PROCESSED_DIR = ROOT / "data" / "processed"
OUT_PATH = PROCESSED_DIR / "translations_raw.jsonl"
BASE_URL = "https://marketplace.moodle.com/plugins/"
HEADERS = {
    "User-Agent": "moodle-plugins-graph-tfm/1.0 (proyecto academico UCAM/Structuralia; "
                  "contacto via forgejo david/moodle-plugins-graph)"
}

TOTAL_STRINGS_RE = re.compile(r"Total strings in this plugin:\s*([\d,]+)")
LANG_LABEL_RE = re.compile(r"^(.+)\s\[([^\]]+)\]$")


@retry(stop=stop_after_attempt(3), wait=wait_fixed(15))
def fetch(url: str) -> tuple[int, str]:
    resp = requests.get(url, headers=HEADERS, timeout=30)
    if resp.status_code == 404:
        return 404, ""
    resp.raise_for_status()
    return resp.status_code, resp.text


def parse_translations_page(html_text: str) -> dict:
    soup = BeautifulSoup(html_text, "lxml")
    result = {"total_strings": None, "languages": []}

    p = soup.find("p", class_="text-muted", string=TOTAL_STRINGS_RE)
    if p:
        m = TOTAL_STRINGS_RE.search(p.get_text())
        if m:
            result["total_strings"] = int(m.group(1).replace(",", ""))

    div = soup.find("div", attrs={"data-controller": "chartjs"})
    if div is None:
        return result

    labels_raw = div.get("data-chartjs-labels-value")
    datasets_raw = div.get("data-chartjs-datasets-value")
    if not labels_raw or not datasets_raw:
        return result

    labels = json.loads(html_module.unescape(labels_raw))
    datasets = json.loads(html_module.unescape(datasets_raw))
    data = datasets[0]["data"] if datasets else []

    languages = []
    for label, pct in zip(labels, data):
        m = LANG_LABEL_RE.match(label)
        if m:
            languages.append({"language": m.group(1), "code": m.group(2), "pct_translated": pct})
        else:
            languages.append({"language": label, "code": None, "pct_translated": pct})
    result["languages"] = languages
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
        result = {"component": component, "found": False, "total_strings": None, "languages": []}
        try:
            if cache_path.exists():
                html_text = cache_path.read_text()
                status = 200
            else:
                status, html_text = fetch(BASE_URL + component + "/translations")
                if status == 200:
                    cache_path.write_text(html_text)
                time.sleep(args.delay)

            if status == 404:
                n_404 += 1
            else:
                result["found"] = True
                result.update(parse_translations_page(html_text))
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
