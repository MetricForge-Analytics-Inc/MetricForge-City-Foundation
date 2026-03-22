cube(`infrastructure_assets`, {
  sql_table: `Foundry.city.infrastructure_integration_view`,

  dimensions: {
    road_id: {
      sql: `road_id`,
      type: `number`,
      primary_key: true,
    },
    record_time: {
      sql: `record_time`,
      type: `time`,
    },
    road_name: {
      sql: `road_name`,
      type: `string`,
    },
    road_classification: {
      sql: `road_classification`,
      type: `string`,
    },
    surface_type: {
      sql: `surface_type`,
      type: `string`,
    },
    surface_condition: {
      sql: `surface_condition`,
      type: `string`,
    },
    number_of_lanes: {
      sql: `number_of_lanes`,
      type: `number`,
    },
    speed_limit_kmh: {
      sql: `speed_limit_kmh`,
      type: `number`,
    },
    road_ownership: {
      sql: `road_ownership`,
      type: `string`,
    },
    maintenance_responsibility: {
      sql: `maintenance_responsibility`,
      type: `string`,
    },
    ward: {
      sql: `ward`,
      type: `string`,
    },
    ward_name: {
      sql: `ward_name`,
      type: `string`,
    },
    councillor: {
      sql: `councillor`,
      type: `string`,
    },
  },

  measures: {
    total_road_segments: {
      sql: `road_id`,
      type: `count`,
    },
    total_road_length_km: {
      sql: `road_length_m / 1000.0`,
      type: `sum`,
    },
    avg_road_length_m: {
      sql: `road_length_m`,
      type: `avg`,
    },
    total_water_mains_in_ward: {
      sql: `total_water_mains`,
      type: `max`,
    },
    oldest_water_infrastructure_year: {
      sql: `oldest_install_year`,
      type: `min`,
    },
    total_water_network_km: {
      sql: `total_water_length_m / 1000.0`,
      type: `max`,
    },
    ward_population: {
      sql: `ward_population`,
      type: `max`,
    },
  },
});
