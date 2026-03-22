"""
Kitchener Open Data DLT pipeline.

Extracts datasets from the City of Kitchener ArcGIS Open Data portal
and loads them into a local DuckDB as a normalized landing schema.
"""
import time
from pathlib import Path
from typing import Any

import dlt

from opendata import kitchener_opendata, DATASET_CATALOG

# Resolve the shared DuckDB file so DLT and SQLMesh use the same database.
_WORKSPACE_ROOT = Path(__file__).resolve().parents[4]
_DB_PATH = str(_WORKSPACE_ROOT / "db" / "metricforge.duckdb")


def load_all_datasets() -> Any:
    """Load every registered dataset from the catalog."""
    pipeline = dlt.pipeline(
        pipeline_name="dlt_kitchener_opendata",
        destination=dlt.destinations.duckdb(_DB_PATH),
        dev_mode=False,
        dataset_name="normalized_opendata_extract",
    )
    data = kitchener_opendata()
    info = pipeline.run(data=data)
    return info


def load_infrastructure_only() -> Any:
    """Load only infrastructure-related layers (roads, water, sewers, bridges)."""
    pipeline = dlt.pipeline(
        pipeline_name="dlt_kitchener_opendata",
        destination=dlt.destinations.duckdb(_DB_PATH),
        dev_mode=False,
        dataset_name="normalized_opendata_extract",
    )
    infra_keys = [
        "road_segments",
        "bridges",
        "water_mains",
        "sanitary_sewers",
        "storm_sewers",
    ]
    data = kitchener_opendata(datasets=infra_keys)
    info = pipeline.run(data=data)
    return info


def load_planning_only() -> Any:
    """Load only planning & development layers."""
    pipeline = dlt.pipeline(
        pipeline_name="dlt_kitchener_opendata",
        destination=dlt.destinations.duckdb(_DB_PATH),
        dev_mode=False,
        dataset_name="normalized_opendata_extract",
    )
    planning_keys = [
        "building_permits",
        "ward_boundaries",
        "neighbourhood_boundaries",
        "property_boundaries",
    ]
    data = kitchener_opendata(datasets=planning_keys)
    info = pipeline.run(data=data)
    return info


def load_parks_and_environment() -> Any:
    """Load parks and tree inventory."""
    pipeline = dlt.pipeline(
        pipeline_name="dlt_kitchener_opendata",
        destination=dlt.destinations.duckdb(_DB_PATH),
        dev_mode=False,
        dataset_name="normalized_opendata_extract",
    )
    keys = [
        "parks",
        "tree_inventory",
    ]
    data = kitchener_opendata(datasets=keys)
    info = pipeline.run(data=data)
    return info


if __name__ == "__main__":
    start = time.time()
    load_info = load_all_datasets()
    elapsed = time.time() - start
    print(load_info)
    print(f"Time taken: {elapsed:.1f}s")
