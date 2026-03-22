"""Temporary script to discover Kitchener Open Data ArcGIS feature service URLs."""
import requests
import json

# Get ALL datasets from the Kitchener group
all_datasets = []
next_url = "https://open-kitchenergis.opendata.arcgis.com/api/v3/datasets"
params = {
    "filter[groupIds]": "29614814565e4342bbc6938cd461d5b4",
    "page[size]": "100",
}
while next_url:
    r = requests.get(next_url, params=params, timeout=30)
    data = r.json()
    all_datasets.extend(data.get("data", []))
    next_url = data.get("links", {}).get("next")
    params = {}  # next_url has params already

print(f"Total datasets: {len(all_datasets)}")

# We need: road_segments, bridges, water_mains (water distribution mains),
# sanitary_sewers, storm_sewers, building_permits, zoning, official_plan_land_use,
# ward_boundaries, neighbourhood_boundaries, parks, tree_inventory,
# transit_routes (GRT), transit_stops (GRT), property_boundaries

KEYWORDS = [
    "road", "bridge", "water", "sanitary", "storm", "sewer",
    "building", "permit", "zoning", "official_plan", "land_use",
    "ward", "neighbourhood", "park", "tree", "transit", "grt",
    "property", "boundaries",
]

for d in all_datasets:
    attrs = d.get("attributes", {})
    name = attrs.get("name", "")
    url = attrs.get("url", "")
    name_lower = name.lower()
    if any(kw in name_lower for kw in KEYWORDS):
        print(f"  {name}  ->  {url}")
