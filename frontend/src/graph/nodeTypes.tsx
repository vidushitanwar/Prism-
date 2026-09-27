import { Handle, Position, type NodeProps } from "reactflow";
import clsx from "clsx";

const TYPE_STYLES: Record<string, { ring: string; dot: string; text: string }> = {
  skill: { ring: "border-spectrum-violet/60", dot: "bg-spectrum-violet", text: "text-prism-100" },
  occupation: { ring: "border-spectrum-cyan/60", dot: "bg-spectrum-cyan", text: "text-prism-100" },
  industry: { ring: "border-spectrum-amber/60", dot: "bg-spectrum-amber", text: "text-prism-100" },
};

const STAGE_DOT: Record<string, string> = {
  Emerging: "bg-spectrum-violet",
  Growing: "bg-spectrum-cyan",
  Established: "bg-spectrum-emerald",
  Transforming: "bg-spectrum-amber",
  Declining: "bg-spectrum-rose",
  Ghost: "bg-prism-500",
};

interface PrismNodeData {
  label: string;
  type: string;
  category?: string;
  demandScore?: number; // 0-100, from the Time Machine snapshot (skills only)
  lifecycleStage?: string;
  growthRate?: number;
}

function BaseNode({ data, selected }: NodeProps<PrismNodeData>) {
  const style = TYPE_STYLES[data.type] ?? TYPE_STYLES.skill;
  const hasSnapshot = data.type === "skill" && typeof data.demandScore === "number";
  // Scale 0.85x-1.25x by demand so the Time Machine visibly changes the map.
  const scale = hasSnapshot ? 0.85 + Math.min(1, (data.demandScore as number) / 100) * 0.4 : 1;

  return (
    <div
      style={{ transform: `scale(${scale})` }}
      className={clsx(
        "rounded-xl border px-3.5 py-2 backdrop-blur-md shadow-lg transition-all duration-300",
        "bg-prism-900/80 min-w-[110px] max-w-[180px] cursor-pointer",
        style.ring,
        selected && "ring-2 ring-white/70 -translate-y-0.5 shadow-2xl"
      )}
    >
      <Handle type="target" position={Position.Top} className="!bg-prism-500 !border-none !w-1.5 !h-1.5" />
      <div className="flex items-center gap-2">
        <span
          className={clsx(
            "h-1.5 w-1.5 shrink-0 rounded-full",
            hasSnapshot ? STAGE_DOT[data.lifecycleStage ?? ""] ?? style.dot : style.dot
          )}
        />
        <span className={clsx("truncate text-xs font-medium", style.text)}>{data.label}</span>
      </div>
      {data.category && (
        <div className="mt-0.5 truncate text-[10px] uppercase tracking-wide text-prism-400">
          {data.category}
        </div>
      )}
      {hasSnapshot && (
        <div className="mt-1 flex items-center justify-between text-[10px] text-prism-500">
          <span>{data.lifecycleStage}</span>
          <span>
            {(data.growthRate ?? 0) >= 0 ? "▲" : "▼"} {Math.abs(data.growthRate ?? 0).toFixed(0)}%
          </span>
        </div>
      )}
      <Handle type="source" position={Position.Bottom} className="!bg-prism-500 !border-none !w-1.5 !h-1.5" />
    </div>
  );
}

export const nodeTypes = {
  skill: BaseNode,
  occupation: BaseNode,
  industry: BaseNode,
};
