from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models import Industry, IndustrySkill, Skill
from app.schemas.schemas import IndustryOut

router = APIRouter(prefix="/industries", tags=["industries"])


@router.get("", response_model=list[IndustryOut])
def list_industries(db: Session = Depends(get_db)):
    return db.query(Industry).order_by(Industry.name).all()


@router.get("/{industry_id}")
def get_industry(industry_id: int, db: Session = Depends(get_db)):
    industry = db.get(Industry, industry_id)
    if not industry:
        raise HTTPException(status_code=404, detail="Industry not found")
    links = (
        db.query(IndustrySkill)
        .filter(IndustrySkill.industry_id == industry_id)
        .order_by(IndustrySkill.weight.desc())
        .all()
    )
    skills = [
        {"id": l.skill_id, "name": db.get(Skill, l.skill_id).name, "weight": l.weight}
        for l in links
    ]
    return {"id": industry.id, "name": industry.name, "description": industry.description, "top_skills": skills}

    @router.get("/{industry_id}/evolution")
    def get_industry_evolution(industry_id: int, db: Session = Depends(get_db)):
        """Aggregate linked skill demand trajectories into an industry timeline."""
        industry = db.get(Industry, industry_id)
        if not industry:
            raise HTTPException(status_code=404, detail="Industry not found")

        skill_ids = [
            link.skill_id
            for link in db.query(IndustrySkill).filter(IndustrySkill.industry_id == industry_id)
        ]
        by_year: dict[int, list[float]] = {}
        for row in db.query(TemporalMetric).filter(TemporalMetric.skill_id.in_(skill_ids)):
            by_year.setdefault(row.year, []).append(row.demand_score)

        evolution = [
            {"year": year, "avg_demand_score": round(sum(values) / len(values), 2)}
            for year, values in sorted(by_year.items())
        ]
        return {"industry": industry.name, "evolution": evolution}
