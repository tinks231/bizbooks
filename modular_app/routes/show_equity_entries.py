"""
Show all equity entries with their exact narrations
"""

from flask import Blueprint, jsonify, g
from models import db
from sqlalchemy import text
from utils.tenant_middleware import require_tenant, get_current_tenant_id

show_equity_entries_bp = Blueprint('show_equity_entries', __name__, url_prefix='/debug')

@show_equity_entries_bp.route('/equity-entries')
@require_tenant
def show_equity_entries():
    """Show all equity entries with exact details"""
    
    try:
        tenant_id = get_current_tenant_id()
        
        entries = db.session.execute(text("""
            SELECT 
                id,
                transaction_type,
                transaction_date,
                narration,
                debit_amount,
                credit_amount,
                voucher_number,
                created_at
            FROM account_transactions
            WHERE tenant_id = :tenant_id
            AND transaction_type IN ('opening_balance_equity', 'opening_balance_inventory_equity')
            ORDER BY created_at
        """), {'tenant_id': tenant_id}).fetchall()
        
        result = []
        for entry in entries:
            result.append({
                'id': entry[0],
                'transaction_type': entry[1],
                'transaction_date': str(entry[2]),
                'narration': entry[3],
                'debit_amount': float(entry[4]),
                'credit_amount': float(entry[5]),
                'voucher_number': entry[6],
                'created_at': str(entry[7]),
                'label_shown_in_trial_balance': get_trial_balance_label(entry[1], entry[3])
            })
        
        return jsonify({
            'status': 'success',
            'tenant_id': tenant_id,
            'total_entries': len(result),
            'entries': result
        })
        
    except Exception as e:
        import traceback
        return jsonify({
            'status': 'error',
            'message': str(e),
            'traceback': traceback.format_exc()
        }), 500

def get_trial_balance_label(transaction_type, narration):
    """
    Determine what label the trial balance will show
    This mimics the logic in accounts.py trial_balance()
    """
    if 'Inventory' in narration or transaction_type == 'opening_balance_inventory_equity':
        return "Owner's Capital - Inventory Opening"
    elif 'Cash' in narration or 'cash' in narration.lower():
        return "Owner's Capital - Cash Opening"
    elif 'Bank' in narration or any(bank in narration for bank in ['ICICI', 'HDFC', 'SBI', 'Axis']):
        return "Owner's Capital - Bank Opening"
    else:
        return "Owner's Capital - Opening Balance"

