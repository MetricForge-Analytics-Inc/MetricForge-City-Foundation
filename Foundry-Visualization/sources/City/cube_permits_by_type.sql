-- Permit activity by type and status.

SELECT
  permit_type,
  permit_status,
  COUNT(*)                    AS total,
  SUM(construction_value)     AS total_value
FROM city__local.permits_atomic_view
GROUP BY permit_type, permit_status
