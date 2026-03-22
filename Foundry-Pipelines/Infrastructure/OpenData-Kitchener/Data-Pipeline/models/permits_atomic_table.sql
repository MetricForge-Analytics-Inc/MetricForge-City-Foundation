MODEL (
  name Foundry.city.permits_atomic_table,
  kind INCREMENTAL_BY_TIME_RANGE (
    time_column record_time
  ),
  @permits_atomic_grain()
);

@permits_atomic_query("table")
