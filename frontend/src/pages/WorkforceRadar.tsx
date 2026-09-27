import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { AppNav } from "@/components/AppNav";
import { EvidenceDrawer } from "@/components/EvidenceDrawer";
import { api } from "@/services/api";
import { useGraphStore } from "@/store/useGraphStore";
import type { WorkforceSignal } from "@/types/graph";

interface Section {
  key: string;
  title: string;
  accent: string;
  fetcher: () => Promise<WorkforceSignal[]>;
}

const SECTIONS: Section[] = [
  { key: "emerging", title: "Emerging", accent: "border-spectrum-violet/40 bg-spectrum-violet/5", fetcher: () => api.getEmergingSkills(5) },
  { key: "declining", title: "Declining", accent: "border-spectrum-rose/40 bg-spectrum-rose/5", fetcher: () => api.getDecliningSkills(5) },
  { key: "talent_gap", title: "Talent Gap", accent: "border-spectrum-amber/40 bg-spectrum-amber/5", fetcher: () => api.getTalentGaps(5) },
  { key: "structural_shift", title: "Structural Shift", accent: "border-spectrum-cyan/40 bg-spectrum-cyan/5", fetcher: () => api.getStructuralShifts(5) },
  { key: "new_capability", title: "New Capability", accent: "border-spectrum-emerald/40 bg-spectrum-emerald/5", fetcher: () => api.getCombinationClusters(5) },
];

export default function WorkforceRadar() {
  const [data, setData] = useState<Record<string, WorkforceSignal[]>>({});
  const [loading, setLoading] = useState(true);
  const [evidenceTarget, setEvidenceTarget] = useState<WorkforceSignal | null>(null);
  const navigate = useNavigate();
  const focusNode = useGraphStore((s) => s.focusNode);

  useEffect(() => {
    setLoading(true);
    Promise.all(SECTIONS.map((s) => s.fetcher().catch(() => [])))
      .then((results) => {
        const map: Record<string, WorkforceSignal[]> = {};
        SECTIONS.forEach((s, i) => (map[s.key] = results[i]));
        setData(map);
      })
      .finally(() => setLoading(false));
  }, []);

  function openNode(subjectId: number, subjectType: string) {
    if (subjectType !== "skill") return;
    navigate("/explore");
    focusNode(`skill:${subjectId}`);
  }

  return (
    <div className="min-h-screen">
      <AppNav />
      <div className="mx-auto max-w-6xl px-4 py-8">
        <p className="text-[10px] uppercase tracking-[0.3em] text-spectrum-cyan">Workforce Radar</p>
        <h1 className="mt-1 font-display text-2xl text-prism-100">Live Workforce Intelligence Signals</h1>
        <p className="mt-2 max-w-2xl text-sm text-prism-400">
          Every card below is computed from the seeded 2022–2026 dataset — click "Evidence" on any item to
          see the method and parameters behind it.
        </p>

        {loading && <p className="mt-6 text-sm text-prism-400">Loading signals…</p>}

        <div className="mt-6 grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
          {SECTIONS.map((section) => (
            <div key={section.key} className={`rounded-2xl border ${section.accent} p-4`}>
              <h2 className="font-display text-sm uppercase tracking-wide text-prism-200">{section.title}</h2>
              <div className="mt-3 space-y-2">
                {(data[section.key] ?? []).length === 0 && !loading && (
                  <p className="text-xs text-prism-500">No signals in this category.</p>
                )}
                {(data[section.key] ?? []).map((s) => (
                  <div key={s.id} className="rounded-lg border border-prism-700/40 bg-prism-950/40 px-3 py-2">
                    <button
                      onClick={() => openNode(s.subject_id, s.subject_type)}
                      className="text-left text-sm font-medium text-prism-100 hover:text-spectrum-cyan"
                    >
                      {s.title}
                    </button>
                    <p className="mt-0.5 line-clamp-2 text-[11px] text-prism-500">{s.description}</p>
                    <button
                      onClick={() => setEvidenceTarget(s)}
                      className="mt-1 text-[10px] uppercase tracking-wide text-prism-500 hover:text-spectrum-cyan"
                    >
                      Evidence →
                    </button>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {evidenceTarget && <EvidenceDrawer signal={evidenceTarget} onClose={() => setEvidenceTarget(null)} />}
    </div>
  );
}
