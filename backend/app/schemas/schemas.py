"""
Pydantic response models. Kept separate from the SQLAlchemy models so the
API's public shape can evolve independently of the DB schema.
"""
from pydantic import BaseModel


class SkillOut(BaseModel):
    id: int
    name: str
    category: str
    model_config = {"from_attributes": True}


class OccupationOut(BaseModel):
    id: int
    title: str
    model_config = {"from_attributes": True}


class IndustryOut(BaseModel):
    id: int
    name: str
    model_config = {"from_attributes": True}


class TemporalMetricOut(BaseModel):
    year: int
    demand_score: float
    postings_count: int
    growth_rate: float
    lifecycle_stage: str
    model_config = {"from_attributes": True}


class SkillDetailOut(SkillOut):
    description: str | None = None
    timeline: list[TemporalMetricOut] = []
    related_skills: list[str] = []
    occupations: list[str] = []
    industries: list[str] = []


class WorkforceSignalOut(BaseModel):
    id: int
    signal_type: str
    subject_type: str
    subject_id: int
    title: str
    description: str
    magnitude: float | None = None
    confidence: float
    year: int | None = None
    evidence_json: str | None = None
    model_config = {"from_attributes": True}


class OccupationTransitionOut(BaseModel):
    source_occupation: str
    target_occupation: str
    overlap_score: float
    shared_skills: list[str]
    evidence_count: int


class GraphNodeOut(BaseModel):
    id: str
    type: str
    label: str
    category: str | None = None


class GraphEdgeOut(BaseModel):
    source: str
    target: str
    weight: float
    edge_type: str


class GraphResponse(BaseModel):
    nodes: list[GraphNodeOut]
    edges: list[GraphEdgeOut]
