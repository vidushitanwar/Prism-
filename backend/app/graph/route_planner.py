"""
Career Route Planner (Google-Maps-style routing, but between occupations).

Builds a graph from the precomputed OccupationTransition edges (weighted
by 1 - overlap_score, so higher skill overlap = "shorter" distance) and
finds several alternative paths between a source and target occupation.
Routes are NOT ranked as universally "best" — the API returns them
labeled Route 1, Route 2, ... in shortest-path order, and the frontend
must not imply a guaranteed outcome.
"""
from __future__ import annotations

import networkx as nx
from sqlalchemy.orm import Session

from app.models import Occupation, OccupationSkill, OccupationTransition, Industry, IndustrySkill, Skill


def _build_occupation_graph(db: Session) -> nx.Graph:
    g = nx.Graph()
    for occ in db.query(Occupation).all():
        g.add_node(occ.id, title=occ.title)
    for t in db.query(OccupationTransition).all():
        distance = max(0.01, 1 - t.overlap_score)
        g.add_edge(
            t.source_occupation_id, t.target_occupation_id,
            distance=distance, overlap_score=t.overlap_score,
            shared_skills=t.shared_skills, evidence_count=t.evidence_count,
        )
    return g


def _skill_set(db: Session, occupation_id: int) -> dict[int, float]:
    return {
        l.skill_id: l.weight
        for l in db.query(OccupationSkill).filter(OccupationSkill.occupation_id == occupation_id)
    }


def _industry_context(db: Session, occupation_id: int, top_n: int = 4) -> list[str]:
    skill_ids = list(_skill_set(db, occupation_id).keys())
    if not skill_ids:
        return []
    industry_ids = {
        l.industry_id
        for l in db.query(IndustrySkill).filter(IndustrySkill.skill_id.in_(skill_ids))
    }
    names = [db.get(Industry, iid).name for iid in industry_ids]
    return sorted(names)[:top_n]


def find_career_routes(db: Session, source_id: int, target_id: int, k: int = 3) -> dict:
    source = db.get(Occupation, source_id)
    target = db.get(Occupation, target_id)
    if not source or not target:
        return {"error": "occupation not found"}

    source_skills = _skill_set(db, source_id)
    target_skills = _skill_set(db, target_id)

    existing_overlap_ids = sorted(set(source_skills) & set(target_skills))
    missing_ids = sorted(set(target_skills) - set(source_skills))

    def names_for(ids):
        return [s.name for s in db.query(Skill).filter(Skill.id.in_(ids)).all()] if ids else []

    if source_id == target_id:
        return {
            "source_occupation": source.title,
            "target_occupation": target.title,
            "existing_overlap": names_for(list(source_skills.keys())),
            "missing_capabilities": [],
            "routes": [],
            "note": "Source and target are the same occupation.",
        }

    graph = _build_occupation_graph(db)
    routes = []

    if source_id in graph and target_id in graph and nx.has_path(graph, source_id, target_id):
        try:
            path_generator = nx.shortest_simple_paths(graph, source_id, target_id, weight="distance")
            for i, path in enumerate(path_generator):
                if i >= k:
                    break
                hops = []
                for a, b in zip(path[:-1], path[1:]):
                    edge = graph.edges[a, b]
                    hops.append({
                        "from_occupation": db.get(Occupation, a).title,
                        "to_occupation": db.get(Occupation, b).title,
                        "overlap_score": edge["overlap_score"],
                        "shared_skills": [s.strip() for s in edge["shared_skills"].split(",") if s.strip()],
                        "evidence_count": edge["evidence_count"],
                    })
                occupations_in_path = [db.get(Occupation, oid).title for oid in path]
                routes.append({
                    "label": f"Route {i + 1}",
                    "occupations": occupations_in_path,
                    "hops": hops,
                    "total_evidence_count": sum(h["evidence_count"] for h in hops),
                    "industry_context": _industry_context(db, target_id),
                })
        except nx.NetworkXNoPath:
            pass

    return {
        "source_occupation": source.title,
        "target_occupation": target.title,
        "existing_overlap": names_for(existing_overlap_ids),
        "missing_capabilities": names_for(missing_ids),
        "routes": routes,
        "note": (
            None
            if routes
            else "No observed multi-hop transition path between these occupations in the current "
                 "dataset — shown overlap/missing capabilities are still based on real skill data."
        ),
    }
