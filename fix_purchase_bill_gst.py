#!/usr/bin/env python3
"""
Fix Purchase Bill GST Accounting Entries
==========================================
Fixes the purchase bill that was created before the GST fix.

OLD (WRONG):
  DEBIT:  Inventory ₹1,799.84 (included GST)
  CREDIT: Payables  ₹1,799.84

NEW (CORRECT):
  DEBIT:  Inventory        ₹1,607.00 (before GST)
  DEBIT:  Input Tax Credit ₹192.84   (GST)
  CREDIT: Payables         ₹1,799.84
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
import pytz

def fix_purchase_bill_gst():
    """Fix GST accounting for purchase bill"""
    
    with app.app_context():
        ist = pytz.timezone('Asia/Kolkata')
        now = datetime.now(ist)
        
        print("\n" + "="*80)
        print("🔧 FIXING PURCHASE BILL GST ACCOUNTING")
        print("="*80 + "\n")
        
        # Get ayushi tenant
        tenant = db.session.execute(text("""
            SELECT id FROM tenants WHERE subdomain = 'ayushi'
        """)).fetchone()
        
        if not tenant:
            print("❌ Ayushi tenant not found!")
            return
        
        tenant_id = tenant[0]
        
        # Find purchase bills with wrong accounting
        bills = db.session.execute(text("""
            SELECT 
                pb.id,
                pb.bill_number,
                pb.subtotal,
                pb.cgst_amount,
                pb.sgst_amount,
                pb.igst_amount,
                pb.total_amount,
                pb.bill_date
            FROM purchase_bills pb
            WHERE pb.tenant_id = :tenant_id
            AND pb.status = 'approved'
            AND EXISTS (
                SELECT 1 FROM account_transactions
                WHERE reference_type = 'purchase_bill'
                AND reference_id = pb.id
                AND transaction_type = 'inventory_purchase'
                AND debit_amount = pb.total_amount  -- Old wrong way
            )
            ORDER BY pb.created_at DESC
        """), {'tenant_id': tenant_id}).fetchall()
        
        if not bills:
            print("✅ No bills to fix! (Either already fixed or no bills exist)\n")
            return
        
        print(f"📋 Found {len(bills)} bill(s) to fix:\n")
        
        for bill in bills:
            bill_id = bill[0]
            bill_number = bill[1]
            subtotal = float(bill[2])
            cgst = float(bill[3] or 0)
            sgst = float(bill[4] or 0)
            igst = float(bill[5] or 0)
            total = float(bill[6])
            bill_date = bill[7]
            
            gst_total = cgst + sgst + igst
            
            print(f"🔨 Fixing {bill_number}:")
            print(f"   Subtotal: ₹{subtotal:,.2f}")
            print(f"   GST: ₹{gst_total:,.2f}")
            print(f"   Total: ₹{total:,.2f}")
            
            # Step 1: Delete OLD wrong entries
            deleted = db.session.execute(text("""
                DELETE FROM account_transactions
                WHERE tenant_id = :tenant_id
                AND reference_type = 'purchase_bill'
                AND reference_id = :bill_id
                AND transaction_type IN ('inventory_purchase', 'accounts_payable')
            """), {'tenant_id': tenant_id, 'bill_id': bill_id})
            
            print(f"   ✓ Deleted {deleted.rowcount} old entries")
            
            # Step 2: Create NEW correct entries
            
            # Entry 1: DEBIT Inventory (subtotal only)
            db.session.execute(text("""
                INSERT INTO account_transactions
                (tenant_id, account_id, transaction_date, transaction_type,
                 debit_amount, credit_amount, balance_after, reference_type, reference_id,
                 voucher_number, narration, created_at, created_by)
                VALUES (:tenant_id, NULL, :transaction_date, 'inventory_purchase',
                        :debit_amount, 0.00, :debit_amount, 'purchase_bill', :bill_id,
                        :voucher, :narration, :created_at, NULL)
            """), {
                'tenant_id': tenant_id,
                'transaction_date': bill_date,
                'debit_amount': subtotal,
                'bill_id': bill_id,
                'voucher': bill_number,
                'narration': f'[FIXED] Inventory purchase - {bill_number}',
                'created_at': now
            })
            print(f"   ✓ Created Inventory entry: ₹{subtotal:,.2f}")
            
            # Entry 2: DEBIT Input Tax Credit (GST)
            if gst_total > 0:
                db.session.execute(text("""
                    INSERT INTO account_transactions
                    (tenant_id, account_id, transaction_date, transaction_type,
                     debit_amount, credit_amount, balance_after, reference_type, reference_id,
                     voucher_number, narration, created_at, created_by)
                    VALUES (:tenant_id, NULL, :transaction_date, 'input_tax_credit',
                            :debit_amount, 0.00, :debit_amount, 'purchase_bill', :bill_id,
                            :voucher, :narration, :created_at, NULL)
                """), {
                    'tenant_id': tenant_id,
                    'transaction_date': bill_date,
                    'debit_amount': gst_total,
                    'bill_id': bill_id,
                    'voucher': bill_number,
                    'narration': f'[FIXED] Input Tax Credit - {bill_number}',
                    'created_at': now
                })
                print(f"   ✓ Created ITC entry: ₹{gst_total:,.2f}")
            
            # Entry 3: CREDIT Accounts Payable (total)
            db.session.execute(text("""
                INSERT INTO account_transactions
                (tenant_id, account_id, transaction_date, transaction_type,
                 debit_amount, credit_amount, balance_after, reference_type, reference_id,
                 voucher_number, narration, created_at, created_by)
                VALUES (:tenant_id, NULL, :transaction_date, 'accounts_payable',
                        0.00, :credit_amount, :credit_amount, 'purchase_bill', :bill_id,
                        :voucher, :narration, :created_at, NULL)
            """), {
                'tenant_id': tenant_id,
                'transaction_date': bill_date,
                'credit_amount': total,
                'bill_id': bill_id,
                'voucher': bill_number,
                'narration': f'[FIXED] Payable - {bill_number}',
                'created_at': now
            })
            print(f"   ✓ Created Payable entry: ₹{total:,.2f}")
            print(f"   ✅ FIXED! ₹{subtotal:,.2f} + ₹{gst_total:,.2f} = ₹{total:,.2f}\n")
        
        # Commit all changes
        db.session.commit()
        
        print("="*80)
        print(f"🎉 SUCCESS! Fixed {len(bills)} purchase bill(s)")
        print("="*80)
        print("\n✅ Trial Balance should now be BALANCED!")
        print("✅ Input Tax Credit (ITC) will show as an asset\n")

if __name__ == "__main__":
    fix_purchase_bill_gst()

