from sqlmesh import macro


@macro()
def roads_atomic_query(evaluator, table_type):
    query_suffix = ""
    if table_type == "table":
        query_suffix = """
    WHERE
        COALESCE(roads.EditDate, roads.CreatedDate, TIMESTAMP '2020-01-01')
        BETWEEN @start_date AND @end_date
        """

    return f"""--sql
    SELECT
        roads.OBJECTID             AS road_id,
        roads.ROAD_NAME            AS road_name,
        roads.ROAD_CLASS           AS road_classification,
        roads.SURFACE_TYPE         AS surface_type,
        roads.SURFACE_COND         AS surface_condition,
        roads.NUM_LANES            AS number_of_lanes,
        roads.SPEED_LIMIT          AS speed_limit_kmh,
        roads.LENGTH_M             AS segment_length_m,
        roads.OWNERSHIP            AS ownership,
        roads.MAINT_RESP           AS maintenance_responsibility,
        roads.WARD                 AS ward,
        roads.CreatedDate          AS created_time,
        roads.EditDate             AS last_updated_time,
        COALESCE(roads.EditDate, roads.CreatedDate, TIMESTAMP '2020-01-01')
                                   AS record_time
    FROM
        Foundry.normalized_opendata_extract.road_segments AS roads
    {query_suffix}
    """


@macro()
def roads_atomic_grain(evaluator):
    return "'grain (road_id, record_time)'"
