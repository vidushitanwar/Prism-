import { create } from "zustand";
import type { GraphNode, GraphEdge, NodeType } from "@/types/graph";
import { api } from "@/services/api";

interface GraphState {
  nodes: GraphNode[];
  edges: GraphEdge[];
  selectedNodeId: string | null;
  visibleTypes: Record<NodeType, boolean>;
  depth: number;
  loading: boolean;
  error: string | null;
  expandedNodeIds: Set<string>;

  loadInitial: () => Promise<void>;
  expandNode: (nodeId: string) => Promise<void>;
  focusNode: (nodeId: string) => Promise<void>;
  selectNode: (nodeId: string | null) => void;
  toggleType: (type: NodeType) => void;
  setDepth: (depth: number) => void;
  reset: () => Promise<void>;
}

function mergeGraphs(a: { nodes: GraphNode[]; edges: GraphEdge[] }, b: { nodes: GraphNode[]; edges: GraphEdge[] }) {
  const nodeMap = new Map(a.nodes.map((n) => [n.id, n]));
  for (const n of b.nodes) nodeMap.set(n.id, n);

  const edgeKey = (e: GraphEdge) => `${e.source}__${e.target}__${e.edge_type}`;
  const edgeMap = new Map(a.edges.map((e) => [edgeKey(e), e]));
  for (const e of b.edges) edgeMap.set(edgeKey(e), e);

  return { nodes: Array.from(nodeMap.values()), edges: Array.from(edgeMap.values()) };
}

export const useGraphStore = create<GraphState>((set, get) => ({
  nodes: [],
  edges: [],
  selectedNodeId: null,
  visibleTypes: { skill: true, occupation: true, industry: true },
  depth: 1,
  loading: false,
  error: null,
  expandedNodeIds: new Set(),

  loadInitial: async () => {
    set({ loading: true, error: null });
    try {
      const data = await api.getGraph({ maxNodes: 70 });
      set({ nodes: data.nodes, edges: data.edges, loading: false, expandedNodeIds: new Set() });
    } catch (e) {
      set({ loading: false, error: e instanceof Error ? e.message : "Failed to load graph" });
    }
  },

  expandNode: async (nodeId: string) => {
    const { expandedNodeIds, depth } = get();
    if (expandedNodeIds.has(nodeId)) return;
    set({ loading: true, error: null });
    try {
      const data = await api.getGraph({ nodeId, depth, maxNodes: 40 });
      set((state) => ({
        ...mergeGraphs(state, data),
        loading: false,
        expandedNodeIds: new Set(state.expandedNodeIds).add(nodeId),
      }));
    } catch (e) {
      set({ loading: false, error: e instanceof Error ? e.message : "Failed to expand node" });
    }
  },

  focusNode: async (nodeId: string) => {
    const { depth } = get();
    set({ loading: true, error: null, selectedNodeId: nodeId });
    try {
      const data = await api.getGraph({ nodeId, depth, maxNodes: 50 });
      set({ nodes: data.nodes, edges: data.edges, loading: false, expandedNodeIds: new Set([nodeId]) });
    } catch (e) {
      set({ loading: false, error: e instanceof Error ? e.message : "Failed to focus node" });
    }
  },

  selectNode: (nodeId) => set({ selectedNodeId: nodeId }),

  toggleType: (type) =>
    set((state) => ({ visibleTypes: { ...state.visibleTypes, [type]: !state.visibleTypes[type] } })),

  setDepth: (depth) => set({ depth }),

  reset: async () => {
    set({ selectedNodeId: null });
    await get().loadInitial();
  },
}));
