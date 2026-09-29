#!/usr/bin/env python3
"""Tabla unica de poblaciones de analisis (feedback tutora, 2do borrador, punto 8).

Cada cifra base que aparece en la memoria (2.888, 2.963, 2.876, 2.590, 979,
292, 2.145...) se recalcula aqui en vivo desde Neo4j / data/processed, con su
definicion y filtro exacto, para que el texto cite una sola fuente.

Salidas: data/processed/tabla_poblaciones.csv, docs/tabla_poblaciones.md
Uso: python3 11_poblaciones.py
"""
import csv
import json
import os
import sys
from pathlib import Path

from neo4j import GraphDatabase

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _gds_utils import ROOT, STALE_CUTOFF_UNIX, load_env  # noqa: E402

load_env()
PROCESSED = ROOT / "data" / "processed"
MIN_MONTHS = 24
GITHUB_EXACT = 1909  # fijo: resultado de la ruta GitHub antes de la recuperacion por ZIP (docs/decisions.md)


def es(x, dec=None):
    s = f"{x:,.{dec}f}" if dec is not None else f"{x:,}"
    return s.replace(",", "_").replace(".", ",").replace("_", ".")


def one(session, q):
    return session.run(q).single()[0]


def series_counts():
    found = usable = long_enough = 0
    with open(PROCESSED / "stats_series_raw.jsonl") as f:
        for line in f:
            r = json.loads(line)
            if not r.get("found"):
                continue
            found += 1
            if r.get("installs_series"):
                usable += 1
    with open(PROCESSED / "series_descriptivo_trend.csv") as f:
        long_enough = sum(1 for row in csv.DictReader(f) if int(row["n_months"]) >= MIN_MONTHS)
    return found, usable, long_enough


def main():
    d = GraphDatabase.driver(os.environ["NEO4J_URI"], auth=(os.environ["NEO4J_USER"], os.environ["NEO4J_PASSWORD"]))
    with d.session() as s:
        n_nodes = one(s, "MATCH (p:Plugin) RETURN count(p)")
        n_dir = one(s, "MATCH (p:Plugin {in_directory:true}) RETURN count(p)")
        n_core = one(s, "MATCH (p:Plugin {in_directory:false}) RETURN count(p)")
        n_maint = one(s, "MATCH (p:Plugin {in_directory:true}) WHERE EXISTS {(:Maintainer)-[:MAINTAINS]->(p)} RETURN count(p)")
        n_single = one(s, "MATCH (p:Plugin {in_directory:true}) WHERE COUNT {(:Maintainer)-[:MAINTAINS]->(p)} = 1 RETURN count(p)")
        n_inst = one(s, "MATCH (p:Plugin {in_directory:true}) WHERE p.installations IS NOT NULL RETURN count(p)")
        n_github = one(s, "MATCH (p:Plugin {in_directory:true}) WHERE p.vcs_host = 'github' RETURN count(p)")
        n_vers = one(s, "MATCH (p:Plugin {in_directory:true}) WHERE p.version_in_source IS NOT NULL RETURN count(p)")
        n_exact = one(s, "MATCH (p:Plugin {in_directory:true}) WHERE p.version_exact_match = true RETURN count(p)")
        n_prov = one(s, "MATCH (p:Plugin {in_directory:true}) WHERE EXISTS {()-[:DEPENDS_ON]->(p)} RETURN count(p)")
        n_cons = one(s, "MATCH (p:Plugin {in_directory:true}) WHERE EXISTS {(p)-[:DEPENDS_ON]->()} RETURN count(p)")
        n_stale = one(s, f"MATCH (p:Plugin {{in_directory:true}}) WHERE p.last_release_ts < {STALE_CUTOFF_UNIX} RETURN count(p)")
        n_maintainers = one(s, "MATCH (m:Maintainer) RETURN count(m)")
        # mismo criterio que 02_communities.py para el NMI: grado > 0 en G_soc
        n_soc_ni = one(s, "MATCH (p:Plugin) WHERE p.in_directory <> false AND coalesce(p.degree_soc, 0) > 0 RETURN count(p)")
    d.close()
    s_found, s_usable, s_long = series_counts()

    rows = [
        ("P0", "Plugins del directorio oficial", n_dir, "pluglist.php, snapshot 2026-09-07 (in_directory=true)",
         "Recolección, riesgo, % stale, series"),
        ("P1", "Nodos Plugin del grafo", n_nodes, f"P0 + {n_core} componentes del núcleo de Moodle (mod_data, qtype_multichoice…) que entran solo como destino de DEPENDS_ON",
         "Centralidad (G_dep, G_soc, G_full) y Louvain"),
        ("P2", "Plugins de P0 con ≥1 mantenedor", n_maint, f"P0 menos {n_dir - n_maint} sin relación MAINTAINS",
         f"Bus factor: {es(n_single)}/{es(n_maint)} = {es(100 * n_single / n_maint, 1)}% con mantenedor único"),
        ("P3", "Plugins de P0 con dato de instalaciones", n_inst, f"P0 menos {n_dir - n_inst} sin estadística pública",
         "Término z(instalaciones) del índice de riesgo"),
        ("P4", "Plugins de P0 con repositorio en GitHub", n_github, f"vcs_host=github; los {n_dir - n_github} restantes usan otro host o ninguno",
         "Extracción de version.php vía GitHub"),
        ("P5", "Plugins de P0 con versión de version.php conocida", n_vers, f"GitHub + recuperación por ZIP del residual; {es(n_exact)} con coincidencia exacta con el directorio",
         "Validación de la calidad de datos (Anexo)"),
        ("P5b", "Residual sin coincidencia exacta vía GitHub", n_dir - GITHUB_EXACT,
         f"P0 menos los {es(GITHUB_EXACT)} plugins cuyo version.php de GitHub coincide exactamente con la última versión del directorio (reconciliación en docs/decisions.md, 2026-09-08)",
         "Recuperación por ZIP del directorio (Anexo B)"),
        ("P6", "Proveedores (in-degree DEPENDS_ON > 0)", n_prov, "Plugins de P0 de los que depende al menos otro plugin",
         "Análisis de dependencias y fragilidad transitiva"),
        ("P7", "Consumidores (out-degree DEPENDS_ON > 0)", n_cons, "Plugins de P0 que declaran al menos una dependencia", "Ídem"),
        ("P8", "Plugins con serie de instalaciones", s_usable, f"{es(s_found)} encontrados en stats.php, con serie no vacía",
         "Capítulo de series temporales"),
        ("P9", f"Series con ≥{MIN_MONTHS} meses", s_long, f"Subconjunto de P8 con historia suficiente para comparar pico y últimos 12 meses",
         "Cuota relativa (mediana -0,006 pp)"),
        ("P10", "Stale (sin release > 3 años)", n_stale, "last_release_ts < 2023-09-10 UTC, sobre P0",
         f"{es(100 * n_stale / n_dir, 1)}% de P0; señal del índice de riesgo"),
        ("P11", "Plugins no aislados en G_soc", n_soc_ni, "P0 con al menos una arista DEPENDS_ON o CO_MAINTAINED (degree_soc > 0)",
         "NMI entre comunidades de Louvain y categoría oficial"),
        ("M0", "Mantenedores", n_maintainers, "Nodos Maintainer (personas u organizaciones)", "G_maint, bus factor, Gini"),
    ]

    with open(PROCESSED / "tabla_poblaciones.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "poblacion", "n", "definicion", "uso"])
        w.writerows(rows)

    md = ["# Tabla de poblaciones de análisis", "",
          "Generada por `src/analyze/11_poblaciones.py` desde Neo4j y `data/processed/`. No editar a mano.", "",
          "| Id | Población | N | Definición / filtro | Dónde se usa |", "|---|---|---:|---|---|"]
    for r in rows:
        md.append(f"| {r[0]} | {r[1]} | {es(r[2])} | {r[3]} | {r[4]} |")
    (ROOT / "docs" / "tabla_poblaciones.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
