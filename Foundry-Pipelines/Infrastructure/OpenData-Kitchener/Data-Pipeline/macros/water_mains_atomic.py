from sqlmesh import macro


@macro()
def water_mains_atomic_query(evaluator):
    """Extracts water-main-specific attributes from the universal assets + events tables."""
    return """--sql
    SELECT
        CAST(a.source_system_id AS INTEGER)                                      AS main_id,
        json_extract_string(e.payload, '$.material')                             AS pipe_material,
        TRY_CAST(json_extract_string(e.payload, '$.pipe_size') AS DOUBLE)        AS pipe_size,
        json_extract_string(e.payload, '$.pressure_zone')                        AS pressure_zone,
        json_extract_string(e.payload, '$.status')                               AS pipe_status,
        json_extract_string(e.payload, '$.category')                             AS category,
        json_extract_string(e.payload, '$.lined')                                AS lined,
        json_extract_string(e.payload, '$.ownership')                            AS ownership,
        TRY_CAST(json_extract_string(e.payload, '$.condition_score') AS DOUBLE)  AS condition_score,
        json_extract_string(e.payload, '$.criticality')                          AS criticality,
        a.created_at                                                             AS install_date,
        a.record_time
    FROM city.assets_view AS a
    JOIN city.events_view AS e
        ON a.asset_id = e.asset_id
    WHERE a.asset_type = 'pipe'
      AND e.event_subtype = 'water_main'
    """


@macro()
def water_mains_atomic_grain(evaluator):
    return "'grain (main_id, record_time)'"
