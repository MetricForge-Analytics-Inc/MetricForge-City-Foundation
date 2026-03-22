# MetricForge Foundry — System Architecture

## High-Level Overview

```mermaid
%%{init: {'theme': 'dark', 'themeVariables': {'mainBkg': 'transparent', 'nodeBorder': '#555', 'clusterBkg': 'transparent', 'clusterBorder': '#555'}}}%%
flowchart LR
    classDef input fill:none,color:#e0e0e0,stroke:#6ba3d6,stroke-width:2.5px
    classDef process fill:none,color:#e0e0e0,stroke:#d4a24e,stroke-width:2.5px
    classDef data fill:none,color:#e0e0e0,stroke:#6db89e,stroke-width:2.5px
    classDef config fill:none,color:#e0e0e0,stroke:#d4797a,stroke-width:2.5px
    classDef db fill:none,color:#e0e0e0,stroke:#9b8ab8,stroke-width:2.5px
    classDef infra fill:none,color:#e0e0e0,stroke:#888,stroke-width:2px,stroke-dasharray: 5 3
    classDef portal fill:none,color:#e0e0e0,stroke:#c084fc,stroke-width:2.5px

    subgraph LEFT [" "]
        direction TB
        subgraph PORTAL ["MetricForge Customer Portal"]
            direction TB
            CUST1["Customer 1"]:::portal
            CUST2["Customer 2"]:::portal
            PAGE["Onboarding Page"]:::portal
            V1{{"API Secret Vault<br/>Tenant 1"}}:::config
            V2{{"API Secret Vault<br/>Tenant 2"}}:::config
            CUST1 --> PAGE
            CUST2 --> PAGE
            PAGE --> V1
            PAGE --> V2
        end

        subgraph SOURCES ["Data Sources"]
            direction TB
            S1[/"Support Tools<br/>Zendesk, Freshdesk, etc."/]:::input
            S2[/"CRM<br/>Salesforce, HubSpot, etc."/]:::input
            S3[/"Marketing Automation<br/>Marketo, Pardot, etc."/]:::input
            S4[/"Contact Center<br/>Genesys, Five9, etc."/]:::input
            S1 ~~~ S2 ~~~ S3 ~~~ S4
        end

        PORTAL ~~~ SOURCES
    end

    subgraph T1 ["Support Pipelines: Tenant 1"]
        direction LR
        subgraph CTR1 ["Container Image"]
            direction LR
            E1(["DLT Pipeline"]):::process
            M1A["Normalized<br/>Base Tables"]:::data
            Q1B(["SQLMesh<br/>Atomic Queries"]):::process
            PG1[("Postgres<br/>Tenant 1 State")]:::db
            M1B["Dimension Tables"]:::data
            Q1C(["SQLMesh<br/>Atomic Queries"]):::process
            M1C["Fact Tables"]:::data
            Q1D(["SQLMesh Integration<br/>& Detail Queries"]):::process
            DM1["Data Marts"]:::data
            CU1{{"Cube.dev Config"}}:::config
            EV1["Evidence<br/>Dashboard"]:::config

            E1 --> M1A
            M1A --> Q1B --> M1B
            M1A --> Q1C --> M1C
            M1B --> Q1D
            M1C --> Q1D
            Q1D --> DM1
            DM1 --> CU1 --> EV1
            Q1B -.-|state| PG1
            PG1 -.-|state| Q1C
            PG1 -.-|state| Q1D
        end
        MD1[("MotherDuck<br/>Tenant 1 DB")]:::db
        BS1[/"Block Storage<br/>Tenant 1"/]:::infra
        E1 -.-|storage| MD1
        M1A -.-|storage| MD1
        M1B -.-|storage| MD1
        M1C -.-|storage| MD1
        DM1 -.-|storage| MD1
        PG1 -.-|persists to| BS1
    end

    subgraph T2 ["Support Pipelines: Tenant 2"]
        direction LR
        subgraph CTR2 ["Container Image"]
            direction LR
            E2(["DLT Pipeline"]):::process
            M2A["Normalized<br/>Base Tables"]:::data
            Q2B(["SQLMesh<br/>Atomic Queries"]):::process
            PG2[("Postgres<br/>Tenant 2 State")]:::db
            M2B["Dimension Tables"]:::data
            Q2C(["SQLMesh<br/>Atomic Queries"]):::process
            M2C["Fact Tables"]:::data
            Q2D(["SQLMesh Integration<br/>& Detail Queries"]):::process
            DM2["Data Marts"]:::data
            CU2{{"Cube.dev Config"}}:::config
            EV2["Evidence<br/>Dashboard"]:::config

            E2 --> M2A
            M2A --> Q2B --> M2B
            M2A --> Q2C --> M2C
            M2B --> Q2D
            M2C --> Q2D
            Q2D --> DM2
            DM2 --> CU2 --> EV2
            Q2B -.-|state| PG2
            PG2 -.-|state| Q2C
            PG2 -.-|state| Q2D
        end
        MD2[("MotherDuck<br/>Tenant 2 DB")]:::db
        BS2[/"Block Storage<br/>Tenant 2"/]:::infra
        E2 -.-|storage| MD2
        M2A -.-|storage| MD2
        M2B -.-|storage| MD2
        M2C -.-|storage| MD2
        DM2 -.-|storage| MD2
        PG2 -.-|persists to| BS2
    end

    SOURCES --> E1
    SOURCES --> E2
    V1 -.-|API credentials| E1
    V2 -.-|API credentials| E2
```

> | Shape | Meaning |
> |---|---|
> | Parallelogram | External input / data source |
> | Rounded rectangle | Process (DLT Pipeline, SQLMesh Query) |
> | Rectangle | Data output (tables, marts) |
> | Hexagon | Configuration (Cube.dev, Evidence) |
> | Cylinder | Database (MotherDuck, Postgres) |
> | Solid arrow | Data flow |
> | Dotted line | Storage dependency |
>
> Pipelines are duplicated per tenant, each with isolated MotherDuck databases. Postgres is shared for SQLMesh state management.

---

## Step-by-Step Pipeline Details

### Step 1 — Orchestration

```mermaid
%%{init: {'theme': 'dark', 'themeVariables': {'mainBkg': 'transparent', 'nodeBorder': '#555', 'clusterBkg': 'transparent', 'clusterBorder': '#555'}}}%%
flowchart LR
    classDef process fill:none,color:#e0e0e0,stroke:#c084fc,stroke-width:2.5px
    classDef config fill:none,color:#e0e0e0,stroke:#d4797a,stroke-width:2.5px
    classDef infra fill:none,color:#e0e0e0,stroke:#888,stroke-width:2px,stroke-dasharray: 5 3

    subgraph ORCH ["Prefect Orchestration"]
        direction TB
        FLOW(["Support-Main.py<br/>@flow decorator"]):::process
        subgraph TASKS ["Prefect Tasks"]
            direction LR
            T1(["Source Data Pipelines<br/>@task decorator<br/>e.g. run_zendesk_pipeline"]):::process
            T2(["run_sqlmesh<br/>@task decorator"]):::process
        end
        FLOW --> T1
        FLOW --> T2
    end

    subgraph CONTAINER ["Docker Container"]
        direction TB
        IMG["Python 3.13<br/>Ubuntu 22.04"]:::infra
        VENV[".venv<br/>pip requirements.txt"]:::infra
        IMG --- VENV
    end

    subgraph ENV ["Environment"]
        direction TB
        SECRETS{{"Source Data Env Variables<br/>e.g. ZENDESK_SUBDOMAIN<br/>ZENDESK_EMAIL, ZENDESK_TOKEN"}}:::config
        MD_TOKEN{{"OLAP Warehouse Token<br/>e.g. MOTHERDUCK_CODESPACE_TOKEN"}}:::config
        PG_CREDS{{"Postgres Credentials<br/>HOST, PORT, USER<br/>PASSWORD, DATABASE"}}:::config
    end

    CONTAINER --> ORCH
    ENV -.-|injected at runtime| ORCH
    T1 -->|subprocess call| EXTRACT["Source Pipeline Script<br/>e.g. zendesk_pipeline.py"]:::process
    T2 -->|subprocess call| SQLMESH["sqlmesh plan --auto-apply"]:::process
```

### Step 2 — Extraction (DLT)

```mermaid
%%{init: {'theme': 'dark', 'themeVariables': {'mainBkg': 'transparent', 'nodeBorder': '#555', 'clusterBkg': 'transparent', 'clusterBorder': '#555'}}}%%
flowchart LR
    classDef source fill:none,color:#e0e0e0,stroke:#6ba3d6,stroke-width:2.5px
    classDef process fill:none,color:#e0e0e0,stroke:#0891b2,stroke-width:2.5px
    classDef data fill:none,color:#e0e0e0,stroke:#6db89e,stroke-width:2.5px
    classDef db fill:none,color:#e0e0e0,stroke:#9b8ab8,stroke-width:2.5px

    subgraph APIS ["Source Data APIs"]
        direction TB
        ZS(["API Endpoints<br/>e.g. Zendesk Support API<br/>tickets, users, orgs, groups"]):::source
        ZC(["Additional Endpoints<br/>e.g. Chat API, Talk API"]):::source
        ZS ~~~ ZC
    end

    subgraph DLT ["DLT — Source Pipeline Script"]
        direction TB
        PIPELINE(["dlt.pipeline<br/>destination = OLAP warehouse<br/>dataset = normalized_source_extract<br/>e.g. normalized_zendesk_extract"]):::process
        subgraph MODES ["Load Strategies"]
            direction LR
            INC(["Incremental<br/>start_date state tracking"]):::process
            BACK(["Backloading<br/>weekly date ranges<br/>start_date → end_date"]):::process
            FULL(["Full Reload<br/>load_all=True<br/>replace write disposition"]):::process
        end
        PIPELINE --- MODES
    end

    subgraph LANDING ["Landing Zone"]
        direction TB
        MD[("OLAP Warehouse<br/>e.g. MotherDuck<br/>normalized_source_extract")]:::db
        META["DLT Metadata<br/>_dlt_loads table<br/>_dlt_id, _dlt_load_id columns"]:::data
        MD --- META
    end

    APIS ==>|"REST API<br/>OAuth / Token Auth"| DLT
    DLT ==>|"dlt adapter<br/>normalize + load"| LANDING
```

### Step 3 — Transformation (SQLMesh)

```mermaid
%%{init: {'theme': 'dark', 'themeVariables': {'mainBkg': 'transparent', 'nodeBorder': '#555', 'clusterBkg': 'transparent', 'clusterBorder': '#555'}}}%%
flowchart TB
    classDef data fill:none,color:#e0e0e0,stroke:#6db89e,stroke-width:2.5px
    classDef process fill:none,color:#e0e0e0,stroke:#d4a24e,stroke-width:2.5px
    classDef db fill:none,color:#e0e0e0,stroke:#9b8ab8,stroke-width:2.5px
    classDef config fill:none,color:#e0e0e0,stroke:#d4797a,stroke-width:2.5px

    MD[("OLAP Warehouse<br/>e.g. MotherDuck<br/>normalized_source_extract")]:::db

    subgraph SQLMESH ["SQLMesh — DuckDB Compute Engine"]
        direction TB

        subgraph EXTRACT_PROJECT ["Data-Extract Project"]
            direction LR
            subgraph NORM ["Normalized Models"]
                direction TB
                N1["normalized__source_table_1<br/>e.g. normalized__tickets"]:::process
                N2["normalized__source_table_2<br/>e.g. normalized__users"]:::process
                N3["normalized__source_table_n"]:::process
                N1 ~~~ N2 ~~~ N3
            end
            subgraph ATOM ["Atomic Models"]
                direction TB
                A1["atomic__source_table_1<br/>e.g. atomic__tickets"]:::process
                A2["atomic__source_table_2<br/>e.g. atomic__users"]:::process
                A3["atomic__source_table_n"]:::process
                A1 ~~~ A2 ~~~ A3
            end
            NORM -->|"type casting<br/>deduplication"| ATOM
        end

        subgraph PIPE_PROJECT ["Data-Pipeline Project"]
            direction LR
            subgraph INTEG ["Integration Models"]
                direction TB
                I1["integration__entity_1<br/>e.g. integration__tickets"]:::process
                I2["integration__entity_2<br/>e.g. integration__ticket_metrics"]:::process
                I1 ~~~ I2
            end
            subgraph DETAIL ["Detail Models"]
                direction TB
                D1["details__entity_details<br/>e.g. details__tickets_details"]:::process
            end
            INTEG -->|"joins + enrichment"| DETAIL
        end

        subgraph MACROS ["Python Macros"]
            direction LR
            M1{{"INCREMENTAL_BY_TIME_RANGE<br/>WHERE _dlt_load_time<br/>BETWEEN @start_ds AND @end_ds"}}:::config
            M2{{"Grain-based Dedup<br/>QUALIFY ROW_NUMBER()<br/>PARTITION BY id<br/>ORDER BY updated_at DESC"}}:::config
        end

        EXTRACT_PROJECT --> PIPE_PROJECT
        MACROS -.-|applied to all models| EXTRACT_PROJECT
        MACROS -.-|applied to all models| PIPE_PROJECT
    end

    PG[("Postgres<br/>SQLMesh State")]:::db
    OUTPUT["Foundry.support<br/>Dimension Tables<br/>Fact Tables<br/>Data Marts"]:::data

    MD ==>|"reads raw tables"| SQLMESH
    SQLMESH ==>|"writes views + tables"| OUTPUT
    PG -.-|"plan state<br/>snapshot tracking"| SQLMESH
```

### Step 4 — Semantic Layer (Cube.js)

```mermaid
%%{init: {'theme': 'dark', 'themeVariables': {'mainBkg': 'transparent', 'nodeBorder': '#555', 'clusterBkg': 'transparent', 'clusterBorder': '#555'}}}%%
flowchart LR
    classDef data fill:none,color:#e0e0e0,stroke:#6db89e,stroke-width:2.5px
    classDef semantic fill:none,color:#e0e0e0,stroke:#6db89e,stroke-width:2.5px
    classDef config fill:none,color:#e0e0e0,stroke:#d4797a,stroke-width:2.5px
    classDef db fill:none,color:#e0e0e0,stroke:#9b8ab8,stroke-width:2.5px

    SOURCE[("Foundry.support<br/>tickets_details_view")]:::db

    subgraph CUBEJS ["Cube.js Semantic Layer"]
        direction TB
        subgraph CHAIN ["6-Cube Inheritance Chain"]
            direction TB
            C1["tickets_case_created_time<br/>time: case_created_time<br/>case_created_volume, satisfaction_score<br/>on_hold_time, case_unsolved_volume"]:::semantic
            C2["tickets_case_response_time<br/>time: case_latest_comment_added_time<br/>total_agent_replies<br/>avg_first_reply_time_business_minutes"]:::semantic
            C3["tickets_case_reassigned_time<br/>time: case_last_assignment_time<br/>case_reassigned_volume"]:::semantic
            C4["tickets_case_incident_time<br/>time: case_created_time<br/>total_incidents, total_problems"]:::semantic
            C5["tickets_case_reopened_time<br/>time: case_last_updated_time<br/>case_reopened_volume"]:::semantic
            C6["tickets_case_closed_time<br/>time: case_status_last_updated_time<br/>total_solved_tickets<br/>one_touch / two_touch / multi_touch"]:::semantic
            C1 -->|extends| C2 -->|extends| C3 -->|extends| C4 -->|extends| C5 -->|extends| C6
        end
        C7["tickets_case_detail<br/>Presentation Cube<br/>all dimensions + measures"]:::config
        C6 -->|extends| C7
    end

    PG[("Postgres<br/>Cube.js SQL API<br/>Port 5432")]:::db

    SOURCE ==>|sql_table| C1
    C7 ==>|"exposes via"| PG
```

### Step 5 — Visualization (Evidence)

```mermaid
%%{init: {'theme': 'dark', 'themeVariables': {'mainBkg': 'transparent', 'nodeBorder': '#555', 'clusterBkg': 'transparent', 'clusterBorder': '#555'}}}%%
flowchart LR
    classDef source fill:none,color:#e0e0e0,stroke:#9b8ab8,stroke-width:2.5px
    classDef query fill:none,color:#e0e0e0,stroke:#d4a24e,stroke-width:2.5px
    classDef page fill:none,color:#e0e0e0,stroke:#eab308,stroke-width:2.5px

    PG[("Postgres<br/>Cube.js SQL API")]:::source

    subgraph SQL ["SQL Source Queries"]
        direction TB
        Q1["cube_kpis.sql<br/>headline metrics"]:::query
        Q2["cases_cube.sql<br/>case-level detail"]:::query
        Q3["cube_daily_trend.sql<br/>time series aggregations"]:::query
        Q4["cube_by_channel.sql<br/>channel breakdown"]:::query
        Q5["cube_by_priority.sql<br/>priority breakdown"]:::query
        Q6["cube_by_status.sql<br/>status breakdown"]:::query
        Q1 ~~~ Q2 ~~~ Q3 ~~~ Q4 ~~~ Q5 ~~~ Q6
    end

    subgraph EVIDENCE ["Evidence — Markdown BI"]
        direction TB
        D1["index.md<br/>Operational Health<br/>KPIs, daily trends"]:::page
        D2["cases.md<br/>Case Explorer<br/>filterable data table"]:::page
        D3["performance.md<br/>SLAs and Efficiency<br/>reply times, resolution"]:::page
        D4["satisfaction.md<br/>CSAT Analytics<br/>scores, distributions"]:::page
        D5["trends.md<br/>Time Series<br/>volume over time"]:::page
        D1 ~~~ D2 ~~~ D3 ~~~ D4 ~~~ D5
    end

    PG ==>|"SELECT MEASURE<br/>FROM tickets_case_detail"| SQL
    SQL ==>|"injected into<br/>Markdown templates"| EVIDENCE
```

## Infrastructure and Environment

```mermaid
%%{init: {'theme': 'dark', 'themeVariables': {'mainBkg': 'transparent', 'nodeBorder': '#555', 'clusterBkg': 'transparent', 'clusterBorder': '#555'}}}%%
flowchart LR
    classDef infra fill:none,color:#e0e0e0,stroke:#6ba3d6,stroke-width:2.5px
    classDef env fill:none,color:#e0e0e0,stroke:#d4a24e,stroke-width:2.5px
    classDef secret fill:none,color:#e0e0e0,stroke:#d4797a,stroke-width:2.5px

    subgraph RUNTIME ["Runtime Environment"]
        direction TB
        DC["Docker<br/>Ubuntu 22.04, Python 3.13"]:::infra
        VENV[".venv<br/>Virtual Environment"]:::infra
        DC --- VENV
    end

    subgraph DEV ["Development Environment"]
        direction TB
        DEVCON["Dev Container<br/>VS Code Remote"]:::infra
        EXTENSIONS["Extensions<br/>SQLMesh, Jupyter<br/>Evidence, SQLTools"]:::env
        DEVCON --- EXTENSIONS
    end

    subgraph SECRETS ["Environment Variables"]
        direction TB
        ZEN_CREDS["Zendesk<br/>SUBDOMAIN, EMAIL, TOKEN"]:::secret
        MD_CREDS["MotherDuck<br/>MOTHERDUCK_CODESPACE_TOKEN"]:::secret
        PG_CREDS["Postgres / Cube.js<br/>HOST, PORT, USER<br/>PASSWORD, DATABASE"]:::secret
    end

    RUNTIME --> SECRETS
    DEV --> SECRETS
```

## Data Lakehouse Layers

```mermaid
%%{init: {'theme': 'dark', 'themeVariables': {'mainBkg': 'transparent', 'nodeBorder': '#555', 'clusterBkg': 'transparent', 'clusterBorder': '#555'}}}%%
flowchart LR
    classDef bronze fill:none,color:#e0e0e0,stroke:#cd7f32,stroke-width:2.5px
    classDef silver fill:none,color:#e0e0e0,stroke:#c0c0c0,stroke-width:2.5px
    classDef gold fill:none,color:#e0e0e0,stroke:#ffd700,stroke-width:2.5px
    classDef vizstyle fill:none,color:#e0e0e0,stroke:#6ba3d6,stroke-width:2.5px

    B["BRONZE<br/>Raw DLT Tables<br/>MotherDuck<br/>normalized_zendesk_extract"]:::bronze
    S["SILVER<br/>Cleaned and Deduped<br/>SQLMesh Models<br/>Foundry.support"]:::silver
    G["GOLD<br/>Semantic Metrics<br/>Cube.js 6-Cube Chain<br/>tickets_case_detail"]:::gold
    V["VISUALIZATION<br/>Evidence Dashboards<br/>5 Pages, 6 SQL Sources<br/>Markdown + Charts"]:::vizstyle

    B ==>|"SQLMesh<br/>incremental macros"| S
    S ==>|"Cube.js<br/>YAML definitions"| G
    G ==>|"Postgres SQL API<br/>MEASURE queries"| V
```

## Semantic Cube Inheritance

```mermaid
%%{init: {'theme': 'dark', 'themeVariables': {'mainBkg': 'transparent', 'nodeBorder': '#555', 'clusterBkg': 'transparent', 'clusterBorder': '#555'}}}%%
flowchart TB
    classDef base fill:none,color:#e0e0e0,stroke:#6db89e,stroke-width:2.5px
    classDef mid fill:none,color:#e0e0e0,stroke:#d4a24e,stroke-width:2.5px
    classDef final fill:none,color:#e0e0e0,stroke:#d4797a,stroke-width:2.5px

    subgraph CUBE_CHAIN ["Cube.js - Time-Attributed Measure Chain"]
        direction TB

        C1["tickets_case_created_time<br/>Time: case_created_time<br/>case_created_volume, end_user_created<br/>satisfaction_score, on_hold_time<br/>case_unsolved_volume cumulative"]:::base

        C2["tickets_case_response_time<br/>Time: case_latest_comment_added_time<br/>total_agent_replies<br/>avg_first_reply_time_business_minutes<br/>avg_first_reply_time_calendar_minutes"]:::base

        C3["tickets_case_reassigned_time<br/>Time: case_last_assignment_time<br/>case_reassigned_volume"]:::mid

        C4["tickets_case_incident_time<br/>Time: case_created_time<br/>total_incidents, total_problems"]:::mid

        C5["tickets_case_reopened_time<br/>Time: case_last_updated_time<br/>case_reopened_volume"]:::mid

        C6["tickets_case_closed_time<br/>Time: case_status_last_updated_time<br/>total_solved_tickets<br/>one_touch / two_touch / multi_touch"]:::final

        C7["tickets_case_detail<br/>Presentation Cube<br/>All dimensions and measures<br/>Exposed to Evidence dashboards"]:::final

        C1 -->|extends| C2
        C2 -->|extends| C3
        C3 -->|extends| C4
        C4 -->|extends| C5
        C5 -->|extends| C6
        C6 -->|extends| C7
    end

    SQL_TABLE[("Foundry.support<br/>tickets_details_view")]:::base
    SQL_TABLE -->|sql_table source| C1
```

## Technology Stack

```mermaid
%%{init: {'theme': 'dark', 'themeVariables': {'mainBkg': 'transparent', 'nodeBorder': '#555', 'clusterBkg': 'transparent', 'clusterBorder': '#555'}}}%%
flowchart TB
    classDef layer fill:none,color:#e0e0e0,stroke:#6ba3d6,stroke-width:2.5px

    subgraph STACK ["MetricForge Technology Stack"]
        direction TB

        subgraph L1 ["Data Source"]
            Z["Zendesk SaaS<br/>Support, Chat, Talk"]:::layer
        end

        subgraph L2 ["Orchestration"]
            P["Prefect 3.6<br/>Python Flows"]:::layer
            DK["Docker<br/>Ubuntu 22.04"]:::layer
        end

        subgraph L3 ["Extraction"]
            DLTX["DLT 1.23<br/>Data Load Tool"]:::layer
        end

        subgraph L4 ["Storage"]
            MDK["MotherDuck<br/>Cloud DuckDB"]:::layer
        end

        subgraph L5 ["Transformation"]
            SM["SQLMesh 0.231<br/>Incremental Models"]:::layer
            DDB["DuckDB<br/>Compute Engine"]:::layer
        end

        subgraph L6 ["Semantic"]
            CJ["Cube.js<br/>YAML Cubes"]:::layer
            PGS["Postgres<br/>SQL API"]:::layer
        end

        subgraph L7 ["Visualization"]
            EV["Evidence 40.1<br/>Markdown BI"]:::layer
            NJ["Node.js<br/>Runtime"]:::layer
        end

        L1 --> L2 --> L3 --> L4 --> L5 --> L6 --> L7
    end
```