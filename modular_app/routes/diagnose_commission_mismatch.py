"""
Diagnose Commission Mismatch
Check why commission amounts don't match expected calculations
"""

from flask import Blueprint, jsonify
from models import db, Invoice, InvoiceCommission
from sqlalchemy import text
from decimal import Decimal
from utils.tenant_middleware import require_tenant, get_current_tenant_id
from utils.accounting_helpers import calculate_commission

diagnose_commission_mismatch_bp = Blueprint('diagnose_commission_mismatch', __name__, url_prefix='/migration')

@diagnose_commission_mismatch_bp.route('/diagnose-commission-mismatch')
@require_tenant
def diagnose_commission_mismatch():
    """Check all invoice commissions and compare stored vs calculated amounts"""
    tenant_id = get_current_tenant_id()
    
    try:
        # Get all invoice commissions
        commissions = InvoiceCommission.query.filter_by(tenant_id=tenant_id).all()
        
        results = []
        mismatches = []
        
        for comm in commissions:
            # Get the invoice
            invoice = Invoice.query.get(comm.invoice_id)
            
            # Calculate what commission SHOULD be
            expected_commission = calculate_commission(
                invoice.total_amount,
                Decimal(str(comm.commission_percentage)),
                round_to_whole=True
            )
            
            # Compare
            stored = Decimal(str(comm.commission_amount))
            expected = Decimal(str(expected_commission))
            difference = stored - expected
            
            result = {
                'invoice_number': invoice.invoice_number,
                'invoice_total': float(invoice.total_amount),
                'commission_percentage': comm.commission_percentage,
                'stored_commission': float(stored),
                'expected_commission': float(expected),
                'difference': float(difference),
                'is_mismatch': (difference != 0),
                'is_paid': comm.is_paid,
                'agent_name': comm.agent_name
            }
            
            results.append(result)
            
            if difference != 0:
                mismatches.append(result)
        
        return jsonify({
            'status': 'success',
            'total_commissions': len(results),
            'mismatches_found': len(mismatches),
            'all_commissions': results,
            'mismatches_only': mismatches
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

