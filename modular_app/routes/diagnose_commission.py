"""
Diagnose Commission Status
"""

from flask import Blueprint, jsonify
from models import db
from sqlalchemy import text
from utils.tenant_middleware import require_tenant, get_current_tenant_id

diagnose_commission_bp = Blueprint('diagnose_commission', __name__, url_prefix='/migration')

@diagnose_commission_bp.route('/diagnose-commission')
@require_tenant
def diagnose_commission():
    """Check commission status for returns"""
    tenant_id = get_current_tenant_id()
    
    try:
        # Find Priya's commission for INV-2025-0003
        commissions = db.session.execute(text("""
            SELECT 
                ic.id,
                ic.invoice_id,
                i.invoice_number,
                ic.agent_name,
                ic.invoice_amount,
                ic.commission_percentage,
                ic.commission_amount,
                ic.is_paid,
                ic.paid_date
            FROM invoice_commissions ic
            JOIN invoices i ON ic.invoice_id = i.id
            WHERE i.invoice_number = 'INV-2025-0003'
            AND ic.tenant_id = :tenant_id
        """), {'tenant_id': tenant_id}).fetchall()
        
        # Check returns
        returns = db.session.execute(text("""
            SELECT 
                r.id,
                r.return_number,
                r.invoice_id,
                i.invoice_number,
                r.total_amount,
                r.status
            FROM returns r
            JOIN invoices i ON r.invoice_id = i.id
            WHERE i.invoice_number = 'INV-2025-0003'
            AND r.tenant_id = :tenant_id
        """), {'tenant_id': tenant_id}).fetchall()
        
        # Check commission_reversal entries
        reversals = db.session.execute(text("""
            SELECT 
                at.id,
                at.transaction_type,
                at.credit_amount,
                at.reference_id,
                at.narration
            FROM account_transactions at
            WHERE at.tenant_id = :tenant_id
            AND at.transaction_type = 'commission_reversal'
            AND at.reference_type = 'return'
        """), {'tenant_id': tenant_id}).fetchall()
        
        return jsonify({
            'status': 'success',
            'tenant_id': tenant_id,
            'commissions': [{
                'id': c[0],
                'invoice_id': c[1],
                'invoice_number': c[2],
                'agent_name': c[3],
                'invoice_amount': float(c[4]),
                'commission_percentage': float(c[5]),
                'commission_amount': float(c[6]),
                'is_paid': c[7],
                'paid_date': str(c[8]) if c[8] else None
            } for c in commissions],
            'returns': [{
                'id': r[0],
                'return_number': r[1],
                'invoice_id': r[2],
                'invoice_number': r[3],
                'total_amount': float(r[4]),
                'status': r[5]
            } for r in returns],
            'commission_reversals': [{
                'id': rev[0],
                'type': rev[1],
                'amount': float(rev[2]),
                'return_id': rev[3],
                'narration': rev[4]
            } for rev in reversals]
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

