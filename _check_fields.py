"""Check field names for each ArcGIS feature service."""
import requests
import json

SERVICES = {
    "Roads": "https://services1.arcgis.com/qAo1OsXi67t7XgmS/arcgis/rest/services/Roads/FeatureServer/0",
    "Water_Mains": "https://services1.arcgis.com/qAo1OsXi67t7XgmS/arcgis/rest/services/Water_Mains/FeatureServer/0",
    "Building_Permits": "https://services1.arcgis.com/qAo1OsXi67t7XgmS/arcgis/rest/services/Building_Permits/FeatureServer/0",
    "Wards": "https://services1.arcgis.com/qAo1OsXi67t7XgmS/arcgis/rest/services/Wards/FeatureServer/0",
    "Bridge": "https://services1.arcgis.com/qAo1OsXi67t7XgmS/arcgis/rest/services/Bridge/FeatureServer/0",
}

for name, url in SERVICES.items():
    print(f"\n=== {name} ===")
    r = requests.get(f"{url}/query", params={
        "where": "1=1",
        "outFields": "*",
        "returnGeometry": "false",
        "resultRecordCount": 1,
        "f": "json",
    }, timeout=30)
    data = r.json()
    features = data.get("features", [])
    if features:
        attrs = features[0].get("attributes", {})
        print("Fields:", list(attrs.keys()))
    else:
        print("ERROR:", data.get("error", "No features"))
