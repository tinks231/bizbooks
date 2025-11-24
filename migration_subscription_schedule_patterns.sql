-- Migration: Add delivery schedule patterns to subscription plans
-- Date: 2025-11-24
-- Purpose: Support custom delivery schedules (alternate days, weekdays only, etc.)

-- Add delivery_pattern column (default: 'daily' for existing plans)
ALTER TABLE subscription_plans 
ADD COLUMN IF NOT EXISTS delivery_pattern VARCHAR(20) DEFAULT 'daily';

-- Add custom_days column (stores comma-separated weekday numbers: 0=Mon, 6=Sun)
ALTER TABLE subscription_plans 
ADD COLUMN IF NOT EXISTS custom_days VARCHAR(50);

-- Set default pattern for existing metered plans
UPDATE subscription_plans 
SET delivery_pattern = 'daily' 
WHERE delivery_pattern IS NULL;

-- Add comment for clarity
COMMENT ON COLUMN subscription_plans.delivery_pattern IS 'Delivery schedule: daily, alternate, weekdays, weekends, custom';
COMMENT ON COLUMN subscription_plans.custom_days IS 'Custom weekdays (0-6): e.g. 1,3,5 for Mon,Wed,Fri';

