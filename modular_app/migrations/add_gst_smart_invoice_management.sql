-- Migration: GST-Smart Invoice Management System
-- Created: 2025-12-23
-- Feature: Batch-level GST tracking + Smart invoice validation

-- ====================================
-- 1. CREATE STOCK_BATCHES TABLE
-- ====================================

CREATE TABLE IF NOT EXISTS stock_batches (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL REFERENCES tenants(id),
    item_id INTEGER NOT NULL REFERENCES items(id),
    
    -- Purchase reference
    purchase_bill_id INTEGER REFERENCES purchase_bills(id),
    purchase_bill_item_id INTEGER REFERENCES purchase_bill_items(id),
    purchase_bill_number VARCHAR(50),
    purchase_date DATE,
    vendor_id INTEGER REFERENCES vendors(id),
    vendor_name VARCHAR(200),
    
    -- Site/location
    site_id INTEGER REFERENCES sites(id),
    
    -- Quantity tracking
    quantity_purchased NUMERIC(15, 3) NOT NULL,
    quantity_remaining NUMERIC(15, 3) NOT NULL,
    quantity_sold NUMERIC(15, 3) DEFAULT 0,
    quantity_adjusted NUMERIC(15, 3) DEFAULT 0,
    
    -- KEY FIELD: GST Status
    purchased_with_gst BOOLEAN NOT NULL DEFAULT FALSE,
    
    -- Cost tracking
    base_cost_per_unit NUMERIC(15, 2) NOT NULL,
    gst_rate NUMERIC(5, 2) DEFAULT 0,
    gst_per_unit NUMERIC(15, 2) DEFAULT 0,
    total_cost_per_unit NUMERIC(15, 2) NOT NULL,
    
    -- ITC tracking
    itc_per_unit NUMERIC(15, 2) DEFAULT 0,
    itc_total_available NUMERIC(15, 2) DEFAULT 0,
    itc_claimed NUMERIC(15, 2) DEFAULT 0,
    itc_remaining NUMERIC(15, 2) DEFAULT 0,
    
    -- Batch details
    batch_number VARCHAR(50),
    expiry_date DATE,
    batch_status VARCHAR(20) DEFAULT 'active',
    
    -- Audit
    notes TEXT,
    created_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes
    CONSTRAINT idx_batch_tenant_item_idx CREATE INDEX ON stock_batches(tenant_id, item_id),
    CONSTRAINT idx_batch_purchase_idx CREATE INDEX ON stock_batches(purchase_bill_id),
    CONSTRAINT idx_batch_status_idx CREATE INDEX ON stock_batches(batch_status)
);

-- Create indexes separately (PostgreSQL syntax)
CREATE INDEX IF NOT EXISTS idx_batch_tenant_item ON stock_batches(tenant_id, item_id);
CREATE INDEX IF NOT EXISTS idx_batch_purchase ON stock_batches(purchase_bill_id);
CREATE INDEX IF NOT EXISTS idx_batch_status ON stock_batches(batch_status);

-- ====================================
-- 2. UPDATE ITEMS TABLE
-- ====================================

-- Add GST classification field
ALTER TABLE items 
ADD COLUMN IF NOT EXISTS gst_classification VARCHAR(20) DEFAULT 'gst_applicable';
-- Values: 'gst_applicable', 'non_gst', 'mixed'

COMMENT ON COLUMN items.gst_classification IS 'Expected GST handling: gst_applicable (standard), non_gst (exempt/unregistered), mixed (flexible)';

-- ====================================
-- 3. UPDATE INVOICES TABLE
-- ====================================

-- Add invoice type field
ALTER TABLE invoices 
ADD COLUMN IF NOT EXISTS invoice_type VARCHAR(20) DEFAULT 'taxable';
-- Values: 'taxable', 'non_taxable', 'credit_adjustment'

-- Add credit adjustment fields
ALTER TABLE invoices 
ADD COLUMN IF NOT EXISTS linked_invoice_id INTEGER REFERENCES invoices(id);

ALTER TABLE invoices 
ADD COLUMN IF NOT EXISTS credit_commission_rate NUMERIC(5, 2) DEFAULT 0;

ALTER TABLE invoices 
ADD COLUMN IF NOT EXISTS credit_commission_amount NUMERIC(15, 2) DEFAULT 0;

ALTER TABLE invoices 
ADD COLUMN IF NOT EXISTS reduce_stock BOOLEAN DEFAULT TRUE;

COMMENT ON COLUMN invoices.invoice_type IS 'Invoice type: taxable (GST charged), non_taxable (no GST), credit_adjustment (GST shown, no stock reduction)';
COMMENT ON COLUMN invoices.linked_invoice_id IS 'For credit_adjustment: links to original non_taxable invoice';
COMMENT ON COLUMN invoices.reduce_stock IS 'FALSE for credit_adjustment invoices (stock already reduced in original invoice)';

-- ====================================
-- 4. UPDATE INVOICE_ITEMS TABLE
-- ====================================

-- Add batch tracking
ALTER TABLE invoice_items 
ADD COLUMN IF NOT EXISTS stock_batch_id INTEGER REFERENCES stock_batches(id);

ALTER TABLE invoice_items 
ADD COLUMN IF NOT EXISTS uses_gst_stock BOOLEAN DEFAULT TRUE;

-- Add cost tracking for profit calculation
ALTER TABLE invoice_items 
ADD COLUMN IF NOT EXISTS cost_base NUMERIC(15, 2) DEFAULT 0;

ALTER TABLE invoice_items 
ADD COLUMN IF NOT EXISTS cost_gst_paid NUMERIC(15, 2) DEFAULT 0;

COMMENT ON COLUMN invoice_items.stock_batch_id IS 'Which stock batch was used for this sale';
COMMENT ON COLUMN invoice_items.uses_gst_stock IS 'TRUE if sold from GST-purchased stock';
COMMENT ON COLUMN invoice_items.cost_base IS 'Base cost (without GST) per unit';
COMMENT ON COLUMN invoice_items.cost_gst_paid IS 'GST paid on purchase (ITC available if from GST stock)';

-- ====================================
-- 5. UPDATE PURCHASE_BILLS TABLE
-- ====================================

-- Add bill type field
ALTER TABLE purchase_bills 
ADD COLUMN IF NOT EXISTS bill_type VARCHAR(20) DEFAULT 'taxable';
-- Values: 'taxable', 'non_taxable'

ALTER TABLE purchase_bills 
ADD COLUMN IF NOT EXISTS gst_applicable BOOLEAN DEFAULT TRUE;

COMMENT ON COLUMN purchase_bills.bill_type IS 'Purchase type: taxable (with GST/ITC), non_taxable (no GST/ITC)';

-- ====================================
-- 6. UPDATE VENDORS TABLE
-- ====================================

-- Add GST registration type
ALTER TABLE vendors 
ADD COLUMN IF NOT EXISTS gst_registration_type VARCHAR(50) DEFAULT 'registered';
-- Values: 'registered', 'unregistered', 'composition'

ALTER TABLE vendors 
ADD COLUMN IF NOT EXISTS composition_rate NUMERIC(5, 2);

ALTER TABLE vendors 
ADD COLUMN IF NOT EXISTS gst_validated BOOLEAN DEFAULT FALSE;

COMMENT ON COLUMN vendors.gst_registration_type IS 'Vendor GST status: registered (normal), unregistered (no GST), composition (special rate)';

-- ====================================
-- 7. UPDATE CUSTOMERS TABLE
-- ====================================

-- Add GST registration type
ALTER TABLE customers 
ADD COLUMN IF NOT EXISTS gst_registration_type VARCHAR(50) DEFAULT 'unregistered';
-- Values: 'registered', 'unregistered'

ALTER TABLE customers 
ADD COLUMN IF NOT EXISTS gst_validated BOOLEAN DEFAULT FALSE;

COMMENT ON COLUMN customers.gst_registration_type IS 'Customer GST status: registered (B2B, can claim ITC), unregistered (B2C, cannot claim ITC)';

-- ====================================
-- 8. CREATE OTHER_INCOMES TABLE (for commission tracking)
-- ====================================

CREATE TABLE IF NOT EXISTS other_incomes (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL REFERENCES tenants(id),
    invoice_id INTEGER REFERENCES invoices(id),
    
    income_category VARCHAR(100),  -- 'Credit Commission', 'Interest', etc.
    amount NUMERIC(15, 2) NOT NULL,
    income_date DATE NOT NULL,
    
    notes TEXT,
    reference_number VARCHAR(100),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    created_by VARCHAR(100)
);

CREATE INDEX IF NOT EXISTS idx_other_income_tenant ON other_incomes(tenant_id);
CREATE INDEX IF NOT EXISTS idx_other_income_invoice ON other_incomes(invoice_id);
CREATE INDEX IF NOT EXISTS idx_other_income_date ON other_incomes(income_date);

COMMENT ON TABLE other_incomes IS 'Track additional income like credit commissions, interest, etc.';

-- ====================================
-- 9. UPDATE EXISTING DATA (SAFE DEFAULTS)
-- ====================================

-- Mark all existing invoices as 'taxable' (safe default)
UPDATE invoices 
SET invoice_type = 'taxable', 
    reduce_stock = TRUE 
WHERE invoice_type IS NULL;

-- Mark all existing purchase bills as 'taxable' (safe default)
UPDATE purchase_bills 
SET bill_type = 'taxable', 
    gst_applicable = TRUE 
WHERE bill_type IS NULL;

-- Mark all existing items as 'gst_applicable' (safe default)
UPDATE items 
SET gst_classification = 'gst_applicable' 
WHERE gst_classification IS NULL;

-- Mark vendors with GSTIN as 'registered'
UPDATE vendors 
SET gst_registration_type = 'registered' 
WHERE gstin IS NOT NULL AND gstin != '';

UPDATE vendors 
SET gst_registration_type = 'unregistered' 
WHERE (gstin IS NULL OR gstin = '') AND gst_registration_type IS NULL;

-- Mark customers with GSTIN as 'registered'
UPDATE customers 
SET gst_registration_type = 'registered' 
WHERE gstin IS NOT NULL AND gstin != '';

UPDATE customers 
SET gst_registration_type = 'unregistered' 
WHERE (gstin IS NULL OR gstin = '') AND gst_registration_type IS NULL;

-- ====================================
-- END OF MIGRATION
-- ====================================

-- Migration completion note
COMMENT ON TABLE stock_batches IS 'GST-smart batch tracking - Created by migration add_gst_smart_invoice_management.sql';

