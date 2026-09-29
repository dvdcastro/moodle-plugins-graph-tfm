#!/usr/bin/env python3
"""
Fase 2 - Carga en Neo4j lo que ya esta disponible: nodos Plugin, Category y
MoodleRelease + relaciones IN_CATEGORY y SUPPORTS. MAINTAINS/DEPENDS_ON se
cargan aparte (load_relations_from_scrape.py) cuando terminen los scrapers
de la Fase 1, porque dependen de maintainers_raw.jsonl / version_php_raw.jsonl.

Uso: python3 06_load_neo4j.py
"""
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
ROOT_PROCESSED = ROOT / "data" / "processed"


def batched(iterable, n):
    it = iter(iterable)
    while True:
        chunk = [x for _, x in zip(range(n), it)]
        if not chunk:
            return
        yield chunk


def main() -> None:
    plugins_df = pd.read_csv(f"{ROOT_PROCESSED}/plugins_raw.csv")
    versions_df = pd.read_csv(f"{ROOT_PROCESSED}/versions_raw.csv")
    plugins_df = plugins_df.where(pd.notna(plugins_df), None)

    driver = GraphDatabase.driver(URI, auth=AUTH)
    with driver.session() as session:
        # ---- Plugin ----
        rows = plugins_df.to_dict("records")
        for chunk in batched(rows, 500):
            session.run(
                """
                UNWIND $rows AS row
                MERGE (p:Plugin {component: row.component})
                SET p.name = row.name,
                    p.pluglist_id = row.pluglist_id,
                    p.source = row.source,
                    p.plugin_type = row.plugin_type,
                    p.n_versions = row.n_versions,
                    p.first_release_ts = row.first_release_ts,
                    p.last_release_ts = row.last_release_ts,
                    p.latest_version = row.latest_version,
                    p.latest_release = row.latest_release,
                    p.latest_maturity = row.latest_maturity,
                    p.latest_downloadurl = row.latest_downloadurl,
                    p.latest_downloadmd5 = row.latest_downloadmd5,
                    p.vcsrepositoryurl = row.vcsrepositoryurl,
                    p.vcsbranch = row.vcsbranch,
                    p.vcstag = row.vcstag,
                    p.vcs_host = row.vcs_host,
                    p.supported_releases = row.supported_releases,
                    p.in_directory = true
                """,
                rows=chunk,
            )
        print(f"[Plugin] {len(rows)} nodos cargados/actualizados")

        # ---- Category (derivada de plugin_type) ----
        cat_counts = plugins_df["plugin_type"].value_counts()
        cat_rows = [{"code": code, "n_plugins": int(n)} for code, n in cat_counts.items()]
        session.run(
            """
            UNWIND $rows AS row
            MERGE (c:Category {code: row.code})
            SET c.n_plugins = row.n_plugins
            """,
            rows=cat_rows,
        )
        session.run(
            """
            MATCH (p:Plugin), (c:Category {code: p.plugin_type})
            MERGE (p)-[:IN_CATEGORY]->(c)
            """
        )
        print(f"[Category] {len(cat_rows)} categorias, IN_CATEGORY creado")

        # ---- MoodleRelease (de versions_raw.supportedmoodles, explotado) ----
        releases = set()
        for cell in versions_df["supportedmoodles"].dropna():
            for r in str(cell).split(";"):
                r = r.strip()
                if r:
                    releases.add(r)
        release_rows = [{"release": r} for r in sorted(releases)]
        session.run(
            """
            UNWIND $rows AS row
            MERGE (:MoodleRelease {release: row.release})
            """,
            rows=release_rows,
        )
        print(f"[MoodleRelease] {len(release_rows)} releases")

        # ---- SUPPORTS (Plugin -> MoodleRelease, union de TODAS las versiones) ----
        # No "la ultima version": un plugin mantenido en varias ramas en paralelo
        # no tiene una release actual, tiene una por rama (hallazgo del
        # 2026-09-07 -- ver docs/decisions.md). La union evita tener que elegir,
        # pero "alguna vez lo soporto" != "lo soporta ahora" (segundo hallazgo,
        # mismo dia): sin filtro de recencia, plugins viejos acumulan grado en
        # SUPPORTS por antiguedad, no por relevancia estructural -- contaminaria
        # cualquier metrica que mezclara SUPPORTS con DEPENDS_ON/CO_MAINTAINED.
        # Se guarda declared_at (max timecreated de la version que declaro esa
        # release) en la relacion, para poder filtrar por recencia en la query
        # en vez de comprometerse en la carga (mismo principio que
        # version_exact_match: guardar el dato, no la derivacion).
        supports_rows = []
        for _, row in versions_df.iterrows():
            cell = row.get("supportedmoodles")
            if pd.isna(cell) or not str(cell).strip():
                continue
            for r in str(cell).split(";"):
                r = r.strip()
                if r:
                    supports_rows.append({
                        "component": row["component"], "release": r,
                        "timecreated": row.get("timecreated"),
                    })
        supports_df = pd.DataFrame(supports_rows)
        supports_df = supports_df.groupby(["component", "release"], as_index=False)["timecreated"].max()
        supports_rows = supports_df.to_dict("records")
        for chunk in batched(supports_rows, 1000):
            session.run(
                """
                UNWIND $rows AS row
                MATCH (p:Plugin {component: row.component})
                MATCH (r:MoodleRelease {release: row.release})
                MERGE (p)-[rel:SUPPORTS]->(r)
                SET rel.declared_at = row.timecreated
                """,
                rows=chunk,
            )
        print(f"[SUPPORTS] {len(supports_rows)} relaciones (con declared_at)")

        # ---- sanity checks ----
        counts = session.run(
            """
            CALL {
              MATCH (p:Plugin) RETURN 'Plugin' AS label, count(p) AS n
              UNION ALL
              MATCH (c:Category) RETURN 'Category' AS label, count(c) AS n
              UNION ALL
              MATCH (r:MoodleRelease) RETURN 'MoodleRelease' AS label, count(r) AS n
            }
            RETURN label, n ORDER BY label
            """
        ).data()
        print("\n--- conteo de nodos ---")
        for row in counts:
            print(f"  {row['label']}: {row['n']}")

    driver.close()


if __name__ == "__main__":
    main()
