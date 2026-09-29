#!/usr/bin/env python3
"""One-off: re-parsea version_php_raw.jsonl desde la cache local en
data/raw/versionphp/ (sin red) con los regex corregidos de
03_version_php.py -- recupera: dependencias ANY_VERSION, $module->version
(convencion pre-2.0), valores entre comillas, y version con sufijo decimal
no estandar (ver docstring de VERSION_RE en 03_version_php.py). No
re-descarga nada; mantenlo en sync manualmente si los regex de
03_version_php.py cambian otra vez.
"""
import json
import re
from pathlib import Path

DEP_RE = re.compile(r"\$plugin\s*->\s*dependencies\s*=\s*(?:array\s*\(|\[)(.*?)(?:\)|\])\s*;", re.S)
PAIR_RE = re.compile(r"""['"]([a-zA-Z0-9_]+)['"]\s*=>\s*(\d+|ANY_VERSION)""")
DEPENDENCY_VALUE_ALIASES = {"ANY_VERSION": 0}
REQUIRES_RE = re.compile(r"""\$(?:plugin|module)\s*->\s*requires\s*=\s*['"]?(\d+(?:\.\d+)?)['"]?\s*;""")
VERSION_RE = re.compile(r"""\$(?:plugin|module)\s*->\s*version\s*=\s*['"]?(\d+(?:\.\d+)?)['"]?\s*;""")
MATURITY_RE = re.compile(r"\$plugin\s*->\s*maturity\s*=\s*MATURITY_(\w+)\s*;")
COMPONENT_RE = re.compile(r"\$plugin\s*->\s*component\s*=\s*['\"]([a-zA-Z0-9_]+)['\"]\s*;")


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


ROOT = Path(__file__).resolve().parents[2]
RAW_VPHP_DIR = ROOT / "data" / "raw" / "versionphp"
OUT_PATH = ROOT / "data" / "processed" / "version_php_raw.jsonl"

rows = [json.loads(l) for l in open(OUT_PATH) if l.strip()]
n_changed = 0
n_recovered_version = 0
for row in rows:
    if not row.get("found"):
        continue
    cache_path = RAW_VPHP_DIR / f"{row['component']}.php"
    if not cache_path.exists():
        continue
    text = cache_path.read_text()
    had_version = row.get("version_in_file") is not None
    parsed = parse_version_php(text)
    if parsed != {k: row.get(k) for k in parsed}:
        n_changed += 1
    if not had_version and parsed["version_in_file"] is not None:
        n_recovered_version += 1
    row.update(parsed)

with open(OUT_PATH, "w") as f:
    for row in rows:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")

print(f"[reparse] {len(rows)} filas re-escritas, {n_changed} con algun campo distinto, "
      f"{n_recovered_version} recuperaron version_in_file que antes era null")
