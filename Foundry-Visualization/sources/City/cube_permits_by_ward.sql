-- Permits by year with construction value context.

SELECT
  issue_year,
  COUNT(*)                                                             AS total_permits,
  SUM(construction_value)                                              AS total_value,
  SUM(units_created)                                                   AS total_units_created
FROM city__local.permits_atomic_view
GROUP BY issue_year
