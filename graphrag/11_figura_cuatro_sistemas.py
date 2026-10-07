"""Figura de resultados con preguntas de plantilla para los CUATRO sistemas (memoria v4).

Uso: python 11_figura_cuatro_sistemas.py
Lee results/text2cypher/metrics_per_question.csv (generado por 07_evaluate_t2c.py,
que puntua los cuatro sistemas con el mismo score() de 05_evaluate.py) y
sustituye figures/graphrag_resultados.png, que en v1.0.1 solo mostraba tres
sistemas (05_evaluate.py --figure). No llama a la API ni a Neo4j.

Panel superior: recall@20 del contexto. Text-to-Cypher no recupera un top-20 (su
"contexto" son las filas devueltas), asi que no se dibuja en ese panel.
Panel inferior: F1 de citas, los cuatro sistemas.
"""
import sys

import numpy as np
import pandas as pd

import config as C

sys.path.insert(0, str(C.ROOT / "src" / "analyze"))
import _fig_style as S  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

SYSTEMS = ("baseline", "vecrel", "graphrag", "t2c")
COL = {"baseline": "#b8b0a4", "vecrel": "#c98b3b", "graphrag": "#2f5d68", "t2c": "#8c5a8f"}
LAB = {"baseline": "RAG vectorial", "vecrel": "Vectorial + relaciones", "graphrag": "KG-RAG",
       "t2c": "Text-to-Cypher"}
REL = ["T1", "T2", "T3", "T4"]
GROUPS = [("T1", ["T1"]), ("T2", ["T2"]), ("T3", ["T3"]), ("T4", ["T4"]), ("T1–T4", REL), ("T6", ["T6"])]
NAME = {"T1": "T1\nDepend.", "T2": "T2\nDepend.\n+ estado", "T3": "T3\nCo-mant.",
        "T4": "T4\nComun.\nfrágil", "T1–T4": "T1–T4\nagregado", "T6": "T6\nControl\nsemántico"}


def main():
    df = pd.read_csv(C.RESULTS / "text2cypher" / "metrics_per_question.csv")
    df = df[df.system.isin(SYSTEMS)]
    for sy in SYSTEMS:
        assert (df.system == sy).sum() == 30, sy
    # comprobacion contra las cifras citadas en la memoria (T1-T4)
    f1_rel = {sy: df[(df.system == sy) & df.type.isin(REL)].f1.mean() for sy in SYSTEMS}
    assert [round(f1_rel[s], 2) for s in SYSTEMS] == [0.32, 0.47, 0.96, 0.71], f1_rel

    S.apply()
    fig, axes = plt.subplots(2, 1, figsize=(S.TEXT_WIDTH_IN - 0.05, 5.6), sharex=True)
    x = np.arange(len(GROUPS), dtype=float)
    x[-2:] += 0.35
    w = 0.2
    for ax, metric, title, systems in (
            (axes[0], "recall_at_k", "Recuperación: recall@20 del contexto (sin text-to-Cypher)",
             SYSTEMS[:3]),
            (axes[1], "f1", "Respuesta: F1 de citas", SYSTEMS)):
        for j, sy in enumerate(SYSTEMS):
            if sy not in systems:
                continue
            off = (j - (len(SYSTEMS) - 1) / 2) * w
            vals = np.array([df[(df.system == sy) & df.type.isin(ts)][metric].mean() for _, ts in GROUPS])
            ax.bar(x + off, vals, w, color=COL[sy], label=LAB[sy],
                   edgecolor="black" if sy == "vecrel" else "none", linewidth=0.4)
            if metric == "f1":
                for xi, v in zip(x, vals):
                    ax.text(xi + off, v + 0.02, S.num(v, 2), ha="center", va="bottom", fontsize=9, rotation=90)
        ax.axvline((x[3] + x[4]) / 2, color="#999999", lw=0.6, ls=":")
        ax.set_title(title, loc="left")
        ax.set_ylim(0, 1.32 if metric == "f1" else 1.05)
        ax.set_yticks(np.arange(0, 1.01, 0.25))
        ax.yaxis.set_major_formatter(S.comma_formatter(2))
        ax.spines[["top", "right"]].set_visible(False)
        ax.set_ylabel("Media por pregunta")
    n = {g: df[(df.system == "baseline") & df.type.isin(ts)].id.nunique() for g, ts in GROUPS}
    axes[1].set_xticks(x, [f"{NAME[g]}\nn = {n[g]}" for g, _ in GROUPS])
    h, l = axes[1].get_legend_handles_labels()
    fig.legend(h, l, loc="upper center", bbox_to_anchor=(0.5, 1.0), ncol=2, frameon=False)
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    S.save(fig, C.FIG)
    print({s: round(v, 3) for s, v in f1_rel.items()})


if __name__ == "__main__":
    main()
