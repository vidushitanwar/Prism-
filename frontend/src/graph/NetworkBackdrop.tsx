import { useMemo } from "react";

/**
 * Decorative animated node/edge network for the landing hero.
 * This is intentionally lightweight (pure SVG + CSS) — the real,
 * interactive Workforce Map (React Flow / Cytoscape-backed) is built
 * in Phase 2 under src/graph/WorkforceMap.tsx.
 */
export function NetworkBackdrop() {
  const nodes = useMemo(
    () =>
      Array.from({ length: 26 }, (_, i) => ({
        id: i,
        x: Math.random() * 100,
        y: Math.random() * 100,
        r: 1.5 + Math.random() * 2.5,
        delay: Math.random() * 4,
      })),
    []
  );

  const edges = useMemo(() => {
    const list: { a: number; b: number }[] = [];
    nodes.forEach((n, i) => {
      const next = nodes[(i + 1 + Math.floor(Math.random() * 3)) % nodes.length];
      list.push({ a: n.id, b: next.id });
    });
    return list;
  }, [nodes]);

  return (
    <svg
      className="pointer-events-none absolute inset-0 z-0 h-full w-full opacity-60"
      viewBox="0 0 100 100"
      preserveAspectRatio="xMidYMid slice"
    >
      {edges.map((e, i) => {
        const a = nodes[e.a];
        const b = nodes[e.b];
        return (
          <line
            key={i}
            x1={a.x}
            y1={a.y}
            x2={b.x}
            y2={b.y}
            stroke="url(#edgeGradient)"
            strokeWidth="0.15"
          />
        );
      })}
      {nodes.map((n) => (
        <circle
          key={n.id}
          cx={n.x}
          cy={n.y}
          r={n.r * 0.3}
          fill="#7c85d4"
          className="animate-pulse"
          style={{ animationDelay: `${n.delay}s`, animationDuration: "3.5s" }}
        />
      ))}
      <defs>
        <linearGradient id="edgeGradient" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#8b5cf6" stopOpacity="0.5" />
          <stop offset="100%" stopColor="#22d3ee" stopOpacity="0.2" />
        </linearGradient>
      </defs>
    </svg>
  );
}
