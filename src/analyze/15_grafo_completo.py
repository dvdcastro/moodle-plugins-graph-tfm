#!/usr/bin/env python3
"""
Visualización del grafo G_soc completo (todos los plugins, aristas DEPENDS_ON
y CO_MAINTAINED), coloreado por comunidad de Louvain (p.louvain_soc).
Responde a la rúbrica: "herramientas de visualización para representar grandes
volúmenes de información" (feedback del equipo docente, 2026-10-01).

Salidas:
  figures/grafo_completo_comunidades.png      a 15 cm (memoria), 300 dpi
  figures/grafo_completo_comunidades_hd.png   versión grande para ver con zoom
  data/processed/grafo_completo_resumen.csv   cifras del pie de figura
Layout ForceAtlas2 (networkx), semilla fija.
"""
import os
import sys
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import networkx as nx
import numpy as np
import pandas as pd
from neo4j import GraphDatabase

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _fig_style as fs  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
for line in (ROOT / ".env").read_text().splitlines():
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

drv = GraphDatabase.driver(os.environ["NEO4J_URI"], auth=(os.environ["NEO4J_USER"], os.environ["NEO4J_PASSWORD"]))
with drv.session() as s:
    nodes = s.run("MATCH (p:Plugin) WHERE p.louvain_soc IS NOT NULL "
                  "OPTIONAL MATCH (m:Maintainer)-[:MAINTAINS]->(p) "
                  "RETURN p.component AS c, p.louvain_soc AS comm, coalesce(p.installations,0) AS inst, "
                  "p.plugin_type AS cat, p.name AS name, collect(m.display_name) AS maint").data()
    co = s.run("MATCH (a:Plugin)-[:CO_MAINTAINED]-(b:Plugin) WHERE elementId(a) < elementId(b) "
               "RETURN a.component AS a, b.component AS b").data()
    dep = s.run("MATCH (a:Plugin)-[:DEPENDS_ON]->(b:Plugin) RETURN a.component AS a, b.component AS b").data()
drv.close()

G = nx.Graph()
for n in nodes:
    G.add_node(n["c"], comm=n["comm"], inst=n["inst"], cat=n["cat"], name=n["name"], maint=n["maint"])
for kind, rows in (("co", co), ("dep", dep)):
    for e in rows:
        if e["a"] in G and e["b"] in G and e["a"] != e["b"]:
            G.add_edge(e["a"], e["b"], kind=kind)
dep_dir = [(e["a"], e["b"]) for e in dep if e["a"] in G and e["b"] in G and e["a"] != e["b"]]
n_total, e_total = G.number_of_nodes(), G.number_of_edges()
iso = [n for n in G if G.degree(n) == 0]
H = G.subgraph([n for n in G if G.degree(n) > 0]).copy()

pos = nx.forceatlas2_layout(H, max_iter=600, scaling_ratio=2.0, gravity=1.0,
                            strong_gravity=False, seed=42)

sizes = Counter(nx.get_node_attributes(H, "comm").values())
top = [c for c, _ in sizes.most_common(12)]
palette = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b",
           "#e377c2", "#17becf", "#bcbd22", "#393b79", "#ad494a", "#637939"]
col_of = {c: palette[i] for i, c in enumerate(top)}
OTHER = "#b8b8b8"

def dominant(c):
    cats = Counter(H.nodes[n]["cat"] for n in H if H.nodes[n]["comm"] == c)
    k, v = cats.most_common(1)[0]
    return k, v / sum(cats.values())

def draw(path, width_in, height_in, dpi, node_scale, label_pt, edge_lw, below=False):
    fs.apply()
    fig, ax = plt.subplots(figsize=(width_in, height_in))
    xy = np.array([pos[n] for n in H])
    seg = [(pos[a], pos[b]) for a, b in H.edges()]
    from matplotlib.collections import LineCollection
    ax.add_collection(LineCollection(seg, colors="#9a9a9a", linewidths=edge_lw, alpha=0.35, zorder=1))
    order = sorted(H.nodes, key=lambda n: H.nodes[n]["comm"] in col_of)  # grises debajo
    c = [col_of.get(H.nodes[n]["comm"], OTHER) for n in order]
    s = [node_scale * (1 + np.log10(1 + H.nodes[n]["inst"])) for n in order]
    p = np.array([pos[n] for n in order])
    ax.scatter(p[:, 0], p[:, 1], s=s, c=c, linewidths=0, zorder=2)
    ax.autoscale(); ax.set_aspect("equal"); ax.axis("off")
    handles = []
    for i, cm in enumerate(top):
        k, f = dominant(cm)
        handles.append(Line2D([0], [0], marker="o", ls="", color=col_of[cm], markersize=6,
                              label=f"C{i+1}: {fs.num(sizes[cm])} plugins ({k} {fs.num(100*f)} %)"))
    handles.append(Line2D([0], [0], marker="o", ls="", color=OTHER, markersize=6,
                          label=f"Resto: {fs.num(len(sizes)-len(top))} comunidades"))
    kw = (dict(loc="upper center", bbox_to_anchor=(0.5, 0.0), ncol=2, columnspacing=1.0, handletextpad=0.3)
          if below else dict(loc="upper left", bbox_to_anchor=(1.0, 1.0)))
    ax.legend(handles=handles, frameon=False, fontsize=label_pt, title="Comunidad (tipo dominante)",
              title_fontsize=label_pt, **kw)
    fig.savefig(path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)

import json
idx = {n: i for i, n in enumerate(H.nodes)}
rank = {c: i + 1 for i, (c, _) in enumerate(sizes.most_common())}
export = {
    "nodes": [{"id": n, "name": H.nodes[n]["name"] or n, "cat": H.nodes[n]["cat"], "inst": H.nodes[n]["inst"],
               "comm": rank[H.nodes[n]["comm"]], "maint": H.nodes[n]["maint"],
               "x": round(float(pos[n][0]), 2), "y": round(float(pos[n][1]), 2)} for n in H.nodes],
    "co": [[idx[a], idx[b]] for a, b, d in H.edges(data=True) if d["kind"] == "co"],
    "dep": [[idx[a], idx[b]] for a, b in dep_dir if a in idx and b in idx],
    "isolated": len(iso), "communities": len(sizes),
}
(ROOT / "figures/grafo_completo.json").write_text(json.dumps(export, ensure_ascii=False, separators=(",", ":")))

fig_dir = ROOT / "figures"
draw(fig_dir / "grafo_completo_comunidades.png", fs.TEXT_WIDTH_IN, fs.TEXT_WIDTH_IN * 0.8, 300, 0.9, fs.MIN_PT, 0.15, below=True)
draw(fig_dir / "grafo_completo_comunidades_hd.png", 16, 13, 200, 6, 13, 0.4)

pd.DataFrame([{
    "nodos_g_soc": n_total, "aristas_g_soc": e_total, "aislados_no_dibujados": len(iso),
    "nodos_dibujados": H.number_of_nodes(), "aristas_dibujadas": H.number_of_edges(),
    "comunidades_dibujadas": len(sizes), "top12_plugins": sum(sizes[c] for c in top),
}]).to_csv(ROOT / "data/processed/grafo_completo_resumen.csv", index=False)
print(open(ROOT / "data/processed/grafo_completo_resumen.csv").read())
for i, cm in enumerate(top):
    print(f"C{i+1}", cm, sizes[cm], dominant(cm))
