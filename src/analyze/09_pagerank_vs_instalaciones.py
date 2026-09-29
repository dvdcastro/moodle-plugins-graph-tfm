#!/usr/bin/env python3
"""
Fase 8/9 (fuera del plan original) - PageRank estructural vs. instalaciones
reales: donde NO coinciden.

ORIGEN: un consultor externo (sin acceso a herramientas, solo su conocimiento)
recomendo comparar el PageRank estructural (dependencias entre plugins, ya
calculado en 01_centrality.py) contra las instalaciones reales (adopcion),
y senalo como interesante los casos DISCORDANTES: PageRank alto/instalaciones
bajas ("infraestructura invisible", bus factor que nadie percibe porque no es
popular) vs. PageRank bajo/instalaciones altas (hojas populares sin
dependientes). Esa recomendacion citaba papers academicos SIN verificarlos --
NO se repiten esas citas aqui ni se usan como respaldo. Este script es
puramente numerico/empirico sobre los datos propios del proyecto. David
aprobo investigar la pregunta.

QUE HACE:
  1. Correlacion de Spearman entre pagerank_dep/pagerank_soc e installations,
     sobre plugins con AMBOS campos no-nulos, reportada DOS VECES: (a) sobre
     todos esos plugins, y (b) solo sobre los que tienen degree_dep>0 (o
     degree_soc>0, segun la metrica) -- es decir, no aislados en la
     proyeccion correspondiente. Se separan porque ya se establecio en este
     proyecto (01_centrality.py, docstring) que mezclar nodos aislados con
     estructura infla artificialmente estas correlaciones: un nodo aislado
     en G_dep tiene pagerank_dep = valor base identico (1-d)/N para todos,
     así que cualquier variacion de installations entre esos nodos aporta
     "ruido" que Spearman on rank puede leer como señal si se compara contra
     un grupo heterogeneo. Reportar N real en cada celda, no se omite.

  2. Casos discordantes, con criterio explicito por percentiles (documentado
     abajo, no arbitrario sin explicar):
     - "Infraestructura invisible": pagerank_dep en el percentil >= P90 QUE
       ADEMAS tenga degree_dep>0 (i.e. estructuralmente conectado, no un nodo
       aislado con pagerank base alto por casualidad de redondeo) Y
       installations en el percentil <= P40 del conjunto CON degree_dep>0.
       P90/P40 elegidos para que "alto" sea una franja realmente superior
       (top 10%) e "instalaciones bajas" sea una franja generosa (40% inferior,
       no solo el minimo) -- evita que el criterio dependa de un solo umbral
       fragil. Se ordenan por pagerank_dep desc dentro del grupo resultante.
     - "Hojas populares": installations en percentil >= P90 (sobre TODOS los
       plugins con installations no-nulo, no solo los conectados, porque el
       fenomeno que se busca es precisamente instalaciones altas sin
       estructura) Y (degree_dep=0 O pagerank_dep en percentil <= P25 del
       conjunto con degree_dep>0). Se ordenan por installations desc.
     Para cada caso se trae plugin_type y n_maintainers (via MAINTAINS,
     mismo patron de 03_risk.py) para dar contexto, no solo dos numeros.

  3. Verificacion manual: se inspeccionan 2-3 casos llamativos de cada lista
     contra datos crudos (consulta directa a Neo4j: de que depende / quien
     depende del plugin via DEPENDS_ON, n_versions, downloads_90d,
     first_release_ts) para descartar artefactos tipicos ya vistos en este
     proyecto: un degree_dep=1 que es solo una dependencia hacia un framework
     comun, o installations bajas/nulas porque el plugin es muy reciente y no
     porque nadie lo use.

VERIFICACION MANUAL REALIZADA (14/09/2026) -- NINGUN caso de las dos listas se
descarto por completo, pero se encontraron matices importantes que SI cambian
como se debe leer cada lista (documentados aqui en vez de dejarlos implicitos):

  a) "Infraestructura invisible" -- TODOS los 9 casos que superan el umbral
     resultaron ser PARES O TRIOS RECIPROCOS AISLADOS, no nodos centrales de
     una estructura mas grande. Verificado con DEPENDS_ON directo en Neo4j:
     auth_linkedin <-> block_linkedin (2-ciclo, plugin de auth + su bloque
     companero), filter_urlresource <-> local_filterurlresbak (plugin +
     su propio backup helper), assignsubmission_physical <-> local_barcode
     (idem), y block_user_preferences / block_semantic_web / block_case_repository
     (trio mutuamente conectado, con un self-loop DEPENDS_ON en
     block_user_preferences -> block_user_preferences: se confirmo que solo
     hay 2 self-loops DEPENDS_ON en todo el grafo, caso raro pero real, no
     se corrigio aqui por ser un problema de la fase de extraccion, no de
     este script). format_flexpage es el unico caso con un cluster algo mas
     grande (4 plugins de la misma "familia" Flexpage: format+theme+2 blocks),
     tambien desconectado del resto del grafo. CONCLUSION: estos NO son
     dependencias "un framework comun al que aporta media Moodle" (ese
     artefacto especifico que se buscaba no aparecio aqui), pero TAMPOCO son
     "infraestructura muchos dependen de ella" en el sentido amplio que
     sugiere el termino -- son componentes minusculos y aislados donde el
     PageRank se concentra porque no hay fuga de rank hacia el resto del
     grafo (2-3 nodos repartiendose el rank entre si). El hallazgo real y
     honesto es mas estrecho que "infraestructura invisible": son PARES DE
     PLUGINS COMPANEROS (a menudo del mismo autor, plugin+su addon) con bus
     factor 1 cada uno, cuya dependencia mutua es real pero muy local. Se
     mantienen en el CSV porque el patron (PageRank alto, adopcion baja,
     bus factor real) sigue siendo cierto -- se ajusta el nombre/framing al
     reportar, no el criterio numerico.

  b) "Hojas populares" -- 3 casos verificados (theme_moove, format_tiles,
     block_completion_progress): n_versions altos (21, 49, 11) y
     downloads_90d proporcionales a installations (11.416, 8.426, 6.639)
     confirman que son plugins reales, maduros y activamente usados, no
     artefactos de conteo. Un CUARTO caso, local_mailtest (installations=
     11.110, pero n_versions=1 y first_release_ts=2026-04-21, ~5 meses antes
     de esta corrida) se investigo aparte por ser sospechoso segun el patron
     que se esperaba descartar ("parece nuevo pero tiene instalaciones
     altas"): el plugin real (michael-milette/moodle-local_mailtest en
     GitHub) existe desde hace anios en la practica, asi que n_versions=1 y
     first_release_ts=2026 son casi seguro un artefacto de COBERTURA de la
     extraccion de versiones (parseo incompleto de version.php historico),
     NO evidencia de que installations=11.110 sea falso -- installations
     viene de un snapshot independiente de moodle.org, no del conteo de
     versiones. Se mantiene en la lista (el patron "instalaciones altas,
     sin estructura de dependencias" sigue siendo cierto), pero se marca
     aqui explicitamente que first_release_ts/n_versions NO son confiables
     para este componente especifico -- no se usan en ningun calculo de este
     script mas alla de mostrarse en la salida de verificacion.

Salida:
  data/processed/pagerank_vs_instalaciones_correlaciones.csv
  data/processed/pagerank_vs_instalaciones_infraestructura_invisible.csv
  data/processed/pagerank_vs_instalaciones_hojas_populares.csv

Uso: python3 09_pagerank_vs_instalaciones.py
"""
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from neo4j import GraphDatabase
from scipy.stats import spearmanr

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _gds_utils import ROOT, load_env  # noqa: E402

load_env()

URI = os.environ["NEO4J_URI"]
AUTH = (os.environ["NEO4J_USER"], os.environ["NEO4J_PASSWORD"])
PROCESSED = ROOT / "data" / "processed"

P_ALTO = 90       # percentil "PageRank alto" / "installations altas"
P_BAJO_INVISIBLE = 40   # percentil "installations bajas" para infraestructura invisible
P_BAJO_HOJA = 25   # percentil "pagerank bajo" para hojas populares (entre conectados)

N_VERIFICAR = 3  # casos llamativos verificados manualmente por lista


def main() -> None:
    driver = GraphDatabase.driver(URI, auth=AUTH)
    with driver.session() as session:
        rows = session.run(
            """
            MATCH (p:Plugin) WHERE p.in_directory <> false
            RETURN p.component AS component, p.name AS name, p.plugin_type AS plugin_type,
                   p.installations AS installations, p.pagerank_dep AS pagerank_dep,
                   p.pagerank_soc AS pagerank_soc, p.degree_dep AS degree_dep,
                   p.degree_soc AS degree_soc, p.first_release_ts AS first_release_ts,
                   p.last_release_ts AS last_release_ts
            """
        ).data()
        maint_count = {r["c"]: r["n"] for r in session.run(
            "MATCH (p:Plugin)<-[:MAINTAINS]-(m:Maintainer) WHERE p.in_directory <> false "
            "RETURN p.component AS c, count(m) AS n"
        ).data()}
    driver.close()

    df = pd.DataFrame(rows)
    df["n_maintainers"] = df["component"].map(maint_count).fillna(0).astype(int)
    df["maintainer_status"] = np.select(
        [df["n_maintainers"] == 0, df["n_maintainers"] == 1],
        ["sin_mantenedor", "unico"],
        default="multiple",
    )

    # ---------------------------------------------------------------
    # 1. Correlaciones de Spearman
    # ---------------------------------------------------------------
    corr_rows = []
    for pr_col, deg_col, label in [
        ("pagerank_dep", "degree_dep", "pagerank_dep_vs_installations"),
        ("pagerank_soc", "degree_soc", "pagerank_soc_vs_installations"),
    ]:
        sub_all = df.dropna(subset=[pr_col, "installations"])
        rho_all, p_all = spearmanr(sub_all[pr_col], sub_all["installations"])
        corr_rows.append({
            "comparacion": label, "subconjunto": "todos_los_validos",
            "n": len(sub_all), "spearman_rho": rho_all, "p_value": p_all,
        })

        sub_conn = sub_all[sub_all[deg_col] > 0]
        rho_conn, p_conn = spearmanr(sub_conn[pr_col], sub_conn["installations"])
        corr_rows.append({
            "comparacion": label, "subconjunto": f"solo_{deg_col}_mayor_0",
            "n": len(sub_conn), "spearman_rho": rho_conn, "p_value": p_conn,
        })

    corr_df = pd.DataFrame(corr_rows)
    corr_df.to_csv(PROCESSED / "pagerank_vs_instalaciones_correlaciones.csv", index=False)
    print("[correlaciones]")
    print(corr_df.to_string(index=False))

    # ---------------------------------------------------------------
    # 2. Casos discordantes -- infraestructura invisible (dep)
    # ---------------------------------------------------------------
    conn_dep = df.dropna(subset=["pagerank_dep", "installations"])
    conn_dep = conn_dep[conn_dep["degree_dep"] > 0]
    pr_thresh_hi = np.percentile(conn_dep["pagerank_dep"], P_ALTO)
    inst_thresh_lo = np.percentile(conn_dep["installations"], P_BAJO_INVISIBLE)

    invisible = conn_dep[
        (conn_dep["pagerank_dep"] >= pr_thresh_hi)
        & (conn_dep["installations"] <= inst_thresh_lo)
    ].sort_values("pagerank_dep", ascending=False)

    print(f"\n[infraestructura invisible] umbrales sobre {len(conn_dep)} plugins con "
          f"degree_dep>0 e installations no-nulo: pagerank_dep >= P{P_ALTO} "
          f"({pr_thresh_hi:.4f}), installations <= P{P_BAJO_INVISIBLE} ({inst_thresh_lo:.1f}). "
          f"{len(invisible)} plugins cumplen ambos.")

    invisible_out = invisible.head(15)[
        ["component", "name", "plugin_type", "pagerank_dep", "degree_dep",
         "installations", "n_maintainers", "maintainer_status", "first_release_ts"]
    ]
    invisible_out.to_csv(
        PROCESSED / "pagerank_vs_instalaciones_infraestructura_invisible.csv", index=False
    )
    print(invisible_out.to_string(index=False))

    # ---------------------------------------------------------------
    # 2. Casos discordantes -- hojas populares
    # ---------------------------------------------------------------
    all_inst = df.dropna(subset=["installations"])
    inst_thresh_hi = np.percentile(all_inst["installations"], P_ALTO)
    pr_thresh_lo = np.percentile(conn_dep["pagerank_dep"], P_BAJO_HOJA)

    is_isolated_or_low_pr = (
        df["degree_dep"].fillna(0).eq(0)
        | (df["pagerank_dep"].notna() & (df["pagerank_dep"] <= pr_thresh_lo))
    )
    hojas = df[
        df["installations"].notna()
        & (df["installations"] >= inst_thresh_hi)
        & is_isolated_or_low_pr
    ].sort_values("installations", ascending=False)

    print(f"\n[hojas populares] umbrales: installations >= P{P_ALTO} sobre "
          f"{len(all_inst)} plugins con installations no-nulo ({inst_thresh_hi:.1f}), "
          f"y (degree_dep=0 O pagerank_dep <= P{P_BAJO_HOJA} entre conectados "
          f"[{pr_thresh_lo:.4f}]). {len(hojas)} plugins cumplen ambos.")

    hojas_out = hojas.head(15)[
        ["component", "name", "plugin_type", "installations", "pagerank_dep",
         "degree_dep", "n_maintainers", "maintainer_status", "first_release_ts"]
    ]
    hojas_out.to_csv(
        PROCESSED / "pagerank_vs_instalaciones_hojas_populares.csv", index=False
    )
    print(hojas_out.to_string(index=False))

    # ---------------------------------------------------------------
    # 3. Verificacion manual de artefactos (impresa, no filtra los CSV --
    #    los CSV ya reflejan el criterio numerico; esto es un chequeo aparte
    #    documentado en el reporte y en docs/decisions.md, no un post-filtro
    #    silencioso)
    # ---------------------------------------------------------------
    print("\n[verificacion manual -- ver docs/decisions.md para el detalle completo]")
    print("Top candidatos a verificar (infraestructura invisible):")
    print(invisible_out.head(N_VERIFICAR)[["component", "degree_dep", "installations",
                                            "first_release_ts"]].to_string(index=False))
    print("Top candidatos a verificar (hojas populares):")
    print(hojas_out.head(N_VERIFICAR)[["component", "degree_dep", "pagerank_dep",
                                        "installations", "first_release_ts"]].to_string(index=False))


if __name__ == "__main__":
    main()
