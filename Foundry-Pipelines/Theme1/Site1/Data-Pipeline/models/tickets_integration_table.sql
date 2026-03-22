MODEL (
  name Foundry.support.tickets_integration_table,
  kind INCREMENTAL_BY_TIME_RANGE (
    time_column case_created_time
  ),
  @tickets_integration_grain()
);

--Integration Tickets Table:
@tickets_integration_query("table")
