cube(`ward_overview`, {
  sql_table: `Foundry.city.boundaries_atomic_view`,

  dimensions: {
    ward_id: {
      sql: `ward_id`,
      type: `number`,
      primary_key: true,
    },
    record_time: {
      sql: `record_time`,
      type: `time`,
    },
    ward_number: {
      sql: `ward_number`,
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
    total_wards: {
      sql: `ward_id`,
      type: `count`,
    },
    total_population: {
      sql: `population`,
      type: `sum`,
    },
    total_area_sq_km: {
      sql: `area_sq_km`,
      type: `sum`,
    },
    avg_population_per_ward: {
      sql: `population`,
      type: `avg`,
    },
    population_density_per_sq_km: {
      sql: `population / NULLIF(area_sq_km, 0)`,
      type: `avg`,
    },
  },
});
