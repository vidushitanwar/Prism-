# PRISM — The Living Map of Human Capability

An interactive workforce intelligence platform that lets you navigate the
relationships between **skills ↔ occupations ↔ industries ↔ talent ↔
education ↔ geography ↔ opportunities**, and see how those relationships
change over time (2022–2026).

> **Build status: Phase 8 — Production Readiness (final checkpoint)**
> All 8 planned phases are implemented. This checkpoint is a full audit
> pass rather than new features: every frontend `api.*` call was
> cross-referenced against its backend route (all match), every
> promise-returning fetch across the app now has proper `.catch`/error UI
> instead of silently hanging or throwing an unhandled rejection, no
> placeholder routes remain outside the 404 handler, no hardcoded secrets
> exist, an unused heavy dependency (`sentence-transformers`) was removed
> since the actual capability-clustering method is graph-based (see
> [`docs/methodology.md`](docs/methodology.md)), and the methodology doc
> was rewritten to describe what the code actually does. See
> [Limitations](#limitations) for what a *live* install/run audit would
> still need to confirm, since this sandbox has no internet access to
> perform one itself.

## Architecture

```
PRISM_Workforce_Intelligence/
├── frontend/     React + TypeScript + Vite + Tailwind
├── backend/      FastAPI + SQLAlchemy (SQLite by default, Postgres-ready)
├── data/         raw / processed / seed datasets
├── docs/         methodology.md
├── docker-compose.yml   optional Postgres service
└── .env.example
```

## Tech stack

- **Frontend:** React 18, TypeScript, Vite, Tailwind CSS, React Router, Zustand
- **Backend:** Python, FastAPI, SQLAlchemy
- **Database:** SQLite by default (zero setup) — PostgreSQL supported via `DATABASE_URL`
- **Analytics:** Pandas, NumPy, scikit-learn, NetworkX (graph-structural capability clustering via community detection — see [`docs/methodology.md`](docs/methodology.md))

## Prerequisites

- Node.js 18+ and npm
- Python 3.11+
- (Optional) Docker, only if you want PostgreSQL instead of SQLite

## Setup (VS Code / local machine)

### 1. Clone / unzip and open in VS Code

Unzip `PRISM_Workforce_Intelligence.zip` and open the folder in VS Code.

### 2. Configure environment variables

```bash
cp .env.example .env
```

The defaults work out of the box (SQLite, localhost CORS). No API keys are
required for Phase 0.

### 3. Run the backend

Open a terminal in VS Code (`` Ctrl+` ``):

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Verify it's alive:
- http://localhost:8000/ → `{"status": "running", ...}`
- http://localhost:8000/docs → interactive API docs
- http://localhost:8000/api/health/db → confirms the SQLite DB is reachable

### 4. Run the frontend

Open a **second** terminal:

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 — you should see the PRISM landing page with two
live status pills ("API: Online", "DB: Online") confirming the full stack
is connected. Click **Explore Workforce** (or press `Ctrl+K` / `Cmd+K`
anywhere and search) to open the interactive Workforce Map.

On first run, the backend automatically creates all tables and seeds the
database (this takes a few seconds) — you don't need a manual step. You
can force a fresh reseed at any time:

```bash
cd backend
python -m scripts.seed --force
```

### 5. Try the Phase 1 API

With the backend running, open http://localhost:8000/docs and try:

- `GET /api/skills?category=AI/ML` — list AI/ML skills
- `GET /api/skills/{id}` — full skill detail: timeline, related skills, occupations, industries
- `GET /api/skills/{id}/timeline` — 2022–2026 demand/growth/lifecycle history
- `GET /api/workforce/emerging` — computed emerging skills, ranked by YoY growth
- `GET /api/workforce/declining` — ghost/declining skills
- `GET /api/workforce/shifts` — structural shift detections (z-score based)
- `GET /api/workforce/bridges` — skills bridging 4+ industries
- `GET /api/workforce/capability-clusters` — Hidden Capability Discovery (community detection)
- `GET /api/workforce/combination-clusters` — Skill Combination Discovery
- `GET /api/workforce/wormholes` — Career Wormholes (occupation transition overlap)
- `GET /api/graph?node_id=skill:1&depth=1` — bounded graph neighborhood (find an id via `/api/search?q=...`)
- `GET /api/search?q=Generative AI` — search skills/occupations/industries
- `GET /api/routes?from={occupation_id}&to={occupation_id}` — Career Route Planner
- `GET /api/workforce/why/{skill_id}?year=2026` — "Why did this change?" breakdown
- `POST /api/talent-dna` — body `{"skills":[{"name":"Python","strength":0.8}]}`
- `GET /api/geography/locations?year=2026` / `GET /api/geography/{location_id}?year=2026`
- `GET /api/education` / `GET /api/education/{id}/gap-analysis`
- `GET /api/simulation/presets` — list Stress Test presets
- `POST /api/simulation` — body `{"tech_adoption":30,"automation":10,"skill_shortage":10}`
- `POST /api/simulation/preset/ai_adoption_surge` — run a named preset
- `GET /api/workforce/years` / `GET /api/workforce/snapshot?year=2024` — Time Machine data
- `GET /api/workforce/talent-gaps` — demand/growth vs. occupation-coverage heuristic
- `GET /api/workforce/why/{skill_id}?year=2026` — "Why did this change?" breakdown
- `GET /api/routes?from={occupation_id}&to={occupation_id}` — Career Route Planner (find ids via `/api/occupations`)

### (Optional) Run PostgreSQL instead of SQLite

```bash
docker compose up -d
```

Then in `.env`, set:
```
DATABASE_URL=postgresql+psycopg://prism_user:prism_password@localhost:5432/prism
```
Restart the backend.

## What works right now (Phase 0 through Phase 8)

**Phase 0:**
- Landing page with the PRISM hero, animated network backdrop, and branding
- Live backend + database connectivity check rendered in the header
- FastAPI backend with CORS, centralized error handling, `/health` and `/health/db`
- SQLAlchemy configured for SQLite (default) or PostgreSQL (via env var)

**Phase 1:**
- Full relational schema (14 tables) + seeded, internally-consistent 2022–2026 dataset
- A real analytics engine (`app/analytics/`) computing lifecycle stages, emerging/ghost
  skills, structural shifts, bridge skills, capability clusters, combination clusters,
  and career-transition overlap scores
- NetworkX-backed graph builder with bounded neighborhood expansion
- Documented API endpoints for all of the above

**Phase 2:**
- Full-screen, force-directed **Workforce Map** (`/explore`) built with React Flow +
  d3-force: zoom, pan, drag, click-to-expand, node-type filters, adjustable graph depth,
  minimap, and a Reset Graph control
- Live **search** (`SearchBar`) hitting `/api/search`, debounced, focuses the graph on
  the selected skill/occupation/industry
- **Command palette** (`Ctrl+K` / `Cmd+K`) with static navigation commands and live
  search-driven graph navigation
- **Node detail panel** with Overview / Timeline / Related / Evidence tabs
- Main app navigation bar (`AppNav`) used across all real and placeholder routes

**Phase 3:**
- **Workforce Time Machine**: draggable/clickable 2022–2026 timeline with Play
  animation. Moving the year re-fetches `/api/workforce/snapshot?year=` and
  actually restyles the Workforce Map (node size, color, growth badge) —
  it changes displayed intelligence, not just a decorative slider
- **Emerging Skills** (`/emerging`) and **Ghost Skills** (`/ghost-skills`) list
  pages, year-aware, enriched with occupations/industries, linking into the map
- **Skill Evolution Engine** additions in the node panel: overall % change,
  data-derived "first significant year," and the Time-Machine-selected year
  highlighted in the timeline

**Phase 4:**
- **Career Route Planner** (`/routes`): pick a current + target occupation,
  get multiple alternative routes (via `networkx.shortest_simple_paths` over
  the occupation-transition graph) with per-hop shared skills, missing
  capabilities, and industry context — routes are labeled "Route 1/2/3," never
  ranked as universally best
- **Career Wormholes** browser on the same page, from `/api/workforce/wormholes`
- **Structural Shift Detector** page (`/structural-shifts`) with a working
  **"Why did this change?"** modal — a transparent, data-derived contribution
  breakdown (related-skill momentum / industry breadth / occupation breadth),
  explicitly labeled as a heuristic signal split, not a causal claim
- **Workforce Radar** dashboard (`/radar`) — 5 live sections (Emerging,
  Declining, Talent Gap, Structural Shift, New Capability), each computed
  from the seeded data, each with an Evidence link
- App-wide **Evidence Mode** drawer (method, data window, parameters,
  confidence) usable from Structural Shifts and the Radar dashboard
- New backend analytics: `compute_talent_gaps` (demand/growth vs. occupation
  coverage) and `compute_structural_shift_explanation` ("Why" breakdown)

**Phase 5:**
- **Talent DNA** (`/talent-dna`): enter skills + self-rated strength, get a
  multi-dimensional category profile (radar-style bars), the nearest real
  occupations by weighted-overlap score (same method used for career
  transitions elsewhere — one consistent algorithm, not a bespoke formula),
  and nearby capability clusters — deliberately **not** a single resume score
- **Geographic Workforce Map** (`/insights` → Geography tab): per-location
  top skills/occupations/industries and synthetic average compensation from
  `job_postings`, plus skills that are specifically emerging *in that
  location* (cross-referenced against each skill's global lifecycle stage)
- **Education → Workforce pipeline** (`/insights` → Education tab):
  generic curriculum archetypes (never tied to a real institution) compared
  against the top-20 highest-demand skills for the latest year, showing
  covered vs. gap skills and a coverage ratio
- New backend analytics: `app/analytics/talent_dna.py`,
  `app/analytics/geography.py`, `app/analytics/education.py`

**Phase 6:**
- **Workforce Shock Simulator** (`/simulate`): three 0–100 scenario dials
  (Technology Adoption, Automation, Skill Shortage) propagate through a
  transparent, deterministic, documented category-sensitivity model
  (`app/analytics/simulation.py`) — skills → occupations → industries.
  Identical inputs always return identical outputs (results are hashed and
  cached in `simulation_results`, satisfying the reproducibility requirement)
- **🚀 Stress Test presets**: "AI Adoption +30%", "Automation +25%", "Cloud
  Talent Shortage", and "Sudden Demand Spike: AI Agents" — one click runs a
  full scenario via `POST /api/simulation/preset/{key}`
- Results surface **First Affected Capabilities**, **Bottleneck
  Capabilities** (high new demand + below-median existing supply),
  occupations under pressure / in demand, industries affected, and a
  **Workforce Mirror** (current vs. scenario average demand by category)
- Every result carries an explicit disclaimer that this is a scenario
  simulation, not a guaranteed forecast

**Phase 7:**
- **🚀 Demo Mode** (button on the landing page): a guided walkthrough —
  Search "Generative AI" → focus the graph → open a related skill (RAG) →
  auto-play the Time Machine 2022→2026 → Skill Emergence Detector → a real
  Bridge Skill → Career Wormholes → the Simulator — narrated by a live
  progress banner. Every step drives the same stores and API calls a user
  would trigger by hand; nothing is a canned screenshot or fake animation
- Landing page copy and status indicators brought in line with the current
  build (no more stale Phase 0 language)
- Cross-app consistency pass: navigation links, command palette entries,
  and API client methods verified against their backend routes

**Phase 8 (this checkpoint — production audit):**
- Cross-referenced every frontend `api.*` call against every backend route
  by name — all match; no dangling client calls to non-existent endpoints
- Fixed silent-failure bugs across `CareerRoutes.tsx` (route planner +
  wormhole browser), `Insights.tsx` (geography + education panels),
  `Simulator.tsx`, `StructuralShifts.tsx`, and `WhyModal.tsx`: these
  previously could hang on "Loading…" forever or throw an unhandled
  promise rejection if a request failed — they now show a real error
  message and recover cleanly
- Removed an unused, heavy dependency (`sentence-transformers`, which
  pulls in torch) from `backend/requirements.txt` — capability clustering
  is actually done via NetworkX graph community detection, not embeddings,
  so the dependency was dead weight
- Rewrote `docs/methodology.md` from a Phase-0 placeholder into an accurate
  description of what each analytical feature actually computes (lifecycle
  classification thresholds, capability-clustering method, route-planning
  algorithm, and the simulator's sensitivity model), including its
  limitations
- Corrected a misleading `.env.example` / `config.py` comment implying
  `ANTHROPIC_API_KEY` powers search — it's declared for a possible future
  natural-language layer but is not read by any current code path
- Verified: no placeholder routes outside the 404 handler, no hardcoded
  secrets, no TODO/FIXME markers, every Python file compiles, every
  frontend file's brackets balance

## What is *not* built yet

No feature routes are placeholders at this point; everything in the
navigation is implemented and cross-checked against a live backend route.
What remains is listed in [Limitations](#limitations) below — primarily,
an actual from-scratch `npm install` / `pip install` / run-through, since
this sandbox cannot reach the internet to perform one.

## Roadmap

| Phase | Scope |
|---|---|
| 0 ✅ | Project foundation, scaffolding, health check |
| 1 ✅ | Database schema, seeded 2022–2026 dataset, core analytics |
| 2 ✅ | Workforce Map (interactive graph), search, node detail panel, command palette |
| 3 ✅ | Time Machine, Skill Evolution Engine, Emerging/Ghost Skills UI |
| 4 ✅ | Hidden Capability Discovery, Bridges, Wormholes, Route Planner, Structural Shifts, Radar, Evidence Mode |
| 5 ✅ | Talent DNA, Geographic Map, Education pipeline |
| 6 ✅ | Workforce Shock Simulator, Workforce Mirror, Stress Test |
| 7 ✅ | Full integration polish, Demo Mode |
| 8 ✅ | Production audit, final ZIP |

## Limitations (through Phase 7)

- All workforce data is synthetic/seeded (clearly labeled in this README); it does not represent real-world statistics.
- The Workforce Map re-runs a client-side force layout on data changes rather than persisting node positions — large expansions may briefly re-settle.
- The node detail panel's Timeline/Related tabs are only populated for skill nodes so far; occupation/industry equivalents would need their own evidence views.
- The Career Route Planner only finds paths through occupations connected by a precomputed transition edge (top-3 highest-overlap per occupation) — a valid path may exist in the fuller graph but not surface if overlap was below the seeding threshold; this is stated in the UI via the route note rather than hidden.
- The "Why did this change?" breakdown is an explicit heuristic decomposition (related-skill momentum, industry breadth, occupation breadth), not a verified causal/experimental analysis — this is stated directly in the UI.
- The Workforce Shock Simulator's category-sensitivity coefficients (`app/analytics/simulation.py`) are illustrative and documented in code, not fitted to real labor-market data — every result also carries this disclaimer in the API response and UI.
- Demo Mode drives real navigation/API calls end-to-end, but does not click UI buttons on the user's behalf for the Simulator's final step (it navigates there and leaves the Stress Test click to the viewer) to keep the sequence simple and interruptible.
- The landing page's hero background is still a lightweight decorative SVG network (intentionally distinct from the real, data-driven Workforce Map at `/explore`).
- The in-app "About → Methodology / Data Sources" navigation items from the original spec are not built as pages; the full methodology write-up lives in [`docs/methodology.md`](docs/methodology.md) instead.
- Authentication is out of scope for this build; no login is required for any current or planned feature.
- **Not yet done:** a full Phase 8 production audit — running the actual `npm install` / `pip install` / `uvicorn` / `npm run dev` sequence from a clean checkout, a `npm run build` production bundle check, and a final line-by-line click-through. Everything has been statically syntax-checked (Python compiles cleanly; every frontend file's brackets balance) and cross-referenced (every frontend API call matches a real backend route) in this sandbox, which has no internet access to actually install dependencies — see the note at the top of this conversation.

## License / data note

Any dataset shipped in this project is either synthetic/seeded or clearly
labeled as demo data — it does not represent real-world statistics.
