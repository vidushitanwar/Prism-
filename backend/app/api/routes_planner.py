from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.graph.route_planner import find_career_routes

router = APIRouter(prefix="/routes", tags=["career routes"])


@router.get("")
def get_career_routes(
    from_occupation: int = Query(..., alias="from"),
    to_occupation: int = Query(..., alias="to"),
    k: int = Query(default=3, ge=1, le=5),
    db: Session = Depends(get_db),
):
    result = find_career_routes(db, from_occupation, to_occupation, k=k)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result
