"""
test_run.py — Subset smoke test (NO LLM required)
==================================================
Runs the ingestion pipeline directly for 2 small datasets:
  • Municipal Boundary  (1 polygon — tiny, instant)
  • Traffic Closures    (small public dataset, usually < 100 features)

No Ollama, no LLM, no agent loop — just the raw Python functions.
Every step prints to stdout so you can see exactly what is happening.

Usage:
    .venv/bin/python Foundry-Pipelines/Theme1/Site1/Kitchener-GIS-Agent/test_run.py
"""

import pathlib
import sys
import time

# ── Make sure we can import from the agent file (works from any machine/cwd) ──
sys.path.insert(0, str(pathlib.Path(__file__).parent))

from kitchener_agent import (
    TARGET_DATASETS,
    MAX_RECORDS,
    _fetch_dcat_catalogue,
    _find_geojson_url,
    _resolve_targets,
    init_schema,
    ingest_dataset_to_duckdb,
    get_ingestion_status,
    get_conn,
)

# ── Which datasets to test ─────────────────────────────────────────────────────
TEST_KEYS = ["Municipal Boundary", "Traffic Closures"]

print()
print("=" * 60)
print(f"  Record cap : {MAX_RECORDS if MAX_RECORDS else 'unlimited'}")
print(f"  Datasets   : {TEST_KEYS}")
print("=" * 60)

# ── Step 1: Schema ─────────────────────────────────────────────────────────────
print()
print("=" * 60)
print("STEP 1 — Initialising DuckDB schema")
print("=" * 60)
init_schema()

# ── Step 2: Fetch DCAT catalogue ───────────────────────────────────────────────
print()
print("=" * 60)
print("STEP 2 — Fetching Kitchener DCAT-US catalogue …")
print("         (one HTTP call to open-kitchenergis.opendata.arcgis.com)")
print("=" * 60)
t0 = time.time()
catalogue = _fetch_dcat_catalogue()
print(f"  ✅  Got {len(catalogue)} datasets in {time.time() - t0:.1f}s")

# ── Step 3: Resolve URLs for our 2 test datasets ───────────────────────────────
print()
print("=" * 60)
print("STEP 3 — Resolving GeoJSON URLs for test datasets")
print("=" * 60)
resolved = _resolve_targets()

for key in TEST_KEYS:
    if key in resolved:
        info = resolved[key]
        print(f"  ✅  {key}")
        print(f"        Title : {info['title']}")
        print(f"        URL   : {info['geojson_url']}")
    else:
        print(f"  ❌  {key} — NOT FOUND in catalogue (check title substring)")

missing = [k for k in TEST_KEYS if k not in resolved]
if missing:
    print(f"\n  ⛔  Aborting — could not resolve: {missing}")
    sys.exit(1)

# ── Step 4: Ingest each dataset ────────────────────────────────────────────────
for i, key in enumerate(TEST_KEYS, start=1):
    print()
    print("=" * 60)
    print(f"STEP {3 + i} — Ingesting '{key}'")
    print("=" * 60)
    print(f"  Downloading GeoJSON from Kitchener portal …")
    t0 = time.time()

    # ingest_dataset_to_duckdb is a LangChain @tool — call .invoke() on it
    result = ingest_dataset_to_duckdb.invoke(key)

    elapsed = time.time() - t0
    print(f"  Done in {elapsed:.1f}s")
    print(f"  Result: {result}")

# ── Step 5: Verify what landed in DuckDB ──────────────────────────────────────
print()
print("=" * 60)
print(f"STEP {3 + len(TEST_KEYS) + 1} — Querying DuckDB to verify ingestion")
print("=" * 60)

conn = get_conn()

print("\n  Asset counts by type:")
df = conn.execute("""
    SELECT asset_type, department_owner, COUNT(*) AS total_rows
    FROM   assets
    GROUP  BY asset_type, department_owner
    ORDER  BY total_rows DESC
""").fetchdf()
print(df.to_string(index=False))

print("\n  Ingestion log:")
log = conn.execute("""
    SELECT dataset_title, records_in, records_out, status, ran_at
    FROM   ingestion_log
    ORDER  BY ran_at DESC
""").fetchdf()
print(log.to_string(index=False))

print("\n  Sample assets (first 5 rows):")
sample = conn.execute("""
    SELECT asset_id, asset_type, label, latitude, longitude, department_owner
    FROM   assets
    LIMIT  5
""").fetchdf()
print(sample.to_string(index=False))

conn.close()

print()
print("=" * 60)
print("✅  Smoke test complete — DuckDB is populated and queryable.")
print("    Next step: run kitchener_agent.py for all 7 datasets.")
print("=" * 60)
print()
