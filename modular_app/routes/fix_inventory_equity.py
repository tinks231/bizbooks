"""
Fix missing inventory opening balance equity entries
When inventory is imported, it creates stock_value but doesn't create the equity entry
This migration creates the missing equity entries to balance the books
"""

from flask import Blueprint, jsonify, g
from models import db
from sqlalchemy import text
from datetime import datetime
import pytz
from decimal import Decimal

fix_inventory_equity_bp = Blueprint('fix_inventory_equity', __name__, url_prefix='/migration')


@fix_inventory_equity_bp.route('/fix-inventory-equity')
def fix_inventory_equity():
    """
    Create missing equity entries for inventory opening balances
    
    Problem:
    - When inventory is imported, item_stocks.stock_value is calculated
    - But no account_transaction is created for Owner's Capital (equity)
    - Trial Balance shows inventory as debit, but no matching credit
    - Result: Out of balance by inventory value!
    
    Solution:
    - Calculate total inventory value per tenant
    - Create equity entry: CREDIT Owner's Capital (Inventory Opening)
    - Now Trial Balance will be balanced!
    """
    
    try:
        ist = pytz.timezone('Asia/Kolkata')
        now = datetime.now(ist)
        
        print("\n" + "=" * 80)
        print("🔧 FIXING INVENTORY OPENING BALANCE EQUITY")
        print("=" * 80)
        
        # Get all tenants with inventory
        tenants_with_inventory = db.session.execute(text("""
            SELECT DISTINCT tenant_id
            FROM item_stocks
            WHERE stock_value > 0
        """)).fetchall()
        
        if not tenants_with_inventory:
            return jsonify({
                'status': 'success',
                'message': 'No inventory found that needs equity entries'
            })
        
        print(f"\n📊 Found {len(tenants_with_inventory)} tenant(s) with inventory")
        
        fixes_applied = []
        
        for tenant_row in tenants_with_inventory:
            tenant_id = tenant_row[0]
            
            print(f"\n{'─' * 80}")
            print(f"🏢 Processing Tenant ID: {tenant_id}")
            
            # Calculate total inventory value
            inventory_total = db.session.execute(text("""
                SELECT COALESCE(SUM(stock_value), 0)
                FROM item_stocks
                WHERE tenant_id = :tenant_id
            """), {'tenant_id': tenant_id}).fetchone()[0]
            
            inventory_value = Decimal(str(inventory_total))
            
            if inventory_value <= 0:
                print(f"  ℹ️ No inventory value for tenant {tenant_id}, skipping...")
                continue
            
            print(f"  📦 Total Inventory Value: ₹{inventory_value:,.2f}")
            
            # Check if equity entry already exists
            existing_equity = db.session.execute(text("""
                SELECT id, credit_amount
                FROM account_transactions
                WHERE tenant_id = :tenant_id
                AND account_id IS NULL
                AND transaction_type = 'opening_balance_inventory_equity'
            """), {'tenant_id': tenant_id}).fetchone()
            
            if existing_equity:
                print(f"  ✅ Equity entry already exists (ID: {existing_equity[0]}, Amount: ₹{existing_equity[1]:,.2f})")
                print(f"  ℹ️ Skipping tenant {tenant_id}")
                continue
            
            # Get the earliest item creation date for this tenant (use as transaction date)
            earliest_date = db.session.execute(text("""
                SELECT MIN(created_at::date)
                FROM items
                WHERE tenant_id = :tenant_id
            """), {'tenant_id': tenant_id}).fetchone()[0]
            
            if not earliest_date:
                earliest_date = now.date()
            
            print(f"  📅 Using transaction date: {earliest_date}")
            
            # Create the missing equity entry
            print(f"  ➕ Creating equity entry...")
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
                'transaction_type': 'opening_balance_inventory_equity',
                'debit_amount': 0.00,
                'credit_amount': float(inventory_value),
                'balance_after': float(inventory_value),
                'reference_type': 'inventory_opening',
                'reference_id': None,
                'voucher_number': f'OB-INV-{tenant_id}',
                'narration': f'Opening Balance - Inventory Equity (₹{inventory_value:,.2f} worth of stock)',
                'created_at': now,
                'created_by': None
            })
            
            print(f"  ✅ Created equity entry:")
            print(f"     - Type: opening_balance_inventory_equity")
            print(f"     - Amount: ₹{inventory_value:,.2f} (CREDIT)")
            print(f"     - Narration: Opening Balance - Inventory Equity")
            
            fixes_applied.append({
                'tenant_id': tenant_id,
                'inventory_value': float(inventory_value),
                'transaction_date': str(earliest_date),
                'status': 'equity_created'
            })
        
        db.session.commit()
        
        print("\n" + "=" * 80)
        print(f"✅ MIGRATION COMPLETED!")
        print(f"   Fixed {len(fixes_applied)} tenant(s)")
        print("=" * 80)
        
        # Verify trial balance for each tenant
        print("\n🔍 VERIFICATION:")
        for fix in fixes_applied:
            tenant_id = fix['tenant_id']
            totals = db.session.execute(text("""
                SELECT 
                    SUM(debit_amount) as total_debit,
                    SUM(credit_amount) as total_credit
                FROM account_transactions
                WHERE tenant_id = :tenant_id
            """), {'tenant_id': tenant_id}).fetchone()
            
            total_debit = Decimal(str(totals[0] or 0))
            total_credit = Decimal(str(totals[1] or 0))
            difference = total_debit - total_credit
            
            print(f"\n  Tenant {tenant_id}:")
            print(f"    Total Debits:  ₹{total_debit:,.2f}")
            print(f"    Total Credits: ₹{total_credit:,.2f}")
            print(f"    Difference:    ₹{difference:,.2f}")
            
            if difference == 0:
                print(f"    ✅ BALANCED!")
            else:
                print(f"    ⚠️ Still out of balance")
        
        return jsonify({
            'status': 'success',
            'message': f'Successfully fixed inventory equity for {len(fixes_applied)} tenant(s)',
            'fixes_applied': fixes_applied
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'status': 'error',
            'message': f'Migration failed: {str(e)}'
        }), 500

