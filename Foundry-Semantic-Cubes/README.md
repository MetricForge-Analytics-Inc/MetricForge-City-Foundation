# Foundry Semantic Cubes — City

## Overview

Semantic cubes define the **measures** (metrics) and **dimensions** (attributes) that sit between raw data and the visualization layer. Each cube YAML file in `City/` maps to a Cube.js cube definition that queries the `city__local.*` SQLMesh views in DuckDB.

The cubes expose:
- **Dimensions:** Categorical or identifier columns (ward, road_name, pipe_material, permit_type, etc.)
- **Time dimensions:** Temporal columns bound to the cube for date-range filtering (`record_time`)
- **Measures:** Pre-defined aggregations (counts, sums, averages)

## Running Cube Locally

Cube.js (Cube Dev) is **fully open source** (Apache 2.0). You can run it locally via Docker:

```bash
cd Foundry-Semantic-Cubes
docker compose up        # foreground
docker compose up -d     # background (detached)
```

After startup:

| Endpoint | URL | Description |
|---|---|---|
| **Playground** | http://localhost:4000 | Interactive query builder UI |
| **REST API** | http://localhost:4000/cubejs-api/v1 | JSON API for programmatic access |
| **SQL API** | `localhost:15432` | Postgres-wire protocol (user: `cube`) |

**Prerequisites:**
- Docker Desktop running
- Pipeline executed at least once (`python Foundry-Orchestration/City-Main.py`)

The DuckDB file is mounted into the container — the pipeline writes data, Cube reads it.

## Why Time Attribution Matters

In Cube.js, when a user applies a date filter (e.g. "last 30 days"), that filter is applied to the cube's **time dimension**. All municipal cubes use `record_time` (the latest edit or creation timestamp from the source system) as their primary time dimension.

| Question | Cube | Why |
|---|---|---|
| "How many road segments were updated last month?" | `infrastructure_assets` | You want records whose **last edit** falls in the range |
| "How many permits were issued this quarter?" | `development_permits` | You want permits whose **issued/application date** falls in the range |
| "What's the average pipe age for mains updated recently?" | `water_infrastructure` | You want water main records recently refreshed |

## Cube Definitions

### 1. `infrastructure_assets` — Cross-Departmental Infrastructure

**Source:** `city__local.infrastructure_integration_view`
**Time dimension:** `record_time`

Joins roads, ward boundaries, and aggregated water main statistics to create a cross-departmental infrastructure view.

| Measure | Type | Description |
|---|---|---|
| `total_road_segments` | count | Total number of road segment records |
| `total_water_mains_in_ward` | max | Water mains count (pre-aggregated) |
| `distinct_pipe_materials` | max | Number of distinct pipe materials in the water network |
| `ward_population` | max | Ward population from boundary data |
| `ward_households` | max | Number of residential households in the ward |

**Key dimensions:** `road_name`, `road_classification`, `surface_type`, `category`, `subcategory`, `number_of_lanes`, `speed_limit_kmh`, `pavement_width_m`, `road_ownership`, `road_status`, `ward_id`, `ward_name`, `councillor`

---

### 2. `development_permits` — Housing & Development

**Source:** `city__local.development_details_view`
**Time dimension:** `record_time`

Building permits with construction values and unit tracking. Enables the **housing-vs-infrastructure capacity analysis** that directly addresses the problem statement (housing paused due to water capacity).

| Measure | Type | Description |
|---|---|---|
| `total_permits` | count | Total building permit count |
| `total_construction_value` | sum | Sum of construction values |
| `avg_construction_value` | avg | Average permit construction value |
| `total_units_created` | sum | Total housing units created |
| `total_units` | sum | Total units across permits |
| `residential_permits` | sum | Count of residential-type permits |
| `commercial_permits` | sum | Count of commercial-type permits |
| `completed_permits` | sum | Count of completed permits |
| `year_permits_count` | max | Total permits in the same issue year (pre-aggregated) |
| `year_construction_value` | max | Total construction value in the same issue year |
| `year_units_created` | max | Total units created in the same issue year |

**Key dimensions:** `permit_number`, `permit_type`, `permit_status`, `work_type`, `sub_work_type`, `permit_description`, `address`, `issue_year`, `application_date`, `issued_date`

---

### 3. `water_infrastructure` — Water Distribution Network

**Source:** `city__local.water_mains_atomic_view`
**Time dimension:** `record_time`

Water distribution main pipes — age analysis, material breakdown, condition scoring, and criticality ratings.

| Measure | Type | Description |
|---|---|---|
| `total_mains` | count | Total water main count |
| `avg_pipe_size` | avg | Average pipe size |
| `avg_condition_score` | avg | Average condition score |
| `avg_criticality` | avg | Average criticality rating |
| `oldest_install_date` | min | Earliest install date |
| `newest_install_date` | max | Most recent install date |
| `avg_pipe_age_years` | avg | Average age of water mains in years |

**Key dimensions:** `pipe_material`, `pipe_status`, `pressure_zone`, `ownership`, `category`, `lined`, `pipe_size`, `condition_score`, `criticality`, `install_date`

---

### 4. `ward_overview` — Geographic Governance

**Source:** `city__local.boundaries_atomic_view`
**Time dimension:** `record_time`

Ward-level demographics and governance. Serves as the **geographic join key** for cross-departmental analysis.

| Measure | Type | Description |
|---|---|---|
| `total_wards` | count | Number of wards |
| `total_population` | sum | Total city population |
| `avg_population_per_ward` | avg | Average population per ward |
| `total_residential_households` | sum | Total residential households |
| `total_voters` | sum | Total registered voters |
| `avg_voters_per_ward` | avg | Average voters per ward |

**Key dimensions:** `ward_number`, `ward_name`, `councillor`

---

## Design Principles

### Federated Architecture
Each department's data has its own atomic model. Integration happens at the SQLMesh layer through ward-based joins rather than forcing everything into one table. This preserves departmental autonomy while enabling cross-cutting analysis.

### Privacy by Design
- Address-level data stays in atomic models; cubes expose ward-level aggregates by default
- PII-containing datasets are flagged in the data catalog (see `/governance` dashboard)
- Role-based access tiers (Public, Internal, Restricted) control who can query at which granularity

### Incremental Buildability
New departments can be added by:
1. Adding a dataset entry in `DATASET_CATALOG` (extraction)
2. Creating an atomic macro + model pair (transformation)
3. Adding a Cube YAML definition (semantic)
4. Adding source queries and a dashboard page (visualization)

No existing code needs to change — the architecture is designed for incremental extension.

## Future Cubes

As more municipal data sources are integrated, additional cubes can be created:

| Potential Cube | Department | Key Measures |
|---|---|---|
| `transit_service` | Transit (GRT) | Route coverage, stop density, service frequency |
| `parks_greenspace` | Parks & Rec | Park area per capita, tree canopy coverage |
| `sewer_infrastructure` | Utilities | Sewer age, material, capacity vs. development |
| `zoning_capacity` | Planning | Permitted density vs. actual, buildable land |
| `service_requests` | 311 / Bylaw | Request volume, resolution time, spatial patterns |
