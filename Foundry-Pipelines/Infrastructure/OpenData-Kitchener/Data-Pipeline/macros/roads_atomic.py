from sqlmesh import macro


@macro()
def roads_atomic_query(evaluator):
    """Extracts road-specific attributes from the universal assets + events tables."""
    return """--sql
    SELECT
        CAST(a.source_system_id AS INTEGER)                                    AS road_id,
        json_extract_string(e.payload, '$.street')                             AS road_name,
        json_extract_string(e.payload, '$.carto_class')                        AS road_classification,
        json_extract_string(e.payload, '$.surface_type')                       AS surface_type,
        json_extract_string(e.payload, '$.category')                           AS category,
        json_extract_string(e.payload, '$.subcategory')                        AS subcategory,
        TRY_CAST(json_extract_string(e.payload, '$.lanes') AS INTEGER)         AS number_of_lanes,
        TRY_CAST(json_extract_string(e.payload, '$.speed_limit_km') AS INTEGER) AS speed_limit_kmh,
        TRY_CAST(json_extract_string(e.payload, '$.pavement_width') AS DOUBLE) AS pavement_width_m,
        json_extract_string(e.payload, '$.ownership')                          AS ownership,
        json_extract_string(e.payload, '$.status')                             AS road_status,
        TRY_CAST(json_extract_string(e.payload, '$.ward_id') AS INTEGER)       AS ward_id,
        a.created_at                                                           AS created_time,
        a.updated_at                                                           AS last_updated_time,
        a.record_time
    FROM city.assets_view AS a
    JOIN city.events_view AS e
        ON a.asset_id = e.asset_id
    WHERE a.asset_type = 'road'
      AND e.event_subtype = 'road_segment'
    """


@macro()
def roads_atomic_grain(evaluator):
    return "'grain (road_id, record_time)'"
