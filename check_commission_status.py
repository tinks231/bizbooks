"""
Quick script to check commission status in the database
"""
import os
os.environ['DATABASE_URL'] = 'postgresql://postgres.zwilgdncuxqbkmhgbtsq:bizbooks@123@aws-0-ap-south-1.pooler.supabase.com:6543/postgres'

from modular_app.app import create_app
from models import db, InvoiceCommission, Invoice, Return
from sqlalchemy import text

app = create_app()

with app.app_context():
    print("\n" + "="*80)
    print("🔍 CHECKING COMMISSION STATUS")
    print("="*80 + "\n")
    
    # Find Priya's commission for INV-2025-0003
    result = db.session.execute(text("""
        SELECT 
            ic.id,
            ic.invoice_id,
            i.invoice_number,
            ic.agent_name,
            ic.invoice_amount,
            ic.commission_percentage,
            ic.commission_amount,
            ic.is_paid,
            ic.paid_date
        FROM invoice_commissions ic
        JOIN invoices i ON ic.invoice_id = i.id
        WHERE i.invoice_number = 'INV-2025-0003'
        AND ic.tenant_id = 21
    """)).fetchall()
    
    if not result:
        print("❌ No commission found for INV-2025-0003")
    else:
        for comm in result:
            print(f"📊 Commission Record:")
            print(f"   ID: {comm[0]}")
            print(f"   Invoice: {comm[2]} (ID: {comm[1]})")
            print(f"   Agent: {comm[3]}")
            print(f"   Invoice Amount: ₹{comm[4]}")
            print(f"   Commission %: {comm[5]}%")
            print(f"   Commission Amount: ₹{comm[6]}")
            print(f"   Is Paid: {comm[7]}")
            print(f"   Paid Date: {comm[8]}")
    
    print("\n" + "-"*80 + "\n")
    
    # Check if return exists
    ret = db.session.execute(text("""
        SELECT 
            r.id,
            r.return_number,
            r.invoice_id,
            i.invoice_number,
            r.total_amount,
            r.status
        FROM returns r
        JOIN invoices i ON r.invoice_id = i.id
        WHERE i.invoice_number = 'INV-2025-0003'
        AND r.tenant_id = 21
    """)).fetchall()
    
    if not ret:
        print("❌ No return found for INV-2025-0003")
    else:
        for r in ret:
            print(f"📦 Return Record:")
            print(f"   Return ID: {r[0]}")
            print(f"   Return Number: {r[1]}")
            print(f"   Invoice ID: {r[2]}")
            print(f"   Invoice Number: {r[3]}")
            print(f"   Return Amount: ₹{r[4]}")
            print(f"   Status: {r[5]}")
    
    print("\n" + "-"*80 + "\n")
    
    # Check if commission_reversal entry exists
    reversal = db.session.execute(text("""
        SELECT 
            at.id,
            at.transaction_type,
            at.credit_amount,
            at.reference_id,
            at.narration
        FROM account_transactions at
        WHERE at.tenant_id = 21
        AND at.transaction_type = 'commission_reversal'
        AND at.reference_type = 'return'
    """)).fetchall()
    
    if not reversal:
        print("❌ No commission_reversal entries found")
    else:
        print(f"✅ Found {len(reversal)} commission_reversal entries:")
        for rev in reversal:
            print(f"   ID: {rev[0]} | Type: {rev[1]} | Amount: ₹{rev[2]} | Return ID: {rev[3]}")
            print(f"   Narration: {rev[4]}")
    
    print("\n" + "="*80 + "\n")

