#!/usr/bin/env python3
"""Indice de exposicion al riesgo: formalizacion, variantes y sensibilidad del
umbral de inactividad (feedback tutora, 2do borrador, punto 3).

Poblacion: plugins del directorio con >=1 mantenedor (P2 en
docs/tabla_poblaciones.md, n = 2.876). Los 12 plugins sin ningun mantenedor
no se puntuan: todos carecen ademas de estadistica de instalaciones y son en su
mayoria altas recientes (2025-2026); se tratan como registros incompletos
(dato faltante), no como huerfanos.

Senales (0/1):
  SM = exactamente un mantenedor (bus factor 1)
  ST = ultima release anterior al corte T (T = 2, 3 [principal] y 5 anios antes
       del cierre de datos, 2026-09-10)
Magnitudes de impacto:
  inst = instalaciones activas declaradas (1 plugin sin dato -> 0, declarado)
  pr   = PageRank en G_dep (valor minimo 0,15 = sin dependientes). Se usa una
         sola medida de centralidad: in-degree y PageRank en G_dep tienen
         Spearman ~0,999 en esta poblacion, sumarlas duplica el termino.

Variantes:
  V0 literal del plan (03_risk.py), se conserva como referencia:
       R0 = z(inst) + z(indeg + pr) + SM + ST
     Dominada por escala: z(inst) llega a ~19,6 y z(indeg+pr) a ~21,4 frente a
     0/1 de las senales, asi que ordena por popularidad, no por fragilidad.
  V1 aditiva con transformacion logaritmica (prueba de robustez):
       R1 = z(log1p inst) + z(log(pr / 0,15)) + SM + ST
  V2 PRINCIPAL, exposicion = impacto x fragilidad:
       I  = ( mm(log1p inst) + mm(log(pr / 0,15)) ) / 2      en [0, 1]
       F  = (SM + ST) / 2                                      en {0, 0,5, 1}
       E  = I * F
     mm() = normalizacion min-max. No es una probabilidad: SM y ST son
     senales de fragilidad, no probabilidades de fallo. En la practica el
     top de E = plugins con SM=1 y ST=1 ordenados por impacto; con F=0,5 el
     maximo alcanzable es 0,5.
Desempate explicito en todos los rankings: score desc, inst desc, component asc.

Confusor: plugins que fueron parte del nucleo (src/analyze/_ex_core.py) se
marcan y se repite el top-30 sin ellos.

Salidas: data/processed/riesgo_*.csv, docs/riesgo_sensibilidad.md
Uso: python3 12_riesgo_sensibilidad.py
"""
import sys
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _ex_core import EX_CORE, INTO_CORE  # noqa: E402
from _gds_utils import ROOT, STALE_CUTOFF_UNIX  # noqa: E402

PROCESSED = ROOT / "data" / "processed"
DATA_CLOSE = datetime(2026, 9, 10, tzinfo=timezone.utc)
YEARS = [2, 3, 5]
TOP = 30
VARIANTS = ["V0", "V1", "V2"]


def cutoff(years):
    return int(DATA_CLOSE.replace(year=DATA_CLOSE.year - years).timestamp())


def z(s):
    return (s - s.mean()) / s.std(ddof=0)


def mm(s):
    return (s - s.min()) / (s.max() - s.min())


def scores(df, years):
    inst = df["installations"].fillna(0)
    indeg = df["in_degree_dep"]
    pr = df["pagerank_dep"]
    log_pr = np.log(pr / pr.min())
    sm = df["single_maintainer"]
    st = (df["last_release_ts"] < cutoff(years)).astype(int)
    out = df[["component"]].copy()
    out["installations"] = inst
    out["SM"], out["ST"] = sm, st
    out["V0"] = z(inst) + z(indeg + pr) + sm + st
    out["V1"] = z(np.log1p(inst)) + z(log_pr) + sm + st
    out["I"] = (mm(np.log1p(inst)) + mm(log_pr)) / 2
    out["F"] = (sm + st) / 2
    out["V2"] = out["I"] * out["F"]
    out["ex_core"] = out["component"].isin(EX_CORE).astype(int)
    return out


def ranked(r, v):
    return r.sort_values([v, "installations", "component"], ascending=[False, False, True])


def top(r, v, n=TOP):
    return set(ranked(r, v)["component"].head(n))


def jaccard(a, b):
    return len(a & b) / len(a | b)


def md_table(df, fmt=".3f"):
    return df.to_markdown(index=False, floatfmt=fmt)


def main():
    raw = pd.read_csv(PROCESSED / "risk_all_plugins.csv")
    assert len(raw) == 2888, len(raw)
    assert cutoff(3) == STALE_CUTOFF_UNIX, "el corte de 3 anios debe coincidir con Fases 4-5"
    assert raw["last_release_ts"].notna().all(), "ST quedaria en 0 silenciosamente con NaN"
    assert raw[["in_degree_dep", "pagerank_dep"]].notna().all().all()
    missing_ex = set(EX_CORE) - set(raw["component"])
    assert not missing_ex, f"ex_core fuera del directorio: {missing_ex}"

    # V0 sobre los 2.888 reproduce exactamente el risk_score publicado
    assert np.allclose(scores(raw, 3)["V0"].values, raw["risk_score"].values), "V0 no reproduce 03_risk.py"

    no_maint = raw[raw["n_maintainers"] == 0]
    df = raw[raw["n_maintainers"] > 0].reset_index(drop=True)
    no_inst = df[df["installations"].isna()]["component"].tolist()
    rho_indeg_pr = spearmanr(df["in_degree_dep"], df["pagerank_dep"]).statistic

    runs = {y: scores(df, y) for y in YEARS}
    base = runs[3]

    notes = [
        f"- Población puntuada: {len(df)} plugins con ≥1 mantenedor; excluidos {len(no_maint)} sin mantenedor "
        f"({int(no_maint['installations'].isna().sum())} de ellos sin dato de instalaciones).",
        f"- Plugins puntuados sin dato de instalaciones (tomados como 0): {', '.join(no_inst) or 'ninguno'}.",
        f"- Spearman(in-degree, PageRank) en G_dep = {rho_indeg_pr:.4f} → se usa solo PageRank.",
        f"- Plugins ex-núcleo marcados: {len(EX_CORE)} (evidencia literal en `_ex_core.py`); "
        f"incorporados al núcleo: {len(INTO_CORE)}.",
    ]

    # 1. escala de cada termino
    inst = base["installations"]
    pr = df["pagerank_dep"]
    terms = {
        "V0": {"z(inst)": z(inst), "z(indeg+pr)": z(df["in_degree_dep"] + pr)},
        "V1": {"z(log1p inst)": z(np.log1p(inst)), "z(log pr/0,15)": z(np.log(pr / pr.min()))},
        "V2": {"mm(log1p inst)/2": mm(np.log1p(inst)) / 2, "mm(log pr/0,15)/2": mm(np.log(pr / pr.min())) / 2},
    }
    scale = []
    for v, ts in terms.items():
        for t, s in ts.items():
            scale.append({"variante": v, "término": t, "desv. típica": s.std(ddof=0), "máximo": s.max()})
        for t in ["SM", "ST"]:
            s = base[t] if v != "V2" else base[t] / 2
            scale.append({"variante": v, "término": t if v != "V2" else f"{t}/2 (dentro de F)",
                          "desv. típica": s.std(ddof=0), "máximo": s.max()})
    scale = pd.DataFrame(scale)

    # 2. composicion del top-30 (T = 3)
    comp = []
    for v in VARIANTS:
        t = ranked(base, v).head(TOP)
        comp.append({"variante": v, "con SM": int(t["SM"].sum()), "con ST": int(t["ST"].sum()),
                     "sin ninguna señal": int(((t["SM"] == 0) & (t["ST"] == 0)).sum()),
                     "ex-núcleo": int(t["ex_core"].sum()),
                     "mediana instalaciones": float(t["installations"].median())})
    comp = pd.DataFrame(comp)

    # 3. concordancia entre variantes (T = 3)
    agree = []
    for a, b in combinations(VARIANTS, 2):
        agree.append({"par": f"{a}–{b}", "Spearman": spearmanr(base[a], base[b]).statistic,
                      f"Jaccard top-{TOP}": jaccard(top(base, a), top(base, b))})
    agree = pd.DataFrame(agree)

    # 4. sensibilidad al umbral T
    sens = []
    for y in YEARS:
        r = runs[y]
        row = {"T (años)": y, "corte": datetime.fromtimestamp(cutoff(y), timezone.utc).date().isoformat(),
               "stale": int(r["ST"].sum()), "% stale": r["ST"].mean() * 100,
               "frágiles (SM y ST)": int(((r["SM"] == 1) & (r["ST"] == 1)).sum())}
        for v in VARIANTS:
            row[f"{v} ρ vs T=3"] = spearmanr(r[v], base[v]).statistic
            row[f"{v} J top-{TOP} vs T=3"] = jaccard(top(r, v), top(base, v))
        sens.append(row)
    sens = pd.DataFrame(sens)

    # 5. nucleo robusto y robustez sin ex-nucleo (variante principal)
    core = set.intersection(*[top(runs[y], "V2") for y in YEARS])
    no_ex = base[base["ex_core"] == 0]
    j_no_ex = jaccard(top(base, "V2") - set(EX_CORE), top(no_ex, "V2"))
    rob = pd.DataFrame([{
        f"top-{TOP} V2 estable con T=2, 3 y 5": len(core),
        f"Jaccard top-{TOP} V2 con vs. sin ex-núcleo (sin contar los ex-núcleo)": j_no_ex,
    }])

    # ranking principal exportado
    out = ranked(base, "V2")[["component", "installations", "SM", "ST", "I", "F", "V2", "V1", "V0", "ex_core"]]
    out = out.rename(columns={"V2": "E_exposicion"})
    out["rank"] = np.arange(1, len(out) + 1)
    out["en_nucleo_robusto"] = out["component"].isin(core).astype(int)
    out.to_csv(PROCESSED / "riesgo_exposicion_T3.csv", index=False)
    for name, t in [("escala", scale), ("top30_composicion", comp), ("variantes", agree),
                    ("umbral", sens), ("robustez", rob)]:
        t.to_csv(PROCESSED / f"riesgo_sensibilidad_{name}.csv", index=False)

    top_tbl = out.head(TOP)[["rank", "component", "installations", "I", "E_exposicion", "ex_core", "en_nucleo_robusto"]]
    md = ["# Índice de exposición al riesgo: variantes y sensibilidad del umbral de inactividad", "",
          "Generado por `src/analyze/12_riesgo_sensibilidad.py`. No editar a mano. Fórmulas en el docstring del script.", "",
          *notes, "",
          "## Escala de cada término (T = 3 años)", "",
          "Desviación típica y máximo de la contribución de cada término al índice; muestra qué término domina el orden.", "",
          md_table(scale), "",
          f"## Composición del top-{TOP} (T = 3 años)", "", md_table(comp, ".0f"), "",
          "## Concordancia entre variantes (T = 3 años)", "", md_table(agree), "",
          "## Sensibilidad al umbral de inactividad (respecto a T = 3 años)", "", md_table(sens), "",
          "## Robustez de la variante principal (V2)", "", md_table(rob), "",
          f"## Top-{TOP} de la variante principal (V2, T = 3 años)", "", md_table(top_tbl), ""]
    (ROOT / "docs" / "riesgo_sensibilidad.md").write_text("\n".join(md))
    print("\n".join(md))


if __name__ == "__main__":
    main()
