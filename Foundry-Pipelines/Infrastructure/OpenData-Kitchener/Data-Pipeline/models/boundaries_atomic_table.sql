MODEL (
  name Foundry.city.boundaries_atomic_table,
  kind INCREMENTAL_BY_TIME_RANGE (
    time_column record_time
  ),
  @boundaries_atomic_grain()
);

@boundaries_atomic_query("table")
