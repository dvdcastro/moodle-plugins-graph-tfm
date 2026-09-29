#!/usr/bin/env python3
"""
Fase 8 (exploratoria, fuera de la numeracion 0-7 del plan original -- mismo
estatus que 08_sensibilidad_sin_moodlehq.py) - Segunda pregunta de David
Castro sobre Moodle HQ (14/09/2026), MAS ESPECIFICA que la de
08_sensibilidad_sin_moodlehq.py y NO un duplicado de ese script.

============================================================================
QUE ES ESTO Y EN QUE SE DIFERENCIA DE 08_sensibilidad_sin_moodlehq.py:
08_sensibilidad_sin_moodlehq.py responde "si Moodle HQ no existiera como
mantenedor, como cambian los rankings/modularidad del ECOSISTEMA COMPLETO
(2.888 plugins)" -- una PERTURBACION del grafo completo (se quita un nodo y
se ve como se mueve todo lo demas).

Este script responde una pregunta distinta: "quedandonos SOLO con los
plugins que la comunidad mantiene sin Moodle HQ (una POBLACION restringida,
no una perturbacion), como se ve el panorama de centralidad/comunidades/
riesgo comparado con el panorama publicado (que incluye a Moodle HQ)".
La diferencia importa: aqui los 13 plugins de Moodle HQ SALEN del analisis
por completo (no se preguntan sus rankings, no cuentan en los denominadores),
en vez de quedarse en el grafo con un mantenedor menos.

NO modifica NADA en 08_sensibilidad_sin_moodlehq.py (agente en paralelo,
pregunta distinta, no se toca). NO escribe nada en Neo4j -- todo corre en
modo `stream`/`stats` de GDS contra proyecciones nuevas, de solo lectura,
dropeadas al salir (mismo patron `projected_graph` de _gds_utils.py que usan
01_centrality.py, 02_communities.py y 08_sensibilidad_sin_moodlehq.py).
============================================================================

DEFINICION DE LA POBLACION (verificada en vivo antes de escribir el resto
del script, no asumida): los plugins reales del directorio
(`in_directory <> false`) donde Moodle HQ (`Maintainer{user_id:'4380'}`) NO
aparece como mantenedor -- ni como unico ni como co-mantenedor, se excluyen
del analisis por completo. Verificado en vivo: Moodle HQ mantiene 13 plugins
(los 13 ya confirmados: filter_censor, repository_boxnet, message_jabber,
webservice_xmlrpc, portfolio_boxnet, block_quiz_results, tool_migratehvp2h5p,
mod_moodlenet, tool_moodlenet, enrol_oneroster, tool_dataprivacy, tool_policy,
local_hub), TODOS reales del directorio -> poblacion = 2.888 - 13 = **2.875**,
confirmado por consulta directa (ver ASSERT_POPULATION_SIZE abajo). De estos
13, 6 tienen ademas otro co-mantenedor (ver 08_sensibilidad_sin_moodlehq.py,
seccion "Co-mantenencia") -- no importa aqui: la poblacion los excluye a los
13 completos, tengan o no otro mantenedor, porque la pregunta es "el
subconjunto que Moodle HQ no mantiene", no "el subconjunto que quedaria sin
mantenedor si Moodle HQ se fuera" (esa es la pregunta de 08).

MECANICA DE LAS PROYECCIONES (Cypher Aggregation, GDS 2.13.12 -- ver nota
identica en 08_sensibilidad_sin_moodlehq.py sobre por que no se usa
`gds.graph.project.cypher`, removida): a diferencia de 08 (que RECALCULA el
peso de CO_MAINTAINED al quitar a HQ de `shared_maintainers`), aqui NO hace
falta recalcular ningun peso. Esto es una restriccion de POBLACION (se
excluyen NODOS enteros -- los 13 plugins de HQ), no una perturbacion de
mantenedores: para dos plugins que SI sobreviven en la poblacion, ninguno de
los dos tiene a HQ como mantenedor (por definicion de la poblacion), asi que
`shared_maintainers`/`r.weight` de la arista CO_MAINTAINED entre ellos nunca
pudo haber incluido a HQ -- no cambia. Mismo argumento para SAME_CATEGORY
(su peso no depende de mantenedores en absoluto). Se filtran ambos extremos
de cada arista a la poblacion; las aristas que tocan alguno de los 13
plugins de HQ (hacia CUALQUIER otro nodo, no solo entre ellos) desaparecen
de la proyeccion.

LIMITACION DE COBERTURA DE NODOS AISLADOS (misma que 08_sensibilidad_sin_
moodlehq.py, declarada explicitamente, no escondida): la Cypher Aggregation
SOLO incluye nodos que son extremo de al menos una arista sobreviviente. Un
plugin de la poblacion que en G_dep/G_soc no tenia ninguna arista, o cuya
unica arista iba hacia uno de los 13 plugins de HQ, queda FUERA de la
proyeccion (no como nodo aislado con pagerank=0). Por eso se reporta
`nodeCount` de cada proyeccion junto al tamano de poblacion (2.875), y los
Spearman/top-15 se calculan sobre la interseccion real.

SECCION DE RIESGO -- NO requiere GDS ni proyeccion nueva: `single_maintainer`
depende solo de contar aristas MAINTAINS por plugin (ninguno de los 2.875
plugins de la poblacion tiene a HQ como mantenedor, asi que su conteo de
mantenedores es identico al baseline canonico de Fase 5 -- no cambia por
quitar a HQ del grafo, cambia porque el DENOMINADOR/las FILAS que entran al
promedio son distintas: 2.875 en vez de 2.888). `stale` idem (solo depende de
`last_release_ts`, no de quien mantiene). Se reusa literalmente la logica de
03_risk.py (mismo `STALE_CUTOFF_UNIX` de _gds_utils.py), restringida a la
poblacion. "Fragiles" usa la MISMA definicion que el baseline ya publicado en
docs/decisions.md (930 = single_maintainer=1 Y stale=1) -- NO el ranking de
`risk_score` compuesto de z-scores (ese es un top-30 por impacto potencial,
no un conteo; ver docstring de 03_risk.py), para poder comparar cifra contra
cifra con el 930 ya publicado.

Escribe SOLO en data/processed/ (CSV), nunca en Neo4j:
  poblacion_sin_moodlehq_top15_pagerank_dep.csv
  poblacion_sin_moodlehq_top15_pagerank_soc.csv
  poblacion_sin_moodlehq_rank_movers_dep.csv
  poblacion_sin_moodlehq_rank_movers_soc.csv
  poblacion_sin_moodlehq_riesgo.csv
  poblacion_sin_moodlehq_resumen.csv

Uso: python3 10_poblacion_sin_moodlehq.py
"""
import os
import sys
from pathlib import Path

import pandas as pd
from neo4j import GraphDatabase
from scipy.stats import spearmanr

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _gds_utils import ROOT, STALE_CUTOFF_UNIX, load_env, projected_graph  # noqa: E402

load_env()

URI = os.environ["NEO4J_URI"]
AUTH = (os.environ["NEO4J_USER"], os.environ["NEO4J_PASSWORD"])
PROCESSED = ROOT / "data" / "processed"

HQ_USER_ID = "4380"
HQ_NAME = "Moodle HQ"
EXPECTED_POPULATION_SIZE = 2875
EXPECTED_HQ_PLUGIN_COUNT = 13

# Baseline YA PUBLICADO en la memoria (docs/decisions.md), para comparar -- NO se recalcula.
BASELINE_LOUVAIN_SOC = {"modularidad": 0.9275, "n_comunidades": 853}
BASELINE_LOUVAIN_FULL = {"modularidad": 0.8787, "n_comunidades": 57}
BASELINE_SINGLE_MAINTAINER_PCT = 72.3
BASELINE_STALE_PCT = 43.2
BASELINE_FRAGILES_N = 930

# ============ Predicado de poblacion, embebido via .format() en cada query (HQ_USER_ID es ============
# ============ una constante del modulo, no input de usuario -- mismo criterio que 08).       ============
POP_PRED = "{alias}.in_directory <> false AND NOT EXISTS {{ ({alias})<-[:MAINTAINS]-(:Maintainer {{user_id: '{hq}'}}) }}"


def pop_pred(alias: str) -> str:
    return POP_PRED.format(alias=alias, hq=HQ_USER_ID)


PROJECT_G_DEP_POP = """
CALL () {{
  MATCH (a:Plugin)-[:DEPENDS_ON]->(b:Plugin)
  WHERE {pred_a} AND {pred_b}
  RETURN a AS n, b AS m
}}
WITH n, m
WITH gds.graph.project($name, n, m) AS g
RETURN g.graphName AS name, g.nodeCount AS nodeCount, g.relationshipCount AS relCount
""".format(pred_a=pop_pred("a"), pred_b=pop_pred("b"))

PROJECT_G_SOC_POP = """
CALL () {{
  MATCH (a:Plugin)-[:DEPENDS_ON]->(b:Plugin)
  WHERE {pred_a} AND {pred_b}
  RETURN a AS n, b AS m, 'DEPENDS_ON' AS type, 1.0 AS weight
  UNION ALL
  MATCH (a:Plugin)-[r:CO_MAINTAINED]-(b:Plugin)
  WHERE elementId(a) < elementId(b) AND {pred_a} AND {pred_b}
  RETURN a AS n, b AS m, 'CO_MAINTAINED' AS type, toFloat(r.weight) AS weight
}}
WITH n, m, type, weight
WITH gds.graph.project($name, n, m,
       {{ relationshipType: type, relationshipProperties: {{ weight: weight }} }},
       {{ undirectedRelationshipTypes: ['*'] }}
     ) AS g
RETURN g.graphName AS name, g.nodeCount AS nodeCount, g.relationshipCount AS relCount
""".format(pred_a=pop_pred("a"), pred_b=pop_pred("b"))

PROJECT_G_FULL_POP = """
CALL () {{
  MATCH (a:Plugin)-[:DEPENDS_ON]->(b:Plugin)
  WHERE {pred_a} AND {pred_b}
  RETURN a AS n, b AS m, 'DEPENDS_ON' AS type, 1.0 AS weight
  UNION ALL
  MATCH (a:Plugin)-[r:CO_MAINTAINED]-(b:Plugin)
  WHERE elementId(a) < elementId(b) AND {pred_a} AND {pred_b}
  RETURN a AS n, b AS m, 'CO_MAINTAINED' AS type, toFloat(r.weight) AS weight
  UNION ALL
  MATCH (a:Plugin)-[r:SAME_CATEGORY]-(b:Plugin)
  WHERE elementId(a) < elementId(b) AND {pred_a} AND {pred_b}
  RETURN a AS n, b AS m, 'SAME_CATEGORY' AS type, toFloat(r.weight) AS weight
}}
WITH n, m, type, weight
WITH gds.graph.project($name, n, m,
       {{ relationshipType: type, relationshipProperties: {{ weight: weight }} }},
       {{ undirectedRelationshipTypes: ['*'] }}
     ) AS g
RETURN g.graphName AS name, g.nodeCount AS nodeCount, g.relationshipCount AS relCount
""".format(pred_a=pop_pred("a"), pred_b=pop_pred("b"))


def spearman_report(before_map, after_map, degree_before_map, label):
    """Mismo patron de 01_centrality.py/08_sensibilidad_sin_moodlehq.py: rho sobre
    todos los nodos comunes a ambos lados, y por separado restringido a los que
    tenian grado>0 en el grafo ORIGINAL (los aislados inflan el rho sin decir
    nada interesante)."""
    common = sorted(set(before_map) & set(after_map))
    rho, p = spearmanr([before_map[c] for c in common], [after_map[c] for c in common])
    nontrivial = [c for c in common if (degree_before_map.get(c) or 0) > 0]
    rho_nt, p_nt = spearmanr([before_map[c] for c in nontrivial], [after_map[c] for c in nontrivial])
    print(f"[Spearman] {label}: rho={rho:.4f} (p={p:.2e}), n={len(common)} nodos comunes "
          f"| restringido a grado_original>0: rho={rho_nt:.4f}, n={len(nontrivial)} nodos")
    return {
        "metrica": label,
        "spearman_rho_todos_comunes": rho,
        "p_value_todos_comunes": p,
        "n_todos_comunes": len(common),
        "spearman_rho_grado_original_mayor_0": rho_nt,
        "p_value_grado_original_mayor_0": p_nt,
        "n_grado_original_mayor_0": len(nontrivial),
    }


def top_n_side_by_side(before_map, after_map, extra, id_field, top_n, out_path):
    top_before = sorted(before_map, key=lambda c: -before_map[c])[:top_n]
    top_after = sorted(after_map, key=lambda c: -after_map[c])[:top_n]
    rows = []
    for rank in range(top_n):
        b = top_before[rank] if rank < len(top_before) else None
        a = top_after[rank] if rank < len(top_after) else None
        rows.append({
            "rango": rank + 1,
            f"{id_field}_antes_baseline_global": b,
            "valor_antes": before_map.get(b) if b else None,
            f"{id_field}_despues_poblacion_restringida": a,
            "valor_despues": after_map.get(a) if a else None,
            "entra_al_top_despues_no_estaba_antes": (a is not None and a not in top_before),
        })
    df = pd.DataFrame(rows)
    df.to_csv(out_path, index=False)
    n_iguales = sum(1 for r in rows if r[f"{id_field}_antes_baseline_global"] == r[f"{id_field}_despues_poblacion_restringida"])
    print(f"[top-{top_n}] -> {out_path.name} ({n_iguales}/{top_n} mismo componente en la misma posicion)")
    return df, top_before, top_after


def rank_movers(before_map, after_map, top_n, label_id_field, extra_lookup, out_path):
    common = sorted(set(before_map) & set(after_map))
    order_before = sorted(common, key=lambda c: -before_map[c])
    order_after = sorted(common, key=lambda c: -after_map[c])
    rank_before = {c: i + 1 for i, c in enumerate(order_before)}
    rank_after = {c: i + 1 for i, c in enumerate(order_after)}
    rows = []
    for c in common:
        rows.append({
            label_id_field: c,
            **extra_lookup.get(c, {}),
            "valor_antes": before_map[c],
            "valor_despues": after_map[c],
            "rango_antes": rank_before[c],
            "rango_despues": rank_after[c],
            "delta_rango": rank_before[c] - rank_after[c],
        })
    df = pd.DataFrame(rows).sort_values("delta_rango", key=lambda s: s.abs(), ascending=False)
    df.head(top_n).to_csv(out_path, index=False)
    print(f"[rank movers] top {top_n} -> {out_path.name}")
    return df


def main() -> None:
    driver = GraphDatabase.driver(URI, auth=AUTH)
    summary_rows = []

    with driver.session() as session:
        # ============ 0. Poblacion: verificacion en vivo, no asumida ============
        hq_plugins = session.run(
            "MATCH (p:Plugin)<-[:MAINTAINS]-(:Maintainer {user_id: $uid}) "
            "RETURN p.component AS component ORDER BY component",
            uid=HQ_USER_ID,
        ).data()
        hq_components = [r["component"] for r in hq_plugins]
        assert len(hq_components) == EXPECTED_HQ_PLUGIN_COUNT, (
            f"esperaba {EXPECTED_HQ_PLUGIN_COUNT} plugins mantenidos por Moodle HQ, "
            f"encontre {len(hq_components)}: {hq_components}"
        )
        print(f"[Moodle HQ] mantiene {len(hq_components)} plugins (verificado en vivo): {hq_components}")

        pop_count = session.run(
            f"MATCH (p:Plugin) WHERE {pop_pred('p')} RETURN count(p) AS n"
        ).single()["n"]
        print(f"[poblacion] {pop_count} plugins reales del directorio donde Moodle HQ NO es "
              f"mantenedor (esperado: {EXPECTED_POPULATION_SIZE} = 2.888 - {EXPECTED_HQ_PLUGIN_COUNT})")
        assert pop_count == EXPECTED_POPULATION_SIZE, (
            f"poblacion esperada {EXPECTED_POPULATION_SIZE}, encontre {pop_count} -- revisar antes "
            f"de seguir, algo cambio respecto al encargo"
        )

        # ============ 1. Baseline canonico (Fase 3/4/5, YA ESCRITO -- se lee, no se recalcula) ============
        plugin_baseline = {
            r["component"]: r for r in session.run(
                "MATCH (p:Plugin) WHERE p.in_directory <> false "
                "RETURN p.component AS component, p.name AS name, p.installations AS installations, "
                "p.pagerank_dep AS pagerank_dep, p.degree_dep AS degree_dep, "
                "p.pagerank_soc AS pagerank_soc, p.degree_soc AS degree_soc"
            ).data()
        }
        print(f"[baseline] {len(plugin_baseline)} Plugin (in_directory<>false) con centralidad "
              f"canonica de Fase 3, leida tal cual")

        # ============ 2. G_dep_pop: DEPENDS_ON dirigido, sin peso, restringido a poblacion ============
        with projected_graph(session, "g_dep_pop", PROJECT_G_DEP_POP):
            gcounts = session.run(
                "CALL gds.graph.list() YIELD graphName, nodeCount, relationshipCount "
                "WHERE graphName = 'g_dep_pop' RETURN nodeCount, relationshipCount"
            ).single()
            print(f"[G_dep_pop] proyeccion: {gcounts['nodeCount']}/{pop_count} plugins de la poblacion "
                  f"tienen al menos una arista DEPENDS_ON sobreviviente (dirigida), "
                  f"{gcounts['relationshipCount']} aristas")
            pr_dep_pop = {
                r["component"]: r["score"] for r in session.run(
                    "CALL gds.pageRank.stream('g_dep_pop', {dampingFactor: 0.85}) "
                    "YIELD nodeId, score "
                    "RETURN gds.util.asNode(nodeId).component AS component, score"
                ).data()
            }
            deg_dep_pop = {
                r["component"]: r["score"] for r in session.run(
                    "CALL gds.degree.stream('g_dep_pop', {orientation: 'REVERSE'}) "
                    "YIELD nodeId, score "
                    "RETURN gds.util.asNode(nodeId).component AS component, score"
                ).data()
            }
        print(f"[G_dep_pop] pagerank/degree(in) calculados para {len(pr_dep_pop)} plugins (stream, "
              f"nada escrito en Neo4j)")

        # ============ 3. G_soc_pop: DEPENDS_ON (peso 1.0) + CO_MAINTAINED (peso real), restringido ============
        with projected_graph(session, "g_soc_pop", PROJECT_G_SOC_POP):
            gcounts_soc = session.run(
                "CALL gds.graph.list() YIELD graphName, nodeCount, relationshipCount "
                "WHERE graphName = 'g_soc_pop' RETURN nodeCount, relationshipCount"
            ).single()
            print(f"[G_soc_pop] proyeccion: {gcounts_soc['nodeCount']}/{pop_count} plugins con al menos "
                  f"una arista sobreviviente, {gcounts_soc['relationshipCount']} aristas (UNDIRECTED, "
                  f"cuentan 2x)")
            pr_soc_pop = {
                r["component"]: r["score"] for r in session.run(
                    "CALL gds.pageRank.stream('g_soc_pop', {relationshipWeightProperty: 'weight'}) "
                    "YIELD nodeId, score "
                    "RETURN gds.util.asNode(nodeId).component AS component, score"
                ).data()
            }
            deg_soc_pop = {
                r["component"]: r["score"] for r in session.run(
                    "CALL gds.degree.stream('g_soc_pop', {relationshipWeightProperty: 'weight'}) "
                    "YIELD nodeId, score "
                    "RETURN gds.util.asNode(nodeId).component AS component, score"
                ).data()
            }
            louvain_soc_stats = session.run(
                "CALL gds.louvain.stats('g_soc_pop', {relationshipWeightProperty: 'weight'}) "
                "YIELD communityCount, modularity RETURN communityCount, modularity"
            ).single()
        print(f"[G_soc_pop] pagerank/degree calculados para {len(pr_soc_pop)} plugins")
        print(f"[G_soc_pop] Louvain: {louvain_soc_stats['communityCount']} comunidades, "
              f"modularidad={louvain_soc_stats['modularity']:.4f} (baseline: "
              f"{BASELINE_LOUVAIN_SOC['n_comunidades']} comunidades, "
              f"modularidad={BASELINE_LOUVAIN_SOC['modularidad']:.4f})")

        # ============ 4. G_full_pop: + SAME_CATEGORY, restringido -- solo Louvain (mismo alcance del encargo) ============
        with projected_graph(session, "g_full_pop", PROJECT_G_FULL_POP):
            gcounts_full = session.run(
                "CALL gds.graph.list() YIELD graphName, nodeCount, relationshipCount "
                "WHERE graphName = 'g_full_pop' RETURN nodeCount, relationshipCount"
            ).single()
            print(f"[G_full_pop] proyeccion: {gcounts_full['nodeCount']}/{pop_count} plugins, "
                  f"{gcounts_full['relationshipCount']} aristas (UNDIRECTED, cuentan 2x)")
            louvain_full_stats = session.run(
                "CALL gds.louvain.stats('g_full_pop', {relationshipWeightProperty: 'weight'}) "
                "YIELD communityCount, modularity RETURN communityCount, modularity"
            ).single()
        print(f"[G_full_pop] Louvain: {louvain_full_stats['communityCount']} comunidades, "
              f"modularidad={louvain_full_stats['modularity']:.4f} (baseline: "
              f"{BASELINE_LOUVAIN_FULL['n_comunidades']} comunidades, "
              f"modularidad={BASELINE_LOUVAIN_FULL['modularidad']:.4f})")

        # ============ 5. Riesgo: pura lectura/pandas, restringido a poblacion (mismo criterio de 03_risk.py) ============
        risk_rows = session.run(
            f"MATCH (p:Plugin) WHERE {pop_pred('p')} "
            "RETURN p.component AS component, p.name AS name, p.installations AS installations, "
            "p.last_release_ts AS last_release_ts"
        ).data()
        maint_count = {
            r["c"]: r["n"] for r in session.run(
                f"MATCH (p:Plugin)<-[:MAINTAINS]-(m:Maintainer) WHERE {pop_pred('p')} "
                "RETURN p.component AS c, count(m) AS n"
            ).data()
        }

    driver.close()

    # ============ Riesgo: calculo en pandas (identico a 03_risk.py, restringido a poblacion) ============
    risk_df = pd.DataFrame(risk_rows)
    risk_df["n_maintainers"] = risk_df["component"].map(maint_count).fillna(0).astype(int)
    risk_df["single_maintainer"] = (risk_df["n_maintainers"] == 1).astype(int)
    risk_df["last_release_ts"] = pd.to_numeric(risk_df["last_release_ts"], errors="coerce")
    risk_df["stale"] = (risk_df["last_release_ts"] < STALE_CUTOFF_UNIX).astype(int)
    risk_df["fragil"] = ((risk_df["single_maintainer"] == 1) & (risk_df["stale"] == 1)).astype(int)

    n_con_maintainer = int((risk_df["n_maintainers"] > 0).sum())
    n_single = int(risk_df["single_maintainer"].sum())
    pct_single = n_single / n_con_maintainer * 100
    n_stale = int(risk_df["stale"].sum())
    pct_stale = n_stale / len(risk_df) * 100
    n_fragiles = int(risk_df["fragil"].sum())

    print(f"\n[riesgo, poblacion sin Moodle HQ] single_maintainer: {n_single}/{n_con_maintainer} "
          f"({pct_single:.1f}%, de plugins con >=1 mantenedor; baseline: "
          f"{BASELINE_SINGLE_MAINTAINER_PCT}%) -- {len(risk_df) - n_con_maintainer} plugins con "
          f"0 mantenedores en la poblacion, excluidos de este porcentaje")
    print(f"[riesgo, poblacion sin Moodle HQ] stale: {n_stale}/{len(risk_df)} ({pct_stale:.1f}%, "
          f"baseline: {BASELINE_STALE_PCT}%)")
    print(f"[riesgo, poblacion sin Moodle HQ] fragiles (single_maintainer=1 Y stale=1): {n_fragiles} "
          f"(baseline: {BASELINE_FRAGILES_N})")

    risk_df.to_csv(PROCESSED / "poblacion_sin_moodlehq_riesgo.csv", index=False)
    print(f"[export] -> poblacion_sin_moodlehq_riesgo.csv")

    # ============ Centralidad: baseline restringido a poblacion vs. recalculado sobre la poblacion ============
    pagerank_dep_before = {
        c: r["pagerank_dep"] for c, r in plugin_baseline.items()
        if c not in hq_components and r["pagerank_dep"] is not None
    }
    degree_dep_before = {c: (r["degree_dep"] or 0) for c, r in plugin_baseline.items() if c not in hq_components}
    pagerank_soc_before = {
        c: r["pagerank_soc"] for c, r in plugin_baseline.items()
        if c not in hq_components and r["pagerank_soc"] is not None
    }
    degree_soc_before = {c: (r["degree_soc"] or 0) for c, r in plugin_baseline.items() if c not in hq_components}
    plugin_extra = {c: {"name": r["name"], "installations": r["installations"]}
                     for c, r in plugin_baseline.items()}

    print("\n" + "=" * 70)
    print("[interpretacion] 'antes' = valor canonico de Fase 3 (calculado sobre el ecosistema "
          "COMPLETO, con Moodle HQ dentro), restringido a los 2.875 componentes de la poblacion.")
    print("[interpretacion] 'despues' = recalculado desde cero SOLO sobre la poblacion (grafo "
          "restringido, Moodle HQ y sus 13 plugins no existen en la proyeccion).")
    summary_rows.append(spearman_report(pagerank_dep_before, pr_dep_pop, degree_dep_before,
                                         "pagerank_dep (Plugin, baseline global restringido vs. G_dep_pop)"))
    summary_rows.append(spearman_report(degree_dep_before, deg_dep_pop, degree_dep_before,
                                         "degree_dep (Plugin, baseline global restringido vs. G_dep_pop)"))
    summary_rows.append(spearman_report(pagerank_soc_before, pr_soc_pop, degree_soc_before,
                                         "pagerank_soc (Plugin, baseline global restringido vs. G_soc_pop)"))
    summary_rows.append(spearman_report(degree_soc_before, deg_soc_pop, degree_soc_before,
                                         "degree_soc (Plugin, baseline global restringido vs. G_soc_pop)"))

    _, top15_dep_before, top15_dep_after = top_n_side_by_side(
        pagerank_dep_before, pr_dep_pop, plugin_extra, "component", 15,
        PROCESSED / "poblacion_sin_moodlehq_top15_pagerank_dep.csv"
    )
    _, top15_soc_before, top15_soc_after = top_n_side_by_side(
        pagerank_soc_before, pr_soc_pop, plugin_extra, "component", 15,
        PROCESSED / "poblacion_sin_moodlehq_top15_pagerank_soc.csv"
    )
    print(f"[top-15 pagerank_dep] {sorted(set(top15_dep_before) ^ set(top15_dep_after))} entran/salen "
          f"del top-15 (diferencia simetrica; vacio = mismos 15 componentes en ambos lados)")
    print(f"[top-15 pagerank_soc] {sorted(set(top15_soc_before) ^ set(top15_soc_after))} entran/salen "
          f"del top-15 (diferencia simetrica; vacio = mismos 15 componentes en ambos lados)")

    rank_movers(pagerank_dep_before, pr_dep_pop, 10, "component", plugin_extra,
                PROCESSED / "poblacion_sin_moodlehq_rank_movers_dep.csv")
    rank_movers(pagerank_soc_before, pr_soc_pop, 10, "component", plugin_extra,
                PROCESSED / "poblacion_sin_moodlehq_rank_movers_soc.csv")

    # ============ Resumen final ============
    summary_df = pd.DataFrame(summary_rows)
    summary_df["poblacion_n"] = pop_count
    summary_df["poblacion_esperada"] = EXPECTED_POPULATION_SIZE
    summary_df["hq_plugins_excluidos"] = len(hq_components)
    summary_df["louvain_soc_pop_n_comunidades"] = louvain_soc_stats["communityCount"]
    summary_df["louvain_soc_pop_modularidad"] = louvain_soc_stats["modularity"]
    summary_df["louvain_soc_baseline_n_comunidades"] = BASELINE_LOUVAIN_SOC["n_comunidades"]
    summary_df["louvain_soc_baseline_modularidad"] = BASELINE_LOUVAIN_SOC["modularidad"]
    summary_df["louvain_full_pop_n_comunidades"] = louvain_full_stats["communityCount"]
    summary_df["louvain_full_pop_modularidad"] = louvain_full_stats["modularity"]
    summary_df["louvain_full_baseline_n_comunidades"] = BASELINE_LOUVAIN_FULL["n_comunidades"]
    summary_df["louvain_full_baseline_modularidad"] = BASELINE_LOUVAIN_FULL["modularidad"]
    summary_df["pct_single_maintainer_pop"] = pct_single
    summary_df["pct_single_maintainer_baseline"] = BASELINE_SINGLE_MAINTAINER_PCT
    summary_df["pct_stale_pop"] = pct_stale
    summary_df["pct_stale_baseline"] = BASELINE_STALE_PCT
    summary_df["n_fragiles_pop"] = n_fragiles
    summary_df["n_fragiles_baseline"] = BASELINE_FRAGILES_N
    summary_df.to_csv(PROCESSED / "poblacion_sin_moodlehq_resumen.csv", index=False)
    print(f"\n[export] -> poblacion_sin_moodlehq_resumen.csv")


if __name__ == "__main__":
    main()
