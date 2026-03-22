-- Ensure every road segment has an ID.
SELECT *
FROM @this_model
WHERE road_id IS NULL
