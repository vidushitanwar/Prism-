import { useEffect, useState, type ReactNode } from "react";
import { AppNav } from "@/components/AppNav";
import { api } from "@/services/api";
import type { SimulationResult, SimulationPreset } from "@/types/graph";

export default function Simulator() {
  const [techAdoption, setTechAdoption] = useState(20);
  const [automation, setAutomation] = useState(10);
  const [skillShortage, setSkillShortage] = useState(10);
  const [presets, setPresets] = useState<SimulationPreset[]>([]);
  const [result, setResult] = useState<SimulationResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [stressMode, setStressMode] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.getSimulationPresets().then(setPresets).catch(() => setPresets([]));
  }, []);

  async function runCustom() {
    setLoading(true);
    setStressMode(false);
    setError(null);
    try {
      const res = await api.runSimulation({
        tech_adoption: techAdoption, automation, skill_shortage: skillShortage,
      });
      setResult(res);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Simulation failed. Is the backend running?");
    } finally {
      setLoading(false);
    }
  }

  async function runPreset(key: string) {
    setLoading(true);
    setStressMode(true);
    setError(null);
    try {
      const res = await api.runSimulationPreset(key);
      setResult(res);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Simulation failed. Is the backend running?");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen">
      <AppNav />
      <div className="mx-auto max-w-4xl px-4 py-8">
        <p className="text-[10px] uppercase tracking-[0.3em] text-spectrum-amber">Workforce Simulation</p>
        <h1 className="mt-1 font-display text-2xl text-prism-100">Workforce Shock Simulator</h1>
        <p className="mt-2 text-sm text-prism-400">
          Adjust scenario dials and see how the workforce graph responds. This is a
          transparent, deterministic scenario simulation — not a guaranteed forecast.
          Identical inputs always produce identical outputs.
        </p>

        <div className="mt-6 space-y-4 rounded-2xl border border-prism-700/50 bg-prism-900/50 p-5">
          <Dial label="Technology Adoption" value={techAdoption} onChange={setTechAdoption} color="violet" />
          <Dial label="Automation" value={automation} onChange={setAutomation} color="cyan" />
          <Dial label="Skill Shortage" value={skillShortage} onChange={setSkillShortage} color="amber" />
          <button onClick={runCustom} disabled={loading} className="btn-primary w-full disabled:opacity-50">
            {loading && !stressMode ? "Simulating…" : "Run Simulation"}
          </button>
        </div>

        <div className="mt-6">
          <p className="mb-2 text-xs uppercase tracking-wide text-prism-500">🚀 Stress Test Workforce</p>
          <div className="flex flex-wrap gap-2">
            {presets.map((p) => (
              <button
                key={p.key}
                onClick={() => runPreset(p.key)}
                disabled={loading}
                className="rounded-xl border border-spectrum-rose/40 bg-spectrum-rose/10 px-4 py-2.5 text-left text-sm text-prism-100 transition-transform hover:-translate-y-0.5 disabled:opacity-50"
              >
                <span className="block font-medium">{p.label}</span>
                <span className="block text-xs text-prism-400">{p.description}</span>
              </button>
            ))}
          </div>
        </div>

        {error && (
          <p className="mt-4 rounded-lg border border-spectrum-rose/40 bg-spectrum-rose/10 px-4 py-3 text-sm text-spectrum-rose">
            {error}
          </p>
        )}

        {result && <SimulationResults result={result} />}
      </div>
    </div>
  );
}

function Dial({
  label, value, onChange, color,
}: { label: string; value: number; onChange: (v: number) => void; color: "violet" | "cyan" | "amber" }) {
  const accent = { violet: "accent-spectrum-violet", cyan: "accent-spectrum-cyan", amber: "accent-spectrum-amber" }[color];
  return (
    <div>
      <div className="flex items-center justify-between text-sm">
        <span className="text-prism-200">{label}</span>
        <span className="text-prism-400">{value}%</span>
      </div>
      <input
        type="range" min={0} max={100} value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className={`mt-1 w-full ${accent}`}
      />
    </div>
  );
}

function SimulationResults({ result }: { result: SimulationResult }) {
  return (
    <div className="mt-8 space-y-6">
      {result.preset && (
        <div className="rounded-xl border border-spectrum-rose/40 bg-spectrum-rose/10 px-4 py-3">
          <p className="font-display text-sm text-prism-100">{result.preset.label}</p>
          <p className="text-xs text-prism-400">{result.preset.description}</p>
        </div>
      )}

      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        <Stat label="Skills affected" value={result.summary.skills_affected} />
        <Stat label="Avg delta" value={`${result.summary.avg_delta >= 0 ? "+" : ""}${result.summary.avg_delta}`} />
        <Stat label="Max gain" value={`+${result.summary.max_positive_delta}`} accent="emerald" />
        <Stat label="Max loss" value={`${result.summary.max_negative_delta}`} accent="rose" />
      </div>

      <Section title="First Affected Capabilities" subtitle="Largest immediate demand-index moves">
        <SkillDeltaList items={result.first_affected_capabilities} />
      </Section>

      <Section title="Bottleneck Capabilities" subtitle="High new demand, low existing supply (below-median postings)">
        <SkillDeltaList items={result.bottleneck_capabilities} />
      </Section>

      <div className="grid gap-4 sm:grid-cols-2">
        <Section title="Occupations Under Pressure" subtitle="">
          {result.occupations_under_pressure.length === 0 && <EmptyNote />}
          {result.occupations_under_pressure.map((o) => (
            <DeltaRow key={o.occupation} label={o.occupation} value={o.avg_delta} />
          ))}
        </Section>
        <Section title="Occupations In Demand" subtitle="">
          {result.occupations_in_demand.length === 0 && <EmptyNote />}
          {result.occupations_in_demand.map((o) => (
            <DeltaRow key={o.occupation} label={o.occupation} value={o.avg_delta} />
          ))}
        </Section>
      </div>

      <Section title="Industries Affected" subtitle="">
        {result.industries_affected.map((i) => (
          <DeltaRow key={i.industry} label={i.industry} value={i.avg_delta} />
        ))}
      </Section>

      <Section title="Workforce Mirror" subtitle="Current vs. scenario average demand, by skill category">
        <div className="space-y-2">
          {result.workforce_mirror.map((m) => (
            <div key={m.category} className="flex items-center gap-3 text-xs">
              <span className="w-40 shrink-0 text-prism-300">{m.category}</span>
              <MirrorBar current={m.current_avg_demand} scenario={m.scenario_avg_demand} />
            </div>
          ))}
        </div>
      </Section>

      <p className="rounded-lg border border-dashed border-prism-700/60 px-3 py-3 text-xs text-prism-500">
        {result.disclaimer}
      </p>
    </div>
  );
}

function Stat({ label, value, accent }: { label: string; value: string | number; accent?: "emerald" | "rose" }) {
  const color = accent === "emerald" ? "text-spectrum-emerald" : accent === "rose" ? "text-spectrum-rose" : "text-prism-100";
  return (
    <div className="rounded-xl border border-prism-700/50 bg-prism-900/50 px-3 py-2.5 text-center">
      <p className={`font-display text-lg ${color}`}>{value}</p>
      <p className="text-[10px] uppercase tracking-wide text-prism-500">{label}</p>
    </div>
  );
}

function Section({ title, subtitle, children }: { title: string; subtitle: string; children: ReactNode }) {
  return (
    <section>
      <h2 className="font-display text-lg text-prism-100">{title}</h2>
      {subtitle && <p className="mb-2 text-xs text-prism-500">{subtitle}</p>}
      <div className="mt-2 space-y-2">{children}</div>
    </section>
  );
}

function SkillDeltaList({ items }: { items: { name: string; category: string; delta: number; scenario_demand: number }[] }) {
  if (items.length === 0) return <EmptyNote />;
  return (
    <>
      {items.map((s) => (
        <DeltaRow key={s.name} label={`${s.name} (${s.category})`} value={s.delta} />
      ))}
    </>
  );
}

function DeltaRow({ label, value }: { label: string; value: number }) {
  const positive = value >= 0;
  return (
    <div className="flex items-center justify-between rounded-lg border border-prism-700/50 bg-prism-900/40 px-3 py-2 text-sm">
      <span className="text-prism-200">{label}</span>
      <span className={positive ? "text-spectrum-emerald" : "text-spectrum-rose"}>
        {positive ? "+" : ""}{value.toFixed(1)}
      </span>
    </div>
  );
}

function MirrorBar({ current, scenario }: { current: number; scenario: number }) {
  return (
    <div className="relative flex-1">
      <div className="h-2 w-full overflow-hidden rounded-full bg-prism-800">
        <div className="h-full rounded-full bg-prism-500" style={{ width: `${current}%` }} />
      </div>
      <div className="mt-1 h-2 w-full overflow-hidden rounded-full bg-prism-800">
        <div
          className={`h-full rounded-full ${scenario >= current ? "bg-spectrum-emerald" : "bg-spectrum-rose"}`}
          style={{ width: `${scenario}%` }}
        />
      </div>
    </div>
  );
}

function EmptyNote() {
  return <p className="text-xs text-prism-500">No significant effect under this scenario.</p>;
}
