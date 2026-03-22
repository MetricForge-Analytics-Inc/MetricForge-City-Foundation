MetricForge-City-Foundation
FCI (Future Cities Initiative) Challenge - KPI Generation/City Data OS


# MetricForge Foundry

Data platform for MetricForge analytics — extraction through visualization.

## Architecture

```
Prefect (Orchestration)
  │
  ├─► DLT (Extract)       Zendesk/Salesforce/.../Source API → MotherDuck (normalized extract)
  │
  ├─► SQLMesh (Transform)  normalized → atomic → integration → details views
  │
  ├─► Cube (Semantic)      YAML cubes with time-attributed measures
  │
  └─► Evidence (Visualize) Markdown dashboards via Cube's Postgres API
```

## Directory Layout

| Folder | Purpose |
|---|---|
| `Foundry-Orchestration/` | Prefect flow that runs extract → transform |
| `Foundry-Pipelines/Support/zendesk/Data-Extract/` | DLT pipeline pulling Zendesk Support into MotherDuck |
| `Foundry-Pipelines/Support/zendesk/Data-Pipeline/` | SQLMesh models, macros, audits, tests |
| `Foundry-Semantic-Cubes/Support/` | Cube.js YAML definitions (extends chain) |
| `Foundry-Visualization/` | Evidence dashboards and source queries |
| `.sqlmesh/` | SQLMesh gateway config (MotherDuck + Supabase state) |
| `.devcontainer/` | Codespace setup — installs all Python/Node deps |
| `.githooks/` | `prepare-commit-msg` prefixes commits with branch name |

## Quick Start

1. **Open in Codespace** — `postCreateCommand.sh` installs everything automatically.
2. **Set environment variables** — `MOTHERDUCK_CODESPACE_TOKEN`, `POSTGRES_HOST/PORT/USER/PASSWORD/DATABASE`, `ZENDESK_*`.
3. **Run the pipeline**:

```bash
python Foundry-Orchestration/Support-Main.py
```

Or run each step manually:

```bash
# Extract
python Foundry-Pipelines/Support/zendesk/Data-Extract/zendesk_pipeline.py

# Transform
sqlmesh -p Foundry-Pipelines/Support/zendesk/Data-Extract \
        -p Foundry-Pipelines/Support/zendesk/Data-Pipeline \
        plan prod --auto-apply --no-prompts

# Visualize
cd Foundry-Visualization && npm run dev
```

## Key Design Decisions

- **Time attribution** — Each Cube is bound to a specific datetime dimension so date filters always answer the right question. See [Foundry-Semantic-Cubes/README.md](Foundry-Semantic-Cubes/README.md).
- **Table + View pairs** — SQLMesh models come in pairs: an `INCREMENTAL_BY_TIME_RANGE` table for performance and a `VIEW` for always-fresh reads. The Cube layer points at the view.
- **Virtual environments** — SQLMesh uses virtual data environments so `prod` is a zero-copy promotion of validated snapshots.
