"""
run_local.py  —  Zero-token local runner
=========================================
Runs the full Kitchener GIS ingestion pipeline and prints a summary table
WITHOUT using any LLM / OpenAI API calls.

Just calls the tool functions directly:
    1. _resolve_targets()       → discover real GeoJSON URLs from DCAT feed
    2. fetch_dataset()          → preview each dataset
    3. ingest_dataset_to_duckdb() → load into local DuckDB
    4. get_ingestion_status()   → print summary

Usage:
    python run_local.py
"""

import sys
import os

# ── Make sure we can import from kitchener_agent ──────────────────────────────
sys.path.insert(0, os.path.dirname(__file__))

from kitchener_agent import (
    TARGET_DATASETS,
    init_schema,
    _resolve_targets,
    ingest_dataset_to_duckdb,
    get_ingestion_status,
    get_conn,
)

# ── 1. Init schema ─────────────────────────────────────────────────────────────
print("\n🏙️   Kitchener City Foundation — Local Ingestion Runner (no tokens)")
print("=" * 60)
init_schema()

# ── 2. Resolve URLs from live DCAT feed ───────────────────────────────────────
print("\n📡  Resolving dataset URLs from Kitchener DCAT feed...")
try:
    resolved = _resolve_targets()
except Exception as e:
    print(f"❌  Could not reach DCAT feed: {e}")
    sys.exit(1)

print(f"\n✅  Resolved {len(resolved)} / {len(TARGET_DATASETS)} target datasets:\n")
for key, info in resolved.items():
    print(f"  • {key}")
    print(f"      → {info['geojson_url']}")

missing = [k for k in TARGET_DATASETS if k not in resolved]
if missing:
    print(f"\n⚠️   Could not resolve: {missing}")

# ── 3. Ingest each dataset ─────────────────────────────────────────────────────
print("\n⬇️   Starting ingestion...\n")
for title_key in resolved:
    print(f"  Ingesting '{title_key}'...")
    # .invoke() is the LangChain tool wrapper — pass the string arg directly
    result = ingest_dataset_to_duckdb.invoke(title_key)
    print(f"  {result}\n")

# ── 4. Status summary ──────────────────────────────────────────────────────────
print("\n📊  Ingestion Status:")
print("-" * 60)
print(get_ingestion_status.invoke(""))

# ── 5. Cross-departmental demo queries ────────────────────────────────────────
print("\n\n🔍  Demo: Cross-departmental queries")
print("-" * 60)

conn = get_conn()

print("\n[1] Asset counts by department + type:")
df1 = conn.execute("""
    SELECT department_owner, asset_type, COUNT(*) AS total
    FROM   assets
    GROUP  BY department_owner, asset_type
    ORDER  BY total DESC
""").fetchdf()
print(df1.to_string(index=False))

print("\n[2] Privacy class breakdown:")
df2 = conn.execute("""
    SELECT privacy_class, COUNT(*) AS total
    FROM   assets
    GROUP  BY privacy_class
    ORDER  BY total DESC
""").fetchdf()
print(df2.to_string(index=False))

print("\n[3] Events by type + department:")
df3 = conn.execute("""
    SELECT event_type, event_subtype, department_source, COUNT(*) AS cnt
    FROM   events
    GROUP  BY event_type, event_subtype, department_source
    ORDER  BY cnt DESC
    LIMIT  10
""").fetchdf()
print(df3.to_string(index=False))

print("\n[4] The housing-pause query — permits near engineering assets:")
df4 = conn.execute("""
    SELECT
        a.asset_type,
        a.department_owner,
        a.label,
        a.latitude,
        a.longitude,
        a.privacy_class
    FROM assets a
    WHERE a.asset_type IN ('permit', 'pipe', 'road')
    ORDER BY a.asset_type, a.department_owner
    LIMIT 20
""").fetchdf()
print(df4.to_string(index=False))

conn.close()

print("\n✅  Done! Database saved to: city_foundation.duckdb")
print("    You can query it directly with: duckdb city_foundation.duckdb")
