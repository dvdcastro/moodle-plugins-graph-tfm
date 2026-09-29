#!/usr/bin/env python3
"""Experimento supervisado: prediccion de inactividad de publicacion de plugins
(feedback tutora, 2do borrador, punto 6: reforzar el encaje con IA/Big Data).

Pregunta: entre los plugins ACTIVOS en una fecha de corte T0 (al menos una
release en los 3 anios previos), ¿se puede anticipar cuales NO publicaran
ninguna release en los 3 anios siguientes?

La etiqueta mide INACTIVIDAD DE PUBLICACION, no abandono: incluye plugins
estables o terminados que no necesitan versiones nuevas, funcionalidades
absorbidas por el nucleo y desarrollo que sigue en GitHub sin subir versiones
al directorio. "Abandono" es solo una hipotesis de interpretacion.

Diseno anti-fuga:
  - Features del modelo principal calculadas solo con informacion fechada
    <= T0: historial de versiones (versions_raw.csv) y serie mensual de
    instalaciones (stats_series_raw.jsonl). El valor mensual de instalaciones
    se publica al cerrar el mes, asi que en T0 (dia 10) se usa el mes ANTERIOR.
  - Validacion fuera de tiempo: entrena con la cohorte T0 = 2020-09-10
    (etiqueta observada hasta 2023-09-10) y evalua con la cohorte
    T0 = 2023-09-10 (etiqueta observada hasta el cierre de datos, 2026-09-07:
    la ventana queda 3 dias corta, efecto despreciable).
  - Fuga detectada y excluida: la lista "supportedmoodles" de cada version se
    actualiza retroactivamente en el directorio (versiones anteriores a 2020
    declaran soporte para Moodle >= 4.0, publicado en 2022). Esas variables, y
    las que solo existen como foto de 2026 (n_mantenedores, in-degree), van
    solo a un modelo de sensibilidad.
  - Limitacion no corregible: sesgo de supervivencia. El snapshot del
    directorio (2026-09-07) no contiene los plugins retirados; pluglist_id
    llega a ~4.430 pero hay 2.888 plugins.

Modelos:
  - Baseline: una sola variable (anios desde la ultima release).
  - Principal (pre-especificado): regresion logistica estandarizada con todas
    las features fechadas <= T0.
  - Parsimonioso (exploratorio, identificado por ablacion): recency +
    log(instalaciones) + releases en los 2 anios previos.
  - HistGradientBoosting: referencia no lineal.
Incertidumbre: IC 95% por bootstrap sobre la cohorte de evaluacion, pareado
para la diferencia de AUC frente al baseline.

Salidas: data/processed/inactividad_*.csv, docs/prediccion_inactividad.md,
figures/inactividad_roc.png, figures/inactividad_coeficientes.png
Uso: python3 13_prediccion_inactividad.py
"""
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.ticker import FuncFormatter  # noqa: E402
from sklearn.ensemble import HistGradientBoostingClassifier  # noqa: E402
from sklearn.linear_model import LogisticRegression  # noqa: E402
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score, roc_curve  # noqa: E402
from sklearn.model_selection import StratifiedKFold, cross_val_predict  # noqa: E402
from sklearn.pipeline import make_pipeline  # noqa: E402
from sklearn.preprocessing import StandardScaler  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _gds_utils import ROOT  # noqa: E402

PROCESSED = ROOT / "data" / "processed"
FIGURES = ROOT / "figures"
HORIZON_Y = 3
T_TRAIN = datetime(2020, 9, 10, tzinfo=timezone.utc)
T_TEST = datetime(2023, 9, 10, tzinfo=timezone.utc)
SEED = 20260928
N_BOOT = 2000
TEXT_WIDTH_IN = 15 / 2.54  # ancho util del Doc (A4, margenes 3 cm)
TOP_TYPES = ["mod", "block", "local", "theme", "qtype", "format", "auth", "filter", "report", "tool"]

DATED = ["age_y", "recency_y", "n_versions", "releases_2y", "log_installs", "installs_growth"]
TYPES = [f"type_{t}" for t in TOP_TYPES]
MAIN = DATED + TYPES
PARSIMONIOUS = ["recency_y", "log_installs", "releases_2y"]
LEAKY = ["n_maintainers", "log_indeg_dep", "n_supported", "support_lag"]

LABELS = {"age_y": "Antigüedad del plugin (años)", "recency_y": "Años desde la última versión",
          "n_versions": "Nº de versiones publicadas", "releases_2y": "Versiones en los 2 años previos",
          "log_installs": "log(instalaciones)", "installs_growth": "Crecimiento anual de instalaciones (log)"}
LABELS.update({f"type_{t}": f"Tipo {t} (vs. resto)" for t in TOP_TYPES})


def ts(dt):
    return dt.timestamp()


def years_before(dt, n):
    return dt.replace(year=dt.year - n)


def parse_moodle(v):
    try:
        major, minor = str(v).split(".")[:2]
        return int(major) + int(minor) / 100
    except ValueError:
        return np.nan


def load_versions():
    v = pd.read_csv(PROCESSED / "versions_raw.csv", usecols=["component", "timecreated", "supportedmoodles"])
    v = v.dropna(subset=["timecreated"])
    v["timecreated"] = v["timecreated"].astype(float)
    sup = v["supportedmoodles"].fillna("").astype(str).str.split(";")
    v["n_supported"] = sup.map(lambda xs: sum(1 for x in xs if x))
    v["max_supported"] = sup.map(lambda xs: max((parse_moodle(x) for x in xs if x), default=np.nan))
    return v


def load_installs():
    out = {}
    with open(PROCESSED / "stats_series_raw.jsonl") as f:
        for line in f:
            r = json.loads(line)
            s = r.get("installs_series") or {}
            labels = s.get("labels")
            data = None
            if isinstance(s.get("datasets"), list) and s["datasets"]:
                data = s["datasets"][0].get("data")
            if data is None:
                data = s.get("data")
            if labels and data and len(labels) == len(data):
                out[r["component"]] = dict(zip(labels, data))
    return out


def month_before(dt):
    first = dt.replace(day=1)
    return first - timedelta(days=1)


def installs_at(series, dt):
    if series is None:
        return np.nan
    val = series.get(dt.strftime("%b %Y"))
    return float(val) if val is not None else np.nan


def build_cohort(versions, installs, meta, t0):
    t0s, start, end = ts(t0), ts(years_before(t0, HORIZON_Y)), ts(t0.replace(year=t0.year + HORIZON_Y))
    known = sorted(v for v in versions.loc[versions["timecreated"] <= t0s, "max_supported"].dropna().unique())
    order = {v: i for i, v in enumerate(known)}
    m_now, m_prev = month_before(t0), month_before(years_before(t0, 1))
    rows = []
    for comp, g in versions.groupby("component"):
        pre = g[g["timecreated"] <= t0s].sort_values("timecreated")
        if pre.empty or pre["timecreated"].iloc[-1] <= start:
            continue
        last = pre.iloc[-1]
        post = g[(g["timecreated"] > t0s) & (g["timecreated"] <= end)]
        ser = installs.get(comp)
        i0, i_prev = installs_at(ser, m_now), installs_at(ser, m_prev)
        ptype = comp.split("_", 1)[0]
        row = {
            "component": comp,
            "inactivo": int(post.empty),
            "age_y": (t0s - pre["timecreated"].iloc[0]) / (365.25 * 86400),
            "recency_y": (t0s - last["timecreated"]) / (365.25 * 86400),
            "n_versions": len(pre),
            "releases_2y": int((pre["timecreated"] > ts(years_before(t0, 2))).sum()),
            "log_installs": np.log1p(i0) if not np.isnan(i0) else 0.0,
            "installs_growth": (np.log1p(i0) - np.log1p(i_prev)) if not (np.isnan(i0) or np.isnan(i_prev)) else 0.0,
            "n_supported": last["n_supported"],
            "support_lag": (len(known) - 1 - order[last["max_supported"]]) if last["max_supported"] in order else np.nan,
        }
        for t in TOP_TYPES:
            row[f"type_{t}"] = int(ptype == t)
        m = meta.get(comp, {})
        row["n_maintainers"] = m.get("n_maintainers", 0)
        row["log_indeg_dep"] = np.log1p(m.get("indeg", 0))
        row["indeg"], row["pr"] = m.get("indeg", 0), m.get("pr", 0.15)
        row["installs_t0"] = 0.0 if np.isnan(i0) else i0
        row["SM"] = int(m.get("n_maintainers", 0) == 1)
        row["ST_t0"] = int(last["timecreated"] < ts(years_before(t0, 3)))
        rows.append(row)
    df = pd.DataFrame(rows)
    df["support_lag"] = df["support_lag"].fillna(df["support_lag"].median())
    return df


def load_meta():
    from neo4j import GraphDatabase
    from _gds_utils import load_env
    load_env()
    d = GraphDatabase.driver(os.environ["NEO4J_URI"], auth=(os.environ["NEO4J_USER"], os.environ["NEO4J_PASSWORD"]))
    with d.session() as s:
        res = s.run("MATCH (p:Plugin {in_directory:true}) "
                    "RETURN p.component AS c, COUNT {(:Maintainer)-[:MAINTAINS]->(p)} AS nm, "
                    "COUNT {()-[:DEPENDS_ON]->(p)} AS indeg, p.pagerank_dep AS pr")
        meta = {r["c"]: {"n_maintainers": r["nm"], "indeg": r["indeg"], "pr": r["pr"]} for r in res}
    d.close()
    return meta


def logreg():
    return make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000, C=1.0))


def precision_top(y, p, frac=0.10):
    k = max(1, int(round(len(y) * frac)))
    return y[np.argsort(-p, kind="mergesort")[:k]].mean()


def es(x, dec=3):
    return f"{x:.{dec}f}".replace(".", ",")


def comma_axis(ax):
    fmt = FuncFormatter(lambda v, _: f"{v:g}".replace(".", ",").replace("-", "−"))
    ax.xaxis.set_major_formatter(fmt)
    ax.yaxis.set_major_formatter(fmt)


def main():
    versions, installs, meta = load_versions(), load_installs(), load_meta()
    assert len(set(versions["component"]) & set(meta)) / versions["component"].nunique() > 0.95
    assert len(installs) > 2500, len(installs)

    train = build_cohort(versions, installs, meta, T_TRAIN)
    test = build_cohort(versions, installs, meta, T_TEST)
    y_tr, y_te = train["inactivo"].values, test["inactivo"].values
    pre = versions[versions["timecreated"] <= ts(T_TRAIN)]
    notes = [
        f"Cohorte de entrenamiento T0 = {T_TRAIN.date()}: n = {len(train)}, tasa de inactividad = {es(y_tr.mean())}",
        f"Cohorte de evaluación T0 = {T_TEST.date()}: n = {len(test)}, tasa de inactividad = {es(y_te.mean())}",
        f"Plugins presentes en ambas cohortes: {len(set(train.component) & set(test.component))}",
        f"Evidencia de fuga en supportedmoodles: {int((pre['max_supported'] >= 4.0).sum())} versiones publicadas antes de "
        f"{T_TRAIN.date()} declaran soporte para Moodle ≥ 4.0 (publicado en 2022)",
        f"Instalaciones en T0 tomadas del mes anterior al corte ({month_before(T_TEST).strftime('%b %Y')} para la cohorte de evaluación)",
    ]

    models = {
        "Línea base: años desde la última versión": (logreg, ["recency_y"]),
        "Regresión logística principal (16 variables fechadas ≤ T0)": (logreg, MAIN),
        "Regresión logística parsimoniosa (3 variables, exploratoria)": (logreg, PARSIMONIOUS),
        "Regresión logística + variables con fuga (sensibilidad)": (logreg, MAIN + LEAKY),
        "HistGradientBoosting (referencia no lineal)": (
            lambda: HistGradientBoostingClassifier(random_state=SEED, max_iter=300, learning_rate=0.05), MAIN),
    }
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
    preds, res = {}, []
    for name, (mk, feats) in models.items():
        p = mk().fit(train[feats], y_tr).predict_proba(test[feats])[:, 1]
        preds[name] = p
        p_cv = cross_val_predict(mk(), test[feats], y_te, cv=cv, method="predict_proba")[:, 1]
        res.append({"modelo": name, "variables": len(feats), "ROC-AUC": roc_auc_score(y_te, p),
                    "PR-AUC": average_precision_score(y_te, p), "Brier": brier_score_loss(y_te, p),
                    "precisión top-10%": precision_top(y_te, p), "prob. media": p.mean(),
                    "ROC-AUC CV-5 dentro de 2023": roc_auc_score(y_te, p_cv)})
    res = pd.DataFrame(res)

    # bootstrap sobre la cohorte de evaluacion: IC del AUC y diferencia pareada vs. baseline
    # PI4: el indice de riesgo (12_riesgo_sensibilidad.py) recalculado con informacion de T0, sin entrenamiento.
    # En esta poblacion (activos en T0) ST_t0 = 0 para todos, asi que F = SM/2. PageRank y SM son foto 2026.
    assert test["ST_t0"].sum() == 0
    lpr = np.log(test["pr"] / 0.15)
    mmx = lambda s: (s - s.min()) / (s.max() - s.min())  # noqa: E731
    zz = lambda s: (s - s.mean()) / s.std(ddof=0)  # noqa: E731
    idx_models = {
        "Índice de exposición V2 en T0 (sin entrenamiento)":
            ((mmx(np.log1p(test["installs_t0"])) + mmx(lpr)) / 2 * (test["SM"] + test["ST_t0"]) / 2).values,
        "Índice literal V0 en T0 (sin entrenamiento)":
            (zz(test["installs_t0"]) + zz(test["indeg"] + test["pr"]) + test["SM"] + test["ST_t0"]).values,
    }
    for name, s in idx_models.items():
        preds[name] = s
        res.loc[len(res)] = {"modelo": name, "variables": np.nan, "ROC-AUC": roc_auc_score(y_te, s),
                             "PR-AUC": average_precision_score(y_te, s), "Brier": np.nan,
                             "precisión top-10%": precision_top(y_te, s), "prob. media": np.nan,
                             "ROC-AUC CV-5 dentro de 2023": np.nan}

    rng = np.random.default_rng(SEED)
    base_name = next(iter(models))
    boots = {n: [] for n in preds}
    diffs = {n: [] for n in preds if n != base_name}
    n = len(y_te)
    for _ in range(N_BOOT):
        idx = rng.integers(0, n, n)
        if y_te[idx].min() == y_te[idx].max():
            continue
        a_base = roc_auc_score(y_te[idx], preds[base_name][idx])
        for name, p in preds.items():
            a = roc_auc_score(y_te[idx], p[idx])
            boots[name].append(a)
            if name != base_name:
                diffs[name].append(a - a_base)
    res["IC95 ROC-AUC"] = [f"[{es(np.percentile(boots[m], 2.5))}; {es(np.percentile(boots[m], 97.5))}]" for m in res["modelo"]]
    res["ΔAUC vs. baseline [IC95]"] = [
        "—" if m == base_name else
        f"{es(np.mean(diffs[m]))} [{es(np.percentile(diffs[m], 2.5))}; {es(np.percentile(diffs[m], 97.5))}]"
        for m in res["modelo"]]
    res["P(Δ ≤ 0)"] = [np.nan if m == base_name else float(np.mean(np.array(diffs[m]) <= 0)) for m in res["modelo"]]
    res.to_csv(PROCESSED / "inactividad_resultados.csv", index=False)

    drift = pd.DataFrame({"variable": MAIN + LEAKY,
                          "media 2020": [train[f].mean() for f in MAIN + LEAKY],
                          "media 2023": [test[f].mean() for f in MAIN + LEAKY],
                          "diferencia estandarizada": [(test[f].mean() - train[f].mean()) /
                                                       (pd.concat([train[f], test[f]]).std() or 1) for f in MAIN + LEAKY]})
    drift = drift.reindex(drift["diferencia estandarizada"].abs().sort_values(ascending=False).index)
    drift.to_csv(PROCESSED / "inactividad_deriva_cohortes.csv", index=False)

    # coeficientes: solo variables continuas fechadas (las dummies de tipo se reportan aparte, referencia = resto de tipos)
    def coef_table(feats):
        full = logreg().fit(train[feats], y_tr)[-1].coef_[0]
        boot = []
        for _ in range(500):
            idx = rng.integers(0, len(train), len(train))
            if y_tr[idx].min() == y_tr[idx].max():
                continue
            boot.append(logreg().fit(train[feats].iloc[idx], y_tr[idx])[-1].coef_[0])
        boot = np.array(boot)
        t = pd.DataFrame({"variable": feats, "coef": full, "IC95 inf": np.percentile(boot, 2.5, axis=0),
                          "IC95 sup": np.percentile(boot, 97.5, axis=0)})
        t["odds ratio por 1 DE"] = np.exp(t["coef"])
        return t
    coef_main = coef_table(MAIN)
    coef_pars = coef_table(PARSIMONIOUS)
    coef_main.to_csv(PROCESSED / "inactividad_coeficientes_principal.csv", index=False)
    coef_pars.to_csv(PROCESSED / "inactividad_coeficientes_parsimonioso.csv", index=False)

    # figuras a tamano final de pagina (16 cm), texto >= 9 pt, 300 dpi
    plt.rcParams.update({"font.size": 9, "axes.titlesize": 10.5, "axes.labelsize": 9.5,
                         "xtick.labelsize": 9, "ytick.labelsize": 9, "legend.fontsize": 9})
    short = {base_name: "Línea base (1 variable)",
             "Regresión logística principal (16 variables fechadas ≤ T0)": "RL principal (16 var.)",
             "Regresión logística parsimoniosa (3 variables, exploratoria)": "RL parsimoniosa (3 var.)",
             "HistGradientBoosting (referencia no lineal)": "Gradient boosting (16 var.)"}
    fig, ax = plt.subplots(figsize=(TEXT_WIDTH_IN, TEXT_WIDTH_IN * 0.72))
    for name, lab in short.items():
        fpr, tpr, _ = roc_curve(y_te, preds[name])
        ax.plot(fpr, tpr, lw=1.8, label=f"{lab}: AUC {es(roc_auc_score(y_te, preds[name]), 2)}")
    ax.plot([0, 1], [0, 1], ls="--", color="grey", lw=1)
    comma_axis(ax)
    ax.set_xlabel("Tasa de falsos positivos")
    ax.set_ylabel("Tasa de verdaderos positivos")
    ax.set_title(f"Inactividad de publicación a 3 años: validación fuera de tiempo (n = {len(test)})")
    ax.legend(loc="lower right")
    fig.tight_layout()
    fig.savefig(FIGURES / "inactividad_roc.png", dpi=300)
    plt.close(fig)

    c = coef_main[coef_main["variable"].isin(DATED)].sort_values("coef")
    fig, ax = plt.subplots(figsize=(TEXT_WIDTH_IN, TEXT_WIDTH_IN * 0.5))
    yy = np.arange(len(c))
    ax.errorbar(c["coef"], yy, xerr=[c["coef"] - c["IC95 inf"], c["IC95 sup"] - c["coef"]],
                fmt="o", color="#1f4e79", ecolor="#7f9fbf", capsize=3)
    ax.axvline(0, color="grey", lw=1)
    ax.set_yticks(yy, [LABELS[f] for f in c["variable"]])
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}".replace(".", ",").replace("-", "−")))
    ax.set_xlabel("Coeficiente estandarizado e IC 95 %")
    fig.suptitle("Variables asociadas a la inactividad de publicación\n(positivo = más probabilidad de no publicar en 3 años)",
                 fontsize=10.5, x=0.02, ha="left")
    fig.tight_layout()
    fig.savefig(FIGURES / "inactividad_coeficientes.png", dpi=300)
    plt.close(fig)

    fmt = lambda t: t.to_markdown(index=False, floatfmt=".3f")  # noqa: E731
    md = ["# Predicción de inactividad de publicación (experimento supervisado)", "",
          "Generado por `src/analyze/13_prediccion_inactividad.py`. No editar a mano. Diseño y limitaciones en el docstring del script.", "",
          *[f"- {x}" for x in notes], "",
          "## Resultados (evaluación fuera de tiempo sobre la cohorte 2023)", "", fmt(res), "",
          "## Coeficientes del modelo principal (entrenado en la cohorte 2020)", "",
          "Las variables de tipo son indicadoras con referencia «resto de tipos»; `age_y`, `n_versions` y `releases_2y` "
          "son colineales, por lo que solo se interpreta el signo de las variables con IC que no cruza el 0.", "",
          fmt(coef_main), "",
          "## Coeficientes del modelo parsimonioso", "", fmt(coef_pars), "",
          "## Deriva de variables entre cohortes", "", fmt(drift), ""]
    (ROOT / "docs" / "prediccion_inactividad.md").write_text("\n".join(md))
    print("\n".join(md))


if __name__ == "__main__":
    main()
