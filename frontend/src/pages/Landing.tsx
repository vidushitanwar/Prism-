import { useNavigate } from "react-router-dom";
import { useBackendStatus } from "@/hooks/useBackendStatus";
import { StatusPill } from "@/components/ui/StatusPill";
import { NetworkBackdrop } from "@/graph/NetworkBackdrop";
import { useDemoModeStore } from "@/store/useDemoModeStore";

export default function Landing() {
  const navigate = useNavigate();
  const { status, dbStatus } = useBackendStatus();
  const startDemo = useDemoModeStore((s) => s.start);
  const demoRunning = useDemoModeStore((s) => s.running);

  return (
    <div className="relative flex min-h-screen flex-col overflow-hidden">
      <NetworkBackdrop />

      <header className="relative z-10 flex items-center justify-between px-8 py-6">
        <div className="font-display text-lg tracking-widest text-prism-100">PRISM</div>
        <div className="flex items-center gap-3">
          <StatusPill label="API" status={status} />
          <StatusPill label="DB" status={dbStatus} />
        </div>
      </header>

      <main className="relative z-10 flex flex-1 flex-col items-center justify-center px-6 text-center">
        <p className="mb-4 text-xs uppercase tracking-[0.35em] text-spectrum-cyan">
          Workforce Intelligence Platform
        </p>
        <h1 className="max-w-4xl font-display text-5xl font-semibold leading-tight text-prism-100 sm:text-7xl">
          The Living Map of
          <span className="block bg-gradient-to-r from-spectrum-violet via-spectrum-cyan to-spectrum-amber bg-clip-text text-transparent">
            Human Capability
          </span>
        </h1>
        <p className="mt-6 max-w-2xl text-balance text-lg text-prism-300">
          Explore how skills, careers, industries, talent and opportunities connect —
          and watch the workforce evolve through time.
        </p>

        <div className="mt-10 flex flex-wrap items-center justify-center gap-4">
          <button className="btn-primary" onClick={() => navigate("/explore")}>
            Explore Workforce
          </button>
          <button className="btn-secondary" onClick={() => navigate("/radar")}>
            View Live Signals
          </button>
        </div>

        <button
          onClick={startDemo}
          disabled={demoRunning}
          className="mt-6 rounded-full border border-spectrum-violet/50 bg-spectrum-violet/10 px-5 py-2 text-sm text-prism-100 transition-colors hover:bg-spectrum-violet/20 disabled:opacity-50"
        >
          🚀 {demoRunning ? "Demo running…" : "Demo Mode"}
        </button>

        <p className="mt-8 max-w-xl text-xs text-prism-400">
          All data shown is a seeded, internally-consistent synthetic dataset (2022–2026) —
          it demonstrates the platform's methodology and is not real-world workforce data.
        </p>
      </main>
    </div>
  );
}
