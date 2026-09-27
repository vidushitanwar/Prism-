"""
The core workforce-intelligence analytics functions. These read from the
relational tables (temporal_metrics, industry_skills, occupation_skills)
and the NetworkX graph, and produce the derived WorkforceSignal rows that
power Emerging Skills, Ghost Skills, Structural Shift Detector, Bridge
Skills, Hidden Capability Discovery, and Career Wormholes.

Nothing here is hardcoded marketing copy — every number is computed from
the seeded dataset, and every signal records its method + sample size in
evidence_json so the "Evidence Mode" UI (later phase) can show it.
"""
from __future__ import annotations

import json
import statistics
from itertools import combinations

import networkx as nx
from sqlalchemy.orm import Session

from app.models import (
    Skill,
    Occupation,
    Industry,
    OccupationSkill,
    IndustrySkill,
    SkillRelationship,
    TemporalMetric,
    WorkforceSignal,
    OccupationTransition,
)
from app.graph.graph_metrics import build_graph, bridge_scores

LATEST_YEAR = 2026
EARLIEST_YEAR = 2022


def _evidence(method: str, **kwargs) -> str:
    payload = {"method": method, "data_window": f"{EARLIEST_YEAR}-{LATEST_YEAR}", **kwargs}
    return json.dumps(payload)


def compute_emerging_skills(db: Session, top_n: int = 15) -> list[WorkforceSignal]:
    rows = (
        db.query(TemporalMetric)
        .filter(TemporalMetric.year == LATEST_YEAR)
        .filter(TemporalMetric.lifecycle_stage.in_(["Emerging", "Growing"]))
        .order_by(TemporalMetric.growth_rate.desc())
        .limit(top_n)
        .all()
    )
    signals = []
    for r in rows:
        skill = db.get(Skill, r.skill_id)
        confidence = min(1.0, 0.5 + (r.postings_count / 2000))
        signals.append(
            WorkforceSignal(
                signal_type="emerging_skill",
                subject_type="skill",
                subject_id=skill.id,
                title=skill.name,
                description=(
                    f"{skill.name} grew {r.growth_rate:.1f}% year-over-year into {LATEST_YEAR}, "
                    f"reaching a demand index of {r.demand_score:.1f}."
                ),
                magnitude=r.growth_rate,
                confidence=round(confidence, 2),
                year=LATEST_YEAR,
                evidence_json=_evidence(
                    "yoy_growth_rank",
                    postings_count=r.postings_count,
                    demand_score=r.demand_score,
                ),
            )
        )
    return signals


def compute_ghost_skills(db: Session, top_n: int = 15) -> list[WorkforceSignal]:
    rows = (
        db.query(TemporalMetric)
        .filter(TemporalMetric.year == LATEST_YEAR)
        .filter(TemporalMetric.lifecycle_stage.in_(["Ghost", "Declining"]))
        .order_by(TemporalMetric.growth_rate.asc())
        .limit(top_n)
        .all()
    )
    signals = []
    for r in rows:
        skill = db.get(Skill, r.skill_id)
        first_row = (
            db.query(TemporalMetric)
            .filter(TemporalMetric.skill_id == skill.id, TemporalMetric.year == EARLIEST_YEAR)
            .first()
        )
        decline_pct = None
        if first_row and first_row.demand_score > 0:
            decline_pct = round(100 * (r.demand_score - first_row.demand_score) / first_row.demand_score, 1)
        signals.append(
            WorkforceSignal(
                signal_type="ghost_skill",
                subject_type="skill",
                subject_id=skill.id,
                title=skill.name,
                description=(
                    f"{skill.name} demand fell {abs(r.growth_rate):.1f}% year-over-year; "
                    f"down {abs(decline_pct):.1f}% since {EARLIEST_YEAR}."
                    if decline_pct is not None
                    else f"{skill.name} demand fell {abs(r.growth_rate):.1f}% year-over-year."
                ),
                magnitude=r.growth_rate,
                confidence=0.75,
                year=LATEST_YEAR,
                evidence_json=_evidence(
                    "yoy_decline_rank",
                    postings_count=r.postings_count,
                    demand_score=r.demand_score,
                    decline_since_2022_pct=decline_pct,
                ),
            )
        )
    return signals


def compute_structural_shifts(db: Session, z_threshold: float = 1.8) -> list[WorkforceSignal]:
    """
    For each skill, compares the latest year-over-year growth rate against
    the mean/stdev of its own prior growth-rate history. Flags a
    structural shift when the latest move is an outlier relative to the
    skill's own trend (a real, if simple, change-point heuristic —
    appropriate for a 5-point series, and clearly documented as such).
    """
    signals = []
    skills = db.query(Skill).all()
    for skill in skills:
        rows = (
            db.query(TemporalMetric)
            .filter(TemporalMetric.skill_id == skill.id)
            .order_by(TemporalMetric.year.asc())
            .all()
        )
        growth_series = [r.growth_rate for r in rows if not (r.year == EARLIEST_YEAR)]
        if len(growth_series) < 3:
            continue
        history, latest = growth_series[:-1], growth_series[-1]
        mean = statistics.mean(history)
        stdev = statistics.pstdev(history) or 1e-6
        z = (latest - mean) / stdev
        if abs(z) >= z_threshold and abs(latest - mean) >= 15:
            direction = "acceleration" if z > 0 else "deceleration"
            signals.append(
                WorkforceSignal(
                    signal_type="structural_shift",
                    subject_type="skill",
                    subject_id=skill.id,
                    title=f"{skill.name}: structural {direction}",
                    description=(
                        f"{skill.name}'s {LATEST_YEAR} growth rate ({latest:.1f}%) deviates "
                        f"sharply from its {EARLIEST_YEAR}-{LATEST_YEAR-1} average ({mean:.1f}%)."
                    ),
                    magnitude=round(z, 2),
                    confidence=round(min(1.0, abs(z) / 4), 2),
                    year=LATEST_YEAR,
                    evidence_json=_evidence(
                        "growth_rate_zscore",
                        historical_mean_growth=round(mean, 1),
                        historical_stdev_growth=round(stdev, 1),
                        latest_growth=round(latest, 1),
                        z_score=round(z, 2),
                    ),
                )
            )
    return signals


def compute_bridge_skills(db: Session, min_industries: int = 4) -> list[WorkforceSignal]:
    graph = build_graph(db)
    centrality = bridge_scores(graph, "skill")

    industry_counts: dict[int, int] = {}
    industry_names: dict[int, list[str]] = {}
    for link in db.query(IndustrySkill).all():
        industry_counts[link.skill_id] = industry_counts.get(link.skill_id, 0) + 1
        industry_names.setdefault(link.skill_id, []).append(link.industry_id)

    signals = []
    for skill_id, count in industry_counts.items():
        if count < min_industries:
            continue
        skill = db.get(Skill, skill_id)
        industries = [db.get(Industry, iid).name for iid in industry_names[skill_id]]
        node_key = f"skill:{skill_id}"
        signals.append(
            WorkforceSignal(
                signal_type="bridge_skill",
                subject_type="skill",
                subject_id=skill_id,
                title=skill.name,
                description=(
                    f"{skill.name} connects {count} industries "
                    f"({', '.join(sorted(industries)[:4])}{'…' if count > 4 else ''})."
                ),
                magnitude=count,
                confidence=round(min(1.0, count / 8), 2),
                year=LATEST_YEAR,
                evidence_json=_evidence(
                    "industry_count_plus_betweenness_centrality",
                    industries=sorted(industries),
                    betweenness_centrality=round(centrality.get(node_key, 0.0), 4),
                ),
            )
        )
    signals.sort(key=lambda s: s.magnitude, reverse=True)
    return signals


def compute_capability_clusters(db: Session, min_size: int = 3) -> list[WorkforceSignal]:
    """
    Hidden Capability Discovery: runs community detection on the
    skill-skill co-occurrence graph to surface clusters of skills that
    travel together (e.g. RAG + Vector Databases + Semantic Search ->
    "Retrieval-Augmented Generation" capability).
    """
    graph = build_graph(db)
    skill_graph = nx.Graph()
    for u, v, data in graph.edges(data=True):
        if data.get("edge_type") == "skill_skill":
            skill_graph.add_edge(u, v, weight=data.get("weight", 1.0))

    if skill_graph.number_of_edges() == 0:
        return []

    communities = nx.algorithms.community.greedy_modularity_communities(skill_graph, weight="weight")
    signals = []
    for idx, community in enumerate(communities):
        if len(community) < min_size:
            continue
        skill_ids = [int(n.split(":")[1]) for n in community]
        skills = [db.get(Skill, sid) for sid in skill_ids]
        names = [s.name for s in skills]
        anchor = max(skills, key=lambda s: len(s.name))  # arbitrary, stable pick for the label
        signals.append(
            WorkforceSignal(
                signal_type="capability_cluster",
                subject_type="skill",
                subject_id=anchor.id,
                title=f"Capability Cluster: {anchor.name}",
                description=(
                    f"{len(names)} skills consistently co-occur across occupations: "
                    f"{', '.join(sorted(names))}."
                ),
                magnitude=len(names),
                confidence=round(min(1.0, len(names) / 6), 2),
                year=LATEST_YEAR,
                evidence_json=_evidence(
                    "greedy_modularity_community_detection",
                    cluster_members=sorted(names),
                    cluster_index=idx,
                ),
            )
        )
    return signals


def compute_combination_clusters(db: Session, min_occupations: int = 3) -> list[WorkforceSignal]:
    """
    Skill Combination Discovery: for each occupation's top-weighted
    skills, checks how many *other* occupations share at least 3 of them
    — a proxy for "this skill combination is becoming its own emerging
    capability cluster" (e.g. Python + LLMs + API Engineering + Cloud ->
    AI Application Engineering).
    """
    occ_skill_sets: dict[int, set[str]] = {}
    for occ in db.query(Occupation).all():
        top_links = (
            db.query(OccupationSkill)
            .filter(OccupationSkill.occupation_id == occ.id)
            .order_by(OccupationSkill.weight.desc())
            .limit(4)
            .all()
        )
        occ_skill_sets[occ.id] = {l.skill_id for l in top_links}

    signals = []
    seen_combos = set()
    for occ_id, combo in occ_skill_sets.items():
        if len(combo) < 3:
            continue
        combo_key = frozenset(combo)
        if combo_key in seen_combos:
            continue

        matches = sum(
            1
            for other_id, other_combo in occ_skill_sets.items()
            if other_id != occ_id and len(combo & other_combo) >= 3
        )
        if matches < min_occupations - 1:
            continue
        seen_combos.add(combo_key)

        skills = [db.get(Skill, sid) for sid in combo]
        growth_values = []
        for s in skills:
            row = (
                db.query(TemporalMetric)
                .filter(TemporalMetric.skill_id == s.id, TemporalMetric.year == LATEST_YEAR)
                .first()
            )
            if row is not None:
                growth_values.append(row.growth_rate)
        avg_growth = statistics.mean(growth_values) if growth_values else 0.0
        occ = db.get(Occupation, occ_id)
        signals.append(
            WorkforceSignal(
                signal_type="combination_cluster",
                subject_type="occupation",
                subject_id=occ_id,
                title=f"Emerging Combination: {' + '.join(s.name for s in skills)}",
                description=(
                    f"This combination appears as a core skill set for {matches + 1} occupations "
                    f"(anchored by {occ.title}), with {avg_growth:.1f}% average YoY growth."
                ),
                magnitude=matches + 1,
                confidence=round(min(1.0, (matches + 1) / 6), 2),
                year=LATEST_YEAR,
                evidence_json=_evidence(
                    "shared_top_skill_overlap",
                    skills=[s.name for s in skills],
                    occupations_sharing_combo=matches + 1,
                    avg_growth_rate=round(avg_growth, 1),
                ),
            )
        )
    return signals


def compute_talent_gaps(db: Session, top_n: int = 12) -> list[WorkforceSignal]:
    """
    Talent Gap proxy: skills with strong demand + positive growth but
    relatively narrow occupational coverage (few occupations list them as
    a core skill) — a signal that supply/training hasn't caught up with
    demand yet. This is a heuristic derived entirely from the seeded
    data's own structure, not a real labor-supply survey.
    """
    latest = {
        row.skill_id: row
        for row in db.query(TemporalMetric).filter(TemporalMetric.year == LATEST_YEAR).all()
    }
    occ_counts: dict[int, int] = {}
    for link in db.query(OccupationSkill).all():
        occ_counts[link.skill_id] = occ_counts.get(link.skill_id, 0) + 1
    max_occ_count = max(occ_counts.values()) if occ_counts else 1

    scored = []
    for skill_id, metric in latest.items():
        if metric.lifecycle_stage in ("Ghost", "Declining"):
            continue
        coverage_ratio = occ_counts.get(skill_id, 0) / max_occ_count
        demand_component = metric.demand_score / 100
        growth_component = max(0.0, metric.growth_rate) / 100
        gap_score = round(demand_component * (0.4 + growth_component) * (1 - coverage_ratio) * 100, 2)
        scored.append((gap_score, skill_id, metric, occ_counts.get(skill_id, 0), coverage_ratio))

    scored.sort(key=lambda t: t[0], reverse=True)
    signals = []
    for gap_score, skill_id, metric, occ_count, coverage_ratio in scored[:top_n]:
        skill = db.get(Skill, skill_id)
        signals.append(
            WorkforceSignal(
                signal_type="talent_gap",
                subject_type="skill",
                subject_id=skill_id,
                title=skill.name,
                description=(
                    f"{skill.name} has a {metric.demand_score:.0f} demand index and "
                    f"{metric.growth_rate:.1f}% YoY growth, but appears as a core skill in only "
                    f"{occ_count} occupation(s) in the current graph — supply/training may be lagging demand."
                ),
                magnitude=gap_score,
                confidence=round(min(1.0, 0.4 + metric.demand_score / 200), 2),
                year=LATEST_YEAR,
                evidence_json=_evidence(
                    "demand_growth_vs_occupation_coverage_heuristic",
                    demand_score=metric.demand_score,
                    growth_rate=metric.growth_rate,
                    occupation_coverage_count=occ_count,
                    occupation_coverage_ratio=round(coverage_ratio, 3),
                ),
            )
        )
    return signals


def compute_occupation_transitions(db: Session, min_overlap: float = 0.22, top_k_per_occ: int = 6) -> list[OccupationTransition]:
    """
    Career Wormholes: weighted-Jaccard similarity between occupations'
    skill sets. Non-obvious transitions surface naturally when two
    occupations share meaningful skill weight despite different titles.
    """
    occ_weights: dict[int, dict[int, float]] = {}
    for occ in db.query(Occupation).all():
        links = db.query(OccupationSkill).filter(OccupationSkill.occupation_id == occ.id).all()
        occ_weights[occ.id] = {l.skill_id: l.weight for l in links}

    transitions = []
    per_occ_candidates: dict[int, list[tuple[float, int, set[int]]]] = {oid: [] for oid in occ_weights}

    for a_id, b_id in combinations(occ_weights.keys(), 2):
        a, b = occ_weights[a_id], occ_weights[b_id]
        shared = set(a) & set(b)
        union = set(a) | set(b)
        if not union:
            continue
        weighted_overlap = sum(min(a[s], b[s]) for s in shared)
        weighted_union = sum(max(a.get(s, 0), b.get(s, 0)) for s in union)
        score = weighted_overlap / weighted_union if weighted_union else 0
        if score >= min_overlap:
            per_occ_candidates[a_id].append((score, b_id, shared))
            per_occ_candidates[b_id].append((score, a_id, shared))

    seen_pairs = set()
    for occ_id, candidates in per_occ_candidates.items():
        candidates.sort(key=lambda c: c[0], reverse=True)
        for score, other_id, shared in candidates[:top_k_per_occ]:
            pair_key = tuple(sorted((occ_id, other_id)))
            if pair_key in seen_pairs:
                continue
            seen_pairs.add(pair_key)
            shared_names = [db.get(Skill, sid).name for sid in shared]
            transitions.append(
                OccupationTransition(
                    source_occupation_id=pair_key[0],
                    target_occupation_id=pair_key[1],
                    overlap_score=round(score, 3),
                    shared_skills=", ".join(sorted(shared_names)),
                    evidence_count=int(round(score * 500)),
                )
            )
    return transitions


def compute_structural_shift_explanation(db: Session, skill_id: int, year: int = LATEST_YEAR) -> dict:
    """
    Powers the "Why Did This Change?" feature. Decomposes a skill's
    growth into a few observable, data-derived contributing components —
    explicitly labeled as model/data-derived signals, not a real causal
    analysis (that would require experiment/intervention data we don't
    have in a synthetic dataset).
    """
    metric = (
        db.query(TemporalMetric)
        .filter(TemporalMetric.skill_id == skill_id, TemporalMetric.year == year)
        .first()
    )
    if metric is None:
        return {"error": "no data for this skill/year"}

    skill = db.get(Skill, skill_id)
    total_growth = metric.growth_rate

    # Component 1: momentum of related skills (co-occurrence cluster).
    related_ids = []
    for rel in db.query(SkillRelationship).filter(
        (SkillRelationship.skill_a_id == skill_id) | (SkillRelationship.skill_b_id == skill_id)
    ).order_by(SkillRelationship.weight.desc()).limit(5):
        related_ids.append(rel.skill_b_id if rel.skill_a_id == skill_id else rel.skill_a_id)
    related_growth = [
        r.growth_rate
        for r in db.query(TemporalMetric).filter(
            TemporalMetric.skill_id.in_(related_ids), TemporalMetric.year == year
        )
    ]
    related_momentum = sum(related_growth) / len(related_growth) if related_growth else 0.0

    # Component 2: breadth of industry adoption.
    industry_count = db.query(IndustrySkill).filter(IndustrySkill.skill_id == skill_id).count()

    # Component 3: breadth of occupation adoption.
    occupation_count = db.query(OccupationSkill).filter(OccupationSkill.skill_id == skill_id).count()

    raw_components = {
        "Related capability momentum": max(0.0, related_momentum) * 0.5,
        "Industry adoption breadth": industry_count * 1.8,
        "Occupation adoption breadth": occupation_count * 1.2,
    }
    raw_total = sum(raw_components.values()) or 1.0
    # Distribute the *observed* total growth across components proportionally,
    # with an explicit "Other / unattributed" remainder — never claiming the
    # split fully explains the number.
    allocated = {k: round((v / raw_total) * abs(total_growth) * 0.8, 1) for k, v in raw_components.items()}
    allocated_sum = sum(allocated.values())
    allocated["Other / unattributed"] = round(max(0.0, abs(total_growth) - allocated_sum), 1)

    return {
        "skill": skill.name,
        "year": year,
        "observed_growth_rate": total_growth,
        "signals": [{"label": k, "contribution_pct_points": v} for k, v in allocated.items()],
        "evidence": _evidence(
            "proportional_decomposition_of_related_signals",
            note="Illustrative, data-derived contribution split — not a causal/experimental estimate.",
            related_skill_count=len(related_ids),
            industry_count=industry_count,
            occupation_count=occupation_count,
            confidence="low-to-moderate (heuristic; synthetic dataset)",
        ),
    }
