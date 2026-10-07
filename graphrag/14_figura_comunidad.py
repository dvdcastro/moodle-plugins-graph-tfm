"""Figura de la evaluacion con preguntas de la comunidad (memoria v4, apartado 5.10).

Uso: python 14_figura_comunidad.py
Lee las etiquetas descegadas y el F1 de citas de results/libres/preguntas_comunidad/
(09_eval_comunidad.py) y escribe figures/comunidad_resultados.png. No llama a la API ni a Neo4j.
Panel A: distribucion de las cinco etiquetas por sistema (33 respuestas cada uno).
Panel B: F1 de citas medio por sistema en las 21 preguntas con citas esperadas.
"""
import sys

import numpy as np
import pandas as pd

import config as C

sys.path.insert(0, str(C.ROOT / "src" / "analyze"))
import _fig_style as S  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

OUT = C.RESULTS / "libres" / "preguntas_comunidad"
SYSTEMS = ("baseline", "vecrel", "graphrag", "t2c")
LAB = {"baseline": "RAG vectorial", "vecrel": "Vectorial +\nrelaciones", "graphrag": "KG-RAG",
       "t2c": "Text-to-Cypher"}
LABELS = [("correcta", "Correcta", "#2f5d68"), ("abstencion_correcta", "Abstención correcta", "#7fa7b0"),
          ("parcial", "Parcial", "#d9b26b"), ("incorrecta", "Incorrecta", "#b4553f"),
          ("abstencion_incorrecta", "Abstención incorrecta", "#c9c3b8")]


def main():
    lab = pd.read_csv(OUT / "etiquetas_descegadas.csv")
    f1 = pd.read_csv(OUT / "metrics_per_question.csv")
    cnt = lab.groupby(["system", "etiqueta"]).size().unstack(fill_value=0)
    assert all(cnt.loc[s].sum() == 33 for s in SYSTEMS)
    acc = {s: int(cnt.loc[s].get("correcta", 0) + cnt.loc[s].get("abstencion_correcta", 0)) for s in SYSTEMS}
    assert [acc[s] for s in SYSTEMS] == [15, 15, 15, 19], acc
    f1m = {s: f1[f1.system == s].f1.mean() for s in SYSTEMS}
    assert [round(f1m[s], 2) for s in SYSTEMS] == [0.81, 0.88, 0.73, 0.69], f1m

    S.apply()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(S.TEXT_WIDTH_IN - 0.25, 4.0),
                                   gridspec_kw=dict(width_ratios=[2.3, 1]), sharey=True)
    y = np.arange(len(SYSTEMS))[::-1]
    left = np.zeros(len(SYSTEMS))
    for k, name, col in LABELS:
        v = np.array([cnt.loc[s].get(k, 0) for s in SYSTEMS], dtype=float)
        ax1.barh(y, v, left=left, color=col, height=0.62, label=name, edgecolor="white", linewidth=0.5)
        left += v
    for yi, s in zip(y, SYSTEMS):
        ax1.plot([acc[s]] * 2, [yi - 0.36, yi + 0.36], color="black", lw=1.2)
        ax1.text(acc[s] + 0.3, yi + 0.4, f"{acc[s]} aceptables ({S.num(100 * acc[s] / 33, 0)} %)",
                 fontsize=9, va="bottom", ha="left")
    ax1.set_yticks(y, [LAB[s] for s in SYSTEMS])
    ax1.set_xlim(0, 33)
    ax1.set_xlabel("Respuestas (33 preguntas)")
    ax1.set_title("A. Etiquetas del juicio ciego", loc="left")

    ax2.barh(y, [f1m[s] for s in SYSTEMS], color="#2f5d68", height=0.62)
    for yi, s in zip(y, SYSTEMS):
        ax2.text(f1m[s] + 0.02, yi, S.num(f1m[s], 2), va="center", fontsize=9)
    ax2.set_xlim(0, 1.1)
    ax2.xaxis.set_major_formatter(S.comma_formatter(1))
    ax2.set_xlabel("Media por pregunta (n = 21)")
    ax2.set_title("B. F1 de citas", loc="left")
    for ax in (ax1, ax2):
        ax.spines[["top", "right"]].set_visible(False)
    h, l = ax1.get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", bbox_to_anchor=(0.5, 0.0), ncol=3, frameon=False, fontsize=9)
    fig.tight_layout(rect=(0, 0.12, 1, 1))
    S.save(fig, C.ROOT / "figures" / "comunidad_resultados.png")


if __name__ == "__main__":
    main()
