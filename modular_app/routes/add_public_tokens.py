"""
Migration: Add public_token to existing invoices
"""
from flask import Blueprint, jsonify, g
from models.database import db
from models.invoice import Invoice
from decorators import require_tenant, login_required

add_public_tokens_bp = Blueprint('add_public_tokens', __name__, url_prefix='/migration')

@add_public_tokens_bp.route('/add-public-tokens', methods=['GET'])
@require_tenant
@login_required
def add_public_tokens():
    """Add public_token to all existing invoices that don't have one"""
    try:
        tenant_id = g.tenant.id
        
        # Find invoices without public_token
        invoices = Invoice.query.filter_by(
            tenant_id=tenant_id
        ).filter(
            (Invoice.public_token == None) | (Invoice.public_token == '')
        ).all()
        
        count = 0
        for invoice in invoices:
            invoice.public_token = invoice.generate_public_token()
            count += 1
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': f'Added public tokens to {count} invoices',
            'invoices_updated': count
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

