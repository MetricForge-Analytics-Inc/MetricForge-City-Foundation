from sqlmesh import macro


@macro()
def infrastructure_integration_query(evaluator):
    """
    Joins roads and water mains by ward to create a cross-departmental
    infrastructure view — the first step toward coordinated planning.
    Queries from the universal-schema-backed analytical views.
    """
    return """--sql
    SELECT
        roads.road_id,
        roads.road_name,
        roads.road_classification,
        roads.surface_type,
        roads.category,
        roads.subcategory,
        roads.number_of_lanes,
        roads.speed_limit_kmh,
        roads.pavement_width_m,
        roads.ownership          AS road_ownership,
        roads.road_status,
        roads.ward_id,
        roads.record_time,

        -- Ward context (cross-departmental join)
        wards.ward_name,
        wards.councillor,
        wards.population         AS ward_population,
        wards.residential_households AS ward_households,

        -- Water infrastructure count (no ward on water_mains so count all)
        water_agg.total_water_mains,
        water_agg.distinct_materials

    FROM
        city.roads_atomic_view AS roads

    LEFT JOIN
        city.boundaries_atomic_view AS wards
    ON
        roads.ward_id = wards.ward_number

    LEFT JOIN (
        SELECT
            COUNT(*)                            AS total_water_mains,
            COUNT(DISTINCT pipe_material)       AS distinct_materials
        FROM
            city.water_mains_atomic_view
    ) AS water_agg
    ON TRUE
    """


@macro()
def infrastructure_integration_grain(evaluator):
    return "'grain (road_id, record_time)'"
