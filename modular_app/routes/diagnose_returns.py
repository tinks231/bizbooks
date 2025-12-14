"""
Diagnose Returns - Check what returns exist and their accounting status
"""

from flask import Blueprint, jsonify
from models import db
from sqlalchemy import text
from utils.tenant_middleware import require_tenant, get_current_tenant_id

diagnose_returns_bp = Blueprint('diagnose_returns', __name__, url_prefix='/migration')

@diagnose_returns_bp.route('/diagnose-returns')
@require_tenant
def diagnose_returns():
    """Show all returns and their accounting entries"""
    tenant_id = get_current_tenant_id()
    
    try:
        # Get all returns
        returns = db.session.execute(text("""
            SELECT 
                id,
                return_number,
                status,
                refund_method,
                payment_account_id,
                total_amount,
                customer_name,
                created_at,
                approved_at
            FROM returns
            WHERE tenant_id = :tenant_id
            ORDER BY created_at DESC
        """), {'tenant_id': tenant_id}).fetchall()
        
        if not returns:
            return jsonify({
                'status': 'info',
                'message': 'No returns found for this tenant',
                'returns': []
            })
        
        results = []
        
        for ret in returns:
            return_id = ret[0]
            
            # Check accounting entries for this return
            accounting_entries = db.session.execute(text("""
                SELECT 
                    transaction_type,
                    debit_amount,
                    credit_amount,
                    account_id,
                    created_at
                FROM account_transactions
                WHERE tenant_id = :tenant_id
                AND reference_type = 'return'
                AND reference_id = :return_id
                ORDER BY transaction_type
            """), {'tenant_id': tenant_id, 'return_id': return_id}).fetchall()
            
            entries = []
            for entry in accounting_entries:
                entries.append({
                    'type': entry[0],
                    'debit': float(entry[1]),
                    'credit': float(entry[2]),
                    'account_id': entry[3]
                })
            
            # Calculate totals
            total_debits = sum(e['debit'] for e in entries)
            total_credits = sum(e['credit'] for e in entries)
            is_balanced = abs(total_debits - total_credits) < 0.01
            
            # Check what's missing
            missing = []
            has_sales_return = any(e['type'] == 'sales_return' for e in entries)
            has_gst_return = any(e['type'] in ['gst_return_cgst', 'gst_return_sgst', 'gst_return_igst'] for e in entries)
            has_refund_payment = any(e['type'] == 'refund_payment' for e in entries)
            
            if not has_sales_return:
                missing.append('sales_return')
            if not has_gst_return:
                missing.append('gst_return')
            if not has_refund_payment and ret[3] in ['cash', 'bank']:
                missing.append('refund_payment')
            
            results.append({
                'id': return_id,
                'return_number': ret[1],
                'status': ret[2],
                'refund_method': ret[3],
                'payment_account_id': ret[4],
                'total_amount': float(ret[5]),
                'customer_name': ret[6],
                'created_at': str(ret[7]),
                'approved_at': str(ret[8]) if ret[8] else None,
                'accounting': {
                    'entries': entries,
                    'total_debits': total_debits,
                    'total_credits': total_credits,
                    'is_balanced': is_balanced,
                    'difference': abs(total_debits - total_credits),
                    'missing': missing
                }
            })
        
        return jsonify({
            'status': 'success',
            'tenant_id': tenant_id,
            'returns_count': len(returns),
            'returns': results
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

