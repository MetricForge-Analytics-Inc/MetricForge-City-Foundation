-- Water infrastructure by material and ward.

SELECT
  water_infrastructure.pipe_material  AS material,
  water_infrastructure.ward           AS ward,
  MEASURE(water_infrastructure.total_mains)        AS total_mains,
  MEASURE(water_infrastructure.total_length_km)    AS length_km,
  MEASURE(water_infrastructure.avg_diameter_mm)    AS avg_diameter_mm,
  MEASURE(water_infrastructure.avg_pipe_age_years) AS avg_age_years,
  MEASURE(water_infrastructure.oldest_install_year) AS oldest_year,
  MEASURE(water_infrastructure.newest_install_year) AS newest_year
GROUP BY 1, 2
