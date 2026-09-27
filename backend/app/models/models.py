"""
PRISM database schema.

Tables mirror the workforce graph domain: skills, occupations, industries,
locations, education, job postings, and the derived/analytical tables
(temporal metrics, workforce signals, simulation results) that the
analytics engine and API read from.

All "derived" tables (temporal_metrics, workforce_signals,
occupation_transitions, simulation_results) are populated by code in
app/analytics and app/data — never hand-typed marketing claims.
"""
from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Text,
    ForeignKey,
    DateTime,
    UniqueConstraint,
    Index,
)
from sqlalchemy.orm import relationship

from app.db.database import Base


class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True)
    name = Column(String(160), unique=True, nullable=False, index=True)
    category = Column(String(80), nullable=False, index=True)
    # Ground-truth archetype used to *generate* the seed dataset's temporal
    # curve. Real lifecycle_stage per year is still derived analytically
    # (see analytics/lifecycle.py) from the resulting demand numbers, not
    # copied from this field.
    lifecycle_archetype = Column(String(40), nullable=False)
    description = Column(Text, nullable=True)

    occupation_links = relationship("OccupationSkill", back_populates="skill")
    industry_links = relationship("IndustrySkill", back_populates="skill")
    occurrences = relationship("SkillOccurrence", back_populates="skill")
    temporal_metrics = relationship("TemporalMetric", back_populates="skill")


class Occupation(Base):
    __tablename__ = "occupations"

    id = Column(Integer, primary_key=True)
    title = Column(String(160), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)

    skill_links = relationship("OccupationSkill", back_populates="occupation")


class Industry(Base):
    __tablename__ = "industries"

    id = Column(Integer, primary_key=True)
    name = Column(String(120), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)

    skill_links = relationship("IndustrySkill", back_populates="industry")


class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True)
    city = Column(String(120), nullable=True)
    region = Column(String(120), nullable=True)
    country = Column(String(120), nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)


class Education(Base):
    __tablename__ = "education"

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    program_type = Column(String(60), nullable=False)  # e.g. "University Program", "Bootcamp", "Certification"
    # Comma-separated skill names the curriculum is presumed to teach.
    # Used only to compute curriculum-vs-demand gaps in Phase 5 — never
    # attributed to a specific real institution.
    curriculum_skills = Column(Text, nullable=False, default="")


class OccupationSkill(Base):
    __tablename__ = "occupation_skills"
    __table_args__ = (UniqueConstraint("occupation_id", "skill_id", name="uq_occupation_skill"),)

    id = Column(Integer, primary_key=True)
    occupation_id = Column(Integer, ForeignKey("occupations.id"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)
    weight = Column(Float, nullable=False, default=1.0)  # relative importance of skill to occupation

    occupation = relationship("Occupation", back_populates="skill_links")
    skill = relationship("Skill", back_populates="occupation_links")


class SkillRelationship(Base):
    """
    Skill <-> Skill edges. weight = co-occurrence strength, derived from
    how often two skills appear together across occupations (see
    app/data/seed_generator.py and app/analytics/graph_metrics.py).
    """
    __tablename__ = "skill_relationships"
    __table_args__ = (UniqueConstraint("skill_a_id", "skill_b_id", name="uq_skill_pair"),)

    id = Column(Integer, primary_key=True)
    skill_a_id = Column(Integer, ForeignKey("skills.id"), nullable=False)
    skill_b_id = Column(Integer, ForeignKey("skills.id"), nullable=False)
    weight = Column(Float, nullable=False)
    relationship_type = Column(String(40), nullable=False, default="co-occurs-with")


class IndustrySkill(Base):
    __tablename__ = "industry_skills"
    __table_args__ = (UniqueConstraint("industry_id", "skill_id", name="uq_industry_skill"),)

    id = Column(Integer, primary_key=True)
    industry_id = Column(Integer, ForeignKey("industries.id"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)
    weight = Column(Float, nullable=False, default=1.0)

    industry = relationship("Industry", back_populates="skill_links")
    skill = relationship("Skill", back_populates="industry_links")


class OccupationTransition(Base):
    """
    "Career Wormholes" — occupation-to-occupation transitions. overlap_score
    is computed from shared-skill Jaccard similarity, not hand-authored.
    """
    __tablename__ = "occupation_transitions"

    id = Column(Integer, primary_key=True)
    source_occupation_id = Column(Integer, ForeignKey("occupations.id"), nullable=False)
    target_occupation_id = Column(Integer, ForeignKey("occupations.id"), nullable=False)
    overlap_score = Column(Float, nullable=False)  # 0-1 Jaccard similarity of skill sets
    shared_skills = Column(Text, nullable=False, default="")  # comma-separated skill names
    evidence_count = Column(Integer, nullable=False, default=0)  # synthetic supporting-record count


class SkillOccurrence(Base):
    """
    Raw per-year occurrence counts, the input to temporal aggregation.
    Roughly analogous to "how many observed postings/records mentioned
    this skill in this year", optionally split by location.
    """
    __tablename__ = "skill_occurrences"

    id = Column(Integer, primary_key=True)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=True)
    year = Column(Integer, nullable=False)
    occurrence_count = Column(Integer, nullable=False)

    skill = relationship("Skill", back_populates="occurrences")

    __table_args__ = (Index("ix_skill_occurrence_year", "skill_id", "year"),)


class TemporalMetric(Base):
    """
    The aggregated, analytics-ready per-skill-per-year record. This is
    what the Skill Evolution Engine / Time Machine / Emerging & Ghost
    Skills features read from.
    """
    __tablename__ = "temporal_metrics"
    __table_args__ = (UniqueConstraint("skill_id", "year", name="uq_skill_year"),)

    id = Column(Integer, primary_key=True)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)
    year = Column(Integer, nullable=False)
    demand_score = Column(Float, nullable=False)  # normalized 0-100 relative demand index
    postings_count = Column(Integer, nullable=False)
    growth_rate = Column(Float, nullable=False)  # year-over-year % change; 0 for the first year on record
    lifecycle_stage = Column(String(40), nullable=False)  # Emerging / Growing / Established / Transforming / Declining / Ghost

    skill = relationship("Skill", back_populates="temporal_metrics")


class WorkforceSignal(Base):
    """
    Precomputed, evidence-linked insights: emerging skills, ghost skills,
    structural shifts, bridge skills, capability clusters, etc. Each row
    is produced by app/analytics code from the tables above — the API and
    frontend never hardcode these.
    """
    __tablename__ = "workforce_signals"

    id = Column(Integer, primary_key=True)
    signal_type = Column(String(60), nullable=False, index=True)
    # e.g. "emerging_skill", "ghost_skill", "structural_shift", "bridge_skill",
    # "capability_cluster", "combination_cluster"
    subject_type = Column(String(40), nullable=False)  # "skill" | "occupation" | "industry"
    subject_id = Column(Integer, nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    magnitude = Column(Float, nullable=True)  # e.g. growth %, z-score, industry count
    confidence = Column(Float, nullable=False)  # 0-1, derived from sample size / consistency
    year = Column(Integer, nullable=True)
    evidence_json = Column(Text, nullable=False, default="{}")  # method, sample size, data window
    generated_at = Column(DateTime, default=datetime.utcnow)


class JobPosting(Base):
    """
    Synthetic aggregated posting/demand records — NOT individual scraped
    postings. Each row represents a count + average compensation for a
    (skill, occupation, industry, location, year) combination in the
    seed dataset, clearly labeled as demo data in the UI.
    """
    __tablename__ = "job_postings"

    id = Column(Integer, primary_key=True)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=True)
    occupation_id = Column(Integer, ForeignKey("occupations.id"), nullable=True)
    industry_id = Column(Integer, ForeignKey("industries.id"), nullable=True)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=True)
    year = Column(Integer, nullable=False)
    postings_count = Column(Integer, nullable=False)
    avg_salary_usd = Column(Float, nullable=True)

    __table_args__ = (Index("ix_job_posting_year", "year"),)


class SimulationResult(Base):
    """
    Stores Workforce Shock Simulator runs (Phase 6) so results are
    reproducible for identical inputs rather than regenerated randomly
    each time.
    """
    __tablename__ = "simulation_results"

    id = Column(Integer, primary_key=True)
    input_params_json = Column(Text, nullable=False)
    input_hash = Column(String(64), nullable=False, index=True)
    result_json = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
