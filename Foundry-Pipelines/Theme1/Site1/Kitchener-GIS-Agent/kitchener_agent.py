"""
Kitchener Open Data → DuckDB Ingestion Agent
=============================================
Discovers every dataset on the Kitchener ArcGIS Open-Data Hub via the DCAT-US
feed, lets a LangChain ReAct agent choose what to ingest, and maps everything
into the MetricForge City Foundation schema:

    assets / events / accounts / asset_accounts / ingestion_log

Key design decisions
--------------------
* URL resolution  — Uses the authoritative DCAT-US feed
  (open-kitchenergis.opendata.arcgis.com/api/feed/dcat-us/1.1.json)
  to discover real GeoJSON download links; no hard-coded item IDs needed.
* Deduplication    — uuid.uuid5(DNS, "kitchener_gis:<item_id>:<obj_id>")
  guarantees the same asset_id on every re-run.
* Append-only events — every new asset triggers a single 'created' event.
* MotherDuck-ready — set MOTHERDUCK_TOKEN for cloud storage, omit for local.
* Privacy tiers    — inherited from the schema; each dataset carries its own
  privacy_class and department_owner.
"""

from __future__ import annotations

import json
import os
import pathlib
import uuid
from datetime import datetime, timezone
from typing import Any

import duckdb
import requests
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain.tools import tool
from langchain_ollama import ChatOllama

# ── Configuration ─────────────────────────────────────────────────────────────

MOTHERDUCK_TOKEN = os.getenv("MOTHERDUCK_TOKEN", "")
_HERE = pathlib.Path(__file__).parent          # always the agent folder
DB_PATH = (
    f"md:city_foundation?token={MOTHERDUCK_TOKEN}"
    if MOTHERDUCK_TOKEN
    else str(_HERE / "city_foundation.duckdb")  # absolute path — safe from any cwd
)

# DCAT-US feed — the single authoritative catalogue for this Hub
DCAT_FEED_URL = (
    "https://open-kitchenergis.opendata.arcgis.com/api/feed/dcat-us/1.1.json"
)

# Cap records per dataset — keeps the DB small and ingestion fast.
# Set to None to ingest everything (production).
# Set to a small number (e.g. 15) for quick local testing.
MAX_RECORDS: int | None = 500

# Datasets we want to ingest
# key   = dataset title substring (case-insensitive match against DCAT titles)
# value = (asset_type, privacy_class, department_owner)
TARGET_DATASETS: dict[str, tuple[str, str, str]] = {
    "Building Permits":     ("permit",   "internal", "planning"),
    "Property Ownership Public": ("parcel", "internal", "planning"),
    "Water Distribution Mains": ("pipe",   "internal", "engineering"),
    "Roads":                ("road",     "public",   "engineering"),
    "Building Outlines":    ("building", "public",   "planning"),
    "Traffic Closures":     ("closure",  "public",   "engineering"),
    "Municipal Boundary":   ("boundary", "public",   "planning"),
}


# ── DuckDB helpers ─────────────────────────────────────────────────────────────

def get_conn() -> duckdb.DuckDBPyConnection:
    return duckdb.connect(DB_PATH)


def init_schema() -> None:
    """Create core tables from db_schema.md if they don't exist yet."""
    conn = get_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS assets (
            asset_id         VARCHAR PRIMARY KEY,
            asset_type       VARCHAR,
            department_owner VARCHAR,
            source_system_id VARCHAR,
            source_system    VARCHAR,
            label            VARCHAR,
            latitude         DOUBLE,
            longitude        DOUBLE,
            status           VARCHAR DEFAULT 'active',
            privacy_class    VARCHAR DEFAULT 'internal',
            created_at       TIMESTAMP DEFAULT current_timestamp,
            updated_at       TIMESTAMP DEFAULT current_timestamp,
            valid_from       DATE,
            valid_to         DATE,
            raw_properties   JSON
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS events (
            event_id          VARCHAR PRIMARY KEY,
            asset_id          VARCHAR,
            event_type        VARCHAR,
            event_subtype     VARCHAR,
            department_source VARCHAR,
            triggered_by      VARCHAR DEFAULT 'kitchener_gis_agent',
            payload           JSON,
            severity          VARCHAR DEFAULT 'info',
            occurred_at       TIMESTAMP,
            recorded_at       TIMESTAMP DEFAULT current_timestamp,
            is_audit_event    BOOLEAN DEFAULT FALSE
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            account_id    VARCHAR PRIMARY KEY,
            account_type  VARCHAR DEFAULT 'system',
            display_name  VARCHAR,
            department    VARCHAR,
            privacy_class VARCHAR DEFAULT 'internal',
            pii_vault_ref VARCHAR,
            created_at    TIMESTAMP DEFAULT current_timestamp,
            is_active     BOOLEAN DEFAULT TRUE
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS asset_accounts (
            asset_id          VARCHAR,
            account_id        VARCHAR,
            relationship_type VARCHAR,
            valid_from        DATE,
            valid_to          DATE
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS ingestion_log (
            run_id        VARCHAR PRIMARY KEY,
            dataset_title VARCHAR,
            geojson_url   VARCHAR,
            records_in    INTEGER,
            records_out   INTEGER,
            status        VARCHAR,
            error_msg     VARCHAR,
            ran_at        TIMESTAMP DEFAULT current_timestamp
        )
    """)
    conn.close()
    print("✅  Schema initialised")


# ── DCAT catalogue helpers ─────────────────────────────────────────────────────

_DCAT_CACHE: list[dict] | None = None


def _fetch_dcat_catalogue() -> list[dict]:
    """Download and parse the DCAT-US catalogue (cached for the process lifetime)."""
    global _DCAT_CACHE
    if _DCAT_CACHE is not None:
        return _DCAT_CACHE
    print("📡  Fetching DCAT catalogue...", flush=True)
    resp = requests.get(DCAT_FEED_URL, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    _DCAT_CACHE = data.get("dataset", [])
    print(f"📡  Catalogue loaded — {len(_DCAT_CACHE)} datasets found.", flush=True)
    return _DCAT_CACHE


def _find_geojson_url(dataset: dict) -> str | None:
    """Pick the GeoJSON download URL from the distribution list."""
    for dist in dataset.get("distribution", []):
        fmt = dist.get("format", "") or dist.get("mediaType", "")
        url = dist.get("accessURL", "")
        if "geojson" in fmt.lower() or "geo+json" in fmt.lower():
            return url
        if url and url.lower().endswith(".geojson"):
            return url
    return None


def _resolve_targets() -> dict[str, dict]:
    """
    Match TARGET_DATASETS title keys against the live DCAT catalogue.
    Returns {title_key: {"title": ..., "geojson_url": ..., "meta": (type, priv, dept)}}
    """
    catalogue = _fetch_dcat_catalogue()
    resolved: dict[str, dict] = {}

    for title_key, meta in TARGET_DATASETS.items():
        for ds in catalogue:
            ds_title = ds.get("title", "")
            # Exact-ish match: target substring in catalogue title (case-insensitive)
            # Prefer KitchenerGIS datasets over City-of-Waterloo when ambiguous
            if title_key.lower() in ds_title.lower():
                geojson_url = _find_geojson_url(ds)
                if not geojson_url:
                    continue
                landing = ds.get("landingPage", "")
                is_kitchener = "KitchenerGIS" in landing
                # Accept first match; override with a Kitchener-specific one
                if title_key not in resolved or is_kitchener:
                    resolved[title_key] = {
                        "title": ds_title,
                        "geojson_url": geojson_url,
                        "landing_page": landing,
                        "meta": meta,
                    }
                if is_kitchener:
                    break  # stop searching once we have the Kitchener version

    return resolved


# ── Geometry helpers ───────────────────────────────────────────────────────────

def _extract_centroid(geometry: dict | None) -> tuple[float | None, float | None]:
    if not geometry:
        return None, None
    gtype = geometry.get("type", "")
    coords = geometry.get("coordinates")
    if not coords:
        return None, None
    if gtype == "Point":
        return float(coords[1]), float(coords[0])
    if gtype == "MultiPoint":
        return float(coords[0][1]), float(coords[0][0])
    if gtype == "LineString":
        mid = coords[len(coords) // 2]
        return float(mid[1]), float(mid[0])
    if gtype == "MultiLineString":
        mid = coords[0][len(coords[0]) // 2]
        return float(mid[1]), float(mid[0])
    if gtype == "Polygon":
        ring = coords[0]
        lats = [c[1] for c in ring]
        lons = [c[0] for c in ring]
        return sum(lats) / len(lats), sum(lons) / len(lons)
    if gtype == "MultiPolygon":
        ring = coords[0][0]
        lats = [c[1] for c in ring]
        lons = [c[0] for c in ring]
        return sum(lats) / len(lats), sum(lons) / len(lons)
    return None, None


def _pick_label(props: dict) -> str:
    """Return the most human-readable identifier found in feature properties."""
    for key in (
        "label", "address", "LABEL", "ADDRESS",
        "Name", "NAME", "name",
        "PermitNo", "PERMIT_NO", "PERMIT_NUMBER",
        "STREET_NAME", "ROAD_NAME",
        "OBJECTID", "objectid", "FID",
    ):
        val = props.get(key)
        if val and str(val).strip():
            return str(val).strip()
    return "unknown"


def _now() -> datetime:
    return datetime.now(timezone.utc)


# ── LangChain Tools ────────────────────────────────────────────────────────────

@tool
def list_target_datasets(dummy: str = "") -> str:
    """
    Lists the Kitchener datasets the agent is configured to ingest,
    resolving each one against the live DCAT catalogue to verify its
    GeoJSON URL.  Pass any string (or leave blank) as the argument.
    """
    try:
        resolved = _resolve_targets()
    except Exception as exc:
        return f"❌  Could not reach DCAT catalogue: {exc}"

    if not resolved:
        return "⚠️  No target datasets could be resolved from the DCAT catalogue."

    lines = ["Resolved target datasets:\n"]
    for key, info in resolved.items():
        lines.append(
            f"  • [{key}]\n"
            f"      Title      : {info['title']}\n"
            f"      GeoJSON URL: {info['geojson_url']}\n"
            f"      Landing    : {info['landing_page']}\n"
            f"      Type/Priv/Dept: {info['meta']}\n"
        )

    missing = [k for k in TARGET_DATASETS if k not in resolved]
    if missing:
        lines.append(f"\n⚠️  Could not resolve: {missing}")

    return "\n".join(lines)


@tool
def fetch_dataset(title_key: str) -> str:
    """
    Preview a Kitchener dataset before ingestion.
    title_key must be one of the keys in TARGET_DATASETS
    (e.g. 'Building Permits', 'Roads', 'Zoning').
    Returns feature count and a sample of property keys.
    """
    try:
        resolved = _resolve_targets()
    except Exception as exc:
        return f"❌  DCAT catalogue error: {exc}"

    if title_key not in resolved:
        available = list(resolved.keys())
        return (
            f"❌  '{title_key}' not resolved.  "
            f"Available keys: {available}"
        )

    info = resolved[title_key]
    url = info["geojson_url"]

    try:
        resp = requests.get(url, timeout=90)
        resp.raise_for_status()
        data = resp.json()
    except Exception as exc:
        return f"❌  HTTP error fetching '{title_key}': {exc}\n   URL: {url}"

    features = data.get("features", [])
    if not features:
        return f"⚠️  No features returned for '{title_key}'.\n   URL: {url}"

    sample_props = list(features[0].get("properties", {}).keys())[:20]
    geom_types = {f.get("geometry", {}).get("type") for f in features[:50] if f.get("geometry")}

    return (
        f"✅  '{title_key}' — {len(features)} features fetched.\n"
        f"   Geometry types (sample): {geom_types}\n"
        f"   Sample property keys  : {sample_props}\n"
        f"   GeoJSON URL           : {url}"
    )


@tool
def ingest_dataset_to_duckdb(title_key: str) -> str:
    """
    Download a Kitchener ArcGIS dataset and load it into DuckDB
    (assets + events tables).
    title_key must be one of the keys in TARGET_DATASETS
    (e.g. 'Building Permits', 'Roads', 'Zoning').
    Returns a summary of records inserted or skipped (deduplication).
    """
    try:
        resolved = _resolve_targets()
    except Exception as exc:
        return f"❌  DCAT catalogue error: {exc}"

    if title_key not in resolved:
        available = list(resolved.keys())
        return (
            f"❌  '{title_key}' not resolved.  "
            f"Run list_target_datasets first.  Available: {available}"
        )

    info = resolved[title_key]
    url = info["geojson_url"]
    asset_type, privacy_class, department = info["meta"]
    run_id = str(uuid.uuid4())
    now_ts = _now()

    # ── Fetch GeoJSON ──────────────────────────────────────────────────────────
    try:
        print(f"  ⬇️   Downloading GeoJSON for '{title_key}'...", flush=True)
        resp = requests.get(url, timeout=120)
        resp.raise_for_status()
        features: list[dict] = resp.json().get("features", [])
        print(f"  ⬇️   {len(features)} features downloaded.", flush=True)
    except Exception as exc:
        _log_run(run_id, title_key, url, 0, 0, "failed", str(exc))
        return f"❌  Fetch failed for '{title_key}': {exc}"

    # ── Apply record cap ───────────────────────────────────────────────────────
    if MAX_RECORDS is not None and len(features) > MAX_RECORDS:
        print(f"  ✂️   Capping at {MAX_RECORDS} records (dataset has {len(features)}).", flush=True)
        features = features[:MAX_RECORDS]

    conn = get_conn()
    inserted_assets = 0
    inserted_events = 0
    source_system_name = f"kitchener_gis_{title_key.lower().replace(' ', '_')}"

    for i, feat in enumerate(features):
        if i > 0 and i % 500 == 0:
            print(f"  💾  {title_key}: {i}/{len(features)} rows processed...", flush=True)
        props: dict = feat.get("properties") or {}
        geom: dict | None = feat.get("geometry")
        lat, lon = _extract_centroid(geom)

        # Stable dedup key from the ArcGIS OBJECTID (or a UUID fallback)
        source_id = str(
            props.get("OBJECTID")
            or props.get("objectid")
            or props.get("FID")
            or uuid.uuid4()
        )
        asset_id = str(
            uuid.uuid5(
                uuid.NAMESPACE_DNS,
                f"kitchener_gis:{title_key}:{source_id}",
            )
        )
        label = _pick_label(props)

        # ── Upsert asset (skip if already present) ─────────────────────────
        existing = conn.execute(
            "SELECT asset_id FROM assets WHERE asset_id = ?", [asset_id]
        ).fetchone()

        if not existing:
            conn.execute(
                """
                INSERT INTO assets
                    (asset_id, asset_type, department_owner,
                     source_system_id, source_system,
                     label, latitude, longitude,
                     privacy_class, status,
                     created_at, updated_at,
                     raw_properties)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'active', ?, ?, ?)
                """,
                [
                    asset_id, asset_type, department,
                    source_id, source_system_name,
                    label, lat, lon,
                    privacy_class,
                    now_ts, now_ts,
                    json.dumps(props, default=str),
                ],
            )
            inserted_assets += 1

            # ── Append-only 'created' event ───────────────────────────────
            conn.execute(
                """
                INSERT INTO events
                    (event_id, asset_id,
                     event_type, event_subtype,
                     department_source, triggered_by,
                     payload, severity,
                     occurred_at, recorded_at,
                     is_audit_event)
                VALUES (?, ?, ?, ?, ?, 'kitchener_gis_agent', ?, 'info', ?, ?, FALSE)
                """,
                [
                    str(uuid.uuid4()), asset_id,
                    "created", f"{title_key.lower().replace(' ','_')}_ingested",
                    department,
                    json.dumps(
                        {"source_url": url, "source_id": source_id},
                        default=str,
                    ),
                    now_ts, now_ts,
                ],
            )
            inserted_events += 1

    # ── Ingestion log ──────────────────────────────────────────────────────────
    _log_run(
        run_id, title_key, url,
        len(features), inserted_assets, "success", None,
        conn=conn,
    )
    conn.close()

    skipped = len(features) - inserted_assets
    return (
        f"✅  '{title_key}' ingested: "
        f"{inserted_assets} new assets, {inserted_events} events written "
        f"({skipped} duplicates skipped)."
    )


@tool
def query_duckdb(sql: str) -> str:
    """
    Run a read-only SQL SELECT query against the DuckDB city_foundation database.
    Only SELECT statements are permitted.  Returns up to 30 rows as a table.
    """
    if not sql.strip().upper().startswith("SELECT"):
        return "❌  Only SELECT queries are allowed."
    try:
        conn = get_conn()
        df = conn.execute(sql).fetchdf()
        conn.close()
        return df.to_string(index=False, max_rows=30)
    except Exception as exc:
        return f"❌  Query error: {exc}"


@tool
def get_ingestion_status(dummy: str = "") -> str:
    """
    Returns a summary of the ingestion log and current row counts in DuckDB.
    Pass any string (or leave blank) as the argument.
    """
    try:
        conn = get_conn()
        summary = conn.execute("""
            SELECT
                (SELECT COUNT(*) FROM assets)                        AS total_assets,
                (SELECT COUNT(*) FROM events)                        AS total_events,
                (SELECT COUNT(DISTINCT department_owner) FROM assets) AS departments,
                (SELECT COUNT(DISTINCT asset_type)       FROM assets) AS asset_types
        """).fetchdf()

        by_dept = conn.execute("""
            SELECT department_owner, asset_type, COUNT(*) AS cnt
            FROM assets
            GROUP BY department_owner, asset_type
            ORDER BY cnt DESC
        """).fetchdf()

        log = conn.execute("""
            SELECT dataset_title, records_in, records_out, status, ran_at
            FROM ingestion_log
            ORDER BY ran_at DESC
            LIMIT 15
        """).fetchdf()
        conn.close()

        return (
            f"── DB Summary ──\n{summary.to_string(index=False)}\n\n"
            f"── Assets by Department / Type ──\n{by_dept.to_string(index=False)}\n\n"
            f"── Ingestion Log (latest 15) ──\n{log.to_string(index=False)}"
        )
    except Exception as exc:
        return f"❌  Status error: {exc}"


# ── Private helpers ────────────────────────────────────────────────────────────

def _log_run(
    run_id: str,
    title: str,
    url: str,
    records_in: int,
    records_out: int,
    status: str,
    error_msg: str | None,
    conn: duckdb.DuckDBPyConnection | None = None,
) -> None:
    close_after = conn is None
    if conn is None:
        conn = get_conn()
    conn.execute(
        """
        INSERT INTO ingestion_log
            (run_id, dataset_title, geojson_url,
             records_in, records_out, status, error_msg, ran_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [run_id, title, url, records_in, records_out, status, error_msg, _now()],
    )
    if close_after:
        conn.close()


# ── Agent setup ────────────────────────────────────────────────────────────────

TOOLS = [
    list_target_datasets,
    ingest_dataset_to_duckdb,
    query_duckdb,
    get_ingestion_status,
]

REACT_PROMPT = PromptTemplate.from_template("""
You are a municipal data ingestion agent for the City of Kitchener.
Your mission: ingest open GIS datasets from the Kitchener ArcGIS Hub portal
into DuckDB, mapping them to the MetricForge City Foundation schema
(tables: assets, events, accounts).

Available tools:
{tools}

Tool names (use exactly as written):
{tool_names}

Workflow — follow these steps in order, one tool call at a time:
1. Call list_target_datasets (once only) to get the list of resolvable dataset keys.
2. Call ingest_dataset_to_duckdb once for EACH key returned in step 1.
   Do NOT call list_target_datasets again between ingestions.
3. After ALL datasets are ingested, call get_ingestion_status once to confirm totals.

Rules:
- Only use title_keys that appear in the list returned by list_target_datasets.
- Do not fabricate GeoJSON URLs; they are resolved automatically.
- If a dataset fails, log the error and move on to the next one immediately.
- Never call the same tool twice for the same dataset.

{agent_scratchpad}

Question: {input}
""")


def build_agent(model: str = "llama3.2") -> AgentExecutor:
    llm = ChatOllama(model=model, temperature=0)
    agent = create_react_agent(llm, TOOLS, REACT_PROMPT)
    return AgentExecutor(
        agent=agent,
        tools=TOOLS,
        verbose=True,
        max_iterations=15,
        handle_parsing_errors=True,
    )


# ── Entrypoint ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("🏙️   Kitchener City Foundation — GIS Data Ingestion Agent")
    print("=" * 60)

    init_schema()

    executor = build_agent()

    print("\n🤖  Agent starting — each '>' below is one LLM thinking step.")
    print("    (llama3.2 runs locally; each step takes ~10-30s on Mac)\n", flush=True)

    result = executor.invoke(
        {
            "input": (
                "Ingest all target Kitchener GIS datasets into DuckDB. "
                "Call list_target_datasets once, then call ingest_dataset_to_duckdb "
                "for each key returned. After all are done, call get_ingestion_status."
            )
        }
    )

    print("\n── Final Answer ──")
    print(result["output"])

    # ── Demo cross-departmental query ──────────────────────────────────────────
    print("\n── Demo: Asset counts by department and type ──")
    conn = get_conn()
    demo = conn.execute("""
        SELECT department_owner, asset_type, COUNT(*) AS total
        FROM   assets
        GROUP  BY department_owner, asset_type
        ORDER  BY total DESC
    """).fetchdf()
    print(demo.to_string(index=False))

    print("\n── Demo: Recent events ──")
    recent = conn.execute("""
        SELECT event_type, event_subtype, department_source, COUNT(*) AS cnt
        FROM   events
        GROUP  BY event_type, event_subtype, department_source
        ORDER  BY cnt DESC
        LIMIT  10
    """).fetchdf()
    print(recent.to_string(index=False))
    conn.close()
