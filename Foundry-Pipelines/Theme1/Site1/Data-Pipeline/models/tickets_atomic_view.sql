MODEL (
  name Foundry.support.tickets_atomic_view,
  kind VIEW,
  @tickets_atomic_grain()
);



-- Atomic Ticket Table
@tickets_atomic_query("view")