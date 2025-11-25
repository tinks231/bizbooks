-- Migration: Add Delivery Assignments
-- Date: 2025-11-25
-- Purpose: Allow admin to assign deliveries to specific employees

-- 1. Add assigned_to field to subscription_deliveries
ALTER TABLE subscription_deliveries 
ADD COLUMN IF NOT EXISTS assigned_to INTEGER REFERENCES employees(id);

-- 2. Add default_delivery_employee to customers (for auto-assignment)
ALTER TABLE customers 
ADD COLUMN IF NOT EXISTS default_delivery_employee INTEGER REFERENCES employees(id);

-- 3. Add comments
COMMENT ON COLUMN subscription_deliveries.assigned_to IS 'Employee assigned to make this delivery';
COMMENT ON COLUMN customers.default_delivery_employee IS 'Default employee for this customer deliveries';

-- 4. Create index for employee portal queries
CREATE INDEX IF NOT EXISTS idx_deliveries_assigned_employee 
ON subscription_deliveries(assigned_to, delivery_date) 
WHERE assigned_to IS NOT NULL;

-- 5. For existing deliveries, auto-assign based on customer's default employee
UPDATE subscription_deliveries 
SET assigned_to = (
    SELECT default_delivery_employee 
    FROM customers 
    WHERE customers.id = (
        SELECT customer_id 
        FROM customer_subscriptions 
        WHERE customer_subscriptions.id = subscription_deliveries.subscription_id
    )
)
WHERE assigned_to IS NULL 
AND EXISTS (
    SELECT 1 
    FROM customer_subscriptions 
    JOIN customers ON customers.id = customer_subscriptions.customer_id 
    WHERE customer_subscriptions.id = subscription_deliveries.subscription_id 
    AND customers.default_delivery_employee IS NOT NULL
);

