"""
MRP, Discount & GST Toggle Migration
Adds fields for enhanced invoice features
"""
from flask import Blueprint, jsonify
from sqlalchemy import text
from models import db

mrp_discount_migration_bp = Blueprint('mrp_discount_migration', __name__)

@mrp_discount_migration_bp.route('/migrate/add-mrp-discount-gst-fields', methods=['GET'])
def add_mrp_discount_gst_fields():
    """
    Migration to add:
    1. MRP field to items table
    2. Discount type/value fields to sales_invoices table
    3. GST toggle to sales_invoices table
    4. GST customer flag to customers table
    """
    try:
        results = []
        
        with db.engine.begin() as conn:
            # 1. Add MRP to items table
            try:
                conn.execute(text("""
                    ALTER TABLE items 
                    ADD COLUMN IF NOT EXISTS mrp NUMERIC(10, 2) DEFAULT NULL;
                """))
                results.append("✅ Added 'mrp' column to items table")
            except Exception as e:
                if "already exists" in str(e).lower():
                    results.append("ℹ️ MRP column already exists in items table")
                else:
                    raise
            
            # 1b. Add discount_percent to items table
            try:
                conn.execute(text("""
                    ALTER TABLE items 
                    ADD COLUMN IF NOT EXISTS discount_percent NUMERIC(5, 2) DEFAULT 0;
                """))
                results.append("✅ Added 'discount_percent' column to items table")
            except Exception as e:
                if "already exists" in str(e).lower():
                    results.append("ℹ️ discount_percent column already exists in items table")
                else:
                    raise
            
            # 2. Add discount fields to invoices
            try:
                conn.execute(text("""
                    ALTER TABLE invoices 
                    ADD COLUMN IF NOT EXISTS discount_type VARCHAR(20) DEFAULT 'flat';
                """))
                results.append("✅ Added 'discount_type' column to invoices table")
            except Exception as e:
                if "already exists" in str(e).lower():
                    results.append("ℹ️ discount_type column already exists")
                else:
                    raise
            
            try:
                conn.execute(text("""
                    ALTER TABLE invoices 
                    ADD COLUMN IF NOT EXISTS discount_value NUMERIC(10, 2) DEFAULT 0;
                """))
                results.append("✅ Added 'discount_value' column to invoices table")
            except Exception as e:
                if "already exists" in str(e).lower():
                    results.append("ℹ️ discount_value column already exists")
                else:
                    raise
            
            # 3. Add GST toggle to invoices
            try:
                conn.execute(text("""
                    ALTER TABLE invoices 
                    ADD COLUMN IF NOT EXISTS gst_enabled BOOLEAN DEFAULT TRUE;
                """))
                results.append("✅ Added 'gst_enabled' column to invoices table")
            except Exception as e:
                if "already exists" in str(e).lower():
                    results.append("ℹ️ gst_enabled column already exists")
                else:
                    raise
            
            # 4. Add GST customer flag to customers
            try:
                conn.execute(text("""
                    ALTER TABLE customers 
                    ADD COLUMN IF NOT EXISTS is_gst_customer BOOLEAN DEFAULT TRUE;
                """))
                results.append("✅ Added 'is_gst_customer' column to customers table")
            except Exception as e:
                if "already exists" in str(e).lower():
                    results.append("ℹ️ is_gst_customer column already exists")
                else:
                    raise
            
            # 5. Create index on MRP for reporting (optional optimization)
            try:
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_items_mrp ON items(mrp);
                """))
                results.append("✅ Created index on items.mrp")
            except Exception as e:
                results.append(f"ℹ️ Index creation skipped: {str(e)}")
        
        return jsonify({
            'status': 'success',
            'message': '✅ Migration completed successfully!',
            'changes': results,
            'next_steps': [
                '1. Restart your Flask app to load new model fields',
                '2. Go to Inventory → Edit Item to set MRP',
                '3. Create invoice with new discount options',
                '4. Toggle GST on/off per invoice',
                '5. Set customer GST preference in customer profile'
            ]
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'❌ Migration failed: {str(e)}',
            'error': str(e)
        }), 500

