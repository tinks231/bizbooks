"""
Diagnose Trial Balance - Show exactly what's being counted
"""

from flask import Blueprint, jsonify
from models import db
from sqlalchemy import text
from decimal import Decimal
from utils.tenant_middleware import require_tenant, get_current_tenant_id

diagnose_trial_bp = Blueprint('diagnose_trial', __name__, url_prefix='/migration')

@diagnose_trial_bp.route('/diagnose-trial-balance')
@require_tenant
def diagnose_trial_balance():
    """Show exactly what the trial balance is counting"""
    tenant_id = get_current_tenant_id()
    
    try:
        result = {
            'tenant_id': tenant_id,
            'components': {}
        }
        
        # 1. Bank & Cash Accounts
        cash_bank = db.session.execute(text("""
            SELECT 
                account_name,
                account_type,
                current_balance
            FROM bank_accounts
            WHERE tenant_id = :tenant_id 
            AND is_active = TRUE
            ORDER BY account_name
        """), {'tenant_id': tenant_id}).fetchall()
        
        result['components']['cash_bank_accounts'] = [
            {
                'name': row[0],
                'type': row[1],
                'balance': float(row[2]),
                'shows_as': 'DEBIT' if row[2] >= 0 else 'CREDIT',
                'amount': abs(float(row[2]))
            }
            for row in cash_bank
        ]
        
        # 2. Sales Returns
        sales_returns = db.session.execute(text("""
            SELECT COALESCE(SUM(debit_amount), 0)
            FROM account_transactions
            WHERE tenant_id = :tenant_id
            AND transaction_type = 'sales_return'
        """), {'tenant_id': tenant_id}).fetchone()[0]
        
        result['components']['sales_returns'] = {
            'amount': float(sales_returns or 0),
            'shows_as': 'DEBIT'
        }
        
        # 3. GST Receivable (Returns)
        gst_cgst = db.session.execute(text("""
            SELECT COALESCE(SUM(debit_amount), 0)
            FROM account_transactions
            WHERE tenant_id = :tenant_id
            AND transaction_type = 'gst_return_cgst'
        """), {'tenant_id': tenant_id}).fetchone()[0]
        
        gst_sgst = db.session.execute(text("""
            SELECT COALESCE(SUM(debit_amount), 0)
            FROM account_transactions
            WHERE tenant_id = :tenant_id
            AND transaction_type = 'gst_return_sgst'
        """), {'tenant_id': tenant_id}).fetchone()[0]
        
        gst_igst = db.session.execute(text("""
            SELECT COALESCE(SUM(debit_amount), 0)
            FROM account_transactions
            WHERE tenant_id = :tenant_id
            AND transaction_type = 'gst_return_igst'
        """), {'tenant_id': tenant_id}).fetchone()[0]
        
        gst_total = float(gst_cgst or 0) + float(gst_sgst or 0) + float(gst_igst or 0)
        
        result['components']['gst_receivable_returns'] = {
            'cgst': float(gst_cgst or 0),
            'sgst': float(gst_sgst or 0),
            'igst': float(gst_igst or 0),
            'total': gst_total,
            'shows_as': 'DEBIT'
        }
        
        # 4. Refund Payment entries (these should NOT appear in Trial Balance separately)
        refund_payments = db.session.execute(text("""
            SELECT 
                account_id,
                SUM(credit_amount) as total_credits
            FROM account_transactions
            WHERE tenant_id = :tenant_id
            AND transaction_type = 'refund_payment'
            GROUP BY account_id
        """), {'tenant_id': tenant_id}).fetchall()
        
        result['components']['refund_payment_entries'] = [
            {
                'account_id': row[0],
                'total_credits': float(row[1]),
                'note': 'These should already be reflected in bank_accounts.current_balance'
            }
            for row in refund_payments
        ]
        
        # 5. Calculate what Trial Balance SHOULD show
        total_debits = sum(acc['amount'] for acc in result['components']['cash_bank_accounts'] if acc['shows_as'] == 'DEBIT')
        total_debits += result['components']['sales_returns']['amount']
        total_debits += result['components']['gst_receivable_returns']['total']
        
        result['expected_trial_balance'] = {
            'note': 'This is simplified - just showing the return-related accounts',
            'total_debits_from_returns_components': total_debits
        }
        
        return jsonify(result)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

