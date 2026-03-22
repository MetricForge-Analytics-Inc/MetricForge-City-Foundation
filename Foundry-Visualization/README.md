# Foundry Visualization — Evidence Dashboards

## Overview

Evidence-powered markdown dashboards that query the local DuckDB database directly. Each page presents municipal data from the `city__local` schema produced by the SQLMesh transformation pipeline.

## Pages

| Page | Route | Description |
|---|---|---|
| City Data OS | `/` | Overview dashboard with KPIs across all domains |
| Infrastructure | `/infrastructure` | Road assets, conditions, and ward-level analysis |
| Development | `/development` | Building permits, construction values, housing trends |
| Water | `/water` | Water main materials, age distribution, condition |
| Governance | `/governance` | Data catalog and access tier documentation |

## Data Connection

Evidence connects directly to the local DuckDB file via the DuckDB connector. The connection is configured in `sources/City/connection.yaml`:

```yaml
type: duckdb
filename: ../db/metricforge.duckdb
```

SQL source queries in `sources/City/*.sql` run against the `city__local.*` views created by SQLMesh.

## Getting Started

### Prerequisites
- Node.js and npm
- Pipeline executed at least once (`python Foundry-Orchestration/City-Main.py`)

### Run locally

```bash
cd Foundry-Visualization
npm install
npm run sources
npm run dev
```

## Source Queries

| File | Description |
|---|---|
| `city_kpis.sql` | High-level KPIs across all domains |
| `cube_by_ward.sql` | Infrastructure metrics grouped by ward |
| `cube_permits_by_type.sql` | Permit counts by type |
| `cube_permits_by_ward.sql` | Permits aggregated by ward |
| `cube_road_condition.sql` | Road condition and classification analysis |
| `cube_water_by_material.sql` | Water main breakdown by pipe material |

## Learning More

- [Evidence Docs](https://docs.evidence.dev/)
- [Evidence GitHub](https://github.com/evidence-dev/evidence)
- [Evidence Home Page](https://www.evidence.dev)
