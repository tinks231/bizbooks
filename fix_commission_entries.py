#!/usr/bin/env python3
"""
Fix Commission Payment Entries - Remove Duplicate Entries

PROBLEM:
- Commission expense entries were created with account_id (linked to cash/bank)
- This caused them to appear in cash account ledger
- Debits and credits canceled out, so balance didn't change
- Need to delete wrong entries and re-create correctly

SOLUTION:
- Delete all commission_expense entries that have account_id (wrong)
- Keep only cash_payment/bank_payment entries (correct)
- Mark commissions as unpaid so they can be paid again correctly
"""

import os
import sys

# Force use of local database
os.environ['DATABASE_URL'] = "postgresql://bizbooks_dev:local_dev_password_123@localhost:5432/bizbooks_test"

# Add modular_app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modular_app'))

from models import db
from app import app
from sqlalchemy import text
from datetime import datetime

def fix_commission_entries():
    """Fix commission payment accounting entries"""
    
    with app.app_context():
        print("\n" + "="*80)
        print("🔧 FIXING COMMISSION PAYMENT ENTRIES")
        print("="*80 + "\n")
        
        # Get ayushi tenant
        tenant = db.session.execute(text("""
            SELECT id FROM tenants WHERE subdomain = 'ayushi'
        """)).fetchone()
        
        if not tenant:
            print("❌ Ayushi tenant not found!")
            return
        
        tenant_id = tenant[0]
        
        print("📊 Finding wrong commission entries...")
        
        # Find commission_expense entries that have account_id (WRONG!)
        wrong_entries = db.session.execute(text("""
            SELECT 
                id,
                transaction_date,
                voucher_number,
                debit_amount,
                account_id,
                narration
            FROM account_transactions
            WHERE tenant_id = :tenant_id
            AND transaction_type = 'commission_expense'
            AND account_id IS NOT NULL
            ORDER BY transaction_date DESC
        """), {'tenant_id': tenant_id}).fetchall()
        
        if not wrong_entries:
            print("✅ No wrong entries found! (Already fixed or none exist)\n")
            return
        
        print(f"\n⚠️ Found {len(wrong_entries)} wrong entries:\n")
        
        for entry in wrong_entries:
            print(f"  - {entry[1]}: {entry[2]} - ₹{entry[3]:.2f}")
            print(f"    Narration: {entry[5]}")
            print(f"    Problem: Has account_id={entry[4]} (should be NULL)")
        
        # Delete wrong entries
        print(f"\n🗑️ Deleting {len(wrong_entries)} wrong commission_expense entries...")
        
        result = db.session.execute(text("""
            DELETE FROM account_transactions
            WHERE tenant_id = :tenant_id
            AND transaction_type = 'commission_expense'
            AND account_id IS NOT NULL
        """), {'tenant_id': tenant_id})
        
        print(f"✅ Deleted {result.rowcount} wrong entries\n")
        
        # Mark commissions as unpaid so they can be paid again
        print("📝 Marking commissions as unpaid for re-payment...")
        
        comm_result = db.session.execute(text("""
            UPDATE invoice_commissions
            SET is_paid = FALSE,
                paid_date = NULL,
                payment_notes = 'Re-payment needed due to accounting fix'
            WHERE tenant_id = :tenant_id
            AND is_paid = TRUE
        """), {'tenant_id': tenant_id})
        
        print(f"✅ Marked {comm_result.rowcount} commissions as unpaid\n")
        
        db.session.commit()
        
        print("="*80)
        print("🎉 FIX COMPLETE!")
        print("="*80)
        print("\n📌 NEXT STEPS:")
        print("1. Refresh your browser")
        print("2. Go to Commission Reports")
        print("3. Pay commissions again (they'll show as unpaid)")
        print("4. Check Cash Book - balance will now change correctly!")
        print("5. Check Profit & Loss - commission expenses will show correctly!\n")

if __name__ == "__main__":
    fix_commission_entries()

