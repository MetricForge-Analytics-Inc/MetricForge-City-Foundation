MODEL (
  name city.events_table,
  kind INCREMENTAL_BY_TIME_RANGE (
    time_column record_time
  ),
  @events_grain()
);

@events_query("table")
