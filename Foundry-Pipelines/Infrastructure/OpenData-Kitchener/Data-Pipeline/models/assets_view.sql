MODEL (
  name city.assets_view,
  kind VIEW,
  @assets_grain()
);

@assets_query("view")
