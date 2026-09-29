#!/usr/bin/env python3
"""
Objetivo especifico 4 - "detectar comunidades... y visualizarlas".

Las visualizaciones de detalle (grafo completo G_soc) ya existian desde Fase 4
(figures/g_soc.graphml para Gephi, figures/g_soc_interactive.html con pyvis) --
commit de314a2, 2026-09-10 -- pero no tenian una version estatica embebible en
la memoria (documento Word/PDF, no puede incrustar HTML interactivo), y ninguna
de las dos referencia la comunidad de cada nodo dentro del propio archivo (el
GraphML solo trae peso de arista; la comunidad vive como propiedad de Neo4j,
p.louvain_soc, escrita en Fase 4 pero nunca exportada a un fichero standalone).

Este script genera un "meta-grafo" agregado (nodo = comunidad, no plugin) de
las top-15 comunidades de G_soc por tamano.

v2 (2026-09-13): v1 coloreaba cada nodo por su categoria dominante unica --
no mostraba ninguna "mezcla" real pese a que el texto de la memoria afirmaba
que la figura evidenciaba el desajuste NMI≈0,33. Sustituido por graficos de
sectores (composicion real) en layout de rejilla.

v3 (2026-09-13, mismo dia): feedback de David -- (a) usar donut en vez de pie
("dona" con hueco central: mejor jerarquia visual, deja sitio para el numero
de plugins sin una etiqueta aparte que se solape), (b) las lineas de
colaboracion atravesaban circulos no relacionados en el layout de rejilla v2
(un layout arbitrario ordenado solo por tamano no tiene en cuenta que dos
comunidades conectadas pueden caer en extremos opuestos de la rejilla), (c)
pidio comparar con otra libreria. Se generan y comparan dos variantes:

  A) "grid"     -- mismo enfoque matplotlib-puro que v2, pero con orden
                    consciente de las aristas: las comunidades conectadas se
                    colocan adyacentes en la rejilla (BFS por componente
                    conexo) en vez de solo ordenar por tamano, minimizando
                    cuanto tiene que viajar cada linea.
  B) "graphviz" -- layout con Graphviz `neato` (via pydot/networkx), motor
                    especializado en minimizar cruces y evitar solapes --
                    cada nodo se registra con su radio real (atributo
                    width/height) para que `overlap=false` calcule
                    posiciones que ya de por si separan los circulos. El
                    render final (donas, colores, leyenda) se sigue haciendo
                    con matplotlib para mantener el mismo estilo visual que
                    el resto de figuras de la memoria -- graphviz aqui solo
                    aporta las posiciones (x, y), no el dibujo.

Ambas se guardan por separado para comparar antes de elegir una.

v4 (2026-09-28, pase de legibilidad del 2do borrador): la figura se dibuja a
su ancho FINAL en la página (_fig_style.TEXT_WIDTH_IN, 1 unidad de datos =
escala fija en pulgadas), letra >= 9 pt. Se quita la palabra "plugins" del
centro de cada dona (estaba a 6,2 pt; el número central es el nº de plugins,
lo explica el pie de figura) y el subtítulo explicativo incrustado (va al pie
de figura del documento, ver docs/figuras.md). El título ya no lleva el
sufijo "layout A/B" (queda en el nombre de archivo). La variante B (graphviz)
se copia además a comunidades_top15_meta.png, que es la promovida en
decisions.md (2026-09-13).
"""
import shutil
import sys
import os
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge, FancyArrowPatch
import networkx as nx
from neo4j import GraphDatabase

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _fig_style as fs  # noqa: E402

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
fs.apply()
FIGURES = ROOT / "figures"
FIGURES.mkdir(exist_ok=True)

TOP_N = 15
MAIN_CATS = ["local", "block", "mod", "tool", "theme", "qtype"]
OTHER_LABEL = "otras (46 categorías)"
COLOR_TEXT = "#262220"

driver = GraphDatabase.driver(
    os.environ["NEO4J_URI"], auth=(os.environ["NEO4J_USER"], os.environ["NEO4J_PASSWORD"])
)
with driver.session() as session:
    plugin_rows = session.run(
        """
        MATCH (p:Plugin) WHERE p.in_directory <> false AND p.louvain_soc IS NOT NULL
        RETURN p.component AS component, p.plugin_type AS category, p.louvain_soc AS community
        """
    ).data()
    maint_edges = session.run(
        "MATCH (a:Plugin)-[r:CO_MAINTAINED]-(b:Plugin) WHERE elementId(a) < elementId(b) "
        "RETURN a.component AS a, b.component AS b, r.weight AS weight"
    ).data()
    dep_edges = session.run(
        "MATCH (a:Plugin)-[:DEPENDS_ON]->(b:Plugin) RETURN a.component AS a, b.component AS b"
    ).data()
driver.close()

component_to_community = {r["component"]: r["community"] for r in plugin_rows}
component_to_category = {r["component"]: r["category"] for r in plugin_rows}

comm_members = defaultdict(list)
for c, comm in component_to_community.items():
    comm_members[comm].append(c)

comm_size = {comm: len(members) for comm, members in comm_members.items()}
top_communities = sorted(comm_size, key=lambda c: comm_size[c], reverse=True)[:TOP_N]
top_set = set(top_communities)

comm_composition = {}
comm_dominant_cat = {}
for comm in top_communities:
    counts = Counter(component_to_category.get(c, "desconocido") for c in comm_members[comm])
    comm_dominant_cat[comm] = counts.most_common(1)[0][0]
    bucketed = Counter()
    for cat, n in counts.items():
        bucketed[cat if cat in MAIN_CATS else OTHER_LABEL] += n
    comm_composition[comm] = bucketed

inter_weight = defaultdict(float)
for r in maint_edges:
    ca, cb = component_to_community.get(r["a"]), component_to_community.get(r["b"])
    if ca in top_set and cb in top_set and ca != cb:
        key = tuple(sorted((ca, cb)))
        inter_weight[key] += r["weight"] or 1.0
for r in dep_edges:
    ca, cb = component_to_community.get(r["a"]), component_to_community.get(r["b"])
    if ca in top_set and cb in top_set and ca != cb:
        key = tuple(sorted((ca, cb)))
        inter_weight[key] += 1.0

G = nx.Graph()
G.add_nodes_from(top_communities)
for (ca, cb), w in inter_weight.items():
    G.add_edge(ca, cb, weight=w)

max_size = max(comm_size[c] for c in top_communities)
min_size = min(comm_size[c] for c in top_communities)


def node_radius(size, lo=0.42, hi=0.98):
    if max_size == min_size:
        return (lo + hi) / 2
    frac = (size - min_size) / (max_size - min_size)
    return lo + frac ** 0.5 * (hi - lo)


# ---------- layout A: rejilla consciente de aristas ----------
def layout_grid():
    components = sorted(nx.connected_components(G), key=len, reverse=True)
    order = []
    for comp in components:
        sub = G.subgraph(comp)
        if len(comp) == 1:
            order.extend(comp)
            continue
        start = max(comp, key=lambda c: comm_size[c])
        order.extend(nx.bfs_tree(sub, start).nodes())
    N_COLS = 4
    CELL = 2.5
    positions = {}
    for i, comm in enumerate(order):
        row, col = divmod(i, N_COLS)
        positions[comm] = (col * CELL, -row * CELL)
    return positions, order, N_COLS, CELL


# ---------- layout B: Graphviz neato (overlap-aware) ----------
def layout_graphviz():
    Gc = G.copy()
    for c in Gc.nodes():
        r_in = node_radius(comm_size[c])  # unidades matplotlib; graphviz usa pulgadas, factor comun
        Gc.nodes[c]["width"] = str(round(2 * r_in / 1.4, 2))
        Gc.nodes[c]["height"] = str(round(2 * r_in / 1.4, 2))
        Gc.nodes[c]["shape"] = "circle"
        Gc.nodes[c]["fixedsize"] = "true"
    Gc.graph["graph"] = {"overlap": "false", "sep": "+18", "splines": "true", "esep": "+6"}
    pos = nx.nx_pydot.graphviz_layout(Gc, prog="neato")
    # normalizar a la misma escala de unidades que layout_grid (aprox)
    xs = [p[0] for p in pos.values()]
    ys = [p[1] for p in pos.values()]
    scale = 2.6 / max(1.0, (max(xs) - min(xs)) / max(1, len(top_communities) ** 0.5))
    cx = (max(xs) + min(xs)) / 2
    cy = (max(ys) + min(ys)) / 2
    positions = {c: ((x - cx) * 0.018, (y - cy) * 0.018) for c, (x, y) in pos.items()}
    return positions


def draw_donut(ax, x, y, r, comm, show_center_label=True):
    comp = comm_composition[comm]
    total = sum(comp.values())
    order = [c for c in MAIN_CATS if comp.get(c)] + ([OTHER_LABEL] if comp.get(OTHER_LABEL) else [])
    ring_w = r * 0.42
    theta0 = 90.0
    for cat in order:
        frac = comp[cat] / total
        theta1 = theta0 - frac * 360.0
        wedge = Wedge((x, y), r, theta1, theta0, width=ring_w, facecolor=cat_color[cat],
                       edgecolor="white", linewidth=0.7, zorder=2)
        ax.add_patch(wedge)
        theta0 = theta1
    ax.add_patch(plt.Circle((x, y), r, fill=False, edgecolor="#2b2b2b", linewidth=0.9, zorder=3))
    # hueco relleno de blanco: las líneas de colaboración ya no cruzan el número central
    ax.add_patch(plt.Circle((x, y), r - ring_w, facecolor="white", edgecolor="#d8d2c4", linewidth=0.6, zorder=3))
    if show_center_label:
        ax.text(x, y, f"{comm_size[comm]}", ha="center", va="center",
                fontsize=max(fs.MIN_PT, 9.5 + 4 * (r / 0.98 - 0.4)), fontweight="bold",
                color=COLOR_TEXT, zorder=4)
    dom_label = comm_dominant_cat[comm]
    ax.text(x, y + r + 0.08, dom_label, ha="center", va="bottom",
            fontsize=9, color="#55504a", style="italic", zorder=4)


palette = plt.get_cmap("tab10")
cat_color = {cat: palette(i) for i, cat in enumerate(MAIN_CATS)}
cat_color[OTHER_LABEL] = "#c7c2b8"

legend_handles = [plt.Line2D([0], [0], marker="o", color="none", markerfacecolor=cat_color[c],
                              markeredgecolor="#2b2b2b", markersize=8, label=c)
                   for c in MAIN_CATS] + \
                  [plt.Line2D([0], [0], marker="o", color="none", markerfacecolor=cat_color[OTHER_LABEL],
                               markeredgecolor="#2b2b2b", markersize=8, label=OTHER_LABEL)]


def render(positions, title_suffix, out_name, curved=False):
    # title_suffix se conserva en la firma (identifica la variante en el log)
    # pero ya no se dibuja en el título.
    xs = [p[0] for p in positions.values()]
    ys = [p[1] for p in positions.values()]
    pad_x, pad_top, pad_bot = 1.05, 1.40, 1.05  # unidades de datos (r máx = 0,98 + etiqueta)
    data_w = (max(xs) - min(xs)) + 2 * pad_x
    data_h = (max(ys) - min(ys)) + pad_top + pad_bot
    W = fs.TEXT_WIDTH_IN
    scale = W / data_w                      # pulgadas por unidad de datos
    title_in, legend_in = 0.50, 0.62
    H = data_h * scale + title_in + legend_in
    fig = plt.figure(figsize=(W, H))
    ax = fig.add_axes([0, legend_in / H, 1, data_h * scale / H])

    for (ca, cb), wgt in inter_weight.items():
        if ca in positions and cb in positions:
            (x1, y1), (x2, y2) = positions[ca], positions[cb]
            if curved:
                arrow = FancyArrowPatch((x1, y1), (x2, y2), connectionstyle="arc3,rad=0.12",
                                         arrowstyle="-", color="#9aa5b1", linewidth=0.6 + 0.18 * wgt,
                                         alpha=0.75, zorder=1)
                ax.add_patch(arrow)
            else:
                ax.plot([x1, x2], [y1, y2], color="#9aa5b1", linewidth=0.6 + 0.18 * wgt,
                        alpha=0.75, zorder=1, solid_capstyle="round")

    for comm in top_communities:
        x, y = positions[comm]
        r = node_radius(comm_size[comm])
        draw_donut(ax, x, y, r, comm)

    ax.set_xlim(min(xs) - pad_x, max(xs) + pad_x)
    ax.set_ylim(min(ys) - pad_bot, max(ys) + pad_top)
    ax.set_aspect("equal")
    ax.axis("off")

    fig.legend(handles=legend_handles, title="Categoría oficial (composición del sector)",
               loc="lower center", bbox_to_anchor=(0.5, 0.0), ncol=4, frameon=False,
               columnspacing=1.0, handletextpad=0.3)
    fig.text(0.5, 1 - 0.04 / H,
             f"Composición de categorías de las {TOP_N} comunidades\nmás grandes de G_soc (Louvain)",
             ha="center", va="top", fontsize=11, fontweight="bold")
    out_path = FIGURES / out_name
    fs.save(fig, out_path)
    print("saved:", out_path, f"({title_suffix})")
    plt.close(fig)
    return out_path


pos_grid, order_grid, N_COLS, CELL = layout_grid()
render(pos_grid, "layout A: rejilla por componente", "comunidades_top15_donut_grid.png", curved=False)

pos_gv = layout_graphviz()
out_gv = render(pos_gv, "layout B: Graphviz neato", "comunidades_top15_donut_graphviz.png", curved=True)
shutil.copyfile(out_gv, FIGURES / "comunidades_top15_meta.png")
print("copiada a:", FIGURES / "comunidades_top15_meta.png")
