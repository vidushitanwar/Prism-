import { useDemoModeStore } from "@/store/useDemoModeStore";

export function DemoModeOverlay() {
  const { running, caption, stepIndex, totalSteps, stop } = useDemoModeStore();

  if (!running) return null;

  return (
    <div className="fixed inset-x-0 bottom-6 z-[60] flex justify-center px-4">
      <div className="flex items-center gap-4 rounded-2xl border border-spectrum-violet/50 bg-prism-950/95 px-5 py-3 shadow-2xl backdrop-blur-xl">
        <span className="text-lg">🚀</span>
        <div>
          <p className="text-[10px] uppercase tracking-[0.25em] text-spectrum-violet">
            Demo Mode — Step {stepIndex}/{totalSteps}
          </p>
          <p className="text-sm text-prism-100">{caption}</p>
        </div>
        <button
          onClick={stop}
          className="ml-2 shrink-0 rounded-full border border-prism-600/60 px-3 py-1.5 text-xs text-prism-300 hover:border-spectrum-rose/60 hover:text-spectrum-rose"
        >
          Stop Demo
        </button>
      </div>
    </div>
  );
}
