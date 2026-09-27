from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models import Occupation, OccupationSkill, Skill, OccupationTransition
from app.schemas.schemas import OccupationOut, OccupationTransitionOut

router = APIRouter(prefix="/occupations", tags=["occupations"])


@router.get("", response_model=list[OccupationOut])
def list_occupations(limit: int = 200, db: Session = Depends(get_db)):
    return db.query(Occupation).order_by(Occupation.title).limit(limit).all()


@router.get("/{occupation_id}")
def get_occupation(occupation_id: int, db: Session = Depends(get_db)):
    occ = db.get(Occupation, occupation_id)
    if not occ:
        raise HTTPException(status_code=404, detail="Occupation not found")
    links = (
        db.query(OccupationSkill)
        .filter(OccupationSkill.occupation_id == occupation_id)
        .order_by(OccupationSkill.weight.desc())
        .all()
    )
    skills = [
        {"id": l.skill_id, "name": db.get(Skill, l.skill_id).name, "weight": l.weight}
        for l in links
    ]
    return {"id": occ.id, "title": occ.title, "description": occ.description, "core_skills": skills}


@router.get("/{occupation_id}/evolution")
def get_occupation_evolution(occupation_id: int, db: Session = Depends(get_db)):
    """
    Aggregates the occupation's core skills' demand trajectories into a
    single evolution signal for the occupation itself.
    """
    from app.models import TemporalMetric

    occ = db.get(Occupation, occupation_id)
    if not occ:
        raise HTTPException(status_code=404, detail="Occupation not found")

    skill_ids = [l.skill_id for l in db.query(OccupationSkill).filter(OccupationSkill.occupation_id == occupation_id)]
    by_year: dict[int, list[float]] = {}
    for row in db.query(TemporalMetric).filter(TemporalMetric.skill_id.in_(skill_ids)):
        by_year.setdefault(row.year, []).append(row.demand_score)

    evolution = [
        {"year": year, "avg_demand_score": round(sum(vals) / len(vals), 2)}
        for year, vals in sorted(by_year.items())
    ]
    return {"occupation": occ.title, "evolution": evolution}


@router.get("/{occupation_id}/transitions", response_model=list[OccupationTransitionOut])
def get_occupation_transitions(occupation_id: int, db: Session = Depends(get_db)):
    occ = db.get(Occupation, occupation_id)
    if not occ:
        raise HTTPException(status_code=404, detail="Occupation not found")

    rows = (
        db.query(OccupationTransition)
        .filter(
            (OccupationTransition.source_occupation_id == occupation_id)
            | (OccupationTransition.target_occupation_id == occupation_id)
        )
        .order_by(OccupationTransition.overlap_score.desc())
        .all()
    )
    out = []
    for r in rows:
        other_id = r.target_occupation_id if r.source_occupation_id == occupation_id else r.source_occupation_id
        other = db.get(Occupation, other_id)
        out.append(OccupationTransitionOut(
            source_occupation=occ.title,
            target_occupation=other.title,
            overlap_score=r.overlap_score,
            shared_skills=[s.strip() for s in r.shared_skills.split(",") if s.strip()],
            evidence_count=r.evidence_count,
        ))
    return out
