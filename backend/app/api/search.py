from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models import Skill, Occupation, Industry

router = APIRouter(tags=["search"])


@router.get("/search")
def search(q: str = Query(..., min_length=1), limit: int = 8, db: Session = Depends(get_db)):
    """
    Phase 1 implementation: straightforward case-insensitive substring
    matching across skills, occupations, and industries, structured into
    typed results. Natural-language interpretation ("AI jobs in India",
    "skills emerging in cybersecurity") is layered on top of this in a
    later phase — the underlying matches always come from this data
    layer, never invented by an LLM.
    """
    like = f"%{q.lower()}%"

    skills = (
        db.query(Skill)
        .filter(Skill.name.ilike(like))
        .order_by(Skill.name)
        .limit(limit)
        .all()
    )
    occupations = (
        db.query(Occupation)
        .filter(Occupation.title.ilike(like))
        .order_by(Occupation.title)
        .limit(limit)
        .all()
    )
    industries = (
        db.query(Industry)
        .filter(Industry.name.ilike(like))
        .order_by(Industry.name)
        .limit(limit)
        .all()
    )

    return {
        "query": q,
        "results": {
            "skills": [{"id": s.id, "name": s.name, "node_id": f"skill:{s.id}"} for s in skills],
            "occupations": [{"id": o.id, "name": o.title, "node_id": f"occupation:{o.id}"} for o in occupations],
            "industries": [{"id": i.id, "name": i.name, "node_id": f"industry:{i.id}"} for i in industries],
        },
    }
