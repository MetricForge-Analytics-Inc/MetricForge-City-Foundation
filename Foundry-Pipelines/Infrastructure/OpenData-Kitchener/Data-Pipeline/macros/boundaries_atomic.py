from sqlmesh import macro


@macro()
def boundaries_atomic_query(evaluator, table_type):
    query_suffix = ""
    if table_type == "table":
        query_suffix = """
    WHERE
        COALESCE(wards.EditDate, wards.CreatedDate, TIMESTAMP '2020-01-01')
        BETWEEN @start_date AND @end_date
        """

    return f"""--sql
    SELECT
        wards.OBJECTID             AS ward_id,
        wards.WARD_NUM             AS ward_number,
        wards.WARD_NAME            AS ward_name,
        wards.COUNCILLOR           AS councillor,
        wards.AREA_SQ_KM           AS area_sq_km,
        wards.POPULATION           AS population,
        wards.CreatedDate          AS created_time,
        wards.EditDate             AS last_updated_time,
        COALESCE(wards.EditDate, wards.CreatedDate, TIMESTAMP '2020-01-01')
                                   AS record_time
    FROM
        Foundry.normalized_opendata_extract.ward_boundaries AS wards
    {query_suffix}
    """


@macro()
def boundaries_atomic_grain(evaluator):
    return "'grain (ward_id, record_time)'"
