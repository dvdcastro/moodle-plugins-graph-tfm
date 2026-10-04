#!/usr/bin/env python3
"""Prediccion de inactividad: calibracion (Brier), robustez a varios cortes
temporales y exposicion esperada (feedback tutora sobre el borrador 2:
"anade la puntuacion de Brier que anuncias, prueba mas de un corte temporal y
calcula ya la exposicion esperada").

Reutiliza sin modificarlo 13_prediccion_inactividad.py (importlib): mismas
features, misma etiqueta (ninguna version en los 3 anios siguientes a T0),
mismos modelos y misma semilla. Antes de extender, se reproducen con asserts
los numeros publicados por 13_ (AUC 0,771 / 0,750 / 0,783 / 0,738).

1. Brier y calibracion (split de 13_: entrena cohorte 2020, evalua cohorte 2023)
   - Brier de cada modelo, Brier de referencia climatologica y Brier skill
     score BSS = 1 - Brier / Brier_ref. Dos referencias:
       * clim. evaluacion: predecir siempre la tasa observada en la cohorte de
         evaluacion, ybar(1 - ybar) (referencia estandar, optimista porque usa
         la tasa del futuro);
       * clim. entrenamiento: predecir siempre la tasa de la cohorte de
         entrenamiento (la unica disponible en T0; referencia operativa).
   - Calibracion: intercepto con el logit como offset (calibration-in-the-
     large, 0 = ideal), pendiente de calibracion (1 = ideal; < 1 = predicciones
     demasiado extremas) y tabla de fiabilidad por deciles de probabilidad.
   - IC 95 % por bootstrap (2.000 remuestreos) del Brier y del BSS.

2. Robustez a varios cortes (origen movil, estrictamente fuera de tiempo)
   Para cada cohorte de evaluacion T0 se entrena con la cohorte T0 - 3 anios,
   cuya etiqueta se cierra exactamente en T0: el modelo nunca ve informacion
   posterior al momento en que se usaria. Todas las features se calculan con
   versiones e instalaciones fechadas <= T0 (funcion build_cohort de 13_); la
   lista supportedmoodles (fuga retroactiva) no entra en ningun modelo.
   Cortes de evaluacion: 10-sep de 2017 a 2023 (entrenamiento 2014 a 2020).
   El limite superior lo fija el cierre de datos (2026-09-07): la etiqueta de
   la cohorte 2023 termina 3 dias antes de completarse; cohortes posteriores no
   tienen la etiqueta observada. El limite inferior lo fija el tamano de la
   cohorte de entrenamiento y la serie de instalaciones (desde abr-2012).

3. Exposicion esperada  E = P(inactividad en 3 anios | features en T_now) x I
   - Modelo: regresion logistica principal (16 variables) entrenada con la
     cohorte mas reciente con etiqueta completa, T0 = 2023-09-10.
   - Aplicacion: features en T_now = 2026-09-10 (cierre de datos usado por
     12_riesgo_sensibilidad.py), sobre los plugins ACTIVOS en T_now (al menos
     una version en los 3 anios previos, es decir ST = 0 en 12_).
   - I: termino de impacto del indice V2 (columna I de
     data/processed/riesgo_exposicion_T3.csv), mismo escalado min-max sobre la
     poblacion P2. E es una magnitud esperada en unidades de I, no un riesgo
     calibrado absoluto: hereda la deriva de la tasa base entre cohortes.
   - Comparacion con el top-30 de V2 (Jaccard, solapamiento, Spearman) en toda
     la poblacion y restringido a los activos.

Salidas: data/processed/inactividad_brier.csv, inactividad_fiabilidad.csv,
inactividad_cortes.csv, exposicion_esperada.csv (top-20),
exposicion_esperada_completa.csv, docs/prediccion_brier_cortes.md
Uso: python3 17_prediccion_brier_cortes.py
"""
import importlib.util
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import brentq
from scipy.special import expit, logit
from scipy.stats import spearmanr
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import brier_score_loss, roc_auc_score

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
_spec = importlib.util.spec_from_file_location("m13", HERE / "13_prediccion_inactividad.py")
m13 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m13)

ROOT, PROCESSED = m13.ROOT, m13.PROCESSED
SEED, N_BOOT, HORIZON_Y = m13.SEED, m13.N_BOOT, m13.HORIZON_Y
T_NOW = datetime(2026, 9, 10, tzinfo=timezone.utc)  # = DATA_CLOSE de 12_
TEST_YEARS = list(range(2017, 2024))
TOP_E, TOP_V2 = 20, 30

MODELS = {
    "Línea base (años desde la última versión)": (m13.logreg, ["recency_y"]),
    "RL principal (16 variables)": (m13.logreg, m13.MAIN),
    "RL parsimoniosa (3 variables, exploratoria)": (m13.logreg, m13.PARSIMONIOUS),
    "HistGradientBoosting (16 variables)": (
        lambda: HistGradientBoostingClassifier(random_state=SEED, max_iter=300, learning_rate=0.05), m13.MAIN),
}
BASE, MAIN = "Línea base (años desde la última versión)", "RL principal (16 variables)"
EXPECTED_13 = {BASE: 0.750, MAIN: 0.771, "RL parsimoniosa (3 variables, exploratoria)": 0.783,
               "HistGradientBoosting (16 variables)": 0.738}
EXPECTED_BRIER_13 = {BASE: 0.193, MAIN: 0.183, "RL parsimoniosa (3 variables, exploratoria)": 0.179,
                     "HistGradientBoosting (16 variables)": 0.223}

es = m13.es


def cutoff(year):
    return datetime(year, 9, 10, tzinfo=timezone.utc)


def calib(y, p):
    """Intercepto de calibracion (offset = logit p) y pendiente de calibracion."""
    lp = logit(np.clip(p, 1e-6, 1 - 1e-6))
    a_citl = brentq(lambda a: np.sum(y - expit(a + lp)), -10, 10)
    beta = np.zeros(2)  # IRLS para y ~ a + b * lp
    X = np.column_stack([np.ones_like(lp), lp])
    for _ in range(50):
        mu = expit(X @ beta)
        w = mu * (1 - mu)
        step = np.linalg.solve(X.T @ (X * w[:, None]), X.T @ (y - mu))
        beta += step
        if np.abs(step).max() < 1e-10:
            break
    return a_citl, beta[1]


def bss(y, p, ref):
    return 1 - brier_score_loss(y, p) / brier_score_loss(y, np.full_like(p, ref, dtype=float))


def reliability(y, p, q=10):
    d = pd.DataFrame({"y": y, "p": p})
    d["decil"] = pd.qcut(d["p"].rank(method="first"), q, labels=range(1, q + 1))
    t = d.groupby("decil", observed=True).agg(n=("y", "size"), p_media=("p", "mean"), tasa_observada=("y", "mean"))
    t["diferencia"] = t["tasa_observada"] - t["p_media"]
    t = t.reset_index()
    t["decil"] = t["decil"].astype(int)
    return t


def fit_predict(mk, feats, train, test):
    return mk().fit(train[feats], train["inactivo"].values).predict_proba(test[feats])[:, 1]


def main():
    versions, installs = m13.load_versions(), m13.load_installs()
    meta = {}  # ningun modelo de este script usa las variables de foto 2026 (n_mantenedores, in-degree)

    # ---------- 0. reproducir 13_ ----------
    train, test = (m13.build_cohort(versions, installs, meta, t) for t in (m13.T_TRAIN, m13.T_TEST))
    assert (len(train), len(test)) == (781, 974), (len(train), len(test))
    y_tr, y_te = train["inactivo"].values, test["inactivo"].values
    preds = {n: fit_predict(mk, f, train, test) for n, (mk, f) in MODELS.items()}
    for n, auc in EXPECTED_13.items():
        assert round(roc_auc_score(y_te, preds[n]), 3) == auc, (n, roc_auc_score(y_te, preds[n]))
        assert round(brier_score_loss(y_te, preds[n]), 3) == EXPECTED_BRIER_13[n], n
    assert not set(MODELS[MAIN][1]) & set(m13.LEAKY)

    # ---------- 1. Brier, BSS y calibracion ----------
    rate_tr, rate_te = y_tr.mean(), y_te.mean()
    rng = np.random.default_rng(SEED)
    boot_idx = [i for i in (rng.integers(0, len(y_te), len(y_te)) for _ in range(N_BOOT))]
    rows = [{"modelo": "Referencia climatológica (tasa de evaluación)", "Brier": brier_score_loss(y_te, np.full(len(y_te), rate_te)),
             "BSS (clim. evaluación)": 0.0, "BSS (clim. entrenamiento)": np.nan},
            {"modelo": "Referencia climatológica (tasa de entrenamiento)", "Brier": brier_score_loss(y_te, np.full(len(y_te), rate_tr)),
             "BSS (clim. evaluación)": bss(y_te, np.full(len(y_te), rate_tr), rate_te), "BSS (clim. entrenamiento)": 0.0}]
    for n, p in preds.items():
        a, b = calib(y_te, p)
        bb = np.array([[brier_score_loss(y_te[i], p[i]), bss(y_te[i], p[i], y_te[i].mean())] for i in boot_idx])
        rows.append({"modelo": n, "Brier": brier_score_loss(y_te, p),
                     "IC95 Brier": f"[{es(np.percentile(bb[:, 0], 2.5))}; {es(np.percentile(bb[:, 0], 97.5))}]",
                     "BSS (clim. evaluación)": bss(y_te, p, rate_te),
                     "IC95 BSS": f"[{es(np.percentile(bb[:, 1], 2.5))}; {es(np.percentile(bb[:, 1], 97.5))}]",
                     "BSS (clim. entrenamiento)": bss(y_te, p, rate_tr),
                     "prob. media": p.mean(), "intercepto calibración": a, "pendiente calibración": b,
                     "ROC-AUC": roc_auc_score(y_te, p)})
    brier = pd.DataFrame(rows)
    brier.to_csv(PROCESSED / "inactividad_brier.csv", index=False)
    rel = reliability(y_te, preds[MAIN])
    rel.to_csv(PROCESSED / "inactividad_fiabilidad.csv", index=False)
    ece = float(np.sum(rel["n"] * rel["diferencia"].abs()) / rel["n"].sum())

    # ---------- 2. varios cortes ----------
    cohorts = {y: m13.build_cohort(versions, installs, meta, cutoff(y)) for y in range(TEST_YEARS[0] - HORIZON_Y, TEST_YEARS[-1] + 1)}
    for y, c in cohorts.items():  # sin informacion posterior a T0 en las features
        assert c["recency_y"].min() >= 0 and (c["recency_y"] <= HORIZON_Y + 0.01).all()  # 3 anios naturales, base 365,25 d
        assert cutoff(y).replace(year=y + HORIZON_Y) <= datetime(2026, 9, 10, tzinfo=timezone.utc)
    cut_rows, rng = [], np.random.default_rng(SEED)
    for ty in TEST_YEARS:
        tr, te = cohorts[ty - HORIZON_Y], cohorts[ty]
        yt = te["inactivo"].values
        pm = {k: fit_predict(*MODELS[k], tr, te) for k in (BASE, MAIN)}
        boots = {k: [] for k in pm}
        dif = []
        for _ in range(N_BOOT):
            i = rng.integers(0, len(yt), len(yt))
            ab, am = roc_auc_score(yt[i], pm[BASE][i]), roc_auc_score(yt[i], pm[MAIN][i])
            boots[BASE].append(ab)
            boots[MAIN].append(am)
            dif.append(am - ab)
        for k, p in pm.items():
            a, b = calib(yt, p)
            cut_rows.append({
                "T0 entrenamiento": ty - HORIZON_Y, "T0 evaluación": ty, "etiqueta hasta": ty + HORIZON_Y,
                "n entrenamiento": len(tr), "n evaluación": len(te),
                "tasa entrenamiento": tr["inactivo"].mean(), "tasa evaluación": yt.mean(), "modelo": k,
                "ROC-AUC": roc_auc_score(yt, p),
                "IC95 ROC-AUC": f"[{es(np.percentile(boots[k], 2.5))}; {es(np.percentile(boots[k], 97.5))}]",
                "ΔAUC vs. base [IC95]": "—" if k == BASE else
                    f"{es(np.mean(dif))} [{es(np.percentile(dif, 2.5))}; {es(np.percentile(dif, 97.5))}]",
                "Brier": brier_score_loss(yt, p), "Brier ref.": yt.mean() * (1 - yt.mean()),
                "BSS": bss(yt, p, yt.mean()), "BSS (clim. entrenamiento)": bss(yt, p, tr["inactivo"].mean()),
                "prob. media": p.mean(), "intercepto calibración": a, "pendiente calibración": b})
    cuts = pd.DataFrame(cut_rows)
    r23 = cuts[(cuts["T0 evaluación"] == 2023) & (cuts["modelo"] == MAIN)].iloc[0]
    assert round(r23["ROC-AUC"], 3) == 0.771  # el corte 2023 es exactamente el split de 13_
    cuts.to_csv(PROCESSED / "inactividad_cortes.csv", index=False)
    cm = cuts[cuts["modelo"] == MAIN]
    cb = cuts[cuts["modelo"] == BASE].set_index("T0 evaluación")
    summary = {"auc_min": cm["ROC-AUC"].min(), "auc_max": cm["ROC-AUC"].max(), "auc_mean": cm["ROC-AUC"].mean(),
               "bss_min": cm["BSS"].min(), "bss_max": cm["BSS"].max(),
               "wins": int((cm.set_index("T0 evaluación")["ROC-AUC"] > cb["ROC-AUC"]).sum()),
               "dauc_mean": float((cm.set_index("T0 evaluación")["ROC-AUC"] - cb["ROC-AUC"]).mean())}

    # ---------- 3. exposicion esperada ----------
    fit_cohort = cohorts[TEST_YEARS[-1]]  # 2023: la mas reciente con etiqueta observada
    now = m13.build_cohort(versions, installs, meta, T_NOW)  # solo activos en T_NOW; su 'inactivo' no es observable
    model = MODELS[MAIN][0]().fit(fit_cohort[m13.MAIN], fit_cohort["inactivo"].values)
    model_p = MODELS["RL parsimoniosa (3 variables, exploratoria)"][0]().fit(
        fit_cohort[m13.PARSIMONIOUS], fit_cohort["inactivo"].values)
    now["p_inactividad"] = model.predict_proba(now[m13.MAIN])[:, 1]
    now["p_parsimoniosa"] = model_p.predict_proba(now[m13.PARSIMONIOUS])[:, 1]
    risk = pd.read_csv(PROCESSED / "riesgo_exposicion_T3.csv")
    assert len(risk) == 2876
    act_risk = set(risk.loc[risk["ST"] == 0, "component"])
    e = now[["component", "p_inactividad", "p_parsimoniosa", "recency_y", "releases_2y"]].merge(
        risk[["component", "installations", "SM", "ST", "I", "E_exposicion", "rank", "ex_core"]], on="component", how="inner")
    n_sin_I = len(now) - len(e)
    assert (e["ST"] == 0).all(), "un plugin activo en T_now no puede tener ST = 1"
    e["E_esperada"] = e["p_inactividad"] * e["I"]
    e["E_parsimoniosa"] = e["p_parsimoniosa"] * e["I"]
    e = e.sort_values(["E_esperada", "installations", "component"], ascending=[False, False, True]).reset_index(drop=True)
    e["rank_E"] = np.arange(1, len(e) + 1)
    e = e.rename(columns={"rank": "rank_V2", "E_exposicion": "V2"})
    cols = ["rank_E", "component", "installations", "SM", "recency_y", "releases_2y", "I", "p_inactividad",
            "E_esperada", "V2", "rank_V2", "ex_core"]
    e[cols + ["p_parsimoniosa", "E_parsimoniosa"]].to_csv(PROCESSED / "exposicion_esperada_completa.csv", index=False)
    e.head(TOP_E)[cols].to_csv(PROCESSED / "exposicion_esperada.csv", index=False)

    topE30 = set(e.head(TOP_V2)["component"])
    topE20 = set(e.head(TOP_E)["component"])
    v2_all = set(risk.sort_values(["E_exposicion", "installations", "component"], ascending=[False, False, True])
                 .head(TOP_V2)["component"])
    e_by_v2 = e.sort_values(["V2", "installations", "component"], ascending=[False, False, True])
    v2_act = set(e_by_v2.head(TOP_V2)["component"])
    jac = lambda a, b: len(a & b) / len(a | b)  # noqa: E731
    pE = e.sort_values(["E_parsimoniosa", "installations", "component"], ascending=[False, False, True])
    comp = pd.DataFrame([
        {"comparación": "top-30 E vs. top-30 V2 (población completa)", "solapamiento": len(topE30 & v2_all),
         "Jaccard": jac(topE30, v2_all), "Spearman (activos)": np.nan},
        {"comparación": "top-20 E vs. top-30 V2 (población completa)", "solapamiento": len(topE20 & v2_all),
         "Jaccard": jac(topE20, v2_all), "Spearman (activos)": np.nan},
        {"comparación": "top-30 E vs. top-30 V2 (solo activos)", "solapamiento": len(topE30 & v2_act),
         "Jaccard": jac(topE30, v2_act), "Spearman (activos)": spearmanr(e["E_esperada"], e["V2"]).statistic},
        {"comparación": "E vs. impacto I (activos)", "solapamiento": np.nan, "Jaccard": np.nan,
         "Spearman (activos)": spearmanr(e["E_esperada"], e["I"]).statistic},
        {"comparación": "E vs. P(inactividad) (activos)", "solapamiento": np.nan, "Jaccard": np.nan,
         "Spearman (activos)": spearmanr(e["E_esperada"], e["p_inactividad"]).statistic},
        {"comparación": "top-30 E principal vs. E parsimoniosa", "solapamiento": len(topE30 & set(pE.head(TOP_V2)["component"])),
         "Jaccard": jac(topE30, set(pE.head(TOP_V2)["component"])),
         "Spearman (activos)": spearmanr(e["E_esperada"], e["E_parsimoniosa"]).statistic},
    ])
    comp.to_csv(PROCESSED / "exposicion_esperada_comparacion.csv", index=False)
    v2_all_st = risk.set_index("component").loc[list(v2_all), "ST"]
    exp_notes = [
        f"Modelo: RL principal entrenada con la cohorte T0 = {cutoff(TEST_YEARS[-1]).date()} (n = {len(fit_cohort)}, "
        f"tasa = {es(fit_cohort['inactivo'].mean())}), aplicada a las features en T_now = {T_NOW.date()}.",
        f"Plugins activos en T_now: {len(now)}; con término de impacto I (población P2): {len(e)} "
        f"({n_sin_I} sin mantenedor, fuera de P2). Activos según 12_ (ST = 0): {len(act_risk)}.",
        f"Probabilidad media predicha en T_now: {es(e['p_inactividad'].mean())} (mediana {es(e['p_inactividad'].median())}); "
        f"inactivos esperados en 2026-2029: {e['p_inactividad'].sum():.0f} de {len(e)}.",
        f"El top-30 de V2 sobre toda la población contiene {int(v2_all_st.sum())} plugins con ST = 1 "
        f"(ya inactivos), que por definición no entran en E.",
        f"Top-{TOP_E} de E con un solo mantenedor (SM = 1): {int(e.head(TOP_E)['SM'].sum())}; "
        f"P(inactividad) mediana del top-{TOP_E}: {es(e.head(TOP_E)['p_inactividad'].median())}; "
        f"I mediano del top-{TOP_E}: {es(e.head(TOP_E)['I'].median())} frente a {es(e['I'].median())} en todos los activos.",
    ]

    # ---------- documento ----------
    def fmt(t, f=".3f"):
        t = t.copy()
        for c in t.columns:  # enteros sin decimales (tabulate aplica floatfmt a toda columna numerica con NaN)
            if pd.api.types.is_numeric_dtype(t[c]) and (t[c].dropna() % 1 == 0).all() and c not in ("BSS (clim. evaluación)", "BSS (clim. entrenamiento)"):
                t[c] = t[c].map(lambda v: "—" if pd.isna(v) else str(int(v)))
        return t.to_markdown(index=False, floatfmt=f)
    split_notes = [
        f"Split de 13_: entrenamiento T0 = {m13.T_TRAIN.date()} (n = {len(train)}, tasa = {es(rate_tr)}); "
        f"evaluación T0 = {m13.T_TEST.date()} (n = {len(test)}, tasa = {es(rate_te)}).",
        "Reproducción de 13_ verificada con asserts: ROC-AUC 0,750 / 0,771 / 0,783 / 0,738 y Brier 0,193 / 0,183 / 0,179 / 0,223.",
        f"Brier de referencia climatológica = ȳ(1 − ȳ) = {es(rate_te * (1 - rate_te))}; con la tasa de entrenamiento "
        f"(la única conocida en T0) = {es(brier_score_loss(y_te, np.full(len(y_te), rate_tr)))}.",
        f"Error de calibración esperado (ECE, deciles) del modelo principal: {es(ece)}.",
    ]
    cut_cols = ["T0 entrenamiento", "T0 evaluación", "n entrenamiento", "n evaluación", "tasa entrenamiento",
                "tasa evaluación", "modelo", "ROC-AUC", "IC95 ROC-AUC", "ΔAUC vs. base [IC95]", "Brier", "Brier ref.",
                "BSS", "BSS (clim. entrenamiento)", "prob. media", "intercepto calibración", "pendiente calibración"]
    top_tbl = e.head(TOP_E)[cols].copy()
    md = ["# Predicción de inactividad: Brier, varios cortes temporales y exposición esperada", "",
          "Generado por `src/analyze/17_prediccion_brier_cortes.py`. No editar a mano. Diseño en el docstring del script; "
          "reutiliza `13_prediccion_inactividad.py` sin modificarlo.", "",
          "## 1. Brier y calibración (entrenamiento 2020, evaluación 2023)", "",
          *[f"- {x}" for x in split_notes], "",
          "BSS = 1 − Brier / Brier_ref. Intercepto de calibración: 0 ideal (> 0 = el modelo infraestima la tasa). "
          "Pendiente de calibración: 1 ideal (< 1 = predicciones demasiado extremas).", "",
          fmt(brier), "",
          "### Tabla de fiabilidad por deciles (RL principal)", "", fmt(rel), "",
          "## 2. Robustez a varios cortes (entrena en T0 − 3, evalúa en T0, horizonte 3 años)", "",
          f"- Cohortes de evaluación {TEST_YEARS[0]}–{TEST_YEARS[-1]}; la etiqueta de cada cohorte de entrenamiento se cierra "
          "exactamente en el T0 de evaluación. Cohortes posteriores a 2023 no tienen la etiqueta completa (cierre 2026-09-07).",
          f"- RL principal: ROC-AUC entre {es(summary['auc_min'])} y {es(summary['auc_max'])} (media {es(summary['auc_mean'])}); "
          f"BSS entre {es(summary['bss_min'])} y {es(summary['bss_max'])}; supera a la línea base en {summary['wins']} de "
          f"{len(TEST_YEARS)} cortes (ΔAUC medio {es(summary['dauc_mean'])}).", "",
          fmt(cuts[cut_cols]), "",
          "## 3. Exposición esperada E = P̂(inactividad a 3 años) × I", "",
          *[f"- {x}" for x in exp_notes], "",
          f"### Top-{TOP_E} por exposición esperada", "", fmt(top_tbl), "",
          "### Comparación con el índice V2", "", fmt(comp), ""]
    (ROOT / "docs" / "prediccion_brier_cortes.md").write_text("\n".join(md))
    print("\n".join(md))


if __name__ == "__main__":
    main()
