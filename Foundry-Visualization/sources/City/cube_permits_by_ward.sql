-- Permit trends by issue year via Cube semantic layer.

SELECT
  issue_year,
  MEASURE(total_permits)              AS total_permits,
  MEASURE(total_construction_value)   AS total_value,
  MEASURE(total_units_created)        AS total_units_created,
  MEASURE(residential_permits)        AS residential_permits,
  MEASURE(commercial_permits)         AS commercial_permits
FROM development_permits
GROUP BY 1
ORDER BY 1
