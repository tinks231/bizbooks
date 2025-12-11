"""
DATA MIGRATION: Convert existing data to double-entry accounting system

⚠️  WARNING: This is a ONE-TIME migration script!
    Only run this ONCE after deploying the double-entry accounting changes.

What this does:
1. Migrates existing purchase bills
2. Migrates existing invoices (with COGS calculation)
3. Migrates existing expenses
4. Migrates existing salary payments

Created: December 11, 2025
"""

from flask import Blueprint, jsonify, g, session, redirect, url_for, flash
from models import db, PurchaseBill, Invoice, InvoiceItem, Item, Expense, ExpenseCategory
from sqlalchemy import text
from datetime import datetime
import pytz
from decimal import Decimal

migrate_double_entry_bp = Blueprint('migrate_double_entry', __name__, url_prefix='/migration')


@migrate_double_entry_bp.route('/to-double-entry')
def migrate_to_double_entry():
    """
    ONE-TIME migration: Convert existing data to double-entry accounting
    
    ⚠️  WARNING: Only run this ONCE!
    
    This will create accounting entries for:
    - All existing purchase bills (inventory + payables)
    - All existing invoices (sales + COGS + receivables)
    - All existing expenses (expense accounts)
    - All existing salary payments (salary expense)
    """
    
    # Require superadmin or admin login
    if 'tenant_admin_id' not in session:
        flash('Please login to run migrations', 'error')
        return redirect(url_for('admin.login'))
    
    try:
        ist = pytz.timezone('Asia/Kolkata')
        now = datetime.now(ist)
        
        results = {
            'purchase_bills_migrated': 0,
            'invoices_migrated': 0,
            'expenses_migrated': 0,
            'salary_payments_migrated': 0,
            'entries_created': 0,
            'errors': []
        }
        
        print("\n" + "=" * 80)
        print("🔄 MIGRATING TO DOUBLE-ENTRY ACCOUNTING SYSTEM")
        print("=" * 80)
        
        # ═══════════════════════════════════════════════════════════════════
        # STEP 1: Migrate Purchase Bills
        # ═══════════════════════════════════════════════════════════════════
        
        print("\n📦 Step 1: Migrating Purchase Bills...")
        
        # Find purchase bills that don't have accounting entries yet
        purchase_bills = db.session.execute(text("""
            SELECT DISTINCT pb.id, pb.tenant_id, pb.bill_number, pb.vendor_name, 
                   pb.bill_date, pb.total_amount, pb.paid_amount
            FROM purchase_bills pb
            WHERE NOT EXISTS (
                SELECT 1 FROM account_transactions 
                WHERE reference_type = 'purchase_bill' 
                AND reference_id = pb.id
                AND transaction_type IN ('inventory_purchase', 'accounts_payable')
            )
            ORDER BY pb.bill_date, pb.id
        """)).fetchall()
        
        for bill in purchase_bills:
            bill_id = bill[0]
            tenant_id = bill[1]
            bill_number = bill[2]
            vendor_name = bill[3]
            bill_date = bill[4]
            total_amount = Decimal(str(bill[5]))
            paid_amount = Decimal(str(bill[6] or 0))
            
            # Entry 1: DEBIT Inventory
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
                'debit_amount': float(total_amount),
                'bill_id': bill_id,
                'voucher': bill_number,
                'narration': f'[MIGRATED] Inventory purchase from {vendor_name} - {bill_number}',
                'created_at': now
            })
            
            # Entry 2: CREDIT Accounts Payable
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
                'credit_amount': float(total_amount),
                'bill_id': bill_id,
                'voucher': bill_number,
                'narration': f'[MIGRATED] Payable to {vendor_name} - {bill_number}',
                'created_at': now
            })
            
            # If bill was paid, create payment entries
            if paid_amount > 0:
                # Entry 3: DEBIT Accounts Payable (payment made)
                db.session.execute(text("""
                    INSERT INTO account_transactions
                    (tenant_id, account_id, transaction_date, transaction_type,
                     debit_amount, credit_amount, balance_after, reference_type, reference_id,
                     voucher_number, narration, created_at, created_by)
                    VALUES (:tenant_id, NULL, :transaction_date, 'accounts_payable_payment',
                            :debit, 0.00, 0.00, 'purchase_bill', :bill_id,
                            :voucher, :narration, :created_at, NULL)
                """), {
                    'tenant_id': tenant_id,
                    'transaction_date': bill_date,
                    'debit': float(paid_amount),
                    'bill_id': bill_id,
                    'voucher': bill_number,
                    'narration': f'[MIGRATED] Payment to {vendor_name} for {bill_number}',
                    'created_at': now
                })
                
                results['entries_created'] += 1
            
            results['purchase_bills_migrated'] += 1
            results['entries_created'] += 2  # Inventory + Payable
            
            if results['purchase_bills_migrated'] % 10 == 0:
                print(f"  ✓ Migrated {results['purchase_bills_migrated']} purchase bills...")
        
        print(f"✅ Migrated {results['purchase_bills_migrated']} purchase bills")
        
        # ═══════════════════════════════════════════════════════════════════
        # STEP 2: Migrate Invoices (with COGS calculation)
        # ═══════════════════════════════════════════════════════════════════
        
        print("\n📄 Step 2: Migrating Invoices (with COGS)...")
        
        # Find invoices that don't have accounting entries yet
        invoices = db.session.execute(text("""
            SELECT DISTINCT i.id, i.tenant_id, i.invoice_number, i.customer_name,
                   i.invoice_date, i.total_amount, i.paid_amount, i.payment_status
            FROM invoices i
            WHERE NOT EXISTS (
                SELECT 1 FROM account_transactions
                WHERE reference_type = 'invoice'
                AND reference_id = i.id
                AND transaction_type IN ('sales_income', 'cogs')
            )
            ORDER BY i.invoice_date, i.id
        """)).fetchall()
        
        for invoice in invoices:
            invoice_id = invoice[0]
            tenant_id = invoice[1]
            invoice_number = invoice[2]
            customer_name = invoice[3]
            invoice_date = invoice[4]
            total_amount = Decimal(str(invoice[5]))
            paid_amount = Decimal(str(invoice[6] or 0))
            payment_status = invoice[7]
            
            # Calculate COGS for this invoice
            invoice_items = db.session.execute(text("""
                SELECT ii.item_id, ii.quantity
                FROM invoice_items ii
                WHERE ii.invoice_id = :invoice_id
                AND ii.item_id IS NOT NULL
            """), {'invoice_id': invoice_id}).fetchall()
            
            cogs_total = Decimal('0')
            for item_row in invoice_items:
                item_id = item_row[0]
                quantity = Decimal(str(item_row[1]))
                
                # Get item cost price
                item = Item.query.filter_by(id=item_id, tenant_id=tenant_id).first()
                if item and item.cost_price:
                    item_cogs = Decimal(str(item.cost_price)) * quantity
                    cogs_total += item_cogs
            
            # Entry 1: DEBIT Accounts Receivable (for unpaid/partial) OR skip (for paid - handled in step 3)
            if payment_status in ['unpaid', 'partial']:
                unpaid_amount = total_amount - paid_amount
                db.session.execute(text("""
                    INSERT INTO account_transactions
                    (tenant_id, account_id, transaction_date, transaction_type,
                     debit_amount, credit_amount, balance_after, reference_type, reference_id,
                     voucher_number, narration, created_at, created_by)
                    VALUES (:tenant_id, NULL, :transaction_date, 'accounts_receivable',
                            :debit_amount, 0.00, :debit_amount, 'invoice', :invoice_id,
                            :voucher, :narration, :created_at, NULL)
                """), {
                    'tenant_id': tenant_id,
                    'transaction_date': invoice_date,
                    'debit_amount': float(unpaid_amount),
                    'invoice_id': invoice_id,
                    'voucher': invoice_number,
                    'narration': f'[MIGRATED] Receivable from {customer_name} - {invoice_number}',
                    'created_at': now
                })
                results['entries_created'] += 1
            
            # Entry 2: CREDIT Sales Income
            db.session.execute(text("""
                INSERT INTO account_transactions
                (tenant_id, account_id, transaction_date, transaction_type,
                 debit_amount, credit_amount, balance_after, reference_type, reference_id,
                 voucher_number, narration, created_at, created_by)
                VALUES (:tenant_id, NULL, :transaction_date, 'sales_income',
                        0.00, :credit_amount, :credit_amount, 'invoice', :invoice_id,
                        :voucher, :narration, :created_at, NULL)
            """), {
                'tenant_id': tenant_id,
                'transaction_date': invoice_date,
                'credit_amount': float(total_amount),
                'invoice_id': invoice_id,
                'voucher': invoice_number,
                'narration': f'[MIGRATED] Sales income from {customer_name} - {invoice_number}',
                'created_at': now
            })
            
            # Entry 3: DEBIT COGS (if calculated)
            if cogs_total > 0:
                db.session.execute(text("""
                    INSERT INTO account_transactions
                    (tenant_id, account_id, transaction_date, transaction_type,
                     debit_amount, credit_amount, balance_after, reference_type, reference_id,
                     voucher_number, narration, created_at, created_by)
                    VALUES (:tenant_id, NULL, :transaction_date, 'cogs',
                            :debit_amount, 0.00, :debit_amount, 'invoice', :invoice_id,
                            :voucher, :narration, :created_at, NULL)
                """), {
                    'tenant_id': tenant_id,
                    'transaction_date': invoice_date,
                    'debit_amount': float(cogs_total),
                    'invoice_id': invoice_id,
                    'voucher': invoice_number,
                    'narration': f'[MIGRATED] COGS for {invoice_number}',
                    'created_at': now
                })
                
                # Entry 4: CREDIT Inventory
                db.session.execute(text("""
                    INSERT INTO account_transactions
                    (tenant_id, account_id, transaction_date, transaction_type,
                     debit_amount, credit_amount, balance_after, reference_type, reference_id,
                     voucher_number, narration, created_at, created_by)
                    VALUES (:tenant_id, NULL, :transaction_date, 'inventory_sale',
                            0.00, :credit_amount, 0.00, 'invoice', :invoice_id,
                            :voucher, :narration, :created_at, NULL)
                """), {
                    'tenant_id': tenant_id,
                    'transaction_date': invoice_date,
                    'credit_amount': float(cogs_total),
                    'invoice_id': invoice_id,
                    'voucher': invoice_number,
                    'narration': f'[MIGRATED] Inventory reduction for {invoice_number}',
                    'created_at': now
                })
                
                results['entries_created'] += 2  # COGS + Inventory
            
            results['invoices_migrated'] += 1
            results['entries_created'] += 1  # Sales Income (Receivable counted above)
            
            if results['invoices_migrated'] % 10 == 0:
                print(f"  ✓ Migrated {results['invoices_migrated']} invoices...")
        
        print(f"✅ Migrated {results['invoices_migrated']} invoices")
        
        # ═══════════════════════════════════════════════════════════════════
        # STEP 3: Migrate Expenses
        # ═══════════════════════════════════════════════════════════════════
        
        print("\n💰 Step 3: Migrating Expenses...")
        
        # Find expenses that don't have the DEBIT side yet
        expenses = db.session.execute(text("""
            SELECT DISTINCT e.id, e.tenant_id, e.expense_date, e.amount, 
                   e.category_id, e.description, e.vendor_name
            FROM expenses e
            WHERE NOT EXISTS (
                SELECT 1 FROM account_transactions
                WHERE reference_type = 'expense'
                AND reference_id = e.id
                AND transaction_type = 'operating_expense'
            )
            ORDER BY e.expense_date, e.id
        """)).fetchall()
        
        for expense in expenses:
            expense_id = expense[0]
            tenant_id = expense[1]
            expense_date = expense[2]
            amount = Decimal(str(expense[3]))
            category_id = expense[4]
            description = expense[5] or 'Expense'
            vendor_name = expense[6] or 'Business Expense'
            
            # Get category name
            category_name = 'General Expenses'
            if category_id:
                category = ExpenseCategory.query.get(category_id)
                if category:
                    category_name = category.name
            
            # Entry: DEBIT Operating Expense (Credit side already exists)
            db.session.execute(text("""
                INSERT INTO account_transactions
                (tenant_id, account_id, transaction_date, transaction_type,
                 debit_amount, credit_amount, balance_after, reference_type, reference_id,
                 voucher_number, narration, created_at, created_by)
                VALUES (:tenant_id, NULL, :transaction_date, 'operating_expense',
                        :debit, 0.00, :debit, 'expense', :expense_id,
                        :voucher, :narration, :created_at, NULL)
            """), {
                'tenant_id': tenant_id,
                'transaction_date': expense_date,
                'debit': float(amount),
                'expense_id': expense_id,
                'voucher': f'EXP-{expense_id}',
                'narration': f'[MIGRATED] {category_name}: {description[:80]}',
                'created_at': now
            })
            
            results['expenses_migrated'] += 1
            results['entries_created'] += 1
            
            if results['expenses_migrated'] % 10 == 0:
                print(f"  ✓ Migrated {results['expenses_migrated']} expenses...")
        
        print(f"✅ Migrated {results['expenses_migrated']} expenses")
        
        # ═══════════════════════════════════════════════════════════════════
        # STEP 4: Migrate Salary Payments
        # ═══════════════════════════════════════════════════════════════════
        
        print("\n👥 Step 4: Migrating Salary Payments...")
        
        # Find salary payments that don't have the DEBIT side yet
        salary_payments = db.session.execute(text("""
            SELECT DISTINCT at.tenant_id, at.transaction_date, at.credit_amount,
                   at.voucher_number, at.narration, at.reference_id
            FROM account_transactions at
            WHERE at.transaction_type = 'salary_payment'
            AND NOT EXISTS (
                SELECT 1 FROM account_transactions at2
                WHERE at2.reference_type = 'payroll'
                AND at2.reference_id = at.reference_id
                AND at2.transaction_type = 'salary_expense'
            )
            ORDER BY at.transaction_date
        """)).fetchall()
        
        for payment in salary_payments:
            tenant_id = payment[0]
            payment_date = payment[1]
            amount = Decimal(str(payment[2]))
            voucher = payment[3]
            narration = payment[4]
            payroll_id = payment[5]
            
            # Entry: DEBIT Salary Expense (Credit side already exists)
            db.session.execute(text("""
                INSERT INTO account_transactions
                (tenant_id, account_id, transaction_date, transaction_type,
                 debit_amount, credit_amount, balance_after, reference_type, reference_id,
                 voucher_number, narration, created_at, created_by)
                VALUES (:tenant_id, NULL, :transaction_date, 'salary_expense',
                        :debit, 0.00, :debit, 'payroll', :payroll_id,
                        :voucher, :narration, :created_at, NULL)
            """), {
                'tenant_id': tenant_id,
                'transaction_date': payment_date,
                'debit': float(amount),
                'payroll_id': payroll_id,
                'voucher': voucher,
                'narration': f'[MIGRATED] {narration}',
                'created_at': now
            })
            
            results['salary_payments_migrated'] += 1
            results['entries_created'] += 1
            
            if results['salary_payments_migrated'] % 10 == 0:
                print(f"  ✓ Migrated {results['salary_payments_migrated']} salary payments...")
        
        print(f"✅ Migrated {results['salary_payments_migrated']} salary payments")
        
        # Commit all changes
        db.session.commit()
        
        print("\n" + "=" * 80)
        print("🎉 MIGRATION COMPLETE!")
        print("=" * 80)
        print(f"✅ Purchase Bills Migrated: {results['purchase_bills_migrated']}")
        print(f"✅ Invoices Migrated: {results['invoices_migrated']}")
        print(f"✅ Expenses Migrated: {results['expenses_migrated']}")
        print(f"✅ Salary Payments Migrated: {results['salary_payments_migrated']}")
        print(f"✅ Total Accounting Entries Created: {results['entries_created']}")
        print("=" * 80)
        
        return jsonify({
            'status': 'success',
            'message': 'Successfully migrated to double-entry accounting',
            'results': results
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'status': 'error',
            'message': str(e),
            'results': results
        }), 500

