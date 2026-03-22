-- City KPIs: aggregate measures from all Cube semantic cubes.
-- Queries the Cube.js SQL API (Postgres wire protocol on port 15432).

SELECT
  infra.total_road_segments,
  water.total_water_mains,
  water.avg_pipe_age_years,
  water.avg_condition_score,
  dev.total_permits,
  dev.total_construction_value,
  dev.avg_construction_value,
  dev.total_units_created,
  dev.residential_permits,
  dev.commercial_permits,
  dev.completed_permits,
  wards.total_wards,
  wards.total_population,
  wards.total_residential_households,
  wards.total_voters

FROM (
  SELECT
    MEASURE(total_road_segments)  AS total_road_segments
  FROM infrastructure_assets
) AS infra

CROSS JOIN (
  SELECT
    MEASURE(total_mains)          AS total_water_mains,
    MEASURE(avg_pipe_age_years)   AS avg_pipe_age_years,
    MEASURE(avg_condition_score)  AS avg_condition_score
  FROM water_infrastructure
) AS water

CROSS JOIN (
  SELECT
    MEASURE(total_permits)              AS total_permits,
    MEASURE(total_construction_value)   AS total_construction_value,
    MEASURE(avg_construction_value)     AS avg_construction_value,
    MEASURE(total_units_created)        AS total_units_created,
    MEASURE(residential_permits)        AS residential_permits,
    MEASURE(commercial_permits)         AS commercial_permits,
    MEASURE(completed_permits)          AS completed_permits
  FROM development_permits
) AS dev

CROSS JOIN (
  SELECT
    MEASURE(total_wards)                    AS total_wards,
    MEASURE(total_population)               AS total_population,
    MEASURE(total_residential_households)   AS total_residential_households,
    MEASURE(total_voters)                   AS total_voters
  FROM ward_overview
) AS wards
