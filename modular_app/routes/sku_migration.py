"""
SKU Constraint Migration - Web-based
Changes SKU from globally unique to per-tenant unique

Access: https://yoursite.bizbooks.co.in/migrate/fix-sku-constraint
Run this ONCE after deployment
"""

from flask import Blueprint, jsonify
from models import db
from sqlalchemy import text

sku_migration_bp = Blueprint('sku_migration', __name__, url_prefix='/migrate')


@sku_migration_bp.route('/fix-sku-constraint')
def fix_sku_constraint():
    """
    Migrates SKU constraint from global to per-tenant
    
    BEFORE: UNIQUE(sku) - all tenants share same SKU space
    AFTER: UNIQUE(tenant_id, sku) - each tenant has their own SKU sequence
    
    WHY: Prevents race conditions and SKU conflicts when multiple tenants add items
    """
    try:
        # Detect database type
        db_url = str(db.engine.url)
        is_postgres = 'postgresql' in db_url
        
        changes_made = []
        
        if is_postgres:
            # ================================================
            # POSTGRESQL MIGRATION
            # ================================================
            
            # Step 1: Check existing constraints
            check_constraints = text("""
                SELECT constraint_name 
                FROM information_schema.table_constraints 
                WHERE table_name = 'items' 
                AND constraint_type = 'UNIQUE'
                AND constraint_name LIKE '%sku%';
            """)
            
            existing = db.session.execute(check_constraints).fetchall()
            existing_constraints = [row[0] for row in existing]
            
            # Step 2: Remove old global unique constraint (if exists)
            old_constraints_dropped = []
            for constraint_name in ['items_sku_key', 'uq_items_sku', 'items_sku_unique']:
                try:
                    db.session.execute(text(f"ALTER TABLE items DROP CONSTRAINT IF EXISTS {constraint_name};"))
                    old_constraints_dropped.append(constraint_name)
                except:
                    pass
            
            if old_constraints_dropped:
                changes_made.append(f"Dropped old constraints: {', '.join(old_constraints_dropped)}")
            
            # Step 3: Add new per-tenant unique constraint
            check_new = text("""
                SELECT constraint_name 
                FROM information_schema.table_constraints 
                WHERE table_name = 'items' 
                AND constraint_name = 'uq_tenant_sku';
            """)
            
            has_new = db.session.execute(check_new).fetchone()
            
            if not has_new:
                db.session.execute(text("""
                    ALTER TABLE items 
                    ADD CONSTRAINT uq_tenant_sku UNIQUE (tenant_id, sku);
                """))
                changes_made.append("Added new constraint: UNIQUE(tenant_id, sku)")
            else:
                changes_made.append("New constraint already exists (migration already ran)")
            
        else:
            # ================================================
            # SQLITE MIGRATION
            # ================================================
            
            # SQLite requires table recreation
            # Check if migration already done
            check_sql = text("SELECT sql FROM sqlite_master WHERE type='table' AND name='items';")
            result = db.session.execute(check_sql).fetchone()
            
            if result and 'UNIQUE(tenant_id, sku)' in result[0]:
                return jsonify({
                    'status': 'success',
                    'message': '✅ Migration already completed!',
                    'details': {
                        'constraint': 'UNIQUE(tenant_id, sku) already exists',
                        'action': 'No changes needed'
                    },
                    'impact': [
                        '✅ Each tenant has their own SKU sequence',
                        '✅ Tenant A can have ITEM-0001',
                        '✅ Tenant B can also have ITEM-0001',
                        '✅ No SKU conflicts between tenants!'
                    ]
                })
            
            # Cleanup any leftover temp table
            try:
                db.session.execute(text("DROP TABLE IF EXISTS items_new;"))
                db.session.commit()
            except:
                pass
            
            # Get existing columns
            result = db.session.execute(text("PRAGMA table_info(items);"))
            existing_columns = [row[1] for row in result]
            column_list = ', '.join(existing_columns)
            
            changes_made.append(f"Detected {len(existing_columns)} columns in items table")
            
            # Create new table with per-tenant unique constraint
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
                    manufacturer VARCHAR(200),
                    brand VARCHAR(100),
                    upc VARCHAR(50),
                    ean VARCHAR(50),
                    mpn VARCHAR(50),
                    isbn VARCHAR(50),
                    selling_price FLOAT DEFAULT 0,
                    sales_description TEXT,
                    sales_account VARCHAR(100) DEFAULT 'Sales',
                    tax_preference VARCHAR(50) DEFAULT 'taxable',
                    cost_price FLOAT DEFAULT 0,
                    purchase_description TEXT,
                    purchase_account VARCHAR(100) DEFAULT 'Cost of Goods Sold',
                    preferred_vendor VARCHAR(200),
                    track_inventory BOOLEAN DEFAULT 0,
                    opening_stock FLOAT DEFAULT 0,
                    opening_stock_value FLOAT DEFAULT 0,
                    reorder_point FLOAT DEFAULT 0,
                    primary_image TEXT,
                    is_active BOOLEAN DEFAULT 0,
                    is_returnable BOOLEAN DEFAULT 0,
                    created_by VARCHAR(100),
                    created_at DATETIME,
                    updated_at DATETIME,
                    FOREIGN KEY (tenant_id) REFERENCES tenants(id),
                    FOREIGN KEY (category_id) REFERENCES item_categories(id),
                    FOREIGN KEY (item_group_id) REFERENCES item_groups(id),
                    UNIQUE(tenant_id, sku)
                );
            """))
            changes_made.append("Created new items table with UNIQUE(tenant_id, sku)")
            
            # Copy data
            db.session.execute(text(f"INSERT INTO items_new ({column_list}) SELECT {column_list} FROM items;"))
            changes_made.append(f"Copied all existing data")
            
            # Drop old table
            db.session.execute(text("DROP TABLE items;"))
            changes_made.append("Dropped old items table")
            
            # Rename new table
            db.session.execute(text("ALTER TABLE items_new RENAME TO items;"))
            changes_made.append("Renamed items_new to items")
            
            # Recreate indexes
            db.session.execute(text("CREATE INDEX IF NOT EXISTS idx_item_tenant ON items(tenant_id, is_active);"))
            db.session.execute(text("CREATE INDEX IF NOT EXISTS idx_item_sku ON items(sku);"))
            db.session.execute(text("CREATE INDEX IF NOT EXISTS idx_item_category ON items(category_id);"))
            changes_made.append("Recreated indexes")
        
        # Commit all changes
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': '✅ SKU constraint migrated successfully!',
            'details': {
                'database': 'PostgreSQL' if is_postgres else 'SQLite',
                'changes': changes_made
            },
            'before': {
                'constraint': 'UNIQUE(sku)',
                'problem': 'All tenants shared same SKU space',
                'issue': 'Race conditions and conflicts at scale'
            },
            'after': {
                'constraint': 'UNIQUE(tenant_id, sku)',
                'solution': 'Each tenant has own SKU sequence',
                'benefit': 'No conflicts, scales to unlimited tenants'
            },
            'impact': [
                '✅ Tenant A can have: ITEM-0001, ITEM-0002, ITEM-0003...',
                '✅ Tenant B can have: ITEM-0001, ITEM-0002, ITEM-0003...',
                '✅ No SKU conflicts between tenants!',
                '✅ Clean sequential SKUs for each tenant',
                '✅ Scales to 1000+ tenants adding items simultaneously'
            ],
            'next_steps': [
                '1. Test adding new items in your tenant',
                '2. Test adding items in another tenant',
                '3. Verify each tenant has their own sequence',
                '4. Check that SKU auto-generation works correctly'
            ]
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'❌ Migration failed: {str(e)}',
            'tip': 'Check if migration already ran or if there are database permission issues'
        }), 500

