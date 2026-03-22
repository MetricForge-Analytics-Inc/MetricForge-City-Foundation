MODEL (
  name Foundry.support.users_atomic_view,
  kind VIEW,
  @users_atomic_grain()
);

-- Atomic User Table
@users_atomic_query("view")