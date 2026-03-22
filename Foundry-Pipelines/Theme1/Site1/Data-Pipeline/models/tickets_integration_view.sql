MODEL (
  name Foundry.support.tickets_integration_view,
  kind VIEW,
  @tickets_integration_grain()
);



--Integration Tickets Table:
@tickets_integration_query("view")
