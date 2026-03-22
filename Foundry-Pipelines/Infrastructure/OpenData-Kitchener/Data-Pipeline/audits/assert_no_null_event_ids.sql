AUDIT (
  name assert_no_null_event_ids
);

-- Ensure every event has a non-null event_id.
SELECT *
FROM @this_model
WHERE event_id IS NULL
