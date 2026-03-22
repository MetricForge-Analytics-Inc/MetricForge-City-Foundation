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
        permits.permit_description,
        permits.application_date,
        permits.issued_date,
        permits.completed_date,
        permits.estimated_value,
        permits.actual_value,
        permits.address,
        permits.ward,
        permits.neighbourhood,
        permits.record_time,

        -- Ward context
        wards.ward_name,
        wards.councillor,
        wards.population            AS ward_population,
        wards.area_sq_km            AS ward_area_sq_km,

        -- Infrastructure capacity in same ward (water mains as proxy)
        water_agg.total_water_mains AS ward_water_mains,
        water_agg.oldest_install_year AS ward_oldest_water_year,
        water_agg.total_water_length_m AS ward_water_network_length_m,

        -- Development intensity metrics per ward
        dev_agg.total_permits_in_ward,
        dev_agg.total_estimated_value_in_ward,
        dev_agg.residential_permits_in_ward

    FROM
        Foundry.city.permits_atomic_{table_type} AS permits

    LEFT JOIN
        Foundry.city.boundaries_atomic_{table_type} AS wards
    ON
        permits.ward = wards.ward_number

    LEFT JOIN (
        SELECT
            ward,
            COUNT(*)                   AS total_water_mains,
            MIN(install_year)          AS oldest_install_year,
            SUM(segment_length_m)      AS total_water_length_m
        FROM
            Foundry.city.water_mains_atomic_{table_type}
        GROUP BY
            ward
    ) AS water_agg
    ON
        permits.ward = water_agg.ward

    LEFT JOIN (
        SELECT
            ward,
            COUNT(*)                   AS total_permits_in_ward,
            SUM(estimated_value)       AS total_estimated_value_in_ward,
            SUM(CASE WHEN permit_type ILIKE '%residential%' THEN 1 ELSE 0 END)
                                       AS residential_permits_in_ward
        FROM
            Foundry.city.permits_atomic_{table_type}
        GROUP BY
            ward
    ) AS dev_agg
    ON
        permits.ward = dev_agg.ward

    {query_suffix}
    """


@macro()
def development_details_grain(evaluator):
    return "'grain (permit_id, record_time)'"
