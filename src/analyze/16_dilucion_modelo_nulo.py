#!/usr/bin/env python3
"""
Modelo nulo de dilucion para la perdida de cuota de instalaciones (seccion 5.5).

Pregunta (comentario del tutor sobre el borrador 2): el 91,9% de los plugins con
>=24 meses de serie (N=2.145) pierde cuota del ecosistema entre su pico y los
ultimos 12 meses (metrica de 05_series_descriptivo.py). La cuota suma 1 por
definicion y el ecosistema crece ~46 veces con entrada masiva de plugins nuevos,
de modo que casi todos los plugins existentes DEBEN perder cuota aunque crezcan.
?Respalda eso la frase "el crecimiento se concentra en una minoria de plugins",
o es pura dilucion?

Este script separa las dos cosas. No modifica 05_series_descriptivo.py: importa
sus funciones (carga de la serie, total del ecosistema, cuota) y reproduce su
metrica en numpy, con un assert de que coincide exactamente.

Parte A -- ?de donde sale el 91,9%? (misma metrica, mismos N=2.145 plugins)
  A0  Observado: mediana de la cuota en los ultimos 12 meses menos mediana en
      los 12 meses centrados en el pico de cuota (identico a 05).
  A1  Crecimiento al ritmo del ecosistema: si cada plugin creciera exactamente
      como el total, su cuota seria constante y nadie perderia cuota (0%,
      analitico, no requiere simulacion). Cota inferior trivial.
  A2  Sin crecimiento: las instalaciones absolutas de cada plugin se congelan
      en la mediana de su ventana de pico desde el final de esa ventana. Cota
      superior: cuanto perderia cuota solo porque el denominador crece.
  A3  Sin dilucion por entrada: la cuota de cada plugin se calcula sobre el
      total de los plugins que ya existian cuando el entro (su cohorte de
      entrada y las anteriores), eliminando del denominador a todos los que
      entraron despues. Lo que queda negativo aqui es perdida frente a sus
      contemporaneos, no frente a los recien llegados.
  A4  Artefacto de seleccion del pico: se permuta en el tiempo la serie de
      cuota de cada plugin (sin tendencia, mismo ruido marginal) y se recalcula
      la metrica. Mide cuanto "pierde cuota" una serie estacionaria solo porque
      la ventana de referencia se centra en su maximo. 200 replicas.
  A5  Descomposicion del crecimiento del total: base = media mensual sep 2012 -
      ago 2013, reciente = media mensual de los ultimos 12 meses. Incumbentes =
      plugins con algun reporte en la ventana base; entrantes = el resto. Es
      aditiva exacta (meses sin reporte = 0).

Parte B -- ?esta concentrado el crecimiento ABSOLUTO mas alla de un modelo nulo?
  Poblacion principal: los mismos N=2.145. Para cada plugin, x0 = mediana de sus
  primeros 12 meses reportados, x1 = mediana de sus ultimos 12, ganancia
  g = x1 - x0, tasa anualizada r = ln(x1/x0)/d (d = anios entre los centros de
  ambas ventanas). Metricas de concentracion de g:
    - fraccion de la ganancia neta total que capturan el top 1/5/10% de
      plugins (ordenados por g);
    - fraccion minima de plugins que acumula el 50% de la ganancia neta;
    - Gini de g (diferencia media absoluta / (2*media); con ganancias
      negativas puede exceder 1, se usa solo para comparar con el nulo).
  Nulos:
    B0  Proporcional (Gibrat sin ruido): todos crecen a la misma tasa
        anualizada r*, elegida para reproducir la ganancia neta total
        observada. La concentracion de g refleja solo la de los tamanios
        iniciales.
    B1  Gibrat con ruido (permutacion): se permutan las tasas anualizadas
        observadas entre plugins DEL MISMO ANIO DE ENTRADA (duraciones
        comparables; permutar entre estratos aplicaria la tasa de un plugin
        de 2 anios durante 13 y haria explotar el nulo) y cada plugin las
        aplica a su x0 y su propia duracion. 1.000 permutaciones, semilla
        fija. Conserva tamanios y tasas, rompe la asociacion tamanio-tasa.
        Se dan p empiricos en las dos direcciones (mas y menos concentrado).
  Sensibilidad: dos cohortes fijas de incumbentes con reporte en los 12 meses
  de la ventana base (sep 2012 - ago 2013, coincide con el despliegue de la
  telemetria; sep 2015 - ago 2016, base estable), media de la ventana base
  frente a media de los ultimos 12 meses (meses sin reporte = 0), mismo test
  con factores de crecimiento permutados, y ademas la fraccion de plugins que
  crece menos que el agregado de su cohorte (= pierde cuota dentro de ella)
  observada frente a la del nulo B1.

Salida: docs/dilucion_modelo_nulo.md (generado, no editar a mano) y
        figures/dilucion_modelo_nulo.png.
No requiere Neo4j. Determinista (semillas fijas).
Uso: python3 16_dilucion_modelo_nulo.py
"""
import importlib
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _gds_utils import ROOT  # noqa: E402
import _fig_style as fs  # noqa: E402

s05 = importlib.import_module("05_series_descriptivo")

FIGURES = ROOT / "figures"
DOC_PATH = ROOT / "docs" / "dilucion_modelo_nulo.md"
SEED = 20261004
N_PERM_TIME = 200     # A4
N_PERM_GROWTH = 1000  # B1
WINDOW = 12
TOP_PCTS = (1, 5, 10)
BASE_START, BASE_END = pd.Timestamp("2012-09-01"), pd.Timestamp("2013-08-01")
# 2012-13 coincide con el despliegue de la notificacion de actualizaciones (Moodle 2.3,
# jun 2012): bases pequenias y factores inflados; 2015-16 es una base ya estable.
COHORT_BASES = (pd.Timestamp("2012-09-01"), pd.Timestamp("2015-09-01"))

COLOR_EDGE = s05.COLOR_EDGE
COLOR_TEXT = s05.COLOR_TEXT
COLOR_WARN = s05.COLOR_WARN
COLOR_TEAL_LIGHT = s05.COLOR_TEAL_LIGHT
COLOR_GRAY = s05.COLOR_GRAY


# ---------------------------------------------------------------- utilidades
def metric(share: np.ndarray, window: int = WINDOW) -> float:
    """Misma metrica que s05.recent_vs_peak_median, en numpy (rapido para replicas).
    numpy.median y pandas.median coinciden (promedio de los dos centrales)."""
    n = len(share)
    recent = np.median(share[-window:])
    p = int(np.argmax(share))
    half = window // 2
    peak = np.median(share[max(0, p - half):min(n, p + (window - half))])
    return float(recent - peak)


def peak_window(share: np.ndarray, window: int = WINDOW):
    n = len(share)
    p = int(np.argmax(share))
    half = window // 2
    return max(0, p - half), min(n, p + (window - half))


def top_share(g: np.ndarray, pct: float) -> float:
    k = max(1, math.ceil(len(g) * pct / 100))
    return float(np.sort(g)[::-1][:k].sum() / g.sum())


def frac_for_half(g: np.ndarray) -> float:
    c = np.cumsum(np.sort(g)[::-1]) / g.sum()
    return float((np.argmax(c >= 0.5) + 1) / len(g))


def gini(g: np.ndarray) -> float:
    s = np.sort(g)
    n = len(s)
    i = np.arange(1, n + 1)
    # sum_{i,j}|gi-gj| = 2 * sum_i (2i-n-1) s_i  (s ordenado ascendente)
    return float(2 * np.sum((2 * i - n - 1) * s) / (2 * n * n * s.mean()))


def concentration(g: np.ndarray) -> dict:
    d = {f"top{p}": top_share(g, p) for p in TOP_PCTS}
    d["half"] = frac_for_half(g)
    d["gini"] = gini(g)
    return d


def lorenz_gain(g: np.ndarray, grid: np.ndarray) -> np.ndarray:
    """Fraccion acumulada de la ganancia neta vs fraccion de plugins (de mayor a menor g)."""
    c = np.concatenate([[0.0], np.cumsum(np.sort(g)[::-1]) / g.sum()])
    xs = np.arange(len(g) + 1) / len(g)
    return np.interp(grid, xs, c)


def pct(x, nd=1):
    return fs.num(100 * x, nd) + "%"


def null_test(obs: dict, null_list: list) -> dict:
    out = {}
    for k in obs:
        arr = np.array([d[k] for d in null_list])
        lo, med, hi = np.percentile(arr, [2.5, 50, 97.5])
        ge = (1 + int((arr >= obs[k]).sum())) / (len(arr) + 1)
        le = (1 + int((arr <= obs[k]).sum())) / (len(arr) + 1)
        if k == "half":  # menor = mas concentrado
            ge, le = le, ge
        out[k] = dict(med=med, lo=lo, hi=hi, p_more=ge, p_less=le)
    return out


# ---------------------------------------------------------------- main
def main():
    plugin_series, coverage = s05.load_series()
    T = s05.build_ecosystem_total(plugin_series)
    comps = sorted(plugin_series)
    months = T.index
    midx = {m: i for i, m in enumerate(months)}

    # matriz meses x plugins (0 = sin reporte ese mes; no hay ceros reales en los datos)
    X = np.zeros((len(months), len(comps)))
    entry = np.zeros(len(comps), dtype=int)
    for j, c in enumerate(comps):
        s = plugin_series[c]
        for mth, v in s.items():
            X[midx[mth], j] = v
        entry[j] = midx[min(s)]
    assert min(v for s in plugin_series.values() for v in s.values()) > 0
    Tv = T.values.astype(float)
    assert np.allclose(X.sum(axis=1), Tv)

    # total acumulado por cohorte de entrada: D[c, t] = sum_{j: entry_j <= c} X[t, j]
    D = np.zeros((len(months), len(months)))
    for c in range(len(months)):
        D[c] = X[:, entry == c].sum(axis=1)
    D = np.cumsum(D, axis=0)

    # ---- cifras conocidas del texto ----
    t0, t1 = Tv[midx[pd.Timestamp("2012-09-01")]], Tv[-1]
    growth_x = t1 / t0
    assert round(t0 / 1000) == 27 and round(t1 / 1e4) == 123, (t0, t1)
    assert 45.5 < growth_x < 46.5, growth_x

    # ---- Parte A ----
    rng = np.random.default_rng(SEED)
    rows = []
    a4_neg = np.zeros(N_PERM_TIME)
    trend, trend_c = [], []
    a4c_neg = np.zeros(N_PERM_TIME)
    for j, c in enumerate(comps):
        s = plugin_series[c]
        if len(s) < s05.MIN_MONTHS_TREND:
            continue
        idx = sorted(s)
        pos = np.array([midx[m] for m in idx])
        x = np.array([s[m] for m in idx], dtype=float)
        share = x / Tv[pos]
        # A0 (verificacion contra 05)
        ref = s05.recent_vs_peak_median(s05.share_series(s, T))
        d0 = metric(share)
        assert abs(d0 - (ref[0] - ref[1])) < 1e-15
        # A2 sin crecimiento tras la ventana de pico
        a, b = peak_window(share)
        x2 = x.copy()
        x2[b:] = np.median(x[a:b])
        d2 = metric(x2 / Tv[pos])
        # A3 cuota dentro de la cohorte de entrada y anteriores
        d3 = metric(x / D[entry[j], pos])
        rows.append(dict(component=c, d0=d0, d2=d2, d3=d3))
        trend.append(share)
        trend_c.append(x / D[entry[j], pos])
    df = pd.DataFrame(rows)
    n_trend = len(df)
    frac0 = float((df.d0 < 0).mean())
    assert n_trend == 2145, n_trend
    assert round(100 * frac0, 1) == 91.9, frac0
    frac2 = float((df.d2 < 0).mean())
    frac3 = float((df.d3 < 0).mean())
    # A4 permutacion temporal
    for r in range(N_PERM_TIME):
        a4_neg[r] = np.mean([metric(rng.permutation(sh)) < 0 for sh in trend])
        a4c_neg[r] = np.mean([metric(rng.permutation(sh)) < 0 for sh in trend_c])
    frac4, frac4_lo, frac4_hi = a4_neg.mean(), *np.percentile(a4_neg, [2.5, 97.5])
    frac4c, frac4c_lo, frac4c_hi = a4c_neg.mean(), *np.percentile(a4c_neg, [2.5, 97.5])

    # A5 descomposicion del crecimiento del total
    base_rows = slice(midx[BASE_START], midx[BASE_END] + 1)
    rec_rows = slice(len(months) - WINDOW, len(months))
    xb = X[base_rows].mean(axis=0)
    xr = X[rec_rows].mean(axis=0)
    inc = xb > 0
    Tb, Tr = xb.sum(), xr.sum()
    gain_inc = float((xr[inc] - xb[inc]).sum())
    gain_ent = float(xr[~inc].sum())
    assert abs(gain_inc + gain_ent - (Tr - Tb)) < 1e-6 * Tr
    share_ent_gain = gain_ent / (Tr - Tb)
    share_ent_now = xr[~inc].sum() / Tr
    n_inc = int(inc.sum())
    n_active_now = int((xr > 0).sum())
    n_ent_active = int(((xr > 0) & ~inc).sum())
    # cuota actual de los 2.145 frente a los plugins con <24 meses
    long_mask = np.array([len(plugin_series[c]) >= s05.MIN_MONTHS_TREND for c in comps])
    share_short_now = xr[~long_mask].sum() / Tr
    gain_short = xr[~long_mask].sum() - xb[~long_mask].sum()
    share_short_gain = gain_short / (Tr - Tb)

    # ---- Parte B (principal): N=2.145, historia propia ----
    x0, x1, dur, stratum = [], [], [], []
    for c in comps:
        s = plugin_series[c]
        if len(s) < s05.MIN_MONTHS_TREND:
            continue
        idx = sorted(s)
        v = np.array([s[m] for m in idx], dtype=float)
        x0.append(np.median(v[:WINDOW]))
        x1.append(np.median(v[-WINDOW:]))
        c0 = pd.Timestamp(np.mean([pd.Timestamp(m).value for m in idx[:WINDOW]]))
        c1 = pd.Timestamp(np.mean([pd.Timestamp(m).value for m in idx[-WINDOW:]]))
        dur.append((c1 - c0).days / 365.25)
        stratum.append(min(s).year)
    x0, x1, dur, stratum = np.array(x0), np.array(x1), np.array(dur), np.array(stratum)
    assert len(x0) == 2145 and (dur > 0).all()
    g = x1 - x0
    rate = np.log(x1 / x0) / dur
    obs = concentration(g)
    frac_pos = float((g > 0).mean())
    frac_x10 = float((x1 >= 10 * x0).mean())
    # B0 proporcional: r* tal que sum x0*(exp(r* d)-1) = sum g
    lo, hi = -1.0, 2.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if (x0 * np.expm1(mid * dur)).sum() < g.sum():
            lo = mid
        else:
            hi = mid
    r_star = (lo + hi) / 2
    g_prop = x0 * np.expm1(r_star * dur)
    prop = concentration(g_prop)
    # B1 permutacion de tasas DENTRO de cada estrato de anio de entrada (duraciones
    # comparables; permutar entre estratos aplicaria la tasa de un plugin de 2 anios
    # durante 13 anios y haria explotar el nulo)
    rng_b = np.random.default_rng(SEED + 1)
    grid = np.concatenate([[0.0], np.geomspace(1e-3, 1, 400)])
    null_b, lor_b = [], []
    strata_idx = [np.flatnonzero(stratum == y) for y in np.unique(stratum)]
    for _ in range(N_PERM_GROWTH):
        rp = rate.copy()
        for ix in strata_idx:
            rp[ix] = rate[rng_b.permutation(ix)]
        gn = x0 * np.expm1(rp * dur)
        null_b.append(concentration(gn))
        lor_b.append(lorenz_gain(gn, grid))
    test_b = null_test(obs, null_b)
    lor_b = np.array(lor_b)
    rho_size_rate = float(pd.Series(np.log(x0)).corr(pd.Series(rate), method="spearman"))
    # quienes son el top 1%
    comps_long = [c for c in comps if len(plugin_series[c]) >= s05.MIN_MONTHS_TREND]
    top1_k = math.ceil(len(g) * 0.01)
    top1_names = [comps_long[i] for i in np.argsort(-g)[:top1_k]]

    # ---- Parte B (sensibilidad): cohortes fijas de incumbentes ----
    # Incumbente = reporte en los 12 meses de la ventana base (presencia completa, para que
    # una entrada a mitad de ventana no infle el factor). x_b = media en la ventana base,
    # x_r = media de los ultimos 12 meses (meses sin reporte = 0: las salidas cuentan).
    # Mismo periodo para todos: se permutan factores de crecimiento sin estratificar.
    rng_c = np.random.default_rng(SEED + 2)
    cohorts = []
    for b_start in COHORT_BASES:
        rows_b = slice(midx[b_start], midx[b_start] + WINDOW)
        full = (X[rows_b] > 0).all(axis=0)
        xb_i = X[rows_b][:, full].mean(axis=0)
        xr_i = X[rec_rows][:, full].mean(axis=0)
        g_i = xr_i - xb_i
        f_i = xr_i / xb_i
        F = xr_i.sum() / xb_i.sum()
        obs_i = concentration(g_i)
        obs_i["below"] = float((f_i < F).mean())  # pierden cuota dentro de la cohorte
        prop_i = concentration(xb_i * (F - 1))
        prop_i["below"] = 0.0
        null_i = []
        for _ in range(N_PERM_GROWTH):
            fp = rng_c.permutation(f_i)
            d = concentration(xb_i * (fp - 1))
            d["below"] = float((fp < (xb_i * fp).sum() / xb_i.sum()).mean())
            null_i.append(d)
        cohorts.append(dict(start=b_start, n=int(full.sum()), F=F, frac_pos=float((g_i > 0).mean()),
                            gain=float(g_i.sum()), obs=obs_i, prop=prop_i, test=null_test(obs_i, null_i),
                            rho=float(pd.Series(np.log(xb_i)).corr(pd.Series(f_i), method="spearman"))))

    # ---------------------------------------------------------------- informe
    names = {"top1": "ganancia neta captada por el top 1%",
             "top5": "ganancia neta captada por el top 5%",
             "top10": "ganancia neta captada por el top 10%",
             "half": "fracción mínima de plugins con el 50% de la ganancia",
             "gini": "Gini de la ganancia absoluta",
             "below": "plugins que crecen menos que el agregado de su cohorte"}

    def conc_table(o, pr, t):
        lines = ["| métrica | observado | nulo proporcional (B0) | nulo Gibrat (B1): mediana [IC 95%] "
                 "| p (más concentrado que B1) | p (menos concentrado que B1) |",
                 "|:--|--:|--:|--:|--:|--:|"]
        for k in o:
            fmt = (lambda v: fs.num(v, 3)) if k == "gini" else pct
            lines.append(f"| {names[k]} | {fmt(o[k])} | {fmt(pr[k])} | {fmt(t[k]['med'])} "
                         f"[{fmt(t[k]['lo'])}; {fmt(t[k]['hi'])}] | {fs.num(t[k]['p_more'], 3)} "
                         f"| {fs.num(t[k]['p_less'], 3)} |")
        return lines

    cohort_lines = []
    for co in cohorts:
        end = co["start"] + pd.DateOffset(months=WINDOW - 1)
        cohort_lines += [f"### Sensibilidad: cohorte fija con reporte en los 12 meses {co['start']:%m/%Y} – {end:%m/%Y}", "",
                         f"- {co['n']} plugins; factor agregado de la cohorte ×{fs.num(co['F'], 2)}; con ganancia positiva: "
                         f"{pct(co['frac_pos'])}; ganancia neta total: {fs.num(co['gain'])}; "
                         f"Spearman(log tamaño base, factor) = {fs.num(co['rho'], 3, sign=True)}.", "",
                         *conc_table(co["obs"], co["prop"], co["test"]), ""]

    L = ["# Modelo nulo de dilución para la pérdida de cuota de instalaciones", "",
         "Generado por `src/analyze/16_dilucion_modelo_nulo.py`. No editar a mano. Diseño en el docstring del script.", "",
         f"- Plugins con ≥24 meses de serie: N = {n_trend}; pierden cuota (métrica de 05): {pct(frac0)}.",
         f"- Total del ecosistema: {fs.num(t0)} (sep 2012) → {fs.num(t1)} (ago 2026), ×{fs.num(growth_x, 1)}.",
         f"- Semillas: {SEED} (A4, {N_PERM_TIME} réplicas), {SEED + 1} (B1, {N_PERM_GROWTH} permutaciones), "
         f"{SEED + 2} (sensibilidad, {N_PERM_GROWTH} permutaciones).", "",
         "## A. ¿De dónde sale el 91,9%? (misma métrica, mismos plugins)", "",
         "| escenario | % de plugins con diferencia negativa |", "|:--|--:|",
         f"| A0 observado | {pct(frac0)} |",
         f"| A1 cada plugin crece al ritmo del total (cuota constante, analítico) | 0,0% |",
         f"| A2 instalaciones congeladas en su nivel de pico (solo crece el denominador) | {pct(frac2)} |",
         f"| A3 cuota sobre su cohorte de entrada y anteriores (sin dilución por entrantes) | {pct(frac3)} |",
         f"| A4 serie de cuota permutada en el tiempo (solo artefacto de selección del pico) | {pct(frac4)} [{pct(frac4_lo)}; {pct(frac4_hi)}] |",
         f"| A4 sobre la cuota de cohorte de A3 | {pct(frac4c)} [{pct(frac4c_lo)}; {pct(frac4c_hi)}] |",
         "",
         "### Descomposición del crecimiento del total (A5)", "",
         f"- Base: media mensual sep 2012 – ago 2013 = {fs.num(Tb)}; reciente: media de los últimos 12 meses = {fs.num(Tr)} "
         f"(×{fs.num(Tr / Tb, 1)}).",
         f"- Incumbentes (algún reporte en la ventana base): {n_inc} plugins; aportan {fs.num(gain_inc)} "
         f"({pct(1 - share_ent_gain)}) del crecimiento neto.",
         f"- Entrantes posteriores: {n_ent_active} plugins activos hoy; aportan {fs.num(gain_ent)} "
         f"({pct(share_ent_gain)}) del crecimiento neto y suponen el {pct(share_ent_now)} del total actual.",
         f"- Plugins con <24 meses de serie (fuera de N, dentro del denominador): {pct(share_short_now)} del total actual "
         f"y {pct(share_short_gain)} del crecimiento neto.",
         f"- Plugins activos en los últimos 12 meses: {n_active_now}.", "",
         "## B. Concentración del crecimiento absoluto", "",
         "### B principal: N = 2.145, historia propia (primeros 12 meses frente a últimos 12)", "",
         f"- Ganancia neta total: {fs.num(g.sum())} instalaciones; plugins con ganancia positiva: {pct(frac_pos)}; "
         f"plugins que multiplican por ≥10: {pct(frac_x10)}.",
         f"- Tasa anualizada común del nulo proporcional: r* = {fs.num(r_star, 4)} (×{fs.num(math.exp(r_star), 3)} por año).",
         f"- Spearman(log tamaño inicial, tasa anualizada) = {fs.num(rho_size_rate, 3, sign=True)}.",
         f"- Top 1% ({top1_k} plugins) por ganancia absoluta: {', '.join(top1_names)}.", "",
         *conc_table(obs, prop, test_b), "",
         *cohort_lines,
         "## Lectura", "",
         "- p empíricos unilaterales frente a B1, en las dos direcciones: proporción de permutaciones tan "
         "concentradas o más que lo observado, y tan poco concentradas o menos (para la fracción del 50%, el sentido "
         "se invierte: menor = más concentrado).",
         "- B1 principal permuta las tasas anualizadas dentro de cada año de entrada (estratos de duración comparable).",
         "- Con ganancias negativas la ganancia neta captada por el top puede superar el 100% y el Gini puede superar 1; "
         "solo se usan para comparar observado con nulo.",
         ]
    DOC_PATH.write_text("\n".join(L) + "\n")
    print("\n".join(L))

    # ---------------------------------------------------------------- figura
    fs.apply()
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(fs.TEXT_WIDTH_IN, 6.4),
                                   gridspec_kw=dict(height_ratios=[1, 1.5]))
    labels = ["Observado (A0)", "Sin entrantes en el\ndenominador (A3)",
              "Solo artefacto del pico,\nserie permutada (A4)", "Instalaciones congeladas\nen el pico (A2)"]
    vals = [frac0, frac3, frac4, frac2]
    cols = [COLOR_EDGE, COLOR_TEAL_LIGHT, COLOR_GRAY, COLOR_GRAY]
    ypos = np.arange(len(vals))[::-1]
    ax1.barh(ypos, [100 * v for v in vals], color=cols, edgecolor=COLOR_TEXT, linewidth=0.6, height=0.62)
    for y, v in zip(ypos, vals):
        ax1.text(100 * v + 1.5, y, fs.num(100 * v, 1) + " %", ha="left", va="center", fontsize=9, color=COLOR_TEXT)
    ax1.set_yticks(ypos)
    ax1.set_yticklabels(labels)
    ax1.set_xlim(0, 112)
    ax1.xaxis.set_major_formatter(fs.comma_formatter(0))
    ax1.set_xlabel("% de plugins con diferencia de cuota negativa (N = 2.145)", color=COLOR_TEXT)
    ax1.set_title("A. Pérdida de cuota observada y bajo modelos nulos", color=COLOR_TEXT, pad=6)

    xs = grid * 100
    ax2.fill_between(xs, 100 * np.percentile(lor_b, 2.5, axis=0), 100 * np.percentile(lor_b, 97.5, axis=0),
                     color=COLOR_GRAY, alpha=0.45, linewidth=0, label="Nulo Gibrat (IC 95%)")
    ax2.plot(xs, 100 * lorenz_gain(g_prop, grid), color=COLOR_WARN, linewidth=1.4, linestyle="--",
             label="Nulo proporcional")
    ax2.plot(xs, 100 * lorenz_gain(g, grid), color=COLOR_EDGE, linewidth=1.8, label="Observado")
    ax2.axhline(100, color=COLOR_TEXT, linewidth=0.6, linestyle=":")
    ax2.set_xscale("log")
    ax2.set_xlim(0.1, 100)
    ax2.xaxis.set_major_formatter(fs.comma_formatter(1))
    ax2.yaxis.set_major_formatter(fs.comma_formatter(0))
    ax2.set_xlabel("% de plugins (mayor ganancia primero)", color=COLOR_TEXT)
    ax2.set_ylabel("% acumulado de la\nganancia neta", color=COLOR_TEXT)
    ax2.set_title("B. Concentración de la ganancia absoluta (N = 2.145)", color=COLOR_TEXT, pad=6)
    ax2.legend(frameon=False, loc="lower right")
    for ax in (ax1, ax2):
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.tick_params(colors=COLOR_TEXT)
    s05.assert_no_banned_words(*labels, ax1.get_title(), ax2.get_title())
    fig.tight_layout()
    fs.save(fig, FIGURES / "dilucion_modelo_nulo.png")
    plt.close(fig)
    print("\nOK -- 16_dilucion_modelo_nulo.py termino sin errores.")


if __name__ == "__main__":
    main()
