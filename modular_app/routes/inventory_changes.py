"""
Show inventory changes - what was added when
"""

from flask import Blueprint, jsonify, g
from models import db
from sqlalchemy import text
from utils.tenant_middleware import require_tenant, get_current_tenant_id

inventory_changes_bp = Blueprint('inventory_changes', __name__, url_prefix='/diagnose')

@inventory_changes_bp.route('/inventory-changes')
@require_tenant
def inventory_changes():
    """
    Show what changed in inventory between original import and now
    """
    
    try:
        tenant_id = get_current_tenant_id()
        
        result = {
            'tenant_id': tenant_id
        }
        
        # 1. Items created after Dec 10
        new_items = db.session.execute(text("""
            SELECT 
                i.id,
                i.name,
                i.cost_price,
                i.opening_stock,
                i.cost_price * i.opening_stock as total_value,
                i.created_at
            FROM items i
            WHERE i.tenant_id = :tenant_id
            AND i.created_at > '2025-12-10'
            ORDER BY i.created_at
        """), {'tenant_id': tenant_id}).fetchall()
        
        new_items_total = sum(float(item[4]) for item in new_items)
        
        result['items_added_after_dec_10'] = {
            'count': len(new_items),
            'total_value': new_items_total,
            'items': [
                {
                    'id': item[0],
                    'name': item[1],
                    'cost_price': float(item[2]),
                    'quantity': float(item[3]),
                    'total_value': float(item[4]),
                    'created_at': str(item[5])
                }
                for item in new_items[:20]  # Show first 20
            ],
            'showing': min(len(new_items), 20),
            'total_items': len(new_items)
        }
        
        # 2. Current total inventory value
        current_total = db.session.execute(text("""
            SELECT COALESCE(SUM(stock_value), 0)
            FROM item_stocks
            WHERE tenant_id = :tenant_id
        """), {'tenant_id': tenant_id}).fetchone()[0]
        
        # 3. Items count by date
        items_by_date = db.session.execute(text("""
            SELECT 
                DATE(created_at) as date,
                COUNT(*) as count,
                SUM(cost_price * opening_stock) as total_value
            FROM items
            WHERE tenant_id = :tenant_id
            GROUP BY DATE(created_at)
            ORDER BY DATE(created_at)
        """), {'tenant_id': tenant_id}).fetchall()
        
        result['items_by_date'] = [
            {
                'date': str(row[0]),
                'count': row[1],
                'total_value': float(row[2]) if row[2] else 0
            }
            for row in items_by_date
        ]
        
        result['summary'] = {
            'current_total_inventory': float(current_total),
            'new_items_added': len(new_items),
            'new_items_value': new_items_total
        }
        
        return jsonify({
            'status': 'success',
            'analysis': result
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

