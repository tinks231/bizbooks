#!/usr/bin/env python3
"""
Diagnose Trial Balance Issues
Find transactions that aren't properly balanced
"""

import os
os.environ['DATABASE_URL'] = "postgresql://bizbooks_dev:local_dev_password_123@localhost:5432/bizbooks_test"

from modular_app.models import db
from modular_app.app import app
from sqlalchemy import text
from decimal import Decimal

def diagnose_trial_balance(tenant_subdomain):
    """Find unbalanced transactions for a tenant"""
    
    with app.app_context():
        # Get tenant ID
        tenant = db.session.execute(text("""
            SELECT id, company_name FROM tenants WHERE subdomain = :subdomain
        """), {'subdomain': tenant_subdomain}).fetchone()
        
        if not tenant:
            print(f"❌ Tenant '{tenant_subdomain}' not found!")
            return
        
        tenant_id = tenant[0]
        print(f"\n{'='*80}")
        print(f"🔍 DIAGNOSING: {tenant[1]} ({tenant_subdomain})")
        print(f"{'='*80}\n")
        
        # Check total debits vs credits
        result = db.session.execute(text("""
            SELECT 
                SUM(debit_amount) as total_debits,
                SUM(credit_amount) as total_credits,
                SUM(debit_amount) - SUM(credit_amount) as difference
            FROM account_transactions
            WHERE tenant_id = :tenant_id
        """), {'tenant_id': tenant_id}).fetchone()
        
        total_debits = Decimal(str(result[0] or 0))
        total_credits = Decimal(str(result[1] or 0))
        difference = Decimal(str(result[2] or 0))
        
        print(f"📊 ACCOUNT TRANSACTIONS SUMMARY:")
        print(f"   Total Debits:  ₹{total_debits:,.2f}")
        print(f"   Total Credits: ₹{total_credits:,.2f}")
        print(f"   Difference:    ₹{difference:,.2f}")
        
        if abs(difference) < 0.01:
            print(f"   ✅ BALANCED!\n")
            return
        else:
            print(f"   ❌ OUT OF BALANCE by ₹{abs(difference):,.2f}\n")
        
        # Find transactions by type
        print(f"📋 TRANSACTIONS BY TYPE:")
        print(f"{'Type':<35} {'Count':>8} {'Debits':>15} {'Credits':>15} {'Diff':>15}")
        print(f"{'-'*80}")
        
        transactions_by_type = db.session.execute(text("""
            SELECT 
                transaction_type,
                COUNT(*) as count,
                SUM(debit_amount) as total_debits,
                SUM(credit_amount) as total_credits,
                SUM(debit_amount) - SUM(credit_amount) as difference
            FROM account_transactions
            WHERE tenant_id = :tenant_id
            GROUP BY transaction_type
            ORDER BY ABS(SUM(debit_amount) - SUM(credit_amount)) DESC
        """), {'tenant_id': tenant_id}).fetchall()
        
        for row in transactions_by_type:
            txn_type = row[0]
            count = row[1]
            debits = Decimal(str(row[2] or 0))
            credits = Decimal(str(row[3] or 0))
            diff = Decimal(str(row[4] or 0))
            
            status = "✅" if abs(diff) < 0.01 else "❌"
            print(f"{txn_type:<35} {count:>8} {debits:>15,.2f} {credits:>15,.2f} {diff:>15,.2f} {status}")
        
        print(f"\n")
        
        # Find specific unbalanced transaction types
        print(f"🔴 PROBLEMATIC TRANSACTION TYPES:")
        print(f"{'-'*80}")
        
        for row in transactions_by_type:
            txn_type = row[0]
            diff = Decimal(str(row[4] or 0))
            
            if abs(diff) > 0.01:
                print(f"\n❌ {txn_type}: Out by ₹{abs(diff):,.2f}")
                
                # Show sample transactions
                samples = db.session.execute(text("""
                    SELECT id, transaction_date, voucher_number, 
                           debit_amount, credit_amount, narration
                    FROM account_transactions
                    WHERE tenant_id = :tenant_id 
                    AND transaction_type = :txn_type
                    ORDER BY transaction_date DESC
                    LIMIT 5
                """), {'tenant_id': tenant_id, 'txn_type': txn_type}).fetchall()
                
                print(f"   Sample transactions:")
                for sample in samples:
                    print(f"   • {sample[2]}: Dr ₹{sample[3]:,.2f} / Cr ₹{sample[4]:,.2f} - {sample[5][:50]}")
        
        print(f"\n{'='*80}\n")
        
        # Suggestions
        print(f"💡 SUGGESTED FIXES:")
        print(f"   1. Check if migration completed successfully")
        print(f"   2. Look at transaction types with imbalances above")
        print(f"   3. May need to create matching entries for old transactions")
        print(f"   4. Consider re-running migration (safe to run multiple times)")
        print(f"\n")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        subdomain = sys.argv[1]
    else:
        subdomain = "mahaveerelectricals"
    
    diagnose_trial_balance(subdomain)

