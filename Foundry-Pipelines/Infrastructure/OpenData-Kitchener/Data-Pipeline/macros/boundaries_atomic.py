from sqlmesh import macro


@macro()
def boundaries_atomic_query(evaluator, table_type):
    query_suffix = ""
    if table_type == "table":
        query_suffix = """
    WHERE
        TIMESTAMP '2020-01-01'
        BETWEEN @start_date AND @end_date
        """

    return f"""--sql
    SELECT
        wards.objectid             AS ward_id,
        wards.wardid               AS ward_number,
        wards.ward                 AS ward_code,
        wards.maplabel1            AS ward_name,
        wards.councillor_name      AS councillor,
        wards.address              AS address,
        wards.postal_code          AS postal_code,
        wards.work_phone           AS work_phone,
        wards.email                AS email,
        wards.shape__area          AS area_sq_m,
        wards.shape__area / 1000000.0 AS area_sq_km,
        wards.mpac_population      AS population,
        wards.residential_household_count AS household_count,
        wards.mpac_voters          AS voters,
        wards.shape__length        AS perimeter_length,
        TIMESTAMP '2020-01-01'     AS record_time
    FROM
        Foundry.normalized_opendata_extract.ward_boundaries AS wards
    {query_suffix}
    """


@macro()
def boundaries_atomic_grain(evaluator):
    return "'grain (ward_id, record_time)'"
