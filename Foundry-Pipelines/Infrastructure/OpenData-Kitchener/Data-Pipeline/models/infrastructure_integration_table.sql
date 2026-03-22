MODEL (
  name Foundry.city.infrastructure_integration_table,
  kind INCREMENTAL_BY_TIME_RANGE (
    time_column record_time
  ),
  @infrastructure_integration_grain()
);

@infrastructure_integration_query("table")
