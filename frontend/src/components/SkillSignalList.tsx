import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "@/services/api";
import { useGraphStore } from "@/store/useGraphStore";
import { useTimeMachineStore } from "@/store/useTimeMachineStore";
import type { WorkforceSignal, SkillDetail } from "@/types/graph";

interface EnrichedSignal extends WorkforceSignal {
  detail?: SkillDetail;
}

export function SkillSignalList({
  title,
  subtitle,
  accentColor,
  fetcher,
  emptyLabel,
}: {
  title: string;
  subtitle: string;
  accentColor: "violet" | "rose";
  fetcher: (year: number) => Promise<WorkforceSignal[]>;
  emptyLabel: string;
}) {
  const navigate = useNavigate();
  const focusNode = useGraphStore((s) => s.focusNode);
  const { years, currentYear, setYear } = useTimeMachineStore();
  const [signals, setSignals] = useState<EnrichedSignal[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    (async () => {
      try {
        const base = await fetcher(currentYear);
        const enriched = await Promise.all(
          base.map(async (s) => {
            try {
              const detail = await api.getSkill(s.subject_id);
              return { ...s, detail };
            } catch {
              return s;
            }
          })
        );
        if (!cancelled) setSignals(enriched);
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentYear]);

  function explore(subjectId: number) {
    navigate("/explore");
    focusNode(`skill:${subjectId}`);
  }

  const accent =
    accentColor === "violet"
      ? { text: "text-spectrum-violet", border: "border-spectrum-violet/40", bg: "bg-spectrum-violet/10" }
      : { text: "text-spectrum-rose", border: "border-spectrum-rose/40", bg: "bg-spectrum-rose/10" };

  return (
    <div className="mx-auto max-w-4xl px-4 py-8">
      <div className="mb-6 flex flex-wrap items-center justify-between gap-4">
        <div>
          <p className={`text-[10px] uppercase tracking-[0.3em] ${accent.text}`}>{subtitle}</p>
          <h1 className="mt-1 font-display text-2xl text-prism-100">{title}</h1>
        </div>
        <label className="flex items-center gap-2 text-xs text-prism-400">
          Year
          <select
            value={currentYear}
            onChange={(e) => setYear(Number(e.target.value))}
            className="rounded-lg border border-prism-600/50 bg-prism-900/70 px-2 py-1 text-xs text-prism-100 outline-none"
          >
            {years.map((y) => (
              <option key={y} value={y}>{y}</option>
            ))}
          </select>
        </label>
      </div>

      {loading && <p className="text-sm text-prism-400">Loading signals…</p>}
      {!loading && signals.length === 0 && (
        <p className="rounded-xl border border-dashed border-prism-700/60 px-4 py-6 text-center text-sm text-prism-500">
          {emptyLabel}
        </p>
      )}

      <div className="space-y-3">
        {signals.map((s) => (
          <button
            key={s.id}
            onClick={() => explore(s.subject_id)}
            className={`w-full rounded-2xl border ${accent.border} ${accent.bg} px-5 py-4 text-left transition-transform hover:-translate-y-0.5`}
          >
            <div className="flex flex-wrap items-baseline justify-between gap-2">
              <h3 className="font-display text-lg text-prism-100">{s.title}</h3>
              <span className={`text-sm font-semibold ${accent.text}`}>
                {(s.magnitude ?? 0) >= 0 ? "▲" : "▼"} {Math.abs(s.magnitude ?? 0).toFixed(1)}% YoY
              </span>
            </div>
            <p className="mt-1 text-sm text-prism-300">{s.description}</p>

            <div className="mt-3 flex flex-wrap gap-4 text-xs text-prism-400">
              <span>Confidence: <span className="text-prism-200">{Math.round(s.confidence * 100)}%</span></span>
              {s.year && <span>Year: <span className="text-prism-200">{s.year}</span></span>}
            </div>

            {s.detail && (
              <div className="mt-3 flex flex-wrap gap-4">
                <MiniTagGroup label="Occupations" items={s.detail.occupations} />
                <MiniTagGroup label="Industries" items={s.detail.industries} />
              </div>
            )}

            <p className="mt-3 text-[11px] text-prism-500">Click to open in the Workforce Map →</p>
          </button>
        ))}
      </div>
    </div>
  );
}

function MiniTagGroup({ label, items }: { label: string; items: string[] }) {
  if (items.length === 0) return null;
  return (
    <div>
      <p className="mb-1 text-[10px] uppercase tracking-wide text-prism-500">{label}</p>
      <div className="flex flex-wrap gap-1">
        {items.slice(0, 4).map((i) => (
          <span key={i} className="rounded-full border border-prism-700/60 px-2 py-0.5 text-[11px] text-prism-300">
            {i}
          </span>
        ))}
        {items.length > 4 && <span className="text-[11px] text-prism-500">+{items.length - 4} more</span>}
      </div>
    </div>
  );
}
