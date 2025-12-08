"""
Barcode API Endpoints
=====================
Fast API routes for barcode operations

Endpoints:
- POST /api/barcode/search - Search item by barcode
- POST /api/barcode/check-duplicate - Check if barcode exists
- POST /api/barcode/generate - Auto-generate barcode for item
"""

from flask import Blueprint, request, jsonify, g
from models.item import Item
from models import db
import logging

barcode_api_bp = Blueprint('barcode_api', __name__, url_prefix='/api/barcode')
logger = logging.getLogger(__name__)


@barcode_api_bp.route('/search', methods=['GET', 'POST'])
def search_by_barcode():
    """
    Search for an item by barcode
    
    Query params:
        code: Barcode string to search
        
    Returns:
        JSON with item details or 404 if not found
    """
    try:
        # Get barcode from query params or JSON body
        barcode = request.args.get('code') or request.json.get('code') if request.is_json else None
        
        if not barcode:
            return jsonify({'error': 'Barcode required'}), 400
        
        # Get tenant from session
        tenant_id = g.tenant.id if hasattr(g, 'tenant') else None
        if not tenant_id:
            return jsonify({'error': 'Tenant not found'}), 401
        
        # Search for item (strip whitespace and handle different formats)
        barcode_clean = barcode.strip().replace(' ', '').replace('-', '')
        
        item = Item.query.filter_by(
            barcode=barcode_clean,
            tenant_id=tenant_id,
            is_active=True
        ).first()
        
        if not item:
            # Try searching without stripping (in case barcode has spaces stored)
            item = Item.query.filter_by(
                barcode=barcode,
                tenant_id=tenant_id,
                is_active=True
            ).first()
        
        if not item:
            logger.warning(f"Barcode not found for tenant {tenant_id}: '{barcode}' (cleaned: '{barcode_clean}')")
            
            # Check if barcode exists for ANY tenant (debugging)
            any_item = Item.query.filter_by(barcode=barcode_clean).first()
            if any_item:
                logger.error(f"FOUND barcode in tenant {any_item.tenant_id} but user is in tenant {tenant_id}!")
            
            return jsonify({
                'found': False,
                'error': 'Item not found',
                'barcode': barcode
            }), 404
        
        # Get total stock
        total_stock = sum([stock.quantity_available for stock in item.stocks]) if item.track_inventory else None
        
        # Return item details
        return jsonify({
            'found': True,
            'item': {
                'id': item.id,
                'name': item.name,
                'sku': item.sku,
                'barcode': item.barcode,
                'mrp': item.mrp,
                'discount_percent': item.discount_percent or 0,
                'selling_price': item.selling_price,
                'cost_price': item.cost_price,
                'gst_rate': item.gst_rate or 18,
                'hsn_code': item.hsn_code or '',
                'unit': item.unit or 'nos',
                'track_inventory': item.track_inventory,
                'stock': total_stock if total_stock is not None else 'N/A',
                'is_low_stock': item.is_low_stock(),
                'category': item.category.name if item.category else None,
                'brand': item.brand,
                'manufacturer': item.manufacturer
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error searching barcode: {str(e)}")
        return jsonify({'error': f'Search failed: {str(e)}'}), 500


@barcode_api_bp.route('/check-duplicate', methods=['POST'])
def check_duplicate():
    """
    Check if a barcode already exists for this tenant
    
    JSON body:
        barcode: Barcode to check
        item_id: Optional - exclude this item ID from check (for editing)
        
    Returns:
        JSON with exists: true/false
    """
    try:
        data = request.json
        barcode = data.get('barcode', '').strip()
        item_id = data.get('item_id')
        
        if not barcode:
            return jsonify({'error': 'Barcode required'}), 400
        
        tenant_id = g.tenant.id if hasattr(g, 'tenant') else None
        if not tenant_id:
            return jsonify({'error': 'Tenant not found'}), 401
        
        # Build query
        query = Item.query.filter_by(
            barcode=barcode,
            tenant_id=tenant_id
        )
        
        # Exclude current item if editing
        if item_id:
            query = query.filter(Item.id != item_id)
        
        existing_item = query.first()
        
        if existing_item:
            return jsonify({
                'exists': True,
                'item': {
                    'id': existing_item.id,
                    'name': existing_item.name,
                    'sku': existing_item.sku
                }
            }), 200
        else:
            return jsonify({'exists': False}), 200
            
    except Exception as e:
        logger.error(f"Error checking duplicate barcode: {str(e)}")
        return jsonify({'error': f'Check failed: {str(e)}'}), 500


@barcode_api_bp.route('/generate', methods=['POST'])
def generate_barcode():
    """
    Auto-generate a barcode for an item
    Uses EAN-13 format: 890 (India) + tenant_id (4 digits) + item_id (5 digits) + check digit
    
    JSON body:
        item_id: Item ID to generate barcode for
        
    Returns:
        JSON with generated barcode
    """
    try:
        data = request.json
        item_id = data.get('item_id')
        
        if not item_id:
            return jsonify({'error': 'Item ID required'}), 400
        
        tenant_id = g.tenant.id if hasattr(g, 'tenant') else None
        if not tenant_id:
            return jsonify({'error': 'Tenant not found'}), 401
        
        # Get item
        item = Item.query.filter_by(id=item_id, tenant_id=tenant_id).first()
        if not item:
            return jsonify({'error': 'Item not found'}), 404
        
        # Generate EAN-13 barcode
        # Format: 890 + tenant_id (4 digits) + item_id (5 digits) + check digit
        base = f"890{tenant_id:04d}{item_id:05d}"
        
        # Calculate EAN-13 check digit
        check_digit = calculate_ean13_check_digit(base)
        barcode = base + str(check_digit)
        
        # Update item
        item.barcode = barcode
        db.session.commit()
        
        logger.info(f"Generated barcode {barcode} for item {item.name}")
        
        return jsonify({
            'success': True,
            'barcode': barcode,
            'item_id': item_id,
            'item_name': item.name
        }), 200
        
    except Exception as e:
        logger.error(f"Error generating barcode: {str(e)}")
        db.session.rollback()
        return jsonify({'error': f'Generation failed: {str(e)}'}), 500


def calculate_ean13_check_digit(barcode_base):
    """
    Calculate EAN-13 check digit
    Algorithm: https://en.wikipedia.org/wiki/International_Article_Number
    
    Args:
        barcode_base: First 12 digits of barcode (string)
        
    Returns:
        Check digit (int)
    """
    if len(barcode_base) != 12:
        raise ValueError("Barcode base must be 12 digits")
    
    # Sum odd position digits (1st, 3rd, 5th, etc.)
    odd_sum = sum(int(barcode_base[i]) for i in range(0, 12, 2))
    
    # Sum even position digits and multiply by 3
    even_sum = sum(int(barcode_base[i]) * 3 for i in range(1, 12, 2))
    
    # Total sum
    total = odd_sum + even_sum
    
    # Check digit is the amount needed to make total a multiple of 10
    check_digit = (10 - (total % 10)) % 10
    
    return check_digit

