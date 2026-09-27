import { useEffect, useMemo, useCallback, type MouseEvent } from "react";
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  type Node,
  type Edge,
  BackgroundVariant,
} from "reactflow";
import "reactflow/dist/style.css";

import { useGraphStore } from "@/store/useGraphStore";
import { useTimeMachineStore } from "@/store/useTimeMachineStore";
import { nodeTypes } from "@/graph/nodeTypes";
import { computeForceLayout } from "@/graph/forceLayout";
import type { NodeType } from "@/types/graph";

const EDGE_COLOR: Record<string, string> = {
  occupation_skill: "#4750a3",
  skill_skill: "#8b5cf6",
  industry_skill: "#f59e0b",
};

export function WorkforceMap() {
  const {
    nodes: rawNodes,
    edges: rawEdges,
    visibleTypes,
    selectedNodeId,
    loading,
    loadInitial,
    expandNode,
    selectNode,
  } = useGraphStore();

  useEffect(() => {
    loadInitial();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const filteredGraph = useMemo(() => {
    const visibleIds = new Set(
      rawNodes.filter((n) => visibleTypes[n.type as NodeType]).map((n) => n.id)
    );
    return {
      nodes: rawNodes.filter((n) => visibleIds.has(n.id)),
      edges: rawEdges.filter((e) => visibleIds.has(e.source) && visibleIds.has(e.target)),
    };
  }, [rawNodes, rawEdges, visibleTypes]);

  const positioned = useMemo(
    () => computeForceLayout(filteredGraph.nodes, filteredGraph.edges),
    // Re-layout only when the node/edge *set* changes, not on every render.
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [filteredGraph.nodes.map((n) => n.id).join(","), filteredGraph.edges.length]
  );

  const snapshotByskillId = useTimeMachineStore((s) => s.snapshotByskillId);

  const flowNodes: Node[] = useMemo(
    () =>
      positioned.map((n) => {
        const skillId = n.type === "skill" ? Number(n.id.split(":")[1]) : null;
        const snapshot = skillId !== null ? snapshotByskillId.get(skillId) : undefined;
        return {
          id: n.id,
          type: n.type,
          position: { x: n.x, y: n.y },
          data: {
            label: n.label,
            type: n.type,
            category: n.category,
            demandScore: snapshot?.demand_score,
            lifecycleStage: snapshot?.lifecycle_stage,
            growthRate: snapshot?.growth_rate,
          },
          selected: n.id === selectedNodeId,
        };
      }),
    [positioned, selectedNodeId, snapshotByskillId]
  );

  const flowEdges: Edge[] = useMemo(
    () =>
      filteredGraph.edges.map((e, i) => ({
        id: `${e.source}-${e.target}-${i}`,
        source: e.source,
        target: e.target,
        type: "smoothstep",
        animated: false,
        style: {
          stroke: EDGE_COLOR[e.edge_type] ?? "#4750a3",
          strokeWidth: Math.max(0.8, Math.min(1.8, e.weight * 1.6)),
          opacity: 0.32,
        },
      })),
    [filteredGraph.edges]
  );

  const handleNodeClick = useCallback(
    (_: MouseEvent, node: Node) => {
      selectNode(node.id);
      expandNode(node.id);
    },
    [selectNode, expandNode]
  );

  const handlePaneClick = useCallback(() => selectNode(null), [selectNode]);

  return (
    <div className="relative h-full w-full">
      {loading && (
        <div className="absolute left-1/2 top-4 z-20 -translate-x-1/2 rounded-full bg-prism-900/90 px-4 py-1.5 text-xs text-prism-300 shadow-lg">
          Loading workforce graph…
        </div>
      )}
      <ReactFlow
        nodes={flowNodes}
        edges={flowEdges}
        nodeTypes={nodeTypes}
        onNodeClick={handleNodeClick}
        onPaneClick={handlePaneClick}
        fitView
        fitViewOptions={{ padding: 0.08 }}
        minZoom={0.15}
        maxZoom={2.5}
        proOptions={{ hideAttribution: true }}
      >
        <Background variant={BackgroundVariant.Dots} gap={24} size={1} color="#1c2140" />
        <Controls className="!bg-prism-900/80 !border !border-prism-600/40 !rounded-xl overflow-hidden" />
        <MiniMap
          className="!bg-prism-900/80 !border !border-prism-600/40 !rounded-xl"
          nodeColor={(n) =>
            n.type === "skill" ? "#8b5cf6" : n.type === "occupation" ? "#22d3ee" : "#f59e0b"
          }
          maskColor="rgba(6,7,13,0.75)"
        />
      </ReactFlow>
    </div>
  );
}
