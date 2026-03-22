MODEL (
  name Foundry.support.tickets_details_view,
  kind VIEW,
  @tickets_details_grain()
);



--Details Tickets Table:
@tickets_details_query("view")
