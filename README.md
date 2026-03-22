MetricForge-City-Foundation
FCI (Future Cities Initiative) Challenge - KPI Generation/City Data OS


# MetricForge City Foundation

Municipal data infrastructure platform — treating data as foundational city infrastructure, from extraction through visualization.

## Architecture

```
Prefect (Orchestration)
  │
  ├─► DLT (Extract)       ArcGIS Open Data / Municipal APIs → Local DuckDB
  │
  ├─► SQLMesh (Transform)  normalized → atomic → integration → details views
  │
  ├─► Cube.js (Semantic)   YAML cubes over DuckDB views (local Docker)
  │
  └─► Evidence (Visualize) Markdown dashboards querying DuckDB views directly
```

## Directory Layout

| Folder | Purpose |
|---|---|
| `Foundry-Orchestration/` | Prefect flow that runs extract → transform → cube refresh |
| `Foundry-Pipelines/Infrastructure/OpenData-Kitchener/Data-Extract/` | DLT pipeline pulling Kitchener Open Data (ArcGIS Hub) into local DuckDB |
| `Foundry-Pipelines/Infrastructure/OpenData-Kitchener/Data-Pipeline/` | SQLMesh models, macros, audits, tests for municipal data |
| `Foundry-Semantic-Cubes/` | Cube.js Docker setup and YAML cube definitions (infrastructure, permits, water, wards) |
| `Foundry-Visualization/` | Evidence dashboards and source queries (direct DuckDB connection) |
| `db/` | Local DuckDB database file (`metricforge.duckdb`) |
| `Documentation/` | Architecture diagrams, CI/CD flow documentation |
| `.sqlmesh/` | SQLMesh workspace config |

## Quick Start

### Prerequisites

- **Python 3.11+** with pip
- **Docker Desktop** (for Cube.js semantic layer)

### 1. Install Python dependencies

```bash
pip install -r Foundry-Orchestration/requirements.txt
pip install -r Foundry-Pipelines/Infrastructure/OpenData-Kitchener/Data-Extract/requirements.txt
```

### 2. Run the full pipeline

```bash
python Foundry-Orchestration/City-Main.py
```

This runs three tasks in sequence:
1. **Extract** — DLT pulls 11 datasets from Kitchener ArcGIS Open Data into `db/metricforge.duckdb`
2. **Transform** — SQLMesh applies 10 models (atomic → integration → details views)
3. **Cube Refresh** — Pings the local Cube.js instance to reload (best-effort, skips if not running)

### 3. Start the semantic layer (Cube.js)

```bash
cd Foundry-Semantic-Cubes
docker compose up -d
```

After startup:
- **Playground UI**: http://localhost:4000
- **REST API**: http://localhost:4000/cubejs-api/v1
- **SQL API**: `localhost:15432` (Postgres wire protocol, user: `cube`)

### 4. Start Evidence dashboards

```bash
cd Foundry-Visualization
npm install
npm run dev
```

### Run each pipeline step manually

```bash
# Extract (Kitchener Open Data → local DuckDB)
python Foundry-Pipelines/Infrastructure/OpenData-Kitchener/Data-Extract/opendata_pipeline.py

# Transform (SQLMesh)
cd Foundry-Pipelines/Infrastructure/OpenData-Kitchener/Data-Pipeline
sqlmesh plan local --auto-apply --no-prompts

# Visualize (Evidence)
cd Foundry-Visualization && npm run dev
```

## Key Design Decisions

- **Local DuckDB** — All data lives in a single local DuckDB file (`db/metricforge.duckdb`). No cloud connections required. The DLT pipeline writes raw data, SQLMesh creates transformed views, and both Cube.js and Evidence read from the same file.
- **Time attribution** — Each Cube is bound to a specific datetime dimension so date filters always answer the right question. Infrastructure cubes use `record_time` (last edit/creation), permit cubes use `issued_date` or `application_date`.
- **Table + View pairs** — SQLMesh models come in pairs: an `INCREMENTAL_BY_TIME_RANGE` table for performance and a `VIEW` for always-fresh reads. The Cube layer points at the view.
- **Ward as common integration key** — Geographic ward boundaries serve as the primary cross-departmental join key, enabling infrastructure × planning × utilities analysis without exposing individual-level data.
- **Federated by design** — Each department's data lives in its own atomic model. Integration models perform the cross-departmental joins, preserving departmental autonomy while enabling holistic views.
- **Privacy-first** — PII-containing datasets (addresses, property records) are flagged in the data catalog. Analytical views aggregate to ward/neighbourhood level by default.

## Technology Stack

| Layer | Tool | Version |
|---|---|---|
| Orchestration | Prefect | 3.x |
| Extraction | DLT (Data Load Tool) | 1.8.x |
| OLAP Engine | DuckDB (local) | 1.x |
| Transformation | SQLMesh | 0.174.x |
| Semantic Layer | Cube.js (Docker) | 1.3.x |
| Visualization | Evidence | Latest |


## Problem Statement and Information

Problem Statement: Build the Blueprint for Municipal Data Infrastructure
Lead: Linnea Scian Linnea.Scian@kitchener.ca


The Challenge
Cities invest billions in roads, water systems, and public transit because these are recognized as foundational infrastructure—essential assets that enable everything else to function. Yet there's another form of infrastructure that remains largely invisible and underinvested: municipal data.

Just as water infrastructure delivers clean water to every tap, data infrastructure should deliver reliable information to every decision-maker—from engineers planning road repairs, to planners analyzing development patterns, to public health officials tracking disease outbreaks.

But unlike water or roads, municipalities don't treat data as infrastructure. Instead, data is fragmented across departments, trapped in incompatible systems, duplicated inefficiently, and protected inconsistently.

Engineering has its databases. Planning has separate systems and databases. Public health maintains its own records. Economic development, transit, bylaw enforcement, parks, and social services all operate in silos. When these departments need to collaborate or make cross-cutting decisions, they face data chaos: incompatible formats, inconsistent definitions, privacy concerns, and no shared architecture.

The result? Infrastructure projects that could benefit from planning data don't get it. Public health initiatives that need engineering data can't access it. Economic development strategies that should incorporate transit and housing data proceed without comprehensive information. Every department operates with partial visibility. A current example of the importance of this problem is the pause on housing development because of a water capacity in our Region. This is partly due to the Region not accounting for development growth for infill areas (they were only counting subdivisions, even though 50% of residential building permits in 2024 were for infill development)! 

That's where you come in.

Your Task:
Design and prototype a municipal data infrastructure architecture that treats data as a foundational asset—enabling secure, privacy-preserving integration across engineering, planning, public health, and other municipal departments.

Your solution should address:
Unified data architecture: Design a technical framework that allows different departments to share data while maintaining departmental autonomy and ensuring data integrity. This includes data schemas, integration patterns, APIs, and governance structures that enable cross-departmental analysis without forcing everyone into a single monolithic system.
Privacy and confidentiality by design: Build mechanisms that protect sensitive information while enabling legitimate use. This includes role-based access controls, data anonymization and aggregation tools, audit logging, and clear protocols for handling personally identifiable information (PII) and confidential records.
Interoperability standards: Create or adopt common data standards that let engineering data integrate with planning data, health data connect with social services, and transit information link with land use patterns—without requiring every department to overhaul their existing systems.
Data governance framework: Define who owns what data, who can access it, how quality is maintained, and how conflicts are resolved. Include policies for data sharing, retention, accuracy verification, and stewardship responsibilities.
Practical implementation pathway: Show how a municipality could actually build this infrastructure incrementally—starting with pilot integrations between two departments and scaling toward comprehensive data infrastructure. Consider technical feasibility, budget constraints, and change management.

Consider including (optional):
Data quality dashboards, automated validation systems, cross-departmental data dictionaries, example APIs for common integration use cases, privacy impact assessment templates, citizen-facing data portals, real-time data pipelines, machine learning-ready data lakes, or demonstration use cases showing tangible benefits of integration.

Why Current Approaches Fail
Municipalities struggle with data infrastructure because:

Siloed systems were built independently: Each department adopted tools based on their specific needs without considering cross-departmental integration. Engineering uses GIS platforms, planning uses development tracking software, public health uses epidemiological databases—all incompatible.
Privacy concerns prevent sharing: Departments are (rightfully) cautious about data breaches and privacy violations, but lack technical mechanisms to share data safely. Without proper infrastructure, the default response is "don't share"—even when integration would create huge public value.
No one owns horizontal integration: Each department owns vertical systems (planning owns planning data), but no one is responsible for horizontal infrastructure that connects across departments. IT departments maintain systems but don't drive data strategy.
Budget cycles reward visible projects: Fixing a road generates ribbon-cutting ceremonies. Building data infrastructure is invisible to citizens, making it difficult to secure funding even though the ROI can be enormous.
Lack of technical blueprints: Even municipalities that recognize the need don't know how to build data infrastructure. What architecture patterns work? What standards should they adopt? How do you handle privacy? Where do you start?

That's why your solution must be both technically rigorous and practically implementable—providing municipalities with a concrete blueprint they can follow to transform data from scattered departmental assets into true foundational infrastructure.

Key Design Principles
Privacy-First: Security and confidentiality aren't obstacles to overcome—they're core requirements. Build privacy protection into the architecture from day one.
Federated by Default: Don't force departments into one system. Enable integration while preserving autonomy and existing workflows.
Incrementally Buildable: Municipalities can't rip and replace everything. Design for gradual implementation with immediate value at each step.
Standards-Based: Use open standards and proven patterns rather than proprietary vendor lock-in. Make it possible to evolve and adapt.

Technical Considerations
Data catalog and discovery: How do departments find out what data exists elsewhere? What metadata standards enable discoverability?
Access control architecture: Role-based access, attribute-based access, or something more sophisticated? How granular? How audited?
Integration patterns: APIs, data lakes, event streaming, federated queries? What works for which use cases?
Data quality assurance: Validation rules, quality metrics, lineage tracking, and accountability mechanisms.
Geographic integration: Most municipal data has spatial components. How does location become a common integration key while respecting privacy?
Temporal consistency: Departments work on different time scales (real-time traffic vs. annual planning cycles). How do you harmonize temporal data?
Legacy system integration: Many departments run 20-year-old systems that can't be replaced. How do you integrate them anyway?

Example Use Cases to Enable
Your infrastructure should make these cross-departmental scenarios possible:
Coordinated infrastructure planning: Engineering plans road reconstruction that incorporates planning's development forecasts, transit's route data, and utilities' underground asset locations—all while respecting property-level confidentiality.
Public health surveillance: Health officials detect a disease cluster and can (with proper privacy controls) access relevant environmental data, building permits, water quality records, and demographic information to investigate causes.
Climate adaptation: Climate planners combine flood risk models (engineering), vulnerable population data (social services), critical infrastructure (utilities), and development patterns (planning) to prioritize adaptation investments.
Housing affordability analysis: Planners analyze how zoning policies, transit access, infrastructure capacity, and development activity interact to affect housing costs—using data from six different departments.
Service optimization: Transit planners use anonymized travel patterns, employment locations, housing development data, and service usage statistics to redesign routes and schedules.

Impact
By treating data as foundational infrastructure, municipalities could:
Make evidence-based decisions that incorporate comprehensive information rather than departmental fragments
Identify cross-cutting problems and opportunities that are invisible when departments work in isolation
Reduce duplication and inefficiency from maintaining redundant datasets across departments
Enable innovation by allowing departments and external partners to build on reliable, accessible data
Improve accountability through better tracking of outcomes and performance across municipal functions
Serve residents more effectively by understanding their needs holistically rather than through departmental lenses

Just as investing in water infrastructure in the 1800s transformed public health and enabled urban growth, investing in data infrastructure today could transform municipal decision-making and unlock new forms of public value.

Your challenge is to design the blueprint that makes this transformation possible—showing municipalities not just why data infrastructure matters, but how to build it.

## More Info
 - https://docs.google.com/spreadsheets/d/1i1MSefZNf1u7hEU3rZOfjhiCzUod8OcDfJP7045yxkY/edit?gid=0#gid=0
 - https://open-kitchenergis.opendata.arcgis.com/pages/open-data-listing
 - https://docs.google.com/document/d/1-oPEGOWrgWSYgQgUzZe9uYGK0UyK1Ai1/edit
