from sqlmesh import macro


@macro()
def boundaries_atomic_query(evaluator):
    """Extracts ward-boundary attributes from the universal assets + events tables."""
    return """--sql
    SELECT
        CAST(a.source_system_id AS INTEGER)                                           AS ward_id,
        TRY_CAST(json_extract_string(e.payload, '$.ward_id') AS INTEGER)              AS ward_number,
        json_extract_string(e.payload, '$.ward_name')                                 AS ward_name,
        json_extract_string(e.payload, '$.councillor_name')                           AS councillor,
        TRY_CAST(json_extract_string(e.payload, '$.residential_households') AS INTEGER) AS residential_households,
        TRY_CAST(json_extract_string(e.payload, '$.mpac_population') AS INTEGER)      AS population,
        TRY_CAST(json_extract_string(e.payload, '$.mpac_voters') AS INTEGER)          AS voters,
        a.record_time
    FROM city.assets_view AS a
    JOIN city.events_view AS e
        ON a.asset_id = e.asset_id
    WHERE a.asset_type = 'zone'
      AND e.event_subtype = 'ward_boundary'
    """


@macro()
def boundaries_atomic_grain(evaluator):
    return "'grain (ward_id, record_time)'"
