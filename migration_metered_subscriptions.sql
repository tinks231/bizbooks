-- ============================================================
-- Metered Subscriptions Migration (PostgreSQL)
-- ============================================================

-- 1. Add new columns to subscription_plans
ALTER TABLE subscription_plans 
ADD COLUMN IF NOT EXISTS plan_type VARCHAR(20) DEFAULT 'fixed' NOT NULL,
ADD COLUMN IF NOT EXISTS unit_rate DECIMAL(10, 2),
ADD COLUMN IF NOT EXISTS unit_name VARCHAR(20);

-- Update existing plans to be 'fixed' type
UPDATE subscription_plans 
SET plan_type = 'fixed' 
WHERE plan_type IS NULL OR plan_type = '';

-- 2. Add new column to customer_subscriptions
ALTER TABLE customer_subscriptions 
ADD COLUMN IF NOT EXISTS default_quantity DECIMAL(10, 2);

-- 3. Create new subscription_deliveries table
CREATE TABLE IF NOT EXISTS subscription_deliveries (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL,
    subscription_id INTEGER NOT NULL,
    delivery_date DATE NOT NULL,
    quantity DECIMAL(10, 2) NOT NULL,
    rate DECIMAL(10, 2) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(20) DEFAULT 'delivered' NOT NULL,
    is_modified BOOLEAN DEFAULT FALSE,
    modification_reason VARCHAR(200),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_delivery_tenant FOREIGN KEY (tenant_id) REFERENCES tenants(id),
    CONSTRAINT fk_delivery_subscription FOREIGN KEY (subscription_id) REFERENCES customer_subscriptions(id),
    CONSTRAINT uq_subscription_delivery_date UNIQUE (subscription_id, delivery_date)
);

-- 4. Create indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_subscription_deliveries_date ON subscription_deliveries(delivery_date);
CREATE INDEX IF NOT EXISTS idx_subscription_deliveries_tenant ON subscription_deliveries(tenant_id);
CREATE INDEX IF NOT EXISTS idx_subscription_deliveries_subscription ON subscription_deliveries(subscription_id);

-- 5. Verify changes
SELECT 
    'subscription_plans' as table_name,
    column_name,
    data_type
FROM information_schema.columns
WHERE table_name = 'subscription_plans'
    AND column_name IN ('plan_type', 'unit_rate', 'unit_name')
UNION ALL
SELECT 
    'customer_subscriptions' as table_name,
    column_name,
    data_type
FROM information_schema.columns
WHERE table_name = 'customer_subscriptions'
    AND column_name = 'default_quantity'
UNION ALL
SELECT 
    'subscription_deliveries' as table_name,
    'table_created' as column_name,
    'success' as data_type
FROM information_schema.tables
WHERE table_name = 'subscription_deliveries';

