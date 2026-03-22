cube(`water_infrastructure`, {
  sql_table: `Foundry.city.water_mains_atomic_view`,

  dimensions: {
    main_id: {
      sql: `main_id`,
      type: `number`,
      primary_key: true,
    },
    record_time: {
      sql: `record_time`,
      type: `time`,
    },
    pipe_material: {
      sql: `pipe_material`,
      type: `string`,
    },
    pipe_status: {
      sql: `pipe_status`,
      type: `string`,
    },
    pressure_zone: {
      sql: `pressure_zone`,
      type: `string`,
    },
    ownership: {
      sql: `ownership`,
      type: `string`,
    },
    ward: {
      sql: `ward`,
      type: `string`,
    },
    install_year: {
      sql: `install_year`,
      type: `number`,
    },
    diameter_mm: {
      sql: `diameter_mm`,
      type: `number`,
    },
  },

  measures: {
    total_mains: {
      sql: `main_id`,
      type: `count`,
    },
    total_length_km: {
      sql: `segment_length_m / 1000.0`,
      type: `sum`,
    },
    avg_diameter_mm: {
      sql: `diameter_mm`,
      type: `avg`,
    },
    oldest_install_year: {
      sql: `install_year`,
      type: `min`,
    },
    newest_install_year: {
      sql: `install_year`,
      type: `max`,
    },
    avg_pipe_age_years: {
      sql: `2026 - install_year`,
      type: `avg`,
    },
  },
});
