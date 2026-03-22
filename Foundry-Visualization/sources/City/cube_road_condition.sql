-- Road breakdown by classification and surface type.

SELECT
  road_classification                AS classification,
  surface_type,
  COUNT(*)                           AS segments
FROM city__local.roads_atomic_view
GROUP BY road_classification, surface_type
