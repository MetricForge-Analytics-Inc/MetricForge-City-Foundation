-- Infrastructure breakdown by ward via Cube semantic layer.

SELECT
  ward_name,
  MEASURE(total_road_segments)        AS road_segments,
  MEASURE(total_water_mains_in_ward)  AS water_mains,
  MEASURE(ward_population)            AS population,
  MEASURE(ward_households)            AS households,
  MEASURE(distinct_pipe_materials)    AS distinct_materials
FROM infrastructure_assets
GROUP BY 1
