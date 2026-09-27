import { useEffect, useState } from "react";
import { api } from "@/services/api";
import type { WhyExplanation } from "@/types/graph";

const BAR_COLORS = ["#8b5cf6", "#22d3ee", "#f59e0b", "#4750a3"];

export function WhyModal({ skillId, year, onClose }: { skillId: number; year: number; onClose: () => void }) {
  const [data, setData] = useState<WhyExplanation | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    api
      .getWhy(skillId, year)
      .then((res) => !cancelled && setData(res))
      .catch(() => !cancelled && setError("Could not load the explanation for this skill."))
      .finally(() => !cancelled && setLoading(false));
    return () => {
      cancelled = true;
    };
  }, [skillId, year]);

  const maxContribution = data ? Math.max(...data.signals.map((s) => s.contribution_pct_points), 1) : 1;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 px-4" onClick={onClose}>
      <div
        className="w-full max-w-md overflow-hidden rounded-2xl border border-prism-600/50 bg-prism-900/95 shadow-2xl backdrop-blur-xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between border-b border-prism-700/50 px-5 py-4">
          <div>
            <p className="text-[10px] uppercase tracking-[0.25em] text-spectrum-amber">Why did this change?</p>
            <h3 className="mt-1 font-display text-lg text-prism-100">{data?.skill ?? "Loading…"}</h3>
          </div>
          <button onClick={onClose} className="rounded-full border border-prism-700/50 p-1.5 text-prism-400 hover:text-prism-100">✕</button>
        </div>

        <div className="px-5 py-4">
          {loading && <p className="text-sm text-prism-400">Computing contributing signals…</p>}
          {!loading && error && <p className="text-sm text-spectrum-rose">{error}</p>}
          {!loading && data && (
            <>
              <p className="mb-4 text-sm text-prism-300">
                Observed {data.year} year-over-year growth:{" "}
                <span className={data.observed_growth_rate >= 0 ? "text-spectrum-emerald" : "text-spectrum-rose"}>
                  {data.observed_growth_rate >= 0 ? "+" : ""}
                  {data.observed_growth_rate.toFixed(1)}%
                </span>
              </p>

              <div className="space-y-3">
                {data.signals.map((s, i) => (
                  <div key={s.label}>
                    <div className="mb-1 flex justify-between text-xs text-prism-300">
                      <span>{s.label}</span>
                      <span>{s.contribution_pct_points.toFixed(1)} pts</span>
                    </div>
                    <div className="h-2 w-full overflow-hidden rounded-full bg-prism-800">
                      <div
                        className="h-full rounded-full"
                        style={{
                          width: `${(s.contribution_pct_points / maxContribution) * 100}%`,
                          backgroundColor: BAR_COLORS[i % BAR_COLORS.length],
                        }}
                      />
                    </div>
                  </div>
                ))}
              </div>

              <p className="mt-4 rounded-lg border border-dashed border-prism-700/60 px-3 py-2 text-[11px] text-prism-500">
                These are model/data-derived signals from the seeded dataset's own structure (related-skill
                momentum, industry breadth, occupation breadth) — not a verified causal analysis.
              </p>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
