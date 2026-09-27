from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models import Skill, TemporalMetric, SkillRelationship, OccupationSkill, Occupation, IndustrySkill, Industry
from app.schemas.schemas import SkillOut, SkillDetailOut, TemporalMetricOut

router = APIRouter(prefix="/skills", tags=["skills"])


@router.get("", response_model=list[SkillOut])
def list_skills(category: str | None = None, limit: int = 200, db: Session = Depends(get_db)):
    query = db.query(Skill)
    if category:
        query = query.filter(Skill.category == category)
    return query.order_by(Skill.name).limit(limit).all()


@router.get("/{skill_id}", response_model=SkillDetailOut)
def get_skill(skill_id: int, db: Session = Depends(get_db)):
    skill = db.get(Skill, skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    timeline = (
        db.query(TemporalMetric)
        .filter(TemporalMetric.skill_id == skill_id)
        .order_by(TemporalMetric.year)
        .all()
    )

    related_ids = set()
    for rel in db.query(SkillRelationship).filter(
        (SkillRelationship.skill_a_id == skill_id) | (SkillRelationship.skill_b_id == skill_id)
    ).order_by(SkillRelationship.weight.desc()).limit(10):
        related_ids.add(rel.skill_b_id if rel.skill_a_id == skill_id else rel.skill_a_id)
    related_names = [s.name for s in db.query(Skill).filter(Skill.id.in_(related_ids)).all()]

    occ_ids = [l.occupation_id for l in db.query(OccupationSkill).filter(OccupationSkill.skill_id == skill_id).all()]
    occ_names = [o.title for o in db.query(Occupation).filter(Occupation.id.in_(occ_ids)).all()]

    ind_ids = [l.industry_id for l in db.query(IndustrySkill).filter(IndustrySkill.skill_id == skill_id).all()]
    ind_names = [i.name for i in db.query(Industry).filter(Industry.id.in_(ind_ids)).all()]

    return SkillDetailOut(
        id=skill.id, name=skill.name, category=skill.category, description=skill.description,
        timeline=[TemporalMetricOut.model_validate(t) for t in timeline],
        related_skills=related_names, occupations=occ_names, industries=ind_names,
    )


@router.get("/{skill_id}/timeline", response_model=list[TemporalMetricOut])
def get_skill_timeline(skill_id: int, db: Session = Depends(get_db)):
    skill = db.get(Skill, skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    rows = (
        db.query(TemporalMetric)
        .filter(TemporalMetric.skill_id == skill_id)
        .order_by(TemporalMetric.year)
        .all()
    )
    return rows


@router.get("/{skill_id}/related", response_model=list[SkillOut])
def get_related_skills(skill_id: int, db: Session = Depends(get_db)):
    skill = db.get(Skill, skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    related_ids = set()
    for rel in db.query(SkillRelationship).filter(
        (SkillRelationship.skill_a_id == skill_id) | (SkillRelationship.skill_b_id == skill_id)
    ).order_by(SkillRelationship.weight.desc()).limit(15):
        related_ids.add(rel.skill_b_id if rel.skill_a_id == skill_id else rel.skill_a_id)
    return db.query(Skill).filter(Skill.id.in_(related_ids)).all()
