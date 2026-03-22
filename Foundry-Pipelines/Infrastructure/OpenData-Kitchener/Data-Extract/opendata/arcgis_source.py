"""
ArcGIS Hub REST API source for DLT.

Pulls feature layers from Kitchener's Open Data portal using the
ArcGIS REST API query endpoint.  Each dataset is exposed as a DLT
resource that yields GeoJSON-style feature dicts.

Portal root:  https://open-kitchenergis.opendata.arcgis.com
REST pattern: https://services1.arcgis.com/<org_id>/arcgis/rest/services/<layer>/FeatureServer/0/query
"""

from typing import Any, Iterator

import dlt
from dlt.sources import DltResource
import requests

# ────────────────────────────────────────────────────────────────────
# Dataset catalog — maps a friendly name to the ArcGIS feature server URL.
# Add new layers here to include them in the pipeline.
# ────────────────────────────────────────────────────────────────────
DATASET_CATALOG: dict[str, dict[str, str]] = {
    # ── Infrastructure ──────────────────────────────────────────────
    "road_segments": {
        "url": "https://services1.arcgis.com/gE4bwEMEYBMnOIkR/arcgis/rest/services/Road_Segments/FeatureServer/0",
        "description": "Road network centrelines with classification, surface type, and condition.",
    },
    "bridges": {
        "url": "https://services1.arcgis.com/gE4bwEMEYBMnOIkR/arcgis/rest/services/Bridges/FeatureServer/0",
        "description": "Bridge assets with structural condition and inspection data.",
    },
    "water_mains": {
        "url": "https://services1.arcgis.com/gE4bwEMEYBMnOIkR/arcgis/rest/services/Water_Distribution_Mains/FeatureServer/0",
        "description": "Water distribution main pipes — material, diameter, install year.",
    },
    "sanitary_sewers": {
        "url": "https://services1.arcgis.com/gE4bwEMEYBMnOIkR/arcgis/rest/services/Sanitary_Sewers/FeatureServer/0",
        "description": "Sanitary sewer lines — material, diameter, install year.",
    },
    "storm_sewers": {
        "url": "https://services1.arcgis.com/gE4bwEMEYBMnOIkR/arcgis/rest/services/Storm_Sewers/FeatureServer/0",
        "description": "Storm sewer lines — material, diameter, install year.",
    },
    # ── Planning & Development ──────────────────────────────────────
    "building_permits": {
        "url": "https://services1.arcgis.com/gE4bwEMEYBMnOIkR/arcgis/rest/services/Building_Permits/FeatureServer/0",
        "description": "Building permit applications with status, type, and value.",
    },
    "zoning": {
        "url": "https://services1.arcgis.com/gE4bwEMEYBMnOIkR/arcgis/rest/services/Zoning/FeatureServer/0",
        "description": "Zoning polygons — land use category, permitted densities.",
    },
    "official_plan_land_use": {
        "url": "https://services1.arcgis.com/gE4bwEMEYBMnOIkR/arcgis/rest/services/Official_Plan_Land_Use/FeatureServer/0",
        "description": "Official plan designations for land use across the city.",
    },
    # ── Boundaries & Geography ──────────────────────────────────────
    "ward_boundaries": {
        "url": "https://services1.arcgis.com/gE4bwEMEYBMnOIkR/arcgis/rest/services/Ward_Boundaries/FeatureServer/0",
        "description": "Electoral ward boundary polygons.",
    },
    "neighbourhood_boundaries": {
        "url": "https://services1.arcgis.com/gE4bwEMEYBMnOIkR/arcgis/rest/services/Neighbourhood_Planning_Boundaries/FeatureServer/0",
        "description": "Neighbourhood planning area boundaries.",
    },
    # ── Parks & Environment ─────────────────────────────────────────
    "parks": {
        "url": "https://services1.arcgis.com/gE4bwEMEYBMnOIkR/arcgis/rest/services/Parks/FeatureServer/0",
        "description": "City parks — names, area, amenities.",
    },
    "tree_inventory": {
        "url": "https://services1.arcgis.com/gE4bwEMEYBMnOIkR/arcgis/rest/services/Tree_Inventory/FeatureServer/0",
        "description": "Street and park trees with species, diameter, condition.",
    },
    # ── Transit ─────────────────────────────────────────────────────
    "transit_routes": {
        "url": "https://services1.arcgis.com/gE4bwEMEYBMnOIkR/arcgis/rest/services/GRT_Routes/FeatureServer/0",
        "description": "Grand River Transit route lines.",
    },
    "transit_stops": {
        "url": "https://services1.arcgis.com/gE4bwEMEYBMnOIkR/arcgis/rest/services/GRT_Stops/FeatureServer/0",
        "description": "Grand River Transit stop locations.",
    },
    # ── Property & Assessment ───────────────────────────────────────
    "property_boundaries": {
        "url": "https://services1.arcgis.com/gE4bwEMEYBMnOIkR/arcgis/rest/services/Property_Boundaries/FeatureServer/0",
        "description": "Legal property boundary polygons.",
    },
}

# Maximum records per ArcGIS REST request (server cap is usually 1000–2000).
_PAGE_SIZE = 1000


def _fetch_features(
    base_url: str,
    where: str = "1=1",
) -> Iterator[dict[str, Any]]:
    """
    Paginate through an ArcGIS Feature Server layer using result offsets.

    Yields one dict per feature (attributes only — geometry is dropped for
    the analytical warehouse; add ``&returnGeometry=true`` if needed later).
    """
    offset = 0
    while True:
        params = {
            "where": where,
            "outFields": "*",
            "returnGeometry": "false",
            "resultOffset": offset,
            "resultRecordCount": _PAGE_SIZE,
            "f": "json",
        }
        resp = requests.get(f"{base_url}/query", params=params, timeout=120)
        resp.raise_for_status()
        payload = resp.json()

        features = payload.get("features", [])
        if not features:
            break

        for feat in features:
            yield feat.get("attributes", {})

        # ArcGIS signals "no more pages" by returning fewer than requested
        # or by including exceededTransferLimit=false.
        if len(features) < _PAGE_SIZE:
            break
        if not payload.get("exceededTransferLimit", True):
            break

        offset += _PAGE_SIZE


@dlt.source(name="kitchener_opendata")
def kitchener_opendata(
    datasets: list[str] | None = None,
) -> list[DltResource]:
    """
    DLT source that exposes each Kitchener Open Data layer as a resource.

    Parameters
    ----------
    datasets : list[str] | None
        Subset of dataset keys from ``DATASET_CATALOG`` to load.
        Loads all datasets when ``None``.
    """
    keys = datasets or list(DATASET_CATALOG.keys())

    resources: list[DltResource] = []
    for key in keys:
        entry = DATASET_CATALOG[key]

        @dlt.resource(name=key, write_disposition="replace")
        def _resource(
            _url: str = entry["url"],
        ) -> Iterator[dict[str, Any]]:
            yield from _fetch_features(_url)

        resources.append(_resource)

    return resources
