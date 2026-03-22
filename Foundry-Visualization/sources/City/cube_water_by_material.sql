-- Water infrastructure by material.

SELECT
  pipe_material                       AS material,
  pipe_status,
  COUNT(*)                            AS total_mains,
  ROUND(AVG(pipe_size), 1)            AS avg_pipe_size,
  COUNT(DISTINCT pressure_zone)       AS pressure_zones
FROM city.water_mains_atomic_view
GROUP BY pipe_material, pipe_status
