-- Road breakdown by classification and surface type via Cube semantic layer.

SELECT
  road_classification   AS classification,
  surface_type,
  MEASURE(total_road_segments) AS segments
FROM infrastructure_assets
GROUP BY 1, 2
