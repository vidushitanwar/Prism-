import { AppNav } from "@/components/AppNav";
import { SearchBar } from "@/components/SearchBar";
import { GraphControls } from "@/components/GraphControls";
import { WorkforceMap } from "@/graph/WorkforceMap";
import { NodeDetailPanel } from "@/components/NodeDetailPanel";
import { TimeMachine } from "@/components/TimeMachine";
import { useGraphStore } from "@/store/useGraphStore";

export default function Explore() {
  const error = useGraphStore((s) => s.error);

  return (
    <div className="flex h-screen flex-col">
      <AppNav />

      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-prism-700/40 bg-prism-950/70 px-4 py-3">
        <SearchBar />
        <GraphControls />
      </div>

      <div className="relative flex-1 overflow-hidden">
        {error && (
          <div className="absolute left-1/2 top-4 z-30 -translate-x-1/2 rounded-lg border border-spectrum-rose/40 bg-prism-900/95 px-4 py-2 text-xs text-spectrum-rose shadow-lg">
            {error} — is the backend running at the configured API URL?
          </div>
        )}
        <WorkforceMap />
        <NodeDetailPanel />
      </div>

      <TimeMachine />
    </div>
  );
}
