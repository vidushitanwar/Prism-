from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models import WorkforceSignal, TemporalMetric, Skill
from app.schemas.schemas import WorkforceSignalOut

router = APIRouter(prefix="/workforce", tags=["workforce intelligence"])

VALID_YEARS = [2022, 2023, 2024, 2025, 2026]
LATEST_YEAR = 2026


def _signals_by_type(db: Session, signal_type: str, limit: int) -> list[WorkforceSignal]:
    return (
        db.query(WorkforceSignal)
        .filter(WorkforceSignal.signal_type == signal_type)
        .order_by(WorkforceSignal.magnitude.desc())
        .limit(limit)
        .all()
    )


@router.get("/years")
def available_years(db: Session = Depends(get_db)):
    """
    Powers the Time Machine's timeline markers. Reads distinct years
    actually present in temporal_metrics rather than hardcoding a range
    in the frontend.
    """
    rows = db.query(TemporalMetric.year).distinct().order_by(TemporalMetric.year).all()
    years = [r[0] for r in rows] or VALID_YEARS
    return {"years": years, "earliest": min(years), "latest": max(years)}


@router.get("/snapshot")
def workforce_snapshot(year: int = Query(..., description="e.g. 2024"), db: Session = Depends(get_db)):
    """
    The Time Machine's core data source: for every skill, its demand
    score / growth rate / lifecycle stage *as of the selected year*. The
    frontend uses this to re-style (not just re-decorate) the Workforce
    Map when the timeline is dragged — node size, color, and the
    Emerging/Ghost lists all change with it.
    """
    if year not in VALID_YEARS:
        raise HTTPException(status_code=400, detail=f"year must be one of {VALID_YEARS}")

    rows = db.query(TemporalMetric).filter(TemporalMetric.year == year).all()
    skill_names = {s.id: s.name for s in db.query(Skill).all()}

    return {
        "year": year,
        "skills": [
            {
                "skill_id": r.skill_id,
                "name": skill_names.get(r.skill_id, "Unknown"),
                "demand_score": r.demand_score,
                "growth_rate": r.growth_rate,
                "lifecycle_stage": r.lifecycle_stage,
                "postings_count": r.postings_count,
            }
            for r in rows
        ],
    }


@router.get("/emerging", response_model=list[WorkforceSignalOut])
def emerging_skills(limit: int = 15, year: int | None = None, db: Session = Depends(get_db)):
    if year is None or year == LATEST_YEAR:
        return _signals_by_type(db, "emerging_skill", limit)
    return _live_ranked_by_year(db, year, limit, stages=["Emerging", "Growing"], descending=True)


@router.get("/declining", response_model=list[WorkforceSignalOut])
def declining_skills(limit: int = 15, year: int | None = None, db: Session = Depends(get_db)):
    if year is None or year == LATEST_YEAR:
        rows = (
            db.query(WorkforceSignal)
            .filter(WorkforceSignal.signal_type == "ghost_skill")
            .order_by(WorkforceSignal.magnitude.asc())
            .limit(limit)
            .all()
        )
        return rows
    return _live_ranked_by_year(db, year, limit, stages=["Ghost", "Declining"], descending=False)


def _live_ranked_by_year(
    db: Session, year: int, limit: int, stages: list[str], descending: bool
) -> list[WorkforceSignalOut]:
    """
    For years other than the precomputed latest year, rank directly from
    temporal_metrics so the Time Machine reflects that year's actual
    numbers rather than reusing 2026's cached signals.
    """
    if year not in VALID_YEARS:
        raise HTTPException(status_code=400, detail=f"year must be one of {VALID_YEARS}")

    query = db.query(TemporalMetric).filter(
        TemporalMetric.year == year, TemporalMetric.lifecycle_stage.in_(stages)
    )
    query = query.order_by(TemporalMetric.growth_rate.desc() if descending else TemporalMetric.growth_rate.asc())
    rows = query.limit(limit).all()

    skill_names = {s.id: s.name for s in db.query(Skill).all()}
    out = []
    for r in rows:
        name = skill_names.get(r.skill_id, "Unknown")
        out.append(WorkforceSignalOut(
            id=r.id,
            signal_type="emerging_skill" if descending else "ghost_skill",
            subject_type="skill",
            subject_id=r.skill_id,
            title=name,
            description=(
                f"{name} {'grew' if r.growth_rate >= 0 else 'fell'} {abs(r.growth_rate):.1f}% "
                f"year-over-year in {year}, at a demand index of {r.demand_score:.1f}."
            ),
            magnitude=r.growth_rate,
            confidence=0.7,
            year=year,
        ))
    return out


@router.get("/shifts", response_model=list[WorkforceSignalOut])
def structural_shifts(limit: int = 15, db: Session = Depends(get_db)):
    rows = (
        db.query(WorkforceSignal)
        .filter(WorkforceSignal.signal_type == "structural_shift")
        .order_by(WorkforceSignal.confidence.desc())
        .limit(limit)
        .all()
    )
    return rows


@router.get("/bridges", response_model=list[WorkforceSignalOut])
def bridge_skills(limit: int = 15, db: Session = Depends(get_db)):
    return _signals_by_type(db, "bridge_skill", limit)


@router.get("/capability-clusters", response_model=list[WorkforceSignalOut])
def capability_clusters(limit: int = 15, db: Session = Depends(get_db)):
    return _signals_by_type(db, "capability_cluster", limit)


@router.get("/combination-clusters", response_model=list[WorkforceSignalOut])
def combination_clusters(limit: int = 15, db: Session = Depends(get_db)):
    return _signals_by_type(db, "combination_cluster", limit)


@router.get("/talent-gaps", response_model=list[WorkforceSignalOut])
def talent_gaps(limit: int = 12, db: Session = Depends(get_db)):
    return _signals_by_type(db, "talent_gap", limit)


@router.get("/why/{skill_id}")
def why_did_this_change(skill_id: int, year: int = LATEST_YEAR, db: Session = Depends(get_db)):
    """
    Powers the "Why Did This Change?" button. Returns a data-derived
    contribution breakdown — explicitly labeled as a heuristic signal
    split, not a causal claim.
    """
    from app.analytics.signals import compute_structural_shift_explanation

    result = compute_structural_shift_explanation(db, skill_id, year)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.get("/wormholes")
def career_wormholes(limit: int = 20, db: Session = Depends(get_db)):
    from app.models import OccupationTransition, Occupation

    rows = (
        db.query(OccupationTransition)
        .order_by(OccupationTransition.overlap_score.desc())
        .limit(limit)
        .all()
    )
    out = []
    for r in rows:
        source = db.get(Occupation, r.source_occupation_id)
        target = db.get(Occupation, r.target_occupation_id)
        out.append({
            "source_occupation": source.title,
            "target_occupation": target.title,
            "overlap_score": r.overlap_score,
            "shared_skills": [s.strip() for s in r.shared_skills.split(",") if s.strip()],
            "evidence_count": r.evidence_count,
        })
    return out

