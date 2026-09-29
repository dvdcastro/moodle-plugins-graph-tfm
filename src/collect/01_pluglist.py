#!/usr/bin/env python3
"""
Fase 0/1 - Descarga la 'fotografia' primaria del ecosistema de plugins de Moodle.

download.moodle.org/api/1.3/pluglist.php no requiere autenticacion. Se guarda
crudo (nunca se sobreescribe: cada corrida usa la fecha de hoy) mas su sha256,
y se derivan dos tablas planas (plugins_raw.csv, versions_raw.csv) mas
plugin_type/vcs_host/first-last_release_ts por plugin.

Uso: python3 01_pluglist.py
"""
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd
import requests

FEED_URL = "https://download.moodle.org/api/1.3/pluglist.php"
ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"

# Prefijos frankenstyle -> tipo de plugin (Moodle Component Reference).
# https://moodledev.io/docs/apis/commonfiles#moodle-component
KNOWN_PREFIXES = [
    "mod", "block", "local", "theme", "report", "tool", "admin_tool", "auth",
    "enrol", "format", "filter", "editor", "repository", "portfolio", "search",
    "cachestore", "cachelock", "message", "media", "gradeexport", "gradeimport",
    "gradereport", "gradingform", "mnetservice", "plagiarism", "webservice",
    "availability", "calendartype", "customfield", "fileconverter", "profilefield",
    "qbank", "qbehaviour", "qformat", "qtype", "quizaccess", "assignsubmission",
    "assignfeedback", "assignment", "atto", "tiny", "booktool", "coursereport",
    "datafield", "dataformat", "dataformat", "ltiservice", "logstore", "mlbackend",
    "contenttype", "h5plib", "forumreport", "scormreport", "workshopform",
    "workshopallocation", "workshopeval", "paygw", "tinymce", "antivirus",
    "communication", "customreport", "reportbuilder", "aiprovider", "aiplacement",
]
KNOWN_PREFIXES.sort(key=len, reverse=True)  # que "gradeexport" gane a "grade" si existiera


def guess_type(component: str) -> str:
    for prefix in KNOWN_PREFIXES:
        if component.startswith(prefix + "_"):
            return prefix
    return "unknown"


def guess_vcs_host(url: str | None) -> str:
    if not url:
        return "none"
    host = urlparse(url).netloc.lower()
    if "github" in host:
        return "github"
    if "gitlab" in host:
        return "gitlab"
    if "bitbucket" in host:
        return "bitbucket"
    if "moodle.org" in host:
        return "moodle.org"
    return host or "unknown"


def main() -> None:
    today = datetime.now(timezone.utc).strftime("%Y%m%d")
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    raw_path = RAW_DIR / f"pluglist_{today}.json"

    if raw_path.exists():
        print(f"[skip-download] {raw_path} ya existe hoy, no se vuelve a pedir la API.")
        raw_bytes = raw_path.read_bytes()
    else:
        print(f"GET {FEED_URL}")
        resp = requests.get(FEED_URL, timeout=60, headers={
            "User-Agent": "moodle-plugins-graph-tfm/1.0 (proyecto academico, contacto via forgejo david/moodle-plugins-graph)"
        })
        resp.raise_for_status()
        raw_bytes = resp.content
        raw_path.write_bytes(raw_bytes)
        print(f"[saved] {raw_path} ({len(raw_bytes)/1024:.1f} KB)")

    sha256 = hashlib.sha256(raw_bytes).hexdigest()
    sha_path = raw_path.with_suffix(raw_path.suffix + ".sha256")
    sha_path.write_text(f"{sha256}  {raw_path.name}\n")
    print(f"[sha256] {sha256}")

    data = json.loads(raw_bytes)
    plugins = data.get("plugins", data if isinstance(data, list) else [])
    print(f"[parsed] {len(plugins)} plugins en el feed")

    plugin_rows = []
    version_rows = []
    for p in plugins:
        component = p.get("component")
        versions = p.get("versions", []) or []
        # "newest" por el ENTERO version (no por el string release, que ordena mal
        # por backports -- primer hallazgo). Segundo hallazgo
        # (2026-09-07): "newest" por timecreated tambien sesga -- 54 plugins con
        # backports publicados DESPUES de una release hacia adelante quedan
        # subestimados en supportedmoodles. version (entero) es la senal correcta;
        # ademas max_supported_release ya no depende de "newest" en absoluto, ver abajo.
        newest = max(versions, key=lambda v: v.get("version", 0)) if versions else {}
        all_supported = {
            sm.get("release", "")
            for v in versions
            for sm in (v.get("supportedmoodles") or [])
            if sm.get("release")
        }

        plugin_rows.append({
            "component": component,
            "name": p.get("name"),
            "pluglist_id": p.get("id"),
            "source": p.get("source"),
            "doc": p.get("doc"),
            "bugs": p.get("bugs"),
            "discussion": p.get("discussion"),
            "timelastreleased": p.get("timelastreleased"),
            "plugin_type": guess_type(component) if component else "unknown",
            "n_versions": len(versions),
            "first_release_ts": min((v.get("timecreated", 0) for v in versions), default=None),
            "last_release_ts": max((v.get("timecreated", 0) for v in versions), default=None),
            "latest_version": newest.get("version"),
            "latest_release": newest.get("release"),
            "latest_maturity": newest.get("maturity"),
            "latest_downloadurl": newest.get("downloadurl"),
            "latest_downloadmd5": newest.get("downloadmd5"),
            "vcsrepositoryurl": newest.get("vcsrepositoryurl"),
            "vcsbranch": newest.get("vcsbranch"),
            "vcstag": newest.get("vcstag"),
            "vcs_host": guess_vcs_host(newest.get("vcsrepositoryurl")),
            # union de TODAS las versiones, no la de una sola "newest": un plugin
            # mantenido en varias ramas en paralelo no tiene una release actual,
            # tiene una por rama (hallazgo del 2026-09-07). Ademas comparar
            # release como string ("3.11" < "3.9" lexicograficamente) es el mismo
            # tipo de bug que el de version-como-string, asi que no se calcula un
            # "maximo" aqui -- ver 06_load_neo4j.py, que carga SUPPORTS desde esta
            # union completa en vez de elegir una release.
            "supported_releases": ";".join(sorted(all_supported)),
        })

        for v in versions:
            version_rows.append({
                "component": component,
                "version": v.get("version"),
                "release": v.get("release"),
                "maturity": v.get("maturity"),
                "downloadurl": v.get("downloadurl"),
                "downloadmd5": v.get("downloadmd5"),
                "vcssystem": v.get("vcssystem"),
                "vcsrepositoryurl": v.get("vcsrepositoryurl"),
                "vcsbranch": v.get("vcsbranch"),
                "vcstag": v.get("vcstag"),
                "timecreated": v.get("timecreated"),
                "supportedmoodles": ";".join(
                    sm.get("release", "") for sm in (v.get("supportedmoodles") or [])
                ),
            })

    plugins_df = pd.DataFrame(plugin_rows)
    versions_df = pd.DataFrame(version_rows)

    plugins_df.to_csv(PROCESSED_DIR / "plugins_raw.csv", index=False)
    versions_df.to_csv(PROCESSED_DIR / "versions_raw.csv", index=False)

    print(f"[written] plugins_raw.csv: {len(plugins_df)} filas")
    print(f"[written] versions_raw.csv: {len(versions_df)} filas")
    print("\n--- plugin_type (top 15) ---")
    print(plugins_df["plugin_type"].value_counts().head(15).to_string())
    print("\n--- vcs_host ---")
    print(plugins_df["vcs_host"].value_counts().to_string())
    n_stale = (plugins_df["latest_downloadurl"].isna()).sum()
    print(f"\n[check] plugins sin downloadurl en newest: {n_stale}")


if __name__ == "__main__":
    sys.exit(main())
