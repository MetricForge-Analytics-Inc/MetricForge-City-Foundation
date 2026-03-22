from sqlmesh import macro


_SRC_SCHEMA = "normalized_opendata_extract"


@macro()
def events_query(evaluator, table_type):
    """
    Immutable event log aligned with db_schema.md `events` table.
    Domain-specific attributes are stored in the JSON payload column.

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
    -- ── Road Events ──────────────────────────────────────────────
    SELECT
        'kitchener_arcgis:road:' || CAST(src.objectid AS VARCHAR) || ':created'
                                      AS event_id,
        'kitchener_arcgis:road:' || CAST(src.objectid AS VARCHAR)
                                      AS asset_id,
        'created'                     AS event_type,
        'road_segment'                AS event_subtype,
        'engineering'                 AS department_source,
        'kitchener_arcgis'            AS triggered_by,
        to_json({{
            'street':           src.street,
            'street_name':      src.street_name,
            'street_type':      src.street_type,
            'carto_class':      src.carto_class,
            'surface_type':     src.surface_layer_type,
            'lanes':            src.lanes,
            'speed_limit_km':   src.speed_limit_km,
            'pavement_width':   src.pavement_width,
            'ownership':        src.ownership,
            'status':           src.status,
            'ward_id':          src.wardid,
            'category':         src.category,
            'subcategory':      src.subcategory
        }})                           AS payload,
        'info'                        AS severity,
        COALESCE(
          CASE WHEN src.create_date IS NOT NULL
               THEN epoch_ms(src.create_date) END,
          TIMESTAMP '2020-01-01'
        )                             AS occurred_at,
        COALESCE(
          CASE WHEN src.update_date IS NOT NULL
               THEN epoch_ms(src.update_date) END,
          CASE WHEN src.create_date IS NOT NULL
               THEN epoch_ms(src.create_date) END,
          TIMESTAMP '2020-01-01'
        )                             AS recorded_at,
        FALSE                         AS is_audit_event,
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

    -- ── Water Main Events ────────────────────────────────────────
    SELECT
        'kitchener_arcgis:pipe:' || CAST(src.objectid AS VARCHAR) || ':created',
        'kitchener_arcgis:pipe:' || CAST(src.objectid AS VARCHAR),
        'created',
        'water_main',
        'utilities',
        'kitchener_arcgis',
        to_json({{
            'material':        src.material,
            'pipe_size':       src.pipe_size,
            'pressure_zone':   src.pressure_zone,
            'status':          src.status,
            'category':        src.category,
            'lined':           src.lined,
            'ownership':       src.ownership,
            'condition_score': src.condition_score,
            'criticality':     src.criticality
        }}),
        'info',
        COALESCE(
          CASE WHEN src.installation_date IS NOT NULL
               THEN epoch_ms(src.installation_date) END,
          TIMESTAMP '2020-01-01'
        ),
        COALESCE(
          CASE WHEN src.installation_date IS NOT NULL
               THEN epoch_ms(src.installation_date) END,
          TIMESTAMP '2020-01-01'
        ),
        FALSE,
        COALESCE(
          CASE WHEN src.installation_date IS NOT NULL
               THEN epoch_ms(src.installation_date) END,
          TIMESTAMP '2020-01-01'
        )
    FROM {_SRC_SCHEMA}.water_mains AS src
    {water_filter}

    UNION ALL

    -- ── Permit Events ────────────────────────────────────────────
    SELECT
        'kitchener_arcgis:permit:' || CAST(src.objectid AS VARCHAR) || ':issued',
        'kitchener_arcgis:permit:' || CAST(src.objectid AS VARCHAR),
        'permit_issued',
        LOWER(COALESCE(src.permit_type, 'unknown')) || '_permit',
        'planning',
        'kitchener_arcgis',
        to_json({{
            'permit_number':      src.permitno,
            'permit_type':        src.permit_type,
            'permit_status':      src.permit_status,
            'work_type':          src.work_type,
            'sub_work_type':      src.sub_work_type,
            'description':        src.permit_description,
            'construction_value': src.construction_value,
            'total_units':        src.total_units,
            'units_created':      src.units_created,
            'units_lost':         src.units_lost,
            'folder_name':        src.foldername,
            'issue_year':         src.issue_year
        }}),
        'info',
        COALESCE(
          CASE WHEN src.issue_date IS NOT NULL
               THEN epoch_ms(src.issue_date) END,
          CASE WHEN src.application_date IS NOT NULL
               THEN epoch_ms(src.application_date) END,
          TIMESTAMP '2020-01-01'
        ),
        COALESCE(
          CASE WHEN src.issue_date IS NOT NULL
               THEN epoch_ms(src.issue_date) END,
          CASE WHEN src.application_date IS NOT NULL
               THEN epoch_ms(src.application_date) END,
          TIMESTAMP '2020-01-01'
        ),
        FALSE,
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

    -- ── Ward Boundary Events ─────────────────────────────────────
    SELECT
        'kitchener_arcgis:zone:ward_' || CAST(src.objectid AS VARCHAR) || ':created',
        'kitchener_arcgis:zone:ward_' || CAST(src.objectid AS VARCHAR),
        'created',
        'ward_boundary',
        'governance',
        'kitchener_arcgis',
        to_json({{
            'ward_id':             src.wardid,
            'ward_name':           src.ward,
            'councillor_name':     src.councillor_name,
            'residential_households': src.residential_household_count,
            'mpac_population':     src.mpac_population,
            'mpac_voters':         src.mpac_voters
        }}),
        'info',
        TIMESTAMP '2020-01-01',
        TIMESTAMP '2020-01-01',
        FALSE,
        TIMESTAMP '2020-01-01'
    FROM {_SRC_SCHEMA}.ward_boundaries AS src
    {wards_filter}
    """


@macro()
def events_grain(evaluator):
    return "'grain (event_id, record_time)'"
