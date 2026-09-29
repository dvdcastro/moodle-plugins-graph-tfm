#!/usr/bin/env python3
"""
Fase 2 - Fusiona la segunda fuente (ZIP del directorio, ver
docs/decisions.md "Segunda fuente real para el residual") con el grafo ya
cargado. Cubre el residual de 979 plugins que 03_version_php.py no pudo
resolver via GitHub (03b/zip), completando Plugin.version_exact_match y
DEPENDS_ON con la mejor fuente disponible por plugin.

DECISION DE MERGE (para no pisar datos ya buenos): esto SOLO rellena
plugins donde GitHub no encontro version.php en absoluto
(Plugin.dep_source_ref IS NULL, el subconjunto "554 unusable" de la
reconciliacion). Para los 425 restantes del residual (153 approx + 272
mismatch), GitHub SI encontro un version.php real -- su declaracion de
dependencias desde el HEAD del repo ya esta cargada por 07_load_relations.py
y se deja intacta. Fusionar ahi tambien la version del ZIP (la version
REALMENTE publicada, distinta de HEAD por definicion en el grupo mismatch)
es una pregunta metodologica real -- "cual pesa mas para un grafo de riesgo,
lo que declara el HEAD o lo que la gente realmente instala" -- que no se
resuelve aqui con un pisado silencioso de una fuente sobre otra. Queda
para una decision explicita antes de Fase 5 (interpretacion de riesgo),
donde SI importa. Ver docs/decisions.md.

PRECAUCION DE TIPOS: dependencies_in_zip trae los valores de version como
STRING (a diferencia de version_php_raw.jsonl, donde el parser propio ya
los deja como int) -- el mismo tipo de bug de comparacion str/int que ya
nos mordio dos veces en este proyecto (ver reconciliacion 2026-09-08).
Cast explicito a int aqui antes de escribir a Neo4j.

Uso: python3 09_merge_zip_residual.py
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
ZIP_RESIDUAL = PROCESSED / "version_php_zip_residual979.jsonl"

# Moodle define ANY_VERSION=0 (core/lib/setuplib.php) como constante PHP para
# "sin version minima" en $plugin->dependencies. El campo dependencies_in_zip
# trae los valores como string (ver docstring del modulo); "ANY_VERSION" es
# el unico literal no numerico que aparece en los 979 (verificado sobre el
# dataset completo antes de escribir esto, no asumido).
DEPENDENCY_VALUE_ALIASES = {"ANY_VERSION": 0}


def _dep_version_to_int(value: str) -> int:
    if value in DEPENDENCY_VALUE_ALIASES:
        return DEPENDENCY_VALUE_ALIASES[value]
    return int(value)


def batched(iterable, n):
    it = iter(iterable)
    while True:
        chunk = [x for _, x in zip(range(n), it)]
        if not chunk:
            return
        yield chunk


def main() -> None:
    rows = [json.loads(l) for l in open(ZIP_RESIDUAL) if l.strip()]

    plugin_updates = []
    dep_source_components = []
    for row in rows:
        component = row["component"]
        plugin_updates.append({
            "component": component,
            "version_in_source_zip": row.get("version_in_zip"),
            "requires_core_zip": row.get("requires_in_zip"),
            "version_exact_match_zip": row.get("agrees_with_pluglist"),
            "http_status_zip": row.get("http_status"),
            "zip_note": row.get("note"),
        })
        deps = row.get("dependencies_in_zip") or {}
        if deps:
            dep_source_components.append((component, deps))

    driver = GraphDatabase.driver(URI, auth=AUTH)
    with driver.session() as session:
        # Solo escribe version_in_source / version_exact_match / dep_source_ref
        # cuando el plugin NO tiene ya una fuente de GitHub (dep_source_ref IS NULL).
        for chunk in batched(plugin_updates, 500):
            session.run(
                """
                UNWIND $rows AS row
                MATCH (p:Plugin {component: row.component})
                WHERE p.dep_source_ref IS NULL
                SET p.version_in_source = row.version_in_source_zip,
                    p.requires_core = row.requires_core_zip,
                    p.version_exact_match = row.version_exact_match_zip,
                    p.dep_source_ref = 'zip_marketplace',
                    p.http_status_zip = row.http_status_zip,
                    p.zip_note = row.zip_note
                """,
                rows=chunk,
            )
        result = session.run(
            "MATCH (p:Plugin) WHERE p.dep_source_ref = 'zip_marketplace' RETURN count(p) AS n"
        ).single()
        print(f"[merge zip -> Plugin] {result['n']} plugins completados solo via ZIP "
              f"(GitHub no habia encontrado version.php)")

        # DEPENDS_ON: mismo criterio -- solo para componentes que acaban de
        # quedar marcados dep_source_ref='zip_marketplace' en este mismo run
        # o en uno anterior (idempotente).
        dep_rows = []
        for component, deps in dep_source_components:
            for dep_component, required_version in deps.items():
                dep_rows.append({
                    "component": component,
                    "depends_on_component": dep_component,
                    "required_version": _dep_version_to_int(required_version),
                })
        for chunk in batched(dep_rows, 500):
            session.run(
                """
                UNWIND $rows AS row
                MATCH (a:Plugin {component: row.component})
                WHERE a.dep_source_ref = 'zip_marketplace'
                MERGE (b:Plugin {component: row.depends_on_component})
                  ON CREATE SET b.in_directory = false, b.name = row.depends_on_component
                MERGE (a)-[r:DEPENDS_ON]->(b)
                SET r.required_version = row.required_version, r.provenance = 'zip_marketplace'
                """,
                rows=chunk,
            )
        print(f"[DEPENDS_ON via ZIP] hasta {len(dep_rows)} relaciones candidatas procesadas")

        counts = session.run(
            """
            CALL () {
              MATCH ()-[r:DEPENDS_ON]->() WHERE r.provenance = 'zip_marketplace' RETURN 'DEPENDS_ON (zip)' AS t, count(r) AS n
              UNION ALL
              MATCH ()-[r:DEPENDS_ON]->() RETURN 'DEPENDS_ON (total)' AS t, count(r) AS n
              UNION ALL
              MATCH (p:Plugin) WHERE p.version_exact_match IS NOT NULL RETURN 'Plugin con version_exact_match' AS t, count(p) AS n
              UNION ALL
              MATCH (p:Plugin) WHERE p.in_directory <> false AND p.version_in_source IS NULL RETURN 'Plugin sin ninguna fuente de version' AS t, count(p) AS n
            }
            RETURN t, n ORDER BY t
            """
        ).data()
        print("\n--- conteos tras la fusion ---")
        for row in counts:
            print(f"  {row['t']}: {row['n']}")

    driver.close()


if __name__ == "__main__":
    main()
