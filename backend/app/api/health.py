"""
Health-check endpoints used to verify the backend (and DB connection) is up.
This is the Phase 0 checkpoint: frontend -> backend -> DB round trip.
"""
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.database import get_db

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check():
    return {"status": "ok", "service": "prism-backend"}


@router.get("/health/db")
def health_check_db(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as exc:  # pragma: no cover - defensive
        return {"status": "error", "database": "unreachable", "detail": str(exc)}
