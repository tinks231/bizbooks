"""
Diagnose All Round-off Entries
Check all transactions with round_off_expense to find imbalances
"""

from flask import Blueprint, jsonify
from models import db
from sqlalchemy import text
from decimal import Decimal
from utils.tenant_middleware import require_tenant, get_current_tenant_id

diagnose_all_round_offs_bp = Blueprint('diagnose_all_round_offs', __name__, url_prefix='/migration')

@diagnose_all_round_offs_bp.route('/diagnose-all-round-offs')
@require_tenant
def diagnose_all_round_offs():
    """Check all round-off entries across all transactions"""
    tenant_id = get_current_tenant_id()
    
    try:
        # Get ALL round-off entries
        round_off_entries = db.session.execute(text("""
            SELECT 
                id,
                transaction_date,
                transaction_type,
                debit_amount,
                credit_amount,
                reference_type,
                reference_id,
                voucher_number,
                narration
            FROM account_transactions
            WHERE tenant_id = :tenant_id
            AND transaction_type = 'round_off_expense'
            ORDER BY transaction_date, id
        """), {'tenant_id': tenant_id}).fetchall()
        
        entries = []
        total_debits = Decimal('0')
        total_credits = Decimal('0')
        
        for entry in round_off_entries:
            debit = Decimal(str(entry[3]))
            credit = Decimal(str(entry[4]))
            
            entries.append({
                'id': entry[0],
                'date': str(entry[1]),
                'type': entry[2],
                'debit': float(debit),
                'credit': float(credit),
                'reference_type': entry[5],
                'reference_id': entry[6],
                'voucher': entry[7],
                'narration': entry[8],
                'net': float(debit - credit)
            })
            
            total_debits += debit
            total_credits += credit
        
        net_round_off = total_debits - total_credits
        
        # Also check for any unbalanced returns
        unbalanced_returns = db.session.execute(text("""
            SELECT 
                r.id,
                r.return_number,
                r.total_amount,
                r.taxable_amount,
                r.cgst_amount,
                r.sgst_amount,
                r.igst_amount,
                (r.taxable_amount + COALESCE(r.cgst_amount, 0) + COALESCE(r.sgst_amount, 0) + COALESCE(r.igst_amount, 0)) as calculated_total,
                (r.total_amount - (r.taxable_amount + COALESCE(r.cgst_amount, 0) + COALESCE(r.sgst_amount, 0) + COALESCE(r.igst_amount, 0))) as round_off_diff
            FROM returns r
            WHERE r.tenant_id = :tenant_id
            AND r.status = 'approved'
        """), {'tenant_id': tenant_id}).fetchall()
        
        returns_data = []
        for ret in unbalanced_returns:
            returns_data.append({
                'return_id': ret[0],
                'return_number': ret[1],
                'total_amount': float(ret[2]),
                'calculated_total': float(ret[7]),
                'round_off_needed': float(ret[8]),
                'has_issue': abs(float(ret[8])) > 0.001
            })
        
        # Get complete trial balance for round-off
        trial_balance_round_off = db.session.execute(text("""
            SELECT 
                SUM(debit_amount) as total_debit,
                SUM(credit_amount) as total_credit
            FROM account_transactions
            WHERE tenant_id = :tenant_id
            AND transaction_type = 'round_off_expense'
        """), {'tenant_id': tenant_id}).fetchone()
        
        return jsonify({
            'status': 'success',
            'round_off_entries': entries,
            'summary': {
                'total_entries': len(entries),
                'total_debits': float(total_debits),
                'total_credits': float(total_credits),
                'net_balance': float(net_round_off),
                'should_show_in_trial_balance': float(net_round_off)
            },
            'returns_analysis': returns_data,
            'trial_balance_check': {
                'total_debit': float(trial_balance_round_off[0] or 0),
                'total_credit': float(trial_balance_round_off[1] or 0),
                'net': float((trial_balance_round_off[0] or 0) - (trial_balance_round_off[1] or 0))
            }
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

