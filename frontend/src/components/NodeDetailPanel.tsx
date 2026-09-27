import { useEffect, useState } from "react";
import { useGraphStore } from "@/store/useGraphStore";
import { useTimeMachineStore } from "@/store/useTimeMachineStore";
import { api } from "@/services/api";
import type {
  SkillDetail,
  OccupationDetail,
  IndustryDetail,
  EvolutionPoint,
  GraphNode,
  GraphEdge,
} from "@/types/graph";

type Tab = "overview" | "timeline" | "related" | "evidence";

const LIFECYCLE_COLOR: Record<string, string> = {
  Emerging: "text-spectrum-violet",
  Growing: "text-spectrum-cyan",
  Established: "text-spectrum-emerald",
  Transforming: "text-spectrum-amber",
  Declining: "text-spectrum-rose",
  Ghost: "text-prism-500",
};

export function NodeDetailPanel() {
  const selectedNodeId = useGraphStore((s) => s.selectedNodeId);
  const graphNodes = useGraphStore((s) => s.nodes);
  const graphEdges = useGraphStore((s) => s.edges);
  const selectNode = useGraphStore((s) => s.selectNode);
  const currentYear = useTimeMachineStore((s) => s.currentYear);
  const [tab, setTab] = useState<Tab>("overview");
  const [skill, setSkill] = useState<SkillDetail | null>(null);
  const [occupation, setOccupation] = useState<OccupationDetail | null>(null);
  const [industry, setIndustry] = useState<IndustryDetail | null>(null);
  const [occupationEvolution, setOccupationEvolution] = useState<EvolutionPoint[]>([]);
  const [industryEvolution, setIndustryEvolution] = useState<EvolutionPoint[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setSkill(null);
    setOccupation(null);
    setIndustry(null);
    setOccupationEvolution([]);
    setIndustryEvolution([]);
    setTab("overview");
    if (!selectedNodeId) return;

    const [type, idStr] = selectedNodeId.split(":");
    const id = Number(idStr);
    setLoading(true);

    (async () => {
      try {
        if (type === "skill") setSkill(await api.getSkill(id));
        else if (type === "occupation") {
          const [details, evolution] = await Promise.all([
            api.getOccupation(id),
            api.getOccupationEvolution(id),
          ]);
          setOccupation(details);
          setOccupationEvolution(evolution.evolution);
        } else if (type === "industry") {
          const [details, evolution] = await Promise.all([
            api.getIndustry(id),
            api.getIndustryEvolution(id),
          ]);
          setIndustry(details);
          setIndustryEvolution(evolution.evolution);
        }
      } finally {
        setLoading(false);
      }
    })();
  }, [selectedNodeId]);

  if (!selectedNodeId) return null;

  const title = skill?.name ?? occupation?.title ?? industry?.name ?? "";
  const kind = skill ? "Skill" : occupation ? "Occupation" : industry ? "Industry" : "";
  const relatedEntities = getRelatedEntities(selectedNodeId, graphNodes, graphEdges);

  return (
    <aside className="absolute right-0 top-0 z-20 h-full w-full max-w-sm overflow-y-auto border-l border-prism-600/40 bg-prism-950/95 backdrop-blur-xl shadow-2xl sm:w-96">
      <div className="flex items-start justify-between border-b border-prism-700/50 px-5 py-4">
        <div>
          <p className="text-[10px] uppercase tracking-[0.25em] text-spectrum-cyan">{kind}</p>
          <h2 className="mt-1 font-display text-xl text-prism-100">{title || "Loading…"}</h2>
        </div>
        <button
          onClick={() => selectNode(null)}
          className="rounded-full border border-prism-700/50 p-1.5 text-prism-400 hover:text-prism-100"
          aria-label="Close panel"
        >
          ✕
        </button>
      </div>

      <div className="flex gap-1 border-b border-prism-700/50 px-3 pt-2 text-xs">
        {(["overview", "timeline", "related", "evidence"] as Tab[]).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`rounded-t-lg px-3 py-2 capitalize transition-colors ${
              tab === t ? "bg-prism-800/70 text-prism-100" : "text-prism-500 hover:text-prism-300"
            }`}
          >
            {t}
          </button>
        ))}
      </div>

      <div className="px-5 py-4">
        {loading && <p className="text-sm text-prism-400">Loading details…</p>}

        {!loading && tab === "overview" && (
          <div className="space-y-4 text-sm text-prism-300">
            {skill && (
              <>
                <p>Category: <span className="text-prism-100">{skill.category}</span></p>
                <div>
                  <p className="mb-1 text-xs uppercase tracking-wide text-prism-500">Occupations</p>
                  <TagList items={skill.occupations} />
                </div>
                <div>
                  <p className="mb-1 text-xs uppercase tracking-wide text-prism-500">Industries</p>
                  <TagList items={skill.industries} />
                </div>
              </>
            )}
            {occupation && (
              <div>
                <p className="mb-1 text-xs uppercase tracking-wide text-prism-500">Core skills</p>
                <ul className="space-y-1.5">
                  {occupation.core_skills.map((s) => (
                    <li key={s.id} className="flex items-center justify-between">
                      <span className="text-prism-100">{s.name}</span>
                      <WeightBar weight={s.weight} />
                    </li>
                  ))}
                </ul>
              </div>
            )}
            {industry && (
              <div>
                <p className="mb-1 text-xs uppercase tracking-wide text-prism-500">Top skills</p>
                <ul className="space-y-1.5">
                  {industry.top_skills.map((s) => (
                    <li key={s.id} className="flex items-center justify-between">
                      <span className="text-prism-100">{s.name}</span>
                      <WeightBar weight={s.weight} />
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

        {!loading && tab === "timeline" && (
          <div>
            {skill ? (
              <div className="space-y-2">
                <SkillEvolutionSummary skill={skill} />
                {skill.timeline.map((t) => (
                  <div
                    key={t.year}
                    className={`rounded-lg border px-3 py-2 transition-colors ${
                      t.year === currentYear
                        ? "border-spectrum-violet/60 bg-spectrum-violet/10"
                        : "border-prism-700/50 bg-prism-900/50"
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-prism-100">
                        {t.year}
                        {t.year === currentYear && (
                          <span className="ml-2 text-[10px] uppercase tracking-wide text-spectrum-violet">
                            Time Machine
                          </span>
                        )}
                      </span>
                      <span className={`text-xs font-medium ${LIFECYCLE_COLOR[t.lifecycle_stage] ?? "text-prism-300"}`}>
                        {t.lifecycle_stage}
                      </span>
                    </div>
                    <div className="mt-1.5 h-1.5 w-full overflow-hidden rounded-full bg-prism-800">
                      <div
                        className="h-full rounded-full bg-gradient-to-r from-spectrum-violet to-spectrum-cyan"
                        style={{ width: `${Math.min(100, t.demand_score)}%` }}
                      />
                    </div>
                    <div className="mt-1 flex justify-between text-[11px] text-prism-500">
                      <span>Demand index: {t.demand_score.toFixed(1)}</span>
                      <span>{t.growth_rate >= 0 ? "▲" : "▼"} {Math.abs(t.growth_rate).toFixed(1)}% YoY</span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <EntityEvolutionTimeline
                points={occupation ? occupationEvolution : industryEvolution}
                currentYear={currentYear}
              />
            )}
          </div>
        )}

        {!loading && tab === "related" && (
          <div className="space-y-4">
            {skill && (
              <div>
                <p className="mb-1 text-xs uppercase tracking-wide text-prism-500">Related skills</p>
                <TagList items={skill.related_skills} />
              </div>
            )}
            {!skill && (
              <div>
                <p className="mb-1 text-xs uppercase tracking-wide text-prism-500">
                  Related {kind.toLowerCase()}s by shared skills
                </p>
                {relatedEntities.length > 0 ? (
                  <TagList items={relatedEntities} />
                ) : (
                  <ComingSoonNote text="No related entities are present in the current graph view." />
                )}
              </div>
            )}
          </div>
        )}

        {!loading && tab === "evidence" && (
          <EvidenceView skill={skill} occupation={occupation} industry={industry} />
        )}
      </div>
    </aside>
  );
}

function SkillEvolutionSummary({ skill }: { skill: SkillDetail }) {
  const timeline = skill.timeline;
  if (timeline.length === 0) return null;

  const first = timeline[0];
  const latest = timeline[timeline.length - 1];
  const overallChangePct =
    first.demand_score > 0 ? ((latest.demand_score - first.demand_score) / first.demand_score) * 100 : 0;

  // "First significant appearance" = first year the skill's demand index
  // crossed a modest visibility threshold, computed from the data rather
  // than hardcoded per skill.
  const firstSignificant = timeline.find((t) => t.demand_score >= 20) ?? latest;

  return (
    <div className="mb-3 grid grid-cols-2 gap-2">
      <div className="rounded-lg border border-prism-700/50 bg-prism-900/60 px-3 py-2">
        <p className="text-[10px] uppercase tracking-wide text-prism-500">
          {first.year}–{latest.year} change
        </p>
        <p className={`mt-0.5 text-sm font-semibold ${overallChangePct >= 0 ? "text-spectrum-emerald" : "text-spectrum-rose"}`}>
          {overallChangePct >= 0 ? "+" : ""}
          {overallChangePct.toFixed(0)}%
        </p>
      </div>
      <div className="rounded-lg border border-prism-700/50 bg-prism-900/60 px-3 py-2">
        <p className="text-[10px] uppercase tracking-wide text-prism-500">First significant year</p>
        <p className="mt-0.5 text-sm font-semibold text-prism-100">{firstSignificant.year}</p>
      </div>
    </div>
  );
}

function EntityEvolutionTimeline({
  points,
  currentYear,
}: {
  points: EvolutionPoint[];
  currentYear: number;
}) {
  if (points.length === 0) {
    return <p className="rounded-lg border border-dashed border-prism-700/60 px-3 py-3 text-xs text-prism-500">No timeline records are available for this node.</p>;
  }

  const first = points[0].avg_demand_score;
  const latest = points[points.length - 1].avg_demand_score;
  const change = first > 0 ? ((latest - first) / first) * 100 : 0;

  return (
    <div className="space-y-2">
      <div className="mb-3 grid grid-cols-2 gap-2">
        <div className="rounded-lg border border-prism-700/50 bg-prism-900/60 px-3 py-2">
          <p className="text-[10px] uppercase tracking-wide text-prism-500">Average demand change</p>
          <p className={`mt-0.5 text-sm font-semibold ${change >= 0 ? "text-spectrum-emerald" : "text-spectrum-rose"}`}>
            {change >= 0 ? "+" : ""}{change.toFixed(0)}%
          </p>
        </div>
        <div className="rounded-lg border border-prism-700/50 bg-prism-900/60 px-3 py-2">
          <p className="text-[10px] uppercase tracking-wide text-prism-500">Years observed</p>
          <p className="mt-0.5 text-sm font-semibold text-prism-100">{points.length}</p>
        </div>
      </div>
      {points.map((point) => (
        <div
          key={point.year}
          className={`rounded-lg border px-3 py-2 ${
            point.year === currentYear
              ? "border-spectrum-violet/60 bg-spectrum-violet/10"
              : "border-prism-700/50 bg-prism-900/50"
          }`}
        >
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-prism-100">
              {point.year}
              {point.year === currentYear && <span className="ml-2 text-[10px] uppercase tracking-wide text-spectrum-violet">Time Machine</span>}
            </span>
            <span className="text-xs text-prism-300">{point.avg_demand_score.toFixed(1)} demand</span>
          </div>
          <div className="mt-1.5 h-1.5 w-full overflow-hidden rounded-full bg-prism-800">
            <div className="h-full rounded-full bg-gradient-to-r from-spectrum-violet to-spectrum-cyan" style={{ width: `${Math.min(100, point.avg_demand_score)}%` }} />
          </div>
        </div>
      ))}
    </div>
  );
}

function TagList({ items }: { items: string[] }) {
  if (items.length === 0) return <p className="text-xs text-prism-500">None recorded.</p>;
  return (
    <div className="flex flex-wrap gap-1.5">
      {items.map((i) => (
        <span key={i} className="rounded-full border border-prism-700/60 px-2.5 py-1 text-xs text-prism-200">
          {i}
        </span>
      ))}
    </div>
  );
}

function getRelatedEntities(nodeId: string, nodes: GraphNode[], edges: GraphEdge[]) {
  const [type] = nodeId.split(":");
  if (type !== "occupation" && type !== "industry") return [];

  const connectedSkills = new Set(
    edges
      .filter((edge) => edge.source === nodeId || edge.target === nodeId)
      .map((edge) => (edge.source.startsWith("skill:") ? edge.source : edge.target))
      .filter((id) => id.startsWith("skill:"))
  );
  if (connectedSkills.size === 0) return [];

  return nodes
    .filter((node) => node.type === type && node.id !== nodeId)
    .map((node) => {
      const sharedSkills = new Set(
        edges
          .filter((edge) => edge.source === node.id || edge.target === node.id)
          .map((edge) => (edge.source.startsWith("skill:") ? edge.source : edge.target))
          .filter((id) => id.startsWith("skill:"))
      );
      const overlap = [...connectedSkills].filter((skillId) => sharedSkills.has(skillId)).length;
      return { label: node.label, overlap };
    })
    .filter((node) => node.overlap > 0)
    .sort((first, second) => second.overlap - first.overlap || first.label.localeCompare(second.label))
    .slice(0, 12)
    .map((node) => node.label);
}

function WeightBar({ weight }: { weight: number }) {
  return (
    <div className="h-1.5 w-16 overflow-hidden rounded-full bg-prism-800">
      <div className="h-full rounded-full bg-spectrum-cyan" style={{ width: `${weight * 100}%` }} />
    </div>
  );
}

function EvidenceView({
  skill,
  occupation,
  industry,
}: {
  skill: SkillDetail | null;
  occupation: OccupationDetail | null;
  industry: IndustryDetail | null;
}) {
  const isSkill = Boolean(skill);
  const timeRange = skill?.timeline.length
    ? `${skill.timeline[0].year}–${skill.timeline[skill.timeline.length - 1].year}`
    : "Current seeded catalog";
  const supportingRecords = skill
    ? skill.timeline.length
    : occupation?.core_skills.length ?? industry?.top_skills.length ?? 0;
  const method = isSkill
    ? "Demand and lifecycle metrics calculated from the seeded workforce timeline."
    : "Relationships ranked from the seeded skill catalog and graph relationships.";

  return (
    <div className="space-y-3 text-sm">
      <div className="rounded-lg border border-spectrum-cyan/30 bg-spectrum-cyan/5 px-3 py-3">
        <p className="text-[10px] uppercase tracking-[0.2em] text-spectrum-cyan">Evidence mode</p>
        <p className="mt-1 text-xs leading-relaxed text-prism-300">
          This view explains which seeded records support the information shown for this node.
        </p>
      </div>
      <EvidenceRow label="Data source" value="PRISM seeded synthetic workforce dataset" />
      <EvidenceRow label="Time range" value={timeRange} />
      <EvidenceRow label="Method" value={method} />
      <EvidenceRow label="Supporting records" value={String(supportingRecords)} />
      <p className="border-t border-prism-800/70 pt-3 text-[11px] italic leading-relaxed text-prism-500">
        This is a transparent, internally consistent demo dataset. It is not a claim about real-world labor-market outcomes.
      </p>
    </div>
  );
}

function EvidenceRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="space-y-1 rounded-lg border border-prism-700/50 bg-prism-900/50 px-3 py-2">
      <p className="text-[10px] uppercase tracking-wide text-prism-500">{label}</p>
      <p className="text-xs leading-relaxed text-prism-100">{value}</p>
    </div>
  );
}

function ComingSoonNote({ text }: { text: string }) {
  return <p className="rounded-lg border border-dashed border-prism-700/60 px-3 py-3 text-xs text-prism-500">{text}</p>;
}
