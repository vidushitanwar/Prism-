from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.analytics.talent_dna import compute_talent_dna
from app.analytics.geography import list_locations_summary, location_detail
from app.analytics.education import list_education_programs, education_gap_analysis

router = APIRouter(tags=["talent, geography & education"])


@router.post("/talent-dna")
def talent_dna(
    skills: list[dict] = Body(..., embed=True, description='[{"name": "Python", "strength": 0.8}, ...]'),
    db: Session = Depends(get_db),
):
    if not skills:
        raise HTTPException(status_code=400, detail="Provide at least one skill.")
    return compute_talent_dna(db, skills)


@router.get("/geography/locations")
def geography_locations(year: int = 2026, db: Session = Depends(get_db)):
    return list_locations_summary(db, year)


@router.get("/geography/{location_id}")
def geography_detail(location_id: int, year: int = 2026, db: Session = Depends(get_db)):
    result = location_detail(db, location_id, year)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.get("/education")
def education_programs(db: Session = Depends(get_db)):
    return list_education_programs(db)


@router.get("/education/{education_id}/gap-analysis")
def education_gap(education_id: int, db: Session = Depends(get_db)):
    result = education_gap_analysis(db, education_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result
