"""
Fix missing inventory asset (DEBIT) entries in double-entry accounting
When inventory is imported, both DEBIT (asset) and CREDIT (equity) entries needed
"""

from flask import Blueprint, jsonify, g
from models import db
from sqlalchemy import text
from decimal import Decimal
from datetime import datetime
import pytz

fix_inventory_double_entry_bp = Blueprint('fix_inventory_double_entry', __name__, url_prefix='/migration')


@fix_inventory_double_entry_bp.route('/fix-inventory-double-entry')
def fix_inventory_double_entry():
    """
    Fix missing inventory DEBIT entries (asset side)
    
    Problem:
    - Inventory imported: ₹2,143,000 in item_stocks table
    - Equity (CREDIT) created: ₹2,143,000 ✅
    - BUT inventory asset (DEBIT) missing: ❌
    - Result: Trial balance shows only credits, no matching debits!
    
    Solution:
    - Create DEBIT entry for inventory asset
    - Now both sides of the equation are recorded
    - Trial balance will be balanced!
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
        print(f"🔧 FIXING INVENTORY DOUBLE-ENTRY FOR TENANT: {tenant_id}")
        print(f"{'=' * 80}")
        
        # 1. Get current inventory value from item_stocks
        inventory_value = db.session.execute(text("""
            SELECT COALESCE(SUM(stock_value), 0)
            FROM item_stocks
            WHERE tenant_id = :tenant_id
        """), {'tenant_id': tenant_id}).fetchone()[0]
        
        inventory_amount = Decimal(str(inventory_value))
        print(f"\n📦 Current Inventory Value: ₹{inventory_amount:,.2f}")
        
        if inventory_amount <= 0:
            return jsonify({
                'status': 'success',
                'message': 'No inventory found, no fix needed'
            })
        
        # 2. Check if inventory asset DEBIT entry already exists
        existing_inventory_debit = db.session.execute(text("""
            SELECT COALESCE(SUM(debit_amount), 0)
            FROM account_transactions
            WHERE tenant_id = :tenant_id
            AND (transaction_type = 'opening_balance_inventory_asset'
                 OR narration LIKE '%Inventory (Stock on Hand)%')
        """), {'tenant_id': tenant_id}).fetchone()[0]
        
        existing_debit = Decimal(str(existing_inventory_debit))
        print(f"📊 Existing Inventory DEBIT Entries: ₹{existing_debit:,.2f}")
        
        # 3. Calculate what's missing
        missing_debit = inventory_amount - existing_debit
        print(f"⚠️  Missing DEBIT Amount: ₹{missing_debit:,.2f}")
        
        if abs(missing_debit) < 0.01:
            print(f"\n✅ Inventory DEBIT already matches! No fix needed.")
            return jsonify({
                'status': 'success',
                'message': 'Inventory DEBIT entries already correct',
                'inventory_value': float(inventory_amount),
                'existing_debit': float(existing_debit)
            })
        
        # 4. Get the earliest item creation date (use as transaction date)
        earliest_date = db.session.execute(text("""
            SELECT MIN(created_at::date)
            FROM items
            WHERE tenant_id = :tenant_id
        """), {'tenant_id': tenant_id}).fetchone()[0]
        
        if not earliest_date:
            earliest_date = now.date()
        
        print(f"📅 Using transaction date: {earliest_date}")
        
        # 5. Create DEBIT entry for inventory asset
        print(f"\n➕ Creating inventory asset (DEBIT) entry for ₹{missing_debit:,.2f}...")
        
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
            'transaction_date': earliest_date,
            'transaction_type': 'opening_balance_inventory_asset',
            'debit_amount': float(missing_debit),
            'credit_amount': 0.00,
            'balance_after': float(missing_debit),
            'reference_type': 'inventory_opening',
            'reference_id': None,
            'voucher_number': f'OB-INVA-{tenant_id}',
            'narration': f'Opening Balance - Inventory (Stock on Hand) - Asset Entry',
            'created_at': now,
            'created_by': None
        })
        
        db.session.commit()
        
        print(f"✅ Created inventory asset entry:")
        print(f"   - Type: opening_balance_inventory_asset")
        print(f"   - Amount: ₹{missing_debit:,.2f} (DEBIT)")
        print(f"   - Narration: Opening Balance - Inventory (Stock on Hand)")
        
        # 6. Verify trial balance NOW
        trial_balance = db.session.execute(text("""
            SELECT 
                COALESCE(SUM(debit_amount), 0) as total_debit,
                COALESCE(SUM(credit_amount), 0) as total_credit
            FROM account_transactions
            WHERE tenant_id = :tenant_id
        """), {'tenant_id': tenant_id}).fetchone()
        
        total_debit = Decimal(str(trial_balance[0]))
        total_credit = Decimal(str(trial_balance[1]))
        difference = total_debit - total_credit
        
        print(f"\n{'=' * 80}")
        print(f"📊 TRIAL BALANCE AFTER FIX:")
        print(f"   Total Debits:  ₹{total_debit:,.2f}")
        print(f"   Total Credits: ₹{total_credit:,.2f}")
        print(f"   Difference:    ₹{difference:,.2f}")
        
        if abs(difference) < 0.01:
            print(f"   🎉 PERFECTLY BALANCED!")
        else:
            print(f"   ⚠️ Still out by ₹{abs(difference):,.2f} (other issues may exist)")
        
        print(f"{'=' * 80}\n")
        
        return jsonify({
            'status': 'success',
            'message': f'Inventory asset (DEBIT) entry created for ₹{missing_debit:,.2f}',
            'fix_applied': {
                'inventory_value': float(inventory_amount),
                'previous_debit': float(existing_debit),
                'adjustment_amount': float(missing_debit),
                'new_debit_total': float(inventory_amount)
            },
            'trial_balance': {
                'total_debit': float(total_debit),
                'total_credit': float(total_credit),
                'difference': float(difference),
                'is_balanced': abs(difference) < 0.01
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

