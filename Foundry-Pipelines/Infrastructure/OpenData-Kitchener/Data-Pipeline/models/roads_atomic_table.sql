MODEL (
  name Foundry.city.roads_atomic_table,
  kind INCREMENTAL_BY_TIME_RANGE (
    time_column record_time
  ),
  @roads_atomic_grain()
);

@roads_atomic_query("table")
