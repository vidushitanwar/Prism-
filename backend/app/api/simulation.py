from fastapi import APIRouter, Depends, Body, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models import Skill
from app.analytics.simulation import run_or_get_cached_simulation, PRESET_SCENARIOS

router = APIRouter(prefix="/simulation", tags=["simulation"])


@router.get("/presets")
def get_presets():
    """Powers the 'Break the Workforce' stress-test buttons."""
    return PRESET_SCENARIOS


@router.post("")
def run_simulation(
    tech_adoption: float = Body(0, ge=0, le=100),
    automation: float = Body(0, ge=0, le=100),
    skill_shortage: float = Body(0, ge=0, le=100),
    shock_skill_name: str | None = Body(None),
    db: Session = Depends(get_db),
):
    shock_skill_id = None
    if shock_skill_name:
        skill = db.query(Skill).filter(Skill.name.ilike(shock_skill_name)).first()
        if not skill:
            raise HTTPException(status_code=404, detail=f"Skill '{shock_skill_name}' not found")
        shock_skill_id = skill.id

    return run_or_get_cached_simulation(db, tech_adoption, automation, skill_shortage, shock_skill_id)


@router.post("/preset/{key}")
def run_preset(key: str, db: Session = Depends(get_db)):
    preset = next((p for p in PRESET_SCENARIOS if p["key"] == key), None)
    if not preset:
        raise HTTPException(status_code=404, detail="Unknown preset")

    shock_skill_id = None
    if "shock_skill_name" in preset:
        skill = db.query(Skill).filter(Skill.name.ilike(preset["shock_skill_name"])).first()
        shock_skill_id = skill.id if skill else None

    params = preset["params"]
    result = run_or_get_cached_simulation(
        db, params["tech_adoption"], params["automation"], params["skill_shortage"], shock_skill_id
    )
    result["preset"] = {"key": preset["key"], "label": preset["label"], "description": preset["description"]}
    return result
