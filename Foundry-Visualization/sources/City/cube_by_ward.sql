-- Infrastructure breakdown by ward.

SELECT
  i.ward_id,
  i.ward_name,
  COUNT(*)                                  AS road_segments,
  MAX(i.total_water_mains)                  AS water_mains,
  MAX(i.ward_population)                    AS population
FROM city.infrastructure_integration_view AS i
GROUP BY i.ward_id, i.ward_name
