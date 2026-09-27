"""
Talent DNA analytics.

Takes a person's self-reported skill list (name + self-rated strength
0-1) and:
  1. builds a "DNA" profile grouped by skill category (for the radar/bar
     visualization),
  2. finds the closest occupations by weighted overlap with each
     occupation's real skill-weight profile (the same weighted-Jaccard
     approach used for career transitions — one consistent method across
     the product, not a bespoke scoring formula),
  3. surfaces the nearest *capability clusters* (from workforce_signals)
     so the person sees where they sit in the graph, not just a score.

Deliberately NOT a single 0-100 "resume score" — the output is a
multi-dimensional profile plus graph placement.
"""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.models import Skill, Occupation, OccupationSkill, WorkforceSignal


def _weighted_overlap(person: dict[int, float], occupation: dict[int, float]) -> float:
    shared = set(person) & set(occupation)
    if not shared:
        return 0.0
    union = set(person) | set(occupation)
    overlap = sum(min(person[s], occupation[s]) for s in shared)
    union_weight = sum(max(person.get(s, 0), occupation.get(s, 0)) for s in union)
    return overlap / union_weight if union_weight else 0.0


def compute_talent_dna(db: Session, skill_inputs: list[dict], top_n_occupations: int = 6) -> dict:
    """
    skill_inputs: [{"name": "Python", "strength": 0.8}, ...] strength in [0,1]
    """
    all_skills = {s.name.lower(): s for s in db.query(Skill).all()}
    person_weights: dict[int, float] = {}
    matched: list[dict] = []
    unmatched: list[str] = []

    for item in skill_inputs:
        name = item.get("name", "").strip()
        strength = max(0.0, min(1.0, float(item.get("strength", 0.6))))
        skill = all_skills.get(name.lower())
        if skill:
            person_weights[skill.id] = max(person_weights.get(skill.id, 0), strength)
            matched.append({"skill_id": skill.id, "name": skill.name, "category": skill.category, "strength": strength})
        else:
            unmatched.append(name)

    # DNA profile grouped by category (for the bar-chart visualization).
    category_totals: dict[str, list[float]] = {}
    for m in matched:
        category_totals.setdefault(m["category"], []).append(m["strength"])
    dna_profile = [
        {"category": cat, "strength": round(sum(vals) / len(vals), 2), "skill_count": len(vals)}
        for cat, vals in sorted(category_totals.items(), key=lambda kv: -sum(kv[1]) / len(kv[1]))
    ]

    # Nearest occupations by weighted overlap.
    occupation_matches = []
    for occ in db.query(Occupation).all():
        occ_weights = {
            l.skill_id: l.weight
            for l in db.query(OccupationSkill).filter(OccupationSkill.occupation_id == occ.id)
        }
        score = _weighted_overlap(person_weights, occ_weights)
        if score <= 0:
            continue
        missing = sorted(set(occ_weights) - set(person_weights), key=lambda sid: -occ_weights[sid])
        missing_names = [db.get(Skill, sid).name for sid in missing[:4]]
        occupation_matches.append({
            "occupation": occ.title,
            "match_score": round(score, 3),
            "missing_capabilities": missing_names,
        })
    occupation_matches.sort(key=lambda m: m["match_score"], reverse=True)

    # Nearby capability clusters (Hidden Capability Discovery signals that
    # share at least one matched skill) — shows graph placement, not a score.
    nearby_clusters = []
    matched_ids = set(person_weights.keys())
    for sig in db.query(WorkforceSignal).filter(WorkforceSignal.signal_type == "capability_cluster").all():
        # evidence_json stores cluster_members as skill names; cheap containment check via title text.
        overlap_count = sum(1 for m in matched if m["name"] in sig.description)
        if overlap_count > 0:
            nearby_clusters.append({"title": sig.title, "description": sig.description, "shared_skill_count": overlap_count})
    nearby_clusters.sort(key=lambda c: -c["shared_skill_count"])

    return {
        "dna_profile": dna_profile,
        "matched_skills": matched,
        "unmatched_skills": unmatched,
        "nearest_occupations": occupation_matches[:top_n_occupations],
        "nearby_capability_clusters": nearby_clusters[:5],
        "method": "weighted_jaccard_overlap_against_occupation_skill_profiles",
        "note": "This is a graph placement, not a single resume score — see nearest_occupations and dna_profile.",
    }
