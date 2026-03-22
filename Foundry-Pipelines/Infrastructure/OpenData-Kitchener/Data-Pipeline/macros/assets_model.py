from sqlmesh import macro


_SRC_SCHEMA = "normalized_opendata_extract"


@macro()
def assets_query(evaluator, table_type):
    """
    Maps all Kitchener Open Data sources into the universal `assets` schema
    defined in db_schema.md.  One row per physical or logical municipal asset.

    Column names are lowercase (DLT normalizes them).
    Date fields from ArcGIS arrive as epoch-millisecond BIGINTs.
    """
    roads_filter = ""
    water_filter = ""
    permits_filter = ""
    wards_filter = ""

    if table_type == "table":
        roads_filter = (
            "WHERE COALESCE("
            "  CASE WHEN src.update_date IS NOT NULL "
            "       THEN epoch_ms(src.update_date) END, "
            "  CASE WHEN src.create_date IS NOT NULL "
            "       THEN epoch_ms(src.create_date) END, "
            "  TIMESTAMP '2020-01-01'"
            ") BETWEEN @start_date AND @end_date"
        )
        water_filter = (
            "WHERE COALESCE("
            "  CASE WHEN src.installation_date IS NOT NULL "
            "       THEN epoch_ms(src.installation_date) END, "
            "  TIMESTAMP '2020-01-01'"
            ") BETWEEN @start_date AND @end_date"
        )
        wards_filter = "WHERE TRUE"
        permits_filter = (
            "WHERE COALESCE("
            "  CASE WHEN src.issue_date IS NOT NULL "
            "       THEN epoch_ms(src.issue_date) END, "
            "  CASE WHEN src.application_date IS NOT NULL "
            "       THEN epoch_ms(src.application_date) END, "
            "  TIMESTAMP '2020-01-01'"
            ") BETWEEN @start_date AND @end_date"
        )

    return f"""--sql
    -- ── Roads → asset_type = 'road' ──────────────────────────────
    SELECT
        'kitchener_arcgis:road:' || CAST(src.objectid AS VARCHAR) AS asset_id,
        'road'                        AS asset_type,
        'engineering'                 AS department_owner,
        CAST(src.objectid AS VARCHAR) AS source_system_id,
        'kitchener_arcgis'            AS source_system,
        src.street                    AS label,
        NULL                          AS geom,
        NULL                          AS latitude,
        NULL                          AS longitude,
        COALESCE(src.status, 'active') AS status,
        'internal'                    AS privacy_class,
        CASE WHEN src.create_date IS NOT NULL
             THEN epoch_ms(src.create_date) END AS created_at,
        CASE WHEN src.update_date IS NOT NULL
             THEN epoch_ms(src.update_date) END AS updated_at,
        NULL                          AS valid_from,
        NULL                          AS valid_to,
        COALESCE(
          CASE WHEN src.update_date IS NOT NULL
               THEN epoch_ms(src.update_date) END,
          CASE WHEN src.create_date IS NOT NULL
               THEN epoch_ms(src.create_date) END,
          TIMESTAMP '2020-01-01'
        )                             AS record_time
    FROM {_SRC_SCHEMA}.road_segments AS src
    {roads_filter}

    UNION ALL

    -- ── Water Mains → asset_type = 'pipe' ────────────────────────
    SELECT
        'kitchener_arcgis:pipe:' || CAST(src.objectid AS VARCHAR),
        'pipe',
        'utilities',
        CAST(src.objectid AS VARCHAR),
        'kitchener_arcgis',
        'Water Main ' || CAST(src.objectid AS VARCHAR),
        NULL, NULL, NULL,
        COALESCE(src.status, 'active'),
        'internal',
        CASE WHEN src.installation_date IS NOT NULL
             THEN epoch_ms(src.installation_date) END,
        NULL,
        NULL, NULL,
        COALESCE(
          CASE WHEN src.installation_date IS NOT NULL
               THEN epoch_ms(src.installation_date) END,
          TIMESTAMP '2020-01-01'
        )
    FROM {_SRC_SCHEMA}.water_mains AS src
    {water_filter}

    UNION ALL

    -- ── Building Permits → asset_type = 'permit' ─────────────────
    SELECT
        'kitchener_arcgis:permit:' || CAST(src.objectid AS VARCHAR),
        'permit',
        'planning',
        COALESCE(src.permitno, CAST(src.objectid AS VARCHAR)),
        'kitchener_arcgis',
        src.foldername,
        NULL, NULL, NULL,
        CASE
            WHEN src.permit_status ILIKE '%complete%' THEN 'inactive'
            WHEN src.permit_status ILIKE '%cancel%'   THEN 'inactive'
            ELSE 'active'
        END,
        'internal',
        CASE WHEN src.application_date IS NOT NULL
             THEN epoch_ms(src.application_date) END,
        CASE WHEN src.issue_date IS NOT NULL
             THEN epoch_ms(src.issue_date) END,
        CASE WHEN src.application_date IS NOT NULL
             THEN CAST(epoch_ms(src.application_date) AS DATE) END,
        CASE WHEN src.final_date IS NOT NULL
             THEN CAST(epoch_ms(src.final_date) AS DATE) END,
        COALESCE(
          CASE WHEN src.issue_date IS NOT NULL
               THEN epoch_ms(src.issue_date) END,
          CASE WHEN src.application_date IS NOT NULL
               THEN epoch_ms(src.application_date) END,
          TIMESTAMP '2020-01-01'
        )
    FROM {_SRC_SCHEMA}.building_permits AS src
    {permits_filter}

    UNION ALL

    -- ── Ward Boundaries → asset_type = 'zone' ────────────────────
    SELECT
        'kitchener_arcgis:zone:ward_' || CAST(src.objectid AS VARCHAR),
        'zone',
        'governance',
        CAST(src.objectid AS VARCHAR),
        'kitchener_arcgis',
        src.ward,
        NULL, NULL, NULL,
        'active',
        'public',
        NULL,
        NULL,
        NULL, NULL,
        TIMESTAMP '2020-01-01'
    FROM {_SRC_SCHEMA}.ward_boundaries AS src
    {wards_filter}
    """


@macro()
def assets_grain(evaluator):
    return "'grain (asset_id, record_time)'"
