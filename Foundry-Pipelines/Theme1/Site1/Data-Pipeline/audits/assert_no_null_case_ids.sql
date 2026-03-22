AUDIT (
  name assert_no_null_case_ids,
);

-- Every ticket must have a non-null case_id.
SELECT *
FROM @this_model
WHERE
  case_id IS NULL
  