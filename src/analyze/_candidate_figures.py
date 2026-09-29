#!/usr/bin/env python3
"""
Candidatos de figuras nuevas desde datos vivos de Neo4j -- exploracion pedida
por David (revisa src/analyze/CLAUDE-investigacion, no forma parte del pipeline
canonico). Genera 3 PNGs en figures/_candidate_*.png, paleta identica al resto
del proyecto (ver 06_pipeline_figures.py / 07_attack_simulation.py).

No toca las figuras numeradas existentes. No es parte del pipeline de memoria
(04_build_memoria.py) -- solo para revision manual.

Pase de legibilidad (2026-09-28, 2do borrador): las tres figuras se dibujan a
su ancho FINAL en la pagina (_fig_style.TEXT_WIDTH_IN, coordenadas en
pulgadas, circulos reales con aspecto 1:1) y se guardan directamente con su
nombre definitivo (cascada_stack.png, ego_mantenedor_justin_hunt.png,
cluster_colaboracion.png) en vez de _candidate_*.png + copia manual. Los
parrafos explicativos incrustados se quitan (van al pie de figura, ver
docs/figuras.md). Ego-network: solo se rotulan los plugins mas instalados
(el listado completo esta en la Tabla A5). Cluster: etiquetas de 9 pt.
"""
import math
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _gds_utils import load_env
load_env()
import _fig_style as fs  # noqa: E402

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Circle
import networkx as nx
from neo4j import GraphDatabase

ROOT = Path(__file__).resolve().parents[2]
FIGURES = ROOT / "figures"

URI = os.environ["NEO4J_URI"]
AUTH = (os.environ["NEO4J_USER"], os.environ["NEO4J_PASSWORD"])

# ---- paleta identica al resto del proyecto ----
COLOR_TEXT = "#262220"
COLOR_EDGE = "#2f5d68"        # teal apagado
COLOR_WARN = "#a8741c"        # ambar
COLOR_TEAL_LIGHT = "#7fa8b0"  # teal claro
COLOR_GRAY = "#9aa5b1"        # gris calido
COLOR_BG_NODE = "#eef3f6"

driver = GraphDatabase.driver(URI, auth=AUTH)
fs.apply()
W = fs.TEXT_WIDTH_IN


def inch_canvas(height_in):
    """Figura al ancho final; eje = lienzo completo, 1 unidad = 1 pulgada."""
    fig = plt.figure(figsize=(W, height_in))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(0, height_in)
    ax.set_aspect("equal")
    ax.axis("off")
    return fig, ax


# =============================================================================
# CANDIDATO 1: cascada de dependencia de la familia STACK (DAG, 9 nodos)
# =============================================================================
def candidate_stack_cascade():
    nodes = ["qtype_stack", "local_quizanalytics", "qformat_stack", "local_stackmatheditor",
             "quiz_stack", "qbank_importasversion", "qbehaviour_dfcbmexplicitvaildate",
             "qbehaviour_dfexplicitvaildate", "qbehaviour_adaptivemultipart"]
    with driver.session() as session:
        info = session.run("""
            UNWIND $ns AS comp
            MATCH (p:Plugin {component:comp})
            OPTIONAL MATCH (p)<-[:MAINTAINS]-(m:Maintainer)
            WITH p, collect(m.display_name) AS maints
            RETURN p.component AS c, p.name AS name, p.installations AS i, maints
        """, ns=nodes).data()
        dep_edges = session.run("""
            UNWIND $ns AS comp
            MATCH (a:Plugin {component:comp})-[:DEPENDS_ON]->(b:Plugin)
            WHERE b.component IN $ns
            RETURN a.component AS a, b.component AS b
        """, ns=nodes).data()
    info_map = {r["c"]: r for r in info}

    dependents = ["local_quizanalytics", "qformat_stack", "local_stackmatheditor", "quiz_stack"]
    upstream = ["qbank_importasversion", "qbehaviour_dfcbmexplicitvaildate",
                "qbehaviour_dfexplicitvaildate", "qbehaviour_adaptivemultipart"]
    center = "qtype_stack"

    # Color ambar = plugin mantenido SOLO por Tim Hunt y/o Chris Sangwin (el mismo duo que
    # qtype_stack). Verificado en Neo4j (2026-09-28): 3 de las 4 dependencias (no
    # qbank_importasversion, que suma a Andreas Steiger) y 2 de los 4 dependientes
    # (qformat_stack, quiz_stack). La v1 de esta figura afirmaba en su subtitulo
    # incrustado que las 4 dependencias eran del duo y los 4 dependientes no -- incorrecto.
    duo = {"Tim Hunt", "Chris Sangwin"}

    def is_duo(comp):
        m = set(info_map[comp]["maints"])
        return m and m.issubset(duo | {None}) and m & duo

    n_up_duo = sum(1 for c in upstream if is_duo(c))

    ROW_H = 1.18
    TITLE_H, HEAD_H, LEG_H = 0.34, 0.50, 0.62
    H = TITLE_H + HEAD_H + 4 * ROW_H + LEG_H
    fig, ax = inch_canvas(H)
    X_LEFT, X_CENTER, X_RIGHT = 0.95, W / 2 - 0.1, W - 1.28
    y_top = H - TITLE_H - HEAD_H - 0.32
    positions = {}
    for i, c in enumerate(dependents):
        positions[c] = (X_LEFT, y_top - i * ROW_H)
    for i, c in enumerate(upstream):
        positions[c] = (X_RIGHT, y_top - i * ROW_H)
    positions[center] = (X_CENTER, y_top - 1.5 * ROW_H)

    def node_radius(installs):
        return 0.19 + 0.10 * math.log10(max(installs, 1) + 1) / math.log10(3000)

    radius = {c: node_radius(info_map[c]["i"] or 0) for c in positions}

    # Aristas con brazos horizontales en ambos extremos (salen por el lado del nodo que
    # mira a la otra columna y entran igual): asi no cruzan los rotulos, que van
    # debajo de cada nodo.
    for r in dep_edges:
        (x1, y1), (x2, y2) = positions[r["a"]], positions[r["b"]]
        start = (x1 + radius[r["a"]], y1)
        end = (x2 - radius[r["b"]], y2)
        # brazo largo del lado de las columnas externas (el tramo diagonal queda en el
        # hueco libre junto al nodo central, lejos de los rotulos de las columnas)
        arm_a, arm_b = (100, 14) if r["b"] == center else (20, 110)
        arrow = FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=11,
                                linewidth=1.3, color=COLOR_GRAY, zorder=1,
                                shrinkA=2, shrinkB=2,
                                connectionstyle=(f"arc,angleA=0,angleB=180,armA={arm_a},armB={arm_b},rad=6"))
        ax.add_patch(arrow)

    for c, (x, y) in positions.items():
        row = info_map[c]
        r = radius[c]
        is_center = c == center
        duo_flag = is_duo(c)
        face = COLOR_EDGE if is_center else (COLOR_WARN if duo_flag else COLOR_TEAL_LIGHT)
        ax.add_patch(Circle((x, y), r, facecolor=face, edgecolor="white", linewidth=1.4, zorder=3))
        ax.text(x, y, fs.num(row['i'] or 0), ha="center", va="center", fontsize=9,
                fontweight="bold", color="white", zorder=4)
        ax.text(x, y - r - 0.04, c, ha="center", va="top", fontsize=9,
                color=COLOR_TEXT, zorder=4, fontweight=("bold" if is_center else "normal"))
        maints = row["maints"] or []
        maints_txt = ",\n".join(maints) if maints else "(sin mantenedor)"
        ax.text(x, y - r - 0.21, maints_txt, ha="center", va="top", fontsize=9,
                color="#6b6459", style="italic", zorder=4, linespacing=1.05)

    y_head = H - TITLE_H - 0.02
    ax.text(0.03, y_head, "Dependen de STACK\n(se rompen si STACK falla)",
            ha="left", multialignment="center", va="top", fontsize=9.5, fontweight="bold", color=COLOR_TEAL_LIGHT)
    ax.text(W - 0.03, y_head, f"STACK depende de ellos\n({n_up_duo} de {len(upstream)} con el mismo dúo)",
            ha="right", multialignment="center", va="top", fontsize=9.5, fontweight="bold", color=COLOR_WARN)
    ax.text(W / 2, H - 0.03, "Cascada de dependencia de la familia STACK (qtype_stack)",
            ha="center", va="top", fontsize=11, fontweight="bold", color=COLOR_TEXT)

    from matplotlib.lines import Line2D
    handles = [
        Line2D([0], [0], marker="o", color="none", markerfacecolor=COLOR_EDGE, markersize=9,
               label="núcleo: qtype_stack"),
        Line2D([0], [0], marker="o", color="none", markerfacecolor=COLOR_WARN, markersize=9,
               label="solo Tim Hunt y/o Chris Sangwin"),
        Line2D([0], [0], marker="o", color="none", markerfacecolor=COLOR_TEAL_LIGHT, markersize=9,
               label="otros mantenedores"),
        Line2D([0], [0], color=COLOR_GRAY, lw=1.3, marker=">", markevery=[1], markersize=6,
               label="A → B: A depende de B"),
    ]
    ax.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, 0.0), ncol=2,
              frameon=False, columnspacing=1.2, handletextpad=0.4)

    out = FIGURES / "cascada_stack.png"
    fs.save(fig, out)
    plt.close(fig)
    print("saved:", out)


# =============================================================================
# CANDIDATO 2: ego-network de un mantenedor bus-factor-1 (punto único de fallo)
# =============================================================================
def candidate_maintainer_ego(user_id="573", label="Justin Hunt"):
    with driver.session() as session:
        rows = session.run("""
            MATCH (m:Maintainer {user_id:$uid})-[:MAINTAINS]->(p:Plugin)
            OPTIONAL MATCH (p)<-[:MAINTAINS]-(o:Maintainer)
            WITH p, count(o) AS nm
            RETURN p.component AS c, p.installations AS i, nm ORDER BY i DESC
        """, uid=user_id).data()
    n = len(rows)
    total_installs = sum(r["i"] or 0 for r in rows)
    n_solo = sum(1 for r in rows if r["nm"] == 1)

    # Pase de legibilidad (2026-09-28): a 15 cm de ancho, 32 etiquetas radiales no
    # caben a >= 9 pt (en la v3 estaban a 6,6 pt sobre 33 cm de lienzo, ~3,3 pt
    # efectivos en pagina). Se rotulan SOLO los N_LABEL plugins con mas
    # instalaciones, repartidos en posiciones equiespaciadas del anillo; el resto
    # de nodos se dibuja sin rotulo (listado completo: Tabla A5 del Anexo).
    N_LABEL = 10
    labeled = set(range(min(N_LABEL, n)))          # rows ya viene ordenado por instalaciones desc
    slots_labeled = [round(k * n / len(labeled)) % n for k in range(len(labeled))]
    free = [sl for sl in range(n) if sl not in slots_labeled]
    slot_of = {}
    for k, idx in enumerate(sorted(labeled)):
        slot_of[idx] = slots_labeled[k]
    for idx, sl in zip([i for i in range(n) if i not in labeled], free):
        slot_of[idx] = sl

    TITLE_H, LEG_H = 0.50, 0.40
    R = 1.40
    LABEL_GAP = 0.10
    ring_h = 2 * (R + 0.45)
    H = TITLE_H + ring_h + LEG_H
    fig, ax = inch_canvas(H)
    cx, cy = W / 2, LEG_H + ring_h / 2
    angle0 = math.pi / 2

    def node_radius(installs):
        return 0.035 + 0.07 * math.log10(max(installs, 1) + 1) / math.log10(6000)

    for i, row in enumerate(rows):
        theta = angle0 - 2 * math.pi * slot_of[i] / n
        x, y = cx + R * math.cos(theta), cy + R * math.sin(theta)
        color = COLOR_WARN if row["nm"] == 1 else COLOR_TEAL_LIGHT
        ax.plot([cx, x], [cy, y], color=color, linewidth=0.8, alpha=0.8, zorder=1)
        r = node_radius(row["i"] or 0)
        is_lab = i in labeled
        ax.add_patch(Circle((x, y), r, facecolor=color, edgecolor=(COLOR_TEXT if is_lab else "white"),
                            linewidth=(1.3 if is_lab else 0.6), zorder=3))
        if not is_lab:
            continue
        lr = R + r + LABEL_GAP
        lx, ly = cx + lr * math.cos(theta), cy + lr * math.sin(theta)
        deg = math.degrees(theta) % 360
        if 70 < deg < 110:
            ha, va = "center", "bottom"
        elif 250 < deg < 290:
            ha, va = "center", "top"
        else:
            ha, va = ("left" if math.cos(theta) >= 0 else "right"), "center"
        ax.text(lx, ly, f"{row['c']}\n({fs.num(row['i'] or 0)} inst.)", ha=ha, va=va, fontsize=9,
                color=COLOR_TEXT, zorder=4, linespacing=1.0, multialignment="center")

    ax.add_patch(Circle((cx, cy), 0.34, facecolor=COLOR_EDGE, edgecolor="white", linewidth=1.5, zorder=5))
    ax.text(cx, cy, label.replace(" ", "\n"), ha="center", va="center", fontsize=10,
            fontweight="bold", color="white", zorder=6, linespacing=1.0)
    ax.text(W / 2, H - 0.03, f"Red de mantenimiento de {label}\n(ego-network de un mantenedor individual)",
            ha="center", va="top", fontsize=11, fontweight="bold", color=COLOR_TEXT)

    from matplotlib.lines import Line2D
    handles = [Line2D([0], [0], marker="o", color="none", markerfacecolor=COLOR_WARN, markersize=8,
                      label=f"{label} es el único mantenedor ({n_solo})"),
               Line2D([0], [0], marker="o", color="none", markerfacecolor="white", markeredgecolor=COLOR_TEXT,
                      markeredgewidth=1.3, markersize=8, label=f"rotulado (los {len(labeled)} más instalados)")]
    if n - n_solo:
        handles.append(Line2D([0], [0], marker="o", color="none", markerfacecolor=COLOR_TEAL_LIGHT,
                              markersize=8, label=f"co-mantenido ({n - n_solo})"))
    ax.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, 0.0), ncol=2, frameon=False)

    out = FIGURES / "ego_mantenedor_justin_hunt.png"
    fs.save(fig, out)
    plt.close(fig)
    print("saved:", out, f"({n} plugins, {n_solo} solo, {total_installs} installs)")


# =============================================================================
# CANDIDATO 3: clúster de colaboración real (componente conexo mediano del
# bipartito Maintainer-Plugin, filtrado a mantenedores multi-plugin)
# =============================================================================
def candidate_collaboration_cluster():
    with driver.session() as session:
        maints = session.run("MATCH (m:Maintainer) RETURN m.user_id AS id, m.n_plugins AS n, "
                              "m.display_name AS name").data()
        edges = session.run("MATCH (m:Maintainer)-[:MAINTAINS]->(p:Plugin) "
                             "RETURN m.user_id AS m, p.component AS p").data()
        installs = {r["c"]: r["i"] for r in session.run(
            "MATCH (p:Plugin) RETURN p.component AS c, p.installations AS i").data()}

    def mnode(u):
        return f"M::{u}"

    name_map = {r["id"]: r["name"] for r in maints}
    n_plugins_map = {r["id"]: r["n"] for r in maints}
    G = nx.Graph()
    G.add_edges_from([(mnode(r["m"]), r["p"]) for r in edges])

    multi = {r["id"] for r in maints if (r["n"] or 0) >= 2}
    sub_nodes = set()
    for r in edges:
        if r["m"] in multi:
            sub_nodes.add(mnode(r["m"]))
            sub_nodes.add(r["p"])
    Gs = G.subgraph(sub_nodes)
    comps = sorted(nx.connected_components(Gs), key=len, reverse=True)

    # componente #5 por tamano (47 nodos): cluster academico francofono/suizo real
    # (Ubicast, CSE Universite de Lausanne, etc.) -- ni el mas grande (demasiado denso
    # para leer, 193 nodos) ni un caso trivial de 2 nodos.
    target = comps[4]
    sub = Gs.subgraph(target)
    plugin_nodes = [n for n in sub.nodes() if not n.startswith("M::")]
    maint_nodes = [n for n in sub.nodes() if n.startswith("M::")]

    # Layout bipartito de dos columnas con reduccion de cruces por barycenter
    # (spring_layout probado primero y descartado: con solo 63 aristas sobre 47
    # nodos no es denso, pero el layout de fuerzas lo colapsaba en una esquina
    # ilegible -- un layout de dos columnas ordenado es la tecnica estandar para
    # grafos bipartitos y aqui si funciona).
    plugin_order = sorted(plugin_nodes)
    maint_order = sorted(maint_nodes, key=lambda n: name_map.get(n[3:], n[3:]))

    def barycenter_pass(fixed_order, fixed_side_pos, moving_nodes, adj):
        scores = {}
        for n in moving_nodes:
            nbrs = [fixed_side_pos[nb] for nb in adj.get(n, []) if nb in fixed_side_pos]
            scores[n] = sum(nbrs) / len(nbrs) if nbrs else fixed_side_pos.get(n, 0)
        return sorted(moving_nodes, key=lambda n: scores[n])

    adj = {n: list(sub.neighbors(n)) for n in sub.nodes()}
    for _ in range(4):
        plugin_pos = {n: i for i, n in enumerate(plugin_order)}
        maint_order = barycenter_pass(plugin_order, plugin_pos, maint_order, adj)
        maint_pos = {n: i for i, n in enumerate(maint_order)}
        plugin_order = barycenter_pass(maint_order, maint_pos, plugin_order, adj)

    # Pase de legibilidad (2026-09-28): lienzo al ancho final, coordenadas en
    # pulgadas; el ancho de cada columna de rotulos se MIDE con el renderer (no se
    # estima) para dejar el maximo espacio a las aristas. Rotulos de nodo a 8 pt
    # (excepcion declarada para etiquetas densas): a 9 pt el rotulo mas largo
    # ("qbehaviour_regexpadaptivewithhelpnopenalty (1.113)", 3,5 in) mas la
    # columna de mantenedores no dejaban hueco para las aristas en 15 cm.
    LABEL_PT = fs.DENSE_LABEL_PT
    n_left, n_right = len(plugin_order), len(maint_order)
    plugin_lbl = {n: f"{n} ({fs.num(installs.get(n, 0) or 0)})" for n in plugin_order}
    # Los rotulos de plugin mas largos que WRAP_IN se parten tras el prefijo de tipo
    # (frankenstyle "tipo_nombre") y esa fila recibe alto extra.
    WRAP_IN = 2.3
    maint_lbl = {}
    for n in maint_order:
        uid = n[3:]
        npl = n_plugins_map.get(uid, 1) or 1
        maint_lbl[n] = f"{name_map.get(uid, uid)} ({npl})"

    probe = plt.figure(figsize=(W, 2))
    rend = probe.canvas.get_renderer()

    def text_w_in(txt, bold=False):
        t = probe.text(0, 0, txt, fontsize=LABEL_PT, fontweight=("bold" if bold else "normal"))
        w = t.get_window_extent(rend).width / probe.dpi
        t.remove()
        return w

    for n in plugin_order:
        if text_w_in(plugin_lbl[n]) > WRAP_IN and "_" in n:
            pre, rest = n.split("_", 1)
            plugin_lbl[n] = f"{pre}_\n{rest} ({fs.num(installs.get(n, 0) or 0)})"
    left_w = max(text_w_in(t) for t in plugin_lbl.values())
    right_w = max(text_w_in(t) for t in maint_lbl.values())
    print("  rotulo mantenedor mas ancho:", max(maint_lbl.values(), key=text_w_in))
    plt.close(probe)

    PITCH = 0.16
    r_p, r_m = 0.035, 0.05
    TITLE_H, HEAD_H = 0.48, 0.28
    # alto por fila de plugins: 1 (una linea) o 1,8 (rotulo partido en dos lineas)
    units = [1.8 if "\n" in plugin_lbl[n] else 1.0 for n in plugin_order]
    offs, acc = [], 0.0
    for k, u in enumerate(units):
        acc += (u + units[k - 1]) / 2 - 1.0 + 1.0 if k else 0.0
        offs.append(acc)
    height = max(offs[-1], n_right - 1) * PITCH
    H = TITLE_H + HEAD_H + height + 0.12
    fig, ax = inch_canvas(H)
    left_x = 0.02 + left_w + 0.05 + r_p
    right_x = W - 0.02 - right_w - 0.05 - r_m
    print(f"  cluster: columna izq {left_w:.2f} in, der {right_w:.2f} in, hueco aristas {right_x - left_x:.2f} in")
    y_top = H - TITLE_H - HEAD_H - 0.06
    pos = {}
    left_scale = height / max(offs[-1], 1e-9)
    right_gap = height / max(n_right - 1, 1)
    for i, n in enumerate(plugin_order):
        pos[n] = (left_x, y_top - offs[i] * left_scale)
    for i, n in enumerate(maint_order):
        pos[n] = (right_x, y_top - i * right_gap)

    for u, v in sub.edges():
        (x1, y1), (x2, y2) = pos[u], pos[v]
        ax.plot([x1, x2], [y1, y2], color=COLOR_GRAY, linewidth=0.8, alpha=0.6, zorder=1)

    for n in plugin_order:
        x, y = pos[n]
        ax.add_patch(Circle((x, y), r_p, facecolor=COLOR_TEAL_LIGHT, edgecolor="white",
                            linewidth=0.5, zorder=3))
        ax.text(x - r_p - 0.05, y, plugin_lbl[n], ha="right", va="center", fontsize=LABEL_PT,
                color=COLOR_TEXT, zorder=4, linespacing=1.0)

    for n in maint_order:
        x, y = pos[n]
        ax.add_patch(Circle((x, y), r_m, facecolor=COLOR_WARN, edgecolor="white",
                            linewidth=0.7, zorder=3))
        ax.text(x + r_m + 0.05, y, maint_lbl[n], ha="left", va="center",
                fontsize=LABEL_PT, color=COLOR_TEXT, zorder=4)

    y_head = y_top + 0.14
    ax.text(left_x, y_head, f"PLUGINS ({n_left})", ha="right", va="bottom",
            fontsize=9.5, fontweight="bold", color=COLOR_TEAL_LIGHT)
    ax.text(right_x, y_head, f"MANTENEDORES ({n_right})", ha="left", va="bottom",
            fontsize=9.5, fontweight="bold", color=COLOR_WARN)
    ax.text(W / 2, H - 0.03, "Clúster real de colaboración\nen el grafo bipartito Mantenedor-Plugin",
            ha="center", va="top", fontsize=11, fontweight="bold", color=COLOR_TEXT)

    out = FIGURES / "cluster_colaboracion.png"
    fs.save(fig, out, min_allowed=fs.DENSE_LABEL_PT)
    plt.close(fig)
    print("saved:", out, f"({len(sub.nodes())} nodos: {len(maint_nodes)} mantenedores + {len(plugin_nodes)} plugins)")


if __name__ == "__main__":
    candidate_stack_cascade()
    candidate_maintainer_ego()
    candidate_collaboration_cluster()
    driver.close()
