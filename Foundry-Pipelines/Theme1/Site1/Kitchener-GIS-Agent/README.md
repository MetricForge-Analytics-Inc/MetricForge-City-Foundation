# Kitchener GIS Ingestion Agent

A LangChain agent that pulls open GIS datasets from the City of Kitchener's ArcGIS portal and stores them in a local DuckDB database — mapped to the MetricForge City Foundation schema (`assets`, `events`, `accounts`).

**No API keys required. Runs 100% locally and for free using Ollama.**

---

## What this does (plain English)

The agent hits the Kitchener open data website, downloads datasets like Building Permits, Roads, Water Mains, Building Outlines, and Traffic Closures, and saves them all into a local database file (`city_foundation.duckdb`). Once the data is in there, you can run SQL queries across all departments — for example, *"which building permits are in areas with water capacity issues?"*

---

## First-time machine setup (do this once)

### 1. Install Ollama (the free local AI brain)

```bash
brew install ollama
brew services start ollama
```

> **What is Ollama?** It runs an AI model locally on your Mac — no internet, no API key, no cost. LangChain uses it as the "brain" that decides which tools to call.

### 2. Download the AI model (~2GB, one-time download)

```bash
ollama pull llama3.2
```

Grab a coffee — this takes a few minutes depending on your internet.

### 3. Set up the Python environment

From the root of the repo:

```bash
# Create the virtual environment (if not already done)
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r Foundry-Pipelines/Theme1/Site1/Kitchener-GIS-Agent/requirements.txt
```

---

## Running the agent (all 7 datasets)

```bash
# Step 1 — make sure Ollama is running
brew services start ollama

# Step 2 — go to the agent folder (from repo root)
cd Foundry-Pipelines/Theme1/Site1/Kitchener-GIS-Agent

# Step 3 — delete old DB (clean slate)
rm -f city_foundation.duckdb

# Step 4 — run the full agent
../../../../.venv/bin/python kitchener_agent.py
```

The agent will print its reasoning step by step and then write everything to `city_foundation.duckdb` in the same folder.

> **Note:** Zoning data was intentionally left out. The Kitchener open data portal only publishes zoning as static PDF maps — no downloadable GeoJSON exists for it.

---

## Quick smoke test — 2 datasets, no LLM, prints every step live

This is the fastest way to verify everything works end-to-end. Runs in ~30 seconds, no Ollama needed:

```bash
# From repo root
cd Foundry-Pipelines/Theme1/Site1/Kitchener-GIS-Agent
rm -f city_foundation.duckdb
../../../../.venv/bin/python test_run.py
```

You should see every step print live — catalogue fetch, URL resolution, download, insert, and a final DuckDB query confirming rows are in the table.

---

## Viewing the tables after ingestion

```bash
# From repo root
cd Foundry-Pipelines/Theme1/Site1/Kitchener-GIS-Agent
../../../../.venv/bin/python -c "
import duckdb, pathlib
conn = duckdb.connect(str(pathlib.Path('city_foundation.duckdb').resolve()))
print('--- Asset counts by type ---')
print(conn.execute('SELECT asset_type, department_owner, COUNT(*) AS total FROM assets GROUP BY asset_type, department_owner ORDER BY total DESC').fetchdf())
print()
print('--- Ingestion log ---')
print(conn.execute('SELECT dataset_title, records_in, records_out, status, ran_at FROM ingestion_log ORDER BY ran_at DESC').fetchdf())
print()
print('--- Sample assets (first 5) ---')
print(conn.execute('SELECT asset_id, asset_type, label, latitude, longitude FROM assets LIMIT 5').fetchdf())
"
```

---

## Querying the data after ingestion

Open a Python shell or script and run:

```python
import duckdb
conn = duckdb.connect("city_foundation.duckdb")

# Asset counts by department
print(conn.execute("""
    SELECT department_owner, asset_type, COUNT(*) AS total
    FROM assets
    GROUP BY department_owner, asset_type
    ORDER BY total DESC
""").fetchdf())
```

---

## Datasets being ingested

| Kitchener Dataset | Stored as | Department | Privacy |
|---|---|---|---|
| Building Permits | `permit` | planning | internal |
| Property Ownership Public | `parcel` | planning | internal |
| Water Distribution Mains | `pipe` | engineering | internal |
| Roads | `road` | engineering | public |
| Building Outlines | `building` | planning | public |
| Traffic Closures | `closure` | engineering | public |
| Municipal Boundary | `boundary` | planning | public |

---

## Want to use a different AI (e.g. OpenAI or Gemini)?

Change these two lines in `kitchener_agent.py`:

**OpenAI (costs ~$0.01 per run):**
```python
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
# Also: export OPENAI_API_KEY=sk-...
```

**Google Gemini (free tier):**
```python
from langchain_google_genai import ChatGoogleGenerativeAI
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key="your-key")
# Get a free key at aistudio.google.com
```

---

## MotherDuck (cloud DuckDB)

By default the agent writes to a **local file** (`city_foundation.duckdb`). If your team sets up MotherDuck for shared cloud storage:

```bash
export MOTHERDUCK_TOKEN=your-token-here
```

The agent will automatically detect this and write to the cloud instead.

---

## Adding more datasets

Edit `TARGET_DATASETS` at the top of `kitchener_agent.py`:

```python
TARGET_DATASETS: dict[str, tuple[str, str, str]] = {
    "Building Permits": ("permit", "internal", "planning"),
    "My New Dataset":   ("my_type", "public",  "my_department"),
}
```

The key is matched against dataset titles on the Kitchener Hub — any publicly listed dataset can be added this way.
