MODEL (
  name city.roads_atomic_view,
  kind VIEW,
  @roads_atomic_grain()
);

@roads_atomic_query()
