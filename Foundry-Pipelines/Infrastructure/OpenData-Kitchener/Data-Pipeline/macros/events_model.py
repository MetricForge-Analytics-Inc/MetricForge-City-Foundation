from sqlmesh import macro


@macro()
def events_query(evaluator, table_type):
    """
    Immutable event log aligned with db_schema.md `events` table.
    Domain-specific attributes are stored in the JSON payload column.

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
        wards_filter = "WHERE TRUE"
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
    -- ── Road Events ──────────────────────────────────────────────
    SELECT
        'kitchener_arcgis:road:' || CAST(src.OBJECTID AS VARCHAR) || ':created'
                                      AS event_id,
        'kitchener_arcgis:road:' || CAST(src.OBJECTID AS VARCHAR)
                                      AS asset_id,
        'created'                     AS event_type,
        'road_segment'                AS event_subtype,
        'engineering'                 AS department_source,
        'kitchener_arcgis'            AS triggered_by,
        to_json({{
            'street':           src.STREET,
            'street_name':      src.STREET_NAME,
            'street_type':      src.STREET_TYPE,
            'carto_class':      src.CARTO_CLASS,
            'surface_type':     src.SURFACE_LAYER_TYPE,
            'lanes':            src.LANES,
            'speed_limit_km':   src.SPEED_LIMIT_KM,
            'pavement_width':   src.PAVEMENT_WIDTH,
            'ownership':        src.OWNERSHIP,
            'status':           src.STATUS,
            'ward_id':          src.WARDID,
            'category':         src.CATEGORY,
            'subcategory':      src.SUBCATEGORY
        }})                           AS payload,
        'info'                        AS severity,
        COALESCE(
          CASE WHEN src.CREATE_DATE IS NOT NULL
               THEN epoch_ms(src.CREATE_DATE) END,
          TIMESTAMP '2020-01-01'
        )                             AS occurred_at,
        COALESCE(
          CASE WHEN src.UPDATE_DATE IS NOT NULL
               THEN epoch_ms(src.UPDATE_DATE) END,
          CASE WHEN src.CREATE_DATE IS NOT NULL
               THEN epoch_ms(src.CREATE_DATE) END,
          TIMESTAMP '2020-01-01'
        )                             AS recorded_at,
        FALSE                         AS is_audit_event,
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

    -- ── Water Main Events ────────────────────────────────────────
    SELECT
        'kitchener_arcgis:pipe:' || CAST(src.OBJECTID AS VARCHAR) || ':created',
        'kitchener_arcgis:pipe:' || CAST(src.OBJECTID AS VARCHAR),
        'created',
        'water_main',
        'utilities',
        'kitchener_arcgis',
        to_json({{
            'material':        src.MATERIAL,
            'pipe_size':       src.PIPE_SIZE,
            'pressure_zone':   src.PRESSURE_ZONE,
            'status':          src.STATUS,
            'category':        src.CATEGORY,
            'lined':           src.LINED,
            'ownership':       src.OWNERSHIP,
            'condition_score': src.CONDITION_SCORE,
            'criticality':     src.CRITICALITY
        }}),
        'info',
        COALESCE(
          CASE WHEN src.INSTALLATION_DATE IS NOT NULL
               THEN epoch_ms(src.INSTALLATION_DATE) END,
          TIMESTAMP '2020-01-01'
        ),
        COALESCE(
          CASE WHEN src.INSTALLATION_DATE IS NOT NULL
               THEN epoch_ms(src.INSTALLATION_DATE) END,
          TIMESTAMP '2020-01-01'
        ),
        FALSE,
        COALESCE(
          CASE WHEN src.INSTALLATION_DATE IS NOT NULL
               THEN epoch_ms(src.INSTALLATION_DATE) END,
          TIMESTAMP '2020-01-01'
        )
    FROM normalized_opendata_extract.water_mains AS src
    {water_filter}

    UNION ALL

    -- ── Permit Events ────────────────────────────────────────────
    SELECT
        'kitchener_arcgis:permit:' || CAST(src.OBJECTID AS VARCHAR) || ':issued',
        'kitchener_arcgis:permit:' || CAST(src.OBJECTID AS VARCHAR),
        'permit_issued',
        LOWER(COALESCE(src.PERMIT_TYPE, 'unknown')) || '_permit',
        'planning',
        'kitchener_arcgis',
        to_json({{
            'permit_number':      src.PERMITNO,
            'permit_type':        src.PERMIT_TYPE,
            'permit_status':      src.PERMIT_STATUS,
            'work_type':          src.WORK_TYPE,
            'sub_work_type':      src.SUB_WORK_TYPE,
            'description':        src.PERMIT_DESCRIPTION,
            'construction_value': src.CONSTRUCTION_VALUE,
            'total_units':        src.TOTAL_UNITS,
            'units_created':      src.UNITS_CREATED,
            'units_lost':         src.UNITS_LOST,
            'folder_name':        src.FOLDERNAME,
            'issue_year':         src.ISSUE_YEAR
        }}),
        'info',
        COALESCE(
          CASE WHEN src.ISSUE_DATE IS NOT NULL
               THEN epoch_ms(src.ISSUE_DATE) END,
          CASE WHEN src.APPLICATION_DATE IS NOT NULL
               THEN epoch_ms(src.APPLICATION_DATE) END,
          TIMESTAMP '2020-01-01'
        ),
        COALESCE(
          CASE WHEN src.ISSUE_DATE IS NOT NULL
               THEN epoch_ms(src.ISSUE_DATE) END,
          CASE WHEN src.APPLICATION_DATE IS NOT NULL
               THEN epoch_ms(src.APPLICATION_DATE) END,
          TIMESTAMP '2020-01-01'
        ),
        FALSE,
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

    -- ── Ward Boundary Events ─────────────────────────────────────
    SELECT
        'kitchener_arcgis:zone:ward_' || CAST(src.OBJECTID AS VARCHAR) || ':created',
        'kitchener_arcgis:zone:ward_' || CAST(src.OBJECTID AS VARCHAR),
        'created',
        'ward_boundary',
        'governance',
        'kitchener_arcgis',
        to_json({{
            'ward_id':             src.WARDID,
            'ward_name':           src.WARD,
            'councillor_name':     src.COUNCILLOR_NAME,
            'residential_households': src.RESIDENTIAL_HOUSEHOLD_COUNT,
            'mpac_population':     src.MPAC_POPULATION,
            'mpac_voters':         src.MPAC_VOTERS
        }}),
        'info',
        TIMESTAMP '2020-01-01',
        TIMESTAMP '2020-01-01',
        FALSE,
        TIMESTAMP '2020-01-01'
    FROM normalized_opendata_extract.ward_boundaries AS src
    {wards_filter}
    """


@macro()
def events_grain(evaluator):
    return "'grain (event_id, record_time)'"
