MODEL (
  name Foundry.support.tickets_details_table,
  kind INCREMENTAL_BY_TIME_RANGE (
    time_column case_created_time
  ),
  @tickets_details_grain()
);

--Details Tickets Table:
@tickets_details_query("table")
