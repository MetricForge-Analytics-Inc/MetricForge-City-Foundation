from sqlmesh import macro


@macro()
def assets_query(evaluator, table_type):
    """
    Maps all Kitchener Open Data sources into the universal `assets` schema
    defined in db_schema.md.  One row per physical or logical municipal asset.

    Field names match the actual Kitchener ArcGIS feature services.
    Date fields from ArcGIS arrive as epoch-millisecond integers.
    """
    roads_filter = ""
    water_filter = ""
    permits_filter = ""
    wards_filter = ""

    if table_type == "table":
        roads_filter = (
            "WHERE COALESCE("
            "  CASE WHEN src.UPDATE_DATE IS NOT NULL "
            "       THEN epoch_ms(src.UPDATE_DATE) END, "
            "  CASE WHEN src.CREATE_DATE IS NOT NULL "
            "       THEN epoch_ms(src.CREATE_DATE) END, "
            "  TIMESTAMP '2020-01-01'"
            ") BETWEEN @start_date AND @end_date"
        )
        water_filter = (
            "WHERE COALESCE("
            "  CASE WHEN src.INSTALLATION_DATE IS NOT NULL "
            "       THEN epoch_ms(src.INSTALLATION_DATE) END, "
            "  TIMESTAMP '2020-01-01'"
            ") BETWEEN @start_date AND @end_date"
        )
        wards_filter = "WHERE TRUE"  # wards have no date fields
        permits_filter = (
            "WHERE COALESCE("
            "  CASE WHEN src.ISSUE_DATE IS NOT NULL "
            "       THEN epoch_ms(src.ISSUE_DATE) END, "
            "  CASE WHEN src.APPLICATION_DATE IS NOT NULL "
            "       THEN epoch_ms(src.APPLICATION_DATE) END, "
            "  TIMESTAMP '2020-01-01'"
            ") BETWEEN @start_date AND @end_date"
        )

    return f"""--sql
    -- ── Roads → asset_type = 'road' ──────────────────────────────
    SELECT
        'kitchener_arcgis:road:' || CAST(src.OBJECTID AS VARCHAR) AS asset_id,
        'road'                        AS asset_type,
        'engineering'                 AS department_owner,
        CAST(src.OBJECTID AS VARCHAR) AS source_system_id,
        'kitchener_arcgis'            AS source_system,
        src.STREET                    AS label,
        NULL                          AS geom,
        NULL                          AS latitude,
        NULL                          AS longitude,
        COALESCE(src.STATUS, 'active') AS status,
        'internal'                    AS privacy_class,
        CASE WHEN src.CREATE_DATE IS NOT NULL
             THEN epoch_ms(src.CREATE_DATE) END AS created_at,
        CASE WHEN src.UPDATE_DATE IS NOT NULL
             THEN epoch_ms(src.UPDATE_DATE) END AS updated_at,
        NULL                          AS valid_from,
        NULL                          AS valid_to,
        COALESCE(
          CASE WHEN src.UPDATE_DATE IS NOT NULL
               THEN epoch_ms(src.UPDATE_DATE) END,
          CASE WHEN src.CREATE_DATE IS NOT NULL
               THEN epoch_ms(src.CREATE_DATE) END,
          TIMESTAMP '2020-01-01'
        )                             AS record_time
    FROM normalized_opendata_extract.road_segments AS src
    {roads_filter}

    UNION ALL

    -- ── Water Mains → asset_type = 'pipe' ────────────────────────
    SELECT
        'kitchener_arcgis:pipe:' || CAST(src.OBJECTID AS VARCHAR),
        'pipe',
        'utilities',
        CAST(src.OBJECTID AS VARCHAR),
        'kitchener_arcgis',
        'Water Main ' || CAST(src.OBJECTID AS VARCHAR),
        NULL, NULL, NULL,
        COALESCE(src.STATUS, 'active'),
        'internal',
        CASE WHEN src.INSTALLATION_DATE IS NOT NULL
             THEN epoch_ms(src.INSTALLATION_DATE) END,
        NULL,
        NULL, NULL,
        COALESCE(
          CASE WHEN src.INSTALLATION_DATE IS NOT NULL
               THEN epoch_ms(src.INSTALLATION_DATE) END,
          TIMESTAMP '2020-01-01'
        )
    FROM normalized_opendata_extract.water_mains AS src
    {water_filter}

    UNION ALL

    -- ── Building Permits → asset_type = 'permit' ─────────────────
    SELECT
        'kitchener_arcgis:permit:' || CAST(src.OBJECTID AS VARCHAR),
        'permit',
        'planning',
        COALESCE(src.PERMITNO, CAST(src.OBJECTID AS VARCHAR)),
        'kitchener_arcgis',
        src.FOLDERNAME,
        NULL, NULL, NULL,
        CASE
            WHEN src.PERMIT_STATUS ILIKE '%complete%' THEN 'inactive'
            WHEN src.PERMIT_STATUS ILIKE '%cancel%'   THEN 'inactive'
            ELSE 'active'
        END,
        'internal',
        CASE WHEN src.APPLICATION_DATE IS NOT NULL
             THEN epoch_ms(src.APPLICATION_DATE) END,
        CASE WHEN src.ISSUE_DATE IS NOT NULL
             THEN epoch_ms(src.ISSUE_DATE) END,
        CASE WHEN src.APPLICATION_DATE IS NOT NULL
             THEN CAST(epoch_ms(src.APPLICATION_DATE) AS DATE) END,
        CASE WHEN src.FINAL_DATE IS NOT NULL
             THEN CAST(epoch_ms(src.FINAL_DATE) AS DATE) END,
        COALESCE(
          CASE WHEN src.ISSUE_DATE IS NOT NULL
               THEN epoch_ms(src.ISSUE_DATE) END,
          CASE WHEN src.APPLICATION_DATE IS NOT NULL
               THEN epoch_ms(src.APPLICATION_DATE) END,
          TIMESTAMP '2020-01-01'
        )
    FROM normalized_opendata_extract.building_permits AS src
    {permits_filter}

    UNION ALL

    -- ── Ward Boundaries → asset_type = 'zone' ────────────────────
    SELECT
        'kitchener_arcgis:zone:ward_' || CAST(src.OBJECTID AS VARCHAR),
        'zone',
        'governance',
        CAST(src.OBJECTID AS VARCHAR),
        'kitchener_arcgis',
        src.WARD,
        NULL, NULL, NULL,
        'active',
        'public',
        NULL,
        NULL,
        NULL, NULL,
        TIMESTAMP '2020-01-01'
    FROM normalized_opendata_extract.ward_boundaries AS src
    {wards_filter}
    """


@macro()
def assets_grain(evaluator):
    return "'grain (asset_id, record_time)'"
