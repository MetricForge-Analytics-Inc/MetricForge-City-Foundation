-- City KPIs: pre-computed aggregate measures across all cubes.
-- Runs against the Cube.js Postgres SQL API.

SELECT
  -- Infrastructure
  MEASURE(infrastructure_assets.total_road_segments)    AS total_road_segments,
  MEASURE(infrastructure_assets.total_road_length_km)   AS total_road_length_km,

  -- Water
  MEASURE(water_infrastructure.total_mains)             AS total_water_mains,
  MEASURE(water_infrastructure.total_length_km)         AS total_water_network_km,
  MEASURE(water_infrastructure.avg_pipe_age_years)      AS avg_pipe_age_years,
  MEASURE(water_infrastructure.oldest_install_year)     AS oldest_water_install_year,

  -- Development
  MEASURE(development_permits.total_permits)            AS total_permits,
  MEASURE(development_permits.total_estimated_value)    AS total_permit_value,
  MEASURE(development_permits.avg_estimated_value)      AS avg_permit_value,
  MEASURE(development_permits.residential_permits)      AS residential_permits,
  MEASURE(development_permits.commercial_permits)       AS commercial_permits,
  MEASURE(development_permits.completed_permits)        AS completed_permits,

  -- Wards
  MEASURE(ward_overview.total_wards)                    AS total_wards,
  MEASURE(ward_overview.total_population)               AS total_population,
  MEASURE(ward_overview.total_area_sq_km)               AS total_area_sq_km
