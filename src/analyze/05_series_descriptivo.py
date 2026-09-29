#!/usr/bin/env python3
"""
Fase 7, Item 6 (docs/plan_fase7_analisis.md) - Capitulo descriptivo de series
temporales de instalaciones del Marketplace de Moodle.

Que mide la serie (declararlo explicitamente, no asumirlo): `installs_series`
en `data/processed/stats_series_raw.jsonl` es "Number of sites" reportado por
el Marketplace (marketplace.moodle.com/plugins/{component}/stats) -- SITIOS
REGISTRADOS QUE REPORTAN el plugin via telemetria, NO instalaciones activas
verificadas. Una caida en la serie puede significar que sitios dejaron de
REPORTAR (telemetria desactivada, sitio dado de baja, upgrade que cambio el
mecanismo de reporte), no que alguien desinstalo el plugin. Esta salvedad se
repite en cada figura/leyenda generada aqui, no solo en este docstring
(exigido literalmente por el plan).

Alcance FIJO segun el plan (no opcional):
  - Descriptivo, NO causal. No se argumenta abandono/riesgo desde aqui (eso
    vive en 03_risk.py, indice de riesgo ya existente).
  - 2-3 figuras maximo. Este script produce 2:
      figures/series_cobertura.png      -> cobertura de datos (Regla 1)
      figures/series_declive_agregado.png -> distribucion agregada (Regla 5)
  - Toda cifra de TENDENCIA se calcula sobre la CUOTA del plugin en el total
    mensual del ecosistema (Regla 4), nunca sobre el valor absoluto. Si el
    ecosistema completo cae X%, un plugin que cae X% no tiene declive propio
    que reportar -- por eso se normaliza contra el total del ecosistema por
    mes ANTES de comparar nada entre plugins o en el tiempo.
  - Se EXCLUYEN del calculo de tendencia (no del descriptivo general de
    cobertura) los plugins con serie <24 meses -- sesgo de censura: un plugin
    nuevo con 6 meses de historia no es comparable a uno con 14 anios (Regla
    3). El total del ecosistema, en cambio, SI incluye todos los plugins con
    datos (incluidos los de serie corta) porque esos sitios reportaron de
    verdad ese mes y excluirlos distorsionaria el denominador.
  - NO se usa "declive desde el pico" como metrica principal -- esta sesgada
    por construccion (cualquier serie con ruido tiene, por definicion, un
    "declive" desde su propio maximo historico). En su lugar (Regla 5):
    mediana de la CUOTA en los ultimos 12 meses disponibles vs. mediana de la
    CUOTA en los 12 meses centrados en el mes de cuota maxima historica de
    ESE plugin. Se reporta la DISTRIBUCION agregada de (mediana_reciente -
    mediana_pico) entre plugins -- no una lista de "peores casos" individuales
    presentados como prueba de nada (prohibido explicitamente por el plan).
  - Vocabulario: PERMITIDO "descenso relativo", "perdida de cuota (del
    ecosistema)" / "perdida de cuota de mercado". PROHIBIDO en cualquier
    texto generado por este script: "abandono", "muerte", "obsoleto" (y
    equivalentes en ingles) -- son inferencias causales que un analisis
    puramente descriptivo no puede sostener. Autocheck al final del script:
    se grepean las cadenas de titulo/caption generadas contra la lista de
    palabras prohibidas antes de guardar cualquier figura.

No requiere Neo4j: la entrada es puramente data/processed/stats_series_raw.jsonl
(JSONL producido por src/collect/04_marketplace_stats_scrape.py), procesado con
pandas/numpy y graficado con matplotlib. Se reutiliza ROOT de _gds_utils.py
para no duplicar la resolucion de rutas del repo, pero no se abre ninguna
sesion de driver de Neo4j en este script.

Uso: python3 05_series_descriptivo.py
"""
import json
import re
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _gds_utils import ROOT  # noqa: E402  (solo para ROOT; este script no toca Neo4j)
import _fig_style as fs  # noqa: E402

PROCESSED = ROOT / "data" / "processed"
FIGURES = ROOT / "figures"
FIGURES.mkdir(exist_ok=True)
RAW_PATH = PROCESSED / "stats_series_raw.jsonl"

# Regla 3 del plan (Item 6): umbral de censura para el calculo de tendencia.
MIN_MONTHS_TREND = 24

# Paleta identica a 06_pipeline_figures.py -- mismo estilo visual en toda la
# memoria (teal apagado / gris calido, no los colores por defecto de matplotlib).
COLOR_EDGE = "#2f5d68"       # teal apagado (bordes, barras principales)
COLOR_TEXT = "#262220"       # texto principal
COLOR_ACCENT = "#2f5d68"
COLOR_WARN = "#a8741c"       # ambar apagado (advertencias / notas al pie)
COLOR_BOX = "#eef3f6"        # fondo claro de recuadros
COLOR_TEAL_LIGHT = "#7fa8b0"  # teal claro (barra secundaria)
COLOR_GRAY = "#9aa5b1"       # gris calido (barra terciaria / neutra)

# Regla 6 del plan (Item 6): vocabulario prohibido en cualquier texto generado aqui.
BANNED_WORDS = ["abandono", "abandon", "muerte", "death", "obsoleto", "obsolete"]

# Nota metodologica repetida en cada figura (Regla 2 del plan: telemetria, no
# instalaciones activas verificadas; caracter descriptivo, no causal).
TELEMETRY_FOOTNOTE = (
    "La serie mide sitios registrados que REPORTAN el plugin al Marketplace de Moodle\n"
    "(telemetria), no instalaciones activas verificadas. Analisis descriptivo, no causal."
)


def parse_month(label: str) -> datetime:
    """'Aug 2026' -> datetime(2026, 8, 1). Los labels del Marketplace son mes+anio en
    ingles abreviado; NO se pueden ordenar como string (ej. 'Apr' > 'Aug' lexicograficamente
    pero es un mes anterior) -- se parsean siempre a un objeto datetime real antes de ordenar."""
    return datetime.strptime(label.strip(), "%b %Y")


def load_series():
    """Lee stats_series_raw.jsonl linea a linea y devuelve:
      plugin_series: dict component -> {datetime(mes): installs (int)}
      coverage: dict con los conteos de la Regla 1 (validacion de cobertura)
    """
    plugin_series = {}
    n_total = 0
    n_found = 0
    n_found_nonempty = 0
    n_ge24 = 0

    with open(RAW_PATH) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            n_total += 1
            d = json.loads(line)
            component = d["component"]
            if not d.get("found"):
                continue
            n_found += 1
            series = d.get("installs_series") or {}
            labels = series.get("labels") or []
            datasets = series.get("datasets") or []
            if not labels or not datasets:
                continue
            data = datasets[0].get("data") or []
            if len(data) != len(labels) or len(labels) == 0:
                continue
            n_found_nonempty += 1
            months = [parse_month(l) for l in labels]
            plugin_series[component] = dict(zip(months, data))
            if len(labels) >= MIN_MONTHS_TREND:
                n_ge24 += 1

    coverage = dict(
        n_total=n_total,
        n_found=n_found,
        n_found_nonempty=n_found_nonempty,
        n_ge24=n_ge24,
    )
    return plugin_series, coverage


def build_ecosystem_total(plugin_series: dict) -> pd.Series:
    """Total mensual del ecosistema: suma de installs de TODOS los plugins con serie no
    vacia (incluidos los de <24 meses, Regla 3 -- el total del ecosistema si los incluye,
    solo se excluyen del CALCULO DE TENDENCIA por plugin). Alineado por mes real (datetime),
    no por posicion ni por string, porque cada plugin puede empezar/terminar en un mes distinto."""
    totals = {}
    for series in plugin_series.values():
        for month, installs in series.items():
            totals[month] = totals.get(month, 0) + installs
    s = pd.Series(totals).sort_index()
    return s


def share_series(series: dict, ecosystem_total: pd.Series) -> pd.Series:
    """Convierte la serie absoluta de un plugin en su CUOTA del total del ecosistema por mes
    (Regla 4: toda cifra de tendencia se calcula sobre la cuota, nunca sobre el valor absoluto)."""
    idx = sorted(series.keys())
    vals = [series[m] / ecosystem_total.loc[m] for m in idx]
    return pd.Series(vals, index=idx)


def recent_vs_peak_median(share: pd.Series, window: int = 12):
    """Regla 5: reemplaza 'declive desde el pico' (sesgado por construccion) por:
      - mediana de los ULTIMOS `window` meses disponibles de la cuota del plugin
      - mediana de una ventana de `window` meses CENTRADA en el mes de cuota maxima
        historica de ese mismo plugin
    Si el pico esta cerca del borde de la serie, la ventana centrada se recorta (queda
    con menos de `window` meses) en vez de fallar o de desplazarse fuera de la serie --
    se documenta como limitacion menor, no invalida la comparacion.
    Devuelve (recent_median, peak_median, peak_month) o None si la serie es demasiado corta.
    """
    n = len(share)
    if n < window:
        return None
    recent_median = float(share.iloc[-window:].median())

    peak_pos = int(np.argmax(share.values))
    half = window // 2
    start = max(0, peak_pos - half)
    end = min(n, peak_pos + (window - half))
    peak_median = float(share.iloc[start:end].median())
    peak_month = share.index[peak_pos]

    return recent_median, peak_median, peak_month


def assert_no_banned_words(*texts):
    """Autocheck de la Regla 6: ninguna cadena generada por este script puede contener
    vocabulario prohibido (causal). Falla ruidosamente si algo se cuela."""
    for t in texts:
        low = t.lower()
        for w in BANNED_WORDS:
            if w in low:
                raise AssertionError(
                    f"Palabra prohibida '{w}' encontrada en texto generado: {t!r}"
                )


def main():
    print("=" * 78)
    print("Fase 7, Item 6 -- capitulo descriptivo de series temporales de instalaciones")
    print("=" * 78)

    plugin_series, coverage = load_series()

    # ---- Regla 1: validar cobertura ANTES de calcular nada ----
    n_total = coverage["n_total"]
    n_found_nonempty = coverage["n_found_nonempty"]
    n_ge24 = coverage["n_ge24"]
    frac_nonempty = n_found_nonempty / n_total
    frac_ge24_of_nonempty = n_ge24 / n_found_nonempty if n_found_nonempty else 0.0
    frac_ge24_of_total = n_ge24 / n_total

    print("\n[cobertura] (Regla 1 -- obligatorio validar antes de calcular tendencias)")
    print(f"  lineas totales en stats_series_raw.jsonl: {n_total}")
    print(f"  found=true: {coverage['n_found']} ({coverage['n_found']/n_total*100:.1f}%)")
    print(f"  found=true CON installs_series no vacia: {n_found_nonempty}/{n_total} "
          f"({frac_nonempty*100:.1f}%)")
    print(f"  de esos, con serie >=24 meses (umbral de censura, Regla 3): "
          f"{n_ge24}/{n_found_nonempty} ({frac_ge24_of_nonempty*100:.1f}% del subconjunto con datos; "
          f"{frac_ge24_of_total*100:.1f}% del total de {n_total})")

    if frac_nonempty < 0.90:
        print(f"  *** WARNING: cobertura de datos utilizables ({frac_nonempty*100:.1f}%) por debajo "
              f"del 90% -- revisar el scraping antes de confiar en cualquier cifra downstream ***")
    if frac_ge24_of_nonempty < 0.50:
        print(f"  *** WARNING: menos de la mitad de los plugins con datos tienen >=24 meses de "
              f"historia ({frac_ge24_of_nonempty*100:.1f}%) -- el calculo de tendencia (Regla 3) "
              f"quedaria con una muestra chica/sesgada hacia plugins viejos ***")

    # ---- Regla 4: total mensual del ecosistema (para calcular CUOTA, nunca absolutos) ----
    ecosystem_total = build_ecosystem_total(plugin_series)
    print(f"\n[ecosistema] total mensual construido sobre {len(plugin_series)} plugins con serie "
          f"no vacia, {len(ecosystem_total)} meses distintos "
          f"({ecosystem_total.index.min():%b %Y} a {ecosystem_total.index.max():%b %Y})")

    # ---- Reglas 3+4+5: calculo de tendencia SOLO sobre plugins con >=24 meses, sobre CUOTA ----
    diffs = []
    rows = []
    for component, series in plugin_series.items():
        if len(series) < MIN_MONTHS_TREND:
            continue
        share = share_series(series, ecosystem_total)
        result = recent_vs_peak_median(share, window=12)
        if result is None:
            continue
        recent_median, peak_median, peak_month = result
        diff = recent_median - peak_median
        diffs.append(diff)
        rows.append(dict(
            component=component,
            n_months=len(series),
            recent_median_share=recent_median,
            peak_median_share=peak_median,
            peak_month=peak_month.strftime("%b %Y"),
            diff_share=diff,
        ))

    trend_df = pd.DataFrame(rows).sort_values("diff_share")
    trend_df.to_csv(PROCESSED / "series_descriptivo_trend.csv", index=False)

    diffs_arr = np.array(diffs)
    n_trend = len(diffs_arr)
    q1, median_diff, q3 = np.percentile(diffs_arr, [25, 50, 75])
    mean_diff = float(diffs_arr.mean())

    print(f"\n[tendencia agregada] (Regla 5 -- mediana ultimos 12m vs. mediana 12m centrados en el "
          f"pico de CUOTA, NUNCA 'declive desde el pico') sobre N={n_trend} plugins con serie "
          f">=24 meses")
    print(f"  diferencia (mediana_reciente - mediana_pico), en puntos de cuota (fraccion, no %):")
    print(f"    media   = {mean_diff:+.6f}")
    print(f"    Q1      = {q1:+.6f}")
    print(f"    mediana = {median_diff:+.6f}")
    print(f"    Q3      = {q3:+.6f}")
    print(f"  en puntos porcentuales de cuota del ecosistema: media={mean_diff*100:+.3f} pp, "
          f"mediana={median_diff*100:+.3f} pp, Q1={q1*100:+.3f} pp, Q3={q3*100:+.3f} pp")
    n_neg = int((diffs_arr < 0).sum())
    n_pos = int((diffs_arr > 0).sum())
    n_zero = n_trend - n_neg - n_pos
    print(f"  {n_neg}/{n_trend} ({n_neg/n_trend*100:.1f}%) con perdida de cuota relativa "
          f"(diferencia negativa); {n_pos}/{n_trend} con ganancia; {n_zero} sin cambio exacto")

    # =====================================================================
    # Pase de legibilidad (2026-09-28): figuras al ancho final de pagina
    # (_fig_style.TEXT_WIDTH_IN), letra >= 9 pt, coma decimal. Las notas al pie
    # que antes se incrustaban en la imagen con fig.text(...) a 7,6 pt se
    # conservan en fig1_caption / fig2_caption (siguen pasando el autocheck de
    # la Regla 6) pero ya NO se dibujan: su texto va al pie de figura del
    # documento (ver docs/figuras.md).
    # =====================================================================
    fs.apply()

    # =====================================================================
    # FIGURA 1: series_cobertura.png -- cobertura de datos (Regla 1)
    # =====================================================================
    fig1_title = "Cobertura de datos de series de instalaciones\n(Marketplace de Moodle)"
    fig1_caption = (
        f"{n_total} plugins en el directorio oficial. {TELEMETRY_FOOTNOTE}\n"
        f"Plugins con serie <24 meses se describen aqui pero se excluyen del calculo de\n"
        f"tendencia (sesgo de censura, Regla 3 del plan Fase 7)."
    )
    assert_no_banned_words(fig1_title, fig1_caption)

    cats = ["Total plugins\n(directorio)", "Con serie de\ninstalaciones", "Serie ≥24 meses\n(usados en\ntendencia)"]
    vals = [n_total, n_found_nonempty, n_ge24]
    colors = [COLOR_GRAY, COLOR_TEAL_LIGHT, COLOR_EDGE]

    fig, ax = plt.subplots(figsize=(fs.TEXT_WIDTH_IN * 0.8, 3.6))
    bars = ax.bar(cats, vals, color=colors, edgecolor=COLOR_TEXT, linewidth=0.8, width=0.6)
    for bar, v in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width() / 2, v + n_total * 0.015,
                f"{fs.num(v)}\n({fs.num(v / n_total * 100, 1)} %)",
                ha="center", va="bottom", fontsize=9.5, color=COLOR_TEXT)
    ax.set_ylim(0, n_total * 1.22)
    ax.yaxis.set_major_formatter(fs.comma_formatter(0))
    ax.set_ylabel("Número de plugins", color=COLOR_TEXT)
    ax.set_title(fig1_title, color=COLOR_TEXT, pad=8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(colors=COLOR_TEXT)
    fig.tight_layout()
    fs.save(fig, FIGURES / "series_cobertura.png")
    plt.close(fig)
    print("\n[figura] guardada: figures/series_cobertura.png")

    # =====================================================================
    # FIGURA 2: series_declive_agregado.png -- distribucion agregada (Regla 5)
    # =====================================================================
    fig2_title = "Variación agregada de la cuota de instalaciones:\nmediana reciente frente a mediana en el pico"
    fig2_caption = (
        f"N={n_trend} plugins con serie >=24 meses. Cuota = instalaciones del plugin / total\n"
        f"mensual del ecosistema (nunca valor absoluto). {TELEMETRY_FOOTNOTE}\n"
        f"Distribucion agregada, no casos individuales; descenso relativo o perdida de cuota\n"
        f"del ecosistema, sin inferencia causal."
    )
    assert_no_banned_words(fig2_title, fig2_caption)

    diffs_pp = diffs_arr * 100  # puntos porcentuales de cuota

    # v1 (histograma lineal, rango completo): ~90% del area en blanco, cola invisible.
    # v2 (recorte percentil 1-99, lineal): oculta la cola, que es la senial mas interesante.
    # v3 (symlog + bins log-espaciados): muestra el rango completo, pero un histograma sigue
    #    graficando CONTEO CRUDO sobre bins de ancho muy desigual (0,004pp cerca de 0 vs. 1,5pp
    #    en la cola) -- el bin central (1.187/2.145 = 55,3% de los plugins, |diff|<=0,01pp) se ve
    #    como una pared que domina visualmente sobre bins de cola dispersos con 1-2 plugins cada
    #    uno, un artefacto de binning que se leyo como un "salto"/outlier inexistente (David,
    #    14/09/2026 -- investigado con un agente dedicado antes de decidir el cambio: confirmado
    #    que el caso mas extremo, un unico plugin, SI es real -- z=-22,5, ~131x el RIC por debajo
    #    de Q1, sin ningun caso comparable cerca -- pero el "salto" visual central es el artefacto
    #    de binning, no el outlier).
    # v4 (esta version, ECDF -- funcion de distribucion acumulada empirica): no usa bins, por lo
    #    tanto no puede producir ningun artefacto de binning. El caso extremo real aparece como un
    #    unico escalon aislado en el extremo izquierdo (visible y anotado, no oculto), y la
    #    concentracion real cerca de cero se ve como un ascenso empinado suave, no como una pared.
    extreme = trend_df.iloc[0]  # trend_df ya esta ordenado por diff_share ascendente
    diffs_sorted = np.sort(diffs_pp)
    ecdf_y = np.arange(1, len(diffs_sorted) + 1) / len(diffs_sorted)

    fig, ax = plt.subplots(figsize=(fs.TEXT_WIDTH_IN, 4.4))
    ax.plot(diffs_sorted, ecdf_y, color=COLOR_EDGE, linewidth=1.8)
    ax.axvline(0, color=COLOR_TEXT, linewidth=1.0, linestyle="-")
    ax.axvline(median_diff * 100, color=COLOR_WARN, linewidth=1.6, linestyle="--",
               label=f"mediana = {fs.num(median_diff * 100, 3, sign=True)} pp")
    ax.annotate(
        f"{extreme['component']}\n({fs.num(extreme['diff_share'] * 100, 2, sign=True)} pp)",
        xy=(diffs_sorted[0], ecdf_y[0]), xytext=(diffs_sorted[0] * 0.8, 0.16),
        fontsize=9, color=COLOR_WARN, ha="left", va="bottom",
        arrowprops=dict(arrowstyle="-", color=COLOR_WARN, linewidth=0.9),
    )
    ax.set_xscale("symlog", linthresh=0.01)
    ax.set_xlabel("Mediana últimos 12 meses − mediana 12 meses centrados en el pico\n"
                  "(pp de cuota, escala logarítmica simétrica)", color=COLOR_TEXT)
    ax.set_ylabel("Fracción acumulada de plugins\n(ECDF)", color=COLOR_TEXT)
    ax.set_title(fig2_title, color=COLOR_TEXT, pad=8)
    ax.legend(frameon=True, facecolor="white", edgecolor="none",
              framealpha=0.9, loc="lower right")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(colors=COLOR_TEXT)
    ax.yaxis.set_major_formatter(fs.comma_formatter(1))
    ax.set_ylim(-0.02, 1.02)
    fig2_caption += (
        f"\nFuncion de distribucion acumulada empirica (ECDF), sin binning -- evita cualquier\n"
        f"artefacto visual de agrupar en intervalos (una version anterior con histograma y bins\n"
        f"logaritmicos generaba un 'salto' donde en realidad solo habia un bin muy angosto con el\n"
        f"55% de los plugins junto a bins de cola muy anchos y dispersos). El caso mas extremo\n"
        f"real queda anotado explicitamente, no oculto ni recortado."
    )
    assert_no_banned_words(fig2_caption)
    fig.tight_layout()
    fs.save(fig, FIGURES / "series_declive_agregado.png")
    plt.close(fig)
    print("[figura] guardada: figures/series_declive_agregado.png")
    print(f"  (ECDF, sin binning, rango completo {diffs_pp.min():.3f} a {diffs_pp.max():.3f} pp)")
    print(f"  (caso mas extremo: {extreme['component']}, diff={extreme['diff_share']*100:.3f}pp)")

    print(f"\n[csv] tabla completa por plugin (N={n_trend}) -> data/processed/series_descriptivo_trend.csv")
    print("\nOK -- 05_series_descriptivo.py termino sin errores.")


if __name__ == "__main__":
    main()
