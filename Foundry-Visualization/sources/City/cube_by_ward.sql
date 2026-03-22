-- Infrastructure breakdown by ward.

SELECT
  infrastructure_assets.ward                                     AS ward,
  infrastructure_assets.ward_name                                AS ward_name,
  MEASURE(infrastructure_assets.total_road_segments)             AS road_segments,
  MEASURE(infrastructure_assets.total_road_length_km)            AS road_length_km,
  MEASURE(infrastructure_assets.total_water_mains_in_ward)       AS water_mains,
  MEASURE(infrastructure_assets.total_water_network_km)          AS water_network_km,
  MEASURE(infrastructure_assets.oldest_water_infrastructure_year) AS oldest_water_year,
  MEASURE(infrastructure_assets.ward_population)                 AS population
GROUP BY 1, 2
