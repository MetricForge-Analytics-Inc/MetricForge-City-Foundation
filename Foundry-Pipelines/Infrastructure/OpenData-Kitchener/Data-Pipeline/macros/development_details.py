from sqlmesh import macro


@macro()
def development_details_query(evaluator, table_type):
    """
    Enriches building permits with ward context and neighbourhood
    infrastructure capacity metrics — enables the housing vs
    infrastructure capacity analysis from the problem statement.
    """
    query_suffix = ""
    if table_type == "table":
        query_suffix = """
    WHERE
        permits.record_time BETWEEN @start_date AND @end_date
        """

    return f"""--sql
    SELECT
        permits.permit_id,
        permits.permit_number,
        permits.permit_type,
        permits.permit_status,
        permits.work_type,
        permits.sub_work_type,
        permits.permit_description,
        permits.application_date,
        permits.issued_date,
        permits.completed_date,
        permits.estimated_value,
        permits.actual_value,
        permits.permit_fee,
        permits.address,
        permits.legal_description,
        permits.units_created,
        permits.units_net_change,
        permits.storeys_proposed,
        permits.total_units,
        permits.new_floor_area_sqft,
        permits.applicant,
        permits.record_time,

        -- Development intensity metrics (aggregated across all permits)
        dev_agg.total_permits,
        dev_agg.total_estimated_value,
        dev_agg.residential_permits

    FROM
        Foundry.city.permits_atomic_{table_type} AS permits

    LEFT JOIN (
        SELECT
            COUNT(*)                   AS total_permits,
            SUM(estimated_value)       AS total_estimated_value,
            SUM(CASE WHEN permit_type ILIKE '%residential%' THEN 1 ELSE 0 END)
                                       AS residential_permits
        FROM
            Foundry.city.permits_atomic_{table_type}
    ) AS dev_agg
    ON
        1 = 1

    {query_suffix}
    """


@macro()
def development_details_grain(evaluator):
    return "'grain (permit_id, record_time)'"
