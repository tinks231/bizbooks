"""
Diagnose Commission Balance Issues
"""

from flask import Blueprint, jsonify, g
from models import db
from sqlalchemy import text
from decimal import Decimal
from utils.tenant_middleware import require_tenant, get_current_tenant_id

diagnose_commission_balance_bp = Blueprint('diagnose_commission_balance', __name__, url_prefix='/migration')

@diagnose_commission_balance_bp.route('/diagnose-commission-balance')
@require_tenant
def diagnose_commission_balance():
    """Diagnose why commission expense is not showing in Trial Balance"""
    tenant_id = get_current_tenant_id()
    
    try:
        print("\n" + "="*80)
        print("🔍 DIAGNOSING COMMISSION BALANCE ISSUE")
        print("="*80 + "\n")
        
        # 1. Commission Expense DEBITS
        commission_expense = db.session.execute(text("""
            SELECT COALESCE(SUM(debit_amount), 0)
            FROM account_transactions
            WHERE tenant_id = :tenant_id
            AND transaction_type = 'commission_expense'
        """), {'tenant_id': tenant_id}).fetchone()[0]
        
        commission_expense_decimal = Decimal(str(commission_expense or 0))
        print(f"1️⃣ Commission Expense DEBITS: ₹{commission_expense_decimal}")
        
        # 2. Commission Reversal CREDITS
        commission_reversal = db.session.execute(text("""
            SELECT COALESCE(SUM(credit_amount), 0)
            FROM account_transactions
            WHERE tenant_id = :tenant_id
            AND transaction_type = 'commission_reversal'
        """), {'tenant_id': tenant_id}).fetchone()[0]
        
        commission_reversal_decimal = Decimal(str(commission_reversal or 0))
        print(f"2️⃣ Commission Reversal CREDITS: ₹{commission_reversal_decimal}")
        
        # 3. Commission Recoverable DEBITS
        commission_recoverable = db.session.execute(text("""
            SELECT COALESCE(SUM(debit_amount), 0)
            FROM account_transactions
            WHERE tenant_id = :tenant_id
            AND transaction_type = 'commission_recoverable'
        """), {'tenant_id': tenant_id}).fetchone()[0]
        
        commission_recoverable_decimal = Decimal(str(commission_recoverable or 0))
        print(f"3️⃣ Commission Recoverable DEBITS: ₹{commission_recoverable_decimal}")
        
        # 4. Calculate Net
        net_commission = commission_expense_decimal - commission_reversal_decimal
        print(f"\n📊 Net Commission Expense: ₹{net_commission}")
        print(f"   Formula: ₹{commission_expense_decimal} - ₹{commission_reversal_decimal} = ₹{net_commission}")
        
        # 5. Check if it would show in Trial Balance
        print(f"\n🔍 Trial Balance Check:")
        if net_commission > 0:
            print(f"   ✅ SHOULD SHOW as Commission Expenses: ₹{net_commission}")
        elif net_commission == 0:
            print(f"   ⚠️  Net is ZERO - Will NOT show in Trial Balance")
        else:
            print(f"   ❌ Net is NEGATIVE (₹{net_commission}) - Will NOT show in Trial Balance")
        
        # 6. Show individual entries
        print(f"\n📋 Individual Commission Entries:\n")
        
        entries = db.session.execute(text("""
            SELECT 
                id,
                transaction_type,
                debit_amount,
                credit_amount,
                transaction_date,
                voucher_number,
                narration
            FROM account_transactions
            WHERE tenant_id = :tenant_id
            AND transaction_type IN ('commission_expense', 'commission_reversal', 'commission_recoverable')
            ORDER BY transaction_date, id
        """), {'tenant_id': tenant_id}).fetchall()
        
        entries_list = []
        for entry in entries:
            entry_dict = {
                'id': entry[0],
                'type': entry[1],
                'debit': float(entry[2]),
                'credit': float(entry[3]),
                'date': str(entry[4]),
                'voucher': entry[5],
                'narration': entry[6]
            }
            entries_list.append(entry_dict)
            
            print(f"   [{entry[0]}] {entry[1]:<30} DEBIT: ₹{entry[2]:<10.2f} CREDIT: ₹{entry[3]:<10.2f} | {entry[5]}")
        
        # 7. Trial Balance Imbalance Check
        print(f"\n🧮 EXPECTED TRIAL BALANCE IMPACT:")
        print(f"   ASSETS (Debits):")
        print(f"      + Commission Recoverable: ₹{commission_recoverable_decimal}")
        print(f"   EXPENSES (Debits):")
        print(f"      + Commission Expenses: ₹{net_commission if net_commission > 0 else 0}")
        print(f"   ")
        print(f"   Total Added Debits: ₹{commission_recoverable_decimal + (net_commission if net_commission > 0 else Decimal('0'))}")
        print(f"   Total Added Credits: ₹0")
        print(f"   ")
        print(f"   ⚠️  THIS CREATES IMBALANCE OF: ₹{commission_recoverable_decimal + (net_commission if net_commission > 0 else Decimal('0'))}")
        
        print("\n" + "="*80)
        
        return jsonify({
            'status': 'success',
            'commission_expense_debits': float(commission_expense_decimal),
            'commission_reversal_credits': float(commission_reversal_decimal),
            'commission_recoverable_debits': float(commission_recoverable_decimal),
            'net_commission_expense': float(net_commission),
            'will_show_in_trial_balance': net_commission > 0,
            'expected_imbalance': float(commission_recoverable_decimal + (net_commission if net_commission > 0 else Decimal('0'))),
            'entries': entries_list
        })
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}\n")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

