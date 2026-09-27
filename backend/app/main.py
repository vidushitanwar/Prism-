"""
PRISM — The Living Map of Human Capability
FastAPI application entrypoint.

Wires up: app instance, CORS, a global JSON error handler (never leaks
raw stack traces), automatic startup seeding, and every API router —
health, search, skills, occupations, industries, workforce intelligence
(emerging/declining/shifts/bridges/clusters/wormholes/why), the graph
endpoint, the career route planner, talent DNA / geography / education,
and the workforce shock simulator.
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.api import health, skills, occupations, industries, workforce, graph, search, routes_planner, talent_geo_education, simulation
from app.data.seed_generator import seed_all

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    description="Workforce intelligence graph API powering PRISM.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    # Never leak raw stack traces to the client.
    return JSONResponse(
        status_code=500,
        content={"status": "error", "message": "Internal server error."},
    )


app.include_router(health.router, prefix=settings.API_PREFIX)
app.include_router(search.router, prefix=settings.API_PREFIX)
app.include_router(skills.router, prefix=settings.API_PREFIX)
app.include_router(occupations.router, prefix=settings.API_PREFIX)
app.include_router(industries.router, prefix=settings.API_PREFIX)
app.include_router(workforce.router, prefix=settings.API_PREFIX)
app.include_router(graph.router, prefix=settings.API_PREFIX)
app.include_router(routes_planner.router, prefix=settings.API_PREFIX)
app.include_router(talent_geo_education.router, prefix=settings.API_PREFIX)
app.include_router(simulation.router, prefix=settings.API_PREFIX)


@app.on_event("startup")
def on_startup():
    """
    Creates tables and seeds the database automatically if it's empty, so
    the app "just works" immediately after `pip install` + `uvicorn` with
    no manual data-loading step. Safe to call repeatedly — seed_all() is
    a no-op once data already exists.
    """
    seed_all(force=False)


@app.get("/")
def root():
    return {
        "name": "PRISM Workforce Intelligence API",
        "status": "running",
        "docs": "/docs",
    }
