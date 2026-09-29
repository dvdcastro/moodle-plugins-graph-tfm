#!/usr/bin/env python3
"""
Fase 2 (cierre) - Deriva las aristas Plugin-Plugin/Maintainer-Maintainer que
no vienen de ninguna fuente cruda: CO_MAINTAINED, CO_MAINTAINS, SAME_CATEGORY.
Consultas tomadas del plan de implementacion (docs/plan.md / artifact
1ef38130-43b2-4825-b47e-8365081caa21). Idempotente (MERGE + SET, se puede
re-ejecutar tras recargar nodos/relaciones).

SAME_CATEGORY usa peso normalizado 1/(n_categoria-1) -- sin normalizar,
"local" y "block" (las categorias mas grandes) generarian cliques de decenas
de miles de aristas cada una que dominarian Louvain por puro tamano de
categoria, no por señal real de comunidad (razon documentada en el plan
original).

Uso: python3 10_derive_edges.py
"""
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


def main() -> None:
    driver = GraphDatabase.driver(URI, auth=AUTH)
    with driver.session() as session:
        # ---- CO_MAINTAINED (Plugin-Plugin, peso = mantenedores compartidos) ----
        session.run(
            """
            MATCH (m:Maintainer)-[:MAINTAINS]->(p1:Plugin),
                  (m)-[:MAINTAINS]->(p2:Plugin)
            WHERE elementId(p1) < elementId(p2)
            WITH p1, p2, count(m) AS w, collect(m.display_name) AS shared
            MERGE (p1)-[r:CO_MAINTAINED]-(p2)
            SET r.weight = w, r.shared_maintainers = shared
            """
        )
        n = session.run("MATCH ()-[r:CO_MAINTAINED]-() RETURN count(r) AS n").single()["n"]
        print(f"[CO_MAINTAINED] {n // 2} aristas (no dirigidas)")

        # ---- CO_MAINTAINS (Maintainer-Maintainer, peso = plugins compartidos) ----
        session.run(
            """
            MATCH (m1:Maintainer)-[:MAINTAINS]->(p:Plugin)<-[:MAINTAINS]-(m2:Maintainer)
            WHERE elementId(m1) < elementId(m2)
            WITH m1, m2, count(p) AS w
            MERGE (m1)-[r:CO_MAINTAINS]-(m2)
            SET r.weight = w
            """
        )
        n = session.run("MATCH ()-[r:CO_MAINTAINS]-() RETURN count(r) AS n").single()["n"]
        print(f"[CO_MAINTAINS] {n // 2} aristas (no dirigidas)")

        # ---- SAME_CATEGORY (Plugin-Plugin, peso normalizado 1/(n_cat-1)) ----
        session.run(
            """
            MATCH (c:Category)<-[:IN_CATEGORY]-(p:Plugin)
            WITH c, collect(p) AS ps, count(p) AS n
            WHERE n > 1
            UNWIND ps AS p1
            UNWIND ps AS p2
            WITH p1, p2, n WHERE elementId(p1) < elementId(p2)
            MERGE (p1)-[r:SAME_CATEGORY]-(p2)
            SET r.weight = 1.0 / (n - 1)
            """
        )
        n = session.run("MATCH ()-[r:SAME_CATEGORY]-() RETURN count(r) AS n").single()["n"]
        print(f"[SAME_CATEGORY] {n // 2} aristas (no dirigidas)")

        counts = session.run(
            """
            CALL () {
              MATCH ()-[r:CO_MAINTAINED]-() RETURN 'CO_MAINTAINED' AS t, count(r)/2 AS n
              UNION ALL
              MATCH ()-[r:CO_MAINTAINS]-() RETURN 'CO_MAINTAINS' AS t, count(r)/2 AS n
              UNION ALL
              MATCH ()-[r:SAME_CATEGORY]-() RETURN 'SAME_CATEGORY' AS t, count(r)/2 AS n
            }
            RETURN t, n ORDER BY t
            """
        ).data()
        print("\n--- resumen aristas derivadas ---")
        for row in counts:
            print(f"  {row['t']}: {row['n']}")
    driver.close()


if __name__ == "__main__":
    main()
