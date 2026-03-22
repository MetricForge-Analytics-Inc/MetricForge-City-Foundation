MODEL (
  name Foundry.support.users_atomic_table,
  kind INCREMENTAL_BY_TIME_RANGE (
    time_column user_created_time
  ),
  @users_atomic_grain()
);

-- Atomic User Table
@users_atomic_query("table")