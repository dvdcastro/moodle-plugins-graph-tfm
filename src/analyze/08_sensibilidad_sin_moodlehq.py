#!/usr/bin/env python3
"""
Fase 8 (exploratoria, NO forma parte de la numeracion 0-7 del plan original) -
Analisis de sensibilidad: pregunta de David Castro (14/09/2026) sobre que tan
sensibles son los rankings de centralidad de Fase 3 al mantenedor mas grande
del grafo, "Moodle HQ" (Maintainer.user_id='4380', 13 plugins mantenidos
directamente, degree_maint=8.0, betweenness_maint=437.0, pagerank_maint=1.49).
CORRECCION 2026-09-14 (revision de agentes): la version anterior de este
docstring afirmaba erroneamente que estos eran "los tres valores mas altos
de la Fase 3 para Maintainer" -- FALSO, verificado contra los 1.414 nodos
Maintainer: Moodle HQ es rank 47/1.414 en pagerank_maint (Catalyst IT es
#1 con 8.94), rank 118/1.414 en degree_maint (Catalyst IT #1 con 106.0), y
rank 5/1.414 en betweenness_maint (Catalyst IT #1 con 1043.3, Tim Hunt 798.9,
Sara Arjona 571.5). El dato real es mas interesante que el erroneo: HQ ocupa
un rol de "puente" estructural (rank 5 en betweenness) desproporcionado
respecto a su conectividad bruta (rank 118 en degree) -- gatekeeper, no hub.
El resultado del analisis de sensibilidad en si (rho>0.98, efecto local pero
no global) sigue siendo valido; la correccion es de premisa/framing, no de
metodo.

============================================================================
QUE ES ESTO Y QUE NO ES -- LEER ANTES DE CITAR CUALQUIER NUMERO:
Esto es un analisis de sensibilidad EXPLORATORIO, no una fase mas del pipeline
canonico. NO modifica ninguna propiedad ya escrita en Neo4j por 01_centrality.py
(Fase 3), 02_communities.py (Fase 4), 03_risk.py (Fase 5) ni 07_attack_simulation.py
(Fase 7) -- ese fue un requisito explicito del encargo. Todos los calculos de
este script corren en modo STREAM (nunca WRITE/MUTATE sobre propiedades de
Plugin/Maintainer existentes) contra proyecciones GDS nuevas, de solo lectura,
que se dropean antes de salir. Las cifras "antes" (baseline) de este script SI
son las propiedades canonicas de Fase 3 (pagerank_soc, degree_soc,
pagerank_maint, degree_maint) leidas tal cual, sin recalcular -- no hay razon
para recalcular lo que ya existe y es correcto.
NO reemplaza las metricas canonicas de la memoria. Es una vista alternativa
para responder una pregunta puntual: "si Moodle HQ no existiera como
mantenedor, ?cambiaria mucho la foto?". El resultado se integra al documento
(si aplica) en una decision aparte, no aqui.
============================================================================

QUE SIGNIFICA "EXCLUIR A MOODLE HQ" EN CADA PROYECCION (importante, no es lo
mismo en las dos):

  G_maint_excl_hq (Maintainer-Maintainer, CO_MAINTAINS): se remueve el NODO
    Maintainer{user_id:'4380'} y, por definicion de remover un nodo, las 6
    aristas CO_MAINTAINS que lo tocaban desaparecen. Las aristas CO_MAINTAINS
    ENTRE OTROS DOS mantenedores no se recalculan -- su peso (plugins
    compartidos entre esos dos, sin contar a HQ) no depende de si HQ existe o
    no, asi que no hay nada que ajustar ahi.

  G_soc_excl_hq (Plugin-Plugin, DEPENDS_ON + CO_MAINTAINED): DEPENDS_ON queda
    IDENTICO (una dependencia de codigo entre dos plugins no tiene nada que
    ver con quien los mantiene). CO_MAINTAINED SI se recalcula, no solo se
    filtra: cada arista CO_MAINTAINED ya trae en Neo4j la lista
    r.shared_maintainers (Fase 2, 10_derive_edges.py) y r.weight = len(shared_maintainers).
    Aqui se recalcula shared_excl = shared_maintainers - {'Moodle HQ'} por
    arista; si shared_excl queda vacio (Moodle HQ era el UNICO mantenedor en
    comun de ese par de plugins) la arista desaparece por completo de la
    proyeccion; si no, la arista sobrevive con weight = len(shared_excl) (un
    mantenedor compartido menos). Esto es lo que el encargo pedia
    explicitamente ("cualquier CO_MAINTAINED que dependiera exclusivamente de
    mantenedores compartidos con el"), no una simplificacion.

  Mecanismo tecnico: GDS 2.13.12 no tiene ya `gds.graph.project.cypher` (Cypher
  projection classica, removida) -- se usa la forma vigente, "Cypher
  Aggregation" (`gds.graph.project(...)` como funcion agregadora dentro de un
  WITH, no como procedimiento CALL), verificada en vivo contra esta version
  antes de escribir el resto del script (ver PROJECT_G_SOC_EXCL_HQ /
  PROJECT_G_MAINT_EXCL_HQ abajo). Se integra con `projected_graph` de
  _gds_utils.py igual que el resto de src/analyze/ (mismo drop-en-finally),
  pasando el nombre del grafo como parametro `$name` de la query.

LIMITACION DE COBERTURA DE NODOS AISLADOS (declarada explicitamente, no
escondida): a diferencia de la proyeccion basada en config de 01_centrality.py
(`gds.graph.project($name, 'Plugin', {...})`, que proyecta TODOS los nodos con
la etiqueta 'Plugin' incluidos los aislados), la Cypher Aggregation usada aqui
SOLO incluye nodos que son extremo de al menos una arista sobreviviente. Un
plugin que en G_soc SOLO tenia una arista CO_MAINTAINED (y esa arista
dependia exclusivamente de Moodle HQ) queda fuera de G_soc_excl_hq por
completo, no como nodo aislado con pagerank=baseline. Por eso el Spearman se
reporta sobre DOS conjuntos, igual que la convencion ya usada en
01_centrality.py: (a) todos los nodos presentes en ambos lados (antes y
despues) y (b) restringido a los que ademas tenian grado>0 en el G_soc/G_maint
ORIGINAL -- (b) es la cifra que importa; (a) esta inflada por nodos que ya
eran triviales.

Escribe SOLO en data/processed/ (CSV), nunca en Neo4j:
  sensibilidad_sin_moodlehq_top20_pagerank_soc.csv
  sensibilidad_sin_moodlehq_top20_pagerank_maint.csv
  sensibilidad_sin_moodlehq_rank_movers_soc.csv
  sensibilidad_sin_moodlehq_rank_movers_maint.csv
  sensibilidad_sin_moodlehq_comaintenance_hq.csv
  sensibilidad_sin_moodlehq_comunidad220.csv
  sensibilidad_sin_moodlehq_resumen.csv

Uso: python3 08_sensibilidad_sin_moodlehq.py
"""
import os
import sys
from pathlib import Path

import pandas as pd
from neo4j import GraphDatabase
from scipy.stats import spearmanr

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _gds_utils import ROOT, load_env, projected_graph  # noqa: E402

load_env()

URI = os.environ["NEO4J_URI"]
AUTH = (os.environ["NEO4J_USER"], os.environ["NEO4J_PASSWORD"])
PROCESSED = ROOT / "data" / "processed"

HQ_USER_ID = "4380"
HQ_NAME = "Moodle HQ"

# Otras entidades afiliadas a Moodle (nota aparte al final, NO el analisis
# principal -- David pidio enfocarse en el nodo "Moodle HQ" primero).
OTHER_MOODLE_AFFILIATED_NAMES = [
    "Moodle an Hochschulen e.V.", "Open LMS Development", "Moodle Workplace plugins",
    "Moodle Partner lern.link", "Moodle Association Japan", "Moodle RUB",
]

# ============ Cypher Aggregation (forma vigente en GDS 2.13.12; gds.graph.project.cypher
# fue removida en versiones anteriores de GDS) para las dos proyecciones "excl HQ" ============

# NOTA: `projected_graph` (_gds_utils.py) llama a `session.run(project_cypher, name=name)`
# -- solo pasa el parametro `$name`. HQ_NAME/HQ_USER_ID son constantes del modulo (no
# input de usuario), asi que se embeben con .format() antes de pasar la query a
# projected_graph, en vez de extender la firma compartida de _gds_utils.py solo para
# este script exploratorio.
PROJECT_G_SOC_EXCL_HQ = """
CALL () {{
  MATCH (a:Plugin)-[:DEPENDS_ON]->(b:Plugin)
  RETURN a AS n, b AS m, 'DEPENDS_ON' AS type, 1.0 AS weight
  UNION ALL
  MATCH (a:Plugin)-[r:CO_MAINTAINED]-(b:Plugin)
  WHERE elementId(a) < elementId(b)
  WITH a, b, [x IN r.shared_maintainers WHERE x <> '{hq_name}'] AS shared_excl
  WHERE size(shared_excl) > 0
  RETURN a AS n, b AS m, 'CO_MAINTAINED' AS type, toFloat(size(shared_excl)) AS weight
}}
WITH n, m, type, weight
WITH gds.graph.project($name, n, m,
       {{ relationshipType: type, relationshipProperties: {{ weight: weight }} }},
       {{ undirectedRelationshipTypes: ['*'] }}
     ) AS g
RETURN g.graphName AS name, g.nodeCount AS nodeCount, g.relationshipCount AS relCount
""".format(hq_name=HQ_NAME)

PROJECT_G_MAINT_EXCL_HQ = """
MATCH (a:Maintainer)-[r:CO_MAINTAINS]-(b:Maintainer)
WHERE a.user_id <> '{hq_user_id}' AND b.user_id <> '{hq_user_id}' AND elementId(a) < elementId(b)
WITH a AS n, b AS m, toFloat(r.weight) AS weight
WITH gds.graph.project($name, n, m,
       {{ relationshipProperties: {{ weight: weight }} }},
       {{ undirectedRelationshipTypes: ['*'] }}
     ) AS g
RETURN g.graphName AS name, g.nodeCount AS nodeCount, g.relationshipCount AS relCount
""".format(hq_user_id=HQ_USER_ID)


def spearman_report(before_map, after_map, degree_before_map, label):
    """Replica el patron de reporte de 01_centrality.py: rho sobre TODOS los
    nodos comunes a ambos lados, y por separado restringido a los que tenian
    grado>0 en el grafo ORIGINAL (los aislados inflan el rho sin decir nada
    interesante -- mismo razonamiento documentado alli)."""
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
        "n_nodos_que_desaparecen_al_excluir_hq": len(set(before_map) - set(after_map)),
    }


def rank_movers(before_map, after_map, top_n, label_id_field, extra_lookup, out_path):
    """Rankings antes/despues (desc por valor) sobre el conjunto de nodos
    presentes en AMBOS lados; exporta los top_n con mayor |delta de rango|."""
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
        # ============ 0. Confirmacion del nodo Moodle HQ y co-mantenencia de sus 13 plugins ============
        hq = session.run(
            "MATCH (m:Maintainer {user_id: $uid}) RETURN m.display_name AS name, m.n_plugins AS n_plugins, "
            "m.degree_maint AS degree_maint, m.betweenness_maint AS betweenness_maint, "
            "m.pagerank_maint AS pagerank_maint",
            uid=HQ_USER_ID,
        ).single()
        assert hq["name"] == HQ_NAME, f"esperaba {HQ_NAME}, encontre {hq['name']}"
        print(f"[Moodle HQ] user_id={HQ_USER_ID}, n_plugins={hq['n_plugins']}, "
              f"degree_maint={hq['degree_maint']}, betweenness_maint={hq['betweenness_maint']}, "
              f"pagerank_maint={hq['pagerank_maint']:.4f}")

        comaint_rows = session.run(
            """
            MATCH (m:Maintainer {user_id: $uid})-[:MAINTAINS]->(p:Plugin)
            OPTIONAL MATCH (p)<-[:MAINTAINS]-(other:Maintainer) WHERE other.user_id <> $uid
            WITH p, collect(DISTINCT other.display_name) AS otros
            RETURN p.component AS component, p.name AS name, p.installations AS installations,
                   size(otros) AS n_otros_mantenedores, otros
            ORDER BY component
            """,
            uid=HQ_USER_ID,
        ).data()
        comaint_df = pd.DataFrame(comaint_rows)
        comaint_df["quedaria_sin_mantenedor"] = comaint_df["n_otros_mantenedores"] == 0
        comaint_df.to_csv(PROCESSED / "sensibilidad_sin_moodlehq_comaintenance_hq.csv", index=False)
        n_orphan = int(comaint_df["quedaria_sin_mantenedor"].sum())
        n_total_hq = len(comaint_df)
        print(f"[co-mantenencia] {n_orphan}/{n_total_hq} plugins de Moodle HQ quedarian SIN NINGUN "
              f"mantenedor si se excluyera HQ; {n_total_hq - n_orphan} tienen al menos otro mantenedor "
              f"-> sensibilidad_sin_moodlehq_comaintenance_hq.csv")

        # ============ 1. Baseline (Fase 3, YA ESCRITO -- se lee, no se recalcula) ============
        plugin_baseline = {
            r["component"]: r for r in session.run(
                "MATCH (p:Plugin) WHERE p.in_directory <> false "
                "RETURN p.component AS component, p.name AS name, p.installations AS installations, "
                "p.pagerank_soc AS pagerank_soc, p.degree_soc AS degree_soc"
            ).data()
        }
        maint_baseline = {
            r["user_id"]: r for r in session.run(
                "MATCH (m:Maintainer) RETURN m.user_id AS user_id, m.display_name AS display_name, "
                "m.n_plugins AS n_plugins, m.pagerank_maint AS pagerank_maint, m.degree_maint AS degree_maint"
            ).data()
        }
        print(f"[baseline] {len(plugin_baseline)} Plugin (in_directory<>false) con pagerank_soc/degree_soc, "
              f"{len(maint_baseline)} Maintainer con pagerank_maint/degree_maint (Fase 3, leido tal cual)")

        # ============ 2. G_soc_excl_hq: proyeccion nueva, solo lectura (stream, nunca write) ============
        with projected_graph(session, "g_soc_excl_hq", PROJECT_G_SOC_EXCL_HQ):
            gcounts = session.run(
                "CALL gds.graph.list() YIELD graphName, nodeCount, relationshipCount "
                "WHERE graphName = 'g_soc_excl_hq' RETURN nodeCount, relationshipCount"
            ).single()
            print(f"[G_soc_excl_hq] proyeccion: {gcounts['nodeCount']} nodos, "
                  f"{gcounts['relationshipCount']} aristas (dirigidas internamente; recordar que son "
                  f"UNDIRECTED, cada arista logica cuenta 2 veces aqui)")

            pr_soc_excl_raw = {
                r["component"]: r["score"] for r in session.run(
                    "CALL gds.pageRank.stream('g_soc_excl_hq', {relationshipWeightProperty: 'weight'}) "
                    "YIELD nodeId, score "
                    "RETURN gds.util.asNode(nodeId).component AS component, score"
                ).data()
            }
            deg_soc_excl_raw = {
                r["component"]: r["score"] for r in session.run(
                    "CALL gds.degree.stream('g_soc_excl_hq', {relationshipWeightProperty: 'weight'}) "
                    "YIELD nodeId, score "
                    "RETURN gds.util.asNode(nodeId).component AS component, score"
                ).data()
            }
            # IMPORTANTE: pr_soc_excl_raw/deg_soc_excl_raw incluyen TODOS los nodos de la
            # proyeccion, incluidos los ~75 nodos "in_directory=false" (stubs creados solo como
            # destino de DEPENDS_ON -- mod_assign, mod_lti, etc., ver Pregunta 1 del encargo de
            # David sobre plugins de core). export_top20() de 01_centrality.py EXCLUYE esos stubs
            # del top-20 canonico (`AND n.in_directory <> false`) -- si no se aplica el mismo
            # filtro aqui del lado "despues", la comparacion top-20 antes/despues queda sesgada
            # (un stub como mod_assign "aparece" en el top-20 de despues solo porque nunca estuvo
            # en el top-20 de antes, que SI lo excluia por diseno -- no es un cambio real). Se
            # restringe aqui a los mismos componentes de plugin_baseline (in_directory<>false).
            pr_soc_excl = {c: v for c, v in pr_soc_excl_raw.items() if c in plugin_baseline}
            deg_soc_excl = {c: v for c, v in deg_soc_excl_raw.items() if c in plugin_baseline}
            print(f"[G_soc_excl_hq] {len(pr_soc_excl_raw)} nodos en la proyeccion (incluye stubs "
                  f"in_directory=false); {len(pr_soc_excl)} tras restringir a plugins reales del "
                  f"directorio (in_directory<>false), igual que el top-20 canonico de Fase 3")
            # ---- Louvain sobre G_soc_excl_hq, opcional ("si el tiempo alcanza") ----
            louvain_stats = session.run(
                "CALL gds.louvain.stats('g_soc_excl_hq', {relationshipWeightProperty: 'weight'}) "
                "YIELD communityCount, modularity RETURN communityCount, modularity"
            ).single()
            louvain_membership = {
                r["component"]: r["comm"] for r in session.run(
                    "CALL gds.louvain.stream('g_soc_excl_hq', {relationshipWeightProperty: 'weight'}) "
                    "YIELD nodeId, communityId "
                    "RETURN gds.util.asNode(nodeId).component AS component, communityId AS comm"
                ).data()
            }
        print(f"[G_soc_excl_hq] Louvain: {louvain_stats['communityCount']} comunidades, "
              f"modularidad={louvain_stats['modularity']:.4f}")

        # ============ 3. G_maint_excl_hq: proyeccion nueva, solo lectura ============
        with projected_graph(session, "g_maint_excl_hq", PROJECT_G_MAINT_EXCL_HQ):
            gcounts_m = session.run(
                "CALL gds.graph.list() YIELD graphName, nodeCount, relationshipCount "
                "WHERE graphName = 'g_maint_excl_hq' RETURN nodeCount, relationshipCount"
            ).single()
            print(f"[G_maint_excl_hq] proyeccion: {gcounts_m['nodeCount']} nodos (de {len(maint_baseline)} "
                  f"mantenedores totales, HQ excluido), {gcounts_m['relationshipCount']} aristas "
                  f"(UNDIRECTED, cuentan 2x)")
            pr_maint_excl = {
                r["user_id"]: r["score"] for r in session.run(
                    "CALL gds.pageRank.stream('g_maint_excl_hq', {relationshipWeightProperty: 'weight'}) "
                    "YIELD nodeId, score "
                    "RETURN gds.util.asNode(nodeId).user_id AS user_id, score"
                ).data()
            }
            deg_maint_excl = {
                r["user_id"]: r["score"] for r in session.run(
                    "CALL gds.degree.stream('g_maint_excl_hq', {relationshipWeightProperty: 'weight'}) "
                    "YIELD nodeId, score "
                    "RETURN gds.util.asNode(nodeId).user_id AS user_id, score"
                ).data()
            }
        print(f"[G_maint_excl_hq] pagerank/degree calculados para {len(pr_maint_excl)} mantenedores "
              f"(stream, no se escribio nada en Neo4j)")

        # ============ 4. Comunidad(es) Louvain_soc canonicas (Fase 4) de los plugins de HQ -- composicion y destino ============
        hq_comms = session.run(
            "MATCH (m:Maintainer {user_id: $uid})-[:MAINTAINS]->(p:Plugin) "
            "RETURN DISTINCT p.louvain_soc AS comm",
            uid=HQ_USER_ID,
        ).data()
        distinct_comms = [r["comm"] for r in hq_comms if r["comm"] is not None]
        if len(distinct_comms) != 1:
            print(f"[aviso] los 13 plugins de HQ NO estan todos en UNA sola comunidad Louvain_soc "
                  f"(encontradas: {distinct_comms}) -- se reporta la primera, revisar manualmente")
        comm220_id = distinct_comms[0] if distinct_comms else None
        comm220_members = []
        if comm220_id is not None:
            comm220_members = [r["c"] for r in session.run(
                "MATCH (p:Plugin) WHERE p.louvain_soc = $comm RETURN p.component AS c",
                comm=comm220_id,
            ).data()]
        print(f"\n[comunidad Louvain_soc de HQ] id={comm220_id}, {len(comm220_members)} plugins "
              f"(canonico, Fase 4, antes de excluir HQ; los 13 de HQ estan dentro de estos)")
        after_ids = [louvain_membership.get(c) for c in comm220_members]
        after_ids_present = [x for x in after_ids if x is not None]
        n_missing = len(comm220_members) - len(after_ids_present)
        rows_comm220 = []
        for c in comm220_members:
            rows_comm220.append({
                "component": c,
                "louvain_soc_original_comunidad": comm220_id,
                "louvain_soc_excl_hq_comunidad": louvain_membership.get(c),
                "desaparece_de_g_soc_excl_hq": c not in louvain_membership,
            })
        comm220_df = pd.DataFrame(rows_comm220)
        comm220_df.to_csv(PROCESSED / "sensibilidad_sin_moodlehq_comunidad220.csv", index=False)
        if after_ids_present:
            from collections import Counter
            dest_counts = Counter(after_ids_present)
            print(f"[comunidad {comm220_id} tras excluir HQ] {n_missing}/{len(comm220_members)} plugins "
                  f"quedan sin ninguna arista sobreviviente (fuera de la proyeccion); de los "
                  f"{len(after_ids_present)} restantes, se reparten en {len(dest_counts)} comunidad(es) "
                  f"nuevas: {dict(dest_counts.most_common())}")
        print(f"[export] -> sensibilidad_sin_moodlehq_comunidad220.csv")

    driver.close()

    # ============ 5. Rankings top-20 antes/despues + Spearman ============
    pagerank_soc_before = {c: r["pagerank_soc"] for c, r in plugin_baseline.items() if r["pagerank_soc"] is not None}
    degree_soc_before = {c: (r["degree_soc"] or 0) for c, r in plugin_baseline.items()}
    plugin_extra = {c: {"name": r["name"], "installations": r["installations"]} for c, r in plugin_baseline.items()}

    pagerank_maint_before = {u: r["pagerank_maint"] for u, r in maint_baseline.items() if r["pagerank_maint"] is not None}
    degree_maint_before = {u: (r["degree_maint"] or 0) for u, r in maint_baseline.items()}
    maint_extra = {u: {"display_name": r["display_name"], "n_plugins": r["n_plugins"]} for u, r in maint_baseline.items()}

    print("\n" + "=" * 70)
    summary_rows.append(spearman_report(pagerank_soc_before, pr_soc_excl, degree_soc_before,
                                         "pagerank_soc (Plugin, G_soc vs G_soc_excl_hq)"))
    summary_rows.append(spearman_report(degree_soc_before, deg_soc_excl, degree_soc_before,
                                         "degree_soc (Plugin, G_soc vs G_soc_excl_hq)"))
    summary_rows.append(spearman_report(pagerank_maint_before, pr_maint_excl, degree_maint_before,
                                         "pagerank_maint (Maintainer, G_maint vs G_maint_excl_hq)"))
    summary_rows.append(spearman_report(degree_maint_before, deg_maint_excl, degree_maint_before,
                                         "degree_maint (Maintainer, G_maint vs G_maint_excl_hq)"))

    # top-20 antes/despues, lado a lado, por pagerank_soc y pagerank_maint
    def top20_side_by_side(before_map, after_map, extra, id_field, out_path):
        top_before = sorted(before_map, key=lambda c: -before_map[c])[:20]
        top_after = sorted(after_map, key=lambda c: -after_map[c])[:20]
        rows = []
        for rank in range(20):
            b = top_before[rank] if rank < len(top_before) else None
            a = top_after[rank] if rank < len(top_after) else None
            rows.append({
                "rango": rank + 1,
                f"{id_field}_antes": b,
                "valor_antes": before_map.get(b) if b else None,
                f"{id_field}_despues": a,
                "valor_despues": after_map.get(a) if a else None,
                "entra_al_top20_despues_no_estaba_antes": (a is not None and a not in top_before),
            })
        pd.DataFrame(rows).to_csv(out_path, index=False)
        print(f"[top-20] -> {out_path.name}")

    top20_side_by_side(pagerank_soc_before, pr_soc_excl, plugin_extra, "component",
                        PROCESSED / "sensibilidad_sin_moodlehq_top20_pagerank_soc.csv")
    top20_side_by_side(pagerank_maint_before, pr_maint_excl, maint_extra, "user_id",
                        PROCESSED / "sensibilidad_sin_moodlehq_top20_pagerank_maint.csv")

    rank_movers(pagerank_soc_before, pr_soc_excl, 10, "component", plugin_extra,
                PROCESSED / "sensibilidad_sin_moodlehq_rank_movers_soc.csv")
    rank_movers(pagerank_maint_before, pr_maint_excl, 10, "user_id", maint_extra,
                PROCESSED / "sensibilidad_sin_moodlehq_rank_movers_maint.csv")

    # ============ 6. Resumen final ============
    summary_df = pd.DataFrame(summary_rows)
    summary_df["n_plugins_hq_sin_otro_mantenedor"] = n_orphan
    summary_df["n_plugins_hq_total"] = n_total_hq
    summary_df["comunidad_louvain_soc_de_hq"] = comm220_id
    summary_df["tamano_comunidad_original"] = len(comm220_members)
    summary_df["louvain_soc_excl_hq_n_comunidades_global"] = louvain_stats["communityCount"]
    summary_df["louvain_soc_excl_hq_modularidad_global"] = louvain_stats["modularity"]
    summary_df.to_csv(PROCESSED / "sensibilidad_sin_moodlehq_resumen.csv", index=False)
    print(f"\n[export] -> sensibilidad_sin_moodlehq_resumen.csv")
    print("\n[NOTA -- otras entidades afiliadas a Moodle, NO analizadas aqui en detalle]")
    print(f"  Ademas de 'Moodle HQ' existen otros mantenedores con nombres afiliados a Moodle "
          f"({', '.join(OTHER_MOODLE_AFFILIATED_NAMES)}). Este script se enfoca solo en el nodo "
          f"'Moodle HQ' (user_id={HQ_USER_ID}), tal como pidio David explicitamente. Si se quisiera "
          f"extender el mismo analisis a ese conjunto ampliado, el patron de este script (proyeccion "
          f"Cypher Aggregation que excluye una lista de nombres en vez de uno solo) es directamente "
          f"reutilizable, pero NO se corrio -- declarado como trabajo futuro, no como resultado.")


if __name__ == "__main__":
    main()
