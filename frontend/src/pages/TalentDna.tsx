import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { AppNav } from "@/components/AppNav";
import { api } from "@/services/api";
import type { TalentDnaResponse } from "@/types/graph";

interface DraftSkill {
  name: string;
  strength: number;
}

const STARTER_SKILLS: DraftSkill[] = [
  { name: "Python", strength: 0.8 },
  { name: "SQL", strength: 0.75 },
  { name: "Data Visualization", strength: 0.7 },
  { name: "Machine Learning", strength: 0.5 },
];

export default function TalentDna() {
  const navigate = useNavigate();
  const [draft, setDraft] = useState<DraftSkill[]>(STARTER_SKILLS);
  const [newSkill, setNewSkill] = useState("");
  const [result, setResult] = useState<TalentDnaResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function addSkill() {
    const name = newSkill.trim();
    if (!name || draft.some((d) => d.name.toLowerCase() === name.toLowerCase())) return;
    setDraft([...draft, { name, strength: 0.6 }]);
    setNewSkill("");
  }

  function updateStrength(index: number, strength: number) {
    setDraft(draft.map((d, i) => (i === index ? { ...d, strength } : d)));
  }

  function removeSkill(index: number) {
    setDraft(draft.filter((_, i) => i !== index));
  }

  async function generate() {
    setLoading(true);
    setError(null);
    try {
      const res = await api.getTalentDna(draft);
      setResult(res);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to compute Talent DNA");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen">
      <AppNav />
      <div className="mx-auto max-w-3xl px-4 py-8">
        <p className="text-[10px] uppercase tracking-[0.3em] text-spectrum-cyan">Talent DNA</p>
        <h1 className="mt-1 font-display text-2xl text-prism-100">Map your capabilities onto the workforce graph</h1>
        <p className="mt-2 text-sm text-prism-400">
          Enter your skills and how strong you'd rate each one. This produces a multi-dimensional
          capability profile and shows where you sit relative to real occupations in the graph —
          not a single resume score.
        </p>

        <div className="mt-6 space-y-3">
          {draft.map((s, i) => (
            <div key={s.name} className="flex items-center gap-3 rounded-xl border border-prism-700/50 bg-prism-900/50 px-4 py-3">
              <span className="w-40 shrink-0 truncate text-sm text-prism-100">{s.name}</span>
              <input
                type="range"
                min={0}
                max={1}
                step={0.05}
                value={s.strength}
                onChange={(e) => updateStrength(i, Number(e.target.value))}
                className="flex-1 accent-spectrum-violet"
              />
              <span className="w-10 text-right text-xs text-prism-400">{Math.round(s.strength * 100)}%</span>
              <button onClick={() => removeSkill(i)} className="text-prism-500 hover:text-spectrum-rose" aria-label={`Remove ${s.name}`}>
                ✕
              </button>
            </div>
          ))}
        </div>

        <div className="mt-4 flex gap-2">
          <input
            value={newSkill}
            onChange={(e) => setNewSkill(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && addSkill()}
            placeholder="Add a skill (e.g. Retrieval-Augmented Generation)"
            className="flex-1 rounded-xl border border-prism-600/50 bg-prism-900/70 px-4 py-2.5 text-sm text-prism-100 outline-none focus:border-spectrum-violet/70"
          />
          <button onClick={addSkill} className="btn-secondary">Add</button>
        </div>

        <button onClick={generate} disabled={loading || draft.length === 0} className="btn-primary mt-6 w-full disabled:opacity-50">
          {loading ? "Generating…" : "Generate Talent DNA"}
        </button>

        {error && <p className="mt-4 text-sm text-spectrum-rose">{error}</p>}

        {result && (
          <div className="mt-8 space-y-6">
            <section>
              <h2 className="mb-2 font-display text-lg text-prism-100">DNA Profile</h2>
              <div className="space-y-2">
                {result.dna_profile.map((c) => (
                  <div key={c.category} className="flex items-center gap-3">
                    <span className="w-40 shrink-0 text-xs text-prism-300">{c.category}</span>
                    <div className="h-2.5 flex-1 overflow-hidden rounded-full bg-prism-800">
                      <div
                        className="h-full rounded-full bg-gradient-to-r from-spectrum-violet to-spectrum-cyan"
                        style={{ width: `${c.strength * 100}%` }}
                      />
                    </div>
                    <span className="w-10 text-right text-xs text-prism-500">{Math.round(c.strength * 100)}%</span>
                  </div>
                ))}
              </div>
              {result.unmatched_skills.length > 0 && (
                <p className="mt-2 text-xs text-prism-500">
                  Not recognized in the seeded skill catalog: {result.unmatched_skills.join(", ")}
                </p>
              )}
            </section>

            <section>
              <h2 className="mb-2 font-display text-lg text-prism-100">Nearest Occupations</h2>
              <div className="space-y-2">
                {result.nearest_occupations.map((o) => (
                  <div key={o.occupation} className="rounded-xl border border-prism-700/50 bg-prism-900/50 px-4 py-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-prism-100">{o.occupation}</span>
                      <span className="text-xs text-spectrum-cyan">{Math.round(o.match_score * 100)}% overlap</span>
                    </div>
                    {o.missing_capabilities.length > 0 && (
                      <p className="mt-1 text-xs text-prism-500">
                        Growth areas: {o.missing_capabilities.join(", ")}
                      </p>
                    )}
                  </div>
                ))}
                {result.nearest_occupations.length === 0 && (
                  <p className="text-xs text-prism-500">No overlapping occupations found for these skills yet.</p>
                )}
              </div>
            </section>

            {result.nearby_capability_clusters.length > 0 && (
              <section>
                <h2 className="mb-2 font-display text-lg text-prism-100">Nearby Capability Clusters</h2>
                <div className="flex flex-wrap gap-2">
                  {result.nearby_capability_clusters.map((c) => (
                    <span key={c.title} className="rounded-full border border-spectrum-violet/40 bg-spectrum-violet/10 px-3 py-1.5 text-xs text-prism-200">
                      {c.title}
                    </span>
                  ))}
                </div>
              </section>
            )}

            <button onClick={() => navigate("/explore")} className="btn-secondary">
              Explore in Workforce Map →
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
