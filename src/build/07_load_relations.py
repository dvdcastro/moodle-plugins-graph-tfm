#!/usr/bin/env python3
"""
Fase 2 - Carga MAINTAINS (desde maintainers_raw.jsonl) y DEPENDS_ON (desde
version_php_raw.jsonl) en Neo4j. Idempotente (MERGE): se puede re-ejecutar
según avanzan los scrapers en background sin duplicar nada.

DEPENDS_ON solo cubre por ahora los plugins alojados en GitHub (fuente propia,
raw.githubusercontent.com). Los ~298 restantes llegan luego como export
autoritativo extraido de los ZIP del directorio (data/processed/version_php_zip_residual979.jsonl).

Uso: python3 07_load_relations.py
"""
import json
import os
from pathlib import Path

from neo4j import GraphDatabase

ROOT = Path(__file__).resolve().parents[2]


def _load_env() -> None:
    env_path = ROOT / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())


_load_env()

URI = os.environ["NEO4J_URI"]
AUTH = (os.environ["NEO4J_USER"], os.environ["NEO4J_PASSWORD"])
PROCESSED = ROOT / "data" / "processed"


def batched(iterable, n):
    it = iter(iterable)
    while True:
        chunk = [x for _, x in zip(range(n), it)]
        if not chunk:
            return
        yield chunk


def load_jsonl(path):
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


def main() -> None:
    driver = GraphDatabase.driver(URI, auth=AUTH)
    with driver.session() as session:
        # ---- MAINTAINS ----
        maint_rows = []
        for row in load_jsonl(f"{PROCESSED}/maintainers_raw.jsonl"):
            if not row.get("found"):
                continue
            for m in row.get("maintainers", []):
                if not m.get("user_id"):
                    continue
                maint_rows.append({
                    "component": row["component"],
                    "user_id": m["user_id"],
                    "name": m["name"],
                    "is_lead": m["is_lead"],
                })
        for chunk in batched(maint_rows, 500):
            session.run(
                """
                UNWIND $rows AS row
                MERGE (m:Maintainer {user_id: row.user_id})
                  ON CREATE SET m.display_name = row.name
                WITH m, row
                MATCH (p:Plugin {component: row.component})
                MERGE (m)-[r:MAINTAINS]->(p)
                SET r.is_lead = row.is_lead
                """,
                rows=chunk,
            )
        print(f"[MAINTAINS] {len(maint_rows)} relaciones desde {sum(1 for _ in load_jsonl(f'{PROCESSED}/maintainers_raw.jsonl'))} plugins scrapeados hasta ahora")

        # ---- Plugin.installations / downloads_90d / plugin_type_marketplace / set ----
        plugin_updates = []
        for row in load_jsonl(f"{PROCESSED}/maintainers_raw.jsonl"):
            if not row.get("found"):
                continue
            plugin_updates.append({
                "component": row["component"],
                "marketplace_id": row.get("marketplace_id"),
                "installations": row.get("installations"),
                "downloads_90d": row.get("downloads_90d"),
                "price_type": row.get("price_type"),
                "set_name": row.get("set_name"),
                "set_id": row.get("set_id"),
            })
        for chunk in batched(plugin_updates, 500):
            session.run(
                """
                UNWIND $rows AS row
                MATCH (p:Plugin {component: row.component})
                SET p.marketplace_id = row.marketplace_id,
                    p.installations = row.installations,
                    p.downloads_90d = row.downloads_90d,
                    p.price_type = row.price_type
                FOREACH (_ IN CASE WHEN row.set_id IS NOT NULL THEN [1] ELSE [] END |
                  MERGE (s:Set {set_id: row.set_id})
                  SET s.name = row.set_name
                  MERGE (p)-[:PART_OF]->(s)
                )
                """,
                rows=chunk,
            )
        print(f"[Plugin enrich + PART_OF] {len(plugin_updates)} plugins actualizados")

        # ---- DEPENDS_ON ----
        dep_rows = []
        plugin_source_rows = []
        for row in load_jsonl(f"{PROCESSED}/version_php_raw.jsonl"):
            if not row.get("found"):
                continue
            for dep_component, required_version in (row.get("dependencies") or {}).items():
                dep_rows.append({
                    "component": row["component"],
                    "depends_on_component": dep_component,
                    "required_version": required_version,
                    "provenance": "github_tag" if row.get("ref_used") not in (None, "main", "master") else "github_default_branch",
                })
            # Plugin.requires / declared version-in-file, utiles para riesgo/legacy_only despues
            plugin_source_rows.append({
                "component": row["component"],
                "requires": row.get("requires"),
                "version_in_file": row.get("version_in_file"),
                "ref_used": row.get("ref_used"),
            })

        for chunk in batched(plugin_source_rows, 500):
            session.run(
                """
                UNWIND $rows AS row
                MATCH (p:Plugin {component: row.component})
                SET p.requires_core = row.requires, p.version_in_source = row.version_in_file,
                    p.dep_source_ref = row.ref_used
                """,
                rows=chunk,
            )

        for chunk in batched(dep_rows, 500):
            session.run(
                """
                UNWIND $rows AS row
                MATCH (a:Plugin {component: row.component})
                MERGE (b:Plugin {component: row.depends_on_component})
                  ON CREATE SET b.in_directory = false, b.name = row.depends_on_component
                MERGE (a)-[r:DEPENDS_ON]->(b)
                SET r.required_version = row.required_version, r.provenance = row.provenance
                """,
                rows=chunk,
            )
        print(f"[DEPENDS_ON] {len(dep_rows)} relaciones")

        counts = session.run(
            """
            CALL {
              MATCH ()-[r:MAINTAINS]->() RETURN 'MAINTAINS' AS t, count(r) AS n
              UNION ALL
              MATCH ()-[r:DEPENDS_ON]->() RETURN 'DEPENDS_ON' AS t, count(r) AS n
              UNION ALL
              MATCH ()-[r:PART_OF]->() RETURN 'PART_OF' AS t, count(r) AS n
              UNION ALL
              MATCH (m:Maintainer) RETURN 'Maintainer(nodos)' AS t, count(m) AS n
              UNION ALL
              MATCH (p:Plugin) WHERE p.in_directory = false RETURN 'Plugin fuera de directorio' AS t, count(p) AS n
            }
            RETURN t, n ORDER BY t
            """
        ).data()
        print("\n--- conteos ---")
        for row in counts:
            print(f"  {row['t']}: {row['n']}")

    driver.close()


if __name__ == "__main__":
    main()
