"""
Education -> Skills -> Occupations -> Industries pipeline.

For each seeded education program, compares its (generic, non-institution
-specific) curriculum against the latest-year workforce demand ranking to
surface gaps — skills that are highly demanded but not covered by the
curriculum. Never attributes results to a specific real institution (the
seed catalog only contains generic program archetypes).
"""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.models import Education, Skill, TemporalMetric

LATEST_YEAR = 2026
TOP_DEMAND_N = 20


def _top_demand_skills(db: Session, n: int = TOP_DEMAND_N) -> list[tuple[str, float, str]]:
    rows = (
        db.query(TemporalMetric)
        .filter(TemporalMetric.year == LATEST_YEAR)
        .order_by(TemporalMetric.demand_score.desc())
        .limit(n)
        .all()
    )
    out = []
    for r in rows:
        skill = db.get(Skill, r.skill_id)
        out.append((skill.name, r.demand_score, r.lifecycle_stage))
    return out


def list_education_programs(db: Session) -> list[dict]:
    programs = db.query(Education).all()
    top_demand = {name for name, _, _ in _top_demand_skills(db)}

    out = []
    for p in programs:
        curriculum = [s.strip() for s in p.curriculum_skills.split(",") if s.strip()]
        covered_high_demand = [s for s in curriculum if s in top_demand]
        out.append({
            "id": p.id,
            "name": p.name,
            "program_type": p.program_type,
            "curriculum_skills": curriculum,
            "high_demand_coverage": f"{len(covered_high_demand)}/{len(top_demand)}",
        })
    return out


def education_gap_analysis(db: Session, education_id: int) -> dict:
    program = db.get(Education, education_id)
    if not program:
        return {"error": "education program not found"}

    curriculum = {s.strip() for s in program.curriculum_skills.split(",") if s.strip()}
    top_demand = _top_demand_skills(db)

    covered = []
    gaps = []
    for name, demand_score, stage in top_demand:
        entry = {"skill": name, "demand_score": demand_score, "lifecycle_stage": stage}
        if name in curriculum:
            covered.append(entry)
        else:
            gaps.append(entry)

    return {
        "program": program.name,
        "program_type": program.program_type,
        "curriculum_skills": sorted(curriculum),
        "covered_high_demand_skills": covered,
        "gap_high_demand_skills": gaps,
        "coverage_ratio": round(len(covered) / max(len(top_demand), 1), 2),
        "note": (
            "Gap analysis compares this generic curriculum archetype against "
            f"the top {TOP_DEMAND_N} skills by observed demand in {LATEST_YEAR} — "
            "it is not an evaluation of any specific real institution."
        ),
    }
