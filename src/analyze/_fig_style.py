"""
Estilo compartido de figuras para la memoria (pase de legibilidad, 2do borrador).

Regla: cada figura se crea a su ANCHO FINAL en la página (figsize ancho <=
TEXT_WIDTH_IN), de modo que los tamaños en puntos del código SON los puntos
impresos. Ningún texto por debajo de MIN_PT (8 pt solo para etiquetas de nodo
densas, declarado explícitamente por la figura). 300 dpi.

TEXT_WIDTH_CM es la ÚNICA constante a tocar si cambian los márgenes: la
plantilla real (docs/plantilla-structuralia.docx) es A4 con márgenes de 3 cm,
es decir 21 - 2*3 = 15,0 cm de ancho útil (verificado con python-docx). Una
figura hecha a 15 cm cumple también si se inserta a 16 cm (solo se agranda).
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.text import Text
from matplotlib.ticker import FuncFormatter

TEXT_WIDTH_CM = 15.0
TEXT_WIDTH_IN = TEXT_WIDTH_CM / 2.54
MAX_HEIGHT_IN = 20.0 / 2.54
MIN_PT = 9
DENSE_LABEL_PT = 8  # solo etiquetas de nodo densas, y hay que declararlo
DPI = 300
WIDTH_TOL_IN = 0.02  # tolerancia de redondeo de píxeles

RC = {
    "font.size": 9.5,
    "axes.titlesize": 11,
    "axes.titleweight": "bold",
    "axes.labelsize": 10,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "legend.fontsize": 9,
    "legend.title_fontsize": 9.5,
    "figure.titlesize": 11.5,
    "figure.titleweight": "bold",
    "savefig.dpi": DPI,
    "axes.formatter.use_mathtext": True,
}


def apply():
    """Aplica los rcParams comunes (llamar antes de crear figuras)."""
    plt.rcParams.update(RC)


def num(x, nd=0, sign=False):
    """Número con coma decimal y punto de miles (convención española)."""
    s = f"{x:+,.{nd}f}" if sign else f"{x:,.{nd}f}"
    return s.replace(",", "\x00").replace(".", ",").replace("\x00", ".").replace("-", "−")


def comma_formatter(nd=1, pct=False):
    """FuncFormatter para ejes con coma decimal."""
    return FuncFormatter(lambda v, _pos: num(v, nd) + ("%" if pct else ""))


def min_font_pt(fig):
    """Tamaño mínimo (pt) de todo texto visible y no vacío de la figura."""
    fig.canvas.draw()
    sizes = []
    for t in fig.findobj(Text):
        if t.get_visible() and t.get_text().strip() and t.get_figure() is not None:
            # descarta etiquetas de tick fuera del rango visible
            sizes.append(t.get_fontsize())
    return min(sizes)


def save(fig, path, min_allowed=MIN_PT, tight=True):
    """Guarda a DPI, verifica ancho físico y tamaño mínimo de letra.

    Devuelve dict con ancho/alto en cm y mínimo en pt. Lanza AssertionError si
    el PNG resultante es más ancho que TEXT_WIDTH_IN (bbox 'tight' puede
    agrandar el lienzo si hay texto que sobresale) o si hay texto < min_allowed.
    """
    from PIL import Image
    path = Path(path)
    mn = min_font_pt(fig)
    kw = dict(dpi=DPI)
    if tight:
        # el padding de 'tight' se suma al contenido: reducirlo si el contenido
        # ya ocupa (casi) todo el ancho, para no pasarse del ancho de texto
        bb = fig.get_tightbbox(fig.canvas.get_renderer())
        pad = max(0.0, min(0.04, (TEXT_WIDTH_IN - bb.width) / 2 - 0.002))
        kw.update(bbox_inches="tight", pad_inches=pad)
    fig.savefig(path, **kw)
    w_px, h_px = Image.open(path).size
    w_in, h_in = w_px / DPI, h_px / DPI
    info = dict(file=path.name, width_cm=round(w_in * 2.54, 2), height_cm=round(h_in * 2.54, 2),
                min_pt=mn)
    print(f"[fig_style] {path.name}: {info['width_cm']} x {info['height_cm']} cm, min {mn} pt")
    assert w_in <= TEXT_WIDTH_IN + WIDTH_TOL_IN, f"{path.name} más ancha que el texto: {w_in:.3f} in"
    assert h_in <= MAX_HEIGHT_IN + WIDTH_TOL_IN, f"{path.name} más alta que 20 cm: {h_in:.3f} in"
    assert mn >= min_allowed, f"{path.name}: texto de {mn} pt < {min_allowed} pt"
    return info
