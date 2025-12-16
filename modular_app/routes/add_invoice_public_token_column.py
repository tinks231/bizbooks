"""
Database Migration: Add public_token column to invoices table
"""
from flask import Blueprint, jsonify, g, session, redirect, url_for, flash
from models.database import db
from sqlalchemy import text
from utils.tenant_middleware import require_tenant, get_current_tenant_id
from functools import wraps

add_invoice_public_token_bp = Blueprint('add_invoice_public_token', __name__, url_prefix='/migration')

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

@add_invoice_public_token_bp.route('/add-invoice-public-token-column', methods=['GET'])
@require_tenant
@login_required
def add_invoice_public_token_column():
    """
    Add public_token column to invoices table
    This is a database schema migration
    """
    try:
        # Check if column already exists
        check_sql = text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='invoices' 
            AND column_name='public_token'
        """)
        
        result = db.session.execute(check_sql).fetchone()
        
        if result:
            return jsonify({
                'status': 'success',
                'message': 'Column public_token already exists in invoices table',
                'already_exists': True
            })
        
        # Add the column
        alter_sql = text("""
            ALTER TABLE invoices 
            ADD COLUMN public_token VARCHAR(64) UNIQUE
        """)
        
        db.session.execute(alter_sql)
        
        # Create index for faster lookups
        index_sql = text("""
            CREATE INDEX IF NOT EXISTS idx_invoices_public_token 
            ON invoices(public_token)
        """)
        
        db.session.execute(index_sql)
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Successfully added public_token column to invoices table',
            'column_added': True,
            'index_created': True
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e),
            'hint': 'If column already exists, this is safe to ignore'
        }), 500

