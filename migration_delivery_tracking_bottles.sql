-- Migration: Add Delivery Tracking & Bottle Management
-- Date: 2025-11-25
-- Purpose: Track delivery completion and bottle inventory per customer

-- 1. Add delivery tracking fields to subscription_deliveries
ALTER TABLE subscription_deliveries 
ADD COLUMN IF NOT EXISTS delivered_by INTEGER REFERENCES employees(id);

ALTER TABLE subscription_deliveries 
ADD COLUMN IF NOT EXISTS delivered_at TIMESTAMP;

ALTER TABLE subscription_deliveries 
ADD COLUMN IF NOT EXISTS bottles_delivered INTEGER DEFAULT 0;

ALTER TABLE subscription_deliveries 
ADD COLUMN IF NOT EXISTS bottles_collected INTEGER DEFAULT 0;

-- 2. Add bottle tracking to customers
ALTER TABLE customers 
ADD COLUMN IF NOT EXISTS bottles_in_possession INTEGER DEFAULT 0;

-- 3. Add comments
COMMENT ON COLUMN subscription_deliveries.delivered_by IS 'Employee who marked delivery as complete';
COMMENT ON COLUMN subscription_deliveries.delivered_at IS 'Timestamp when delivery was marked complete';
COMMENT ON COLUMN subscription_deliveries.bottles_delivered IS 'Number of new bottles delivered';
COMMENT ON COLUMN subscription_deliveries.bottles_collected IS 'Number of empty bottles collected back';
COMMENT ON COLUMN customers.bottles_in_possession IS 'Total bottles currently with customer';

-- 4. Create index for employee portal queries
CREATE INDEX IF NOT EXISTS idx_deliveries_date_status 
ON subscription_deliveries(delivery_date, status) 
WHERE delivered_at IS NULL;

