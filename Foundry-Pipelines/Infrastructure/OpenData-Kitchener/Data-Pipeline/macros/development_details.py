from sqlmesh import macro


@macro()
def development_details_query(evaluator):
    """
    Enriches building permits with ward context and development
    intensity metrics — enables housing vs infrastructure analysis.
    Queries from the universal-schema-backed analytical views.
    """
    return """--sql
    SELECT
        permits.permit_id,
        permits.permit_number,
        permits.permit_type,
        permits.permit_status,
        permits.work_type,
        permits.sub_work_type,
        permits.permit_description,
        permits.construction_value,
        permits.total_units,
        permits.units_created,
        permits.units_lost,
        permits.address,
        permits.issue_year,
        permits.application_date,
        permits.issued_date,
        permits.record_time,

        -- Development intensity metrics per ward (using issue_year grouping)
        dev_agg.total_permits,
        dev_agg.total_construction_value,
        dev_agg.total_units_created

    FROM
        city.permits_atomic_view AS permits

    LEFT JOIN (
        SELECT
            issue_year,
            COUNT(*)                           AS total_permits,
            SUM(construction_value)            AS total_construction_value,
            SUM(units_created)                 AS total_units_created
        FROM
            city.permits_atomic_view
        GROUP BY
            issue_year
    ) AS dev_agg
    ON
        permits.issue_year = dev_agg.issue_year
    """


@macro()
def development_details_grain(evaluator):
    return "'grain (permit_id, record_time)'"
