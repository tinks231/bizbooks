"""
Diagnose remaining ₹1,800 imbalance
Show exactly what's causing the remaining difference
"""

from flask import Blueprint, jsonify, g
from models import db
from sqlalchemy import text
from decimal import Decimal
from utils.tenant_middleware import require_tenant, get_current_tenant_id

diagnose_remaining_bp = Blueprint('diagnose_remaining', __name__, url_prefix='/diagnose')

@diagnose_remaining_bp.route('/remaining-imbalance')
@require_tenant
def diagnose_remaining_imbalance():
    """
    Show all equity entries and identify what's causing remaining imbalance
    """
    
    try:
        tenant_id = get_current_tenant_id()
        
        from datetime import datetime
        import pytz
        ist = pytz.timezone('Asia/Kolkata')
        as_of_date = datetime.now(ist).date()
        
        result = {
            'tenant_id': tenant_id,
            'components': {}
        }
        
        # 1. All equity entries
        all_equity = db.session.execute(text("""
            SELECT 
                id,
                transaction_type,
                transaction_date,
                narration,
                debit_amount,
                credit_amount,
                created_at
            FROM account_transactions
            WHERE tenant_id = :tenant_id
            AND account_id IS NULL
            AND transaction_date <= :as_of_date
            ORDER BY transaction_type, created_at
        """), {'tenant_id': tenant_id, 'as_of_date': as_of_date}).fetchall()
        
        result['all_equity_entries'] = []
        equity_debit_total = Decimal('0')
        equity_credit_total = Decimal('0')
        
        for entry in all_equity:
            debit = Decimal(str(entry[4]))
            credit = Decimal(str(entry[5]))
            equity_debit_total += debit
            equity_credit_total += credit
            
            result['all_equity_entries'].append({
                'id': entry[0],
                'transaction_type': entry[1],
                'transaction_date': str(entry[2]),
                'narration': entry[3],
                'debit_amount': float(debit),
                'credit_amount': float(credit),
                'net': float(credit - debit),
                'created_at': str(entry[6]),
                'recognized_by_trial_balance': entry[1] in ['opening_balance_equity', 'opening_balance_inventory_equity']
            })
        
        result['equity_totals'] = {
            'total_debit': float(equity_debit_total),
            'total_credit': float(equity_credit_total),
            'net_credit': float(equity_credit_total - equity_debit_total)
        }
        
        # 2. Inventory
        inventory = db.session.execute(text("""
            SELECT COALESCE(SUM(stock_value), 0)
            FROM item_stocks
            WHERE tenant_id = :tenant_id
        """), {'tenant_id': tenant_id}).fetchone()[0]
        
        result['inventory_value'] = float(inventory)
        
        # 3. Bank/Cash balances
        bank_accounts = db.session.execute(text("""
            SELECT 
                account_name,
                opening_balance,
                current_balance,
                account_type
            FROM bank_accounts
            WHERE tenant_id = :tenant_id
            AND is_active = TRUE
        """), {'tenant_id': tenant_id}).fetchall()
        
        result['bank_cash_accounts'] = [
            {
                'name': acc[0],
                'opening_balance': float(acc[1]),
                'current_balance': float(acc[2]),
                'type': acc[3],
                'operations': float(acc[2]) - float(acc[1])
            }
            for acc in bank_accounts
        ]
        
        total_cash_bank_opening = sum(acc[1] for acc in bank_accounts)
        total_cash_bank_current = sum(acc[2] for acc in bank_accounts)
        
        # 4. Calculate what SHOULD be in equity
        required_equity = Decimal(str(inventory)) + Decimal(str(total_cash_bank_opening))
        actual_equity = equity_credit_total - equity_debit_total
        difference = actual_equity - required_equity
        
        result['analysis'] = {
            'required_equity': {
                'inventory': float(inventory),
                'cash_bank_opening': float(total_cash_bank_opening),
                'total': float(required_equity)
            },
            'actual_equity': float(actual_equity),
            'difference': float(difference),
            'problem': 'Equity has EXTRA' if difference > 0 else 'Equity is SHORT' if difference < 0 else 'Perfect match!'
        }
        
        # 5. Identify suspicious entries
        suspicious = []
        for entry in all_equity:
            # Tiny amounts (< ₹10)
            if abs(entry[4]) < 10 and abs(entry[5]) < 10 and (entry[4] > 0 or entry[5] > 0):
                suspicious.append({
                    'id': entry[0],
                    'reason': 'Tiny amount - possible rounding error',
                    'narration': entry[3],
                    'amount': float(entry[5] - entry[4])
                })
            
            # Entries not recognized by trial balance
            if entry[1] not in ['opening_balance_equity', 'opening_balance_inventory_equity']:
                suspicious.append({
                    'id': entry[0],
                    'reason': 'Transaction type not recognized by trial balance',
                    'type': entry[1],
                    'narration': entry[3],
                    'amount': float(entry[5] - entry[4])
                })
        
        result['suspicious_entries'] = suspicious
        
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

