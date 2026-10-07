#!/usr/bin/env python3
"""Grafo interactivo del G_soc (memoria v4): genera figures/grafo_interactivo.html.

Une el export de 15_grafo_completo.py (figures/grafo_completo.json: posiciones ForceAtlas2,
comunidades de Louvain, mantenedores) con el indice de riesgo principal
(data/processed/riesgo_exposicion_T3.csv: SM, ST, E = I x F y su puesto) y lo inserta en la
plantilla src/analyze/templates/grafo_interactivo.html (d3 desde cdnjs, sin servidor).
La pagina permite buscar un plugin, filtrar por tipo y comunidad y colorear por comunidad,
por indice de riesgo o por senales de fragilidad.
No requiere Neo4j. Uso: python3 src/analyze/18_grafo_interactivo.py
"""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TPL = ROOT / "src/analyze/templates/grafo_interactivo.html"
OUT = ROOT / "figures/grafo_interactivo.html"


def main():
    data = json.loads((ROOT / "figures/grafo_completo.json").read_text())
    risk = {}
    with (ROOT / "data/processed/riesgo_exposicion_T3.csv").open() as f:
        for r in csv.DictReader(f):
            risk[r["component"]] = (int(r["SM"]), int(r["ST"]), round(float(r["E_exposicion"]), 4), int(r["rank"]))
    assert len(risk) == 2876, len(risk)
    hit = 0
    for n in data["nodes"]:
        if n["id"] in risk:
            n["sm"], n["st"], n["e"], n["rank"] = risk[n["id"]]
            hit += 1
    data["n_risk"] = len(risk)
    tpl = TPL.read_text()
    assert tpl.count("__DATA__") == 1
    OUT.write_text(tpl.replace("__DATA__", json.dumps(data, ensure_ascii=False, separators=(",", ":"))))
    print(f"{OUT.name}: {len(data['nodes'])} nodos, {hit} con índice de riesgo")


if __name__ == "__main__":
    main()
