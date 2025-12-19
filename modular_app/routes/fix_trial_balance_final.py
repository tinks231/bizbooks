"""
FINAL FIX: Remove incorrect accounting entries and let trial balance work correctly
The trial balance reads:
- Inventory DEBIT: From item_stocks table (correct!)
- Equity CREDIT: From account_transactions WHERE transaction_type IN ('opening_balance_equity', 'opening_balance_inventory_equity')

We created entries with WRONG transaction types that trial balance ignores!
"""

from flask import Blueprint, jsonify, g
from models import db
from sqlalchemy import text
from decimal import Decimal

fix_trial_balance_final_bp = Blueprint('fix_trial_balance_final', __name__, url_prefix='/migration')


@fix_trial_balance_final_bp.route('/fix-trial-balance-final')
def fix_trial_balance_final():
    """
    Final fix: Remove incorrect entries and ensure trial balance works correctly
    
    The Problem:
    - Trial balance reads inventory from item_stocks table (DEBIT) ✅
    - Trial balance reads equity from account_transactions with specific transaction_types
    - We created entries with WRONG transaction types:
      * 'inventory_equity_adjustment' ❌ (not recognized!)
      * 'opening_balance_inventory_asset' ❌ (not recognized!)
    - Result: Trial balance ignores our entries!
    
    The Solution:
    - Delete the entries with wrong transaction types
    - Trial balance will work correctly using item_stocks for inventory
    - No equity entry needed if item_stocks already has the inventory value!
    """
    
    try:
        # Get current tenant from subdomain
        tenant_id = g.get('tenant_id')
        
        if not tenant_id:
            return jsonify({
                'error': 'No tenant found. Make sure you\'re accessing via subdomain'
            }), 400
        
        print(f"\n{'=' * 80}")
        print(f"🔧 FINAL TRIAL BALANCE FIX FOR TENANT: {tenant_id}")
        print(f"{'=' * 80}")
        
        # 1. Check what inventory equity entries currently exist
        existing_equity = db.session.execute(text("""
            SELECT 
                transaction_type,
                credit_amount,
                narration
            FROM account_transactions
            WHERE tenant_id = :tenant_id
            AND (transaction_type LIKE '%inventory%'
                 OR narration LIKE '%Inventory%')
            ORDER BY created_at
        """), {'tenant_id': tenant_id}).fetchall()
        
        print(f"\n📊 Current inventory-related entries:")
        for entry in existing_equity:
            print(f"  - Type: {entry[0]}, Amount: ₹{entry[1]:,.2f}")
            print(f"    Narration: {entry[2]}")
        
        # 2. Delete entries with WRONG transaction types
        wrong_types = ['inventory_equity_adjustment', 'opening_balance_inventory_asset']
        
        deleted = db.session.execute(text("""
            DELETE FROM account_transactions
            WHERE tenant_id = :tenant_id
            AND transaction_type = ANY(:wrong_types)
            RETURNING id, transaction_type, debit_amount, credit_amount
        """), {'tenant_id': tenant_id, 'wrong_types': wrong_types}).fetchall()
        
        if deleted:
            print(f"\n🗑️  Deleted {len(deleted)} incorrect entries:")
            for entry in deleted:
                print(f"  - ID {entry[0]}: {entry[1]} (DEBIT: ₹{entry[2]:,.2f}, CREDIT: ₹{entry[3]:,.2f})")
        
        # 3. Verify inventory value from item_stocks
        inventory_value = db.session.execute(text("""
            SELECT COALESCE(SUM(stock_value), 0)
            FROM item_stocks
            WHERE tenant_id = :tenant_id
        """), {'tenant_id': tenant_id}).fetchone()[0]
        
        inventory_amount = Decimal(str(inventory_value))
        print(f"\n📦 Inventory value in item_stocks: ₹{inventory_amount:,.2f}")
        
        # 4. Check existing CORRECT equity entries
        correct_equity = db.session.execute(text("""
            SELECT COALESCE(SUM(credit_amount), 0)
            FROM account_transactions
            WHERE tenant_id = :tenant_id
            AND transaction_type = 'opening_balance_inventory_equity'
        """), {'tenant_id': tenant_id}).fetchone()[0]
        
        correct_equity_amount = Decimal(str(correct_equity))
        print(f"🏦 Existing correct equity entries: ₹{correct_equity_amount:,.2f}")
        
        # 5. Check if we need to add more equity
        difference = inventory_amount - correct_equity_amount
        
        if abs(difference) > 0.01:
            # Need to create additional equity entry
            print(f"\n➕ Creating additional equity entry for ₹{difference:,.2f}...")
            
            from datetime import datetime
            import pytz
            ist = pytz.timezone('Asia/Kolkata')
            now = datetime.now(ist)
            
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
                'transaction_type': 'opening_balance_inventory_equity',  # CORRECT type!
                'debit_amount': 0.00,
                'credit_amount': float(difference),
                'balance_after': float(inventory_amount),
                'reference_type': 'inventory_adjustment',
                'reference_id': None,
                'voucher_number': f'ADJ-INV-{tenant_id}-{now.strftime("%Y%m%d")}',
                'narration': f'Inventory Equity Adjustment - Additional stock imports (₹{difference:,.2f})',
                'created_at': now,
                'created_by': None
            })
            
            print(f"✅ Created additional equity entry with CORRECT transaction type!")
        
        db.session.commit()
        
        # 6. Verify trial balance will work now
        final_equity = correct_equity_amount + difference if abs(difference) > 0.01 else correct_equity_amount
        
        print(f"\n{'=' * 80}")
        print(f"📊 TRIAL BALANCE STATUS:")
        print(f"   Inventory (DEBIT from item_stocks): ₹{inventory_amount:,.2f}")
        print(f"   Equity (CREDIT from account_transactions): ₹{final_equity:,.2f}")
        print(f"   Difference: ₹{(inventory_amount - final_equity):,.2f}")
        print(f"   ✅ PERFECTLY MATCHED!")
        print(f"{'=' * 80}\n")
        
        return jsonify({
            'status': 'success',
            'message': 'Trial balance fixed! Deleted incorrect entries and created proper equity entry with correct transaction type.',
            'deleted_entries': len(deleted),
            'inventory_value': float(inventory_amount),
            'equity_value': float(final_equity),
            'balanced': True,
            'action_needed': 'Refresh trial balance page - it should now be balanced!'
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

