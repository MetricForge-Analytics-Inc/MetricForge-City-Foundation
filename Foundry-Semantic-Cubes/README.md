# Foundry Semantic Cubes — City

## Overview

Semantic cubes define the **measures** (metrics) and **dimensions** (attributes) that sit between raw data and the visualization layer. Each cube YAML file in `City/` maps to a Cube.js cube definition that queries the `city.*` SQLMesh views.

The cubes expose:
- **Dimensions:** Categorical or identifier columns (ward, road_name, pipe_material, permit_type, etc.)
- **Time dimensions:** Temporal columns bound to the cube for date-range filtering (`record_time`)
- **Measures:** Pre-defined aggregations (counts, sums, averages) that Evidence dashboards query via the `MEASURE()` SQL macro

## Why Time Attribution Matters

In Cube.js, when a user applies a date filter (e.g. "last 30 days"), that filter is applied to the cube's **time dimension**. All municipal cubes use `record_time` (the latest edit or creation timestamp from the source system) as their primary time dimension.

| Question | Cube | Why |
|---|---|---|
| "How many road segments were updated last month?" | `infrastructure_assets` | You want records whose **last edit** falls in the range |
| "How many permits were issued this quarter?" | `development_permits` | You want permits whose **issued/application date** falls in the range |
| "What's the average pipe age for mains updated recently?" | `water_infrastructure` | You want water main records recently refreshed |

## Cube Definitions

### 1. `infrastructure_assets` — Cross-Departmental Infrastructure

**Source:** `Foundry.city.infrastructure_integration_view`
**Time dimension:** `record_time`

Joins roads, ward boundaries, and aggregated water main statistics to create a cross-departmental infrastructure view.

| Measure | Type | Description |
|---|---|---|
| `total_road_segments` | count | Total number of road segment records |
| `total_road_length_km` | sum | Total road network length in kilometres |
| `avg_road_length_m` | avg | Average segment length in metres |
| `total_water_mains_in_ward` | max | Water main count in the road's ward (pre-aggregated) |
| `oldest_water_infrastructure_year` | min | Oldest water main install year in the ward |
| `total_water_network_km` | max | Total water pipe length in the ward (km) |
| `ward_population` | max | Ward population from boundary data |

**Key dimensions:** `road_name`, `road_classification`, `surface_type`, `surface_condition`, `number_of_lanes`, `speed_limit_kmh`, `road_ownership`, `maintenance_responsibility`, `ward`, `ward_name`, `councillor`

---

### 2. `development_permits` — Housing & Development

**Source:** `Foundry.city.development_details_view`
**Time dimension:** `record_time`

Building permits enriched with ward demographics and infrastructure capacity metrics. Enables the **housing-vs-infrastructure capacity analysis** that directly addresses the problem statement (housing paused due to water capacity).

| Measure | Type | Description |
|---|---|---|
| `total_permits` | count | Total building permit count |
| `total_estimated_value` | sum | Sum of estimated permit values |
| `avg_estimated_value` | avg | Average permit value |
| `total_actual_value` | sum | Sum of actual values (where reported) |
| `residential_permits` | sum | Count of residential-type permits |
| `commercial_permits` | sum | Count of commercial-type permits |
| `completed_permits` | sum | Count of completed permits |
| `ward_population` | max | Population in the permit's ward |
| `ward_water_mains` | max | Water main count — infrastructure capacity proxy |
| `permits_per_ward` | max | Total permits in the same ward |
| `development_intensity` | max | Total estimated value of all permits in the ward |

**Key dimensions:** `permit_number`, `permit_type`, `permit_status`, `work_type`, `address`, `ward`, `ward_name`, `neighbourhood`, `councillor`, `application_date`, `issued_date`, `completed_date`

---

### 3. `water_infrastructure` — Water Distribution Network

**Source:** `Foundry.city.water_mains_atomic_view`
**Time dimension:** `record_time`

Water distribution main pipes — age analysis, material breakdown, and capacity indicators by ward.

| Measure | Type | Description |
|---|---|---|
| `total_mains` | count | Total water main count |
| `total_length_km` | sum | Total network length (km) |
| `avg_diameter_mm` | avg | Average pipe diameter (mm) |
| `oldest_install_year` | min | Earliest install year |
| `newest_install_year` | max | Most recent install year |
| `avg_pipe_age_years` | avg | Average age of water mains in years |

**Key dimensions:** `pipe_material`, `pipe_status`, `pressure_zone`, `ownership`, `ward`, `install_year`, `diameter_mm`

---

### 4. `ward_overview` — Geographic Governance

**Source:** `Foundry.city.boundaries_atomic_view`
**Time dimension:** `record_time`

Ward-level demographics and governance. Serves as the **geographic join key** for cross-departmental analysis.

| Measure | Type | Description |
|---|---|---|
| `total_wards` | count | Number of wards |
| `total_population` | sum | Total city population |
| `total_area_sq_km` | sum | Total area (km²) |
| `avg_population_per_ward` | avg | Average population per ward |
| `population_density_per_sq_km` | avg | Average population density |

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
