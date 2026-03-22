-- Permits by ward with infrastructure capacity context.

SELECT
  development_permits.ward            AS ward,
  development_permits.ward_name       AS ward_name,
  MEASURE(development_permits.total_permits)          AS total_permits,
  MEASURE(development_permits.residential_permits)    AS residential_permits,
  MEASURE(development_permits.total_estimated_value)  AS total_value,
  MEASURE(development_permits.ward_water_mains)       AS water_mains,
  MEASURE(development_permits.ward_population)        AS population,
  MEASURE(development_permits.development_intensity)  AS development_intensity
GROUP BY 1, 2
