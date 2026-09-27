import clsx from "clsx";
import { useGraphStore } from "@/store/useGraphStore";
import type { NodeType } from "@/types/graph";

const TYPE_CONFIG: { type: NodeType; label: string; dot: string }[] = [
  { type: "skill", label: "Skills", dot: "bg-spectrum-violet" },
  { type: "occupation", label: "Occupations", dot: "bg-spectrum-cyan" },
  { type: "industry", label: "Industries", dot: "bg-spectrum-amber" },
];

export function GraphControls() {
  const { visibleTypes, toggleType, depth, setDepth, reset } = useGraphStore();

  return (
    <div className="flex flex-wrap items-center gap-2">
      {TYPE_CONFIG.map(({ type, label, dot }) => (
        <button
          key={type}
          onClick={() => toggleType(type)}
          className={clsx(
            "flex items-center gap-1.5 rounded-full border px-3 py-1.5 text-xs transition-colors",
            visibleTypes[type]
              ? "border-prism-500/70 bg-prism-800/70 text-prism-100"
              : "border-prism-700/50 bg-prism-900/40 text-prism-500"
          )}
        >
          <span className={clsx("h-1.5 w-1.5 rounded-full", visibleTypes[type] ? dot : "bg-prism-600")} />
          {label}
        </button>
      ))}

      <div className="mx-1 h-4 w-px bg-prism-700/60" />

      <label className="flex items-center gap-2 text-xs text-prism-400">
        Depth
        <select
          value={depth}
          onChange={(e) => setDepth(Number(e.target.value))}
          className="rounded-lg border border-prism-600/50 bg-prism-900/70 px-2 py-1 text-xs text-prism-100 outline-none"
        >
          <option value={1}>1</option>
          <option value={2}>2</option>
          <option value={3}>3</option>
        </select>
      </label>

      <button
        onClick={() => reset()}
        className="rounded-full border border-prism-600/50 px-3 py-1.5 text-xs text-prism-300 hover:border-spectrum-cyan/60 hover:text-spectrum-cyan"
      >
        Reset Graph
      </button>
    </div>
  );
}
