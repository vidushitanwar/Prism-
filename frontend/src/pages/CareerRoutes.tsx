import { useEffect, useState, type ReactNode } from "react";
import { useNavigate } from "react-router-dom";
import { AppNav } from "@/components/AppNav";
import { api } from "@/services/api";
import type { OccupationOut } from "@/types/graph";
import type { CareerRoutesResponse, OccupationTransition as WormholeType } from "@/types/graph";

type Tab = "planner" | "wormholes";

export default function CareerRoutes() {
  const [tab, setTab] = useState<Tab>("planner");

  return (
    <div className="min-h-screen">
      <AppNav />
      <div className="mx-auto max-w-4xl px-4 py-8">
        <p className="text-[10px] uppercase tracking-[0.3em] text-spectrum-cyan">Navigate</p>
        <h1 className="mt-1 font-display text-2xl text-prism-100">Career Routes &amp; Wormholes</h1>
        <p className="mt-2 max-w-2xl text-sm text-prism-400">
          Evidence-based possible transitions between occupations, derived from shared-skill overlap in the
          seeded dataset. Routes are shown as options to consider, never as guaranteed outcomes.
        </p>

        <div className="mt-6 flex gap-2">
          <TabButton active={tab === "planner"} onClick={() => setTab("planner")}>Route Planner</TabButton>
          <TabButton active={tab === "wormholes"} onClick={() => setTab("wormholes")}>Career Wormholes</TabButton>
        </div>

        <div className="mt-6">
          {tab === "planner" ? <RoutePlanner /> : <WormholeBrowser />}
        </div>
      </div>
    </div>
  );
}

function TabButton({ active, onClick, children }: { active: boolean; onClick: () => void; children: ReactNode }) {
  return (
    <button
      onClick={onClick}
      className={`rounded-full border px-4 py-1.5 text-xs transition-colors ${
        active ? "border-spectrum-violet/60 bg-spectrum-violet/10 text-spectrum-violet" : "border-prism-700/50 text-prism-400 hover:text-prism-100"
      }`}
    >
      {children}
    </button>
  );
}

function RoutePlanner() {
  const [occupations, setOccupations] = useState<OccupationOut[]>([]);
  const [fromId, setFromId] = useState<number | null>(null);
  const [toId, setToId] = useState<number | null>(null);
  const [result, setResult] = useState<CareerRoutesResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // list of occupations is small (≈55) — fine to load in full for two dropdowns.
    api.listOccupations().then(setOccupations).catch(() => setOccupations([]));
  }, []);

  async function findRoutes() {
    if (fromId === null || toId === null) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await api.getCareerRoutes(fromId, toId);
      setResult(res);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not find a route between these occupations.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <div className="flex flex-wrap items-end gap-4">
        <OccupationSelect label="Current" occupations={occupations} value={fromId} onChange={setFromId} />
        <div className="pb-2 text-prism-500">→</div>
        <OccupationSelect label="Target" occupations={occupations} value={toId} onChange={setToId} />
        <button
          onClick={findRoutes}
          disabled={fromId === null || toId === null || loading}
          className="btn-primary !px-5 !py-2 text-sm disabled:opacity-40"
        >
          {loading ? "Finding routes…" : "Find Routes"}
        </button>
      </div>

      {error && (
        <p className="mt-4 rounded-lg border border-spectrum-rose/40 bg-spectrum-rose/10 px-4 py-3 text-sm text-spectrum-rose">
          {error}
        </p>
      )}

      {result && (
        <div className="mt-6 space-y-6">
          <div className="grid grid-cols-2 gap-3">
            <div className="rounded-xl border border-prism-700/50 bg-prism-900/50 px-4 py-3">
              <p className="text-xs uppercase tracking-wide text-prism-500">Existing overlap</p>
              <p className="mt-1 text-sm text-prism-200">
                {result.existing_overlap.length > 0 ? result.existing_overlap.join(", ") : "None recorded"}
              </p>
            </div>
            <div className="rounded-xl border border-prism-700/50 bg-prism-900/50 px-4 py-3">
              <p className="text-xs uppercase tracking-wide text-prism-500">Missing capabilities</p>
              <p className="mt-1 text-sm text-prism-200">
                {result.missing_capabilities.length > 0 ? result.missing_capabilities.join(", ") : "None"}
              </p>
            </div>
          </div>

          {result.note && (
            <p className="rounded-lg border border-dashed border-prism-700/60 px-4 py-3 text-sm text-prism-400">
              {result.note}
            </p>
          )}

          {result.routes.map((route) => (
            <div key={route.label} className="rounded-2xl border border-spectrum-cyan/40 bg-spectrum-cyan/5 px-5 py-4">
              <div className="flex items-center justify-between">
                <h3 className="font-display text-lg text-prism-100">{route.label}</h3>
                <span className="text-xs text-prism-400">{route.total_evidence_count} supporting records</span>
              </div>
              <p className="mt-1 text-sm text-prism-300">{route.occupations.join(" → ")}</p>

              <div className="mt-3 space-y-2">
                {route.hops.map((hop, i) => (
                  <div key={i} className="rounded-lg border border-prism-700/50 bg-prism-950/50 px-3 py-2 text-xs">
                    <div className="flex justify-between text-prism-300">
                      <span>{hop.from_occupation} → {hop.to_occupation}</span>
                      <span>{Math.round(hop.overlap_score * 100)}% overlap</span>
                    </div>
                    {hop.shared_skills.length > 0 && (
                      <p className="mt-1 text-prism-500">Shared: {hop.shared_skills.join(", ")}</p>
                    )}
                  </div>
                ))}
              </div>

              {route.industry_context.length > 0 && (
                <p className="mt-3 text-xs text-prism-500">
                  Industry context: {route.industry_context.join(", ")}
                </p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function OccupationSelect({
  label, occupations, value, onChange,
}: { label: string; occupations: OccupationOut[]; value: number | null; onChange: (v: number) => void }) {
  return (
    <label className="flex flex-col gap-1 text-xs text-prism-400">
      {label}
      <select
        value={value ?? ""}
        onChange={(e) => onChange(Number(e.target.value))}
        className="min-w-[200px] rounded-lg border border-prism-600/50 bg-prism-900/70 px-3 py-2 text-sm text-prism-100 outline-none"
      >
        <option value="" disabled>Select occupation…</option>
        {occupations.map((o) => (
          <option key={o.id} value={o.id}>{o.title}</option>
        ))}
      </select>
    </label>
  );
}

function WormholeBrowser() {
  const [wormholes, setWormholes] = useState<WormholeType[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    api.getWormholes(25).then(setWormholes).catch(() => setWormholes([])).finally(() => setLoading(false));
  }, []);

  if (loading) return <p className="text-sm text-prism-400">Loading…</p>;
  if (wormholes.length === 0) {
    return (
      <p className="rounded-xl border border-dashed border-prism-700/60 px-4 py-6 text-center text-sm text-prism-500">
        No non-obvious transitions detected in the seeded dataset.
      </p>
    );
  }

  return (
    <div className="space-y-3">
      {wormholes.map((w, i) => (
        <div key={i} className="rounded-2xl border border-prism-700/50 bg-prism-900/50 px-5 py-4">
          <div className="flex flex-wrap items-baseline justify-between gap-2">
            <h3 className="font-display text-base text-prism-100">
              {w.source_occupation} <span className="text-prism-500">⇄</span> {w.target_occupation}
            </h3>
            <span className="text-xs text-spectrum-cyan">{Math.round(w.overlap_score * 100)}% skill overlap</span>
          </div>
          <p className="mt-1 text-xs text-prism-400">Shared: {w.shared_skills.join(", ")}</p>
          <p className="mt-1 text-[11px] text-prism-500">{w.evidence_count} supporting records in the seeded dataset</p>
        </div>
      ))}
      <button onClick={() => navigate("/explore")} className="btn-secondary mt-2 text-sm">
        Explore in Workforce Map
      </button>
    </div>
  );
}
