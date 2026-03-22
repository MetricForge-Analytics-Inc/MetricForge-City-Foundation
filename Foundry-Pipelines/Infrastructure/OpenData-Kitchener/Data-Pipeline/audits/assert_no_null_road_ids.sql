AUDIT (
  name assert_no_null_road_ids
);

-- Ensure every road segment has an ID.
SELECT *
FROM @this_model
WHERE road_id IS NULL
