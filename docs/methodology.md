# PRISM Methodology

This document explains how PRISM's data is generated and how each
analytical feature actually works — the code these sections describe
lives in `backend/app/data/` and `backend/app/analytics/`.

## 1. Data Acquisition

PRISM ships with a **seeded, internally-consistent synthetic dataset**
covering 2022–2026 (`backend/app/data/catalogs.py` + `seed_generator.py`):
114 skills, 55 occupations, 22 industries, 15 locations, and 10 generic
education-program archetypes. This is clearly labeled as synthetic
throughout the UI and README — it demonstrates the platform's mechanics,
not real labor-market statistics. No real institutions, companies, or
individuals are named or evaluated.

## 2. Data Preparation

Base entities (skills, occupations, industries, locations, education) are
inserted first, followed by their relationships (`occupation_skills`,
`industry_skills`). Skill demand curves are generated per skill using one
of six lifecycle **archetypes** (emerging, growing, established,
transforming, declining, ghost), each with its own start range, YoY growth
range, and noise band — see `ARCHETYPE_CURVES` in `seed_generator.py`.
Randomness is seeded (`random.seed(42)`) so a fresh `--force` reseed
reproduces the same dataset.

## 3. Skill Extraction & Capability Clustering

**Hidden Capability Discovery** and the skill-relationship graph are built
from **structural co-occurrence**, not text/embedding extraction: skills
that appear together in the same occupation's core skill set accumulate a
co-occurrence weight (`_insert_skill_relationships`), and **greedy
modularity community detection** (NetworkX) is run over the resulting
skill-skill graph to surface capability clusters
(`compute_capability_clusters` in `app/analytics/signals.py`). This is a
graph-structural method, not an NLP/embedding pipeline — an
embeddings-based extension (e.g. clustering free-text job-posting
descriptions with sentence embeddings) is a natural next step but is not
implemented in this build.

## 4. Graph Construction

`app/graph/graph_metrics.py` builds an in-memory NetworkX graph from the
relational tables on each request (skills, occupations, and industries as
nodes; `occupation_skill`, `skill_skill`, and `industry_skill` edges).
Rebuilding per-request keeps the relational tables as the single source of
truth; at this dataset's scale (hundreds of nodes) this is fast enough to
do live rather than caching a second copy of the graph.

## 5. Temporal Analysis

Each skill's lifecycle stage per year is **classified from its own
numbers** (`app/analytics/lifecycle.py`), not copied from the seed
archetype: demand level and year-over-year growth rate are compared
against fixed thresholds (e.g. demand < 15 → Ghost, growth ≥ 35% →
Emerging). **Structural shifts** are flagged when a skill's latest growth
rate deviates from its own historical mean by more than 1.8 standard
deviations *and* by at least 15 percentage points — a simple change-point
heuristic appropriate for a 5-point series, not a formal statistical test.

## 6. Career Transitions & Route Planning

**Career Wormholes** and the **Career Route Planner** both use
**weighted Jaccard similarity** between occupations' skill-weight
profiles: shared skill weight ÷ union skill weight. Wormholes keep only
the top-3 highest-overlap transitions per occupation (to surface
genuinely non-obvious pairs); the Route Planner computes overlap against
*all* occupation pairs on demand, so a valid path can exist even if it
didn't make a given occupation's top-3 list.

## 7. Simulation

The **Workforce Shock Simulator** (`app/analytics/simulation.py`) is a
**deterministic, rule-based propagation model**: three 0–100 dials
(technology adoption, automation, skill shortage) are multiplied by
documented per-category sensitivity coefficients to produce a demand
delta for every skill, which is then propagated to occupations and
industries via their existing skill weights. It is explicitly a
**scenario simulation, not a predictive forecast** — every API response
and UI surface carries this disclaimer. Identical inputs always produce
identical outputs (enforced via an input hash cached in
`simulation_results`).

## 8. Limitations

- All figures are derived from the seeded synthetic dataset described
  above, not real job-posting or labor-market data.
- Capability clustering is graph-structural (co-occurrence + community
  detection), not text/embedding-based.
- Structural shift detection and lifecycle classification use fixed,
  documented thresholds rather than fitted statistical models.
- The simulator's sensitivity coefficients are illustrative and
  hand-authored, not calibrated against real economic data.
- Dataset coverage is intentionally broad-but-shallow (114 skills, 55
  occupations); niche skills or occupations outside this seed catalog
  are not represented.
