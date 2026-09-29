"""Utilidades compartidas por los scripts de src/analyze/. Extraido de
01_centrality.py durante la Fase 4 para no duplicar el mismo patron de
proyeccion/limpieza GDS en cada script nuevo (habia sido senalado como
duplicacion menor por la revision de agentes de Fase 3)."""
import os
from contextlib import contextmanager
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def load_env() -> None:
    env_path = ROOT / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())


# Umbral compartido entre Fase 4 (02_communities.py) y Fase 5 (03_risk.py) para
# "stale" (sin release en >3 anios). Vivia duplicado como literal en ambos
# scripts -- hallazgo de la revision de agentes de Fase 5, 2026-09-10: nada
# garantizaba mecanicamente que se mantuvieran sincronizados si uno cambiaba.
STALE_CUTOFF_UNIX = 1_694_304_000  # 2023-09-10 UTC, 3 anios antes de este ciclo (2026-09-10)


def drop_if_exists(session, name):
    exists = session.run(
        "CALL gds.graph.exists($name) YIELD exists RETURN exists", name=name
    ).single()["exists"]
    if exists:
        session.run("CALL gds.graph.drop($name)", name=name)


@contextmanager
def projected_graph(session, name, project_cypher):
    """Crea la proyeccion GDS `name` y garantiza el drop al salir, incluso si
    algo dentro del bloque `with` lanza una excepcion (hallazgo critico de la
    revision de agentes de Fase 3, 2026-09-10: sin esto, un fallo a mitad de
    un algoritmo dejaba la proyeccion huerfana en memoria del servidor)."""
    drop_if_exists(session, name)
    session.run(project_cypher, name=name)
    try:
        yield
    finally:
        drop_if_exists(session, name)
