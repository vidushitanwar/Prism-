import { useEffect, useState } from "react";
import { AppNav } from "@/components/AppNav";
import { useTimeMachineStore } from "@/store/useTimeMachineStore";
import { api } from "@/services/api";
import type { LocationSummary, LocationDetail, EducationProgram, EducationGapAnalysis } from "@/types/graph";

type Tab = "geography" | "education";

export default function Insights() {
  const [tab, setTab] = useState<Tab>("geography");
  return (
    <div className="min-h-screen">
      <AppNav />
      <div className="mx-auto max-w-4xl px-4 py-8">
        <p className="text-[10px] uppercase tracking-[0.3em] text-spectrum-amber">Insights</p>
        <h1 className="mt-1 font-display text-2xl text-prism-100">Geographic & Education Intelligence</h1>

        <div className="mt-4 flex gap-2 border-b border-prism-700/50">
          {(["geography", "education"] as Tab[]).map((t) => (
            <button
              key={t}
              onClick={() => setTab(t)}
              className={`rounded-t-lg px-4 py-2 text-sm capitalize transition-colors ${
                tab === t ? "bg-prism-800/70 text-prism-100" : "text-prism-500 hover:text-prism-300"
              }`}
            >
              {t}
            </button>
          ))}
        </div>

        <div className="mt-6">
          {tab === "geography" ? <GeographyPanel /> : <EducationPanel />}
        </div>
      </div>
    </div>
  );
}

function GeographyPanel() {
  const currentYear = useTimeMachineStore((s) => s.currentYear);
  const [locations, setLocations] = useState<LocationSummary[]>([]);
  const [selected, setSelected] = useState<LocationDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    api
      .getLocations(currentYear)
      .then(setLocations)
      .catch(() => setError("Could not load geographic data. Is the backend running?"))
      .finally(() => setLoading(false));
    setSelected(null);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentYear]);

  async function selectLocation(id: number) {
    try {
      const detail = await api.getLocationDetail(id, currentYear);
      setSelected(detail);
    } catch {
      setError("Could not load details for this location.");
    }
  }

  if (loading) return <p className="text-sm text-prism-400">Loading geographic data…</p>;
  if (error) return <p className="text-sm text-spectrum-rose">{error}</p>;

  return (
    <div className="grid gap-4 sm:grid-cols-2">
      <div className="space-y-2">
        <p className="mb-1 text-xs uppercase tracking-wide text-prism-500">Locations by total postings ({currentYear})</p>
        {locations.map((loc) => (
          <button
            key={loc.location_id}
            onClick={() => selectLocation(loc.location_id)}
            className="flex w-full items-center justify-between rounded-xl border border-prism-700/50 bg-prism-900/50 px-4 py-2.5 text-left hover:border-spectrum-cyan/50"
          >
            <span className="text-sm text-prism-100">{loc.city}, {loc.country}</span>
            <span className="text-xs text-prism-400">{loc.total_postings.toLocaleString()} postings</span>
          </button>
        ))}
      </div>

      <div className="rounded-xl border border-prism-700/50 bg-prism-900/40 p-4">
        {!selected && <p className="text-sm text-prism-500">Select a location to see its workforce profile.</p>}
        {selected && (
          <div className="space-y-4">
            <h3 className="font-display text-lg text-prism-100">{selected.location.city}, {selected.location.country}</h3>
            {selected.avg_salary_usd && (
              <p className="text-xs text-prism-400">Avg. synthetic compensation: ${selected.avg_salary_usd.toLocaleString()}</p>
            )}
            <MiniList title="Top Skills" items={selected.top_skills.map((s) => s.name)} />
            <MiniList title="Top Occupations" items={selected.top_occupations.map((s) => s.name)} />
            <MiniList title="Top Industries" items={selected.top_industries.map((s) => s.name)} />
            {selected.emerging_skills_here.length > 0 && (
              <div>
                <p className="mb-1 text-xs uppercase tracking-wide text-spectrum-violet">Emerging here</p>
                <div className="flex flex-wrap gap-1.5">
                  {selected.emerging_skills_here.map((e) => (
                    <span key={e.skill} className="rounded-full border border-spectrum-violet/40 px-2.5 py-1 text-[11px] text-prism-200">
                      {e.skill} ▲{e.growth_rate.toFixed(0)}%
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

function EducationPanel() {
  const [programs, setPrograms] = useState<EducationProgram[]>([]);
  const [selected, setSelected] = useState<EducationGapAnalysis | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .getEducationPrograms()
      .then(setPrograms)
      .catch(() => setError("Could not load education programs. Is the backend running?"))
      .finally(() => setLoading(false));
  }, []);

  async function selectProgram(id: number) {
    try {
      const detail = await api.getEducationGap(id);
      setSelected(detail);
    } catch {
      setError("Could not load the gap analysis for this program.");
    }
  }

  if (loading) return <p className="text-sm text-prism-400">Loading education programs…</p>;
  if (error) return <p className="text-sm text-spectrum-rose">{error}</p>;

  return (
    <div className="grid gap-4 sm:grid-cols-2">
      <div className="space-y-2">
        <p className="mb-1 text-xs uppercase tracking-wide text-prism-500">Generic program archetypes</p>
        {programs.map((p) => (
          <button
            key={p.id}
            onClick={() => selectProgram(p.id)}
            className="flex w-full items-center justify-between rounded-xl border border-prism-700/50 bg-prism-900/50 px-4 py-2.5 text-left hover:border-spectrum-amber/50"
          >
            <span className="text-sm text-prism-100">{p.name}</span>
            <span className="text-xs text-prism-400">{p.high_demand_coverage} covered</span>
          </button>
        ))}
      </div>

      <div className="rounded-xl border border-prism-700/50 bg-prism-900/40 p-4">
        {!selected && <p className="text-sm text-prism-500">Select a program to see its demand-gap analysis.</p>}
        {selected && (
          <div className="space-y-4">
            <h3 className="font-display text-lg text-prism-100">{selected.program}</h3>
            <p className="text-xs text-prism-500">{selected.note}</p>
            <div>
              <p className="mb-1 text-xs uppercase tracking-wide text-spectrum-emerald">Covered ✓</p>
              <MiniList title="" items={selected.covered_high_demand_skills.map((s) => s.skill)} />
            </div>
            <div>
              <p className="mb-1 text-xs uppercase tracking-wide text-spectrum-rose">Gap ✗</p>
              <MiniList title="" items={selected.gap_high_demand_skills.map((s) => s.skill)} />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function MiniList({ title, items }: { title: string; items: string[] }) {
  if (items.length === 0) return null;
  return (
    <div>
      {title && <p className="mb-1 text-xs uppercase tracking-wide text-prism-500">{title}</p>}
      <div className="flex flex-wrap gap-1.5">
        {items.map((i) => (
          <span key={i} className="rounded-full border border-prism-700/60 px-2.5 py-1 text-[11px] text-prism-300">
            {i}
          </span>
        ))}
      </div>
    </div>
  );
}
