#!/usr/bin/env python3
"""
Fase 5 - Interpretacion de riesgos (objetivo especifico 5).

Tres senales de riesgo, reutilizando SOLO datos ya calculados en fases previas
(nada de esto requiere GDS nuevo):
  single_maintainer : bus factor 1 -- un plugin con exactamente un Maintainer.
                       Mismo criterio que la cifra de Fase 3 (72.3%, 2078/2876).
  stale             : ultima release anterior al 2023-09-10 UTC (unix
                       1_694_304_000). MISMO umbral usado en Fase 4 para no
                       romper consistencia entre fases (ver docs/decisions.md,
                       nota de acoplamiento entre fases del 2026-09-10).
  legacy_only       : la release de Moodle mas alta que el plugin declara
                       soportar (via SUPPORTS) es anterior a 4.1. Los strings
                       de MoodleRelease.release ("3.10", "3.2", ...) NO se
                       pueden comparar lexicograficamente -- "3.10" < "3.2"
                       como texto pero es la release MAS NUEVA de las dos.
                       Se parsean a (major, minor) antes de comparar.

Indice compuesto (formula literal del plan, docs/plan.md): z(installations) +
z(in_degree_dep + pagerank_dep) + single_maintainer + stale. NOTA DE DISENO
(no un bug, es la formula tal cual la definio el plan): in_degree_dep es un
entero (0-20) y pagerank_dep un float pequeno (~0.15-2.7), asi que la suma
in_degree_dep+pagerank_dep antes de estandarizar queda dominada por
in_degree_dep -- z() se aplica sobre la SUMA, no sobre cada termino por
separado. Declarar esto explicitamente en la memoria si se usa este indice
tal cual.

BUG PROPIO ENCONTRADO Y CORREGIDO ANTES DE LA REVISION DE AGENTES: la primera
version de este script leia `p.in_degree_dep`, una propiedad que no existe --
Fase 3 la escribio como `Plugin.degree_dep` (ver 01_centrality.py). Cypher
devuelve null en silencio para una propiedad inexistente en vez de fallar, y
con `fillna(0)` aguas abajo el termino de grado quedaba en 0 para los 2.888
plugins sin que nada lo señalara -- el indice compuesto real solo usaba
pagerank_dep, no la suma que pide el plan. Verificado tras el fix: las 30
filas del top-30 ya no tienen `in_degree_dep` nulo.

legacy_only NO entra en el indice compuesto (el plan solo lista 3 senales
mencionadas en el texto, pero la formula del indice solo suma 2 + single_maintainer
+ stale -- legacy_only se reporta aparte, no se inventa un peso para meterlo
en la formula que el plan no especifico).

Riesgo a nivel de mantenedor: (a) cuantos plugins de bus-factor-1 sostiene cada
mantenedor -- si esa persona/organizacion se va, esos plugins quedan sin nadie;
(b) mantenedores "puente" ya identificados en Fase 3 via betweenness_maint
(no se recalcula, se referencia top20_betweenness_maint.csv).

Cruce con el programa oficial de huerfanos de Moodle: NO IMPLEMENTADO en este
ciclo -- requiere scraping nuevo (snapshot de Wayback Machine del programa de
adopcion) que no existe en el repo. Es una decision de alcance, no tecnica;
preguntado a David antes de intentarlo (ver docs/decisions.md y Telegram).

Uso: python3 03_risk.py
"""
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from neo4j import GraphDatabase

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _gds_utils import ROOT, STALE_CUTOFF_UNIX, load_env  # noqa: E402

load_env()

import os  # noqa: E402

URI = os.environ["NEO4J_URI"]
AUTH = (os.environ["NEO4J_USER"], os.environ["NEO4J_PASSWORD"])
PROCESSED = ROOT / "data" / "processed"

LEGACY_CUTOFF = (4, 1)  # Moodle 4.1


def parse_release(s: str):
    m = re.match(r"^(\d+)\.(\d+)", str(s))
    if not m:
        return None
    return (int(m.group(1)), int(m.group(2)))


def main() -> None:
    driver = GraphDatabase.driver(URI, auth=AUTH)
    with driver.session() as session:
        plugin_rows = session.run(
            """
            MATCH (p:Plugin) WHERE p.in_directory <> false
            RETURN p.component AS component, p.name AS name, p.installations AS installations,
                   p.last_release_ts AS last_release_ts, p.degree_dep AS in_degree_dep,
                   p.pagerank_dep AS pagerank_dep, p.louvain_soc AS louvain_soc
            """
        ).data()
        # Filtro p.in_directory <> false repetido en las 3 queries de abajo por el mismo motivo
        # que en plugin_rows -- hoy no cambia nada (0 nodos fuera de directorio tienen MAINTAINS,
        # verificado 2026-09-10), pero sin el filtro un nodo "fuera de directorio" que en el
        # futuro adquiera un mantenedor contaminaria estas listas en silencio (hallazgo de la
        # revision de agentes de Fase 5).
        maint_count = {r["c"]: r["n"] for r in session.run(
            "MATCH (p:Plugin)<-[:MAINTAINS]-(m:Maintainer) WHERE p.in_directory <> false "
            "RETURN p.component AS c, count(m) AS n"
        ).data()}
        supports_rows = session.run(
            "MATCH (p:Plugin)-[:SUPPORTS]->(r:MoodleRelease) WHERE p.in_directory <> false "
            "RETURN p.component AS c, r.release AS rel"
        ).data()
        # mantenedores que sostienen plugins bus-factor-1: si el mantenedor desaparece, esos
        # plugins quedan sin nadie
        bus_factor_maintainers = session.run(
            """
            MATCH (p:Plugin)<-[:MAINTAINS]-(m:Maintainer) WHERE p.in_directory <> false
            WITH p, collect(m) AS ms
            WHERE size(ms) = 1
            WITH ms[0] AS m, p
            RETURN m.user_id AS user_id, m.display_name AS display_name, m.n_plugins AS n_plugins_total,
                   count(p) AS n_bus_factor_plugins,
                   sum(coalesce(p.installations, 0)) AS installs_en_riesgo
            ORDER BY n_bus_factor_plugins DESC LIMIT 30
            """
        ).data()
        bridge_maintainers = session.run(
            """
            MATCH (m:Maintainer) WHERE m.betweenness_maint IS NOT NULL
            RETURN m.user_id AS user_id, m.display_name AS display_name, m.n_plugins AS n_plugins,
                   m.betweenness_maint AS betweenness_maint
            ORDER BY betweenness_maint DESC LIMIT 30
            """
        ).data()
    driver.close()

    # ---- legacy_only por plugin ----
    max_release = {}
    for r in supports_rows:
        parsed = parse_release(r["rel"])
        if parsed is None:
            continue
        c = r["c"]
        if c not in max_release or parsed > max_release[c]:
            max_release[c] = parsed

    df = pd.DataFrame(plugin_rows)
    df["n_maintainers"] = df["component"].map(maint_count).fillna(0).astype(int)
    df["single_maintainer"] = (df["n_maintainers"] == 1).astype(int)
    df["last_release_ts"] = pd.to_numeric(df["last_release_ts"], errors="coerce")
    df["stale"] = (df["last_release_ts"] < STALE_CUTOFF_UNIX).astype(int)
    df["max_supported_release"] = df["component"].map(max_release)
    df["legacy_only"] = df["max_supported_release"].apply(
        lambda v: int(v is not None and v < LEGACY_CUTOFF)
    )

    # denominador = plugins con AL MENOS un mantenedor (12 plugins tienen 0, "single_maintainer"
    # no esta definido para ellos) -- mismo criterio que la cifra de Fase 3 (72.3%, 2078/2876),
    # para no reportar dos porcentajes distintos del mismo numerador en fases distintas
    n_con_maintainer = int((df["n_maintainers"] > 0).sum())
    print(f"[senales] single_maintainer: {df['single_maintainer'].sum()}/{n_con_maintainer} "
          f"({df['single_maintainer'].sum()/n_con_maintainer*100:.1f}%, de plugins con >=1 mantenedor; "
          f"{len(df)-n_con_maintainer} plugins con 0 mantenedores, excluidos de este porcentaje)")
    print(f"[senales] stale: {df['stale'].sum()}/{len(df)} ({df['stale'].mean()*100:.1f}%)")
    print(f"[senales] legacy_only (max soportado < Moodle 4.1): {df['legacy_only'].sum()}/{len(df)} "
          f"({df['legacy_only'].mean()*100:.1f}%) "
          f"[{df['max_supported_release'].isna().sum()} plugins sin SUPPORTS, excluidos del calculo]")

    # ---- indice compuesto (formula literal del plan) ----
    def zscore(s):
        s = s.astype(float)
        std = s.std(ddof=0)
        if std == 0 or pd.isna(std):
            # guarda defensiva (hallazgo de la revision de agentes de Fase 5): no ocurre hoy
            # sobre las 2888 filas completas (std(installations)~=1598, std(degree_pagerank_sum)
            # ~=0.88, verificado), pero si este script se reusa sobre un subconjunto filtrado
            # (ej. una sola comunidad Louvain) una columna constante daria division por cero
            # silenciosa (NaN/inf) sin este guard.
            return pd.Series(0.0, index=s.index)
        return (s - s.mean()) / std

    df["z_installations"] = zscore(df["installations"].fillna(0))
    df["degree_pagerank_sum"] = df["in_degree_dep"].fillna(0) + df["pagerank_dep"].fillna(0)
    df["z_degree_pagerank"] = zscore(df["degree_pagerank_sum"])
    df["risk_score"] = (
        df["z_installations"] + df["z_degree_pagerank"] + df["single_maintainer"] + df["stale"]
    )

    # NOTA DE INTERPRETACION (hallazgo critico de la revision de agentes de Fase 5, 2026-09-10):
    # risk_score, tal cual la define el plan, mide IMPACTO POTENCIAL (popularidad + centralidad
    # de dependencia), NO probabilidad de abandono -- z_installations y z_degree_pagerank pueden
    # llegar a ~20-28, mientras single_maintainer/stale solo aportan 0-2 puntos combinados. 6/30
    # del top-30 real tienen single_maintainer=0 Y stale=0 y aun asi entran solo por escala
    # (ej. mod_customcert, mod_hvp). NO renombrar la formula (es literal del plan), pero
    # declarar esta salvedad explicitamente en la memoria antes de citar "top riesgo" sin mas.
    # Se exporta ademas un ranking secundario para el caso de uso real "que se cae si nadie mas
    # lo sostiene": filtrado a single_maintainer=1 AND stale=1, ordenado por impacto (installations).
    top30 = df.sort_values("risk_score", ascending=False).head(30)[
        ["component", "name", "installations", "in_degree_dep", "pagerank_dep",
         "single_maintainer", "stale", "legacy_only", "risk_score"]
    ]
    top30.to_csv(PROCESSED / "risk_top30_plugins.csv", index=False)
    print(f"\n[indice] top 30 plugins de mayor riesgo (impacto potencial, NO prob. de abandono) "
          f"-> risk_top30_plugins.csv")
    print(top30[["component", "risk_score"]].head(10).to_string(index=False))
    n_solo_impacto = int(((top30["single_maintainer"] == 0) & (top30["stale"] == 0)).sum())
    print(f"[indice] {n_solo_impacto}/30 del top estan ahi solo por instalaciones/grado "
          f"(single_maintainer=0 AND stale=0) -- confirma que el indice esta dominado por escala")

    fragiles = df[(df["single_maintainer"] == 1) & (df["stale"] == 1)].sort_values(
        "installations", ascending=False
    ).head(30)[["component", "name", "installations", "in_degree_dep", "n_maintainers", "legacy_only"]]
    fragiles.to_csv(PROCESSED / "risk_top30_fragiles_bus_factor1_y_stale.csv", index=False)
    print(f"[indice] {len(df[(df['single_maintainer'] == 1) & (df['stale'] == 1)])} plugins son "
          f"single_maintainer=1 Y stale=1 (fragiles de verdad); top 30 por instalaciones -> "
          f"risk_top30_fragiles_bus_factor1_y_stale.csv")

    # ---- cruce legacy_only vs stale (sugerido por la revision de agentes de Fase 5) ----
    crosstab = pd.crosstab(df["legacy_only"], df["stale"])
    print(f"\n[cruce] legacy_only x stale:\n{crosstab}")

    # ---- correlacion risk_score vs comunidad (Fase 4): confirma el hallazgo de pct_stale variable ----
    comm_risk = df.groupby("louvain_soc")["risk_score"].mean().sort_values(ascending=False)
    print(f"\n[cruce Fase4/Fase5] correlacion risk_score-comunidad: la comunidad con mayor riesgo medio "
          f"es {comm_risk.index[0]} (media={comm_risk.iloc[0]:.2f}), la de menor es "
          f"{comm_risk.index[-1]} (media={comm_risk.iloc[-1]:.2f})")

    df.to_csv(PROCESSED / "risk_all_plugins.csv", index=False)

    # ---- riesgo a nivel de mantenedor ----
    pd.DataFrame(bus_factor_maintainers).to_csv(PROCESSED / "risk_maintainers_bus_factor.csv", index=False)
    pd.DataFrame(bridge_maintainers).to_csv(PROCESSED / "risk_maintainers_bridge.csv", index=False)
    print(f"\n[mantenedores] top 30 por plugins en bus-factor-1 -> risk_maintainers_bus_factor.csv")
    print(f"[mantenedores] top 30 'puente' por betweenness_maint (de Fase 3, referenciado no recalculado) "
          f"-> risk_maintainers_bridge.csv")

    # ---- cruce de las dos listas de mantenedores: bus-factor alto Y puente alto ----
    bf_ids = {r["user_id"] for r in bus_factor_maintainers}
    bridge_ids = {r["user_id"] for r in bridge_maintainers}
    overlap = bf_ids & bridge_ids
    print(f"\n[mantenedores] {len(overlap)} mantenedores estan en AMBOS top-30 (sostienen muchos plugins "
          f"bus-factor-1 Y son puentes estructurales del grafo de co-mantenimiento) -- estos son los "
          f"candidatos mas claros a 'punto unico de fallo' del ecosistema")


if __name__ == "__main__":
    main()
