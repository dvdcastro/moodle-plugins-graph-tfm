#!/usr/bin/env python3
"""
Fase 4 - Deteccion de comunidades y visualizacion (objetivo especifico 4).

DESVIACION RESPECTO AL PLAN ORIGINAL, verificada empiricamente antes de escribir
el resto del script (no asumida de la literatura general de Louvain, que si suele
ser estocastico por orden de visita aleatorio de nodos): GDS 2.13.12 NO expone un
parametro randomSeed para gds.louvain.{stats,stream,write} (falla con
"Unexpected configuration key: randomSeed"). Verificado tambien contra la via
alternativa de no-determinismo que la propia documentacion de GDS advierte
(condiciones de carrera bajo ejecucion concurrente, no solo ausencia de semilla
-- senalado por la revision de agentes 2026-09-10, que noto que la primera
verificacion solo habia usado la concurrencia por defecto): a `concurrency: 1`
la modularidad es bit-a-bit identica en corridas repetidas; a `concurrency: 4`
(el maximo permitido por la licencia Community, `concurrency: 8` fallo con
"unlicensed GDS and cannot exceed concurrency=4") aparece una diferencia real
pero minuscula (10mo digito significativo: 0.9274898191630715 vs
0.9274894856705925) que NO cambia communityCount ni ninguna conclusion
reportada aqui. Conclusion correcta, mas acotada que la primera version de
este docstring: **determinista bit-a-bit a concurrency=1; a concurrencia mayor
hay una variacion de punto flotante sin efecto practico en los resultados**,
no "sin ningun tipo de no-determinismo". El plan original decia "Louvain no es
determinista, 10 ejecuciones con semillas distintas" -- correcto para la
implementacion de referencia de Louvain en general, pero no aplicable tal
cual a esta version de GDS. Por eso:
  - GDS corre UNA sola vez por proyeccion (no tiene sentido repetir un calculo
    determinista 10 veces).
  - El analisis de estabilidad (10 corridas, modularidad media+-desviacion, NMI/ARI
    entre corridas) se hace con networkx/python-louvain, que SI es estocastico
    (parametro random_state real) -- ahi la pregunta original del plan si aplica.

Proyecciones:
  G_soc  = DEPENDS_ON (peso 1.0) + CO_MAINTAINED (peso real), no dirigido.
  G_full = G_soc + SAME_CATEGORY (peso 1/(n_categoria-1)).

Contraste central de esta fase (linea del plan: "el corazon del capitulo de
resultados"): NMI(Louvain, Category).
  - NMI(Louvain_full, Category) es poco informativo por diseno: SAME_CATEGORY ES
    la relacion "misma categoria", asi que una alta correlacion en G_full puede
    ser circular (la arista ya codifica la respuesta que se esta preguntando).
  - NMI(Louvain_soc, Category) SI dice algo: G_soc no tiene ninguna arista basada
    en categoria (solo DEPENDS_ON y CO_MAINTAINED). Si aun asi correlaciona con
    Category, es evidencia de que la categoria del directorio predice
    colaboracion/dependencia real, no solo taxonomia.

Contraste adicional (plan): Louvain GDS vs. Louvain networkx sobre el mismo G_soc,
via NMI -- misma logica de doble motor que el resto del proyecto.

Caracterizacion de las top 15 comunidades de G_soc (la particion con significado
real segun el analisis de arriba): tamano, categoria dominante, instalaciones
agregadas, % "stale" (>3 anios sin release, mismo umbral que usara la Fase 5).

Visualizacion: GraphML (networkx, sin APOC) para Gephi si esta disponible, y HTML
interactivo con pyvis (color = top-15 comunidades, tamano = pagerank_soc de Fase 3).

Uso: python3 02_communities.py
"""
import sys
from itertools import combinations
from pathlib import Path

import community as community_louvain  # python-louvain
import networkx as nx
import numpy as np
import pandas as pd
from neo4j import GraphDatabase
from pyvis.network import Network
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _gds_utils import ROOT, STALE_CUTOFF_UNIX, load_env, projected_graph  # noqa: E402

load_env()

import os  # noqa: E402

URI = os.environ["NEO4J_URI"]
AUTH = (os.environ["NEO4J_USER"], os.environ["NEO4J_PASSWORD"])
PROCESSED = ROOT / "data" / "processed"
FIGURES = ROOT / "figures"
FIGURES.mkdir(parents=True, exist_ok=True)

NX_STABILITY_RUNS = 10
# STALE_CUTOFF_UNIX ahora vive en _gds_utils.py, compartido con Fase 5 (03_risk.py) --
# ver docstring de _gds_utils.py.


def louvain_gds(session, graph_name, suffix):
    """Corre Louvain una vez y escribe Plugin.louvain_{suffix}. `modularity` se
    lee del propio YIELD de `.write` -- la version anterior de esta funcion
    hacia una llamada aparte a `.stats` solo para obtener `modularity`,
    recalculando Louvain una segunda vez sobre el mismo grafo (desperdicio de
    computo real en g_full, que tiene aristas SAME_CATEGORY densas; hallazgo
    de la revision de agentes 2026-09-10)."""
    prop = f"louvain_{suffix}"
    write_result = session.run(
        "CALL gds.louvain.write($graph, {relationshipWeightProperty: 'weight', writeProperty: $prop}) "
        "YIELD communityCount, modularity RETURN communityCount, modularity",
        graph=graph_name, prop=prop,
    ).single()
    rows = session.run(
        f"MATCH (p:Plugin) WHERE p.{prop} IS NOT NULL RETURN p.component AS component, p.{prop} AS comm"
    ).data()
    return {r["component"]: r["comm"] for r in rows}, write_result["modularity"]


def nx_stability(G, n_runs):
    partitions, modularities = [], []
    for seed in range(n_runs):
        part = community_louvain.best_partition(G, weight="weight", random_state=seed)
        partitions.append(part)
        modularities.append(community_louvain.modularity(part, G, weight="weight"))
    nmis, aris = [], []
    for p1, p2 in combinations(partitions, 2):
        common = sorted(set(p1) & set(p2))
        nmis.append(normalized_mutual_info_score([p1[c] for c in common], [p2[c] for c in common]))
        aris.append(adjusted_rand_score([p1[c] for c in common], [p2[c] for c in common]))
    return partitions, modularities, nmis, aris


def main() -> None:
    driver = GraphDatabase.driver(URI, auth=AUTH)
    with driver.session() as session:
        # ============ Louvain GDS: una sola corrida por proyeccion (determinista, ver docstring) ============
        with projected_graph(session, "g_soc", """
            CALL gds.graph.project($name, 'Plugin',
              { DEPENDS_ON:    { orientation: 'UNDIRECTED',
                                  properties: { weight: { property: 'weight', defaultValue: 1.0 } } },
                CO_MAINTAINED: { orientation: 'UNDIRECTED', properties: 'weight' } })
            """):
            soc_final, mod_soc = louvain_gds(session, "g_soc", "soc")
        print(f"[G_soc, GDS] modularidad={mod_soc:.4f}, {len(set(soc_final.values()))} comunidades, "
              f"louvain_soc escrito")

        with projected_graph(session, "g_full", """
            CALL gds.graph.project($name, 'Plugin',
              { DEPENDS_ON:    { orientation: 'UNDIRECTED',
                                  properties: { weight: { property: 'weight', defaultValue: 1.0 } } },
                CO_MAINTAINED: { orientation: 'UNDIRECTED', properties: 'weight' },
                SAME_CATEGORY: { orientation: 'UNDIRECTED', properties: 'weight' } })
            """):
            full_final, mod_full = louvain_gds(session, "g_full", "full")
        print(f"[G_full, GDS] modularidad={mod_full:.4f}, {len(set(full_final.values()))} comunidades, "
              f"louvain_full escrito")

        # ============ Categoria como particion trivial ============
        cat_rows = session.run(
            "MATCH (p:Plugin) WHERE p.in_directory <> false RETURN p.component AS c, p.plugin_type AS cat"
        ).data()
        category = {r["c"]: r["cat"] for r in cat_rows}
        # degree_soc (escrito en Fase 3) para poder excluir nodos aislados de G_soc del NMI --
        # hallazgo de la revision de agentes 2026-09-10: 523/853 comunidades de G_soc son
        # singletons (nodo sin ninguna arista DEPENDS_ON/CO_MAINTAINED), que por definicion
        # tienen pureza de categoria del 100% e inflan el NMI global sin decir nada sobre
        # colaboracion real. Se reportan ambas cifras, no solo la global.
        degree_soc_map = {r["c"]: r["d"] for r in session.run(
            "MATCH (p:Plugin) WHERE p.in_directory <> false RETURN p.component AS c, p.degree_soc AS d"
        ).data()}

        def nmi_vs_category(partition, label):
            common = sorted(set(partition) & set(category))
            nmi = normalized_mutual_info_score([partition[c] for c in common], [category[c] for c in common])
            non_isolated = [c for c in common if (degree_soc_map.get(c) or 0) > 0]
            nmi_ni = normalized_mutual_info_score(
                [partition[c] for c in non_isolated], [category[c] for c in non_isolated]
            )
            print(f"[NMI vs. Category] {label}: {nmi:.4f} (n={len(common)}) | "
                  f"excluyendo nodos aislados de G_soc: {nmi_ni:.4f} (n={len(non_isolated)})")
            return nmi, nmi_ni

        nmi_soc_cat, nmi_soc_cat_ni = nmi_vs_category(soc_final, "Louvain(G_soc, GDS) vs. Category")
        nmi_full_cat, nmi_full_cat_ni = nmi_vs_category(full_final, "Louvain(G_full, GDS) vs. Category")

        # ============ Distribucion de tamanos de comunidad en G_soc (523/853 son singletons -- ============
        # ============ la hipotesis inicial de "nodos fuera de directorio" era incorrecta,     ============
        # ============ ninguno de los 75 nodos in_directory=false esta aislado en G_soc)        ============
        size_dist = pd.Series(list(soc_final.values())).value_counts().value_counts().sort_index()
        size_dist_df = pd.DataFrame({"tamano_comunidad": size_dist.index, "n_comunidades": size_dist.values})
        size_dist_df.to_csv(PROCESSED / "communities_soc_size_distribution.csv", index=False)
        n_singletons = int((pd.Series(list(soc_final.values())).value_counts() == 1).sum())
        print(f"[distribucion G_soc] {len(set(soc_final.values()))} comunidades totales, "
              f"{n_singletons} son singletons ({n_singletons/len(set(soc_final.values()))*100:.1f}%) -> "
              f"communities_soc_size_distribution.csv")

        # ============ Datos para caracterizar comunidades y para el grafo networkx ============
        plugin_rows = session.run(
            """
            MATCH (p:Plugin) WHERE p.in_directory <> false
            RETURN p.component AS component, p.name AS name, p.plugin_type AS category,
                   p.installations AS installations, p.louvain_soc AS louvain_soc,
                   p.pagerank_soc AS pagerank_soc, p.last_release_ts AS last_release_ts,
                   p.degree_soc AS degree_soc
            """
        ).data()
        maint_edges = session.run(
            "MATCH (a:Plugin)-[r:CO_MAINTAINED]-(b:Plugin) WHERE elementId(a) < elementId(b) "
            "RETURN a.component AS a, b.component AS b, r.weight AS weight"
        ).data()
        dep_edges_all = session.run(
            "MATCH (a:Plugin)-[:DEPENDS_ON]->(b:Plugin) RETURN a.component AS a, b.component AS b"
        ).data()

    driver.close()

    # ============ Reconstruye G_soc en networkx (peso: CO_MAINTAINED real + DEPENDS_ON=1.0) ============
    G_nx = nx.Graph()
    for r in maint_edges:
        G_nx.add_edge(r["a"], r["b"], weight=r["weight"])
    for r in dep_edges_all:
        if G_nx.has_edge(r["a"], r["b"]):
            G_nx[r["a"]][r["b"]]["weight"] += 1.0
        else:
            G_nx.add_edge(r["a"], r["b"], weight=1.0)
    for c in soc_final:
        if c not in G_nx:
            G_nx.add_node(c)

    # ============ Estabilidad de Louvain (motor estocastico real: networkx/python-louvain) ============
    nx_partitions, nx_mods, nx_nmis, nx_aris = nx_stability(G_nx, NX_STABILITY_RUNS)
    print(f"\n[estabilidad, networkx/python-louvain, {NX_STABILITY_RUNS} corridas random_state=0..{NX_STABILITY_RUNS-1}] "
          f"modularidad: media={np.mean(nx_mods):.4f} +- {np.std(nx_mods):.4f}")
    print(f"[estabilidad] NMI entre corridas: {np.mean(nx_nmis):.4f} +- {np.std(nx_nmis):.4f} "
          f"| ARI: {np.mean(nx_aris):.4f} +- {np.std(nx_aris):.4f} "
          f"({len(nx_nmis)} pares de {NX_STABILITY_RUNS} corridas)")

    best_nx_idx = int(np.argmax(nx_mods))
    nx_best_partition = nx_partitions[best_nx_idx]
    common_engines = sorted(set(soc_final) & set(nx_best_partition))
    nmi_gds_nx = normalized_mutual_info_score(
        [soc_final[c] for c in common_engines], [nx_best_partition[c] for c in common_engines]
    )
    print(f"\n[contraste motores] Louvain GDS (determinista) vs. mejor de {NX_STABILITY_RUNS} corridas networkx: "
          f"NMI={nmi_gds_nx:.4f} (n={len(common_engines)}); "
          f"modularidad GDS={mod_soc:.4f} vs. networkx (mejor)={nx_mods[best_nx_idx]:.4f}")

    pd.DataFrame([{
        "modularidad_soc_gds": mod_soc, "modularidad_full_gds": mod_full,
        "n_comunidades_soc_gds": len(set(soc_final.values())), "n_comunidades_full_gds": len(set(full_final.values())),
        "nmi_louvain_soc_vs_category": nmi_soc_cat,
        "nmi_louvain_soc_vs_category_sin_singletons": nmi_soc_cat_ni,
        "nmi_louvain_full_vs_category": nmi_full_cat,
        "nmi_louvain_full_vs_category_sin_singletons": nmi_full_cat_ni,
        "n_singletons_soc": n_singletons,
        "pct_singletons_soc": round(n_singletons / len(set(soc_final.values())) * 100, 1),
        "estabilidad_networkx_modularidad_media": np.mean(nx_mods),
        "estabilidad_networkx_modularidad_std": np.std(nx_mods),
        "estabilidad_networkx_nmi_media": np.mean(nx_nmis),
        "estabilidad_networkx_nmi_std": np.std(nx_nmis),
        "estabilidad_networkx_ari_media": np.mean(nx_aris),
        "estabilidad_networkx_ari_std": np.std(nx_aris),
        "nmi_gds_vs_mejor_networkx": nmi_gds_nx,
        "gds_louvain_deterministic": "bit-a-bit a concurrency=1; variacion de punto flotante en "
                                      "el 10mo digito a concurrency=4, sin efecto en communityCount",
        "n_stability_runs_networkx": NX_STABILITY_RUNS,
    }]).to_csv(PROCESSED / "communities_validation.csv", index=False)
    print(f"[export] -> communities_validation.csv")

    # ============ Caracterizacion de las top 15 comunidades (G_soc, GDS) ============
    df = pd.DataFrame(plugin_rows)
    df["last_release_ts"] = pd.to_numeric(df["last_release_ts"], errors="coerce")
    has_release_data = df["last_release_ts"].notna().mean()
    df["stale"] = df["last_release_ts"] < STALE_CUTOFF_UNIX

    top15 = df["louvain_soc"].value_counts().head(15).index.tolist()
    rows_out = []
    for comm in top15:
        sub = df[df["louvain_soc"] == comm]
        rows_out.append({
            "comunidad": int(comm),
            "n_plugins": len(sub),
            "categoria_dominante": sub["category"].mode().iat[0] if not sub["category"].mode().empty else None,
            "pct_categoria_dominante": round(sub["category"].value_counts(normalize=True).iat[0] * 100, 1)
                                       if len(sub) else 0,
            "instalaciones_totales": int(sub["installations"].fillna(0).sum()),
            "pct_stale": round(sub["stale"].mean() * 100, 1) if has_release_data > 0.5 else None,
            "top_plugin_por_pagerank_soc": sub.sort_values("pagerank_soc", ascending=False)["component"].iat[0]
                                            if sub["pagerank_soc"].notna().any() else None,
        })
    top15_df = pd.DataFrame(rows_out)
    top15_df.to_csv(PROCESSED / "communities_top15_soc.csv", index=False)
    print(f"[comunidades] top 15 de G_soc caracterizadas -> communities_top15_soc.csv "
          f"(cobertura de last_release_ts: {has_release_data*100:.1f}%)")

    # ============ Visualizacion ============
    nx.write_graphml(G_nx, FIGURES / "g_soc.graphml")
    print(f"[export] GraphML de G_soc -> figures/g_soc.graphml (abrir en Gephi si esta disponible)")

    pagerank_map = dict(zip(df["component"], df["pagerank_soc"].fillna(0)))
    max_pr = max(pagerank_map.values()) if pagerank_map else 1.0
    net = Network(height="900px", width="100%", notebook=False, cdn_resources="in_line")
    palette = [
        "#4C78A8", "#F58518", "#54A24B", "#E45756", "#72B7B2", "#EECA3B", "#B279A2", "#FF9DA6",
        "#9D755D", "#BAB0AC", "#1F77B4", "#FF7F0E", "#2CA02C", "#D62728", "#9467BD",
    ]
    comm_to_color = {c: palette[i % len(palette)] for i, c in enumerate(top15)}
    comm_of = dict(zip(df["component"], df["louvain_soc"]))
    for c in G_nx.nodes():
        comm = comm_of.get(c)
        color = comm_to_color.get(comm, "#CCCCCC")
        size = 8 + 25 * (pagerank_map.get(c, 0) / max_pr if max_pr else 0)
        net.add_node(c, label=c, color=color, size=size, title=f"comunidad {comm}")
    for u, v, d in G_nx.edges(data=True):
        net.add_edge(u, v, value=d.get("weight", 1.0))
    net.write_html(str(FIGURES / "g_soc_interactive.html"))
    print(f"[export] visualizacion interactiva -> figures/g_soc_interactive.html "
          f"(color = top-15 comunidades, tamano de nodo = pagerank_soc)")


if __name__ == "__main__":
    main()
