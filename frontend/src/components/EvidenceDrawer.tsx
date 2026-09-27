import type { WorkforceSignal } from "@/types/graph";

/**
 * Parses a signal's evidence_json (method, data window, sample details)
 * and renders it as a small, honest "Evidence" panel — the app-wide
 * implementation of the spec's Evidence Mode requirement.
 */
export function EvidenceDrawer({ signal, onClose }: { signal: WorkforceSignal; onClose: () => void }) {
  let parsed: Record<string, unknown> = {};
  try {
    parsed = signal.evidence_json ? JSON.parse(signal.evidence_json) : {};
  } catch {
    parsed = {};
  }

  const { method, data_window, ...rest } = parsed as { method?: string; data_window?: string; [k: string]: unknown };

  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center bg-black/60 sm:items-center" onClick={onClose}>
      <div
        className="w-full max-w-lg overflow-hidden rounded-t-2xl border border-prism-600/50 bg-prism-900/95 shadow-2xl backdrop-blur-xl sm:rounded-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between border-b border-prism-700/50 px-5 py-4">
          <div>
            <p className="text-[10px] uppercase tracking-[0.25em] text-spectrum-cyan">Evidence Mode</p>
            <h3 className="mt-1 font-display text-lg text-prism-100">{signal.title}</h3>
          </div>
          <button onClick={onClose} className="rounded-full border border-prism-700/50 p-1.5 text-prism-400 hover:text-prism-100">✕</button>
        </div>

        <div className="max-h-[60vh] space-y-3 overflow-y-auto px-5 py-4 text-sm">
          <Row label="Data source" value="PRISM seeded synthetic workforce dataset (clearly labeled demo data)" />
          <Row label="Time range" value={data_window ?? "2022-2026"} />
          <Row label="Method" value={method ?? "not recorded"} />
          <Row label="Confidence" value={`${Math.round(signal.confidence * 100)}%`} />
          {signal.magnitude !== null && <Row label="Magnitude" value={String(signal.magnitude)} />}

          {Object.keys(rest).length > 0 && (
            <div>
              <p className="mb-1.5 text-xs uppercase tracking-wide text-prism-500">Parameters</p>
              <div className="space-y-1.5 rounded-lg border border-prism-700/50 bg-prism-950/60 p-3">
                {Object.entries(rest).map(([k, v]) => (
                  <div key={k} className="flex items-start justify-between gap-3 text-xs">
                    <span className="text-prism-500">{k.replace(/_/g, " ")}</span>
                    <span className="text-right text-prism-200">
                      {Array.isArray(v) ? v.join(", ") : String(v)}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
          <p className="pt-2 text-[11px] italic text-prism-500">
            This is a data-derived signal, not a guaranteed outcome. Confidence reflects sample size and
            consistency in the seeded dataset, not real-world certainty.
          </p>
        </div>
      </div>
    </div>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-xs uppercase tracking-wide text-prism-500">{label}</span>
      <span className="text-prism-100">{value}</span>
    </div>
  );
}
