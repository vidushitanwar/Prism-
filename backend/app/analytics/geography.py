"""
Geographic workforce intelligence. Reads job_postings (which carries
synthetic aggregated postings + compensation per skill/occupation/
industry/location/year) to answer "what does the workforce look like in
location X", plus a lightweight cross-reference against each skill's
global lifecycle stage to surface locally-emerging skills.
"""
from __future__ import annotations

import statistics

from sqlalchemy.orm import Session

from app.models import Location, JobPosting, Skill, Occupation, Industry, TemporalMetric


def list_locations_summary(db: Session, year: int) -> list[dict]:
    locations = db.query(Location).all()
    out = []
    for loc in locations:
        postings = db.query(JobPosting).filter(JobPosting.location_id == loc.id, JobPosting.year == year).all()
        total_postings = sum(p.postings_count for p in postings)
        salaries = [p.avg_salary_usd for p in postings if p.avg_salary_usd]
        out.append({
            "location_id": loc.id,
            "city": loc.city,
            "country": loc.country,
            "latitude": loc.latitude,
            "longitude": loc.longitude,
            "total_postings": total_postings,
            "avg_salary_usd": round(statistics.mean(salaries), -2) if salaries else None,
        })
    out.sort(key=lambda r: r["total_postings"], reverse=True)
    return out


def location_detail(db: Session, location_id: int, year: int) -> dict:
    loc = db.get(Location, location_id)
    if not loc:
        return {"error": "location not found"}

    postings = db.query(JobPosting).filter(JobPosting.location_id == location_id, JobPosting.year == year).all()

    skill_counts: dict[int, int] = {}
    occupation_counts: dict[int, int] = {}
    industry_counts: dict[int, int] = {}
    salaries = []
    for p in postings:
        if p.skill_id:
            skill_counts[p.skill_id] = skill_counts.get(p.skill_id, 0) + p.postings_count
        if p.occupation_id:
            occupation_counts[p.occupation_id] = occupation_counts.get(p.occupation_id, 0) + p.postings_count
        if p.industry_id:
            industry_counts[p.industry_id] = industry_counts.get(p.industry_id, 0) + p.postings_count
        if p.avg_salary_usd:
            salaries.append(p.avg_salary_usd)

    def top(counts: dict[int, int], model, name_attr: str, n: int = 8):
        ranked = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)[:n]
        return [{"name": getattr(db.get(model, k), name_attr), "postings": v} for k, v in ranked]

    top_skill_ids = sorted(skill_counts, key=lambda k: -skill_counts[k])[:15]
    emerging_here = []
    for sid in top_skill_ids:
        metric = db.query(TemporalMetric).filter(TemporalMetric.skill_id == sid, TemporalMetric.year == year).first()
        if metric and metric.lifecycle_stage in ("Emerging", "Growing"):
            emerging_here.append({
                "skill": db.get(Skill, sid).name,
                "growth_rate": metric.growth_rate,
                "local_postings": skill_counts[sid],
            })
    emerging_here.sort(key=lambda e: -e["growth_rate"])

    return {
        "location": {"id": loc.id, "city": loc.city, "country": loc.country},
        "year": year,
        "top_skills": top(skill_counts, Skill, "name"),
        "top_occupations": top(occupation_counts, Occupation, "title"),
        "top_industries": top(industry_counts, Industry, "name"),
        "avg_salary_usd": round(statistics.mean(salaries), -2) if salaries else None,
        "emerging_skills_here": emerging_here[:8],
    }
