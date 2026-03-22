-- Road condition breakdown.

SELECT
  infrastructure_assets.surface_condition  AS condition,
  infrastructure_assets.road_classification AS classification,
  MEASURE(infrastructure_assets.total_road_segments) AS segments,
  MEASURE(infrastructure_assets.total_road_length_km) AS length_km
GROUP BY 1, 2
