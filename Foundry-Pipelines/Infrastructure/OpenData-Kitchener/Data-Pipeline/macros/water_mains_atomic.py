from sqlmesh import macro


@macro()
def water_mains_atomic_query(evaluator, table_type):
    query_suffix = ""
    if table_type == "table":
        query_suffix = """
    WHERE
        COALESCE(mains.EditDate, mains.CreatedDate, TIMESTAMP '2020-01-01')
        BETWEEN @start_date AND @end_date
        """

    return f"""--sql
    SELECT
        mains.OBJECTID             AS main_id,
        mains.PIPE_MATERIAL        AS pipe_material,
        mains.DIAMETER             AS diameter_mm,
        mains.INSTALL_YEAR         AS install_year,
        mains.LENGTH_M             AS segment_length_m,
        mains.PRESSURE_ZONE        AS pressure_zone,
        mains.PIPE_STATUS          AS pipe_status,
        mains.OWNERSHIP            AS ownership,
        mains.WARD                 AS ward,
        mains.CreatedDate          AS created_time,
        mains.EditDate             AS last_updated_time,
        COALESCE(mains.EditDate, mains.CreatedDate, TIMESTAMP '2020-01-01')
                                   AS record_time
    FROM
        Foundry.normalized_opendata_extract.water_mains AS mains
    {query_suffix}
    """


@macro()
def water_mains_atomic_grain(evaluator):
    return "'grain (main_id, record_time)'"
