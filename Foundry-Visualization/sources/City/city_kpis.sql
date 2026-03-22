-- City KPIs: pre-computed aggregate measures across all views.
-- Runs directly against the local DuckDB warehouse.

SELECT
  -- Infrastructure
  infra.total_road_segments,

  -- Water
  water.total_water_mains,
  water.distinct_materials,

  -- Development
  dev.total_permits,
  dev.total_construction_value,
  dev.total_units_created,

  -- Wards
  wards.total_wards,
  wards.total_population

FROM (
  SELECT
    COUNT(*)  AS total_road_segments
  FROM city.roads_atomic_view
) AS infra

CROSS JOIN (
  SELECT
    COUNT(*)                         AS total_water_mains,
    COUNT(DISTINCT pipe_material)    AS distinct_materials
  FROM city.water_mains_atomic_view
) AS water

CROSS JOIN (
  SELECT
    COUNT(*)                  AS total_permits,
    SUM(construction_value)   AS total_construction_value,
    SUM(units_created)        AS total_units_created
  FROM city.permits_atomic_view
) AS dev

CROSS JOIN (
  SELECT
    COUNT(*)         AS total_wards,
    SUM(population)  AS total_population
  FROM city.boundaries_atomic_view
) AS wards
