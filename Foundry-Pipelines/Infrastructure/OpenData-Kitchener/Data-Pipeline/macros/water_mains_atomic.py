from sqlmesh import macro


@macro()
def water_mains_atomic_query(evaluator, table_type):
    query_suffix = ""
    if table_type == "table":
        query_suffix = """
    WHERE
        COALESCE(epoch_ms(mains.installation_date), TIMESTAMP '2020-01-01')
        BETWEEN @start_date AND @end_date
        """

    return f"""--sql
    SELECT
        mains.objectid             AS main_id,
        mains.watmainid            AS water_main_id,
        mains.material             AS pipe_material,
        mains.pipe_size            AS diameter_mm,
        YEAR(epoch_ms(mains.installation_date)) AS install_year,
        epoch_ms(mains.installation_date) AS installation_date,
        mains.shape__length        AS segment_length_m,
        mains.pressure_zone        AS pressure_zone,
        mains.status               AS pipe_status,
        mains.category             AS category,
        mains.ownership            AS ownership,
        mains.lined                AS lined,
        mains.lined_material       AS lined_material,
        mains.bridge_main          AS bridge_main,
        mains.criticality          AS criticality,
        mains.condition_score      AS condition_score,
        mains.roadsegmentid        AS road_segment_id,
        COALESCE(epoch_ms(mains.installation_date), TIMESTAMP '2020-01-01')
                                   AS record_time
    FROM
        Foundry.normalized_opendata_extract.water_mains AS mains
    {query_suffix}
    """


@macro()
def water_mains_atomic_grain(evaluator):
    return "'grain (main_id, record_time)'"
