#!/usr/bin/env python3
"""
Fase 3 - Metricas de centralidad (objetivo especifico 3: "cada plugin y cada
mantenedor" -- ver docs/plan.md).

Proyecciones GDS:
  G_dep   = DEPENDS_ON dirigido (Plugin -> Plugin), SIN peso (una dependencia
            cuenta como una dependencia; no hay una nocion natural de "cuanto"
            depende un plugin de otro mas alla de si depende o no).
  G_soc   = DEPENDS_ON + CO_MAINTAINED, no dirigido, PONDERADO: DEPENDS_ON usa
            peso constante 1.0 (no tiene propiedad de peso propia), CO_MAINTAINED
            usa su peso real (mantenedores compartidos).
  G_full  = G_soc + SAME_CATEGORY (peso 1/(n_categoria-1)). Solo PageRank y
            degree exactos; betweenness exacta se omite por costo (419.831
            aristas SAME_CATEGORY) y se corre una version APROXIMADA por
            muestreo (gds.betweenness samplingSize, disponible en Community)
            en su lugar -- la Fase 3 anterior la omitia del todo, correccion
            tras revision de agentes 2026-09-10.
  G_maint = CO_MAINTAINS (Maintainer-Maintainer), ponderado por plugins
            compartidos. Sin esto el objetivo especifico 3 ("centralidad de
            cada... mantenedor") quedaba sin cubrir -- hallazgo de la revision
            de agentes 2026-09-10, corregido aqui.

CORRECCION 2026-09-10 (revision de agentes) respecto a la version anterior de
este script: el peso de CO_MAINTAINED/SAME_CATEGORY se proyectaba pero nunca
se pasaba a los algoritmos (relationshipWeightProperty faltante) -- los tres
corrian sin ponderar pese a documentarse como ponderados, y la validacion
networkx tenia el mismo olvido del lado nx (weight=None), asi que "coincidian"
por compartir el error, no por medir lo correcto. Corregido: todos los calculos
sobre G_soc/G_full pasan relationshipWeightProperty='weight' en GDS y
weight="weight" en networkx.

Cada bloque de proyeccion usa el context manager `projected_graph`, que
garantiza el drop en un finally -- una proyeccion GDS huerfana en memoria
(Community edition, memoria limitada) si un algoritmo falla a mitad de camino
era un hallazgo critico de la revision anterior.

Escribe en Neo4j: Plugin.{pagerank_dep, pagerank_soc, pagerank_full,
betweenness_soc, betweenness_full_approx, degree_dep, degree_soc, degree_full},
Maintainer.{pagerank_maint, betweenness_maint, degree_maint}.
Exporta rankings top-20 a data/processed/ para cada metrica.

Valida GDS contra networkx (Spearman) sobre pagerank_dep y betweenness_soc,
reportando el rho sobre TODOS los nodos y, por separado, solo sobre los nodos
con grado>0 -- la mayoria de nodos de G_dep/G_soc son aislados y comparten un
valor base identico en ambos motores, lo que infla el rho global sin ser una
validacion fuerte de la parte estructuralmente interesante del grafo
(hallazgo de la revision de agentes 2026-09-10: el rho global reportado antes
como "1.0000" (redondeo de .4f) era en realidad 0.99999536, no exactamente 1).

Uso: python3 01_centrality.py
"""
import os
import sys
from pathlib import Path

import networkx as nx
import pandas as pd
from neo4j import GraphDatabase
from scipy.stats import spearmanr

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _gds_utils import ROOT, load_env, projected_graph  # noqa: E402

load_env()

URI = os.environ["NEO4J_URI"]
AUTH = (os.environ["NEO4J_USER"], os.environ["NEO4J_PASSWORD"])
PROCESSED = ROOT / "data" / "processed"

BETWEENNESS_FULL_SAMPLE_SIZE = 600  # de ~2963 nodos; RA-Brandes aproximado
BETWEENNESS_FULL_SAMPLE_SEED = 42


def export_top20(session, prop, node_label, id_field, extra_fields, out_name):
    extra = ", ".join(f"n.{f} AS {f}" for f in extra_fields)
    rows = session.run(
        f"""
        MATCH (n:{node_label}) WHERE n.{prop} IS NOT NULL
        {"AND n.in_directory <> false" if node_label == "Plugin" else ""}
        RETURN n.{id_field} AS {id_field}, {extra}, n.{prop} AS score
        ORDER BY score DESC LIMIT 20
        """
    ).data()
    pd.DataFrame(rows).to_csv(PROCESSED / out_name, index=False)
    print(f"[ranking] top 20 por {prop} -> {out_name}")


def main() -> None:
    driver = GraphDatabase.driver(URI, auth=AUTH)
    with driver.session() as session:
        # ---- n_plugins en Maintainer (propiedad clave del plan, no estaba escrita) ----
        session.run(
            """
            MATCH (m:Maintainer)-[:MAINTAINS]->(p:Plugin)
            WITH m, count(p) AS n
            SET m.n_plugins = n
            """
        )

        # ============ G_dep: DEPENDS_ON dirigido, sin peso ============
        with projected_graph(session, "g_dep", """
            CALL gds.graph.project($name, 'Plugin',
              { DEPENDS_ON: { orientation: 'NATURAL' } })
            """):
            session.run(
                "CALL gds.pageRank.write('g_dep', "
                "{ dampingFactor: 0.85, writeProperty: 'pagerank_dep' }) YIELD nodePropertiesWritten"
            )
            session.run(
                "CALL gds.degree.write('g_dep', "
                "{ orientation: 'REVERSE', writeProperty: 'degree_dep' }) YIELD nodePropertiesWritten"
            )
        print("[G_dep] pagerank_dep + degree_dep (in-degree) escritos")

        # ============ G_soc: DEPENDS_ON (peso 1.0) + CO_MAINTAINED (peso real), ponderado ============
        with projected_graph(session, "g_soc", """
            CALL gds.graph.project($name, 'Plugin',
              { DEPENDS_ON:    { orientation: 'UNDIRECTED',
                                  properties: { weight: { property: 'weight', defaultValue: 1.0 } } },
                CO_MAINTAINED: { orientation: 'UNDIRECTED', properties: 'weight' } })
            """):
            session.run(
                "CALL gds.pageRank.write('g_soc', { dampingFactor: 0.85, "
                "relationshipWeightProperty: 'weight', writeProperty: 'pagerank_soc' }) "
                "YIELD nodePropertiesWritten"
            )
            session.run(
                "CALL gds.betweenness.write('g_soc', "
                "{ relationshipWeightProperty: 'weight', writeProperty: 'betweenness_soc' }) "
                "YIELD nodePropertiesWritten"
            )
            session.run(
                "CALL gds.degree.write('g_soc', "
                "{ relationshipWeightProperty: 'weight', writeProperty: 'degree_soc' }) "
                "YIELD nodePropertiesWritten"
            )
        print("[G_soc] pagerank_soc + betweenness_soc + degree_soc escritos (ponderados)")

        # ============ G_full: + SAME_CATEGORY, ponderado. Betweenness aproximada ============
        with projected_graph(session, "g_full", """
            CALL gds.graph.project($name, 'Plugin',
              { DEPENDS_ON:    { orientation: 'UNDIRECTED',
                                  properties: { weight: { property: 'weight', defaultValue: 1.0 } } },
                CO_MAINTAINED: { orientation: 'UNDIRECTED', properties: 'weight' },
                SAME_CATEGORY: { orientation: 'UNDIRECTED', properties: 'weight' } })
            """):
            session.run(
                "CALL gds.pageRank.write('g_full', { dampingFactor: 0.85, "
                "relationshipWeightProperty: 'weight', writeProperty: 'pagerank_full' }) "
                "YIELD nodePropertiesWritten"
            )
            session.run(
                "CALL gds.degree.write('g_full', "
                "{ relationshipWeightProperty: 'weight', writeProperty: 'degree_full' }) "
                "YIELD nodePropertiesWritten"
            )
            session.run(
                "CALL gds.betweenness.write('g_full', "
                "{ samplingSize: $k, samplingSeed: $seed, writeProperty: 'betweenness_full_approx' }) "
                "YIELD nodePropertiesWritten",
                k=BETWEENNESS_FULL_SAMPLE_SIZE, seed=BETWEENNESS_FULL_SAMPLE_SEED,
            )
        print(f"[G_full] pagerank_full + degree_full (exactos) + betweenness_full_approx "
              f"(RA-Brandes muestreado, k={BETWEENNESS_FULL_SAMPLE_SIZE}) escritos")

        # ============ G_maint: CO_MAINTAINS, ponderado ============
        with projected_graph(session, "g_maint", """
            CALL gds.graph.project($name, 'Maintainer',
              { CO_MAINTAINS: { orientation: 'UNDIRECTED', properties: 'weight' } })
            """):
            session.run(
                "CALL gds.pageRank.write('g_maint', { dampingFactor: 0.85, "
                "relationshipWeightProperty: 'weight', writeProperty: 'pagerank_maint' }) "
                "YIELD nodePropertiesWritten"
            )
            session.run(
                "CALL gds.betweenness.write('g_maint', "
                "{ relationshipWeightProperty: 'weight', writeProperty: 'betweenness_maint' }) "
                "YIELD nodePropertiesWritten"
            )
            session.run(
                "CALL gds.degree.write('g_maint', "
                "{ relationshipWeightProperty: 'weight', writeProperty: 'degree_maint' }) "
                "YIELD nodePropertiesWritten"
            )
        print("[G_maint] pagerank_maint + betweenness_maint + degree_maint escritos (mantenedores)")

        # ============ Rankings top-20 ============
        for prop in ["pagerank_dep", "pagerank_soc", "pagerank_full",
                     "betweenness_soc", "betweenness_full_approx",
                     "degree_dep", "degree_soc", "degree_full"]:
            export_top20(session, prop, "Plugin", "component",
                         ["name", "installations"], f"top20_{prop}.csv")
        for prop in ["pagerank_maint", "betweenness_maint", "degree_maint"]:
            export_top20(session, prop, "Maintainer", "user_id",
                         ["display_name", "n_plugins"], f"top20_{prop}.csv")

        # ============ Concentracion de mantenedores ============
        # LIMITACION (senalada en revision de agentes 2026-09-10, no resuelta
        # aqui): el schema de Maintainer no distingue persona de organizacion
        # (ej. cuentas de Moodle HQ / Catalyst IT cuentan igual que un
        # individuo). "Bus factor 1" mezcla ambos casos -- declarar esta
        # limitacion explicitamente en la memoria antes de citar la cifra.
        maint_rows = session.run(
            "MATCH (m:Maintainer) RETURN m.n_plugins AS n ORDER BY n DESC"
        ).data()
        n_values = sorted([r["n"] for r in maint_rows], reverse=True)
        total = sum(n_values)
        n_maint = len(n_values)

        def top_pct_share(pct):
            k = max(1, int(n_maint * pct))
            return sum(n_values[:k]) / total

        asc = sorted(n_values)
        n = len(asc)
        cum = sum(i * v for i, v in enumerate(asc, 1))
        gini = (2 * cum) / (n * total) - (n + 1) / n

        bus_factor_1 = session.run(
            """
            MATCH (p:Plugin)<-[:MAINTAINS]-(m:Maintainer)
            WITH p, count(m) AS n_maint
            WHERE n_maint = 1
            RETURN count(p) AS n
            """
        ).single()["n"]
        total_plugins_con_maintainer = session.run(
            "MATCH (p:Plugin)<-[:MAINTAINS]-(:Maintainer) RETURN count(DISTINCT p) AS n"
        ).single()["n"]

        print("\n--- concentracion de mantenedores ---")
        print(f"  Gini: {gini:.3f}")
        print(f"  top 1% de mantenedores cubre {top_pct_share(0.01)*100:.1f}% de las relaciones MAINTAINS")
        print(f"  top 5% de mantenedores cubre {top_pct_share(0.05)*100:.1f}% de las relaciones MAINTAINS")
        print(f"  top 10% de mantenedores cubre {top_pct_share(0.10)*100:.1f}% de las relaciones MAINTAINS")
        print(f"  bus factor 1 (un solo mantenedor, persona u organizacion sin distinguir): "
              f"{bus_factor_1}/{total_plugins_con_maintainer} plugins "
              f"({bus_factor_1/total_plugins_con_maintainer*100:.1f}%)")

        # ============ Validacion cruzada con networkx ============
        dep_edges = session.run(
            "MATCH (a:Plugin)-[:DEPENDS_ON]->(b:Plugin) RETURN a.component AS a, b.component AS b"
        ).data()
        soc_edges = session.run(
            """
            MATCH (a:Plugin)-[r:DEPENDS_ON|CO_MAINTAINED]-(b:Plugin) WHERE elementId(a) < elementId(b)
            RETURN a.component AS a, b.component AS b, coalesce(r.weight, 1.0) AS weight
            """
        ).data()
        deg_dep = {r["component"]: r["n"] for r in session.run(
            "MATCH (p:Plugin) OPTIONAL MATCH (p)-[:DEPENDS_ON]-(x) "
            "RETURN p.component AS component, count(x) AS n"
        ).data()}
        gds_pagerank_dep = {r["component"]: r["score"] for r in session.run(
            "MATCH (p:Plugin) WHERE p.pagerank_dep IS NOT NULL "
            "RETURN p.component AS component, p.pagerank_dep AS score"
        ).data()}
        gds_betweenness_soc = {r["component"]: r["score"] for r in session.run(
            "MATCH (p:Plugin) WHERE p.betweenness_soc IS NOT NULL "
            "RETURN p.component AS component, p.betweenness_soc AS score"
        ).data()}

    driver.close()

    # ---- networkx: PageRank en G_dep (sin peso, igual que GDS) ----
    G_dep = nx.DiGraph()
    G_dep.add_edges_from([(r["a"], r["b"]) for r in dep_edges])
    for c in gds_pagerank_dep:
        if c not in G_dep:
            G_dep.add_node(c)
    nx_pagerank_dep = nx.pagerank(G_dep, alpha=0.85)

    # ---- networkx: betweenness en G_soc (ponderado, igual que GDS ahora) ----
    G_soc = nx.Graph()
    for r in soc_edges:
        G_soc.add_edge(r["a"], r["b"], weight=r["weight"])
    for c in gds_betweenness_soc:
        if c not in G_soc:
            G_soc.add_node(c)
    nx_betweenness_soc = nx.betweenness_centrality(G_soc, weight="weight", normalized=True)

    def report(gds_vals_map, nx_vals_map, degree_map, label):
        common = [c for c in gds_vals_map if c in nx_vals_map]
        rho, p = spearmanr([gds_vals_map[c] for c in common], [nx_vals_map[c] for c in common])
        nontrivial = [c for c in common if degree_map.get(c, 0) > 0]
        rho_nt, p_nt = spearmanr(
            [gds_vals_map[c] for c in nontrivial], [nx_vals_map[c] for c in nontrivial]
        )
        print(f"\n[validacion] {label}: Spearman rho={rho:.8f} (p={p:.2e}), n={len(common)} nodos "
              f"| restringido a grado>0: rho={rho_nt:.8f}, n={len(nontrivial)} nodos")
        return rho, p, len(common), rho_nt, p_nt, len(nontrivial)

    deg_soc = {c: G_soc.degree(c, weight=None) if c in G_soc else 0 for c in gds_betweenness_soc}
    rho_pr, p_pr, n_pr, rho_pr_nt, p_pr_nt, n_pr_nt = report(
        gds_pagerank_dep, nx_pagerank_dep, deg_dep, "PageRank G_dep"
    )
    rho_b, p_b, n_b, rho_b_nt, p_b_nt, n_b_nt = report(
        gds_betweenness_soc, nx_betweenness_soc, deg_soc, "Betweenness G_soc"
    )

    pd.DataFrame({
        "metric": ["pagerank_dep", "pagerank_dep_grado>0", "betweenness_soc", "betweenness_soc_grado>0"],
        "spearman_rho": [rho_pr, rho_pr_nt, rho_b, rho_b_nt],
        "p_value": [p_pr, p_pr_nt, p_b, p_b_nt],
        "n_compared": [n_pr, n_pr_nt, n_b, n_b_nt],
    }).to_csv(PROCESSED / "centrality_validation_networkx.csv", index=False)


if __name__ == "__main__":
    main()
