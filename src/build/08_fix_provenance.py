#!/usr/bin/env python3
"""
Fase 2 - correccion: la exactitud de version.php NO se puede
inferir de ref_used (tag especifico vs. fallback a main/master). Un branch
puede ir por delante de la release publicada (aproximado aunque uso un ref
"especifico"), y un plugin dormido puede tener HEAD == release publicada
(exacto aunque cayo a main/master).

La unica senal fiable es comparar version_in_file (leido del propio
version.php) contra la version publicada mas reciente del feed
(plugins_raw.csv.latest_version). Este script recalcula esa comparacion y
actualiza Plugin.version_exact_match y DEPENDS_ON.provenance en Neo4j.

Uso: python3 08_fix_provenance.py
"""
import json
import os
from pathlib import Path

import pandas as pd
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


def main() -> None:
    plugins_df = pd.read_csv(f"{PROCESSED}/plugins_raw.csv")
    latest_version = dict(zip(plugins_df["component"], plugins_df["latest_version"]))

    vphp_rows = [json.loads(l) for l in open(f"{PROCESSED}/version_php_raw.jsonl") if l.strip()]

    exact, approx, no_compare = 0, 0, 0
    updates = []
    for row in vphp_rows:
        if not row.get("found"):
            continue
        component = row["component"]
        vif = row.get("version_in_file")
        published = latest_version.get(component)
        if vif is None or pd.isna(published):
            no_compare += 1
            exact_match = None
        else:
            exact_match = int(vif) == int(published)
            if exact_match:
                exact += 1
            else:
                approx += 1
        updates.append({
            "component": component,
            "version_exact_match": exact_match,
            "version_in_file": vif,
        })

    print(f"[recompute] exact={exact} approx={approx} no_compare={no_compare} "
          f"(total found={len(updates)})")

    driver = GraphDatabase.driver(URI, auth=AUTH)
    with driver.session() as session:
        for i in range(0, len(updates), 500):
            chunk = updates[i:i + 500]
            session.run(
                """
                UNWIND $rows AS row
                MATCH (p:Plugin {component: row.component})
                SET p.version_exact_match = row.version_exact_match
                """,
                rows=chunk,
            )
        # DEPENDS_ON.provenance ahora se deriva de version_exact_match del plugin ORIGEN
        # (la version.php de la que se leyo la propia declaracion de dependencias)
        session.run(
            """
            MATCH (a:Plugin)-[r:DEPENDS_ON]->(b:Plugin)
            WHERE a.version_exact_match IS NOT NULL
            SET r.provenance = CASE WHEN a.version_exact_match THEN 'exact' ELSE 'approximate' END
            """
        )
        result = session.run(
            """
            MATCH ()-[r:DEPENDS_ON]->()
            RETURN r.provenance AS prov, count(r) AS n
            ORDER BY prov
            """
        ).data()
        print("\n--- DEPENDS_ON por provenance (tras la correccion) ---")
        for row in result:
            print(f"  {row['prov']}: {row['n']}")
    driver.close()


if __name__ == "__main__":
    main()
