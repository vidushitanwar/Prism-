import clsx from "clsx";
import type { BackendStatus } from "@/hooks/useBackendStatus";

const LABEL: Record<BackendStatus, string> = {
  checking: "Checking…",
  online: "Online",
  offline: "Offline",
};

const DOT_COLOR: Record<BackendStatus, string> = {
  checking: "bg-prism-400 animate-pulse",
  online: "bg-spectrum-emerald",
  offline: "bg-spectrum-rose",
};

export function StatusPill({ label, status }: { label: string; status: BackendStatus }) {
  return (
    <div className="flex items-center gap-2 rounded-full border border-prism-600/50 bg-prism-900/60 px-3 py-1.5 text-xs text-prism-300">
      <span className={clsx("h-2 w-2 rounded-full", DOT_COLOR[status])} />
      <span>
        {label}: <span className="text-prism-100">{LABEL[status]}</span>
      </span>
    </div>
  );
}
