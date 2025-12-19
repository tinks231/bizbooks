"""
Diagnose Trial Balance in Detail - Show EXACTLY what trial balance report sees
"""

from flask import Blueprint, jsonify, g
from models import db
from sqlalchemy import text
from decimal import Decimal
from utils.tenant_middleware import require_tenant, get_current_tenant_id

diagnose_trial_detail_bp = Blueprint('diagnose_trial_detail', __name__, url_prefix='/diagnose')


@diagnose_trial_detail_bp.route('/trial-balance-detail')
@require_tenant
def diagnose_trial_balance_detail():
    """
    Show EXACTLY what the trial balance report logic sees
    Mimics the exact queries used in accounts.py trial_balance() function
    """
    
    tenant_id = get_current_tenant_id()
    
    try:
        from datetime import datetime
        import pytz
        ist = pytz.timezone('Asia/Kolkata')
        as_of_date = datetime.now(ist).date()
        
        result = {
            'tenant_id': tenant_id,
            'as_of_date': str(as_of_date),
            'components': {}
        }
        
        # 1. Inventory (from item_stocks) - This is what trial balance sees!
        inventory_value = db.session.execute(text("""
            SELECT COALESCE(SUM(ist.stock_value), 0) as total_value
            FROM item_stocks ist
            WHERE ist.tenant_id = :tenant_id
        """), {'tenant_id': tenant_id}).fetchone()[0]
        
        result['components']['inventory'] = {
            'source': 'item_stocks table (DEBIT)',
            'amount': float(inventory_value or 0),
            'query': 'SELECT SUM(stock_value) FROM item_stocks WHERE tenant_id = ?'
        }
        
        # 2. Equity entries (exactly as trial balance reads them!)
        equity_entries = db.session.execute(text("""
            SELECT 
                transaction_type,
                narration,
                SUM(credit_amount - debit_amount) as net_credit
            FROM account_transactions
            WHERE tenant_id = :tenant_id 
            AND account_id IS NULL
            AND transaction_type IN ('opening_balance_equity', 'opening_balance_inventory_equity')
            AND transaction_date <= :as_of_date
            GROUP BY transaction_type, narration
            ORDER BY transaction_type, narration
        """), {'tenant_id': tenant_id, 'as_of_date': as_of_date}).fetchall()
        
        result['components']['equity_entries'] = []
        equity_total = Decimal('0')
        
        for equity in equity_entries:
            transaction_type = equity[0]
            narration = equity[1]
            net_amount = Decimal(str(equity[2]))
            equity_total += net_amount
            
            # Determine label (exactly as trial balance does)
            if 'Inventory' in narration or transaction_type == 'opening_balance_inventory_equity':
                account_label = "Owner's Capital - Inventory Opening"
            elif 'Cash' in narration or 'cash' in narration.lower():
                account_label = "Owner's Capital - Cash Opening"
            elif 'Bank' in narration or any(bank in narration for bank in ['ICICI', 'HDFC', 'SBI', 'Axis']):
                account_label = "Owner's Capital - Bank Opening"
            else:
                account_label = "Owner's Capital - Opening Balance"
            
            result['components']['equity_entries'].append({
                'account_label': account_label,
                'transaction_type': transaction_type,
                'narration': narration,
                'net_credit': float(net_amount),
                'shows_as': 'CREDIT' if net_amount > 0 else 'DEBIT'
            })
        
        result['components']['equity_total'] = {
            'source': 'account_transactions (CREDIT)',
            'amount': float(equity_total),
            'query': 'SELECT SUM(credit_amount - debit_amount) FROM account_transactions WHERE transaction_type IN (opening_balance_equity, opening_balance_inventory_equity)'
        }
        
        # 3. Show what trial balance will calculate
        inventory_debit = Decimal(str(inventory_value or 0))
        equity_credit = equity_total
        
        result['trial_balance_will_show'] = {
            'inventory_debit': float(inventory_debit),
            'equity_credit': float(equity_credit),
            'difference': float(inventory_debit - equity_credit),
            'is_balanced': abs(inventory_debit - equity_credit) < 0.01
        }
        
        # 4. Show ALL inventory-related entries (including wrong types)
        all_inventory_entries = db.session.execute(text("""
            SELECT 
                id,
                transaction_type,
                transaction_date,
                debit_amount,
                credit_amount,
                narration,
                created_at
            FROM account_transactions
            WHERE tenant_id = :tenant_id
            AND (transaction_type LIKE '%inventory%'
                 OR narration LIKE '%Inventory%')
            ORDER BY created_at
        """), {'tenant_id': tenant_id}).fetchall()
        
        result['all_inventory_entries'] = [
            {
                'id': entry[0],
                'transaction_type': entry[1],
                'transaction_date': str(entry[2]),
                'debit_amount': float(entry[3]),
                'credit_amount': float(entry[4]),
                'narration': entry[5],
                'created_at': str(entry[6]),
                'recognized_by_trial_balance': entry[1] in ['opening_balance_equity', 'opening_balance_inventory_equity']
            }
            for entry in all_inventory_entries
        ]
        
        # 5. Diagnosis
        if abs(inventory_debit - equity_credit) < 0.01:
            result['diagnosis'] = '✅ BALANCED! Trial balance should show correct values.'
            result['action_needed'] = 'Just refresh the trial balance page'
        else:
            missing_equity = inventory_debit - equity_credit
            result['diagnosis'] = f'⚠️ MISMATCH: Equity is ₹{abs(float(missing_equity)):,.2f} {"less" if missing_equity > 0 else "more"} than inventory'
            result['action_needed'] = f'Need to {"add" if missing_equity > 0 else "remove"} equity entry for ₹{abs(float(missing_equity)):,.2f} with transaction_type = opening_balance_inventory_equity'
        
        return jsonify({
            'status': 'success',
            'diagnosis': result
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

