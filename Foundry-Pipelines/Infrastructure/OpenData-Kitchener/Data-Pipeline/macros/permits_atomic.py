from sqlmesh import macro


@macro()
def permits_atomic_query(evaluator):
    """Extracts permit-specific attributes from the universal assets + events tables."""
    return """--sql
    SELECT
        a.source_system_id                                                               AS permit_id,
        json_extract_string(e.payload, '$.permit_number')                                AS permit_number,
        json_extract_string(e.payload, '$.permit_type')                                  AS permit_type,
        json_extract_string(e.payload, '$.permit_status')                                AS permit_status,
        json_extract_string(e.payload, '$.work_type')                                    AS work_type,
        json_extract_string(e.payload, '$.sub_work_type')                                AS sub_work_type,
        json_extract_string(e.payload, '$.description')                                  AS permit_description,
        TRY_CAST(json_extract_string(e.payload, '$.construction_value') AS DOUBLE)       AS construction_value,
        TRY_CAST(json_extract_string(e.payload, '$.total_units') AS INTEGER)             AS total_units,
        TRY_CAST(json_extract_string(e.payload, '$.units_created') AS INTEGER)           AS units_created,
        TRY_CAST(json_extract_string(e.payload, '$.units_lost') AS INTEGER)              AS units_lost,
        json_extract_string(e.payload, '$.folder_name')                                  AS address,
        TRY_CAST(json_extract_string(e.payload, '$.issue_year') AS INTEGER)              AS issue_year,
        a.created_at                                                                     AS application_date,
        a.updated_at                                                                     AS issued_date,
        a.record_time
    FROM city.assets_view AS a
    JOIN city.events_view AS e
        ON a.asset_id = e.asset_id
    WHERE a.asset_type = 'permit'
      AND e.event_type = 'permit_issued'
    """


@macro()
def permits_atomic_grain(evaluator):
    return "'grain (permit_id, record_time)'"
