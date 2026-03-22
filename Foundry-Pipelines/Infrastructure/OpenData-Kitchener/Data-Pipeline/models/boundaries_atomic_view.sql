MODEL (
  name Foundry.city.boundaries_atomic_view,
  kind VIEW,
  @boundaries_atomic_grain()
);

@boundaries_atomic_query("view")
