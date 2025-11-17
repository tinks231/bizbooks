#!/usr/bin/env python3
"""
Database Migration: Change SKU Unique Constraint
=================================================
Changes SKU from globally unique to per-tenant unique

BEFORE: UNIQUE(sku) - SKU must be unique across ALL tenants
AFTER:  UNIQUE(tenant_id, sku) - SKU unique per tenant

This allows:
- Tenant A: ITEM-0001, ITEM-0002
- Tenant B: ITEM-0001, ITEM-0002 (same SKUs, different tenant - OK!)

Run this ONCE after deploying the new code.
"""

import sys
import os

# Add modular_app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modular_app'))

from app import app, db
from sqlalchemy import text

def migrate():
    """Migrate SKU constraint from global to per-tenant"""
    
    print("\n" + "="*70)
    print("🔄 MIGRATING SKU UNIQUE CONSTRAINT")
    print("="*70)
    
    with app.app_context():
        try:
            # Check database type
            engine = db.engine
            dialect = engine.dialect.name
            
            print(f"\n📊 Database: {dialect}")
            print(f"🔗 URL: {engine.url}")
            
            if dialect == 'sqlite':
                print("\n⚠️  SQLite detected - requires table recreation")
                print("="*70)
                
                # SQLite doesn't support DROP CONSTRAINT
                # Must recreate table
                
                # Step 1: Create new table with correct constraint
                print("1. Creating new items table...")
                db.session.execute(text("""
                    CREATE TABLE items_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        tenant_id INTEGER NOT NULL,
                        name VARCHAR(200) NOT NULL,
                        sku VARCHAR(100) NOT NULL,
                        type VARCHAR(20) DEFAULT 'goods',
                        category_id INTEGER,
                        item_group_id INTEGER,
                        unit VARCHAR(50) DEFAULT 'nos',
                        dimensions_length FLOAT,
                        dimensions_width FLOAT,
                        dimensions_height FLOAT,
                        dimensions_unit VARCHAR(10) DEFAULT 'cm',
                        weight FLOAT,
                        weight_unit VARCHAR(10) DEFAULT 'kg',
                        manufacturer VARCHAR(100),
                        brand VARCHAR(100),
                        upc VARCHAR(50),
                        ean VARCHAR(50),
                        mpn VARCHAR(50),
                        isbn VARCHAR(50),
                        hsn_code VARCHAR(20),
                        selling_price FLOAT DEFAULT 0,
                        sales_description TEXT,
                        sales_account VARCHAR(100) DEFAULT 'Sales',
                        tax_preference VARCHAR(20) DEFAULT 'taxable',
                        gst_rate FLOAT DEFAULT 18,
                        cost_price FLOAT DEFAULT 0,
                        purchase_description TEXT,
                        purchase_account VARCHAR(100) DEFAULT 'Cost of Goods Sold',
                        preferred_vendor VARCHAR(100),
                        track_inventory BOOLEAN DEFAULT 0,
                        opening_stock FLOAT DEFAULT 0,
                        opening_stock_value FLOAT DEFAULT 0,
                        reorder_point FLOAT DEFAULT 0,
                        primary_image VARCHAR(500),
                        is_active BOOLEAN DEFAULT 1,
                        is_returnable BOOLEAN DEFAULT 0,
                        created_by VARCHAR(100),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (tenant_id) REFERENCES tenants(id),
                        FOREIGN KEY (category_id) REFERENCES item_categories(id),
                        FOREIGN KEY (item_group_id) REFERENCES item_groups(id),
                        UNIQUE(tenant_id, sku)
                    );
                """))
                
                # Step 2: Copy data
                print("2. Copying data from old table...")
                db.session.execute(text("""
                    INSERT INTO items_new SELECT * FROM items;
                """))
                
                # Step 3: Drop old table
                print("3. Dropping old table...")
                db.session.execute(text("DROP TABLE items;"))
                
                # Step 4: Rename new table
                print("4. Renaming new table...")
                db.session.execute(text("ALTER TABLE items_new RENAME TO items;"))
                
                # Step 5: Recreate indexes
                print("5. Recreating indexes...")
                db.session.execute(text("""
                    CREATE INDEX idx_item_tenant ON items(tenant_id, is_active);
                """))
                db.session.execute(text("""
                    CREATE INDEX idx_item_sku ON items(sku);
                """))
                db.session.execute(text("""
                    CREATE INDEX idx_item_category ON items(category_id);
                """))
                
            elif dialect == 'postgresql':
                print("\n✅ PostgreSQL detected")
                print("="*70)
                
                # Step 1: Find and drop old unique constraint
                print("1. Dropping old UNIQUE(sku) constraint...")
                
                # Find constraint name
                result = db.session.execute(text("""
                    SELECT constraint_name 
                    FROM information_schema.table_constraints 
                    WHERE table_name = 'items' 
                    AND constraint_type = 'UNIQUE'
                    AND constraint_name LIKE '%sku%';
                """))
                
                constraint_name = None
                for row in result:
                    constraint_name = row[0]
                    break
                
                if constraint_name:
                    print(f"   Found constraint: {constraint_name}")
                    db.session.execute(text(f"""
                        ALTER TABLE items DROP CONSTRAINT {constraint_name};
                    """))
                else:
                    print("   No old constraint found (might be already migrated)")
                
                # Step 2: Add new composite unique constraint
                print("2. Adding new UNIQUE(tenant_id, sku) constraint...")
                db.session.execute(text("""
                    ALTER TABLE items 
                    ADD CONSTRAINT uq_tenant_sku UNIQUE (tenant_id, sku);
                """))
            
            else:
                print(f"\n❌ Unsupported database: {dialect}")
                print("   Manual migration required")
                return False
            
            # Commit changes
            db.session.commit()
            
            print("\n" + "="*70)
            print("✅ MIGRATION SUCCESSFUL!")
            print("="*70)
            print("\n📊 Results:")
            print("   ✅ Old constraint (UNIQUE sku) removed")
            print("   ✅ New constraint (UNIQUE tenant_id, sku) added")
            print("\n💡 What this means:")
            print("   • Each tenant can now have ITEM-0001, ITEM-0002...")
            print("   • SKUs are unique within each tenant")
            print("   • No more global SKU conflicts!")
            print("   • Scales to unlimited tenants ✨")
            print("\n" + "="*70)
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ MIGRATION FAILED: {e}")
            print("\n💡 If error is 'duplicate key' or 'already exists':")
            print("   Migration might have already run - check constraint manually")
            return False

if __name__ == '__main__':
    success = migrate()
    sys.exit(0 if success else 1)

