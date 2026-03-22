-- Ensure every building permit has an ID.
SELECT *
FROM @this_model
WHERE permit_id IS NULL
