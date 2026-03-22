from sqlmesh import macro


@macro()
def permits_atomic_query(evaluator, table_type):
    query_suffix = ""
    if table_type == "table":
        query_suffix = """
    WHERE
        COALESCE(epoch_ms(permits.issue_date), epoch_ms(permits.application_date), TIMESTAMP '2020-01-01')
        BETWEEN @start_date AND @end_date
        """

    return f"""--sql
    SELECT
        permits.objectid              AS permit_id,
        permits.permitno              AS permit_number,
        permits.permit_type           AS permit_type,
        permits.permit_status         AS permit_status,
        permits.work_type             AS work_type,
        permits.sub_work_type         AS sub_work_type,
        permits.permit_description    AS permit_description,
        epoch_ms(permits.application_date) AS application_date,
        epoch_ms(permits.issue_date)      AS issued_date,
        epoch_ms(permits.final_date)      AS completed_date,
        epoch_ms(permits.expiry_date)     AS expiry_date,
        permits.issue_year            AS issue_year,
        permits.construction_value    AS estimated_value,
        permits.construction_value__v_double AS actual_value,
        permits.permit_fee            AS permit_fee,
        permits.foldername            AS address,
        permits.legal_description     AS legal_description,
        permits.roll_no               AS roll_no,
        permits.units_created         AS units_created,
        permits.units_net_change      AS units_net_change,
        permits.storeys_proposed      AS storeys_proposed,
        permits.total_units           AS total_units,
        permits.existing_gfa_m2       AS existing_gfa_m2,
        permits.proposed_gfa          AS proposed_gfa,
        permits.total_gfa_m2          AS total_gfa_m2,
        permits.new_floor_area_sqft   AS new_floor_area_sqft,
        permits.applicant             AS applicant,
        permits.issued_by             AS issued_by,
        permits.extraction_date       AS extraction_date,
        COALESCE(epoch_ms(permits.issue_date), epoch_ms(permits.application_date), TIMESTAMP '2020-01-01')
                                      AS record_time
    FROM
        Foundry.normalized_opendata_extract.building_permits AS permits
    {query_suffix}
    """


@macro()
def permits_atomic_grain(evaluator):
    return "'grain (permit_id, record_time)'"
