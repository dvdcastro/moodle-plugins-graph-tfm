#!/usr/bin/env python3
"""
Genera dos figuras de pipeline para la memoria (paso a paso, no resultados):
(A) recoleccion de datos (scraping, Fases 0/1/7) y (B) ETL de carga del grafo
(extract/transform-incl.limpieza/load/derive, Fase 2). Mismo estilo visual
que Figura 1 (matplotlib, sin dependencias nuevas).

v2 (2026-09-13): corrige texto desbordando los recuadros inferiores de la
figura ETL (matplotlib `wrap=True` envuelve segun el ancho de la FIGURA, no
del FancyBboxPatch que lo contiene -- por eso el texto largo se salia del
recuadro). Se reemplaza por saltos de linea manuales (`\\n`) dimensionados al
ancho real del recuadro, con recuadros mas anchos y una figura ligeramente
mas alta para dar espacio a las dos lineas.
v3 (2026-09-28, pase de legibilidad del 2do borrador): el tutor señaló letra
demasiado pequeña. Las figuras se dibujan ahora a su ancho FINAL en la página
(`_fig_style.TEXT_WIDTH_IN`) con coordenadas en pulgadas (1 unidad = 1 in),
de modo que los puntos del código son los puntos impresos (mín. 9 pt). Los
recuadros se reorganizaron y los textos se re-envolvieron a mano para ese
ancho; ningún número cambió.
"""
import sys
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _fig_style as fs  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
FIGURES = ROOT / "figures"
FIGURES.mkdir(exist_ok=True)

COLOR_BOX = "#eef3f6"
COLOR_EDGE = "#2f5d68"
COLOR_TEXT = "#262220"
COLOR_ACCENT = "#2f5d68"
COLOR_WARN = "#a8741c"
COLOR_DOTTED = "#9aa5b1"

fs.apply()
W = fs.TEXT_WIDTH_IN


def new_canvas(height_in, title):
    """Figura al ancho final; eje = lienzo completo, 1 unidad = 1 pulgada."""
    fig = plt.figure(figsize=(W, height_in))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(0, height_in)
    ax.axis("off")
    ax.text(W / 2, height_in - 0.05, title, ha="center", va="top", fontsize=11,
            fontweight="bold", color=COLOR_TEXT)
    return fig, ax


def draw_box(ax, xy, w, h, title, subtitle, color=COLOR_BOX, edge=COLOR_EDGE,
             title_size=9.5, subtitle_size=9, gap=0.08):
    """Recuadro con título (negrita) y subtítulo apilados y centrados en bloque."""
    x, y = xy
    box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.06",
                         linewidth=1.2, edgecolor=edge, facecolor=color, zorder=2)
    ax.add_patch(box)
    line_in = 1.22 / 72  # alto de línea por punto de fuente, en pulgadas
    n_t = title.count("\n") + 1
    n_s = (subtitle.count("\n") + 1) if subtitle else 0
    h_t = n_t * title_size * line_in
    h_s = n_s * subtitle_size * line_in
    total = h_t + (gap + h_s if subtitle else 0)
    top = y + h / 2 + total / 2
    ax.text(x + w / 2, top, title, ha="center", va="top", fontsize=title_size,
            fontweight="bold", color=COLOR_TEXT, zorder=3, linespacing=1.1)
    if subtitle:
        ax.text(x + w / 2, top - h_t - gap, subtitle, ha="center", va="top",
                fontsize=subtitle_size, color=COLOR_TEXT, zorder=3, linespacing=1.1)


def draw_arrow(ax, start, end, color=COLOR_EDGE, style="-"):
    arrow = FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=11,
                            linewidth=1.1, color=color, linestyle=style, zorder=1,
                            shrinkA=0, shrinkB=0)
    ax.add_patch(arrow)


# ---------- FIGURA: pipeline de recolección (scraping) ----------
H = 3.40
fig, ax = new_canvas(H, "Pipeline de recolección de datos")
GAP = 0.22
BW = (W - 2 * GAP - 0.04) / 3
BH = 1.0
Y1 = H - 0.40 - BH
xs = [0.02 + i * (BW + GAP) for i in range(3)]
boxes = [
    (xs[0], Y1, "1. Feed oficial\npluglist.php", "1 GET · 2.888 plugins\n21.734 versiones\nchecksum"),
    (xs[1], Y1, "2. Marketplace\n(por componente)", "mantenedores +\ninstalaciones\n1 petición cada 10 s"),
    (xs[2], Y1, "3. version.php\n(GitHub / ZIP)", "dependencias declaradas\n2 fuentes de lectura"),
]
Y2 = Y1 - 0.26 - BH
boxes.append((xs[1], Y2, "4. Marketplace /stats\n(serie histórica)", "series mensuales de\ninstalaciones 2012–2026"))
for x, y, t, s in boxes:
    draw_box(ax, (x, y), BW, BH, t, s)
CH = 0.50
draw_box(ax, (0.02, 0.03), W - 0.04, CH,
         "Caché local + checksum por archivo", "resumible: cada script salta lo ya descargado",
         title_size=9.5, subtitle_size=9, gap=0.04)

draw_arrow(ax, (xs[0] + BW, Y1 + BH / 2), (xs[1], Y1 + BH / 2))
draw_arrow(ax, (xs[1] + BW, Y1 + BH / 2), (xs[2], Y1 + BH / 2))
draw_arrow(ax, (xs[1] + BW / 2, Y1), (xs[1] + BW / 2, Y2 + BH))
for x, y, *_ in (boxes[0], boxes[2], boxes[3]):
    draw_arrow(ax, (x + BW / 2, y), (x + BW / 2, 0.03 + CH + 0.02), color=COLOR_DOTTED, style=":")

fs.save(fig, FIGURES / "pipeline_recoleccion.png")
print("saved: pipeline_recoleccion.png")
plt.close(fig)

# ---------- FIGURA: pipeline ETL de carga del grafo ----------
H = 4.10
fig, ax = new_canvas(H, "Pipeline ETL de carga del grafo")
GAP = 0.16
widths = [1.20, 1.55, 1.35, 1.35]
scale = (W - 0.04 - 3 * GAP) / sum(widths)
widths = [w * scale for w in widths]
BH = 1.35
Y1 = H - 0.40 - BH
x = 0.02
etl = []
for w, (t, s) in zip(widths, [
    ("EXTRACT", "JSONL/CSV\ncrudos de cada\nfuente"),
    ("TRANSFORM\n(incl. limpieza)", "parseo version.php\n3 errores propios\ncorregidos · tipos\nstring↔int ·\ndeduplicación"),
    ("LOAD", "Cypher MERGE →\nnodos + relaciones\nobservadas"),
    ("DERIVE", "relaciones\nderivadas sobre\nel grafo ya\ncargado"),
]):
    draw_box(ax, (x, Y1), w, BH, t, s)
    etl.append((x, w))
    x += w + GAP
for (xa, wa), (xb, _) in zip(etl[:-1], etl[1:]):
    draw_arrow(ax, (xa + wa, Y1 + BH / 2), (xb, Y1 + BH / 2))

# (v3: la nota ambar "ANY_VERSION · $module-> legacy · subdir en URL (bugs propios
# detectados y corregidos)" se movio al pie de figura, ver docs/figuras.md)

# Recuadros inferiores (detalle de LOAD y DERIVE)
BH2 = 1.30
Y2 = 0.03
LW = 2.95
load_x, der_x = 0.02, 0.02 + LW + 0.18
der_w = W - 0.02 - der_x
draw_box(ax, (load_x, Y2), LW, BH2, "Plugin · Maintainer · Category\nMoodleRelease · Set",
         "MAINTAINS 4.111 · DEPENDS_ON 741\nSUPPORTS 25.710 · IN_CATEGORY 2.888\nPART_OF 383",
         title_size=10)
draw_box(ax, (der_x, Y2), der_w, BH2, "CO_MAINTAINED\nCO_MAINTAINS\nSAME_CATEGORY",
         "15.123 + 838 + 419.831 aristas\nponderadas (se calculan sobre el\ngrafo ya cargado: no se\nre-descarga nada)",
         color="#e4eeef", title_size=10)
lx, lw = etl[2]
dx, dw = etl[3]
draw_arrow(ax, (lx + lw / 2, Y1), (load_x + LW * 0.72, Y2 + BH2))
draw_arrow(ax, (dx + dw / 2, Y1), (der_x + der_w * 0.6, Y2 + BH2))

fs.save(fig, FIGURES / "pipeline_etl.png")
print("saved: pipeline_etl.png")
plt.close(fig)
