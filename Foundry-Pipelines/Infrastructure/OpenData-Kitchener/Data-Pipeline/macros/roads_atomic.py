from sqlmesh import macro


@macro()
def roads_atomic_query(evaluator, table_type):
    query_suffix = ""
    if table_type == "table":
        query_suffix = """
    WHERE
        COALESCE(epoch_ms(roads.update_date), epoch_ms(roads.create_date), TIMESTAMP '2020-01-01')
        BETWEEN @start_date AND @end_date
        """

    return f"""--sql
    SELECT
        roads.objectid             AS road_id,
        roads.roadsegmentid        AS road_segment_id,
        roads.street               AS road_name,
        roads.street_name          AS street_name,
        roads.street_type          AS street_type,
        roads.street_direction     AS street_direction,
        roads.from_street          AS from_street,
        roads.to_street            AS to_street,
        roads.carto_class          AS road_classification,
        roads.category             AS category,
        roads.subcategory          AS subcategory,
        roads.surface_layer_type   AS surface_type,
        roads.status               AS surface_condition,
        roads.lanes                AS number_of_lanes,
        roads.speed_limit_km       AS speed_limit_kmh,
        roads.shape__length        AS segment_length_m,
        roads.pavement_width       AS pavement_width,
        roads.row_width            AS row_width,
        roads.ownership            AS ownership,
        roads.maintenance          AS maintenance_responsibility,
        roads.operations_class     AS operations_class,
        roads.aadt                 AS aadt,
        roads.wardid               AS ward,
        epoch_ms(roads.create_date)  AS created_time,
        epoch_ms(roads.update_date)  AS last_updated_time,
        COALESCE(epoch_ms(roads.update_date), epoch_ms(roads.create_date), TIMESTAMP '2020-01-01')
                                   AS record_time
    FROM
        Foundry.normalized_opendata_extract.road_segments AS roads
    {query_suffix}
    """


@macro()
def roads_atomic_grain(evaluator):
    return "'grain (road_id, record_time)'"
