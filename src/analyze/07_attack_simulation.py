#!/usr/bin/env python3
"""
Fase 7, Item 5 (docs/plan_fase7_analisis.md) - Simulacion de ataque dirigido,
acotada (tope de 3 horas, sin excepciones, ver seccion "alcance fijo" del item).

============================================================================
MARCO OBLIGATORIO -- LEER ANTES DE CITAR CUALQUIER NUMERO DE ESTE SCRIPT:
Esta es una simulacion ESTATICA de exposicion estructural inmediata. NO modela
la reaccion real de la comunidad (otros mantenedores que asuman el plugin,
forks que aparezcan, usuarios que migren, el propio programa de mantenedores
huerfanos de Moodle interviniendo). Mide unicamente que le pasaria a la
topologia del grafo en el INSTANTE en que un conjunto de mantenedores
desaparece, todo lo demas constante. NO USAR lenguaje que sugiera que esto
predice lo que "pasaria" en la realidad -- solo lo que queda EXPUESTO
estructuralmente.
============================================================================

GRAFO USADO (discrepancia encontrada y declarada explicitamente, no asumida):
El texto del item 5 en el plan describe el grafo como "la union
CO_MAINTAINED+DEPENDS_ON, 2.963 nodos, LCC=1.222 (41.2%)". Verificado en vivo
contra Neo4j (14/09/2026): esa cifra es EXACTA (2.963 nodos, LCC=1.222,
41.2%), pero describe un grafo DISTINTO al que este item necesita -- ese es
G_soc de 01_centrality.py: solo nodos Plugin, aristas CO_MAINTAINED (Plugin-
Plugin, dos plugins que comparten mantenedor) + DEPENDS_ON. Ese grafo NO TIENE
nodos Maintainer, por lo que es imposible "remover mantenedores" o medir
"plugins que quedan sin mantenedor" sobre el (ninguna de las dos cosas existe
en un grafo sin nodos Maintainer).

Lo que el procedimiento del propio item 5 exige (remover mantenedores, medir
plugins sin mantenedor / instalaciones expuestas) solo es computable sobre un
grafo BIPARTITO Mantenedor-Plugin. Este script usa por lo tanto:
  Nodos: Maintainer (1.414) + Plugin (2.963, incluye los 75 nodos de
         dependencias hacia el nucleo/plugins retirados fuera del directorio,
         ya documentados en la metodologia).
  Aristas: MAINTAINS (Maintainer->Plugin, 4.111 en Neo4j) + DEPENDS_ON
         (Plugin->Plugin, 741 en Neo4j), ambas tratadas como no dirigidas
         (misma convencion que G_soc en 01_centrality.py para DEPENDS_ON).
Verificado en vivo (14/09/2026): 4.377 nodos (2.963 Plugin + 1.414
Maintainer), 4.839 aristas, componente conexo mayor = 1.579 nodos (36,1% de
4.377) -- NO coincide con el 2.963/1.222/41,2% citado en el plan porque es,
como se explico arriba, un grafo distinto (bipartito vs. solo-Plugin). Ambas
cifras son correctas para su respectivo grafo; se documentan las dos en la
memoria para no dejar una cifra sin explicar frente a otras partes del
documento (mismo espiritu de la nota que el plan pide para 2.888 vs 2.963).

CENTRALIDAD: fresca, no reusada de Fase 3. degree_maint/betweenness_maint
(01_centrality.py) se calcularon sobre G_maint = CO_MAINTAINS, una proyeccion
Maintainer-Maintainer ponderada por plugins compartidos -- una topologia
distinta a la bipartita+DEPENDS_ON que este item necesita (un mantenedor
"puente" en G_maint no es necesariamente el mismo nodo critico en este grafo,
donde los caminos tambien pueden pasar por cadenas DEPENDS_ON entre plugins).
Por eso se calculan aqui, con networkx, degree y betweenness EXACTOS sobre
este grafo especifico -- exactamente la salvedad que el encargo preveia
("si las almacenadas no aplican a este grafo especifico, calcular unas
nuevas y decirlo explicitamente").

PROCEDIMIENTO:
  - Orden de remocion PRECALCULADO una sola vez (ranking estatico por grado /
    por betweenness sobre el grafo ORIGINAL), no recalculado tras cada
    remocion -- eleccion deliberada por costo (recalcular betweenness exacta
    ~1.400 veces no cabe en el tope de 3h) y es la convencion estandar en la
    literatura de "attack tolerance" (Albert, Jeong & Barabasi 2000: ranking
    inicial, no adaptativo). Declarado aqui explicitamente.
  - Remocion dirigida por grado y por betweenness: 2 corridas deterministas.
  - Remocion aleatoria: 100 replicas con orden aleatorio de mantenedores,
    semillas fijas 1000..1099 (reproducible).
  - En cada paso t (mantenedores removidos) se mide, con t/M = fraccion de
    mantenedores removidos (M=1.414 mantenedores totales):
      (a) tamano de la componente conexa mayor del grafo restante, como
          fraccion del grafo ORIGINAL completo (4.377 nodos) -- denominador
          FIJO durante toda la simulacion (misma convencion que el 41,2%
          citado en el plan: LCC / N_total_original, no N_restante).
      (b) numero de plugins que se quedan con cero mantenedores activos.
      (c) instalaciones totales de esos plugins sin mantenedor ("expuestas").
  - Implementacion: la trayectoria de LCC se calcula con una tecnica de
    Union-Find "reverse-add" (offline dynamic connectivity bajo eliminacion
    de nodos: se reconstruye anadiendo los mantenedores de atras hacia
    adelante sobre el orden de remocion) -- O((V+E) alpha(V)) por corrida en
    vez de recomputar componentes conexas desde cero en cada uno de los ~1.400
    pasos x 102 corridas, lo que habria sido demasiado lento en Python puro
    para el tope de 3h. Los conteos de plugins-sin-mantenedor / instalaciones
    expuestas se acumulan de forma incremental hacia adelante (O(aristas)).

RECORTE DE ALCANCE: NINGUNO. El truco de Union-Find hace que las 100 replicas
aleatorias + las 2 corridas dirigidas completas (barriendo el 100% de los
1.414 mantenedores, no solo una fraccion) corran en segundos, muy por debajo
del tope de 3h -- no hizo falta reducir replicas ni limitarse a un solo
criterio de centralidad.

Salida:
  figures/simulacion_ataque_dirigido.png  (figura unica, 2 paneles: %plugins
    sin mantenedor y %instalaciones expuestas, ambos vs. fraccion de
    mantenedores removidos; grado vs. betweenness vs. mediana+RIC aleatorio)
  data/processed/attack_simulation_summary.csv (tabla de puntos de control)

Uso: python3 07_attack_simulation.py
"""
import os
import random
import sys
import time
from pathlib import Path

import networkx as nx
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from neo4j import GraphDatabase

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _gds_utils import ROOT, load_env  # noqa: E402
import _fig_style as fs  # noqa: E402

load_env()

URI = os.environ["NEO4J_URI"]
AUTH = (os.environ["NEO4J_USER"], os.environ["NEO4J_PASSWORD"])
PROCESSED = ROOT / "data" / "processed"
FIGURES = ROOT / "figures"
FIGURES.mkdir(exist_ok=True)

N_RANDOM_REPLICATES = 100
RANDOM_SEED_BASE = 1000  # semillas 1000..1099, reproducible

# Paleta identica al resto del proyecto (05_series_descriptivo.py / 06_pipeline_figures.py)
COLOR_TEXT = "#262220"
COLOR_EDGE = "#2f5d68"        # teal apagado -- betweenness (criterio "mas agresivo" esperado)
COLOR_WARN = "#a8741c"        # ambar -- grado
COLOR_TEAL_LIGHT = "#7fa8b0"  # teal claro -- mediana aleatoria
COLOR_GRAY = "#9aa5b1"        # gris calido -- banda RIC aleatoria

STATIC_FOOTNOTE = (
    "Simulacion ESTATICA de exposicion estructural inmediata: no modela reaccion real de la\n"
    "comunidad (relevo de mantenedores, forks, migracion de usuarios). Mide que queda expuesto\n"
    "en el grafo al instante de remover mantenedores, no una prediccion de lo que ocurriria."
)


class UnionFind:
    """Union-Find (weighted quick-union + path compression) sobre nodos arbitrarios
    (hashables). Se usa para reconstruir la trayectoria de la componente conexa mayor
    en O((V+E) alpha(V)) por corrida via la tecnica 'reverse-add' (ver docstring del
    modulo): en vez de recomputar componentes conexas desde cero en cada uno de los
    ~1.400 pasos de remocion x 102 corridas (demasiado lento en Python puro para el
    tope de 3h), se parte del grafo con TODOS los mantenedores ya removidos y se van
    anadiendo de vuelta en orden inverso, registrando el tamano de la componente mayor
    tras cada adicion."""

    def __init__(self, nodes):
        self.parent = {n: n for n in nodes}
        self.size = {n: 1 for n in nodes}
        self.max_size = 1 if nodes else 0

    def find(self, x):
        root = x
        while self.parent[root] != root:
            root = self.parent[root]
        while self.parent[x] != root:
            self.parent[x], x = root, self.parent[x]
        return root

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return
        if self.size[ra] < self.size[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        self.size[ra] += self.size[rb]
        if self.size[ra] > self.max_size:
            self.max_size = self.size[ra]


def lcc_trajectory(all_nodes, permanent_edges, maint_neighbors, removal_order):
    """Devuelve una lista de longitud M+1 (M=len(removal_order)) con el tamano de la
    componente conexa mayor tras remover t=0..M mantenedores, en ese orden."""
    uf = UnionFind(all_nodes)
    for u, v in permanent_edges:
        uf.union(u, v)
    M = len(removal_order)
    trace_reverse = [uf.max_size]  # i=0 -> t=M (todos los mantenedores removidos)
    for node in reversed(removal_order):
        for nbr in maint_neighbors.get(node, ()):
            uf.union(node, nbr)
        trace_reverse.append(uf.max_size)  # i-esimo -> t = M - i
    return [trace_reverse[M - t] for t in range(M + 1)]


def exposure_trajectory(plugin_ids, initial_count, maint_to_plugins, removal_order, installs):
    """Devuelve (n_expuestos[t], installs_expuestas[t]) para t=0..M, acumulando hacia
    adelante en O(aristas) total (sin recomputar sumas completas en cada paso)."""
    count = dict(initial_count)
    exposed = set(p for p in plugin_ids if count[p] == 0)
    total_installs_exposed = sum(installs.get(p, 0) or 0 for p in exposed)
    n_exposed = [len(exposed)]
    installs_exposed = [total_installs_exposed]
    for node in removal_order:
        for p in maint_to_plugins.get(node, ()):
            count[p] -= 1
            if count[p] == 0:
                exposed.add(p)
                total_installs_exposed += installs.get(p, 0) or 0
        n_exposed.append(len(exposed))
        installs_exposed.append(total_installs_exposed)
    return n_exposed, installs_exposed


def main() -> None:
    t0 = time.time()
    driver = GraphDatabase.driver(URI, auth=AUTH)
    with driver.session() as session:
        maintainer_ids = [r["user_id"] for r in session.run(
            "MATCH (m:Maintainer) RETURN m.user_id AS user_id"
        ).data()]
        plugin_rows = session.run(
            "MATCH (p:Plugin) RETURN p.component AS component, p.installations AS installations"
        ).data()
        maintains_edges = session.run(
            "MATCH (m:Maintainer)-[:MAINTAINS]->(p:Plugin) RETURN m.user_id AS m, p.component AS p"
        ).data()
        depends_edges = session.run(
            "MATCH (a:Plugin)-[:DEPENDS_ON]->(b:Plugin) RETURN a.component AS a, b.component AS b"
        ).data()
    driver.close()

    plugin_ids = [r["component"] for r in plugin_rows]
    installs = {r["component"]: (r["installations"] or 0) for r in plugin_rows}

    def mnode(user_id):
        return f"M::{user_id}"

    # ---- construccion del grafo bipartito Maintainer-Plugin + DEPENDS_ON ----
    G = nx.Graph()
    G.add_nodes_from(plugin_ids, kind="plugin")
    G.add_nodes_from([mnode(m) for m in maintainer_ids], kind="maintainer")
    G.add_edges_from([(mnode(r["m"]), r["p"]) for r in maintains_edges])
    G.add_edges_from([(r["a"], r["b"]) for r in depends_edges])

    n_total = G.number_of_nodes()
    n_edges = G.number_of_edges()
    comps = sorted(nx.connected_components(G), key=len, reverse=True)
    lcc0 = len(comps[0])
    print(f"[grafo] {n_total} nodos ({len(plugin_ids)} Plugin + {len(maintainer_ids)} Maintainer), "
          f"{n_edges} aristas")
    print(f"[grafo] LCC baseline: {lcc0} nodos ({lcc0/n_total*100:.1f}% de {n_total}) -- "
          f"cf. 2.963/1.222 (41.2%) del plan, que describe el grafo SOLO-Plugin "
          f"CO_MAINTAINED+DEPENDS_ON, no este bipartito (ver docstring)")

    maint_to_plugins = {r["m"]: [] for r in maintains_edges}
    for r in maintains_edges:
        maint_to_plugins[r["m"]].append(r["p"])
    maint_neighbors = {mnode(m): plugins for m, plugins in maint_to_plugins.items()}
    initial_maint_count = {p: 0 for p in plugin_ids}
    for r in maintains_edges:
        initial_maint_count[r["p"]] += 1
    n_orphan_baseline = sum(1 for p in plugin_ids if initial_maint_count[p] == 0)
    installs_orphan_baseline = sum(installs[p] for p in plugin_ids if initial_maint_count[p] == 0)
    print(f"[baseline] {n_orphan_baseline}/{len(plugin_ids)} plugins ya sin mantenedor antes de "
          f"cualquier remocion ({installs_orphan_baseline} instalaciones)")

    permanent_edges = [(r["a"], r["b"]) for r in depends_edges]

    # ---- centralidad fresca sobre ESTE grafo (no se reusa degree_maint/betweenness_maint) ----
    degree_maint = {mnode(m): G.degree(mnode(m)) for m in maintainer_ids}
    print(f"[centralidad] grado calculado para {len(degree_maint)} mantenedores (grado en este grafo "
          f"bipartito = numero de plugins que mantiene, ya que Maintainer solo tiene aristas MAINTAINS)")

    tb0 = time.time()
    betweenness_all = nx.betweenness_centrality(G, normalized=True)
    print(f"[centralidad] betweenness EXACTA calculada sobre los {n_total} nodos en "
          f"{time.time()-tb0:.1f}s (fresca, sobre este grafo bipartito+DEPENDS_ON, no G_maint de Fase 3)")
    betweenness_maint = {mnode(m): betweenness_all[mnode(m)] for m in maintainer_ids}

    order_degree = sorted([mnode(m) for m in maintainer_ids],
                           key=lambda n: (-degree_maint[n], n))
    order_betweenness = sorted([mnode(m) for m in maintainer_ids],
                                key=lambda n: (-betweenness_maint[n], n))

    all_nodes = list(G.nodes())
    M = len(maintainer_ids)

    def run(order):
        lcc = lcc_trajectory(all_nodes, permanent_edges, maint_neighbors, order)
        # BUG corregido antes de dar por buena la corrida: exposure_trajectory recibia
        # maint_to_plugins (claves = user_id crudo), pero `order`/removal_order contiene
        # nodos con prefijo "M::<user_id>" (mismo namespace que el grafo bipartito) --
        # el .get(node, ()) nunca encontraba nada y ningun plugin se marcaba expuesto tras
        # el paso 0. Se usa maint_neighbors (mismas claves prefijadas que `order`), que ya
        # existia para lcc_trajectory. Verificado tras el fix: la exposicion ahora SI crece
        # con cada mantenedor removido.
        n_exp, inst_exp = exposure_trajectory(plugin_ids, initial_maint_count, maint_neighbors,
                                               order, installs)
        return lcc, n_exp, inst_exp

    lcc_deg, nexp_deg, instexp_deg = run(order_degree)
    lcc_bet, nexp_bet, instexp_bet = run(order_betweenness)
    print(f"[simulacion] corridas dirigidas (grado, betweenness) completas, M={M} mantenedores")

    rng_nexp = []
    rng_instexp = []
    rng_lcc = []
    for i in range(N_RANDOM_REPLICATES):
        rnd = random.Random(RANDOM_SEED_BASE + i)
        order = [mnode(m) for m in maintainer_ids]
        rnd.shuffle(order)
        lcc_r, nexp_r, instexp_r = run(order)
        rng_lcc.append(lcc_r)
        rng_nexp.append(nexp_r)
        rng_instexp.append(instexp_r)
    print(f"[simulacion] {N_RANDOM_REPLICATES} replicas aleatorias completas "
          f"(semillas {RANDOM_SEED_BASE}..{RANDOM_SEED_BASE + N_RANDOM_REPLICATES - 1})")

    rng_nexp_df = pd.DataFrame(rng_nexp)     # filas=replica, cols=t
    rng_instexp_df = pd.DataFrame(rng_instexp)
    rng_lcc_df = pd.DataFrame(rng_lcc)
    rng_nexp_p50 = rng_nexp_df.median(axis=0).to_numpy()
    rng_nexp_p25 = rng_nexp_df.quantile(0.25, axis=0).to_numpy()
    rng_nexp_p75 = rng_nexp_df.quantile(0.75, axis=0).to_numpy()
    rng_instexp_p50 = rng_instexp_df.median(axis=0).to_numpy()
    rng_instexp_p25 = rng_instexp_df.quantile(0.25, axis=0).to_numpy()
    rng_instexp_p75 = rng_instexp_df.quantile(0.75, axis=0).to_numpy()

    total_installs = sum(installs.values())
    frac = [t / M for t in range(M + 1)]

    # =====================================================================
    # TABLA RESUMEN (puntos de control) -> consola + CSV
    # =====================================================================
    checkpoints_frac = [0.01, 0.02, 0.05, 0.10, 0.20, 0.30, 0.50]
    rows = []
    for f in checkpoints_frac:
        t = round(f * M)
        if t == 0 or t > M:
            continue
        row = {
            "fraccion_mantenedores_removidos": f,
            "n_mantenedores_removidos": t,
            "plugins_sin_mantenedor_grado": nexp_deg[t],
            "plugins_sin_mantenedor_betweenness": nexp_bet[t],
            "plugins_sin_mantenedor_aleatorio_mediana": rng_nexp_p50[t],
            "plugins_sin_mantenedor_aleatorio_p25": rng_nexp_p25[t],
            "plugins_sin_mantenedor_aleatorio_p75": rng_nexp_p75[t],
            "pct_installs_expuestas_grado": instexp_deg[t] / total_installs * 100,
            "pct_installs_expuestas_betweenness": instexp_bet[t] / total_installs * 100,
            "pct_installs_expuestas_aleatorio_mediana": rng_instexp_p50[t] / total_installs * 100,
            "lcc_frac_grado": lcc_deg[t] / n_total,
            "lcc_frac_betweenness": lcc_bet[t] / n_total,
            "lcc_frac_aleatorio_mediana": rng_lcc_df.median(axis=0).to_numpy()[t] / n_total,
        }
        rows.append(row)
    summary_df = pd.DataFrame(rows)
    summary_df.to_csv(PROCESSED / "attack_simulation_summary.csv", index=False)
    print("\n[tabla] puntos de control -> data/processed/attack_simulation_summary.csv")
    with pd.option_context("display.width", 200, "display.max_columns", 20):
        print(summary_df.round(2).to_string(index=False))

    # hallazgo destacado: comparacion a un checkpoint representativo (5%)
    f_hi = 0.05
    t_hi = round(f_hi * M)
    print(f"\n[hallazgo] al remover el {f_hi*100:.0f}% de mantenedores ({t_hi} de {M}):")
    print(f"  por BETWEENNESS: {nexp_bet[t_hi]} plugins sin mantenedor "
          f"({instexp_bet[t_hi]} instalaciones, {instexp_bet[t_hi]/total_installs*100:.1f}% del total)")
    print(f"  por GRADO:       {nexp_deg[t_hi]} plugins sin mantenedor "
          f"({instexp_deg[t_hi]} instalaciones, {instexp_deg[t_hi]/total_installs*100:.1f}% del total)")
    print(f"  ALEATORIO (mediana de {N_RANDOM_REPLICATES}): {rng_nexp_p50[t_hi]:.0f} plugins sin mantenedor "
          f"({rng_instexp_p50[t_hi]:.0f} instalaciones, {rng_instexp_p50[t_hi]/total_installs*100:.1f}% del total) "
          f"[RIC: {rng_nexp_p25[t_hi]:.0f}-{rng_nexp_p75[t_hi]:.0f} plugins]")
    ratio_bet_vs_rand = nexp_bet[t_hi] / rng_nexp_p50[t_hi] if rng_nexp_p50[t_hi] > 0 else float("nan")
    print(f"  -> betweenness expone {ratio_bet_vs_rand:.1f}x mas plugins sin mantenedor que la "
          f"mediana aleatoria equivalente, al mismo {f_hi*100:.0f}% de mantenedores removidos")

    # =====================================================================
    # FIGURA UNICA: simulacion_ataque_dirigido.png (2 paneles)
    # Pase de legibilidad (2026-09-28): ancho final de pagina, letra >= 9 pt,
    # una sola leyenda compartida debajo de los paneles (antes: una por panel a
    # 8 pt), coma decimal en los ejes. STATIC_FOOTNOTE ya no se incrusta en la
    # imagen (estaba a 7,8 pt): su texto va al pie de figura del documento.
    # =====================================================================
    fs.apply()
    fig, axes = plt.subplots(1, 2, figsize=(fs.TEXT_WIDTH_IN, 3.9))

    pct_plugins_deg = [100 * n / len(plugin_ids) for n in nexp_deg]
    pct_plugins_bet = [100 * n / len(plugin_ids) for n in nexp_bet]
    pct_plugins_rnd_p50 = 100 * rng_nexp_p50 / len(plugin_ids)
    pct_plugins_rnd_p25 = 100 * rng_nexp_p25 / len(plugin_ids)
    pct_plugins_rnd_p75 = 100 * rng_nexp_p75 / len(plugin_ids)

    pct_inst_deg = [100 * v / total_installs for v in instexp_deg]
    pct_inst_bet = [100 * v / total_installs for v in instexp_bet]
    pct_inst_rnd_p50 = 100 * rng_instexp_p50 / total_installs
    pct_inst_rnd_p25 = 100 * rng_instexp_p25 / total_installs
    pct_inst_rnd_p75 = 100 * rng_instexp_p75 / total_installs

    panels = [
        (axes[0], pct_plugins_rnd_p25, pct_plugins_rnd_p75, pct_plugins_rnd_p50, pct_plugins_deg,
         pct_plugins_bet, "% de plugins sin mantenedor", "Plugins sin mantenedor"),
        (axes[1], pct_inst_rnd_p25, pct_inst_rnd_p75, pct_inst_rnd_p50, pct_inst_deg,
         pct_inst_bet, "% de instalaciones expuestas", "Instalaciones expuestas\n(plugins sin mantenedor)"),
    ]
    for ax, p25, p75, p50, deg, bet, ylabel, title in panels:
        ax.fill_between(frac, p25, p75, color=COLOR_GRAY, alpha=0.4,
                        label=f"aleatorio, RIC (n={N_RANDOM_REPLICATES})")
        ax.plot(frac, p50, color=COLOR_TEAL_LIGHT, linewidth=1.8, linestyle="-",
                label="aleatorio, mediana")
        ax.plot(frac, deg, color=COLOR_WARN, linewidth=1.8, label="dirigido: grado")
        ax.plot(frac, bet, color=COLOR_EDGE, linewidth=1.8, label="dirigido: intermediación")
        ax.set_xlabel("Fracción de mantenedores\nretirados", color=COLOR_TEXT)
        ax.set_ylabel(ylabel, color=COLOR_TEXT)
        ax.set_title(title, fontsize=10.5, color=COLOR_TEXT, pad=6)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.tick_params(colors=COLOR_TEXT)
        ax.xaxis.set_major_locator(MultipleLocator(0.2))
        ax.xaxis.set_major_formatter(fs.comma_formatter(1))

    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=2, frameon=False,
               bbox_to_anchor=(0.5, 0.0), columnspacing=1.5)
    fig.suptitle("Retirada dirigida frente a aleatoria de mantenedores\n"
                 "(grafo mantenedor-plugin con dependencias, 4.377 nodos)",
                 color=COLOR_TEXT, fontsize=11)
    fig.tight_layout(rect=(0, 0.13, 1, 1))
    out_path = FIGURES / "simulacion_ataque_dirigido.png"
    fs.save(fig, out_path)
    plt.close(fig)
    print(f"\n[figura] guardada: {out_path}")

    print(f"\n[tiempo total] {time.time()-t0:.1f}s (muy por debajo del tope de 3h del item 5)")


if __name__ == "__main__":
    main()
