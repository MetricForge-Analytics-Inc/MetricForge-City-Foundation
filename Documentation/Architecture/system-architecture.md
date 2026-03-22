# MetricForge City Foundation — System Architecture

## High-Level Overview

```mermaid
%%{init: {'theme': 'dark', 'themeVariables': {'mainBkg': 'transparent', 'nodeBorder': '#555', 'clusterBkg': 'transparent', 'clusterBorder': '#555'}}}%%
flowchart LR
    classDef input fill:none,color:#e0e0e0,stroke:#6ba3d6,stroke-width:2.5px
    classDef process fill:none,color:#e0e0e0,stroke:#d4a24e,stroke-width:2.5px
    classDef data fill:none,color:#e0e0e0,stroke:#6db89e,stroke-width:2.5px
    classDef config fill:none,color:#e0e0e0,stroke:#d4797a,stroke-width:2.5px
    classDef db fill:none,color:#e0e0e0,stroke:#9b8ab8,stroke-width:2.5px
    classDef portal fill:none,color:#e0e0e0,stroke:#c084fc,stroke-width:2.5px

    subgraph SOURCES ["Municipal Data Sources"]
        direction TB
        S1[/"ArcGIS Open Data<br/>Kitchener Hub"/]:::input
        S2[/"Engineering Dept<br/>Roads, Bridges, Sewers"/]:::input
        S3[/"Planning Dept<br/>Permits, Zoning"/]:::input
        S4[/"Utilities<br/>Water, Sanitary, Storm"/]:::input
        S5[/"Transit (GRT)<br/>Routes, Stops"/]:::input
        S6[/"Parks & Rec<br/>Parks, Trees"/]:::input
    end

    subgraph PIPELINE ["City Data Pipeline"]
        direction TB
        subgraph EXTRACT ["Extract (DLT)"]
            DLT(["opendata_pipeline.py<br/>ArcGIS REST API → Local DuckDB"]):::process
        end
        subgraph TRANSFORM ["Transform (SQLMesh)"]
            direction TB
            ATOMIC(["Atomic Models<br/>roads, water_mains, permits, boundaries"]):::process
            INTEG(["Integration Models<br/>infrastructure_integration<br/>development_details"]):::process
            ATOMIC --> INTEG
        end
        subgraph SEMANTIC ["Semantic (Cube.js)"]
            direction TB
            C1["infrastructure_assets"]:::data
            C2["development_permits"]:::data
            C3["water_infrastructure"]:::data
            C4["ward_overview"]:::data
        end
        DLT --> ATOMIC
        INTEG --> C1
        INTEG --> C2
        INTEG --> C3
        INTEG --> C4
    end

    subgraph VIZ ["Visualization (Evidence)"]
        direction TB
        D1["City Data OS<br/>Overview Dashboard"]:::portal
        D2["Infrastructure Assets"]:::portal
        D3["Development & Housing"]:::portal
        D4["Water Systems"]:::portal
        D5["Data Governance"]:::portal
    end

    SOURCES --> DLT
    C1 --> D1
    C1 --> D2
    C2 --> D1
    C2 --> D3
    C3 --> D4
    C4 --> D1
```

---

## Step-by-Step Pipeline Details

### Step 1 — Orchestration (Prefect)

```mermaid
%%{init: {'theme': 'dark', 'themeVariables': {'mainBkg': 'transparent', 'nodeBorder': '#555', 'clusterBkg': 'transparent', 'clusterBorder': '#555'}}}%%
flowchart TB
    classDef process fill:none,color:#e0e0e0,stroke:#d4a24e,stroke-width:2.5px
    classDef config fill:none,color:#e0e0e0,stroke:#d4797a,stroke-width:2.5px

    FLOW["City-Main.py<br/>@flow(name='city-pipeline')"]:::process
    T1(["@task: extract<br/>Runs opendata_pipeline.py"]):::process
    T2(["@task: transform<br/>Runs sqlmesh plan local"]):::process
    T3(["@task: cube-refresh<br/>Pings Cube.js /meta"]):::process

    FLOW --> T1 --> T2 --> T3

    T1 -->|subprocess call| EXTRACT["opendata_pipeline.py<br/>DLT → Local DuckDB"]:::process
    T2 -->|subprocess call| SQLMESH["sqlmesh plan local<br/>--auto-apply --no-prompts"]:::process
    T3 -->|HTTP GET| CUBE["Cube.js REST API<br/>localhost:4000 (best-effort)"]:::process
```

The orchestrator (`City-Main.py`) is parameterised by `--theme` and `--site`, defaulting to `Infrastructure` / `OpenData-Kitchener`. This enables adding new municipal pipelines (e.g. `PublicHealth` / `Region-Waterloo`) without modifying orchestration code. The third task (`cube-refresh`) is best-effort — if Cube.js is not running, the pipeline still completes successfully.

### Step 2 — Extraction (DLT)

```mermaid
%%{init: {'theme': 'dark', 'themeVariables': {'mainBkg': 'transparent', 'nodeBorder': '#555', 'clusterBkg': 'transparent', 'clusterBorder': '#555'}}}%%
flowchart TB
    classDef source fill:none,color:#e0e0e0,stroke:#6ba3d6,stroke-width:2.5px
    classDef process fill:none,color:#e0e0e0,stroke:#d4a24e,stroke-width:2.5px
    classDef db fill:none,color:#e0e0e0,stroke:#9b8ab8,stroke-width:2.5px

    subgraph API ["ArcGIS REST API — Kitchener Open Data"]
        direction TB
        A1(["11 Feature Layers<br/>road_segments, water_mains<br/>building_permits<br/>ward_boundaries<br/>parks, tree_inventory<br/>transit_routes, transit_stops<br/>etc."]):::source
    end

    PIPELINE(["dlt.pipeline<br/>destination = duckdb<br/>dataset = normalized_opendata_extract"]):::process

    subgraph DUCK ["Local DuckDB (db/metricforge.duckdb)"]
        direction TB
        T1[("road_segments")]:::db
        T2[("water_mains")]:::db
        T3[("building_permits")]:::db
        T4[("ward_boundaries")]:::db
        T5[("... 11 datasets total")]:::db
    end

    A1 -->|"paginated JSON<br/>resultOffset pagination"| PIPELINE
    PIPELINE -->|"write_disposition: replace"| DUCK
```

The `arcgis_source.py` module provides a `DATASET_CATALOG` dictionary mapping friendly names to ArcGIS Feature Server URLs (org: `qAo1OsXi67t7XgmS`). Adding a new dataset is a single dictionary entry — the pagination, schema inference, and loading are handled by DLT automatically. Data lands in the `normalized_opendata_extract` schema within the local DuckDB file.

### Step 3 — Transformation (SQLMesh)

```mermaid
%%{init: {'theme': 'dark', 'themeVariables': {'mainBkg': 'transparent', 'nodeBorder': '#555', 'clusterBkg': 'transparent', 'clusterBorder': '#555'}}}%%
flowchart TD
    classDef process fill:none,color:#e0e0e0,stroke:#d4a24e,stroke-width:2.5px
    classDef db fill:none,color:#e0e0e0,stroke:#9b8ab8,stroke-width:2.5px

    subgraph BRONZE ["Bronze — Raw Landing (DLT)"]
        BT[("normalized_opendata_extract<br/>road_segments, water_mains, building_permits<br/>ward_boundaries, parks, etc.")]:::db
    end

    subgraph SILVER ["Silver — Atomic (Standardised)"]
        direction TB
        A1["roads_atomic<br/>table + view"]:::process
        A2["water_mains_atomic<br/>table + view"]:::process
        A3["permits_atomic<br/>table + view"]:::process
        A4["boundaries_atomic<br/>table + view"]:::process
    end

    subgraph GOLD_T ["Gold — Integration & Details"]
        direction TB
        I1["infrastructure_integration<br/>roads × wards × water (aggregated)"]:::process
        D1["development_details<br/>permits × wards × water capacity"]:::process
    end

    BT --> A1
    BT --> A2
    BT --> A3
    BT --> A4
    A1 --> I1
    A2 --> I1
    A4 --> I1
    A3 --> D1
    A2 --> D1
    A4 --> D1
```

**Model pattern:** Each atomic model uses a Python macro that generates SQL. Models come in table + view pairs:
- **Table** (`INCREMENTAL_BY_TIME_RANGE`): Efficient for large datasets with time-based partitioning.
- **View**: Always-fresh reads for the semantic layer.

**Integration key:** Ward number serves as the cross-departmental join, enabling federated analysis while preserving departmental autonomy. This directly addresses the problem statement's requirement for integration without forcing departments into a monolithic system.

### Step 4 — Semantic Layer (Cube.js)

```mermaid
%%{init: {'theme': 'dark', 'themeVariables': {'mainBkg': 'transparent', 'nodeBorder': '#555', 'clusterBkg': 'transparent', 'clusterBorder': '#555'}}}%%
flowchart TD
    classDef semantic fill:none,color:#e0e0e0,stroke:#6db89e,stroke-width:2.5px
    classDef db fill:none,color:#e0e0e0,stroke:#9b8ab8,stroke-width:2.5px
    classDef config fill:none,color:#e0e0e0,stroke:#d4797a,stroke-width:2.5px

    SOURCE1[("city__local<br/>infrastructure_integration_view")]:::db
    SOURCE2[("city__local<br/>development_details_view")]:::db
    SOURCE3[("city__local<br/>water_mains_atomic_view")]:::db
    SOURCE4[("city__local<br/>boundaries_atomic_view")]:::db

    subgraph CUBES ["Cube.js Semantic Cubes"]
        direction TB
        C1["infrastructure_assets<br/>time: record_time<br/>road segments, ownership<br/>ward population, water main counts"]:::semantic
        C2["development_permits<br/>time: record_time<br/>permit counts, construction values<br/>residential vs commercial"]:::semantic
        C3["water_infrastructure<br/>time: record_time<br/>pipe counts, materials<br/>condition score, criticality, avg age"]:::semantic
        C4["ward_overview<br/>time: record_time<br/>population, households, voters<br/>councillor assignments"]:::semantic
    end

    PG["Cube.js APIs<br/>REST: port 4000<br/>SQL: port 15432"]:::config

    SOURCE1 --> C1
    SOURCE2 --> C2
    SOURCE3 --> C3
    SOURCE4 --> C4
    C1 --> PG
    C2 --> PG
    C3 --> PG
    C4 --> PG
```

Each cube is **time-attributed** — bound to `record_time` so that date filters answer the right temporal question. Cube.js runs locally via Docker (`cubejs/cube:v1.3`) with the DuckDB file mounted as a volume. Evidence dashboards query the DuckDB views directly.

### Step 5 — Visualization (Evidence)

```mermaid
%%{init: {'theme': 'dark', 'themeVariables': {'mainBkg': 'transparent', 'nodeBorder': '#555', 'clusterBkg': 'transparent', 'clusterBorder': '#555'}}}%%
flowchart LR
    classDef semantic fill:none,color:#e0e0e0,stroke:#6db89e,stroke-width:2.5px
    classDef portal fill:none,color:#e0e0e0,stroke:#c084fc,stroke-width:2.5px
    classDef config fill:none,color:#e0e0e0,stroke:#d4797a,stroke-width:2.5px

    PG["DuckDB (Direct Connection)<br/>Evidence reads from<br/>db/metricforge.duckdb"]:::config
    SQL["Evidence Source Queries<br/>sources/City/*.sql"]:::semantic

    subgraph PAGES ["Evidence Markdown Dashboards"]
        direction TB
        P1["/ — City Data OS Overview"]:::portal
        P2["/infrastructure — Assets & Condition"]:::portal
        P3["/development — Housing vs Capacity"]:::portal
        P4["/water — Pipe Age & Materials"]:::portal
        P5["/governance — Catalog & RBAC"]:::portal
    end

    PG ==>|\"SELECT ... FROM<br/>city__local.*\"| SQL
    SQL ==> PAGES
```

---

## Infrastructure and Environment

```mermaid
%%{init: {'theme': 'dark', 'themeVariables': {'mainBkg': 'transparent', 'nodeBorder': '#555', 'clusterBkg': 'transparent', 'clusterBorder': '#555'}}}%%
flowchart TB
    classDef process fill:none,color:#e0e0e0,stroke:#d4a24e,stroke-width:2.5px
    classDef db fill:none,color:#e0e0e0,stroke:#9b8ab8,stroke-width:2.5px
    classDef secret fill:none,color:#e0e0e0,stroke:#ef4444,stroke-width:2.5px

    subgraph SECRETS ["Configuration"]
        DB_PATH["DuckDB Path<br/>db/metricforge.duckdb"]:::secret
        CUBE_CFG["Cube.js Config<br/>cube.py + docker-compose.yaml"]:::secret
    end

    subgraph CONTAINERS ["Runtime"]
        C1["Orchestration<br/>Python 3.11+<br/>Prefect + DLT + SQLMesh"]:::process
        C3["Cube.js Container<br/>cubejs/cube:v1.3<br/>Docker"]:::process
        C2["Visualization<br/>Evidence<br/>npm run dev"]:::process
    end

    subgraph STORAGE ["Data Storage"]
        DUCK[("Local DuckDB<br/>db/metricforge.duckdb")]:::db
    end

    DB_PATH --> C1
    CUBE_CFG --> C3
    C1 --> DUCK
    C3 --> DUCK
    C2 --> DUCK
```

---

## Data Lakehouse Layers

```mermaid
%%{init: {'theme': 'dark', 'themeVariables': {'mainBkg': 'transparent', 'nodeBorder': '#555', 'clusterBkg': 'transparent', 'clusterBorder': '#555'}}}%%
flowchart LR
    classDef bronze fill:none,color:#e0e0e0,stroke:#cd7f32,stroke-width:2.5px
    classDef silver fill:none,color:#e0e0e0,stroke:#c0c0c0,stroke-width:2.5px
    classDef gold fill:none,color:#e0e0e0,stroke:#ffd700,stroke-width:2.5px

    B["BRONZE<br/>Raw DLT Tables<br/>Local DuckDB<br/>normalized_opendata_extract"]:::bronze
    S["SILVER<br/>Atomic Models<br/>city__local.*_atomic"]:::silver
    G["GOLD<br/>Semantic Metrics<br/>Cube.js Cubes<br/>infrastructure, permits, water, wards"]:::gold
    P["PRESENTATION<br/>Evidence Dashboards<br/>City Data OS"]:::gold

    B --> S --> G --> P
```

---

## Technology Stack

```mermaid
%%{init: {'theme': 'dark', 'themeVariables': {'mainBkg': 'transparent', 'nodeBorder': '#555', 'clusterBkg': 'transparent', 'clusterBorder': '#555'}}}%%
flowchart TB
    classDef layer fill:none,color:#e0e0e0,stroke:#888,stroke-width:2px

    subgraph STACK ["Technology Stack"]
        direction TB
        subgraph SOURCES ["Data Sources"]
            A["ArcGIS Hub REST API<br/>Kitchener Open Data"]:::layer
        end
        subgraph ORCHESTRATION ["Orchestration"]
            B["Prefect 3.x<br/>@flow / @task"]:::layer
        end
        subgraph EXT ["Extraction"]
            C["DLT (Data Load Tool)<br/>ArcGIS → Local DuckDB"]:::layer
        end
        subgraph OLAP ["OLAP Engine"]
            D["DuckDB (Local)<br/>db/metricforge.duckdb"]:::layer
        end
        subgraph XFORM ["Transformation"]
            E["SQLMesh<br/>Python macros → SQL models"]:::layer
        end
        subgraph SEM ["Semantic"]
            F["Cube.js (Docker)<br/>YAML cubes, REST + SQL API"]:::layer
        end
        subgraph VIZL ["Visualization"]
            G["Evidence<br/>Markdown dashboards"]:::layer
        end
        subgraph INFRA ["Infrastructure"]
            H["Docker, GitHub<br/>Local Development"]:::layer
        end

        SOURCES --> ORCHESTRATION --> EXT --> OLAP --> XFORM --> SEM --> VIZL
    end
```
