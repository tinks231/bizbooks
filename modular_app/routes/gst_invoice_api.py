"""
GST Smart Invoice API Endpoints
================================
API routes for GST-aware stock information and invoice validation

Endpoints:
- GET /api/gst-invoice/item/<item_id>/stock-info - Get stock breakdown (GST vs Non-GST)
- POST /api/gst-invoice/validate-item - Validate if item can be added to invoice
- POST /api/gst-invoice/batch-validate - Validate multiple items at once
"""

from flask import Blueprint, request, jsonify, g, session
from models import db, Item, Customer
from services.stock_batch_service import StockBatchService
from utils.tenant_middleware import get_current_tenant_id
from decimal import Decimal
import logging

gst_invoice_api_bp = Blueprint('gst_invoice_api', __name__, url_prefix='/api/gst-invoice')
logger = logging.getLogger(__name__)


@gst_invoice_api_bp.route('/item/<int:item_id>/stock-info', methods=['GET'])
def get_item_stock_info(item_id):
    """
    Get stock information for an item with GST breakdown
    
    Returns:
        JSON with gst_stock, non_gst_stock, total_stock, and item details
    """
    try:
        # Get tenant
        tenant_id = get_current_tenant_id()
        if not tenant_id:
            return jsonify({'error': 'Tenant not found'}), 401
        
        # Get item
        item = Item.query.filter_by(id=item_id, tenant_id=tenant_id).first()
        if not item:
            return jsonify({'error': 'Item not found'}), 404
        
        # Get stock breakdown from batch service
        stock_info = StockBatchService.get_available_stock(item_id, tenant_id)
        
        return jsonify({
            'success': True,
            'item_id': item_id,
            'item_name': item.name,
            'item_sku': item.sku,
            'gst_stock': float(stock_info['gst_stock']),
            'non_gst_stock': float(stock_info['non_gst_stock']),
            'total_stock': float(stock_info['total_stock']),
            'has_gst_stock': stock_info['gst_stock'] > 0,
            'has_non_gst_stock': stock_info['non_gst_stock'] > 0,
            'batches_count': len(stock_info['batches'])
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching stock info for item {item_id}: {str(e)}")
        return jsonify({
            'error': 'Failed to fetch stock info',
            'message': str(e)
        }), 500


@gst_invoice_api_bp.route('/validate-item', methods=['POST'])
def validate_invoice_item():
    """
    Validate if an item can be added to an invoice
    
    Request body:
        {
            "item_id": 123,
            "quantity": 10,
            "invoice_type": "taxable",  // or "non_taxable" or "credit_adjustment"
            "customer_id": 456  // optional
        }
    
    Returns:
        JSON with validation result and suggestions if blocked
    """
    try:
        # Get tenant
        tenant_id = get_current_tenant_id()
        if not tenant_id:
            return jsonify({'error': 'Tenant not found'}), 401
        
        # Get request data
        data = request.json
        item_id = data.get('item_id')
        quantity = float(data.get('quantity', 0))
        invoice_type = data.get('invoice_type', 'taxable')
        customer_id = data.get('customer_id')
        
        if not item_id or quantity <= 0:
            return jsonify({
                'status': 'error',
                'message': 'Invalid item_id or quantity'
            }), 400
        
        # Get item
        item = Item.query.filter_by(id=item_id, tenant_id=tenant_id).first()
        if not item:
            return jsonify({
                'status': 'error',
                'message': 'Item not found'
            }), 404
        
        # Get customer if provided
        customer = None
        if customer_id:
            customer = Customer.query.filter_by(id=customer_id, tenant_id=tenant_id).first()
        
        # Validate using batch service
        validation_result = StockBatchService.validate_invoice_item(
            item_id=item_id,
            quantity=quantity,
            invoice_type=invoice_type,
            customer=customer,
            tenant_id=tenant_id
        )
        
        # Add item details to response
        validation_result['item_name'] = item.name
        validation_result['item_sku'] = item.sku
        
        if validation_result['status'] == 'ok':
            return jsonify(validation_result), 200
        else:
            return jsonify(validation_result), 422  # Unprocessable Entity
        
    except Exception as e:
        logger.error(f"Error validating invoice item: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Validation failed',
            'details': str(e)
        }), 500


@gst_invoice_api_bp.route('/batch-validate', methods=['POST'])
def batch_validate_items():
    """
    Validate multiple items at once for an invoice
    
    Request body:
        {
            "invoice_type": "taxable",
            "customer_id": 456,  // optional
            "items": [
                {"item_id": 123, "quantity": 10},
                {"item_id": 124, "quantity": 5}
            ]
        }
    
    Returns:
        JSON array with validation result for each item
    """
    try:
        # Get tenant
        tenant_id = get_current_tenant_id()
        if not tenant_id:
            return jsonify({'error': 'Tenant not found'}), 401
        
        # Get request data
        data = request.json
        invoice_type = data.get('invoice_type', 'taxable')
        customer_id = data.get('customer_id')
        items = data.get('items', [])
        
        if not items:
            return jsonify({
                'status': 'error',
                'message': 'No items provided'
            }), 400
        
        # Get customer if provided
        customer = None
        if customer_id:
            customer = Customer.query.filter_by(id=customer_id, tenant_id=tenant_id).first()
        
        # Validate each item
        results = []
        all_valid = True
        
        for item_data in items:
            item_id = item_data.get('item_id')
            quantity = float(item_data.get('quantity', 0))
            
            if not item_id or quantity <= 0:
                results.append({
                    'item_id': item_id,
                    'status': 'error',
                    'message': 'Invalid item_id or quantity'
                })
                all_valid = False
                continue
            
            # Get item
            item = Item.query.filter_by(id=item_id, tenant_id=tenant_id).first()
            if not item:
                results.append({
                    'item_id': item_id,
                    'status': 'error',
                    'message': 'Item not found'
                })
                all_valid = False
                continue
            
            # Validate
            validation_result = StockBatchService.validate_invoice_item(
                item_id=item_id,
                quantity=quantity,
                invoice_type=invoice_type,
                customer=customer,
                tenant_id=tenant_id
            )
            
            # Add item details
            validation_result['item_id'] = item_id
            validation_result['item_name'] = item.name
            validation_result['quantity_requested'] = quantity
            
            results.append(validation_result)
            
            if validation_result['status'] != 'ok':
                all_valid = False
        
        return jsonify({
            'all_valid': all_valid,
            'invoice_type': invoice_type,
            'items_validated': len(results),
            'results': results
        }), 200
        
    except Exception as e:
        logger.error(f"Error batch validating items: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Batch validation failed',
            'details': str(e)
        }), 500


@gst_invoice_api_bp.route('/item/<int:item_id>/batches', methods=['GET'])
def get_item_batches(item_id):
    """
    Get detailed batch information for an item
    
    Returns:
        JSON with list of active batches for the item
    """
    try:
        # Get tenant
        tenant_id = get_current_tenant_id()
        if not tenant_id:
            return jsonify({'error': 'Tenant not found'}), 401
        
        # Get item
        item = Item.query.filter_by(id=item_id, tenant_id=tenant_id).first()
        if not item:
            return jsonify({'error': 'Item not found'}), 404
        
        # Get stock summary
        summary = StockBatchService.get_stock_summary_for_product(item_id, tenant_id)
        
        # Format batch details
        batches = []
        for batch in summary['batches']:
            if batch.batch_status == 'active' and batch.quantity_remaining > 0:
                batches.append({
                    'batch_id': batch.id,
                    'purchase_date': batch.purchase_date.isoformat() if batch.purchase_date else None,
                    'purchase_bill_number': batch.purchase_bill_number,
                    'vendor_name': batch.vendor_name,
                    'quantity_remaining': float(batch.quantity_remaining),
                    'purchased_with_gst': batch.purchased_with_gst,
                    'base_cost_per_unit': float(batch.base_cost_per_unit),
                    'gst_rate': float(batch.gst_rate) if batch.gst_rate else 0,
                    'itc_remaining': float(batch.itc_remaining) if batch.purchased_with_gst else 0
                })
        
        return jsonify({
            'success': True,
            'item_id': item_id,
            'item_name': item.name,
            'total_stock': summary['total_stock'],
            'gst_stock': summary['gst_stock'],
            'non_gst_stock': summary['non_gst_stock'],
            'active_batches': len(batches),
            'batches': batches
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching batches for item {item_id}: {str(e)}")
        return jsonify({
            'error': 'Failed to fetch batch information',
            'message': str(e)
        }), 500

