/**
 * Thin, typed wrapper around the PRISM backend API.
 * Later phases add methods here (search, skills, graph, simulation, etc.)
 * rather than scattering fetch() calls across components.
 */
import type {
  GraphResponse,
  SearchResponse,
  SkillDetail,
  OccupationDetail,
  OccupationOut,
  IndustryDetail,
  TemporalMetric,
  WorkforceSignal,
  OccupationTransition,
  WorkforceSnapshot,
  YearsResponse,
  CareerRoutesResponse,
  WhyExplanation,
  TalentDnaResponse,
  LocationSummary,
  LocationDetail,
  EducationProgram,
  EducationGapAnalysis,
  SimulationResult,
  SimulationPreset,
  EvolutionPoint,
} from "@/types/graph";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  if (!res.ok) {
    let message = `Request failed with status ${res.status}`;
    try {
      const body = await res.json();
      message = body.message || message;
    } catch {
      // response wasn't JSON — keep default message
    }
    throw new ApiError(message, res.status);
  }

  return res.json() as Promise<T>;
}

export interface HealthStatus {
  status: string;
  service?: string;
  database?: string;
}

export const api = {
  health: () => request<HealthStatus>("/health"),
  healthDb: () => request<HealthStatus>("/health/db"),

  search: (q: string) => request<SearchResponse>(`/search?q=${encodeURIComponent(q)}`),

  getGraph: (params?: { nodeId?: string; depth?: number; maxNodes?: number }) => {
    const qs = new URLSearchParams();
    if (params?.nodeId) qs.set("node_id", params.nodeId);
    if (params?.depth) qs.set("depth", String(params.depth));
    if (params?.maxNodes) qs.set("max_nodes", String(params.maxNodes));
    const query = qs.toString();
    return request<GraphResponse>(`/graph${query ? `?${query}` : ""}`);
  },

  getSkill: (id: number) => request<SkillDetail>(`/skills/${id}`),
  getSkillTimeline: (id: number) => request<TemporalMetric[]>(`/skills/${id}/timeline`),
  getOccupation: (id: number) => request<OccupationDetail>(`/occupations/${id}`),
  listOccupations: () => request<OccupationOut[]>("/occupations"),
  getOccupationEvolution: (id: number) =>
    request<{ occupation: string; evolution: EvolutionPoint[] }>(`/occupations/${id}/evolution`),
  getIndustry: (id: number) => request<IndustryDetail>(`/industries/${id}`),
  getIndustryEvolution: async (id: number) => {
    const industry = await api.getIndustry(id);
    const timelines = await Promise.all(industry.top_skills.map((skill) => api.getSkillTimeline(skill.id)));
    const byYear = new Map<number, number[]>();

    for (const timeline of timelines) {
      for (const point of timeline) {
        const values = byYear.get(point.year) ?? [];
        values.push(point.demand_score);
        byYear.set(point.year, values);
      }
    }

    return {
      industry: industry.name,
      evolution: Array.from(byYear.entries())
        .sort(([firstYear], [secondYear]) => firstYear - secondYear)
        .map(([year, values]) => ({
          year,
          avg_demand_score: Number((values.reduce((sum, value) => sum + value, 0) / values.length).toFixed(2)),
        })),
    };
  },

  getEmergingSkills: (limit = 15, year?: number) =>
    request<WorkforceSignal[]>(`/workforce/emerging?limit=${limit}${year ? `&year=${year}` : ""}`),
  getDecliningSkills: (limit = 15, year?: number) =>
    request<WorkforceSignal[]>(`/workforce/declining?limit=${limit}${year ? `&year=${year}` : ""}`),
  getStructuralShifts: (limit = 15) => request<WorkforceSignal[]>(`/workforce/shifts?limit=${limit}`),
  getBridgeSkills: (limit = 15) => request<WorkforceSignal[]>(`/workforce/bridges?limit=${limit}`),
  getCapabilityClusters: (limit = 15) => request<WorkforceSignal[]>(`/workforce/capability-clusters?limit=${limit}`),
  getCombinationClusters: (limit = 15) => request<WorkforceSignal[]>(`/workforce/combination-clusters?limit=${limit}`),
  getWormholes: (limit = 20) => request<OccupationTransition[]>(`/workforce/wormholes?limit=${limit}`),

  getAvailableYears: () => request<YearsResponse>("/workforce/years"),
  getWorkforceSnapshot: (year: number) => request<WorkforceSnapshot>(`/workforce/snapshot?year=${year}`),
  getTalentGaps: (limit = 12) => request<WorkforceSignal[]>(`/workforce/talent-gaps?limit=${limit}`),
  getWhy: (skillId: number, year?: number) =>
    request<WhyExplanation>(`/workforce/why/${skillId}${year ? `?year=${year}` : ""}`),

  getCareerRoutes: (fromId: number, toId: number, k = 3) =>
    request<CareerRoutesResponse>(`/routes?from=${fromId}&to=${toId}&k=${k}`),

  getTalentDna: (skills: { name: string; strength: number }[]) =>
    request<TalentDnaResponse>("/talent-dna", { method: "POST", body: JSON.stringify({ skills }) }),

  getLocations: (year: number) => request<LocationSummary[]>(`/geography/locations?year=${year}`),
  getLocationDetail: (id: number, year: number) => request<LocationDetail>(`/geography/${id}?year=${year}`),

  getEducationPrograms: () => request<EducationProgram[]>("/education"),
  getEducationGap: (id: number) => request<EducationGapAnalysis>(`/education/${id}/gap-analysis`),

  getSimulationPresets: () => request<SimulationPreset[]>("/simulation/presets"),
  runSimulation: (params: { tech_adoption: number; automation: number; skill_shortage: number; shock_skill_name?: string }) =>
    request<SimulationResult>("/simulation", { method: "POST", body: JSON.stringify(params) }),
  runSimulationPreset: (key: string) => request<SimulationResult>(`/simulation/preset/${key}`, { method: "POST" }),
};

