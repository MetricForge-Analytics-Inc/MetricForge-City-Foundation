-- Permit activity by type and status.

SELECT
  development_permits.permit_type     AS permit_type,
  development_permits.permit_status   AS permit_status,
  MEASURE(development_permits.total_permits)         AS total,
  MEASURE(development_permits.total_estimated_value) AS estimated_value,
  MEASURE(development_permits.total_actual_value)    AS actual_value
GROUP BY 1, 2
