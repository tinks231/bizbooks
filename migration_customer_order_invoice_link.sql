-- Migration: Add invoice link to customer orders
-- Date: 2025-11-24
-- Purpose: Link customer orders to invoices for billing and inventory tracking

-- Add invoice_id column to customer_orders table
ALTER TABLE customer_orders 
ADD COLUMN IF NOT EXISTS invoice_id INTEGER REFERENCES invoices(id) ON DELETE SET NULL;

-- Create index for faster invoice lookups
CREATE INDEX IF NOT EXISTS idx_customer_order_invoice 
ON customer_orders(invoice_id);

-- Comment for documentation
COMMENT ON COLUMN customer_orders.invoice_id IS 'Links customer order to generated invoice (NULL if not yet invoiced)';

