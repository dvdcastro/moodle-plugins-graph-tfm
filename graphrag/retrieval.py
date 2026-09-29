"""Recuperacion: baseline vectorial y GraphRAG con el mismo formato de ficha.

Ambos sistemas devuelven exactamente K fichas de plugin (mismo formato,
misma descripcion recortada). GraphRAG ademas devuelve lineas de relacion
explicitas obtenidas por Cypher.

EXPANSIONS controla que relaciones usa GraphRAG:
  cut line (PLAN §7): {"in", "out", "maint"}  (DEPENDS_ON y MAINTAINS)
  plan completo:      + {"comm", "alt"}        (louvain_soc + exposicion, categoria)
"""
import json
import re
from datetime import datetime, timezone

import pandas as pd

import config as C

ALL_EXPANSIONS = ("in", "out", "maint", "comm", "alt")
FRANKEN = re.compile(r"\b([a-z][a-z0-9]*_[a-z0-9_]*[a-z0-9])\b")


class Retriever:
    def __init__(self, expansions=ALL_EXPANSIONS):
        self.expansions = tuple(expansions)
        self.drv = C.driver()
        with self.drv.session() as s:
            rows = s.run("""
                MATCH (p:Plugin)
                OPTIONAL MATCH (p)-[:IN_CATEGORY]->(c:Category)
                OPTIONAL MATCH (m:Maintainer)-[:MAINTAINS]->(p)
                RETURN p.component AS c, p.name AS name, p.plugin_type AS t,
                       p.in_directory AS dir, p.installations AS inst,
                       p.last_release_ts AS lr, p.louvain_soc AS comm,
                       c.code AS cat, collect(m.display_name) AS maint""").data()
        self.meta = {r["c"]: r for r in rows}
        self.components = set(self.meta)
        self.name2comp = {}
        for r in rows:
            if r["name"]:
                self.name2comp.setdefault(r["name"].lower(), r["c"])
        self.desc = {}
        for line in C.TEXTS.read_text().splitlines():
            d = json.loads(line)
            self.desc[d["component"]] = d["body"]
        risk = pd.read_csv(C.RISK_CSV)
        self.risk = risk.set_index("component")[["SM", "ST", "E_exposicion", "rank"]].to_dict("index")

    def close(self):
        self.drv.close()

    # ------------------------------------------------------------------ fichas
    def card(self, c):
        m = self.meta.get(c)
        if m is None:
            return f"[{c}] (componente desconocido)"
        if not m["dir"]:
            return f"[{c}] componente del núcleo de Moodle (sin página en el directorio)."
        lr = (datetime.fromtimestamp(m["lr"], timezone.utc).strftime("%Y-%m-%d")
              if m["lr"] else "desconocida")
        stale = m["lr"] is not None and m["lr"] < C.STALE_CUTOFF_UNIX
        estado = "sin release en más de 3 años" if stale else "con release en los últimos 3 años"
        mant = ", ".join(sorted(x for x in m["maint"] if x)) or "desconocido"
        desc = (self.desc.get(c) or "")[:C.DESC_CHARS]
        return (f"[{c}] {m['name']} — tipo {m['t']}; {int(m['inst'] or 0)} instalaciones; "
                f"última release {lr}, {estado}; mantenedores ({len(m['maint'])}): {mant}.\n"
                f"   {desc}")

    # --------------------------------------------------------------- vectorial
    def vector(self, q, k=C.K):
        v = C.embed_query(q)
        with self.drv.session() as s:
            res = s.run(f"CALL db.index.vector.queryNodes('{C.VECTOR_INDEX}', $k, $v) "
                        "YIELD node, score RETURN node.component AS c, score",
                        k=k, v=v.tolist()).data()
        return [r["c"] for r in res]

    def baseline(self, q):
        comps = self.vector(q, C.K)
        return {"components": comps, "relations": [], "seeds": [], "link_method": None}

    # ------------------------------------------------- vectorial + relaciones
    def vector_rel(self, q):
        """Ablacion (revision independiente): EXACTAMENTE las K fichas del
        baseline vectorial, anotadas con los hechos del grafo que GraphRAG
        verbalizaria, restringidos al conjunto S = fichas recuperadas + semilla.
        Sin expansion: no puede anadir ningun plugin que el vector no devolvio.
        Sin enrutador: se anotan todos los tipos de hecho.
          - DEPENDS_ON entre cualquier par de S
          - Mantenedor -MAINTAINS-> p para los mantenedores de la semilla y para
            los que mantienen >=2 plugins de S (co-mantenimiento visible)
          - misma comunidad Louvain que la semilla, con banderas SM/ST/exposicion
          - misma categoria que la semilla (etiqueta neutra, sin "alternativa")
        """
        comps = self.vector(q, C.K)
        seeds, how = self.link(q)
        S = list(dict.fromkeys(seeds + comps))
        rels = []
        with self.drv.session() as s:
            for r in s.run("""MATCH (a:Plugin)-[:DEPENDS_ON]->(b:Plugin)
                              WHERE a.component IN $S AND b.component IN $S
                              RETURN a.component AS a, b.component AS b ORDER BY a, b""", S=S):
                rels.append(f"[{r['a']}] -DEPENDS_ON-> [{r['b']}]")
            for r in s.run("""MATCH (m:Maintainer)-[:MAINTAINS]->(p:Plugin) WHERE p.component IN $S
                              WITH m, collect(p.component) AS ps
                              WHERE size(ps) >= 2 OR any(x IN ps WHERE x IN $seeds)
                              RETURN m.display_name AS m, ps ORDER BY m""", S=S, seeds=seeds):
                rels += [f"Mantenedor «{r['m']}» -MAINTAINS-> [{p}]" for p in sorted(r["ps"])]
            for seed in seeds:
                sm = self.meta.get(seed, {})
                for c in comps:
                    if c == seed:
                        continue
                    m = self.meta.get(c, {})
                    if sm.get("comm") is not None and m.get("comm") == sm.get("comm"):
                        rk = self.risk.get(c)
                        extra = (f" (un solo mantenedor={'sí' if rk['SM'] else 'no'}, "
                                 f"sin release >3 años={'sí' if rk['ST'] else 'no'}, "
                                 f"exposición={rk['E_exposicion']:.3f})") if rk else ""
                        rels.append(f"[{c}] -MISMA_COMUNIDAD_LOUVAIN-> [{seed}]{extra}")
                    if sm.get("cat") is not None and m.get("cat") == sm.get("cat"):
                        rels.append(f"[{c}] -MISMA_CATEGORÍA-> [{seed}]")
        return {"components": comps, "relations": list(dict.fromkeys(rels)),
                "seeds": seeds, "link_method": how}

    # ---------------------------------------------------------- entity linking
    def link(self, q):
        """(a) frankenstyle, (b) nombre exacto, (c) top-1 vectorial."""
        found = [m for m in FRANKEN.findall(q) if m in self.components]
        if found:
            return list(dict.fromkeys(found)), "frankenstyle"
        ql = q.lower()
        names = [c for n, c in self.name2comp.items() if len(n) >= 4 and re.search(rf"\b{re.escape(n)}\b", ql)]
        if names:
            return names[:1], "nombre"
        return self.vector(q, 1), "vectorial"

    # -------------------------------------------------------------- intencion
    @staticmethod
    def intents(q):
        """Enrutado determinista por palabras clave (español). Si no se detecta
        ninguna intención se usan todas las expansiones en turno rotatorio."""
        ql = q.lower()
        it = []
        if re.search(r"dependen de|depende de (él|ella|este|esta)|quién depende|qué depende de", ql):
            it.append("in")
        if re.search(r"de qué (plugins |componentes )?depende|dependencias de|requiere", ql):
            it.append("out")
        if re.search(r"mantien|mantenedor|desarroll", ql):
            it.append("maint")
        if re.search(r"comunidad|frágil", ql):
            it.append("comm")
        if re.search(r"alternativa|reemplaz|sustitu", ql):
            it.append("alt")
        return it

    # ---------------------------------------------------------------- GraphRAG
    def _expand(self, s, seed, kind, qvec=None):
        """Devuelve ([(component, linea de relacion)], lineas extra)."""
        if kind == "in":
            rows = s.run("""MATCH (q:Plugin)-[:DEPENDS_ON]->(p:Plugin {component:$c})
                            RETURN q.component AS c ORDER BY coalesce(q.installations,0) DESC, c""",
                         c=seed).data()
            return [(r["c"], f"[{r['c']}] -DEPENDS_ON-> [{seed}]") for r in rows], []
        if kind == "out":
            rows = s.run("""MATCH (p:Plugin {component:$c})-[:DEPENDS_ON]->(q:Plugin)
                            RETURN q.component AS c ORDER BY coalesce(q.installations,0) DESC, c""",
                         c=seed).data()
            return [(r["c"], f"[{seed}] -DEPENDS_ON-> [{r['c']}]") for r in rows], []
        if kind == "maint":
            rows = s.run("""MATCH (m:Maintainer)-[:MAINTAINS]->(p:Plugin {component:$c})
                            OPTIONAL MATCH (m)-[:MAINTAINS]->(o:Plugin) WHERE o <> p
                            WITH m, o ORDER BY coalesce(o.installations,0) DESC, o.component
                            RETURN m.display_name AS m, collect(o.component) AS os""", c=seed).data()
            pairs, extra = [], []
            for r in rows:
                extra.append(f"Mantenedor «{r['m']}» -MAINTAINS-> [{seed}]")
                pairs += [(o, f"Mantenedor «{r['m']}» -MAINTAINS-> [{o}]") for o in r["os"]]
            return pairs, extra
        if kind == "comm":
            comm = self.meta.get(seed, {}).get("comm")
            if comm is None:
                return [], []
            rows = s.run("""MATCH (p:Plugin {louvain_soc:$k}) WHERE p.component <> $c
                            RETURN p.component AS c""", k=comm, c=seed).data()
            comps = [r["c"] for r in rows]
            comps.sort(key=lambda c: (-self.risk.get(c, {}).get("E_exposicion", -1), c))
            pairs = []
            for c in comps:
                rk = self.risk.get(c)
                extra = (f" (un solo mantenedor={'sí' if rk['SM'] else 'no'}, "
                         f"sin release >3 años={'sí' if rk['ST'] else 'no'}, "
                         f"exposición={rk['E_exposicion']:.3f})") if rk else ""
                pairs.append((c, f"[{c}] -MISMA_COMUNIDAD_LOUVAIN-> [{seed}]{extra}"))
            return pairs, []
        if kind == "alt":
            rows = s.run("""MATCH (p:Plugin {component:$c})-[:IN_CATEGORY]->(cat:Category)<-[:IN_CATEGORY]-(o:Plugin)
                            MATCH (tp:PluginText {component:$c}), (to:PluginText)-[:DESCRIBES]->(o)
                            WHERE o <> p AND o.last_release_ts >= $cut
                            RETURN o.component AS c,
                                   vector.similarity.cosine(tp.embedding, to.embedding) AS sim
                            ORDER BY sim DESC, c LIMIT 50""",
                         c=seed, cut=C.STALE_CUTOFF_UNIX).data()
            return ([(r["c"], f"[{r['c']}] -ALTERNATIVA_MANTENIDA(misma categoría, "
                              f"similitud={r['sim']:.3f})-> [{seed}]") for r in rows], [])
        raise ValueError(kind)

    def graphrag(self, q):
        seeds, how = self.link(q)
        wanted = [k for k in self.intents(q) if k in self.expansions] or list(self.expansions)
        # presupuesto de fichas de grafo: todo K si la entidad se nombra
        # explicitamente; la mitad si viene del enlazado vectorial (T6), para
        # no desplazar del todo a los candidatos semanticos.
        graph_budget = C.K if how != "vectorial" else C.K // 2
        comps, rels = list(seeds), []
        with self.drv.session() as s:
            lists = []
            for seed in seeds:
                for kind in wanted:
                    lists.append(self._expand(s, seed, kind))
        # turno rotatorio entre listas de expansion
        rel_of = {}
        for pairs, extra in lists:
            rels.extend(extra)          # lineas sin plugin propio (mantenedor->semilla)
            for c, r in pairs:
                rel_of.setdefault(c, []).append(r)
        i = 0
        while len(comps) < graph_budget and any(i < len(p) for p, _ in lists):
            for p, _ in lists:
                if i < len(p) and p[i][0] not in comps and len(comps) < graph_budget:
                    comps.append(p[i][0])
            i += 1
        for c in comps:
            rels.extend(rel_of.get(c, []))
        # relleno con candidatos vectoriales hasta K
        if len(comps) < C.K:
            for c in self.vector(q, C.K * 2):
                if c not in comps:
                    comps.append(c)
                if len(comps) >= C.K:
                    break
        return {"components": comps[:C.K], "relations": list(dict.fromkeys(rels)),
                "seeds": seeds, "link_method": how, "intents": wanted}

    # --------------------------------------------------------------- contexto
    def context(self, ret):
        parts = ["FICHAS DE PLUGINS:"] + [self.card(c) for c in ret["components"]]
        if ret["relations"]:
            parts += ["", "RELACIONES DEL GRAFO (verificadas):"] + ret["relations"]
        return "\n".join(parts)
