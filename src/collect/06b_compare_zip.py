#!/usr/bin/env python3
"""
Fase 1 (reproducibilidad) - Compara el jsonl reproducido por
06_zip_version_php.py contra el original de la descarga original del
2026-09-10 (data/processed/version_php_zip_residual979.jsonl), campo a campo,
sobre los campos que consume la fase de construccion del grafo
(09_merge_zip_residual.py) mas los de procedencia del archivo, y escribe
docs/zip_reproducibilidad.md.

El original sigue siendo el usado en todos los resultados; esto solo mide
cuanto de el se regenera desde fuentes publicas.

Cada diferencia se clasifica en una categoria (ver CATEGORY_TEXT):
  - mismo ZIP (zip_sha256 igual) pero distinto valor parseado -> diferencia
    del parser, no del dato;
  - distinto ZIP o distinto http_status -> el artefacto publicado cambio;
  - fila ausente en el reproducido -> error de descarga/proceso.

Uso: python3 src/collect/06b_compare_zip.py
      [--repro data/processed/version_php_zip_residual979_reproducido.jsonl]
      [--doc docs/zip_reproducibilidad.md]
"""
import argparse
import json
import re
import zipfile
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ORIGINAL = ROOT / "data" / "processed" / "version_php_zip_residual979.jsonl"
DEFAULT_REPRO = ROOT / "data" / "processed" / "version_php_zip_residual979_reproducido.jsonl"
DEFAULT_DOC = ROOT / "docs" / "zip_reproducibilidad.md"
CACHE_DIR = ROOT / "data" / "raw" / "zips" / "cache"
GITHUB_JSONL = ROOT / "data" / "processed" / "version_php_raw.jsonl"
# Lo que 09_merge_zip_residual.py escribe en el grafo, y solo para plugins
# donde GitHub no encontro ningun version.php (dep_source_ref IS NULL).
MERGE_FIELDS = ["version_in_zip", "requires_in_zip", "agrees_with_pluglist", "http_status", "note",
                "dependencies_in_zip"]

# Campos que importan aguas abajo (09_merge_zip_residual.py lee version,
# requires, dependencias, agrees_with_pluglist, http_status y note) mas la
# procedencia del archivo.
FIELDS = ["version_in_zip", "requires_in_zip", "dependencies_in_zip", "maturity_in_zip",
          "release_in_zip", "component_in_zip", "zip_sha256", "zip_md5_matched_published",
          "http_status", "agrees_with_pluglist"]
SECONDARY = ["version_php_path", "version_php_sha256", "zip_bytes", "note"]

CATEGORY_TEXT = {
    "artefacto_cambiado": (
        "El servidor entrego hoy un archivo distinto (zip_sha256 distinto) para la MISMA URL por version. "
        "No es un fallo del script: el directorio regenero o sustituyo el artefacto despues del 2026-09-10."),
    "acceso_cambiado": (
        "Cambio el codigo HTTP para la misma URL (por ejemplo un plugin de pago que paso a ser gratuito, "
        "o un artefacto retirado). Depende del servidor, no del procedimiento."),
    "parser_module_legacy": (
        "Mismo ZIP byte a byte. El version.php usa la convencion pre-2.0 `$module->` para `component`, "
        "`maturity` o `dependencies`. En 03_version_php.py solo VERSION_RE y REQUIRES_RE aceptan `$module->` "
        "(fix del 2026-09-10); MATURITY_RE, COMPONENT_RE y DEP_RE siguen exigiendo `$plugin->`, asi que el "
        "reproducido deja esos campos en null (o `{}`). version_in_zip y requires_in_zip coinciden. "
        "`component_in_zip` y `maturity_in_zip` no los consume 09_merge_zip_residual.py; el caso de "
        "`dependencies_in_zip`, si aparece, se discute aparte en la seccion de impacto."),
    "release_no_literal": (
        "Mismo ZIP byte a byte. `$plugin->release` no es un literal entre comillas: o es una expresion PHP "
        "concatenada (ej. `'2.3 (Build: '.$plugin->version.')'`, donde la descarga original guardo solo el primer "
        "fragmento) o un numero sin comillas (ej. `0.2`). El reproducido solo acepta literales entre comillas y lo "
        "deja en null. release_in_zip es informativo y no se usa aguas abajo."),
    "parser_otro": (
        "Mismo ZIP byte a byte pero distinto valor leido del version.php por otra diferencia de parser."),
    "seleccion_version_php": (
        "Mismo ZIP pero se eligio otro version.php dentro del archivo (distinto version_php_path)."),
    "ausente": "La fila no esta en el reproducido (error de red o de proceso; ver el log).",
}


def load(path: Path) -> dict:
    return {r["component"]: r for r in (json.loads(l) for l in open(path) if l.strip())}


def cached_version_php(r: dict) -> str | None:
    """Texto del version.php elegido, leido de la cache local de ZIP (si existe)."""
    zpath = CACHE_DIR / f"{r['component']}-{r['pluglist_declared_version']}.zip"
    if not zpath.exists() or not r.get("version_php_path"):
        return None
    with zipfile.ZipFile(zpath) as zf:
        return zf.read(r["version_php_path"]).decode("utf-8", errors="replace")


def categorize(o: dict, r: dict, diffs: list[str]) -> str:
    if o["http_status"] != r["http_status"]:
        return "acceso_cambiado"
    if o["zip_sha256"] != r["zip_sha256"]:
        return "artefacto_cambiado"
    if o["version_php_path"] != r["version_php_path"]:
        return "seleccion_version_php"
    text = cached_version_php(r) or ""
    legacy = {"maturity_in_zip": "maturity", "component_in_zip": "component",
              "dependencies_in_zip": "dependencies"}
    if set(diffs) <= set(legacy) and all(
            re.search(rf"\$module\s*->\s*{legacy[f]}\s*=", text) for f in diffs):
        return "parser_module_legacy"
    if diffs == ["release_in_zip"] and re.search(
            r"->\s*release\s*=\s*(['\"][^'\"]*['\"]\s*\.|[0-9])", text):
        return "release_no_literal"
    return "parser_otro"


def fmt(v) -> str:
    s = json.dumps(v, ensure_ascii=False)
    return s if len(s) <= 60 else s[:57] + "..."


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repro", type=Path, default=DEFAULT_REPRO)
    ap.add_argument("--doc", type=Path, default=DEFAULT_DOC)
    args = ap.parse_args()

    orig = load(ORIGINAL)
    repro = load(args.repro)
    n = len(orig)

    field_diff = Counter()
    secondary_diff = Counter()
    by_cat = defaultdict(list)
    exact_main, exact_all = 0, 0
    for comp, o in orig.items():
        r = repro.get(comp)
        if r is None:
            by_cat["ausente"].append((comp, []))
            continue
        diffs = [f for f in FIELDS if o.get(f) != r.get(f)]
        sdiffs = [f for f in SECONDARY if o.get(f) != r.get(f)]
        for f in diffs:
            field_diff[f] += 1
        for f in sdiffs:
            secondary_diff[f] += 1
        if not diffs:
            exact_main += 1
            if not sdiffs:
                exact_all += 1
            continue
        by_cat[categorize(o, r, diffs)].append((comp, diffs))

    o_status = Counter(o["http_status"] for o in orig.values())
    r_status = Counter(r["http_status"] for r in repro.values())
    o_md5 = sum(1 for o in orig.values() if o["zip_md5_matched_published"])
    r_md5 = sum(1 for r in repro.values() if r["zip_md5_matched_published"])
    o_ver = sum(1 for o in orig.values() if o["version_in_zip"] is not None)
    r_ver = sum(1 for r in repro.values() if r["version_in_zip"] is not None)
    same_zip = sum(1 for c, o in orig.items()
                   if c in repro and o["zip_sha256"] and o["zip_sha256"] == repro[c]["zip_sha256"])
    n_200 = o_status.get(200, 0)
    o_deps = sum(len(o["dependencies_in_zip"] or {}) for o in orig.values())
    r_deps = sum(len(repro[c]["dependencies_in_zip"] or {}) for c in orig if c in repro)

    L = []
    L.append("# Reproducibilidad de la fuente ZIP (residual de 979 plugins)\n")
    L.append(f"_Generado por `src/collect/06b_compare_zip.py` el "
             f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}. No editar a mano._\n")
    L.append("## Que se compara\n")
    L.append("- **Original:** `data/processed/version_php_zip_residual979.jsonl`, de la descarga original del "
             "2026-09-10. Es el archivo usado en **todos** los resultados de la memoria y no se modifica.")
    L.append(f"- **Reproducido:** `{args.repro.relative_to(ROOT) if args.repro.is_relative_to(ROOT) else args.repro}`, "
             "generado con `src/collect/06_zip_version_php.py` desde fuentes publicas: el snapshot "
             "`data/raw/pluglist_20260907.json` (URL de descarga y md5 por version) y el ZIP que sirve hoy el "
             "directorio de plugins de Moodle.")
    L.append("- La poblacion se re-deriva con `--population derive` y coincide exactamente con los 979 componentes del "
             "original (residual definido el 2026-09-08: plugins sin coincidencia exacta entre el `version.php` de "
             "GitHub y la version mas nueva del feed).\n")
    L.append("## Resultado\n")
    L.append("| | original | reproducido |")
    L.append("|---|---|---|")
    L.append(f"| filas | {n} | {len(repro)} |")
    L.append(f"| HTTP 200 (ZIP descargado) | {o_status.get(200, 0)} | {r_status.get(200, 0)} |")
    L.append(f"| HTTP 401 (plugin de pago, no descargable anonimo) | {o_status.get(401, 0)} | {r_status.get(401, 0)} |")
    L.append(f"| otros codigos HTTP | {n - o_status.get(200, 0) - o_status.get(401, 0)} | "
             f"{len(repro) - r_status.get(200, 0) - r_status.get(401, 0)} |")
    L.append(f"| md5 coincide con el publicado en el feed | {o_md5} | {r_md5} |")
    L.append(f"| version leida del version.php | {o_ver} | {r_ver} |")
    L.append(f"| dependencias declaradas (pares) | {o_deps} | {r_deps} |")
    L.append("")
    L.append(f"- **Filas identicas en todos los campos que importan aguas abajo** "
             f"({', '.join('`'+f+'`' for f in FIELDS)}): **{exact_main} / {n}** "
             f"({100 * exact_main / n:.1f}%).")
    L.append(f"- Identicas tambien en los campos secundarios ({', '.join('`'+f+'`' for f in SECONDARY)}): "
             f"{exact_all} / {n}.")
    L.append(f"- Mismo archivo byte a byte (`zip_sha256` igual) en {same_zip} de los {n_200} ZIP descargados "
             f"en la descarga original.\n")

    L.append("### Diferencias por campo\n")
    L.append("| campo | filas distintas |")
    L.append("|---|---|")
    for f in FIELDS:
        L.append(f"| `{f}` | {field_diff.get(f, 0)} |")
    for f in SECONDARY:
        L.append(f"| `{f}` (secundario) | {secondary_diff.get(f, 0)} |")
    L.append("")

    L.append("### Categorias de diferencia\n")
    if not by_cat:
        L.append("Ninguna: las 979 filas se reproducen exactamente.\n")
    for cat, items in sorted(by_cat.items(), key=lambda kv: -len(kv[1])):
        L.append(f"#### {cat} ({len(items)})\n")
        L.append(CATEGORY_TEXT[cat] + "\n")
        L.append("| componente | campo | original | reproducido |")
        L.append("|---|---|---|---|")
        for comp, diffs in sorted(items):
            r = repro.get(comp, {})
            for f in (diffs or ["(fila)"]):
                L.append(f"| `{comp}` | `{f}` | {fmt(orig[comp].get(f)) if f in orig[comp] else '-'} | "
                         f"{fmt(r.get(f)) if r else 'ausente'} |")
        L.append("")

    # Impacto aguas abajo: solo cuenta si 09_merge_zip_residual.py usa la fila.
    gh_found = {}
    if GITHUB_JSONL.exists():
        for line in open(GITHUB_JSONL):
            g = json.loads(line)
            gh_found[g["component"]] = bool(g.get("found"))
    L.append("## Impacto aguas abajo\n")
    L.append("09_merge_zip_residual.py solo escribe la fuente ZIP en el grafo para los plugins en los que GitHub no "
             "encontro ningun `version.php` (`dep_source_ref IS NULL`), y de cada fila usa "
             + ", ".join("`" + f + "`" for f in MERGE_FIELDS) + ". Para cada fila con diferencias:\n")
    L.append("| componente | categoria | GitHub encontro version.php | la fusion usa la fila ZIP | "
             "campos de la fusion que difieren |")
    L.append("|---|---|---|---|---|")
    n_impact = 0
    for cat, items in sorted(by_cat.items()):
        for comp, _ in sorted(items):
            r = repro.get(comp, {})
            mdiff = [f for f in MERGE_FIELDS if orig[comp].get(f) != r.get(f)]
            used = not gh_found.get(comp, False)
            if used and mdiff:
                n_impact += 1
            L.append(f"| `{comp}` | {cat} | {'si' if gh_found.get(comp) else 'no'} | {'si' if used else 'no'} | "
                     f"{', '.join('`'+f+'`' for f in mdiff) if mdiff else '-'} |")
    L.append("")
    L.append(f"**Filas cuya diferencia llegaria al grafo si se usara el reproducido en lugar del original: "
             f"{n_impact}.** El original sigue siendo el archivo de todos los resultados.\n")

    L.append("## Como reproducir\n")
    L.append("```bash")
    L.append("python3 src/collect/06_zip_version_php.py          # ~3 h: 979 peticiones a 10 s (Crawl-delay del robots.txt)")
    L.append("python3 src/collect/06b_compare_zip.py             # escribe este documento")
    L.append("```\n")
    L.append("Los ZIP quedan en `data/raw/zips/cache/` (fuera de git); una segunda ejecucion lee de la cache y "
             "no vuelve a pedir nada al servidor (`--offline` lo garantiza).")

    args.doc.write_text("\n".join(L) + "\n")
    print(f"[compare] exactas (campos aguas abajo) {exact_main}/{n}; categorias "
          f"{ {k: len(v) for k, v in by_cat.items()} }; por campo {dict(field_diff)} -> {args.doc}")


if __name__ == "__main__":
    main()
