AUDIT (
  name assert_no_null_permit_ids
);

-- Ensure every building permit has an ID.
SELECT *
FROM @this_model
WHERE permit_id IS NULL
