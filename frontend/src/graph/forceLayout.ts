import {
  forceSimulation,
  forceLink,
  forceManyBody,
  forceCenter,
  forceCollide,
  forceX,
  forceY,
} from "d3-force";
import type { GraphNode, GraphEdge } from "@/types/graph";

export interface PositionedNode extends GraphNode {
  x: number;
  y: number;
}

/**
 * Runs a d3-force simulation for a fixed number of ticks (synchronously,
 * no animation loop) to produce an organic, non-overlapping layout for
 * the Workforce Map. Re-run whenever the node/edge set changes.
 */
export function computeForceLayout(
  nodes: GraphNode[],
  edges: GraphEdge[],
  width = 1600,
  height = 1000
): PositionedNode[] {
  type SimNode = GraphNode & { x: number; y: number; vx?: number; vy?: number };

  const clusterCenters: Record<GraphNode["type"], { x: number; y: number }> = {
    skill: { x: width * 0.5, y: height * 0.5 },
    occupation: { x: width * 0.2, y: height * 0.52 },
    industry: { x: width * 0.8, y: height * 0.48 },
  };

  const simNodes: SimNode[] = nodes.map((n) => ({
    ...n,
    x: clusterCenters[n.type].x + (Math.random() - 0.5) * 80,
    y: clusterCenters[n.type].y + (Math.random() - 0.5) * 80,
  }));

  const idIndex = new Map(simNodes.map((n, i) => [n.id, i]));
  const simLinks = edges
    .filter((e) => idIndex.has(e.source) && idIndex.has(e.target))
    .map((e) => ({ source: e.source, target: e.target, weight: e.weight }));

  const simulation = forceSimulation(simNodes as any)
    .force(
      "x",
      forceX((d: any) => clusterCenters[d.type as GraphNode["type"]].x).strength(0.9)
    )
    .force(
      "y",
      forceY((d: any) => clusterCenters[d.type as GraphNode["type"]].y).strength(0.9)
    )
    .force(
      "link",
      forceLink(simLinks as any)
        .id((d: any) => d.id)
        .distance((l: any) => 130 + (1 - Math.min(l.weight ?? 0.5, 1)) * 70)
        .strength(0.7)
    )
    .force("charge", forceManyBody().strength(-180))
    .force("center", forceCenter(width / 2, height / 2))
    .force("collide", forceCollide().radius(92).strength(1))
    .stop();

  const ticks = Math.min(260, Math.max(100, nodes.length * 2));
  for (let i = 0; i < ticks; i++) simulation.tick();

  return simNodes.map((n) => ({ ...n, x: n.x, y: n.y }));
}
