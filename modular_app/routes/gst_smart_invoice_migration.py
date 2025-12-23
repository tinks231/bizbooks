"""
GST Smart Invoice Management Migration
Adds batch-level GST tracking and smart invoice validation

Access: https://yoursite.bizbooks.co.in/migrate/gst-smart-invoice
Run this ONCE after deployment
"""

from flask import Blueprint, jsonify
from models import db
from sqlalchemy import text, inspect

gst_smart_invoice_migration_bp = Blueprint('gst_smart_invoice_migration', __name__, url_prefix='/migrate')


@gst_smart_invoice_migration_bp.route('/gst-smart-invoice')
def migrate_gst_smart_invoice():
    """
    Migrate database for GST-smart invoice management:
    - Create stock_batches table
    - Add invoice_type to invoices
    - Add bill_type to purchase_bills
    - Add GST classification fields to vendors/customers
    - Create other_incomes table
    """
    try:
        # Detect database type
        db_url = str(db.engine.url)
        is_postgres = 'postgresql' in db_url
        
        changes_made = []
        errors = []
        
        # ================================================
        # 1. CREATE STOCK_BATCHES TABLE
        # ================================================
        try:
            # Check if table exists
            inspector = inspect(db.engine)
            if 'stock_batches' not in inspector.get_table_names():
                if is_postgres:
                    db.session.execute(text("""
                        CREATE TABLE stock_batches (
                            id SERIAL PRIMARY KEY,
                            tenant_id INTEGER NOT NULL REFERENCES tenants(id),
                            item_id INTEGER NOT NULL REFERENCES items(id),
                            purchase_bill_id INTEGER REFERENCES purchase_bills(id),
                            purchase_bill_item_id INTEGER REFERENCES purchase_bill_items(id),
                            purchase_bill_number VARCHAR(50),
                            purchase_date DATE,
                            vendor_id INTEGER REFERENCES vendors(id),
                            vendor_name VARCHAR(200),
                            site_id INTEGER REFERENCES sites(id),
                            quantity_purchased NUMERIC(15, 3) NOT NULL,
                            quantity_remaining NUMERIC(15, 3) NOT NULL,
                            quantity_sold NUMERIC(15, 3) DEFAULT 0,
                            quantity_adjusted NUMERIC(15, 3) DEFAULT 0,
                            purchased_with_gst BOOLEAN NOT NULL DEFAULT FALSE,
                            base_cost_per_unit NUMERIC(15, 2) NOT NULL,
                            gst_rate NUMERIC(5, 2) DEFAULT 0,
                            gst_per_unit NUMERIC(15, 2) DEFAULT 0,
                            total_cost_per_unit NUMERIC(15, 2) NOT NULL,
                            itc_per_unit NUMERIC(15, 2) DEFAULT 0,
                            itc_total_available NUMERIC(15, 2) DEFAULT 0,
                            itc_claimed NUMERIC(15, 2) DEFAULT 0,
                            itc_remaining NUMERIC(15, 2) DEFAULT 0,
                            batch_number VARCHAR(50),
                            expiry_date DATE,
                            batch_status VARCHAR(20) DEFAULT 'active',
                            notes TEXT,
                            created_by VARCHAR(100),
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        );
                    """))
                    
                    # Create indexes
                    db.session.execute(text("CREATE INDEX idx_batch_tenant_item ON stock_batches(tenant_id, item_id);"))
                    db.session.execute(text("CREATE INDEX idx_batch_purchase ON stock_batches(purchase_bill_id);"))
                    db.session.execute(text("CREATE INDEX idx_batch_status ON stock_batches(batch_status);"))
                    
                else:  # SQLite
                    db.session.execute(text("""
                        CREATE TABLE stock_batches (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            tenant_id INTEGER NOT NULL,
                            item_id INTEGER NOT NULL,
                            purchase_bill_id INTEGER,
                            purchase_bill_item_id INTEGER,
                            purchase_bill_number VARCHAR(50),
                            purchase_date DATE,
                            vendor_id INTEGER,
                            vendor_name VARCHAR(200),
                            site_id INTEGER,
                            quantity_purchased NUMERIC(15, 3) NOT NULL,
                            quantity_remaining NUMERIC(15, 3) NOT NULL,
                            quantity_sold NUMERIC(15, 3) DEFAULT 0,
                            quantity_adjusted NUMERIC(15, 3) DEFAULT 0,
                            purchased_with_gst BOOLEAN NOT NULL DEFAULT 0,
                            base_cost_per_unit NUMERIC(15, 2) NOT NULL,
                            gst_rate NUMERIC(5, 2) DEFAULT 0,
                            gst_per_unit NUMERIC(15, 2) DEFAULT 0,
                            total_cost_per_unit NUMERIC(15, 2) NOT NULL,
                            itc_per_unit NUMERIC(15, 2) DEFAULT 0,
                            itc_total_available NUMERIC(15, 2) DEFAULT 0,
                            itc_claimed NUMERIC(15, 2) DEFAULT 0,
                            itc_remaining NUMERIC(15, 2) DEFAULT 0,
                            batch_number VARCHAR(50),
                            expiry_date DATE,
                            batch_status VARCHAR(20) DEFAULT 'active',
                            notes TEXT,
                            created_by VARCHAR(100),
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY (tenant_id) REFERENCES tenants(id),
                            FOREIGN KEY (item_id) REFERENCES items(id),
                            FOREIGN KEY (purchase_bill_id) REFERENCES purchase_bills(id),
                            FOREIGN KEY (purchase_bill_item_id) REFERENCES purchase_bill_items(id),
                            FOREIGN KEY (vendor_id) REFERENCES vendors(id),
                            FOREIGN KEY (site_id) REFERENCES sites(id)
                        );
                    """))
                    
                    # Create indexes
                    db.session.execute(text("CREATE INDEX idx_batch_tenant_item ON stock_batches(tenant_id, item_id);"))
                    db.session.execute(text("CREATE INDEX idx_batch_purchase ON stock_batches(purchase_bill_id);"))
                    db.session.execute(text("CREATE INDEX idx_batch_status ON stock_batches(batch_status);"))
                
                changes_made.append("✅ Created stock_batches table")
            else:
                changes_made.append("ℹ️ stock_batches table already exists")
        except Exception as e:
            errors.append(f"❌ Error creating stock_batches: {str(e)}")
        
        # ================================================
        # 2. UPDATE ITEMS TABLE
        # ================================================
        def add_column_if_not_exists(table, column, definition):
            try:
                columns = [col['name'] for col in inspector.get_columns(table)]
                if column not in columns:
                    db.session.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {definition};"))
                    return f"✅ Added {table}.{column}"
                return f"ℹ️ {table}.{column} already exists"
            except Exception as e:
                return f"❌ Error adding {table}.{column}: {str(e)}"
        
        changes_made.append(add_column_if_not_exists('items', 'gst_classification', "VARCHAR(20) DEFAULT 'gst_applicable'"))
        
        # ================================================
        # 3. UPDATE INVOICES TABLE
        # ================================================
        changes_made.append(add_column_if_not_exists('invoices', 'invoice_type', "VARCHAR(20) DEFAULT 'taxable'"))
        changes_made.append(add_column_if_not_exists('invoices', 'linked_invoice_id', "INTEGER"))
        changes_made.append(add_column_if_not_exists('invoices', 'credit_commission_rate', "NUMERIC(5, 2) DEFAULT 0"))
        changes_made.append(add_column_if_not_exists('invoices', 'credit_commission_amount', "NUMERIC(15, 2) DEFAULT 0"))
        changes_made.append(add_column_if_not_exists('invoices', 'reduce_stock', "BOOLEAN DEFAULT TRUE" if is_postgres else "BOOLEAN DEFAULT 1"))
        
        # ================================================
        # 4. UPDATE INVOICE_ITEMS TABLE
        # ================================================
        changes_made.append(add_column_if_not_exists('invoice_items', 'stock_batch_id', "INTEGER"))
        changes_made.append(add_column_if_not_exists('invoice_items', 'uses_gst_stock', "BOOLEAN DEFAULT TRUE" if is_postgres else "BOOLEAN DEFAULT 1"))
        changes_made.append(add_column_if_not_exists('invoice_items', 'cost_base', "NUMERIC(15, 2) DEFAULT 0"))
        changes_made.append(add_column_if_not_exists('invoice_items', 'cost_gst_paid', "NUMERIC(15, 2) DEFAULT 0"))
        
        # ================================================
        # 5. UPDATE PURCHASE_BILLS TABLE
        # ================================================
        changes_made.append(add_column_if_not_exists('purchase_bills', 'bill_type', "VARCHAR(20) DEFAULT 'taxable'"))
        changes_made.append(add_column_if_not_exists('purchase_bills', 'gst_applicable', "BOOLEAN DEFAULT TRUE" if is_postgres else "BOOLEAN DEFAULT 1"))
        
        # ================================================
        # 6. UPDATE VENDORS TABLE
        # ================================================
        changes_made.append(add_column_if_not_exists('vendors', 'gst_registration_type', "VARCHAR(50) DEFAULT 'registered'"))
        changes_made.append(add_column_if_not_exists('vendors', 'composition_rate', "NUMERIC(5, 2)"))
        changes_made.append(add_column_if_not_exists('vendors', 'gst_validated', "BOOLEAN DEFAULT FALSE" if is_postgres else "BOOLEAN DEFAULT 0"))
        
        # ================================================
        # 7. UPDATE CUSTOMERS TABLE
        # ================================================
        changes_made.append(add_column_if_not_exists('customers', 'gst_registration_type', "VARCHAR(50) DEFAULT 'unregistered'"))
        changes_made.append(add_column_if_not_exists('customers', 'gst_validated', "BOOLEAN DEFAULT FALSE" if is_postgres else "BOOLEAN DEFAULT 0"))
        
        # ================================================
        # 8. CREATE OTHER_INCOMES TABLE
        # ================================================
        try:
            if 'other_incomes' not in inspector.get_table_names():
                if is_postgres:
                    db.session.execute(text("""
                        CREATE TABLE other_incomes (
                            id SERIAL PRIMARY KEY,
                            tenant_id INTEGER NOT NULL REFERENCES tenants(id),
                            invoice_id INTEGER REFERENCES invoices(id),
                            income_category VARCHAR(100),
                            amount NUMERIC(15, 2) NOT NULL,
                            income_date DATE NOT NULL,
                            notes TEXT,
                            reference_number VARCHAR(100),
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            created_by VARCHAR(100)
                        );
                    """))
                    
                    # Create indexes
                    db.session.execute(text("CREATE INDEX idx_other_income_tenant ON other_incomes(tenant_id);"))
                    db.session.execute(text("CREATE INDEX idx_other_income_invoice ON other_incomes(invoice_id);"))
                    db.session.execute(text("CREATE INDEX idx_other_income_date ON other_incomes(income_date);"))
                    
                else:  # SQLite
                    db.session.execute(text("""
                        CREATE TABLE other_incomes (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            tenant_id INTEGER NOT NULL,
                            invoice_id INTEGER,
                            income_category VARCHAR(100),
                            amount NUMERIC(15, 2) NOT NULL,
                            income_date DATE NOT NULL,
                            notes TEXT,
                            reference_number VARCHAR(100),
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            created_by VARCHAR(100),
                            FOREIGN KEY (tenant_id) REFERENCES tenants(id),
                            FOREIGN KEY (invoice_id) REFERENCES invoices(id)
                        );
                    """))
                    
                    # Create indexes
                    db.session.execute(text("CREATE INDEX idx_other_income_tenant ON other_incomes(tenant_id);"))
                    db.session.execute(text("CREATE INDEX idx_other_income_invoice ON other_incomes(invoice_id);"))
                    db.session.execute(text("CREATE INDEX idx_other_income_date ON other_incomes(income_date);"))
                
                changes_made.append("✅ Created other_incomes table")
            else:
                changes_made.append("ℹ️ other_incomes table already exists")
        except Exception as e:
            errors.append(f"❌ Error creating other_incomes: {str(e)}")
        
        # ================================================
        # 9. UPDATE EXISTING DATA (SAFE DEFAULTS)
        # ================================================
        try:
            # Mark all existing invoices as 'taxable' (safe default)
            db.session.execute(text("""
                UPDATE invoices 
                SET invoice_type = 'taxable', 
                    reduce_stock = TRUE 
                WHERE invoice_type IS NULL OR invoice_type = '';
            """))
            
            # Mark all existing purchase bills as 'taxable' (safe default)
            db.session.execute(text("""
                UPDATE purchase_bills 
                SET bill_type = 'taxable', 
                    gst_applicable = TRUE 
                WHERE bill_type IS NULL OR bill_type = '';
            """))
            
            # Mark all existing items as 'gst_applicable' (safe default)
            db.session.execute(text("""
                UPDATE items 
                SET gst_classification = 'gst_applicable' 
                WHERE gst_classification IS NULL OR gst_classification = '';
            """))
            
            # Mark vendors with GSTIN as 'registered'
            db.session.execute(text("""
                UPDATE vendors 
                SET gst_registration_type = 'registered' 
                WHERE (gstin IS NOT NULL AND gstin != '');
            """))
            
            db.session.execute(text("""
                UPDATE vendors 
                SET gst_registration_type = 'unregistered' 
                WHERE (gstin IS NULL OR gstin = '') AND (gst_registration_type IS NULL OR gst_registration_type = '');
            """))
            
            # Mark customers with GSTIN as 'registered'
            db.session.execute(text("""
                UPDATE customers 
                SET gst_registration_type = 'registered' 
                WHERE (gstin IS NOT NULL AND gstin != '');
            """))
            
            db.session.execute(text("""
                UPDATE customers 
                SET gst_registration_type = 'unregistered' 
                WHERE (gstin IS NULL OR gstin = '') AND (gst_registration_type IS NULL OR gst_registration_type = '');
            """))
            
            changes_made.append("✅ Updated existing data with safe defaults")
        except Exception as e:
            errors.append(f"⚠️ Warning updating existing data: {str(e)}")
        
        # Commit all changes
        db.session.commit()
        
        return jsonify({
            'status': 'success' if not errors else 'partial_success',
            'message': '🎉 GST Smart Invoice Migration Completed!',
            'changes': changes_made,
            'errors': errors if errors else None,
            'next_steps': [
                '✅ Stock batch tracking enabled',
                '✅ Smart invoice validation ready',
                '✅ Credit adjustment feature available',
                '⚠️ Restart the application to load new models',
                '📝 Test purchase bill creation with GST toggle',
                '📝 Test invoice creation with smart validation'
            ]
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'❌ Migration failed: {str(e)}',
            'details': 'Please check the error logs and try again'
        }), 500


@gst_smart_invoice_migration_bp.route('/gst-smart-invoice/status')
def check_migration_status():
    """Check if migration has been run"""
    try:
        inspector = inspect(db.engine)
        
        status = {
            'stock_batches': 'stock_batches' in inspector.get_table_names(),
            'other_incomes': 'other_incomes' in inspector.get_table_names(),
            'invoices.invoice_type': 'invoice_type' in [col['name'] for col in inspector.get_columns('invoices')],
            'purchase_bills.bill_type': 'bill_type' in [col['name'] for col in inspector.get_columns('purchase_bills')],
            'vendors.gst_registration_type': 'gst_registration_type' in [col['name'] for col in inspector.get_columns('vendors')],
        }
        
        all_done = all(status.values())
        
        return jsonify({
            'migrated': all_done,
            'details': status,
            'message': '✅ Migration complete!' if all_done else '⚠️ Migration pending or partial'
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'message': 'Could not check migration status'
        }), 500

