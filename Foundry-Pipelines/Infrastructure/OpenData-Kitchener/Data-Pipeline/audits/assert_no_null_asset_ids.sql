AUDIT (
  name assert_no_null_asset_ids
);

-- Ensure every asset has a non-null asset_id.
SELECT *
FROM @this_model
WHERE asset_id IS NULL
