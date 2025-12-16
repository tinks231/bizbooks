"""
Migration: Add public_token to existing invoices
"""
from flask import Blueprint, jsonify, g, session, redirect, url_for, flash
from models.database import db
from models.invoice import Invoice
from utils.tenant_middleware import require_tenant, get_current_tenant_id
from functools import wraps

add_public_tokens_bp = Blueprint('add_public_tokens', __name__, url_prefix='/migration')

def login_required(f):
    """Decorator to require admin login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'tenant_admin_id' not in session:
            flash('Please login first', 'error')
            return redirect(url_for('admin.login'))
        # Verify session tenant matches current tenant
        if session.get('tenant_admin_id') != get_current_tenant_id():
            session.clear()
            flash('Session mismatch. Please login again.', 'error')
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function

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

