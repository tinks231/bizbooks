"""
Migration: Fix missing discount_percent for existing items
Calculates discount_percent from MRP and selling_price for all items where:
- MRP is not null and > 0
- Selling price < MRP
- discount_percent is null or 0

Formula: discount_percent = ((MRP - Selling_Price) / MRP) × 100
"""

from flask import Blueprint, jsonify, g
from sqlalchemy import text
from models.database import db

fix_discounts_bp = Blueprint('fix_discounts', __name__)

@fix_discounts_bp.route('/migrate/fix-item-discounts', methods=['GET'])
def fix_item_discounts():
    """
    Calculate and update discount_percent for items that have MRP and selling_price
    """
    try:
        # Get tenant_id from session/context
        tenant_id = g.get('tenant_id', 1)  # Default to 1 for testing
        
        # Step 1: Get items that need fixing
        items_query = text("""
            SELECT id, name, sku, mrp, selling_price, 
                   discount_percent,
                   ((mrp - selling_price) / mrp) * 100 as calculated_discount
            FROM items
            WHERE tenant_id = :tenant_id
              AND mrp IS NOT NULL
              AND mrp > 0
              AND selling_price > 0
              AND selling_price <= mrp
              AND (discount_percent IS NULL OR discount_percent = 0)
            ORDER BY id
        """)
        
        items = db.session.execute(items_query, {'tenant_id': tenant_id}).fetchall()
        
        if not items:
            return jsonify({
                'status': 'success',
                'message': 'No items need discount calculation',
                'items_fixed': 0
            })
        
        # Step 2: Update each item
        update_count = 0
        fixed_items = []
        
        for item in items:
            calculated_discount = round(item.calculated_discount, 2)
            
            # Ensure discount is between 0 and 100
            calculated_discount = max(0.0, min(100.0, calculated_discount))
            
            # Update the item
            update_query = text("""
                UPDATE items
                SET discount_percent = :discount_percent
                WHERE id = :item_id
            """)
            
            db.session.execute(update_query, {
                'discount_percent': calculated_discount,
                'item_id': item.id
            })
            
            fixed_items.append({
                'id': item.id,
                'name': item.name,
                'sku': item.sku,
                'mrp': float(item.mrp),
                'selling_price': float(item.selling_price),
                'old_discount': float(item.discount_percent) if item.discount_percent else 0.0,
                'new_discount': calculated_discount
            })
            
            update_count += 1
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': f'Fixed discount_percent for {update_count} items',
            'items_fixed': update_count,
            'items': fixed_items
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

