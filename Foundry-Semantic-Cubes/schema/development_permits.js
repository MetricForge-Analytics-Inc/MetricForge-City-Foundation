cube(`development_permits`, {
  sql_table: `Foundry.city.development_details_view`,

  dimensions: {
    permit_id: {
      sql: `permit_id`,
      type: `number`,
      primary_key: true,
    },
    record_time: {
      sql: `record_time`,
      type: `time`,
    },
    application_date: {
      sql: `application_date`,
      type: `time`,
    },
    issued_date: {
      sql: `issued_date`,
      type: `time`,
    },
    completed_date: {
      sql: `completed_date`,
      type: `time`,
    },
    permit_number: {
      sql: `permit_number`,
      type: `string`,
    },
    permit_type: {
      sql: `permit_type`,
      type: `string`,
    },
    permit_status: {
      sql: `permit_status`,
      type: `string`,
    },
    work_type: {
      sql: `work_type`,
      type: `string`,
    },
    permit_description: {
      sql: `permit_description`,
      type: `string`,
    },
    address: {
      sql: `address`,
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
    neighbourhood: {
      sql: `neighbourhood`,
      type: `string`,
    },
    councillor: {
      sql: `councillor`,
      type: `string`,
    },
  },

  measures: {
    total_permits: {
      sql: `permit_id`,
      type: `count`,
    },
    total_estimated_value: {
      sql: `estimated_value`,
      type: `sum`,
    },
    avg_estimated_value: {
      sql: `estimated_value`,
      type: `avg`,
    },
    total_actual_value: {
      sql: `actual_value`,
      type: `sum`,
    },
    residential_permits: {
      sql: `CASE WHEN permit_type ILIKE '%residential%' THEN 1 ELSE 0 END`,
      type: `sum`,
    },
    commercial_permits: {
      sql: `CASE WHEN permit_type ILIKE '%commercial%' THEN 1 ELSE 0 END`,
      type: `sum`,
    },
    completed_permits: {
      sql: `CASE WHEN permit_status ILIKE '%complete%' THEN 1 ELSE 0 END`,
      type: `sum`,
    },
    ward_population: {
      sql: `ward_population`,
      type: `max`,
    },
    ward_water_mains: {
      sql: `ward_water_mains`,
      type: `max`,
    },
    permits_per_ward: {
      sql: `total_permits_in_ward`,
      type: `max`,
    },
    development_intensity: {
      sql: `total_estimated_value_in_ward`,
      type: `max`,
    },
  },
});
