MODEL (
  name city.assets_table,
  kind INCREMENTAL_BY_TIME_RANGE (
    time_column record_time
  ),
  @assets_grain()
);

@assets_query("table")
