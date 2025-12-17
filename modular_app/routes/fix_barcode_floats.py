"""
Migration: Fix barcodes with .0 suffix
Removes .0 from barcodes that were imported as floats from Excel

Example: 8901230000000.0 → 8901230000000
"""

from flask import Blueprint, jsonify, g
from sqlalchemy import text
from models.database import db

fix_barcodes_bp = Blueprint('fix_barcodes', __name__)

@fix_barcodes_bp.route('/migrate/fix-barcode-floats', methods=['GET'])
def fix_barcode_floats():
    """
    Remove .0 suffix from barcodes that have it
    """
    try:
        # Get tenant_id from session/context
        tenant_id = g.get('tenant_id', 1)  # Default to 1 for testing
        
        # Step 1: Get items with barcodes ending in .0
        items_query = text("""
            SELECT id, name, sku, barcode
            FROM items
            WHERE tenant_id = :tenant_id
              AND barcode IS NOT NULL
              AND barcode LIKE '%.0'
            ORDER BY id
        """)
        
        items = db.session.execute(items_query, {'tenant_id': tenant_id}).fetchall()
        
        if not items:
            return jsonify({
                'status': 'success',
                'message': 'No barcodes need fixing',
                'items_fixed': 0
            })
        
        # Step 2: Fix each barcode
        fixed_items = []
        
        for item in items:
            old_barcode = item.barcode
            
            # Remove .0 suffix
            try:
                # Convert to float, then to int, then to string (removes .0)
                new_barcode = str(int(float(old_barcode)))
                
                # Update the item
                update_query = text("""
                    UPDATE items
                    SET barcode = :new_barcode
                    WHERE id = :item_id
                """)
                
                db.session.execute(update_query, {
                    'new_barcode': new_barcode,
                    'item_id': item.id
                })
                
                fixed_items.append({
                    'id': item.id,
                    'name': item.name,
                    'sku': item.sku,
                    'old_barcode': old_barcode,
                    'new_barcode': new_barcode
                })
            except:
                # Skip if conversion fails
                continue
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': f'Fixed {len(fixed_items)} barcodes',
            'items_fixed': len(fixed_items),
            'items': fixed_items
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

