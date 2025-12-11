"""
Migration: Add fields to purchase_bill_items for creating new items

WHAT THIS DOES:
- Adds fields to purchase_bill_items table
- Allows creating new inventory items directly from purchase bills
- Stores: selling_price, MRP, SKU, category for new items

NEW FIELDS:
- is_new_item (BOOLEAN) - Flag to indicate item should be created
- sku (VARCHAR) - SKU/Barcode for new item
- selling_price (NUMERIC) - Selling price for new item
- mrp (NUMERIC) - Maximum Retail Price for new item
- category_id (INTEGER) - Link to item category

Created: December 11, 2025
"""

from flask import Blueprint, jsonify
from models import db
from sqlalchemy import text

migration_purchase_bill_items_bp = Blueprint('migration_purchase_bill_items', __name__, url_prefix='/migration')


@migration_purchase_bill_items_bp.route('/add-purchase-bill-item-fields')
def add_purchase_bill_item_fields():
    """
    ONE-TIME migration: Add fields to purchase_bill_items for creating new items
    """
    
    try:
        print("\n" + "="*80)
        print("🔧 ADDING FIELDS TO PURCHASE_BILL_ITEMS TABLE")
        print("="*80 + "\n")
        
        # Check if columns already exist
        result = db.session.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'purchase_bill_items' 
            AND column_name IN ('is_new_item', 'sku', 'selling_price', 'mrp', 'category_id')
        """)).fetchall()
        
        existing_columns = [row[0] for row in result]
        
        if 'is_new_item' in existing_columns:
            print("⚠️ Columns already exist! Skipping migration.\n")
            return jsonify({
                'status': 'skipped',
                'message': 'Columns already exist'
            })
        
        # Add new columns
        print("📝 Adding is_new_item column...")
        db.session.execute(text("""
            ALTER TABLE purchase_bill_items 
            ADD COLUMN IF NOT EXISTS is_new_item BOOLEAN DEFAULT FALSE
        """))
        print("✅ Added is_new_item\n")
        
        print("📝 Adding sku column...")
        db.session.execute(text("""
            ALTER TABLE purchase_bill_items 
            ADD COLUMN IF NOT EXISTS sku VARCHAR(100)
        """))
        print("✅ Added sku\n")
        
        print("📝 Adding selling_price column...")
        db.session.execute(text("""
            ALTER TABLE purchase_bill_items 
            ADD COLUMN IF NOT EXISTS selling_price NUMERIC(15, 2)
        """))
        print("✅ Added selling_price\n")
        
        print("📝 Adding mrp column...")
        db.session.execute(text("""
            ALTER TABLE purchase_bill_items 
            ADD COLUMN IF NOT EXISTS mrp NUMERIC(15, 2)
        """))
        print("✅ Added mrp\n")
        
        print("📝 Adding category_id column...")
        db.session.execute(text("""
            ALTER TABLE purchase_bill_items 
            ADD COLUMN IF NOT EXISTS category_id INTEGER REFERENCES item_categories(id)
        """))
        print("✅ Added category_id\n")
        
        db.session.commit()
        
        print("="*80)
        print("🎉 SUCCESS! Fields added to purchase_bill_items")
        print("="*80)
        print("\n✅ Can now create items from purchase bills!\n")
        
        return jsonify({
            'status': 'success',
            'message': 'Fields added successfully to purchase_bill_items'
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"\n❌ ERROR: {str(e)}\n")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

