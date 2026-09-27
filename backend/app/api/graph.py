from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.graph.graph_metrics import build_graph, node_neighborhood
from app.schemas.schemas import GraphResponse

router = APIRouter(prefix="/graph", tags=["graph"])


@router.get("", response_model=GraphResponse)
def get_graph(
    node_id: str | None = Query(default=None, description="e.g. skill:12, occupation:3, industry:5"),
    depth: int = Query(default=1, ge=1, le=3),
    max_nodes: int = Query(default=60, le=200),
    db: Session = Depends(get_db),
):
    """
    Without node_id: returns a capped snapshot of the whole graph (for an
    initial "universe" view). With node_id: returns a bounded neighborhood
    around that node — this is what node expansion in the Workforce Map
    (Phase 2) calls.
    """
    g = build_graph(db)

    if node_id:
        return node_neighborhood(g, node_id, depth=depth, max_nodes=max_nodes)

    # Whole-graph snapshot, capped for performance (per-type sampling so
    # the initial view isn't dominated by one node type).
    nodes = list(g.nodes(data=True))
    by_type: dict[str, list] = {}
    for n, data in nodes:
        by_type.setdefault(data.get("type", "unknown"), []).append((n, data))

    kept_ids = set()
    per_type_cap = max(10, max_nodes // max(len(by_type), 1))
    for node_type, items in by_type.items():
        for n, _ in items[:per_type_cap]:
            kept_ids.add(n)

    subgraph = g.subgraph(kept_ids)
    out_nodes = [{"id": n, **subgraph.nodes[n]} for n in subgraph.nodes()]
    out_edges = [{"source": u, "target": v, **subgraph.edges[u, v]} for u, v in subgraph.edges()]
    return {"nodes": out_nodes, "edges": out_edges}
