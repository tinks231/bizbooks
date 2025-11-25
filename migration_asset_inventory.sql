-- Migration: Asset Inventory Management
-- Date: 2025-11-25
-- Purpose: Track total inventory and damaged/lost assets

-- 1. Add inventory fields to tenants table
ALTER TABLE tenants 
ADD COLUMN IF NOT EXISTS total_bottles_inventory INTEGER DEFAULT 0;

ALTER TABLE tenants 
ADD COLUMN IF NOT EXISTS damaged_bottles_count INTEGER DEFAULT 0;

-- 2. Add comments
COMMENT ON COLUMN tenants.total_bottles_inventory IS 'Total returnable assets (bottles/containers) owned by business';
COMMENT ON COLUMN tenants.damaged_bottles_count IS 'Total damaged/lost/broken assets';

-- 3. Optional: Set default values for existing tenants (adjust as needed)
-- UPDATE tenants SET total_bottles_inventory = 0 WHERE total_bottles_inventory IS NULL;
-- UPDATE tenants SET damaged_bottles_count = 0 WHERE damaged_bottles_count IS NULL;

