-- Migration: Customer Orders Feature
-- Allows customers to place orders through customer portal
-- Works for ANY business (not just milk!)

-- Customer Orders table
CREATE TABLE IF NOT EXISTS customer_orders (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    
    -- Order details
    order_number VARCHAR(50) NOT NULL,
    order_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Status: pending, confirmed, fulfilled, cancelled
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    
    -- Totals
    subtotal NUMERIC(10, 2) NOT NULL DEFAULT 0,
    tax_amount NUMERIC(10, 2) NOT NULL DEFAULT 0,
    total_amount NUMERIC(10, 2) NOT NULL DEFAULT 0,
    
    -- Additional info
    notes TEXT,
    admin_notes TEXT,
    
    -- Fulfillment
    fulfilled_date TIMESTAMP,
    fulfilled_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT unique_order_number_per_tenant UNIQUE (tenant_id, order_number)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_customer_order_status ON customer_orders(tenant_id, status);
CREATE INDEX IF NOT EXISTS idx_customer_order_date ON customer_orders(tenant_id, order_date);

-- Customer Order Items table
CREATE TABLE IF NOT EXISTS customer_order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES customer_orders(id) ON DELETE CASCADE,
    item_id INTEGER NOT NULL REFERENCES items(id) ON DELETE RESTRICT,
    
    -- Order details
    quantity NUMERIC(10, 2) NOT NULL,
    rate NUMERIC(10, 2) NOT NULL,
    amount NUMERIC(10, 2) NOT NULL,
    
    -- Tax
    tax_rate NUMERIC(5, 2) DEFAULT 0,
    tax_amount NUMERIC(10, 2) DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Comments for documentation
COMMENT ON TABLE customer_orders IS 'Orders placed by customers through customer portal';
COMMENT ON TABLE customer_order_items IS 'Line items in customer orders';
COMMENT ON COLUMN customer_orders.status IS 'Order status: pending, confirmed, fulfilled, cancelled';
COMMENT ON COLUMN customer_order_items.rate IS 'Price at time of order (snapshot)';

