MODEL (
  name city.permits_atomic_view,
  kind VIEW,
  @permits_atomic_grain()
);

@permits_atomic_query()
