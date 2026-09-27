"""
Generates PRISM's synthetic, internally-consistent 2022-2026 workforce
dataset and loads it into the database.

Pipeline (mirrors the architecture's data pipeline diagram):
  catalogs (skills/occupations/industries/...)
    -> insert base entities
    -> generate temporal demand curves per skill (skill_occurrences)
    -> aggregate into temporal_metrics (with lifecycle classification)
    -> derive skill_relationships from occupation co-membership
    -> derive industry_skills from category association
    -> derive occupation_transitions (Jaccard overlap)
    -> generate synthetic aggregated job_postings
    -> run analytics engine -> workforce_signals

Everything numeric is computed here or in app/analytics — nothing is a
hand-typed "47% growth" style claim. Randomness is seeded for
reproducibility across environments.
"""
from __future__ import annotations

import random
from itertools import combinations

from sqlalchemy.orm import Session

from app.db.database import Base, engine, SessionLocal
from app.models import (
    Skill,
    Occupation,
    Industry,
    Location,
    Education,
    OccupationSkill,
    SkillRelationship,
    IndustrySkill,
    SkillOccurrence,
    TemporalMetric,
    JobPosting,
    WorkforceSignal,
    OccupationTransition,
)
from app.analytics.lifecycle import classify_lifecycle_stage
from app.analytics import signals as signal_engine
from app.data.catalogs import (
    SKILLS,
    OCCUPATIONS,
    INDUSTRIES,
    LOCATIONS,
    EDUCATION_PROGRAMS,
)

YEARS = [2022, 2023, 2024, 2025, 2026]

random.seed(42)

# Archetype -> (start_range, yoy_growth_range, noise_pct)
ARCHETYPE_CURVES = {
    "emerging": {"start": (5, 14), "growth": (0.55, 0.95), "noise": 0.06},
    "growing": {"start": (18, 32), "growth": (0.16, 0.30), "noise": 0.05},
    "established": {"start": (60, 78), "growth": (0.01, 0.05), "noise": 0.04},
    "transforming": {"start": (45, 60), "growth": (0.06, 0.16), "noise": 0.05},
    "declining": {"start": (55, 72), "growth": (-0.16, -0.08), "noise": 0.05},
    "ghost": {"start": (22, 34), "growth": (-0.32, -0.18), "noise": 0.06},
}


def _generate_demand_curve(archetype: str) -> list[float]:
    cfg = ARCHETYPE_CURVES[archetype]
    start = random.uniform(*cfg["start"])
    growth = random.uniform(*cfg["growth"])
    values = [start]
    for _ in YEARS[1:]:
        noise = random.uniform(-cfg["noise"], cfg["noise"])
        next_val = values[-1] * (1 + growth + noise)
        values.append(max(1.0, next_val))
    # Cap at 100 to keep the demand index bounded and comparable across skills.
    return [min(100.0, v) for v in values]


def reset_database() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def is_seeded(db: Session) -> bool:
    return db.query(Skill).first() is not None


def _insert_base_entities(db: Session) -> tuple[dict, dict, dict, list[Location], dict]:
    skill_by_name: dict[str, Skill] = {}
    for s in SKILLS:
        row = Skill(name=s["name"], category=s["category"], lifecycle_archetype=s["archetype"])
        db.add(row)
        skill_by_name[s["name"]] = row
    db.flush()

    occupation_by_title: dict[str, Occupation] = {}
    for o in OCCUPATIONS:
        row = Occupation(title=o["title"])
        db.add(row)
        occupation_by_title[o["title"]] = row
    db.flush()

    industry_by_name: dict[str, Industry] = {}
    for i in INDUSTRIES:
        row = Industry(name=i["name"])
        db.add(row)
        industry_by_name[i["name"]] = row
    db.flush()

    locations: list[Location] = []
    for loc in LOCATIONS:
        row = Location(
            city=loc["city"], region=loc["region"], country=loc["country"],
            latitude=loc["lat"], longitude=loc["lon"],
        )
        db.add(row)
        locations.append(row)
    db.flush()

    for edu in EDUCATION_PROGRAMS:
        db.add(Education(
            name=edu["name"],
            program_type=edu["type"],
            curriculum_skills=", ".join(edu["skills"]),
        ))
    db.flush()

    return skill_by_name, occupation_by_title, industry_by_name, locations, {}


def _insert_occupation_skills(db: Session, skill_by_name, occupation_by_title) -> None:
    for o in OCCUPATIONS:
        occ = occupation_by_title[o["title"]]
        for skill_name, weight in o["skills"]:
            skill = skill_by_name.get(skill_name)
            if not skill:
                continue
            db.add(OccupationSkill(occupation_id=occ.id, skill_id=skill.id, weight=weight))
    db.flush()


def _insert_temporal_data(db: Session, skill_by_name, locations: list[Location]) -> None:
    for s in SKILLS:
        skill = skill_by_name[s["name"]]
        curve = _generate_demand_curve(s["archetype"])
        prev_score = None

        for idx, year in enumerate(YEARS):
            demand_score = curve[idx]
            growth_rate = 0.0 if prev_score is None else round(100 * (demand_score - prev_score) / prev_score, 2)
            postings_count = int(demand_score * random.uniform(60, 160))

            stage = classify_lifecycle_stage(
                demand_score=demand_score,
                growth_rate=growth_rate,
                is_first_year=(prev_score is None),
                transforming_hint=(s["archetype"] == "transforming"),
            )

            db.add(TemporalMetric(
                skill_id=skill.id, year=year, demand_score=round(demand_score, 2),
                postings_count=postings_count, growth_rate=growth_rate, lifecycle_stage=stage,
            ))

            # Split raw occurrences across a handful of locations for realism.
            sample_locations = random.sample(locations, k=min(5, len(locations)))
            remaining = postings_count
            for j, loc in enumerate(sample_locations):
                share = remaining if j == len(sample_locations) - 1 else int(postings_count * random.uniform(0.1, 0.3))
                share = max(0, min(share, remaining))
                remaining -= share
                db.add(SkillOccurrence(skill_id=skill.id, location_id=loc.id, year=year, occurrence_count=share))

            prev_score = demand_score
    db.flush()


def _insert_skill_relationships(db: Session, skill_by_name) -> None:
    co_occurrence: dict[tuple[int, int], float] = {}

    for o in OCCUPATIONS:
        skills_in_occ = [(skill_by_name[name].id, weight) for name, weight in o["skills"] if name in skill_by_name]
        for (id_a, w_a), (id_b, w_b) in combinations(skills_in_occ, 2):
            key = tuple(sorted((id_a, id_b)))
            co_occurrence[key] = co_occurrence.get(key, 0.0) + min(w_a, w_b)

    if not co_occurrence:
        return
    max_weight = max(co_occurrence.values())

    # Keep only the strongest edges per skill to avoid an overly dense graph.
    per_skill: dict[int, list[tuple[float, tuple[int, int]]]] = {}
    for pair, raw_weight in co_occurrence.items():
        norm_weight = raw_weight / max_weight
        for sid in pair:
            per_skill.setdefault(sid, []).append((norm_weight, pair))

    kept_pairs: dict[tuple[int, int], float] = {}
    for sid, edges in per_skill.items():
        edges.sort(key=lambda e: e[0], reverse=True)
        for norm_weight, pair in edges[:10]:
            kept_pairs[pair] = max(kept_pairs.get(pair, 0), norm_weight)

    for (id_a, id_b), weight in kept_pairs.items():
        if weight < 0.05:
            continue
        db.add(SkillRelationship(skill_a_id=id_a, skill_b_id=id_b, weight=round(weight, 3)))
    db.flush()


def _insert_industry_skills(db: Session, skill_by_name, industry_by_name) -> None:
    category_to_skills: dict[str, list[Skill]] = {}
    for s in SKILLS:
        category_to_skills.setdefault(s["category"], []).append(skill_by_name[s["name"]])

    latest_scores = {
        row.skill_id: row.demand_score
        for row in db.query(TemporalMetric).filter(TemporalMetric.year == 2026).all()
    }

    for i in INDUSTRIES:
        industry = industry_by_name[i["name"]]
        candidate_skills: list[Skill] = []
        for cat in i["core_categories"]:
            candidate_skills.extend(category_to_skills.get(cat, []))
        # Dedup, then prioritize by current demand so each industry keeps
        # a meaningful (not exhaustive) top set — matches "10-20 skills".
        unique = {s.id: s for s in candidate_skills}
        ranked = sorted(unique.values(), key=lambda s: latest_scores.get(s.id, 0), reverse=True)
        top = ranked[:18]
        for rank, skill in enumerate(top):
            weight = round(1.0 - (rank / max(len(top), 1)) * 0.5, 3)
            db.add(IndustrySkill(industry_id=industry.id, skill_id=skill.id, weight=weight))
    db.flush()


def _insert_job_postings(db: Session, skill_by_name, occupation_by_title, industry_by_name, locations) -> None:
    industry_by_id = {i.id: i for i in industry_by_name.values()}
    industry_skill_map: dict[int, list[int]] = {}
    for link in db.query(IndustrySkill).all():
        industry_skill_map.setdefault(link.skill_id, []).append(link.industry_id)

    latest_scores = {
        (row.skill_id, row.year): row.demand_score
        for row in db.query(TemporalMetric).all()
    }

    location_cost_multiplier = {
        "United States": 1.35, "United Kingdom": 1.15, "Canada": 1.1,
        "Germany": 1.1, "Netherlands": 1.1, "France": 1.05, "Singapore": 1.2,
        "Australia": 1.15, "India": 0.45, "Brazil": 0.55,
    }
    base_salary = {
        "AI/ML": 135000, "Software Engineering": 118000, "Data": 110000,
        "Cloud & Infra": 122000, "Security": 120000, "Product & Design": 115000,
        "Business": 90000, "Healthcare": 105000, "Manufacturing & Energy": 95000,
        "Finance": 125000, "Cross-Cutting": 95000,
    }
    skill_category = {s["name"]: s["category"] for s in SKILLS}

    for o in OCCUPATIONS:
        occ = occupation_by_title[o["title"]]
        top_skill_name, _ = max(o["skills"], key=lambda t: t[1])
        top_skill = skill_by_name[top_skill_name]
        candidate_industries = industry_skill_map.get(top_skill.id, list(industry_by_id.keys()))

        for year in YEARS:
            demand = latest_scores.get((top_skill.id, year), 30)
            sampled_industries = random.sample(
                candidate_industries, k=min(2, len(candidate_industries))
            )
            sampled_locations = random.sample(locations, k=min(2, len(locations)))
            for industry_id in sampled_industries:
                for loc in sampled_locations:
                    category = skill_category.get(top_skill_name, "Cross-Cutting")
                    salary = base_salary.get(category, 100000) * location_cost_multiplier.get(loc.country, 0.7)
                    salary *= random.uniform(0.9, 1.1)
                    postings = int(demand * random.uniform(3, 9))
                    db.add(JobPosting(
                        skill_id=top_skill.id, occupation_id=occ.id, industry_id=industry_id,
                        location_id=loc.id, year=year, postings_count=postings,
                        avg_salary_usd=round(salary, -2),
                    ))
    db.flush()


def _run_analytics_and_store_signals(db: Session) -> None:
    all_signals = (
        signal_engine.compute_emerging_skills(db)
        + signal_engine.compute_ghost_skills(db)
        + signal_engine.compute_structural_shifts(db)
        + signal_engine.compute_bridge_skills(db)
        + signal_engine.compute_capability_clusters(db)
        + signal_engine.compute_combination_clusters(db)
        + signal_engine.compute_talent_gaps(db)
    )
    for s in all_signals:
        db.add(s)

    for t in signal_engine.compute_occupation_transitions(db):
        db.add(t)

    db.flush()


def seed_all(force: bool = False) -> dict:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if is_seeded(db) and not force:
            return {"status": "already_seeded", "skipped": True}

        if force:
            reset_database()

        skill_by_name, occupation_by_title, industry_by_name, locations, _ = _insert_base_entities(db)
        _insert_occupation_skills(db, skill_by_name, occupation_by_title)
        _insert_temporal_data(db, skill_by_name, locations)
        _insert_skill_relationships(db, skill_by_name)
        _insert_industry_skills(db, skill_by_name, industry_by_name)
        _insert_job_postings(db, skill_by_name, occupation_by_title, industry_by_name, locations)
        _run_analytics_and_store_signals(db)

        db.commit()
        return {
            "status": "seeded",
            "skills": db.query(Skill).count(),
            "occupations": db.query(Occupation).count(),
            "industries": db.query(Industry).count(),
            "locations": db.query(Location).count(),
            "education_programs": db.query(Education).count(),
            "occupation_skills": db.query(OccupationSkill).count(),
            "skill_relationships": db.query(SkillRelationship).count(),
            "industry_skills": db.query(IndustrySkill).count(),
            "temporal_metrics": db.query(TemporalMetric).count(),
            "job_postings": db.query(JobPosting).count(),
            "workforce_signals": db.query(WorkforceSignal).count(),
            "occupation_transitions": db.query(OccupationTransition).count(),
        }
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import json
    result = seed_all(force="--force" in __import__("sys").argv)
    print(json.dumps(result, indent=2))
