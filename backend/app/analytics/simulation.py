"""
Workforce Shock Simulator.

Given three 0-100 scenario dials (technology adoption, automation, skill
shortage) — plus an optional "sudden demand spike" target skill — computes
a deterministic, explainable propagation of impact across:

    skills -> occupations -> industries

This is a **scenario simulation**, not a forecast: the effect model is a
transparent, documented set of category-level sensitivity multipliers
(see the *_SENSITIVITY dicts below), not a fitted predictive model. The
function is pure (no randomness), so identical inputs always produce
identical outputs — reproducibility is enforced at the API layer via a
content hash + the simulation_results table, but the engine itself is
deterministic by construction.
"""
from __future__ import annotations

import hashlib
import json
import statistics

from sqlalchemy.orm import Session

from app.models import Skill, Occupation, Industry, OccupationSkill, IndustrySkill, TemporalMetric, SimulationResult

LATEST_YEAR = 2026

TECH_ADOPTION_SENSITIVITY = {
    "AI/ML": 0.55, "Cloud & Infra": 0.35, "Security": 0.25, "Data": 0.30,
    "Software Engineering": 0.15, "Product & Design": 0.10, "Healthcare": 0.20,
    "Manufacturing & Energy": 0.20, "Finance": 0.20, "Business": 0.05, "Cross-Cutting": 0.10,
}
AUTOMATION_SENSITIVITY = {
    "Software Engineering": -0.10, "Business": -0.15, "Manufacturing & Energy": 0.15,
    "AI/ML": 0.30, "Cloud & Infra": 0.15, "Data": 0.10, "Cross-Cutting": -0.05,
}
SKILL_SHORTAGE_AMPLIFIER = 0.4


def compute_input_hash(params: dict) -> str:
    normalized = json.dumps(params, sort_keys=True)
    return hashlib.sha256(normalized.encode()).hexdigest()


def _baseline(db: Session, year: int = LATEST_YEAR) -> dict[int, dict]:
    rows = db.query(TemporalMetric).filter(TemporalMetric.year == year).all()
    return {
        r.skill_id: {
            "demand_score": r.demand_score, "growth_rate": r.growth_rate,
            "stage": r.lifecycle_stage, "postings": r.postings_count,
        }
        for r in rows
    }


def _run_pure(db: Session, tech_adoption: float, automation: float, skill_shortage: float, shock_skill_id: int | None) -> dict:
    baseline = _baseline(db)
    skills = {s.id: s for s in db.query(Skill).all()}

    skill_impacts = {}
    for sid, base in baseline.items():
        skill = skills[sid]
        tech_effect = TECH_ADOPTION_SENSITIVITY.get(skill.category, 0.05) * (tech_adoption / 100) * 20
        auto_effect = AUTOMATION_SENSITIVITY.get(skill.category, 0.0) * (automation / 100) * 20

        shortage_effect = 0.0
        if base["stage"] in ("Emerging", "Growing") and skill_shortage > 0:
            shortage_effect = (base["growth_rate"] / 100) * skill_shortage * SKILL_SHORTAGE_AMPLIFIER

        shock_effect = 40.0 if (shock_skill_id is not None and sid == shock_skill_id) else 0.0

        delta = tech_effect + auto_effect + shortage_effect + shock_effect
        new_score = max(0.0, min(100.0, base["demand_score"] + delta))
        skill_impacts[sid] = {
            "skill_id": sid, "name": skill.name, "category": skill.category,
            "baseline_demand": base["demand_score"], "scenario_demand": round(new_score, 2),
            "delta": round(delta, 2), "baseline_postings": base["postings"],
        }

    occupation_impacts = []
    for occ in db.query(Occupation).all():
        links = db.query(OccupationSkill).filter(OccupationSkill.occupation_id == occ.id).all()
        if not links:
            continue
        weighted_delta = sum(skill_impacts[l.skill_id]["delta"] * l.weight for l in links if l.skill_id in skill_impacts)
        total_weight = sum(l.weight for l in links if l.skill_id in skill_impacts)
        avg_delta = weighted_delta / total_weight if total_weight else 0
        occupation_impacts.append({"occupation": occ.title, "avg_delta": round(avg_delta, 2)})

    industry_impacts = []
    for ind in db.query(Industry).all():
        links = db.query(IndustrySkill).filter(IndustrySkill.industry_id == ind.id).all()
        if not links:
            continue
        weighted_delta = sum(skill_impacts[l.skill_id]["delta"] * l.weight for l in links if l.skill_id in skill_impacts)
        total_weight = sum(l.weight for l in links if l.skill_id in skill_impacts)
        avg_delta = weighted_delta / total_weight if total_weight else 0
        industry_impacts.append({"industry": ind.name, "avg_delta": round(avg_delta, 2)})

    all_deltas = [v["delta"] for v in skill_impacts.values()]
    median_postings = statistics.median([v["baseline_postings"] for v in skill_impacts.values()]) if skill_impacts else 0

    first_affected = sorted(skill_impacts.values(), key=lambda v: -abs(v["delta"]))[:8]
    bottlenecks = sorted(
        [v for v in skill_impacts.values() if v["delta"] > 5 and v["baseline_postings"] < median_postings],
        key=lambda v: -v["delta"],
    )[:8]
    occupations_under_pressure = sorted([o for o in occupation_impacts if o["avg_delta"] < -2], key=lambda o: o["avg_delta"])[:8]
    occupations_in_demand = sorted([o for o in occupation_impacts if o["avg_delta"] > 2], key=lambda o: -o["avg_delta"])[:8]
    industries_affected = sorted(industry_impacts, key=lambda i: -abs(i["avg_delta"]))[:10]

    category_baseline: dict[str, list[float]] = {}
    category_scenario: dict[str, list[float]] = {}
    for v in skill_impacts.values():
        category_baseline.setdefault(v["category"], []).append(v["baseline_demand"])
        category_scenario.setdefault(v["category"], []).append(v["scenario_demand"])
    mirror = [
        {
            "category": cat,
            "current_avg_demand": round(statistics.mean(vals), 1),
            "scenario_avg_demand": round(statistics.mean(category_scenario.get(cat, vals)), 1),
        }
        for cat, vals in category_baseline.items()
    ]
    mirror.sort(key=lambda m: -abs(m["scenario_avg_demand"] - m["current_avg_demand"]))

    return {
        "parameters": {
            "tech_adoption": tech_adoption, "automation": automation,
            "skill_shortage": skill_shortage, "shock_skill_id": shock_skill_id,
        },
        "summary": {
            "skills_affected": sum(1 for d in all_deltas if abs(d) > 1),
            "avg_delta": round(statistics.mean(all_deltas), 2) if all_deltas else 0,
            "max_positive_delta": round(max(all_deltas), 2) if all_deltas else 0,
            "max_negative_delta": round(min(all_deltas), 2) if all_deltas else 0,
        },
        "first_affected_capabilities": first_affected,
        "bottleneck_capabilities": bottlenecks,
        "occupations_under_pressure": occupations_under_pressure,
        "occupations_in_demand": occupations_in_demand,
        "industries_affected": industries_affected,
        "workforce_mirror": mirror,
        "method": "deterministic_category_sensitivity_propagation",
        "disclaimer": (
            "This is a scenario simulation using illustrative, documented sensitivity "
            "coefficients — not a predictive forecast. Identical inputs always produce "
            "identical outputs."
        ),
    }


def run_or_get_cached_simulation(
    db: Session, tech_adoption: float, automation: float, skill_shortage: float, shock_skill_id: int | None = None
) -> dict:
    params = {
        "tech_adoption": round(tech_adoption, 1), "automation": round(automation, 1),
        "skill_shortage": round(skill_shortage, 1), "shock_skill_id": shock_skill_id,
    }
    input_hash = compute_input_hash(params)

    cached = db.query(SimulationResult).filter(SimulationResult.input_hash == input_hash).first()
    if cached:
        return json.loads(cached.result_json)

    result = _run_pure(db, tech_adoption, automation, skill_shortage, shock_skill_id)
    db.add(SimulationResult(input_params_json=json.dumps(params), input_hash=input_hash, result_json=json.dumps(result)))
    db.commit()
    return result


PRESET_SCENARIOS = [
    {
        "key": "ai_adoption_surge",
        "label": "AI Adoption +30%",
        "description": "A sharp increase in enterprise AI/ML adoption across industries.",
        "params": {"tech_adoption": 30, "automation": 5, "skill_shortage": 10},
    },
    {
        "key": "automation_wave",
        "label": "Automation +25%",
        "description": "Broad automation of routine engineering and business-process work.",
        "params": {"tech_adoption": 10, "automation": 25, "skill_shortage": 5},
    },
    {
        "key": "cloud_talent_shortage",
        "label": "Cloud Talent Shortage",
        "description": "Demand for cloud/infra skills outpaces the available talent pool.",
        "params": {"tech_adoption": 15, "automation": 5, "skill_shortage": 40},
    },
    {
        "key": "sudden_demand_spike",
        "label": "Sudden Demand Spike: AI Agents",
        "description": "A single skill suddenly spikes in demand — tests bottleneck detection.",
        "params": {"tech_adoption": 5, "automation": 0, "skill_shortage": 20},
        "shock_skill_name": "AI Agents",
    },
]
