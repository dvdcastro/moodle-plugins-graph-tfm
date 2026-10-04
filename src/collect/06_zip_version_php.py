#!/usr/bin/env python3
"""
Fase 1 (reproducibilidad) - Lee version.php directamente del ZIP publicado
por el directorio de plugins de Moodle para el residual de 979 plugins, y
reproduce data/processed/version_php_zip_residual979.jsonl con el MISMO
esquema a partir de fuentes publicas.

Contexto: para 979 plugins no hubo coincidencia exacta entre el version.php
leido de GitHub (03_version_php.py) y la version mas nueva que declara
pluglist.php. Para ellos la version y las dependencias se leyeron del ZIP
que publica el directorio. El archivo usado en todos los resultados es el de
la descarga original del 2026-09-10 (su procedimiento esta descrito en el
MANIFEST_full979.md que acompana al jsonl en data/raw/zips/); este script NO
lo reemplaza, solo demuestra que se puede regenerar desde cero. La
comparacion la hace 06b_compare_zip.py.

Procedimiento por plugin:
  1. Toma del snapshot data/raw/pluglist_20260907.json la version "newest"
     (maximo por el ENTERO version, mismo criterio que 01_pluglist.py) y su
     downloadurl + downloadmd5. La URL es por version
     (marketplace.moodle.com/api/plugins/<component>/versions/<version>/download),
     asi que apunta al mismo artefacto aunque el plugin haya publicado
     versiones nuevas despues del snapshot.
  2. Descarga el ZIP (secuencial, User-Agent academico identificable, pausa
     entre peticiones). La pausa efectiva es max(--delay, Crawl-delay del
     robots.txt del host); a 2026-10-04 el robots.txt declara Crawl-delay: 10.
     Cache en data/raw/zips/cache/ (gitignored); un 401 tambien se cachea
     para no repetir la peticion. Tope de tamano por archivo (--max-mb,
     250 MB por defecto, el mismo de la descarga original): si se supera se
     corta la descarga y el ZIP no se abre (zip_truncated_at_cap=true).
  3. Verifica el md5 contra el publicado en el feed.
  4. Ubica el version.php de nivel superior: basename EXACTAMENTE
     "version.php" (no endswith: eso captura check_conversion.php,
     package_version.php, etc.) con la menor profundidad dentro del ZIP.
  5. Lo parsea con parse_version_php() de 03_version_php.py (se importa, no
     se reescribe). Lo unico que ese parser no extrae es $plugin->release y
     el valor literal de cada dependencia; para no cambiar el esquema
     (dependencies_in_zip guarda los valores como string, ANY_VERSION
     incluido) se aplican DEP_RE/PAIR_RE del mismo modulo sobre el texto y
     se anade solo RELEASE_RE aqui.

Poblacion (--population):
  - "jsonl" (por defecto): los 979 componentes del jsonl original, en su
    mismo orden.
  - "derive": se re-deriva desde los datos del repo, tal como se definio el
    2026-09-08: todo plugin de plugins_raw.csv SIN coincidencia exacta entre
    el $plugin->version de su version.php de GitHub (cache data/raw/versionphp/,
    regex de version anterior al fix del 2026-09-10, commit 8ef6d7a, y
    excluyendo los encontrados via subdirectorio, fix posterior 7a50c09) y
    la latest_version del feed. Da exactamente los mismos 979; el script lo
    verifica e imprime la diferencia si la hubiera.

Uso:
  python3 src/collect/06_zip_version_php.py [--limit N] [--delay 2]
      [--out data/processed/version_php_zip_residual979_reproducido.jsonl]
      [--population jsonl|derive] [--max-mb 250] [--offline]
"""
import argparse
import hashlib
import importlib.util
import json
import re
import sys
import time
import zipfile
from pathlib import Path
from urllib.parse import urlparse

import requests

ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
PLUGLIST_PATH = RAW_DIR / "pluglist_20260907.json"
ORIGINAL_JSONL = PROCESSED_DIR / "version_php_zip_residual979.jsonl"
DEFAULT_OUT = PROCESSED_DIR / "version_php_zip_residual979_reproducido.jsonl"
CACHE_DIR = RAW_DIR / "zips" / "cache"
HEADERS = {"User-Agent": "moodle-plugins-graph-tfm/1.0 (proyecto academico UCAM/Structuralia, "
                         "reproducibilidad de TFM; descarga secuencial respetando Crawl-delay)"}

# Reutiliza el parser de 03_version_php.py (nombre de modulo no importable
# con "import" normal por empezar con digito).
_spec = importlib.util.spec_from_file_location("version_php_03", Path(__file__).with_name("03_version_php.py"))
vphp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(vphp)

# Unico regex nuevo: $plugin->release no lo extrae 03_version_php.py. Solo
# literales entre comillas (como en la descarga original): un release sin
# comillas (ej. auth_basic, `$plugin->release = 2022031600;`) queda null.
RELEASE_RE = re.compile(
    r"""\$(?:plugin|module)\s*->\s*release\s*=\s*(?:'([^']*)'|"([^"]*)")\s*;""")

NOTE_401 = "HTTP 401 - archive not downloadable without authentication (paid plugin)"
NOTE_NO_VPHP = "valid archive, but no version.php anywhere in it"
NOTE_NO_VERSION = ("version.php present but declares no machine-readable version "
                   "(no $plugin->version / $module->version assignment)")


def newest_versions() -> dict:
    """component -> version newest (por entero) del snapshot del feed."""
    data = json.loads(PLUGLIST_PATH.read_bytes())
    out = {}
    for p in data["plugins"]:
        versions = p.get("versions") or []
        if versions:
            out[p["component"]] = max(versions, key=lambda v: int(v.get("version") or 0))
    return out


def population_from_jsonl() -> list[str]:
    return [json.loads(l)["component"] for l in open(ORIGINAL_JSONL) if l.strip()]


def population_derived() -> list[str]:
    """Re-deriva el residual tal como se definio el 2026-09-08 (ver docstring)."""
    import pandas as pd
    old_version_re = re.compile(r"\$plugin\s*->\s*version\s*=\s*(\d+)\s*;")  # regex de 8ef6d7a
    plugins = pd.read_csv(PROCESSED_DIR / "plugins_raw.csv")
    gh = {}
    for line in open(PROCESSED_DIR / "version_php_raw.jsonl"):
        r = json.loads(line)
        gh[r["component"]] = r
    residual = []
    for _, row in plugins.iterrows():
        r = gh.get(row["component"])
        cache = RAW_DIR / "versionphp" / f"{row['component']}.php"
        exact = False
        if r and r.get("found") and not r.get("subdir_used") and cache.exists():
            m = old_version_re.search(cache.read_text(errors="replace"))
            exact = bool(m) and pd.notna(row["latest_version"]) and int(m.group(1)) == int(row["latest_version"])
        if not exact:
            residual.append(row["component"])
    return residual


def robots_crawl_delay(url: str) -> float:
    host = urlparse(url)
    try:
        txt = requests.get(f"{host.scheme}://{host.netloc}/robots.txt", headers=HEADERS, timeout=20).text
    except requests.RequestException:
        return 0.0
    m = re.search(r"(?im)^\s*crawl-delay\s*:\s*([\d.]+)", txt)
    return float(m.group(1)) if m else 0.0


def fetch_zip(component: str, version: str, url: str, max_bytes: int, offline: bool):
    """Devuelve (http_status, ruta_zip|None, truncado, hizo_red)."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    zpath = CACHE_DIR / f"{component}-{version}.zip"
    spath = CACHE_DIR / f"{component}-{version}.status.json"
    if zpath.exists():
        return 200, zpath, False, False
    if spath.exists():
        st = json.loads(spath.read_text())
        return st["http_status"], None, st.get("truncated", False), False
    if offline:
        raise RuntimeError("no esta en cache y se pidio --offline")
    with requests.get(url, headers=HEADERS, timeout=120, stream=True) as resp:
        if resp.status_code != 200:
            spath.write_text(json.dumps({"http_status": resp.status_code, "url": url}))
            return resp.status_code, None, False, True
        tmp = zpath.with_suffix(".part")
        size, truncated = 0, False
        with open(tmp, "wb") as f:
            for chunk in resp.iter_content(1 << 16):
                size += len(chunk)
                if size > max_bytes:
                    truncated = True
                    break
                f.write(chunk)
        if truncated:
            tmp.unlink()
            spath.write_text(json.dumps({"http_status": 200, "url": url, "truncated": True}))
            return 200, None, True, True
        tmp.rename(zpath)
        return 200, zpath, False, True


def pick_version_php(names: list[str]) -> str | None:
    cands = [n for n in names if n.rsplit("/", 1)[-1] == "version.php"]
    if not cands:
        return None
    return min(cands, key=lambda n: (n.count("/"), n))


def raw_dependencies(text: str) -> dict:
    """Mismos DEP_RE/PAIR_RE de 03_version_php.py, conservando el literal (str)."""
    m = vphp.DEP_RE.search(text)
    return {name: ver for name, ver in vphp.PAIR_RE.findall(m.group(1))} if m else {}


def process(component: str, nv: dict, args) -> tuple[dict, bool]:
    declared_version = int(nv["version"])
    row = {
        "agrees_with_pluglist": None, "component": component, "component_in_zip": None,
        "dependencies_in_zip": None, "http_status": None, "maturity_in_zip": None, "note": None,
        "pluglist_declared_release": nv.get("release"), "pluglist_declared_version": declared_version,
        "release_in_zip": None, "requires_in_zip": None, "version_in_zip": None,
        "version_php_path": None, "version_php_sha256": None, "zip_bytes": 0,
        "zip_md5_matched_published": None, "zip_sha256": None, "zip_truncated_at_cap": False,
    }
    status, zpath, truncated, networked = fetch_zip(
        component, nv["version"], nv["downloadurl"], args.max_mb * 1024 * 1024, args.offline)
    row["http_status"] = status
    row["zip_truncated_at_cap"] = truncated
    if status == 401:
        row["note"] = NOTE_401
        return row, networked
    if status != 200:
        row["note"] = f"HTTP {status}"
        return row, networked
    if truncated:
        row["note"] = f"archive over the {args.max_mb} MB per-file cap, not opened"
        return row, networked

    blob = zpath.read_bytes()
    row["zip_bytes"] = len(blob)
    row["zip_sha256"] = hashlib.sha256(blob).hexdigest()
    if nv.get("downloadmd5"):
        row["zip_md5_matched_published"] = hashlib.md5(blob).hexdigest() == nv["downloadmd5"].lower()
    try:
        zf = zipfile.ZipFile(zpath)
    except zipfile.BadZipFile:
        row["note"] = "downloaded file is not a valid zip archive"
        return row, networked
    with zf:
        vp = pick_version_php(zf.namelist())
        if vp is None:
            row["note"] = NOTE_NO_VPHP
            return row, networked
        vbytes = zf.read(vp)
    text = vbytes.decode("utf-8", errors="replace")
    parsed = vphp.parse_version_php(text)
    rel = RELEASE_RE.search(text)
    row.update({
        "version_php_path": vp,
        "version_php_sha256": hashlib.sha256(vbytes).hexdigest(),
        "dependencies_in_zip": raw_dependencies(text),
        "requires_in_zip": parsed["requires"],
        "version_in_zip": parsed["version_in_file"],
        "maturity_in_zip": f"MATURITY_{parsed['maturity_in_file']}" if parsed["maturity_in_file"] else None,
        "component_in_zip": parsed["component_in_file"],
        "release_in_zip": next((g for g in rel.groups() if g is not None), None) if rel else None,
    })
    if parsed["version_in_file"] is None:
        row["note"] = NOTE_NO_VERSION
    else:
        row["agrees_with_pluglist"] = parsed["version_in_file"] == declared_version
    return row, networked


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--delay", type=float, default=2.0,
                    help="pausa minima entre peticiones (s); se usa max(delay, Crawl-delay de robots.txt)")
    ap.add_argument("--max-mb", type=int, default=250)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--population", choices=["jsonl", "derive"], default="jsonl")
    ap.add_argument("--offline", action="store_true", help="solo cache, sin red")
    args = ap.parse_args()

    if args.out.resolve() == ORIGINAL_JSONL.resolve():
        sys.exit("[abort] --out no puede ser el jsonl original")

    newest = newest_versions()
    if args.population == "derive":
        comps = population_derived()
        if ORIGINAL_JSONL.exists():
            orig = set(population_from_jsonl())
            print(f"[population] derivada={len(comps)}; igual al jsonl original: {set(comps) == orig} "
                  f"(solo derivada={sorted(set(comps) - orig)}, solo original={sorted(orig - set(comps))})")
    else:
        comps = population_from_jsonl()
    if args.limit:
        comps = comps[: args.limit]

    delay = args.delay
    if not args.offline:
        sample_url = next(newest[c]["downloadurl"] for c in comps if c in newest)
        cd = robots_crawl_delay(sample_url)
        delay = max(args.delay, cd)
        print(f"[robots] Crawl-delay={cd}s -> pausa efectiva {delay}s")
    print(f"[plan] {len(comps)} componentes -> {args.out}")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    counts = {"200": 0, "401": 0, "other": 0, "error": 0, "net": 0}
    with open(args.out, "w") as out_f:
        for i, comp in enumerate(comps, 1):
            nv = newest.get(comp)
            if nv is None or not nv.get("downloadurl"):
                print(f"[error] {comp}: sin downloadurl en el snapshot", file=sys.stderr)
                counts["error"] += 1
                continue
            networked = False
            try:
                row, networked = process(comp, nv, args)
            except Exception as exc:  # noqa: BLE001
                print(f"[error] {comp}: {exc}", file=sys.stderr)
                counts["error"] += 1
                row = None
                networked = True
            if row is not None:
                key = str(row["http_status"]) if row["http_status"] in (200, 401) else "other"
                counts[key] += 1
                out_f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
                out_f.flush()
            if networked:
                counts["net"] += 1
                time.sleep(delay)
            if i % 25 == 0 or i == len(comps):
                print(f"[progress] {i}/{len(comps)} {counts}", flush=True)
    print(f"[done] {counts} -> {args.out}")


if __name__ == "__main__":
    main()
