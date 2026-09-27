import { useEffect } from "react";
import clsx from "clsx";
import { useTimeMachineStore } from "@/store/useTimeMachineStore";

const STAGE_LEGEND: { stage: string; color: string }[] = [
  { stage: "Emerging", color: "bg-spectrum-violet" },
  { stage: "Growing", color: "bg-spectrum-cyan" },
  { stage: "Established", color: "bg-spectrum-emerald" },
  { stage: "Transforming", color: "bg-spectrum-amber" },
  { stage: "Declining", color: "bg-spectrum-rose" },
  { stage: "Ghost", color: "bg-prism-500" },
];

export function TimeMachine() {
  const { years, currentYear, playing, loading, toggle, setYear, init } = useTimeMachineStore();

  useEffect(() => {
    init();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="flex flex-col gap-2 border-t border-prism-700/40 bg-prism-950/90 px-4 py-3 backdrop-blur-xl sm:flex-row sm:items-center sm:gap-6">
      <div className="flex items-center gap-3">
        <button
          onClick={toggle}
          className={clsx(
            "flex h-9 w-9 items-center justify-center rounded-full border transition-colors",
            playing
              ? "border-spectrum-rose/60 text-spectrum-rose"
              : "border-spectrum-violet/60 text-spectrum-violet hover:bg-spectrum-violet/10"
          )}
          aria-label={playing ? "Pause timeline" : "Play timeline"}
        >
          {playing ? "❚❚" : "▶"}
        </button>
        <div>
          <p className="text-[10px] uppercase tracking-[0.25em] text-spectrum-cyan">Workforce Time Machine</p>
          <p className="font-display text-lg text-prism-100">{currentYear}{loading && <span className="ml-2 text-xs text-prism-500">updating…</span>}</p>
        </div>
      </div>

      <div className="relative flex-1">
        <div className="relative h-1.5 w-full rounded-full bg-prism-800">
          <div
            className="absolute h-full rounded-full bg-gradient-to-r from-spectrum-violet to-spectrum-cyan transition-all duration-300"
            style={{
              width: `${(years.indexOf(currentYear) / Math.max(years.length - 1, 1)) * 100}%`,
            }}
          />
        </div>
        <div className="mt-2 flex justify-between">
          {years.map((year) => (
            <button
              key={year}
              onClick={() => setYear(year)}
              className="flex flex-col items-center gap-1 text-xs"
            >
              <span
                className={clsx(
                  "h-3 w-3 rounded-full border-2 transition-all",
                  year === currentYear
                    ? "scale-125 border-spectrum-violet bg-spectrum-violet"
                    : "border-prism-600 bg-prism-900 hover:border-prism-400"
                )}
              />
              <span className={year === currentYear ? "text-prism-100" : "text-prism-500"}>{year}</span>
            </button>
          ))}
        </div>
      </div>

      <div className="hidden items-center gap-3 lg:flex">
        {STAGE_LEGEND.map((l) => (
          <span key={l.stage} className="flex items-center gap-1.5 text-[10px] text-prism-400">
            <span className={clsx("h-1.5 w-1.5 rounded-full", l.color)} />
            {l.stage}
          </span>
        ))}
      </div>
    </div>
  );
}
