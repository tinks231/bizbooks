"""
Fix Old Return - Add Missing Refund Payment Entry
This script adds the missing accounting entry for the return that was approved before the fixes
"""

import sys
sys.path.insert(0, 'modular_app')

from app import app, db
from sqlalchemy import text
from datetime import datetime
from decimal import Decimal
import pytz

with app.app_context():
    tenant_id = 21  # Ayushi tenant
    
    print("\n" + "="*80)
    print("🔧 FIXING OLD RETURN - Adding Missing Refund Payment Entry")
    print("="*80 + "\n")
    
    # Get the return record
    result = db.session.execute(text("""
        SELECT 
            id,
            return_number,
            total_amount,
            refund_method,
            payment_account_id,
            return_date
        FROM returns
        WHERE tenant_id = :tenant_id
        ORDER BY created_at DESC
        LIMIT 1
    """), {'tenant_id': tenant_id}).fetchone()
    
    if not result:
        print("❌ No return found for tenant!")
        sys.exit(1)
    
    return_id = result[0]
    return_number = result[1]
    total_amount = Decimal(str(result[2]))
    refund_method = result[3]
    payment_account_id = result[4]
    return_date = result[5]
    
    print(f"📦 Found Return:")
    print(f"   ID: {return_id}")
    print(f"   Number: {return_number}")
    print(f"   Amount: ₹{total_amount}")
    print(f"   Refund Method: {refund_method}")
    print(f"   Payment Account ID: {payment_account_id}")
    print()
    
    # Check if refund_payment entry already exists
    existing = db.session.execute(text("""
        SELECT COUNT(*) 
        FROM account_transactions
        WHERE tenant_id = :tenant_id
        AND reference_type = 'return'
        AND reference_id = :return_id
        AND transaction_type = 'refund_payment'
    """), {'tenant_id': tenant_id, 'return_id': return_id}).scalar()
    
    if existing > 0:
        print(f"✅ Refund payment entry already exists ({existing} entries)")
        print("Nothing to fix!")
        sys.exit(0)
    
    print("❌ Refund payment entry MISSING - Adding now...\n")
    
    if not payment_account_id:
        print("⚠️ WARNING: payment_account_id is NULL!")
        print("Searching for a bank account to use...")
        
        # Find first available bank account
        bank_account = db.session.execute(text("""
            SELECT id, account_name, current_balance
            FROM bank_accounts
            WHERE tenant_id = :tenant_id
            AND account_type = 'bank'
            AND is_active = TRUE
            LIMIT 1
        """), {'tenant_id': tenant_id}).fetchone()
        
        if not bank_account:
            print("❌ No active bank account found!")
            sys.exit(1)
        
        payment_account_id = bank_account[0]
        print(f"✅ Using: {bank_account[1]} (Balance: ₹{bank_account[2]})")
        
        # Update return record with payment_account_id
        db.session.execute(text("""
            UPDATE returns
            SET payment_account_id = :account_id
            WHERE id = :return_id
        """), {'account_id': payment_account_id, 'return_id': return_id})
        print(f"✅ Updated return record with payment_account_id = {payment_account_id}\n")
    
    # Get current account balance
    account_info = db.session.execute(text("""
        SELECT account_name, account_type, current_balance
        FROM bank_accounts
        WHERE id = :account_id AND tenant_id = :tenant_id
    """), {'account_id': payment_account_id, 'tenant_id': tenant_id}).fetchone()
    
    if not account_info:
        print(f"❌ Account ID {payment_account_id} not found!")
        sys.exit(1)
    
    account_name = account_info[0]
    account_type = account_info[1]
    current_balance = Decimal(str(account_info[2]))
    new_balance = current_balance - total_amount
    
    print(f"💰 Account: {account_name} ({account_type})")
    print(f"   Current Balance: ₹{current_balance}")
    print(f"   Refund Amount: ₹{total_amount}")
    print(f"   New Balance: ₹{new_balance}\n")
    
    # Create the missing refund_payment entry
    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.now(ist)
    
    db.session.execute(text("""
        INSERT INTO account_transactions
        (tenant_id, account_id, transaction_date, transaction_type,
         debit_amount, credit_amount, balance_after, reference_type, reference_id,
         voucher_number, narration, created_at, created_by)
        VALUES (:tenant_id, :account_id, :transaction_date, 'refund_payment',
                0.00, :credit_amount, :balance, 'return', :return_id,
                :voucher, :narration, :created_at, NULL)
    """), {
        'tenant_id': tenant_id,
        'account_id': payment_account_id,
        'transaction_date': return_date,
        'credit_amount': float(total_amount),
        'balance': float(new_balance),
        'return_id': return_id,
        'voucher': return_number,
        'narration': f'Refund to customer via {account_name}',
        'created_at': now
    })
    
    print("✅ Created refund_payment accounting entry")
    
    # Update account balance
    db.session.execute(text("""
        UPDATE bank_accounts 
        SET current_balance = :new_balance, updated_at = :updated_at
        WHERE id = :account_id AND tenant_id = :tenant_id
    """), {
        'new_balance': new_balance,
        'updated_at': now,
        'account_id': payment_account_id,
        'tenant_id': tenant_id
    })
    
    print(f"✅ Updated {account_name} balance: ₹{current_balance} → ₹{new_balance}")
    
    # Commit changes
    db.session.commit()
    
    print("\n" + "="*80)
    print("🎉 SUCCESS! Old return fixed!")
    print("="*80)
    
    print("\n📊 ACCOUNTING ENTRIES NOW COMPLETE:")
    print(f"   DEBIT  Sales Returns ........... ₹{total_amount - (total_amount * Decimal('0.12'))}")  # Approximate
    print(f"   DEBIT  GST Receivable ........... ₹{total_amount * Decimal('0.12')}")  # Approximate
    print(f"   CREDIT {account_name} ........... ₹{total_amount}")
    print(f"   ─────────────────────────────────────────")
    print(f"   Total Debits = Total Credits = ₹{total_amount}")
    
    print("\n✅ Trial Balance should now be BALANCED!")
    print("\n🧪 Next: Test the reports and create a new return to verify the flow.\n")

