import { useEffect, useState } from "react";
import { AppNav } from "@/components/AppNav";
import { WhyModal } from "@/components/WhyModal";
import { EvidenceDrawer } from "@/components/EvidenceDrawer";
import { useGraphStore } from "@/store/useGraphStore";
import { useTimeMachineStore } from "@/store/useTimeMachineStore";
import { useNavigate } from "react-router-dom";
import { api } from "@/services/api";
import type { WorkforceSignal } from "@/types/graph";

export default function StructuralShifts() {
  const [signals, setSignals] = useState<WorkforceSignal[]>([]);
  const [loading, setLoading] = useState(true);
  const [whyTarget, setWhyTarget] = useState<WorkforceSignal | null>(null);
  const [evidenceTarget, setEvidenceTarget] = useState<WorkforceSignal | null>(null);
  const navigate = useNavigate();
  const focusNode = useGraphStore((s) => s.focusNode);
  const currentYear = useTimeMachineStore((s) => s.currentYear);

  useEffect(() => {
    setLoading(true);
    api.getStructuralShifts(20).then(setSignals).catch(() => setSignals([])).finally(() => setLoading(false));
  }, []);

  return (
    <div className="min-h-screen">
      <AppNav />
      <div className="mx-auto max-w-4xl px-4 py-8">
        <p className="text-[10px] uppercase tracking-[0.3em] text-spectrum-amber">Structural Shift Detector</p>
        <h1 className="mt-1 font-display text-2xl text-prism-100">Unusual Deviations From Historical Trends</h1>
        <p className="mt-2 max-w-2xl text-sm text-prism-400">
          Flags skills whose latest year-over-year growth deviates sharply (z-score based) from their own
          2022–2025 trend — a simple, transparent change-point heuristic, not a certified forecast.
        </p>

        {loading && <p className="mt-6 text-sm text-prism-400">Loading…</p>}
        {!loading && signals.length === 0 && (
          <p className="mt-6 rounded-xl border border-dashed border-prism-700/60 px-4 py-6 text-center text-sm text-prism-500">
            No structural shifts detected in the seeded dataset.
          </p>
        )}

        <div className="mt-6 space-y-3">
          {signals.map((s) => (
            <div key={s.id} className="rounded-2xl border border-spectrum-amber/40 bg-spectrum-amber/5 px-5 py-4">
              <div className="flex flex-wrap items-baseline justify-between gap-2">
                <h3 className="font-display text-lg text-prism-100">{s.title}</h3>
                <span className="text-xs text-prism-400">z = {s.magnitude?.toFixed(2)}</span>
              </div>
              <p className="mt-1 text-sm text-prism-300">{s.description}</p>
              <div className="mt-3 flex flex-wrap gap-2">
                <button
                  onClick={() => setWhyTarget(s)}
                  className="rounded-full border border-spectrum-amber/50 px-3 py-1.5 text-xs text-spectrum-amber hover:bg-spectrum-amber/10"
                >
                  Why did this change?
                </button>
                <button
                  onClick={() => setEvidenceTarget(s)}
                  className="rounded-full border border-prism-600/50 px-3 py-1.5 text-xs text-prism-300 hover:border-spectrum-cyan/60 hover:text-spectrum-cyan"
                >
                  Evidence
                </button>
                <button
                  onClick={() => {
                    navigate("/explore");
                    focusNode(`skill:${s.subject_id}`);
                  }}
                  className="rounded-full border border-prism-600/50 px-3 py-1.5 text-xs text-prism-300 hover:border-spectrum-violet/60 hover:text-spectrum-violet"
                >
                  Open in Workforce Map
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {whyTarget && (
        <WhyModal skillId={whyTarget.subject_id} year={whyTarget.year ?? currentYear} onClose={() => setWhyTarget(null)} />
      )}
      {evidenceTarget && <EvidenceDrawer signal={evidenceTarget} onClose={() => setEvidenceTarget(null)} />}
    </div>
  );
}
