"""
Fix Cash & Bank Opening Balance Equity Entries
These should match the opening_balance in bank_accounts table
"""

from flask import Blueprint, jsonify, g
from models import db
from sqlalchemy import text
from decimal import Decimal
from utils.tenant_middleware import require_tenant, get_current_tenant_id

fix_cash_bank_opening_bp = Blueprint('fix_cash_bank_opening', __name__, url_prefix='/migration')

@fix_cash_bank_opening_bp.route('/fix-cash-bank-opening')
@require_tenant
def fix_cash_bank_opening():
    """
    Fix opening balance equity entries for cash and bank accounts
    
    Problem:
    - Current cash/bank balances: ₹33,373
    - Owner's capital (cash/bank): ₹20,000
    - Missing: ₹13,373
    
    Solution:
    - Delete existing cash/bank opening equity entries
    - Recalculate correct opening balances from bank_accounts table
    - Create new equity entries with correct amounts
    """
    
    try:
        tenant_id = get_current_tenant_id()
        
        print(f"\n{'=' * 80}")
        print(f"🔧 FIXING CASH & BANK OPENING BALANCE FOR TENANT: {tenant_id}")
        print(f"{'=' * 80}")
        
        # 1. Get current bank/cash accounts with their opening balances
        bank_accounts = db.session.execute(text("""
            SELECT 
                account_name,
                account_type,
                opening_balance,
                current_balance
            FROM bank_accounts
            WHERE tenant_id = :tenant_id
            AND is_active = TRUE
        """), {'tenant_id': tenant_id}).fetchall()
        
        print(f"\n📊 Current Bank/Cash Accounts:")
        for acc in bank_accounts:
            print(f"  - {acc[0]} ({acc[1]})")
            print(f"    Opening: ₹{acc[2]:,.2f}")
            print(f"    Current: ₹{acc[3]:,.2f}")
        
        # 2. Delete existing cash/bank opening equity entries
        deleted = db.session.execute(text("""
            DELETE FROM account_transactions
            WHERE tenant_id = :tenant_id
            AND transaction_type = 'opening_balance_equity'
            AND (narration LIKE '%Cash%' OR narration LIKE '%Bank%')
            RETURNING id, credit_amount, narration
        """), {'tenant_id': tenant_id}).fetchall()
        
        if deleted:
            print(f"\n🗑️  Deleted {len(deleted)} old cash/bank equity entries:")
            for entry in deleted:
                print(f"  - ID {entry[0]}: ₹{entry[1]:,.2f} - {entry[2]}")
        
        # 3. Create new equity entries with CORRECT opening balances
        from datetime import datetime
        import pytz
        ist = pytz.timezone('Asia/Kolkata')
        now = datetime.now(ist)
        
        total_opening = Decimal('0')
        
        for acc in bank_accounts:
            account_name = acc[0]
            account_type = acc[1]
            opening_balance = Decimal(str(acc[2]))
            
            if opening_balance > 0:
                # Create equity entry
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
                    'transaction_type': 'opening_balance_equity',
                    'debit_amount': 0.00,
                    'credit_amount': float(opening_balance),
                    'balance_after': float(opening_balance),
                    'reference_type': 'opening_balance',
                    'reference_id': None,
                    'voucher_number': f'OB-{account_type.upper()}-{tenant_id}',
                    'narration': f'Opening Balance - {account_name}',
                    'created_at': now,
                    'created_by': None
                })
                
                total_opening += opening_balance
                print(f"\n✅ Created equity entry for {account_name}: ₹{opening_balance:,.2f}")
        
        db.session.commit()
        
        # 4. Verify trial balance now
        print(f"\n{'=' * 80}")
        print(f"📊 VERIFICATION:")
        print(f"   Total Cash/Bank Opening Equity: ₹{total_opening:,.2f}")
        print(f"{'=' * 80}\n")
        
        return jsonify({
            'status': 'success',
            'message': f'Fixed cash/bank opening balance equity entries',
            'deleted_entries': len(deleted),
            'total_opening_balance': float(total_opening),
            'accounts_processed': len(bank_accounts),
            'action': 'Refresh trial balance page'
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

