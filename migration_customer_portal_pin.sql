-- Migration: Add PIN column to customers table for customer portal access
-- Database: PostgreSQL
-- Date: 2025-11-23
-- Description: Adds PIN authentication for customer portal (like employee portal)

-- Add PIN column to customers table
ALTER TABLE customers ADD COLUMN IF NOT EXISTS pin VARCHAR(10);

-- Add index for faster login queries
CREATE INDEX IF NOT EXISTS idx_customer_phone_pin ON customers(tenant_id, phone, pin) WHERE pin IS NOT NULL;

-- Optional: Set default PIN for existing customers (you can change this later)
-- UPDATE customers SET pin = '1234' WHERE pin IS NULL;  -- Uncomment if you want to set default PIN

COMMENT ON COLUMN customers.pin IS 'Customer portal login PIN (4-10 digits)';

