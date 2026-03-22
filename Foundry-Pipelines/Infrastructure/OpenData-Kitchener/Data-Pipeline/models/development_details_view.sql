MODEL (
  name city.development_details_view,
  kind VIEW,
  @development_details_grain()
);

@development_details_query()
