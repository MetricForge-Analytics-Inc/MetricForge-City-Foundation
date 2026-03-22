from sqlmesh import macro


@macro()
def infrastructure_integration_query(evaluator, table_type):
    """
    Joins roads and water mains by ward to create a cross-departmental
    infrastructure view — the first step toward coordinated planning.
    """
    query_suffix = ""
    if table_type == "table":
        query_suffix = """
    WHERE
        roads.record_time BETWEEN @start_date AND @end_date
        """

    return f"""--sql
    SELECT
        roads.road_id,
        roads.road_name,
        roads.road_classification,
        roads.surface_type,
        roads.surface_condition,
        roads.number_of_lanes,
        roads.speed_limit_kmh,
        roads.segment_length_m   AS road_length_m,
        roads.ownership          AS road_ownership,
        roads.maintenance_responsibility,
        roads.ward,
        roads.record_time,

        -- Ward context (cross-departmental join)
        wards.ward_name,
        wards.councillor,
        wards.area_sq_km         AS ward_area_sq_km,
        wards.population         AS ward_population,

        -- Water infrastructure on same road segment (aggregated)
        water_agg.total_water_mains,
        water_agg.avg_pipe_diameter_mm,
        water_agg.oldest_install_year,
        water_agg.total_water_length_m

    FROM
        Foundry.city.roads_atomic_{table_type} AS roads

    LEFT JOIN
        Foundry.city.boundaries_atomic_{table_type} AS wards
    ON
        roads.ward = wards.ward_number

    LEFT JOIN (
        SELECT
            road_segment_id,
            COUNT(*)                   AS total_water_mains,
            ROUND(AVG(diameter_mm), 1) AS avg_pipe_diameter_mm,
            MIN(install_year)          AS oldest_install_year,
            SUM(segment_length_m)      AS total_water_length_m
        FROM
            Foundry.city.water_mains_atomic_{table_type}
        GROUP BY
            road_segment_id
    ) AS water_agg
    ON
        roads.road_segment_id = water_agg.road_segment_id

    {query_suffix}
    """


@macro()
def infrastructure_integration_grain(evaluator):
    return "'grain (road_id, record_time)'"
