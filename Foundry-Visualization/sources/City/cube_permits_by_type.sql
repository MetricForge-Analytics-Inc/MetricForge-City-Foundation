-- Permit activity by type and status via Cube semantic layer.

SELECT
  permit_type,
  permit_status,
  MEASURE(total_permits)            AS total,
  MEASURE(total_construction_value) AS total_value
FROM development_permits
GROUP BY 1, 2
