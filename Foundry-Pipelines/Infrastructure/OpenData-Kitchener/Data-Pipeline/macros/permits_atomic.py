from sqlmesh import macro


@macro()
def permits_atomic_query(evaluator, table_type):
    query_suffix = ""
    if table_type == "table":
        query_suffix = """
    WHERE
        COALESCE(permits.ISSUED_DATE, permits.APPLICATION_DATE, TIMESTAMP '2020-01-01')
        BETWEEN @start_date AND @end_date
        """

    return f"""--sql
    SELECT
        permits.OBJECTID              AS permit_id,
        permits.PERMIT_NUMBER         AS permit_number,
        permits.PERMIT_TYPE           AS permit_type,
        permits.PERMIT_STATUS         AS permit_status,
        permits.WORK_TYPE             AS work_type,
        permits.DESCRIPTION           AS permit_description,
        permits.APPLICATION_DATE      AS application_date,
        permits.ISSUED_DATE           AS issued_date,
        permits.COMPLETED_DATE        AS completed_date,
        permits.ESTIMATED_VALUE       AS estimated_value,
        permits.ACTUAL_VALUE          AS actual_value,
        permits.ADDRESS               AS address,
        permits.WARD                  AS ward,
        permits.NEIGHBOURHOOD         AS neighbourhood,
        permits.CreatedDate           AS created_time,
        permits.EditDate              AS last_updated_time,
        COALESCE(permits.ISSUED_DATE, permits.APPLICATION_DATE, TIMESTAMP '2020-01-01')
                                      AS record_time
    FROM
        Foundry.normalized_opendata_extract.building_permits AS permits
    {query_suffix}
    """


@macro()
def permits_atomic_grain(evaluator):
    return "'grain (permit_id, record_time)'"
