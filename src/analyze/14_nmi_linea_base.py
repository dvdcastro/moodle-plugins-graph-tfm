#!/usr/bin/env python3
"""Linea base nula del NMI entre comunidades de Louvain (G_soc) y categoria oficial.

Misma poblacion que 02_communities.py: plugins del directorio con degree_soc > 0
(P11 en docs/tabla_poblaciones.md). Se permuta la asignacion de comunidad 1.000 veces
(semilla 20260913) conservando el tamano de cada comunidad, y se compara el NMI
real con la distribucion nula.

Salida: docs/nmi_linea_base.md
Uso: python3 14_nmi_linea_base.py
"""
import os
import sys
from pathlib import Path

import numpy as np
from neo4j import GraphDatabase
from sklearn.metrics import normalized_mutual_info_score

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _gds_utils import ROOT, load_env  # noqa: E402

load_env()
SEED = 20260913
N_PERM = 1000


def main():
    d = GraphDatabase.driver(os.environ["NEO4J_URI"], auth=(os.environ["NEO4J_USER"], os.environ["NEO4J_PASSWORD"]))
    with d.session() as s:
        rows = s.run("MATCH (p:Plugin) WHERE p.in_directory <> false AND coalesce(p.degree_soc, 0) > 0 "
                     "RETURN p.component AS c, p.louvain_soc AS comm, p.plugin_type AS cat ORDER BY c").data()
    d.close()
    comm = np.array([r["comm"] for r in rows])
    cat = np.array([r["cat"] for r in rows])
    real = normalized_mutual_info_score(comm, cat)
    rng = np.random.default_rng(SEED)
    null = np.array([normalized_mutual_info_score(rng.permutation(comm), cat) for _ in range(N_PERM)])
    z = (real - null.mean()) / null.std(ddof=1)
    lines = ["# Línea base nula del NMI (Louvain G_soc frente a categoría oficial)", "",
             "Generado por `src/analyze/14_nmi_linea_base.py`. No editar a mano.", "",
             f"- n = {len(rows)} plugins no aislados en G_soc",
             f"- NMI real = {real:.6f}",
             f"- NMI bajo permutación ({N_PERM} permutaciones, semilla {SEED}): media = {null.mean():.6f}, "
             f"desviación típica = {null.std(ddof=1):.6f}, máximo = {null.max():.6f}",
             f"- diferencia = {real - null.mean():.6f}; z = {z:.2f}",
             f"- permutaciones con NMI >= real: {int((null >= real).sum())} de {N_PERM} (p empírico < {1 / (N_PERM + 1):.4f})"]
    (ROOT / "docs" / "nmi_linea_base.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
