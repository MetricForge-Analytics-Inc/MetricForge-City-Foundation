-- Water infrastructure by material via Cube semantic layer.

SELECT
  pipe_material                    AS material,
  pipe_status,
  MEASURE(total_mains)             AS total_mains,
  MEASURE(avg_pipe_size)           AS avg_pipe_size,
  MEASURE(avg_condition_score)     AS avg_condition_score,
  MEASURE(avg_criticality)         AS avg_criticality,
  MEASURE(avg_pipe_age_years)      AS avg_age_years
FROM water_infrastructure
GROUP BY 1, 2
