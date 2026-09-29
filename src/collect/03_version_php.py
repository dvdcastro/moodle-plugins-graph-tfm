#!/usr/bin/env python3
"""
Fase 1 - Extrae $plugin->dependencies y $plugin->requires del version.php real
de cada plugin, via raw.githubusercontent.com (fuente de aristas DEPENDS_ON:
pluglist.php NO trae dependencias, viven solo en el codigo -- confirmado
tanto por la lectura de los ZIP como por verificacion directa en el zip de local_o365
el 2026-09-07).

Solo cubre vcs_host == 'github' en esta pasada (2.590 de 2.888 plugins) para
no competir por el Crawl-delay:10 de marketplace.moodle.com, que ya esta
ocupado por 02_marketplace_scrape.py. Los ~300 restantes (gitlab/bitbucket/
none/otros) quedan para un 03b_version_php_zip.py que baja el zip desde el
Marketplace, a correr DESPUES de que 02 termine.

Prueba una cadena de refs (vcstag -> vcsbranch -> tree_branch -> main ->
master) contra raw.githubusercontent.com/{owner}/{repo}/{ref}/{subdir}/version.php.
`tree_branch`/`subdir` se extraen de la propia vcsrepositoryurl cuando trae
forma .../tree/{branch}/{subdir...} (fix del 2026-09-10, tras detectar
el mismo patron de URL en la lectura de los ZIP). Cuando la URL NO
trae subdirectorio explicito (ej. un fork completo de moodle/moodle usado
como rama de desarrollo, sin ruta al subdirectorio del plugin en la URL),
sigue sin haber forma de adivinar donde vive el plugin dentro del repo --
limitacion conocida, documentada en docs/decisions.md.

Uso: python3 03_version_php.py [--limit N] [--delay 0.5]
"""
import argparse
import json
import re
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd
import requests
from tenacity import retry, stop_after_attempt, wait_fixed

ROOT = Path(__file__).resolve().parents[2]
RAW_VPHP_DIR = ROOT / "data" / "raw" / "versionphp"
PROCESSED_DIR = ROOT / "data" / "processed"
OUT_PATH = PROCESSED_DIR / "version_php_raw.jsonl"
HEADERS = {"User-Agent": "moodle-plugins-graph-tfm/1.0 (proyecto academico UCAM/Structuralia)"}

DEP_RE = re.compile(r"\$plugin\s*->\s*dependencies\s*=\s*(?:array\s*\(|\[)(.*?)(?:\)|\])\s*;", re.S)
# El valor puede ser un entero de version O la constante Moodle ANY_VERSION
# (=0 en core/lib/setuplib.php, "sin version minima"). Verificado sobre el
# residual de 979 (fuente ZIP, 2026-09-10): 52/282 dependencias
# usan ANY_VERSION -- antes de este fix, PAIR_RE solo aceptaba \d+ y las
# perdia en silencio (aqui y en la fuente GitHub por igual, mismo parser).
PAIR_RE = re.compile(r"""['"]([a-zA-Z0-9_]+)['"]\s*=>\s*(\d+|ANY_VERSION)""")
DEPENDENCY_VALUE_ALIASES = {"ANY_VERSION": 0}
# $module-> es la convencion pre-2.0 (antes de que Moodle renombrara la
# variable a $plugin->) -- el 2026-09-10 se detecto que 29/2590 de
# nuestros propios "found=True" no producian version_in_file; verificado
# aqui: la causa real son 3 variantes que el regex viejo no cubria: (1)
# $module->version en vez de $plugin->version (legacy real, ej.
# mod_widgetspace, mod_verbosity), (2) valor entre comillas (mismo bug
# detectado en el parser de los ZIP sobre local_confseed), (3) sufijo
# decimal no estandar tipo "2026040500.01" (ej. format_onetopic). Los
# genuinamente sin $plugin/module->version (ej. mod_openmeetings, que solo
# define $plugin->om_version, una propiedad no estandar inventada por ese
# plugin) siguen sin resolver -- correctamente, no hay nada que leer ahi.
REQUIRES_RE = re.compile(r"""\$(?:plugin|module)\s*->\s*requires\s*=\s*['"]?(\d+(?:\.\d+)?)['"]?\s*;""")
VERSION_RE = re.compile(r"""\$(?:plugin|module)\s*->\s*version\s*=\s*['"]?(\d+(?:\.\d+)?)['"]?\s*;""")
MATURITY_RE = re.compile(r"\$plugin\s*->\s*maturity\s*=\s*MATURITY_(\w+)\s*;")
COMPONENT_RE = re.compile(r"\$plugin\s*->\s*component\s*=\s*['\"]([a-zA-Z0-9_]+)['\"]\s*;")


def owner_repo(vcsrepositoryurl: str) -> tuple[str, str, str | None, str | None] | None:
    """Devuelve (owner, repo, tree_branch, subdir). Los dos ultimos son None
    salvo que la URL sea del tipo .../tree/{branch}/{subdir...} -- el mismo
    patron aparecio el 2026-09-10 en un lector de
    READMEs, que colapsaba esa URL a la raiz del fork y traia el README del
    nucleo de Moodle en vez del del plugin). Aqui el sintoma era el mismo
    tipo de dato (found=True, version_in_file=None): el fetch a la raiz
    trae version.php del nucleo, que no matchea $plugin->/$module-> y por
    eso fallaba en silencio sin corromper nada, solo sin dato. Cuando la
    URL ya trae el subdirectorio explicito, se usa directamente -- no hace
    falta adivinar la convencion de instalacion de Moodle por tipo de
    componente para este caso."""
    path = urlparse(vcsrepositoryurl).path.strip("/")
    parts = path.split("/")
    if len(parts) < 2:
        return None
    owner, repo = parts[0], parts[1]
    if repo.endswith(".git"):
        repo = repo[: -len(".git")]
    tree_branch, subdir = None, None
    if len(parts) >= 4 and parts[2] == "tree":
        tree_branch = parts[3]
        if len(parts) > 4:
            subdir = "/".join(parts[4:])
    return owner, repo, tree_branch, subdir


@retry(stop=stop_after_attempt(2), wait=wait_fixed(3))
def try_fetch(url: str) -> str | None:
    resp = requests.get(url, headers=HEADERS, timeout=20)
    if resp.status_code == 200:
        return resp.text
    return None


def parse_version_php(text: str) -> dict:
    deps = {}
    m = DEP_RE.search(text)
    if m:
        for name, ver in PAIR_RE.findall(m.group(1)):
            deps[name] = DEPENDENCY_VALUE_ALIASES[ver] if ver in DEPENDENCY_VALUE_ALIASES else int(ver)
    requires = REQUIRES_RE.search(text)
    version = VERSION_RE.search(text)
    maturity = MATURITY_RE.search(text)
    component = COMPONENT_RE.search(text)
    return {
        "dependencies": deps,
        "requires": int(float(requires.group(1))) if requires else None,
        "version_in_file": int(float(version.group(1))) if version else None,
        "maturity_in_file": maturity.group(1) if maturity else None,
        "component_in_file": component.group(1) if component else None,
    }


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
    ap.add_argument("--delay", type=float, default=0.5)
    args = ap.parse_args()

    RAW_VPHP_DIR.mkdir(parents=True, exist_ok=True)
    plugins_df = pd.read_csv(PROCESSED_DIR / "plugins_raw.csv")
    github_df = plugins_df[plugins_df["vcs_host"] == "github"].copy()
    if args.limit:
        github_df = github_df.head(args.limit)

    done = load_done()
    todo = github_df[~github_df["component"].isin(done)]
    print(f"[plan] {len(github_df)} plugins en github, {len(done)} ya hechos, "
          f"{len(todo)} pendientes, delay={args.delay}s -> ETA {len(todo) * args.delay / 3600:.2f}h")

    out_f = open(OUT_PATH, "a")
    n_ok, n_fail = 0, 0
    for i, (_, row) in enumerate(todo.iterrows(), 1):
        component = row["component"]
        cache_path = RAW_VPHP_DIR / f"{component}.php"
        result = {"component": component, "found": False, "ref_used": None, "subdir_used": None,
                  "dependencies": {}, "requires": None, "version_in_file": None,
                  "maturity_in_file": None, "component_in_file": None}
        try:
            if cache_path.exists():
                text = cache_path.read_text()
                result["found"] = True
                result["ref_used"] = "cache"
            else:
                ownerrepo = owner_repo(row["vcsrepositoryurl"]) if pd.notna(row["vcsrepositoryurl"]) else None
                text = None
                if ownerrepo:
                    owner, repo, tree_branch, subdir = ownerrepo
                    refs = [r for r in [row.get("vcstag"), row.get("vcsbranch"), tree_branch, "main", "master"]
                            if isinstance(r, str) and r]
                    path_suffix = f"{subdir}/version.php" if subdir else "version.php"
                    seen = set()
                    for ref in refs:
                        if ref in seen:
                            continue
                        seen.add(ref)
                        url = f"https://raw.githubusercontent.com/{owner}/{repo}/{ref}/{path_suffix}"
                        text = try_fetch(url)
                        time.sleep(args.delay)
                        if text:
                            result["ref_used"] = ref
                            result["subdir_used"] = subdir
                            break
                if text:
                    cache_path.write_text(text)
                    result["found"] = True

            if result["found"]:
                text = cache_path.read_text() if cache_path.exists() else text
                result.update(parse_version_php(text))
                n_ok += 1
            else:
                n_fail += 1

            out_f.write(json.dumps(result, ensure_ascii=False) + "\n")
            out_f.flush()
        except Exception as exc:  # noqa: BLE001
            print(f"[error] {component}: {exc}", file=sys.stderr)
            result["error"] = str(exc)
            out_f.write(json.dumps(result, ensure_ascii=False) + "\n")
            out_f.flush()
            n_fail += 1

        if i % 50 == 0 or i == len(todo):
            print(f"[progress] {i}/{len(todo)} -- ok={n_ok} fail={n_fail}")

    out_f.close()
    print(f"[done] ok={n_ok} fail={n_fail} -> {OUT_PATH}")


if __name__ == "__main__":
    main()
