# 📊 Accounting & Contra Module - Feature Roadmap

## ✅ COMPLETED FEATURES (Phases 1-5 Partial)

### Phase 1: Bank/Cash Account Management ✅ COMPLETE
- ✅ Create multiple bank/cash accounts
- ✅ Opening balance management
- ✅ Current balance tracking
- ✅ Default "Cash in Hand" account
- ✅ Non-default accounts (Silak Nandu, Bank HDFC, etc.)
- ✅ Delete non-default accounts
- ✅ Edit account details
- ✅ Account statement view (Tally-style)

### Phase 2: Contra Vouchers ✅ COMPLETE
- ✅ Internal fund transfers (Cash → Bank, Bank → Bank, Cash → Cash)
- ✅ Auto-voucher numbering (CONTRA-0001, CONTRA-0002, etc.)
- ✅ Two-sided ledger entries (Debit/Credit)
- ✅ Transaction history with search/filter
- ✅ Contra voucher details view

### Phase 3: Employee Cash Advances ✅ COMPLETE
- ✅ Give cash to employees (Cash Advance)
- ✅ Record employee expenses (with expense heads)
- ✅ Return cash from employees
- ✅ Employee cash ledger (Tally-style format)
- ✅ Auto-voucher numbering (EMP-ADV-0001, EMP-EXP-0001, RET-0001)
- ✅ Balance tracking per employee
- ✅ Opening/Current/Closing balance display

### Phase 4: Integration with Existing Features ✅ COMPLETE
- ✅ Invoice payments linked to Bank/Cash accounts
- ✅ Purchase bill payments linked to accounts
- ✅ General expenses linked to accounts
- ✅ Automatic ledger entries for all transactions
- ✅ "Pay From Account" / "Deposit To Account" dropdowns
- ✅ Real-time balance updates
- ✅ Double-entry bookkeeping for all transactions

### Phase 5: Accounting Reports ⚠️ PARTIALLY COMPLETE
- ✅ **Cash Book** - All cash transactions with opening/closing balance (Tally-style)
- ✅ **Bank Book** - Bank account transactions with balance tracking (Tally-style)
- ✅ **Day Book** - All transactions across all accounts (daily summary)
- ✅ **Account Summary** - Overview of all accounts with balances
- ❌ **Balance Sheet** - NOT YET IMPLEMENTED
- ❌ **Profit & Loss Statement** - NOT YET IMPLEMENTED
- ❌ **Trial Balance** - NOT YET IMPLEMENTED

---

## ❌ PENDING FEATURES (Priority Order)

### 🔥 PRIORITY 1: Complete Phase 5 Reports

#### 1. Balance Sheet ❌ NOT IMPLEMENTED
**Purpose:** Shows financial position (Assets vs. Liabilities) as of a specific date

**Components:**
```
BALANCE SHEET
As on: [Date]

ASSETS
├── Current Assets
│   ├── Cash & Bank Accounts
│   │   ├── Cash in Hand: ₹52,150
│   │   ├── Bank HDFC: ₹58,650
│   │   └── Silak Nandu: ₹16,000
│   ├── Accounts Receivable (Unpaid Invoices): ₹XX,XXX
│   ├── Inventory/Stock: ₹XX,XXX
│   └── Total Current Assets: ₹XX,XXX
├── Fixed Assets
│   ├── Machinery & Equipment: ₹XX,XXX
│   ├── Furniture & Fixtures: ₹XX,XXX
│   └── Total Fixed Assets: ₹XX,XXX
└── TOTAL ASSETS: ₹XX,XXX

LIABILITIES
├── Current Liabilities
│   ├── Accounts Payable (Unpaid Bills): ₹XX,XXX
│   ├── Outstanding Expenses: ₹XX,XXX
│   ├── Employee Advances (if negative): ₹XX,XXX
│   └── Total Current Liabilities: ₹XX,XXX
├── Long-term Liabilities
│   ├── Loans: ₹XX,XXX
│   └── Total Long-term Liabilities: ₹XX,XXX
└── TOTAL LIABILITIES: ₹XX,XXX

EQUITY
├── Owner's Capital: ₹XX,XXX
├── Retained Earnings: ₹XX,XXX
└── TOTAL EQUITY: ₹XX,XXX

═══════════════════════════════════════
TOTAL LIABILITIES + EQUITY: ₹XX,XXX
(Should equal TOTAL ASSETS)
```

**Data Sources:**
- Cash & Bank: `bank_accounts` table
- Receivables: `invoices` where `payment_status != 'paid'`
- Inventory: `materials` and `items` tables
- Payables: `purchase_bills` where `payment_status != 'paid'`
- Employee Advances: `employee_cash` with negative balances

---

#### 2. Profit & Loss Statement ❌ NOT IMPLEMENTED
**Purpose:** Shows profitability (Income - Expenses) for a period

**Components:**
```
PROFIT & LOSS STATEMENT
Period: [Start Date] to [End Date]

INCOME
├── Sales Revenue
│   ├── Total Invoices (Paid): ₹XX,XXX
│   ├── Total Invoices (Pending): ₹XX,XXX
│   └── Total Sales: ₹XX,XXX
├── Other Income: ₹XX,XXX
└── TOTAL INCOME: ₹XX,XXX

EXPENSES
├── Cost of Goods Sold (COGS)
│   ├── Purchase Bills: ₹XX,XXX
│   ├── Materials: ₹XX,XXX
│   └── Total COGS: ₹XX,XXX
├── Operating Expenses
│   ├── Employee Expenses: ₹XX,XXX
│   ├── General Expenses: ₹XX,XXX
│   ├── Rent: ₹XX,XXX
│   ├── Utilities: ₹XX,XXX
│   └── Total Operating Expenses: ₹XX,XXX
└── TOTAL EXPENSES: ₹XX,XXX

═══════════════════════════════════════
GROSS PROFIT: ₹XX,XXX (Income - COGS)
NET PROFIT: ₹XX,XXX (Gross Profit - Operating Expenses)

Profit Margin: XX.XX%
```

**Data Sources:**
- Sales: `invoices` table (filter by date range)
- Purchases: `purchase_bills` table (filter by date range)
- Expenses: `expenses` table + `account_transactions` with `transaction_type = 'expense'`

---

#### 3. Trial Balance ❌ NOT IMPLEMENTED
**Purpose:** Verifies double-entry bookkeeping accuracy (Total Debits = Total Credits)

**Components:**
```
TRIAL BALANCE
As on: [Date]

ACCOUNT NAME                  | DEBIT      | CREDIT
══════════════════════════════╪════════════╪════════════
ASSETS
Cash in Hand                  | 52,150.00  |
Bank HDFC                     | 58,650.00  |
Silak Nandu                   | 16,000.00  |
Accounts Receivable           | XX,XXX.00  |
Inventory                     | XX,XXX.00  |
──────────────────────────────┼────────────┼────────────
LIABILITIES
Accounts Payable              |            | XX,XXX.00
Outstanding Expenses          |            | XX,XXX.00
──────────────────────────────┼────────────┼────────────
INCOME
Sales Revenue                 |            | XX,XXX.00
Other Income                  |            | XX,XXX.00
──────────────────────────────┼────────────┼────────────
EXPENSES
Purchase Expenses             | XX,XXX.00  |
Operating Expenses            | XX,XXX.00  |
Employee Expenses             | XX,XXX.00  |
══════════════════════════════╪════════════╪════════════
TOTAL                         | XX,XXX.00  | XX,XXX.00
                              ↑ Should be EQUAL ↑
```

**Data Sources:**
- All accounts from `bank_accounts`
- All transactions from `account_transactions`
- Summarize debits and credits for each account head
- Verify: SUM(Debits) = SUM(Credits)

---

### 🔶 PRIORITY 2: Business Intelligence Reports

#### 4. Receivables (Debtors) Aging Report ❌ NOT IMPLEMENTED
**Purpose:** Track outstanding customer payments, identify overdue invoices

**Components:**
```
RECEIVABLES AGING REPORT
As on: [Date]

CUSTOMER NAME    | TOTAL DUE | 0-30 DAYS | 31-60 DAYS | 61-90 DAYS | 90+ DAYS
═════════════════╪═══════════╪═══════════╪════════════╪════════════╪══════════
Rishi Jain       | ₹10,000   | ₹5,000    | ₹3,000     | ₹2,000     | ₹0
Ayushi Samaiya   | ₹5,000    | ₹5,000    | ₹0         | ₹0         | ₹0
Shubham Sethi    | ₹8,000    | ₹0        | ₹0         | ₹0         | ₹8,000 ⚠️
─────────────────┼───────────┼───────────┼────────────┼────────────┼──────────
TOTAL            | ₹23,000   | ₹10,000   | ₹3,000     | ₹2,000     | ₹8,000
```

**Features:**
- Color-coded aging (Green: 0-30, Yellow: 31-60, Orange: 61-90, Red: 90+)
- Click customer → See invoice details
- Send payment reminder emails
- Export to Excel

**Data Sources:**
- `invoices` where `payment_status != 'paid'`
- Calculate days overdue: `CURRENT_DATE - invoice_date`

---

#### 5. Payables (Creditors) Aging Report ❌ NOT IMPLEMENTED
**Purpose:** Track outstanding vendor payments, manage cash flow

**Components:**
```
PAYABLES AGING REPORT
As on: [Date]

VENDOR NAME      | TOTAL DUE | 0-30 DAYS | 31-60 DAYS | 61-90 DAYS | 90+ DAYS
═════════════════╪═══════════╪═══════════╪════════════╪════════════╪══════════
Vendor A         | ₹20,000   | ₹15,000   | ₹5,000     | ₹0         | ₹0
Vendor B         | ₹12,000   | ₹0        | ₹0         | ₹12,000    | ₹0 ⚠️
─────────────────┼───────────┼───────────┼────────────┼────────────┼──────────
TOTAL            | ₹32,000   | ₹15,000   | ₹5,000     | ₹12,000    | ₹0
```

**Features:**
- Payment priority recommendations
- Upcoming due dates
- Available cash vs. upcoming payments
- Vendor payment history

**Data Sources:**
- `purchase_bills` where `payment_status != 'paid'`
- Calculate days overdue: `CURRENT_DATE - bill_date` or `due_date`

---

#### 6. Bank Reconciliation ❌ NOT IMPLEMENTED
**Purpose:** Match bank statements with accounting ledger entries

**Components:**
```
BANK RECONCILIATION
Account: Bank HDFC | Month: November 2025

LEDGER BALANCE (as per books): ₹58,650.00

BANK STATEMENT TRANSACTIONS:
DATE       | DESCRIPTION          | DEBIT    | CREDIT   | ✓ RECONCILED
═══════════╪══════════════════════╪══════════╪══════════╪═════════════
29-Nov-25  | Invoice Payment      |          | 2,150.00 | ✅ Matched
29-Nov-25  | Transfer from Cash   |          | 10,000.00| ✅ Matched
30-Nov-25  | Bank Charges         | 50.00    |          | ❌ Not in ledger
30-Nov-25  | Interest Earned      |          | 125.00   | ❌ Not in ledger

ADJUSTMENTS REQUIRED:
➕ Add: Interest Earned                     + ₹125.00
➖ Less: Bank Charges                       - ₹50.00
══════════════════════════════════════════════════════
ADJUSTED BALANCE (as per bank): ₹58,725.00
```

**Features:**
- Import bank statements (CSV/Excel)
- Auto-match transactions
- Mark transactions as reconciled
- Identify missing/duplicate entries
- One-click adjustment entries

**Data Sources:**
- `account_transactions` for specific bank account
- User-uploaded bank statement file
- Mark reconciled: Add `is_reconciled` boolean field

---

### 🔷 PRIORITY 3: Advanced Accounting Features

#### 7. Financial Year Management ❌ NOT IMPLEMENTED
**Purpose:** Manage year-end closing, comparative reports, opening balances

**Components:**
- **Define Financial Year:**
  - Start Month: April / January / Any
  - End Month: March / December / Any
  - Current FY: 2024-2025
  - Status: Open / Closed

- **Year-End Closing Process:**
  1. Generate closing balances for all accounts
  2. Transfer Net Profit/Loss to Retained Earnings
  3. Lock previous FY (no edits allowed)
  4. Set opening balances for new FY

- **Comparative Reports:**
  - This Year vs. Last Year
  - Month-on-Month comparison
  - Quarter-wise analysis

**Database Schema:**
```sql
CREATE TABLE financial_years (
    id SERIAL PRIMARY KEY,
    tenant_id INT REFERENCES tenants(id),
    fy_name VARCHAR(20),           -- e.g., "2024-2025"
    start_date DATE,
    end_date DATE,
    is_current BOOLEAN DEFAULT TRUE,
    is_locked BOOLEAN DEFAULT FALSE,
    closing_date DATE,
    created_at TIMESTAMP
);
```

---

#### 8. Chart of Accounts ❌ NOT IMPLEMENTED
**Purpose:** Hierarchical organization of all accounts (like Tally's Groups)

**Structure:**
```
PRIMARY GROUPS
├── Assets
│   ├── Current Assets
│   │   ├── Cash & Bank
│   │   │   ├── Cash in Hand (account)
│   │   │   ├── Bank HDFC (account)
│   │   │   └── Silak Nandu (account)
│   │   ├── Sundry Debtors (Receivables)
│   │   │   ├── Rishi Jain (customer)
│   │   │   └── Ayushi Samaiya (customer)
│   │   └── Stock (Inventory)
│   └── Fixed Assets
│       ├── Machinery
│       └── Furniture
│
├── Liabilities
│   ├── Current Liabilities
│   │   ├── Sundry Creditors (Payables)
│   │   └── Outstanding Expenses
│   └── Long-term Liabilities
│       └── Loans
│
├── Income
│   ├── Sales Revenue
│   ├── Service Revenue
│   └── Other Income
│
└── Expenses
    ├── Direct Expenses (COGS)
    │   └── Purchases
    └── Indirect Expenses
        ├── Rent
        ├── Salaries
        ├── Utilities
        └── Office Expenses
```

**Database Schema:**
```sql
CREATE TABLE account_groups (
    id SERIAL PRIMARY KEY,
    tenant_id INT REFERENCES tenants(id),
    group_name VARCHAR(100),
    parent_group_id INT REFERENCES account_groups(id), -- NULL for top-level
    group_type VARCHAR(20),  -- 'asset', 'liability', 'income', 'expense'
    affects_gross_profit BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP
);

-- Link bank_accounts to groups
ALTER TABLE bank_accounts ADD COLUMN group_id INT REFERENCES account_groups(id);
```

---

#### 9. Cheque Management ❌ NOT IMPLEMENTED
**Purpose:** Track issued/received cheques, clearance status

**Components:**
- **Cheque Register:**
  - Cheque Number
  - Date Issued/Received
  - Bank Account
  - Payee/Payer
  - Amount
  - Status: Issued / Cleared / Bounced / Cancelled

- **Features:**
  - Link cheque to invoice/bill payment
  - Mark cheque as cleared (update account balance)
  - Handle bounced cheques
  - Post-dated cheque tracking
  - Cheque printing

**Database Schema:**
```sql
CREATE TABLE cheques (
    id SERIAL PRIMARY KEY,
    tenant_id INT REFERENCES tenants(id),
    cheque_number VARCHAR(50),
    cheque_date DATE,
    bank_account_id INT REFERENCES bank_accounts(id),
    cheque_type VARCHAR(10), -- 'issued' or 'received'
    payee_payer VARCHAR(200),
    amount DECIMAL(15,2),
    status VARCHAR(20), -- 'pending', 'cleared', 'bounced', 'cancelled'
    cleared_date DATE,
    reference_type VARCHAR(50), -- 'invoice', 'purchase_bill', etc.
    reference_id INT,
    created_at TIMESTAMP
);
```

---

#### 10. TDS (Tax Deducted at Source) Tracking ❌ NOT IMPLEMENTED
**Purpose:** Track tax deductions, generate TDS certificates, monthly returns

**Components:**
- TDS on purchases (professional fees, rent, etc.)
- TDS on sales (if applicable)
- TDS Certificate generation
- Form 26AS reconciliation
- Quarterly TDS returns

---

#### 11. GST Reconciliation ❌ NOT IMPLEMENTED
**Purpose:** Match GSTR-1 (outward supply) with actual invoices

**Features:**
- Compare filed GSTR-1 with invoice data
- Identify missing invoices
- Identify invoice amount mismatches
- Auto-correction suggestions
- GSTR-2B matching (input credit)

---

#### 12. Budget vs. Actual ❌ NOT IMPLEMENTED
**Purpose:** Compare budgeted amounts with actual expenses/income

**Components:**
```
BUDGET vs. ACTUAL
Month: November 2025

EXPENSE HEAD     | BUDGETED  | ACTUAL    | VARIANCE  | % USED
═════════════════╪═══════════╪═══════════╪═══════════╪════════
Rent             | ₹20,000   | ₹20,000   | ₹0        | 100%
Salaries         | ₹50,000   | ₹48,000   | +₹2,000   | 96%
Utilities        | ₹5,000    | ₹6,500    | -₹1,500   | 130% ⚠️
Marketing        | ₹10,000   | ₹3,000    | +₹7,000   | 30%
─────────────────┼───────────┼───────────┼───────────┼────────
TOTAL            | ₹85,000   | ₹77,500   | +₹7,500   | 91%
```

---

#### 13. Cost Centers (Department/Project Tracking) ❌ NOT IMPLEMENTED
**Purpose:** Track expenses by department or project

**Example:**
- Cost Center: "Electrical Division"
- Cost Center: "Construction Projects"
- Cost Center: "Admin Office"

**Features:**
- Tag transactions with cost centers
- Generate P&L per cost center
- Allocate shared expenses across centers
- Project profitability analysis

---

#### 14. Multi-Currency Support ❌ NOT IMPLEMENTED
**Purpose:** Handle foreign currency transactions

**Features:**
- Define currencies (USD, EUR, GBP, etc.)
- Exchange rate management
- Foreign currency bank accounts
- Conversion gain/loss tracking
- Multi-currency reports

---

## 📅 IMPLEMENTATION TIMELINE (Suggested)

### Phase 5 Completion (Week 1-2)
1. **Balance Sheet** - 3-4 days
2. **Profit & Loss Statement** - 2-3 days
3. **Trial Balance** - 2-3 days

### Priority 2 Features (Week 3-4)
4. **Receivables Aging** - 2 days
5. **Payables Aging** - 2 days
6. **Bank Reconciliation** - 3-4 days

### Priority 3 Features (Month 2+)
7. **Financial Year Management** - 1 week
8. **Chart of Accounts** - 1 week
9. **Cheque Management** - 1 week
10. **Other Advanced Features** - As needed

---

## 🎯 CURRENT STATUS

### ✅ WORKING PERFECTLY:
- All bank/cash accounts with correct balances
- Contra vouchers for fund transfers
- Employee cash advances & expenses
- Invoice/Bill/Expense linking to accounts
- Cash Book, Bank Book, Day Book, Account Summary reports (Tally-style)

### ⏳ NEXT PRIORITY:
**Complete Phase 5:**
1. Balance Sheet
2. Profit & Loss Statement
3. Trial Balance

### 📊 BALANCES (as of last migration):
- **Cash in Hand:** ₹52,150.00 ✅
- **Bank HDFC:** ₹58,650.00 ✅
- **Silak Nandu:** ₹16,000.00 ✅

**All accounts reconciled and accurate!** 🎉

---

## 📝 NOTES

### Design Principles to Follow:
1. **Tally-Style UI** - All reports should match the clean, bordered format
2. **Double-Entry Bookkeeping** - Every transaction affects two accounts
3. **Multi-Tenant Support** - All features must respect tenant isolation
4. **Real-Time Updates** - Balances update immediately after transactions
5. **Print-Friendly** - All reports must have print CSS
6. **Mobile Responsive** - Reports should be viewable on tablets
7. **Export to Excel** - All reports should be exportable

### Database Best Practices:
1. Always use `tenant_id` in queries
2. Use indexes on frequently queried columns
3. Use PostgreSQL-specific features (`RETURNING id`, `text()` for raw SQL)
4. Set `created_by` to `None` for system-generated entries
5. Always commit/rollback transactions properly

---

**Last Updated:** 30 Nov 2025  
**Status:** Phase 5 - COMPLETE! Balance Sheet, P&L, Trial Balance Implemented  
**Next Action:** Fix opening balance double-entry issue

---

## 🚨 CRITICAL: Opening Balance Setup for New Customers

### **For New Tenant Onboarding:**

When a new customer signs up and wants to import their existing business:

**STEP 1: Set All Opening Balances**
1. Go to **Accounts & Banking** → **Bank & Cash Accounts**
2. Add all their bank/cash accounts with opening balances:
   - Cash in Hand: ₹50,000
   - Bank HDFC: ₹1,00,000
   - Petty Cash: ₹5,000
   - etc.

**STEP 2: Run the Opening Balance Fix (REQUIRED!)**
```
After setting all opening balances, navigate to:
/migrate/fix-opening-balances
```

**What this does:**
- Creates the balancing "Opening Balance - Equity" credit entry
- Makes Trial Balance balanced (Total Debits = Total Credits)
- Follows proper double-entry bookkeeping principles
- **REQUIRED for accounting accuracy!**

**Why this is needed:**
- When you set opening balance ₹50,000 for Cash in Hand, it creates:
  - Debit: Cash in Hand ₹50,000 ✅
  - Credit: ??? ❌ (Missing!)
- The migration creates: Credit: Opening Balance - Equity ₹50,000 ✅
- Now books are balanced!

### **Verification:**
After running the migration, check:
1. **Trial Balance** → Should show: ✅ "Trial Balance is Balanced!"
2. **Balance Sheet** → Owner's Equity will reflect correct opening capital

---

