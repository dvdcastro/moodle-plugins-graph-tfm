"""Paso 5: evaluacion determinista (sin LLM-juez) contra el gold congelado.

Uso: python 05_evaluate.py cutline|full [--figure]
Sistemas: baseline (vectorial), vecrel (ablacion "vectorial + relaciones":
mismas fichas que el baseline + hechos del grafo sobre ellas) y graphrag; se
evaluan los que tengan results/<modo>/answers_<sistema>.jsonl.
Salida: results/<modo>/metrics_per_question.csv, metrics.md; con --figure,
figures/graphrag_resultados.png (15 cm, estilo _fig_style).

Metrica principal: F1 de citas en T1-T4 (tipos con lista gold relacional).
T5 (cumplimiento de la restriccion) se reporta aparte: no es comparable (la
expansion de GraphRAG para T5 ES la restriccion). T6 es el control semantico.
"""
import hashlib
import json
import re
import sys

import numpy as np
import pandas as pd
from scipy.stats import wilcoxon

import config as C

CITE = re.compile(r"\[\s*`?([a-z][a-z0-9]*_[a-z0-9_]*[a-z0-9])`?\s*\]|`([a-z][a-z0-9]*_[a-z0-9_]*[a-z0-9])`")
TYPE_LABEL = {"T1": "T1 Dependientes", "T2": "T2 Dependencias", "T3": "T3 Co-mantenimiento",
              "T4": "T4 Comunidad frágil", "T5": "T5 Alternativas", "T6": "T6 Semántica (control)"}
N_BOOT = 10_000


def citations(text, components):
    toks = [a or b for a, b in CITE.findall(text)]
    toks = list(dict.fromkeys(toks))
    return [t for t in toks if t in components], [t for t in toks if t not in components]


def prf(pred, gold):
    pred, gold = set(pred), set(gold)
    tp = len(pred & gold)
    p = tp / len(pred) if pred else 0.0
    r = tp / len(gold) if gold else 0.0
    f = 2 * p * r / (p + r) if p + r else 0.0
    return p, r, f


def score(q, a, components):
    seed = q.get("seed")
    ctx = [c for c in a["components"] if c != seed]
    valid, invalid = citations(a["answer"], components)
    cited = [c for c in valid if c != seed]
    row = {"id": q["id"], "type": q["type"], "system": a["system"],
           "n_cited": len(cited), "n_invalid": len(invalid), "no_citations": int(not valid),
           "prompt_tokens": (a.get("usage") or {}).get("promptTokenCount", np.nan)}
    # fidelidad: citas que existen en el grafo y estaban en el contexto. La semilla
    # se excluye (aparece en la propia pregunta; citarla no es alucinar).
    allc = cited + invalid
    row["faithfulness"] = (sum(c in a["components"] for c in cited) / len(allc)) if allc else np.nan
    if q["type"] == "T5":
        sat = set(q["gold_satisfying"])
        row["recall_at_k"] = np.nan
        row["ctx_compliance"] = sum(c in sat for c in ctx) / len(ctx) if ctx else 0.0
        row["precision"] = row["recall"] = row["f1"] = np.nan
        row["compliance"] = sum(c in sat for c in cited) / len(cited) if cited else 0.0
        row["primary"] = row["compliance"]
    else:
        gold = set(q["gold"])
        row["recall_at_k"] = len(gold & set(ctx)) / len(gold)
        row["precision"], row["recall"], row["f1"] = prf(cited, gold)
        row["primary"] = row["f1"]
    if q["type"] == "T3":
        al = a["answer"].lower()
        row["maint_named"] = np.mean([m.lower() in al for m in q["gold_maintainers"]])
    if q["type"] == "T2":
        row["stale_recall_ctx"] = (len(set(q["gold_stale"]) & set(ctx)) / len(q["gold_stale"])
                                   if q["gold_stale"] else np.nan)
    if a["system"] in ("graphrag", "vecrel") and seed:
        row["link_ok"] = int(seed in a["seeds"])
    return row


SYSTEMS = ("baseline", "vecrel", "graphrag")
SYS_LABEL = {"baseline": "vectorial", "vecrel": "vectorial + relaciones", "graphrag": "GraphRAG"}
PAIRS = (("baseline", "graphrag"), ("baseline", "vecrel"), ("vecrel", "graphrag"))
REL = ("T1", "T2", "T3", "T4")          # headline: tipos relacionales con lista gold


def fmt(x, nd=2, sign=False):
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "—"
    s = f"{x:+.{nd}f}" if sign else f"{x:.{nd}f}"
    return s.replace(".", ",").replace("-", "−")


def pfmt(p):
    if p is None or np.isnan(p):
        return "—"
    if p < 0.001:
        m, e = f"{p:.1e}".split("e")
        return f"{m.replace('.', ',')}·10^{int(e)}"
    return fmt(p, 3)


def bootstrap(d, types, rng):
    """IC 95 % de la media de d con tres esquemas de remuestreo:
    paired     — preguntas i.i.d. (ignora la estructura plantilla × semilla);
    stratified — remuestreo dentro de cada tipo/plantilla (n_t fijo por tipo);
    cluster    — dos etapas: se remuestrean plantillas y, dentro de cada una,
                 sus preguntas (con 4-5 plantillas es conservador y tosco)."""
    d = np.asarray(d, float)
    types = np.asarray(types)
    groups = [np.where(types == t)[0] for t in dict.fromkeys(types)]
    out = {}
    idx = rng.integers(0, len(d), (N_BOOT, len(d)))
    out["paired"] = d[idx].mean(1)
    strat = np.zeros(N_BOOT)
    for g in groups:
        strat += d[g][rng.integers(0, len(g), (N_BOOT, len(g)))].sum(1)
    out["stratified"] = strat / len(d)
    clus = np.empty(N_BOOT)
    for b in range(N_BOOT):
        pick = rng.integers(0, len(groups), len(groups))
        vals = [d[groups[k]][rng.integers(0, len(groups[k]), len(groups[k]))] for k in pick]
        clus[b] = np.concatenate(vals).mean()
    out["cluster"] = clus
    return {k: (float(np.quantile(v, 0.025)), float(np.quantile(v, 0.975))) for k, v in out.items()}


def wilcoxon_exact(d):
    nz = d[d != 0]
    if len(nz) == 0:
        return 1.0
    try:
        return float(wilcoxon(nz, zero_method="wilcox", method="exact").pvalue)
    except ValueError:
        return np.nan


def paired(df, metric, a, b, rng):
    w = df.pivot(index="id", columns="system", values=metric)[[a, b]].dropna()
    typ = df.drop_duplicates("id").set_index("id").loc[w.index, "type"].values
    d = (w[b] - w[a]).values
    ci = bootstrap(d, typ, rng) if len(d) else {}
    return {"n": len(d), "mean_a": w[a].mean(), "mean_b": w[b].mean(), "diff": d.mean(),
            "ci": ci, "p": wilcoxon_exact(d),
            "wins": int((d > 0).sum()), "ties": int((d == 0).sum()), "losses": int((d < 0).sum())}


def ci_s(ci):
    return f"[{fmt(ci[0], 2, True)}; {fmt(ci[1], 2, True)}]"


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "cutline"
    outdir = C.RESULTS / mode
    gold = {q["id"]: q for q in map(json.loads, C.GOLD.read_text().splitlines())}
    sha = hashlib.sha256(C.GOLD.read_bytes()).hexdigest()
    frozen = (C.GOLD.parent / "questions.sha256").read_text().split()[0]
    assert sha == frozen, "gold/questions.jsonl no coincide con el hash congelado"
    with C.driver() as d, d.session() as s:
        components = {r["c"] for r in s.run("MATCH (p:Plugin) RETURN p.component AS c")}
    systems = [s for s in SYSTEMS if (outdir / f"answers_{s}.jsonl").exists()]
    rows = []
    for system in systems:
        for line in (outdir / f"answers_{system}.jsonl").read_text().splitlines():
            a = json.loads(line)
            rows.append(score(gold[a["id"]], a, components))
    df = pd.DataFrame(rows)
    for col in ("compliance", "link_ok", "recall_at_k", "precision", "recall", "f1"):
        if col not in df:
            df[col] = np.nan
    df.to_csv(outdir / "metrics_per_question.csv", index=False)
    pairs = [p for p in PAIRS if p[0] in systems and p[1] in systems]
    rng = np.random.default_rng(20260928)
    types = sorted(df.type.unique())
    rel = df[df.type.isin(REL)]

    L = [f"# Métricas — modo `{mode}` ({', '.join(SYS_LABEL[s] for s in systems)})", "",
         f"Gold: `gold/questions.jsonl` (sha256 `{sha[:16]}…`), {df.id.nunique()} preguntas. "
         f"K = {C.K} fichas en los tres sistemas. Modelos: `{C.EMBED_MODEL}` ({C.EMBED_DIM} d), "
         f"`{C.GEN_MODEL}` (temperature 0, thinkingBudget 0). Bootstrap {N_BOOT} remuestreos, IC 95 %: "
         "pareado (preguntas i.i.d.), estratificado por tipo y por conglomerados en dos etapas "
         "(plantilla, luego pregunta). Wilcoxon exacto de rangos con signo sobre las diferencias no nulas.", ""]

    # --- titular T1-T4
    if set(REL) & set(types):
        L += [f"## Titular: tipos relacionales con lista gold (T1–T4, n = {rel.id.nunique()})", "",
              "| Sistema | F1 citas | Recall@20 | Precisión citas | Recall citas |", "|---|---|---|---|---|"]
        for sy in systems:
            g = rel[rel.system == sy]
            L.append(f"| {SYS_LABEL[sy]} | {fmt(g.f1.mean())} | {fmt(g.recall_at_k.mean())} | "
                     f"{fmt(g.precision.mean())} | {fmt(g.recall.mean())} |")
        L += ["", "Contrastes pareados en T1–T4 (Δ = segundo − primero):", "",
              "| Contraste | Métrica | Δ | IC pareado | IC estratificado | IC conglomerados | Wilcoxon exacto p | G/E/P |",
              "|---|---|---|---|---|---|---|---|"]
        for a, b in pairs:
            for m, lab in (("f1", "F1"), ("recall_at_k", "Recall@20"), ("precision", "Precisión")):
                r = paired(rel, m, a, b, rng)
                if m == "recall_at_k" and a == "baseline" and b == "vecrel":
                    pass  # idéntico por construcción (Δ = 0)
                L.append(f"| {SYS_LABEL[b]} − {SYS_LABEL[a]} | {lab} | {fmt(r['diff'], 2, True)} | "
                         f"{ci_s(r['ci']['paired'])} | {ci_s(r['ci']['stratified'])} | "
                         f"{ci_s(r['ci']['cluster'])} | {pfmt(r['p'])} | "
                         f"{r['wins']}/{r['ties']}/{r['losses']} |")
        L.append("")

    # --- medias por tipo
    L += ["## Medias por tipo y sistema", "",
          "| Tipo | n | Sistema | Recall@20 | P citas | R citas | F1 citas | Cumplim. T5 | Fidelidad (n def.) | Sin citas | Tokens prompt |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    for t in types + ["T1–T4", "Todas"]:
        sub = df if t == "Todas" else rel if t == "T1–T4" else df[df.type == t]
        for sy in systems:
            g = sub[sub.system == sy]
            L.append(f"| {TYPE_LABEL.get(t, t)} | {g.id.nunique()} | {SYS_LABEL[sy]} | "
                     f"{fmt(g.recall_at_k.mean())} | {fmt(g.precision.mean())} | {fmt(g.recall.mean())} | "
                     f"{fmt(g.f1.mean())} | {fmt(g.compliance.mean())} | "
                     f"{fmt(g.faithfulness.mean())} ({int(g.faithfulness.notna().sum())}) | "
                     f"{int(g.no_citations.sum())} | {g.prompt_tokens.mean():.0f} |")

    # --- contrastes por tipo (F1; T5 cumplimiento, aparte)
    L += ["", "## Contrastes por tipo (F1 de citas; T5: cumplimiento, NO comparable)", "",
          "| Tipo | Contraste | n | Media 1º | Media 2º | Δ | IC pareado | Wilcoxon exacto p | G/E/P |",
          "|---|---|---|---|---|---|---|---|---|"]
    for t in types:
        sub = df[df.type == t]
        for a, b in pairs:
            r = paired(sub, "primary", a, b, rng)
            L.append(f"| {TYPE_LABEL.get(t, t)} | {SYS_LABEL[b]} − {SYS_LABEL[a]} | {r['n']} | "
                     f"{fmt(r['mean_a'])} | {fmt(r['mean_b'])} | {fmt(r['diff'], 2, True)} | "
                     f"{ci_s(r['ci']['paired'])} | {pfmt(r['p'])} | {r['wins']}/{r['ties']}/{r['losses']} |")

    # --- tokens de contexto
    tok = df.pivot(index="id", columns="system", values="prompt_tokens")
    L += ["", "## Longitud del contexto (tokens de prompt según `usageMetadata`)", ""]
    for sy in systems:
        L.append(f"- {SYS_LABEL[sy]}: media {tok[sy].mean():.0f} tokens (T1–T4: "
                 f"{tok.loc[tok.index.str[:2].isin(REL), sy].mean():.0f})")
    for sy in systems:
        if sy == "baseline":
            continue
        ratio = tok[sy] / tok["baseline"] - 1
        L.append(f"- {SYS_LABEL[sy]} vs. vectorial, exceso por pregunta: mediana "
                 f"{fmt(100 * ratio.median(), 0)} %, rango [{fmt(100 * ratio.min(), 0)} %; "
                 f"{fmt(100 * ratio.max(), 0)} %]")

    # --- otros
    for sy in ("vecrel", "graphrag"):
        g = df[(df.system == sy) & df.link_ok.notna()] if "link_ok" in df else df.iloc[:0]
        if len(g):
            L.append(f"- Enlazado de entidades ({SYS_LABEL[sy]}): {int(g.link_ok.sum())}/{len(g)}")
    if "maint_named" in df:
        t3 = df[df.type == "T3"]
        L.append("- T3, fracción de mantenedores gold nombrados: " + ", ".join(
            f"{SYS_LABEL[s]} {fmt(t3[t3.system == s].maint_named.mean())}" for s in systems))
    if "stale_recall_ctx" in df:
        t2 = df[df.type == "T2"]
        L.append("- T2, recall en contexto de las dependencias sin release >3 años: " + ", ".join(
            f"{SYS_LABEL[s]} {fmt(t2[t2.system == s].stale_recall_ctx.mean())}" for s in systems))
    L += ["", f"Gasto API acumulado estimado (todo el proyecto): US$ {C.spend():.3f}", ""]
    (outdir / "metrics.md").write_text("\n".join(L))
    print("\n".join(L))
    if "--figure" in sys.argv:
        figure(df, systems)


def figure(df, systems):
    sys.path.insert(0, str(C.ROOT / "src" / "analyze"))
    import _fig_style as S
    import matplotlib.pyplot as plt
    S.apply()
    col = {"baseline": "#b8b0a4", "vecrel": "#c98b3b", "graphrag": "#2f5d68"}
    lab = {"baseline": "RAG vectorial", "vecrel": "Vectorial + relaciones", "graphrag": "GraphRAG"}
    groups = [("T1", ["T1"]), ("T2", ["T2"]), ("T3", ["T3"]), ("T4", ["T4"]),
              ("T1–T4", list(REL)), ("T6", ["T6"])]
    name = {"T1": "T1\nDepend.", "T2": "T2\nDepend.\n+ estado", "T3": "T3\nCo-mant.",
            "T4": "T4\nComun.\nfrágil", "T1–T4": "T1–T4\nagregado", "T6": "T6\nControl\nsemántico"}
    fig, axes = plt.subplots(2, 1, figsize=(S.TEXT_WIDTH_IN - 0.05, 5.0), sharex=True)
    x = np.arange(len(groups), dtype=float)
    x[-2:] += 0.35                       # separa el agregado y el control
    w = 0.27
    for ax, metric, title in ((axes[0], "recall_at_k", "Recuperación: recall@20 del contexto"),
                              (axes[1], "f1", "Respuesta: F1 de citas")):
        for j, sy in enumerate(systems):
            off = (j - (len(systems) - 1) / 2) * w
            vals = np.array([df[(df.system == sy) & df.type.isin(ts)][metric].mean() for _, ts in groups])
            ax.bar(x + off, vals, w, color=col[sy], label=lab[sy],
                   edgecolor="black" if sy == "vecrel" else "none", linewidth=0.4)
            if metric == "f1":
                for xi, v in zip(x, vals):
                    ax.text(xi + off, v + 0.02, S.num(v, 2), ha="center", va="bottom",
                            fontsize=9, rotation=90)
        ax.axvline((x[3] + x[4]) / 2, color="#999999", lw=0.6, ls=":")
        ax.set_title(title, loc="left")
        ax.set_ylim(0, 1.3 if metric == "f1" else 1.05)
        ax.set_yticks(np.arange(0, 1.01, 0.25))
        ax.yaxis.set_major_formatter(S.comma_formatter(2))
        ax.spines[["top", "right"]].set_visible(False)
        ax.set_ylabel("Media por pregunta")
    n = {g: df[(df.system == systems[0]) & df.type.isin(ts)].id.nunique() for g, ts in groups}
    axes[1].set_xticks(x, [f"{name[g]}\nn = {n[g]}" for g, _ in groups])
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, loc="upper center", bbox_to_anchor=(0.5, 1.0), ncol=3, frameon=False)
    fig.text(0.01, 0.0, "T5 (alternativas) no se muestra: solo tiene cumplimiento de la restricción, "
             "que GraphRAG\nsatisface por construcción; no es comparable con el F1 (ver texto).",
             fontsize=9, ha="left", va="top")
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    S.save(fig, C.FIG)


if __name__ == "__main__":
    main()
