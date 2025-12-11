# 📐 Full Double-Entry Accounting - Technical Specification

**Branch:** `feature/full-double-entry-accounting`  
**Target:** Professional-grade accounting system  
**Timeline:** 3-4 days  
**Status:** 🔧 In Progress

---

## 🎯 **OBJECTIVES:**

Transform BizBooks from cash-based to full accrual-based double-entry accounting system.

### **Success Criteria:**
- ✅ Every transaction creates balanced debit/credit entries
- ✅ Trial Balance remains balanced after ANY transaction
- ✅ Automatic COGS (Cost of Goods Sold) calculation
- ✅ Accurate Profit & Loss reports
- ✅ Professional-grade Balance Sheet
- ✅ Receivables & Payables tracking
- ✅ All existing data migrated correctly

---

## 📊 **ACCOUNTING STRUCTURE:**

### **Account Types in Trial Balance:**

```
ASSETS (Normal Balance: DEBIT)
├─ Current Assets
│  ├─ Cash & Bank Accounts
│  ├─ Accounts Receivable
│  └─ Inventory (Stock on Hand)
└─ Fixed Assets (Future)

LIABILITIES (Normal Balance: CREDIT)
├─ Current Liabilities
│  └─ Accounts Payable
└─ Long-term Liabilities (Future)

EQUITY (Normal Balance: CREDIT)
├─ Owner's Capital
└─ Retained Earnings

INCOME (Normal Balance: CREDIT)
└─ Sales Income

EXPENSES (Normal Balance: DEBIT)
├─ Cost of Goods Sold (COGS)
├─ Operating Expenses
├─ Employee Salaries
└─ Other Expenses
```

---

## 🔧 **IMPLEMENTATION DETAILS:**

### **1. PURCHASE BILLS** (Priority: HIGH)

#### **Current Flow:**
```python
# When purchase bill is created:
1. Create purchase_bills record ✅
2. Create purchase_bill_items records ✅
3. Update item_stocks.quantity_available ✅
4. Update item_stocks.stock_value ✅
5. NO accounting entry ❌

# When payment is made:
1. Update purchase_bill.paid_amount ✅
2. Create account_transaction:
   - CREDIT: Cash/Bank ✅
   - DEBIT: ??? (Missing!) ❌
```

#### **New Flow:**
```python
# When purchase bill is CREATED (even if unpaid):
1. Create purchase_bills record
2. Create purchase_bill_items records
3. Update item_stocks.quantity_available
4. Update item_stocks.stock_value
5. CREATE ACCOUNTING ENTRIES:
   - DEBIT: Inventory (Asset)           [bill_total]
   - CREDIT: Accounts Payable (Liability) [bill_total]

# When payment is MADE:
1. Update purchase_bill.paid_amount
2. CREATE ACCOUNTING ENTRIES:
   - DEBIT: Accounts Payable (Liability)  [payment_amount]
   - CREDIT: Cash/Bank (Asset)            [payment_amount]
```

#### **Code Changes:**

**File:** `modular_app/routes/purchase_bills.py`

**Function:** `create_bill()` (around line 100)

**Add after bill creation:**
```python
# Create double-entry accounting entries
from decimal import Decimal
from datetime import datetime
import pytz

ist = pytz.timezone('Asia/Kolkata')
now = datetime.now(ist)

# Entry 1: DEBIT Inventory (increase asset)
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
    'transaction_date': bill.bill_date,
    'debit_amount': float(bill.total_amount),
    'bill_id': bill.id,
    'voucher': bill.bill_number,
    'narration': f'Inventory purchase from {bill.vendor_name} - {bill.bill_number}',
    'created_at': now
})

# Entry 2: CREDIT Accounts Payable (increase liability)
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
    'transaction_date': bill.bill_date,
    'credit_amount': float(bill.total_amount),
    'bill_id': bill.id,
    'voucher': bill.bill_number,
    'narration': f'Payable to {bill.vendor_name} - {bill.bill_number}',
    'created_at': now
})
```

**Function:** `record_payment_form()` (around line 850)

**Update payment logic:**
```python
# Entry 1: DEBIT Accounts Payable (decrease liability)
db.session.execute(text("""
    INSERT INTO account_transactions
    (tenant_id, account_id, transaction_date, transaction_type,
     debit_amount, credit_amount, balance_after, reference_type, reference_id,
     voucher_number, narration, created_at, created_by)
    VALUES (:tenant_id, NULL, :transaction_date, 'accounts_payable_payment',
            :debit_amount, 0.00, 0.00, 'vendor_payment', :payment_id,
            :voucher, :narration, :created_at, NULL)
"""), {
    'tenant_id': tenant_id,
    'transaction_date': payment_date,
    'debit_amount': float(amount),
    'payment_id': payment.id,
    'voucher': payment.payment_number,
    'narration': f'Payment to {bill.vendor_name} for {bill.bill_number}',
    'created_at': now
})

# Entry 2: CREDIT Cash/Bank (already exists, just update narration)
# ... existing code ...
```

---

### **2. SALES / INVOICES** (Priority: HIGH)

#### **Current Flow:**
```python
# When invoice is created:
1. Create invoices record ✅
2. Create invoice_items records ✅
3. Deduct from item_stocks.quantity_available ✅
4. Update item_stocks.stock_value ✅
5. NO accounting entry for SALE ❌
6. NO accounting entry for COGS ❌

# When payment is received:
1. Update invoice.paid_amount ✅
2. Create account_transaction:
   - DEBIT: Cash/Bank ✅
   - CREDIT: ??? (Missing!) ❌
```

#### **New Flow:**
```python
# When invoice is CREATED (even if unpaid):
1. Create invoices record
2. Create invoice_items records
3. Deduct from item_stocks.quantity_available
4. Update item_stocks.stock_value
5. Calculate COGS (Cost of Goods Sold)
6. CREATE ACCOUNTING ENTRIES (4 entries!):
   
   # Record the sale:
   - DEBIT: Accounts Receivable (Asset) OR Cash [invoice_total]
   - CREDIT: Sales Income (Income)              [invoice_total]
   
   # Record the cost:
   - DEBIT: Cost of Goods Sold (Expense)        [cogs_total]
   - CREDIT: Inventory (Asset)                  [cogs_total]

# When payment is RECEIVED (if not cash sale):
1. Update invoice.paid_amount
2. CREATE ACCOUNTING ENTRIES:
   - DEBIT: Cash/Bank (Asset)             [payment_amount]
   - CREDIT: Accounts Receivable (Asset)  [payment_amount]
```

#### **Code Changes:**

**File:** `modular_app/routes/invoices.py`

**Function:** `create()` (around line 200)

**Add COGS calculation function:**
```python
def calculate_cogs_for_invoice(invoice_items, tenant_id):
    """
    Calculate Cost of Goods Sold for invoice items
    Uses FIFO (First In, First Out) method
    """
    from sqlalchemy import text
    from decimal import Decimal
    
    total_cogs = Decimal('0')
    
    for item in invoice_items:
        # Get item's cost price
        item_obj = Item.query.filter_by(
            id=item.item_id,
            tenant_id=tenant_id
        ).first()
        
        if item_obj and item_obj.cost_price:
            item_cogs = Decimal(str(item_obj.cost_price)) * Decimal(str(item.quantity))
            total_cogs += item_cogs
    
    return total_cogs
```

**Add after invoice creation:**
```python
# Calculate COGS
cogs_total = calculate_cogs_for_invoice(invoice.items, tenant_id)

# Entry 1: DEBIT Accounts Receivable or Cash (increase asset)
receivable_account = 'Cash' if invoice.payment_status == 'paid' else 'Accounts Receivable'

db.session.execute(text("""
    INSERT INTO account_transactions
    (tenant_id, account_id, transaction_date, transaction_type,
     debit_amount, credit_amount, balance_after, reference_type, reference_id,
     voucher_number, narration, created_at, created_by)
    VALUES (:tenant_id, :account_id, :transaction_date, :transaction_type,
            :debit_amount, 0.00, :debit_amount, 'invoice', :invoice_id,
            :voucher, :narration, :created_at, NULL)
"""), {
    'tenant_id': tenant_id,
    'account_id': account_id if invoice.payment_status == 'paid' else None,
    'transaction_date': invoice.invoice_date,
    'transaction_type': 'invoice_sale' if invoice.payment_status == 'paid' else 'accounts_receivable',
    'debit_amount': float(invoice.total_amount),
    'invoice_id': invoice.id,
    'voucher': invoice.invoice_number,
    'narration': f'Sale to {invoice.customer_name} - {invoice.invoice_number}',
    'created_at': now
})

# Entry 2: CREDIT Sales Income (increase income)
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
    'transaction_date': invoice.invoice_date,
    'credit_amount': float(invoice.total_amount),
    'invoice_id': invoice.id,
    'voucher': invoice.invoice_number,
    'narration': f'Sales income from {invoice.customer_name} - {invoice.invoice_number}',
    'created_at': now
})

# Entry 3: DEBIT Cost of Goods Sold (increase expense)
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
    'transaction_date': invoice.invoice_date,
    'debit_amount': float(cogs_total),
    'invoice_id': invoice.id,
    'voucher': invoice.invoice_number,
    'narration': f'COGS for {invoice.invoice_number}',
    'created_at': now
})

# Entry 4: CREDIT Inventory (decrease asset)
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
    'transaction_date': invoice.invoice_date,
    'credit_amount': float(cogs_total),
    'invoice_id': invoice.id,
    'voucher': invoice.invoice_number,
    'narration': f'Inventory reduction for {invoice.invoice_number}',
    'created_at': now
})
```

---

### **3. TRIAL BALANCE UPDATES** (Priority: HIGH)

**File:** `modular_app/routes/accounts.py`

**Function:** `trial_balance()` (around line 1870)

**Add new account types:**

```python
# After existing assets section, add:

# 4. Accounts Receivable (Assets - Debit Balance)
receivables_from_transactions = db.session.execute(text("""
    SELECT COALESCE(SUM(debit_amount - credit_amount), 0)
    FROM account_transactions
    WHERE tenant_id = :tenant_id
    AND transaction_type IN ('accounts_receivable', 'accounts_receivable_payment')
    AND transaction_date <= :as_of_date
"""), {'tenant_id': tenant_id, 'as_of_date': as_of_date}).fetchone()[0]

receivables_total = Decimal(str(receivables_from_transactions))

if receivables_total > 0:
    accounts.append({
        'account_name': 'Accounts Receivable (Customers)',
        'category': 'Assets',
        'debit': receivables_total,
        'credit': Decimal('0')
    })

# In Liabilities section, add:

# 5. Accounts Payable (Liabilities - Credit Balance)
payables_from_transactions = db.session.execute(text("""
    SELECT COALESCE(SUM(credit_amount - debit_amount), 0)
    FROM account_transactions
    WHERE tenant_id = :tenant_id
    AND transaction_type IN ('accounts_payable', 'accounts_payable_payment')
    AND transaction_date <= :as_of_date
"""), {'tenant_id': tenant_id, 'as_of_date': as_of_date}).fetchone()[0]

payables_total = Decimal(str(payables_from_transactions))

if payables_total > 0:
    accounts.append({
        'account_name': 'Accounts Payable (Vendors)',
        'category': 'Liabilities',
        'debit': Decimal('0'),
        'credit': payables_total
    })

# In Income section, add:

# 6. Sales Income (Income - Credit Balance)
sales_income = db.session.execute(text("""
    SELECT COALESCE(SUM(credit_amount), 0)
    FROM account_transactions
    WHERE tenant_id = :tenant_id
    AND transaction_type = 'sales_income'
    AND transaction_date <= :as_of_date
"""), {'tenant_id': tenant_id, 'as_of_date': as_of_date}).fetchone()[0]

sales_income_total = Decimal(str(sales_income))

if sales_income_total > 0:
    accounts.append({
        'account_name': 'Sales Income',
        'category': 'Income',
        'debit': Decimal('0'),
        'credit': sales_income_total
    })

# In Expenses section, add:

# 7. Cost of Goods Sold (Expenses - Debit Balance)
cogs = db.session.execute(text("""
    SELECT COALESCE(SUM(debit_amount), 0)
    FROM account_transactions
    WHERE tenant_id = :tenant_id
    AND transaction_type = 'cogs'
    AND transaction_date <= :as_of_date
"""), {'tenant_id': tenant_id, 'as_of_date': as_of_date}).fetchone()[0]

cogs_total = Decimal(str(cogs))

if cogs_total > 0:
    accounts.append({
        'account_name': 'Cost of Goods Sold (COGS)',
        'category': 'Expenses',
        'debit': cogs_total,
        'credit': Decimal('0')
    })

# 8. Inventory adjustments from sales/purchases
inventory_changes = db.session.execute(text("""
    SELECT 
        SUM(debit_amount) - SUM(credit_amount) as net_change
    FROM account_transactions
    WHERE tenant_id = :tenant_id
    AND transaction_type IN ('inventory_purchase', 'inventory_sale')
    AND transaction_date <= :as_of_date
"""), {'tenant_id': tenant_id, 'as_of_date': as_of_date}).fetchone()[0] or Decimal('0')

# This will be combined with opening inventory to show total inventory in assets
```

---

### **4. DATA MIGRATION** (Priority: HIGH)

**File:** `modular_app/routes/migration_double_entry.py` (NEW FILE)

Create migration to fix existing data:

```python
"""
Migrate existing purchase bills and invoices to double-entry system
This is a ONE-TIME migration for existing data
"""

from flask import Blueprint, jsonify
from models import db
from sqlalchemy import text
from datetime import datetime
import pytz
from decimal import Decimal

migration_double_entry_bp = Blueprint('migration_double_entry', __name__, url_prefix='/migration')


@migration_double_entry_bp.route('/migrate-to-double-entry')
def migrate_to_double_entry():
    """
    Migrate existing purchase bills and invoices to create missing accounting entries
    
    WARNING: This is a ONE-TIME migration!
    Only run this ONCE after deploying double-entry system.
    """
    
    try:
        ist = pytz.timezone('Asia/Kolkata')
        now = datetime.now(ist)
        
        print("\n" + "=" * 80)
        print("🔄 MIGRATING TO DOUBLE-ENTRY ACCOUNTING SYSTEM")
        print("=" * 80)
        
        results = {
            'purchase_bills_migrated': 0,
            'invoices_migrated': 0,
            'entries_created': 0,
            'errors': []
        }
        
        # Step 1: Migrate Purchase Bills
        print("\n📦 Step 1: Migrating Purchase Bills...")
        
        purchase_bills = db.session.execute(text("""
            SELECT id, tenant_id, bill_number, vendor_name, bill_date, total_amount, paid_amount
            FROM purchase_bills
            WHERE id NOT IN (
                SELECT DISTINCT reference_id 
                FROM account_transactions 
                WHERE reference_type = 'purchase_bill' 
                AND transaction_type IN ('inventory_purchase', 'accounts_payable')
            )
            ORDER BY bill_date, id
        """)).fetchall()
        
        for bill in purchase_bills:
            # Create entries for this bill
            # ... (full implementation in actual migration file)
            
        # Step 2: Migrate Invoices
        print("\n📄 Step 2: Migrating Invoices...")
        
        invoices = db.session.execute(text("""
            SELECT id, tenant_id, invoice_number, customer_name, invoice_date, total_amount, paid_amount
            FROM invoices
            WHERE id NOT IN (
                SELECT DISTINCT reference_id 
                FROM account_transactions 
                WHERE reference_type = 'invoice' 
                AND transaction_type IN ('sales_income', 'cogs')
            )
            ORDER BY invoice_date, id
        """)).fetchall()
        
        for invoice in invoices:
            # Calculate COGS
            # Create 4 accounting entries
            # ... (full implementation)
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Successfully migrated to double-entry accounting',
            'results': results
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
```

---

## 🧪 **TESTING PLAN:**

### **Test Scenarios:**

1. **New Purchase Bill (Unpaid):**
   - Create bill for ₹10,000
   - Verify:
     - Trial Balance increases Inventory by ₹10,000 (debit)
     - Trial Balance increases Payables by ₹10,000 (credit)
     - Still balanced

2. **Pay Purchase Bill:**
   - Pay ₹10,000 to vendor
   - Verify:
     - Trial Balance decreases Cash by ₹10,000 (credit)
     - Trial Balance decreases Payables by ₹10,000 (debit)
     - Still balanced

3. **New Invoice (Cash Sale):**
   - Sell for ₹15,000 (cost ₹8,000)
   - Verify:
     - Trial Balance increases Cash by ₹15,000 (debit)
     - Trial Balance increases Sales by ₹15,000 (credit)
     - Trial Balance increases COGS by ₹8,000 (debit)
     - Trial Balance decreases Inventory by ₹8,000 (credit)
     - Still balanced
     - Profit = ₹15,000 - ₹8,000 = ₹7,000

4. **New Invoice (Credit Sale):**
   - Sell for ₹20,000 (cost ₹12,000), customer pays later
   - Verify:
     - Trial Balance increases Receivables by ₹20,000 (debit)
     - Trial Balance increases Sales by ₹20,000 (credit)
     - Trial Balance increases COGS by ₹12,000 (debit)
     - Trial Balance decreases Inventory by ₹12,000 (credit)
     - Still balanced

5. **Receive Payment for Credit Sale:**
   - Receive ₹20,000 from customer
   - Verify:
     - Trial Balance increases Cash by ₹20,000 (debit)
     - Trial Balance decreases Receivables by ₹20,000 (credit)
     - Still balanced

---

## 📅 **IMPLEMENTATION SCHEDULE:**

### **Day 1: Purchase Bills** (6-8 hours)
- [ ] Morning: Update purchase_bills.py for double-entry
- [ ] Afternoon: Add accounts payable to Trial Balance
- [ ] Evening: Test purchase scenarios
- [ ] Commit: "feat: Purchase bills with full double-entry"

### **Day 2: Sales & COGS** (6-8 hours)
- [ ] Morning: Implement COGS calculation
- [ ] Afternoon: Update invoices.py for double-entry
- [ ] Evening: Test sales scenarios
- [ ] Commit: "feat: Sales with COGS and double-entry"

### **Day 3: Receivables & Testing** (6-8 hours)
- [ ] Morning: Add receivables/payables to Trial Balance
- [ ] Afternoon: Comprehensive testing
- [ ] Evening: Fix any issues
- [ ] Commit: "feat: Complete double-entry with receivables/payables"

### **Day 4: Migration & Deployment** (4-6 hours)
- [ ] Morning: Create data migration script
- [ ] Afternoon: Test migration on development data
- [ ] Evening: Merge to main, deploy
- [ ] Commit: "feat: Data migration for double-entry system"

---

## ✅ **ACCEPTANCE CRITERIA:**

- [ ] Every purchase bill creates 2 accounting entries
- [ ] Every invoice creates 4 accounting entries
- [ ] Trial Balance always balanced after ANY transaction
- [ ] COGS calculated correctly
- [ ] Profit & Loss report accurate
- [ ] All existing data migrated
- [ ] No production downtime during deployment
- [ ] User documentation updated
- [ ] Admin guide updated

---

## 🚀 **DEPLOYMENT STRATEGY:**

### **Step 1: Test on Feature Branch**
- Implement all changes
- Test thoroughly with Ayushi's data
- Verify Trial Balance remains balanced

### **Step 2: Merge to Main**
```bash
git checkout main
git merge feature/full-double-entry-accounting
git push origin main
```

### **Step 3: Run Migration**
Visit: `/migration/migrate-to-double-entry`

### **Step 4: Verify Production**
- Check Trial Balance for all tenants
- Verify existing invoices/bills
- Create test transactions
- Monitor for 24 hours

---

## 📞 **SUPPORT PLAN:**

### **Before Deployment:**
- Backup all data (Supabase backup)
- Notify key users (Mahaveer, Ayushi)
- Schedule during low-traffic time

### **After Deployment:**
- Monitor error logs
- Check Trial Balance for all tenants
- Quick rollback plan if needed
- User training materials ready

---

**Created:** December 11, 2025  
**Branch:** `feature/full-double-entry-accounting`  
**Status:** 🔧 Ready to implement  
**Est. Completion:** December 14-15, 2025

