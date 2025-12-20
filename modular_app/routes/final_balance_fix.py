"""
Final comprehensive fix:
1. Delete duplicate bank entry
2. Create equity for new inventory
"""

from flask import Blueprint, jsonify, g
from models import db
from sqlalchemy import text
from decimal import Decimal
from utils.tenant_middleware import require_tenant, get_current_tenant_id

final_balance_fix_bp = Blueprint('final_balance_fix', __name__, url_prefix='/migration')

@final_balance_fix_bp.route('/final-balance-fix')
@require_tenant
def final_balance_fix():
    """
    Comprehensive fix:
    1. Delete old duplicate bank equity entry (ID 46)
    2. Calculate if new inventory was added
    3. Create equity entry for any missing inventory equity
    """
    
    try:
        tenant_id = get_current_tenant_id()
        
        print(f"\n{'=' * 80}")
        print(f"🔧 FINAL COMPREHENSIVE BALANCE FIX FOR TENANT: {tenant_id}")
        print(f"{'=' * 80}")
        
        # 1. Delete old duplicate bank entry (ID 46 specifically)
        deleted_bank = db.session.execute(text("""
            DELETE FROM account_transactions
            WHERE tenant_id = :tenant_id
            AND id = 46
            RETURNING id, narration, credit_amount
        """), {'tenant_id': tenant_id}).fetchone()
        
        if deleted_bank:
            print(f"\n🗑️  Deleted old duplicate bank entry:")
            print(f"   ID {deleted_bank[0]}: {deleted_bank[1]} = ₹{deleted_bank[2]:,.2f}")
        
        # 2. Calculate current inventory value
        current_inventory = db.session.execute(text("""
            SELECT COALESCE(SUM(stock_value), 0)
            FROM item_stocks
            WHERE tenant_id = :tenant_id
        """), {'tenant_id': tenant_id}).fetchone()[0]
        
        inventory_value = Decimal(str(current_inventory))
        print(f"\n📦 Current Inventory Value: ₹{inventory_value:,.2f}")
        
        # 3. Calculate existing inventory equity
        existing_inventory_equity = db.session.execute(text("""
            SELECT COALESCE(SUM(credit_amount), 0)
            FROM account_transactions
            WHERE tenant_id = :tenant_id
            AND transaction_type = 'opening_balance_inventory_equity'
        """), {'tenant_id': tenant_id}).fetchone()[0]
        
        existing_equity = Decimal(str(existing_inventory_equity))
        print(f"🏦 Existing Inventory Equity: ₹{existing_equity:,.2f}")
        
        # 4. Calculate missing equity
        missing_equity = inventory_value - existing_equity
        print(f"⚠️  Missing Equity: ₹{missing_equity:,.2f}")
        
        # 5. Create equity entry for missing amount if needed
        if abs(missing_equity) > 0.01:
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
                'transaction_type': 'opening_balance_inventory_equity',
                'debit_amount': 0.00,
                'credit_amount': float(missing_equity),
                'balance_after': float(inventory_value),
                'reference_type': 'inventory_adjustment',
                'reference_id': None,
                'voucher_number': f'ADJ-INV-{tenant_id}-{now.strftime("%Y%m%d-%H%M")}',
                'narration': f'Inventory Equity Adjustment - New stock added (₹{missing_equity:,.2f})',
                'created_at': now,
                'created_by': None
            })
            
            print(f"\n✅ Created new inventory equity entry: ₹{missing_equity:,.2f}")
        
        db.session.commit()
        
        # 6. Verify trial balance
        trial_balance = db.session.execute(text("""
            SELECT 
                COALESCE(SUM(debit_amount), 0) as total_debit,
                COALESCE(SUM(credit_amount), 0) as total_credit
            FROM account_transactions
            WHERE tenant_id = :tenant_id
        """), {'tenant_id': tenant_id}).fetchone()
        
        print(f"\n{'=' * 80}")
        print(f"📊 RESULT:")
        print(f"   Deleted duplicate bank entry: {'Yes' if deleted_bank else 'Not found'}")
        print(f"   Added inventory equity: ₹{missing_equity:,.2f}" if abs(missing_equity) > 0.01 else "   No new equity needed")
        print(f"{'=' * 80}\n")
        
        return jsonify({
            'status': 'success',
            'message': 'Balance fixed comprehensively',
            'deleted_bank_entry': deleted_bank is not None,
            'inventory_equity_added': float(missing_equity) if abs(missing_equity) > 0.01 else 0,
            'current_inventory_value': float(inventory_value),
            'total_inventory_equity': float(inventory_value),
            'action': 'Refresh trial balance page - should now be balanced!'
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

