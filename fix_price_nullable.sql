-- Make price and duration_days nullable for metered plans
ALTER TABLE subscription_plans 
ALTER COLUMN price DROP NOT NULL;

ALTER TABLE subscription_plans 
ALTER COLUMN duration_days DROP NOT NULL;

-- Verify the change
SELECT 
    column_name,
    is_nullable,
    data_type
FROM information_schema.columns
WHERE table_name = 'subscription_plans'
    AND column_name IN ('price', 'duration_days');
