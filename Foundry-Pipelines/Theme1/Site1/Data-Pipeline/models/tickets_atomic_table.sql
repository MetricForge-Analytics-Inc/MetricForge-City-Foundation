MODEL (
  name Foundry.support.tickets_atomic_table,
  kind INCREMENTAL_BY_TIME_RANGE (
    time_column case_created_time
  ),
  @tickets_atomic_grain()
);

-- Atomic Ticket Table
@tickets_atomic_query("table")
