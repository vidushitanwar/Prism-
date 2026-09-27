"""
Builds the in-memory NetworkX workforce graph from relational data and
provides the traversal operations the Workforce Map API needs: expand a
node, get a bounded neighborhood, compute simple centrality-based
"bridge" scores, etc.

The graph is rebuilt on demand from the DB rather than kept as a second
source of truth — for the dataset sizes in this seed (a few hundred
nodes / a few thousand edges) this is fast enough to do per-request, and
keeps the relational tables authoritative.
"""
from __future__ import annotations

import networkx as nx
from sqlalchemy.orm import Session

from app.models import (
    Skill,
    Occupation,
    Industry,
    OccupationSkill,
    SkillRelationship,
    IndustrySkill,
)


def build_graph(db: Session) -> nx.Graph:
    g = nx.Graph()

    for s in db.query(Skill).all():
        g.add_node(f"skill:{s.id}", type="skill", label=s.name, category=s.category)

    for o in db.query(Occupation).all():
        g.add_node(f"occupation:{o.id}", type="occupation", label=o.title)

    for i in db.query(Industry).all():
        g.add_node(f"industry:{i.id}", type="industry", label=i.name)

    for link in db.query(OccupationSkill).all():
        g.add_edge(
            f"occupation:{link.occupation_id}",
            f"skill:{link.skill_id}",
            weight=link.weight,
            edge_type="occupation_skill",
        )

    for rel in db.query(SkillRelationship).all():
        g.add_edge(
            f"skill:{rel.skill_a_id}",
            f"skill:{rel.skill_b_id}",
            weight=rel.weight,
            edge_type="skill_skill",
        )

    for link in db.query(IndustrySkill).all():
        g.add_edge(
            f"industry:{link.industry_id}",
            f"skill:{link.skill_id}",
            weight=link.weight,
            edge_type="industry_skill",
        )

    return g


def node_neighborhood(g: nx.Graph, node_id: str, depth: int = 1, max_nodes: int = 60) -> dict:
    """
    Returns a bounded ego-graph around node_id — used by GET /api/graph and
    node expansion in the Workforce Map. Bounding max_nodes keeps large
    hubs (e.g. "Python") from returning an unusably huge graph in one call,
    per the performance requirements (progressive expansion).
    """
    if node_id not in g:
        return {"nodes": [], "edges": []}

    ego = nx.ego_graph(g, node_id, radius=depth)

    if ego.number_of_nodes() > max_nodes:
        # Keep the highest-weight edges out to the center node first.
        distances = nx.single_source_shortest_path_length(ego, node_id)
        ranked = sorted(
            ego.nodes(),
            key=lambda n: (distances.get(n, 99), -ego.degree(n, weight="weight")),
        )
        keep = set(ranked[:max_nodes])
        ego = ego.subgraph(keep)

    nodes = [
        {"id": n, **ego.nodes[n]}
        for n in ego.nodes()
    ]
    edges = [
        {"source": u, "target": v, **ego.edges[u, v]}
        for u, v in ego.edges()
    ]
    return {"nodes": nodes, "edges": edges}


def bridge_scores(g: nx.Graph, node_type: str = "skill") -> dict[str, float]:
    """
    Betweenness centrality restricted to nodes of a given type — a proxy
    for "connects otherwise-separate parts of the workforce graph", used
    as one signal (alongside the industry_skills-based cross-industry
    count) for Bridge Skill detection.
    """
    centrality = nx.betweenness_centrality(g, weight="weight", normalized=True)
    return {n: score for n, score in centrality.items() if n.startswith(f"{node_type}:")}
