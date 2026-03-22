MODEL (
  name city.events_view,
  kind VIEW,
  @events_grain()
);

@events_query("view")
