"""
Fix inventory equity mismatch
When new items are imported after initial equity entry, need to adjust equity
"""

from flask import Blueprint, jsonify, g
from models import db
from sqlalchemy import text
from decimal import Decimal
from datetime import datetime
import pytz

fix_inventory_equity_mismatch_bp = Blueprint('fix_inventory_equity_mismatch', __name__, url_prefix='/migration')


@fix_inventory_equity_mismatch_bp.route('/fix-inventory-equity-mismatch')
def fix_inventory_equity_mismatch():
    """
    Fix mismatch between current stock value and equity entries
    
    Problem:
    - Initial import created equity entry for X amount
    - More items imported later, stock value now Y
    - Equity entry still shows X (outdated!)
    - Need to create adjustment entry for difference
    
    Solution:
    - Calculate current total stock value
    - Find existing equity entries
    - Create adjustment entry for the difference
    """
    
    try:
        # Get current tenant from subdomain
        tenant_id = g.get('tenant_id')
        
        if not tenant_id:
            return jsonify({
                'error': 'No tenant found. Make sure you\'re accessing via subdomain'
            }), 400
        
        ist = pytz.timezone('Asia/Kolkata')
        now = datetime.now(ist)
        
        print(f"\n{'=' * 80}")
        print(f"🔧 FIXING INVENTORY EQUITY MISMATCH FOR TENANT: {tenant_id}")
        print(f"{'=' * 80}")
        
        # 1. Get current stock value
        current_stock_value = db.session.execute(text("""
            SELECT COALESCE(SUM(stock_value), 0)
            FROM item_stocks
            WHERE tenant_id = :tenant_id
        """), {'tenant_id': tenant_id}).fetchone()[0]
        
        current_value = Decimal(str(current_stock_value))
        print(f"\n📦 Current Stock Value: ₹{current_value:,.2f}")
        
        # 2. Get existing equity entries
        existing_equity = db.session.execute(text("""
            SELECT COALESCE(SUM(credit_amount), 0)
            FROM account_transactions
            WHERE tenant_id = :tenant_id
            AND (transaction_type = 'opening_balance_inventory_equity'
                 OR transaction_type = 'inventory_equity_adjustment')
        """), {'tenant_id': tenant_id}).fetchone()[0]
        
        existing_value = Decimal(str(existing_equity))
        print(f"🏦 Existing Equity Entries: ₹{existing_value:,.2f}")
        
        # 3. Calculate difference
        difference = current_value - existing_value
        print(f"📊 Difference: ₹{difference:,.2f}")
        
        if abs(difference) < 0.01:
            print(f"\n✅ Stock value and equity already match! No fix needed.")
            return jsonify({
                'status': 'success',
                'message': 'No fix needed - equity already matches stock value',
                'current_stock_value': float(current_value),
                'existing_equity': float(existing_value),
                'difference': float(difference)
            })
        
        # 4. Create adjustment entry
        print(f"\n➕ Creating equity adjustment entry for ₹{difference:,.2f}...")
        
        db.session.execute(text("""
            INSERT INTO account_transactions
            (tenant_id, account_id, transaction_date, transaction_type,
             debit_amount, credit_amount, balance_after, reference_type, reference_id,
             voucher_number, narration, created_at, created_by)
            VALUES (:tenant_id, NULL, :transaction_date, :transaction_type,
                    :debit_amount, :credit_amount, :balance_after, :reference_type, :reference_id,
                    :voucher_number, :narration, :created_at, :created_by)
        """), {
            'tenant_id': tenant_id,
            'transaction_date': now.date(),
            'transaction_type': 'inventory_equity_adjustment',
            'debit_amount': 0.00,
            'credit_amount': float(difference),
            'balance_after': float(current_value),
            'reference_type': 'inventory_adjustment',
            'reference_id': None,
            'voucher_number': f'ADJ-INV-{tenant_id}-{now.strftime("%Y%m%d")}',
            'narration': f'Inventory Equity Adjustment - Additional stock imports (₹{difference:,.2f})',
            'created_at': now,
            'created_by': None
        })
        
        db.session.commit()
        
        print(f"✅ Created adjustment entry:")
        print(f"   - Type: inventory_equity_adjustment")
        print(f"   - Amount: ₹{difference:,.2f} (CREDIT)")
        print(f"   - Total Equity Now: ₹{current_value:,.2f}")
        
        # 5. Verify trial balance
        trial_balance = db.session.execute(text("""
            SELECT 
                COALESCE(SUM(debit_amount), 0) as total_debit,
                COALESCE(SUM(credit_amount), 0) as total_credit
            FROM account_transactions
            WHERE tenant_id = :tenant_id
        """), {'tenant_id': tenant_id}).fetchone()
        
        total_debit = Decimal(str(trial_balance[0]))
        total_credit = Decimal(str(trial_balance[1]))
        balance_diff = total_debit - total_credit
        
        print(f"\n{'=' * 80}")
        print(f"📊 TRIAL BALANCE VERIFICATION:")
        print(f"   Total Debits:  ₹{total_debit:,.2f}")
        print(f"   Total Credits: ₹{total_credit:,.2f}")
        print(f"   Difference:    ₹{balance_diff:,.2f}")
        
        if abs(balance_diff) < 0.01:
            print(f"   ✅ BALANCED!")
        else:
            print(f"   ⚠️ Still out of balance (other issues may exist)")
        
        print(f"{'=' * 80}\n")
        
        return jsonify({
            'status': 'success',
            'message': f'Inventory equity adjusted by ₹{difference:,.2f}',
            'adjustment': {
                'previous_equity': float(existing_value),
                'current_stock_value': float(current_value),
                'adjustment_amount': float(difference),
                'new_equity_total': float(current_value)
            },
            'trial_balance': {
                'total_debit': float(total_debit),
                'total_credit': float(total_credit),
                'difference': float(balance_diff),
                'is_balanced': abs(balance_diff) < 0.01
            }
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

