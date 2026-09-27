export type NodeType = "skill" | "occupation" | "industry";

export interface GraphNode {
  id: string; // e.g. "skill:12"
  type: NodeType;
  label: string;
  category?: string;
}

export interface GraphEdge {
  source: string;
  target: string;
  weight: number;
  edge_type: "occupation_skill" | "skill_skill" | "industry_skill";
}

export interface GraphResponse {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface SearchResultItem {
  id: number;
  name: string;
  node_id: string;
}

export interface SearchResponse {
  query: string;
  results: {
    skills: SearchResultItem[];
    occupations: SearchResultItem[];
    industries: SearchResultItem[];
  };
}

export interface TemporalMetric {
  year: number;
  demand_score: number;
  postings_count: number;
  growth_rate: number;
  lifecycle_stage: string;
}

export interface SkillDetail {
  id: number;
  name: string;
  category: string;
  description: string | null;
  timeline: TemporalMetric[];
  related_skills: string[];
  occupations: string[];
  industries: string[];
}

export interface OccupationOut {
  id: number;
  title: string;
}

export interface OccupationDetail {
  id: number;
  title: string;
  description: string | null;
  core_skills: { id: number; name: string; weight: number }[];
}

export interface EvolutionPoint {
  year: number;
  avg_demand_score: number;
}

export interface IndustryDetail {
  id: number;
  name: string;
  description: string | null;
  top_skills: { id: number; name: string; weight: number }[];
}

export interface WorkforceSignal {
  id: number;
  signal_type: string;
  subject_type: string;
  subject_id: number;
  title: string;
  description: string;
  magnitude: number | null;
  confidence: number;
  year: number | null;
  evidence_json?: string | null;
}

export interface OccupationTransition {
  source_occupation: string;
  target_occupation: string;
  overlap_score: number;
  shared_skills: string[];
  evidence_count: number;
}

export interface SkillSnapshot {
  skill_id: number;
  name: string;
  demand_score: number;
  growth_rate: number;
  lifecycle_stage: string;
  postings_count: number;
}

export interface WorkforceSnapshot {
  year: number;
  skills: SkillSnapshot[];
}

export interface YearsResponse {
  years: number[];
  earliest: number;
  latest: number;
}

export interface RouteHop {
  from_occupation: string;
  to_occupation: string;
  overlap_score: number;
  shared_skills: string[];
  evidence_count: number;
}

export interface CareerRoute {
  label: string;
  occupations: string[];
  hops: RouteHop[];
  total_evidence_count: number;
  industry_context: string[];
}

export interface CareerRoutesResponse {
  source_occupation: string;
  target_occupation: string;
  existing_overlap: string[];
  missing_capabilities: string[];
  routes: CareerRoute[];
  note: string | null;
}

export interface WhySignal {
  label: string;
  contribution_pct_points: number;
}

export interface WhyExplanation {
  skill: string;
  year: number;
  observed_growth_rate: number;
  signals: WhySignal[];
  evidence: string;
}

// --- Phase 5: Talent DNA, Geography, Education ---

export interface TalentDnaCategory {
  category: string;
  strength: number;
  skill_count: number;
}

export interface TalentDnaOccupationMatch {
  occupation: string;
  match_score: number;
  missing_capabilities: string[];
}

export interface TalentDnaCluster {
  title: string;
  description: string;
  shared_skill_count: number;
}

export interface TalentDnaResponse {
  dna_profile: TalentDnaCategory[];
  matched_skills: { skill_id: number; name: string; category: string; strength: number }[];
  unmatched_skills: string[];
  nearest_occupations: TalentDnaOccupationMatch[];
  nearby_capability_clusters: TalentDnaCluster[];
  method: string;
  note: string;
}

export interface LocationSummary {
  location_id: number;
  city: string | null;
  country: string;
  latitude: number | null;
  longitude: number | null;
  total_postings: number;
  avg_salary_usd: number | null;
}

export interface LocationDetail {
  location: { id: number; city: string | null; country: string };
  year: number;
  top_skills: { name: string; postings: number }[];
  top_occupations: { name: string; postings: number }[];
  top_industries: { name: string; postings: number }[];
  avg_salary_usd: number | null;
  emerging_skills_here: { skill: string; growth_rate: number; local_postings: number }[];
}

export interface EducationProgram {
  id: number;
  name: string;
  program_type: string;
  curriculum_skills: string[];
  high_demand_coverage: string;
}

export interface EducationGapAnalysis {
  program: string;
  program_type: string;
  curriculum_skills: string[];
  covered_high_demand_skills: { skill: string; demand_score: number; lifecycle_stage: string }[];
  gap_high_demand_skills: { skill: string; demand_score: number; lifecycle_stage: string }[];
  coverage_ratio: number;
  note: string;
}

// --- Phase 6: Simulation ---

export interface SkillImpact {
  skill_id: number;
  name: string;
  category: string;
  baseline_demand: number;
  scenario_demand: number;
  delta: number;
  baseline_postings: number;
}

export interface OccupationImpact {
  occupation: string;
  avg_delta: number;
}

export interface IndustryImpact {
  industry: string;
  avg_delta: number;
}

export interface WorkforceMirrorRow {
  category: string;
  current_avg_demand: number;
  scenario_avg_demand: number;
}

export interface SimulationResult {
  parameters: {
    tech_adoption: number;
    automation: number;
    skill_shortage: number;
    shock_skill_id: number | null;
  };
  summary: {
    skills_affected: number;
    avg_delta: number;
    max_positive_delta: number;
    max_negative_delta: number;
  };
  first_affected_capabilities: SkillImpact[];
  bottleneck_capabilities: SkillImpact[];
  occupations_under_pressure: OccupationImpact[];
  occupations_in_demand: OccupationImpact[];
  industries_affected: IndustryImpact[];
  workforce_mirror: WorkforceMirrorRow[];
  method: string;
  disclaimer: string;
  preset?: { key: string; label: string; description: string };
}

export interface SimulationPreset {
  key: string;
  label: string;
  description: string;
  params: { tech_adoption: number; automation: number; skill_shortage: number };
  shock_skill_name?: string;
}


