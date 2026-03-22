MODEL (
  name Foundry.city.water_mains_atomic_table,
  kind INCREMENTAL_BY_TIME_RANGE (
    time_column record_time
  ),
  @water_mains_atomic_grain()
);

@water_mains_atomic_query("table")
