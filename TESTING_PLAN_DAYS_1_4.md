# 📋 TESTING PLAN: Double-Entry Accounting (Days 1-4)

**Branch:** `feature/full-double-entry-accounting`  
**Testing Date:** December 11, 2025  
**Tenant:** ayushi (or any tenant with data)

---

## 🎯 **WHAT WE'RE TESTING:**

**Day 1:** Purchase Bills with full double-entry  
**Day 2:** Sales/Invoices with COGS + full double-entry  
**Day 3:** Salary & Expense accounting  
**Day 4:** Data migration script  

---

## ✅ **PRE-TEST CHECKLIST:**

- [ ] Local database has production data copy
- [ ] Server is running locally
- [ ] Can access tenant: `http://ayushi.lvh.me:5001/admin/login`
- [ ] Logged in successfully

---

## 📊 **TEST 1: TRIAL BALANCE (Before Migration)**

**Purpose:** See current state before applying double-entry accounting

### **Steps:**

1. **Go to:**
   ```
   Admin → Accounts → Reports → Trial Balance
   ```

2. **Take Note:**
   - Is it balanced? (Debits = Credits)
   - What's the difference amount?
   - Which accounts are showing?
   - Take a screenshot

3. **Expected Result:**
   - Probably OUT OF BALANCE ❌
   - Missing expense entries (only cash side recorded)
   - Missing COGS entries
   - Missing sales income entries

---

## 🔄 **TEST 2: RUN THE MIGRATION**

**Purpose:** Convert existing data to double-entry accounting

### **Steps:**

1. **Open new browser tab:**
   ```
   http://ayushi.lvh.me:5001/migration/to-double-entry
   ```

2. **Watch the output:**
   - Should show 4 steps (Purchase Bills, Invoices, Expenses, Salaries)
   - Shows progress for each step
   - Shows summary at end

3. **Expected Output:**
   ```
   ════════════════════════════════════════════════════════
   🔄 MIGRATING TO DOUBLE-ENTRY ACCOUNTING SYSTEM
   ════════════════════════════════════════════════════════
   
   📦 Step 1: Migrating Purchase Bills...
   ✅ Migrated X purchase bills
   
   📄 Step 2: Migrating Invoices (with COGS)...
   ✅ Migrated X invoices
   
   💰 Step 3: Migrating Expenses...
   ✅ Migrated X expenses
   
   👥 Step 4: Migrating Salary Payments...
   ✅ Migrated X salary payments
   
   🎉 MIGRATION COMPLETE!
   ✅ Total Accounting Entries Created: XXX
   ```

4. **Check server terminal:**
   - Should see detailed migration logs
   - Shows each transaction being created
   - Any errors will be visible here

5. **Result:**
   - [ ] Migration completed successfully
   - [ ] No critical errors
   - [ ] JSON response shows success

---

## 📊 **TEST 3: TRIAL BALANCE (After Migration)**

**Purpose:** Verify migration fixed the balance

### **Steps:**

1. **Go to:**
   ```
   Admin → Accounts → Reports → Trial Balance
   ```

2. **Verify:**
   - [ ] **Trial Balance is BALANCED!** ✅
   - [ ] Shows these ASSET accounts:
     - Cash in Hand
     - Bank Account(s)
     - Accounts Receivable (Customers)
     - Inventory (Stock on Hand)
   - [ ] Shows these LIABILITY accounts:
     - Accounts Payable (Vendors)
     - Owner's Capital - Inventory Opening
     - Owner's Capital - Cash Opening
     - Owner's Capital - Bank Opening
   - [ ] Shows these INCOME accounts:
     - Sales Income
   - [ ] Shows these EXPENSE accounts:
     - Cost of Goods Sold (COGS)
     - Salary Expenses
     - Operating Expenses (by category)

3. **Take screenshot** for comparison with Test 1

4. **Expected Result:**
   ```
   TRIAL BALANCE - Ayushi
   As of: December 11, 2025
   ═══════════════════════════════════════════════════════════
   
   ASSETS:                                DEBIT       CREDIT
     Cash in Hand                        XX,XXX
     Bank - ICICI                       XXX,XXX
     Accounts Receivable                 XX,XXX
     Inventory                       X,XXX,XXX
                                    ──────────  ──────────
     Total Assets                    X,XXX,XXX           0
   
   LIABILITIES:
     Accounts Payable                                XX,XXX
     Owner's Capital                              X,XXX,XXX
                                    ──────────  ──────────
     Total Liabilities                       0   X,XXX,XXX
   
   INCOME:
     Sales Income                                   XXX,XXX
                                    ──────────  ──────────
     Total Income                            0     XXX,XXX
   
   EXPENSES:
     Cost of Goods Sold                 XXX,XXX
     Salary Expenses                     XX,XXX
     Operating Expenses                  XX,XXX
                                    ──────────  ──────────
     Total Expenses                     XXX,XXX           0
   
   ═══════════════════════════════════════════════════════════
   GRAND TOTAL                        X,XXX,XXX   X,XXX,XXX
   ═══════════════════════════════════════════════════════════
   
   ✅ BALANCED!
   ```

---

## 📈 **TEST 4: PROFIT & LOSS REPORT**

**Purpose:** Verify profit calculation is correct

### **Steps:**

1. **Go to:**
   ```
   Admin → Accounts → Reports → Profit & Loss
   ```

2. **Verify Structure:**
   ```
   INCOME:
     Sales Income                     ₹XXX,XXX
   
   LESS: COST OF GOODS SOLD:
     COGS                            (₹XXX,XXX)
                                     ──────────
     GROSS PROFIT                     ₹XXX,XXX
   
   LESS: OPERATING EXPENSES:
     Salary Expenses                  (₹XX,XXX)
     Rent Expense                      (₹X,XXX)
     Electricity Expense               (₹X,XXX)
     Other Expenses                    (₹X,XXX)
                                     ──────────
     NET PROFIT                        ₹XX,XXX
   ```

3. **Verify Math:**
   - [ ] Sales Income - COGS = Gross Profit ✅
   - [ ] Gross Profit - Operating Expenses = Net Profit ✅
   - [ ] All numbers look reasonable ✅

---

## 💰 **TEST 5: BALANCE SHEET**

**Purpose:** Verify assets = liabilities + equity

### **Steps:**

1. **Go to:**
   ```
   Admin → Accounts → Reports → Balance Sheet
   ```

2. **Verify Structure:**
   ```
   ASSETS:
     Current Assets:
       Cash & Bank                    ₹XXX,XXX
       Accounts Receivable             ₹XX,XXX
       Inventory                    ₹X,XXX,XXX
                                    ──────────
     Total Assets                   ₹X,XXX,XXX
   
   LIABILITIES & EQUITY:
     Current Liabilities:
       Accounts Payable                ₹XX,XXX
     
     Owner's Equity:
       Owner's Capital              ₹X,XXX,XXX
       Retained Earnings/Profit        ₹XX,XXX
                                    ──────────
     Total Liabilities & Equity     ₹X,XXX,XXX
   
   ✅ BALANCED!
   ```

3. **Verify:**
   - [ ] Total Assets = Total Liabilities & Equity ✅
   - [ ] Inventory shows as Asset (not expense) ✅
   - [ ] Owner's equity includes opening balances ✅

---

## 🆕 **TEST 6: CREATE NEW PURCHASE BILL**

**Purpose:** Test Day 1 work - Purchase accounting

### **Steps:**

1. **Go to:**
   ```
   Admin → Purchase Bills → Create Purchase Bill
   ```

2. **Create test bill:**
   - Vendor: Test Vendor
   - Bill Date: Today
   - Add 2-3 items
   - Total: ₹10,000
   - Payment Status: Unpaid (credit purchase)
   - Save

3. **Check server terminal:**
   ```
   ✅ Double-entry for purchase bill BILL-XXX
      DEBIT:  Inventory          ₹10,000
      CREDIT: Accounts Payable   ₹10,000
   ```

4. **Verify in Trial Balance:**
   - Go back to Trial Balance
   - [ ] Inventory increased by ₹10,000 (debit)
   - [ ] Accounts Payable increased by ₹10,000 (credit)
   - [ ] Still balanced ✅

---

## 🛍️ **TEST 7: CREATE NEW INVOICE**

**Purpose:** Test Day 2 work - Sales + COGS

### **Steps:**

1. **Go to:**
   ```
   Admin → Invoices → Create Invoice
   ```

2. **Create test invoice:**
   - Customer: Test Customer
   - Invoice Date: Today
   - Add 2-3 items (items that have cost_price set!)
   - Total: ₹15,000
   - Payment Status: Unpaid (credit sale)
   - Save

3. **Check server terminal:**
   ```
   📦 Item 1: Qty 5 × Cost ₹800 = COGS ₹4,000
   📦 Item 2: Qty 3 × Cost ₹1,200 = COGS ₹3,600
   
   ✅ Double-entry for invoice INV-XXX
      DEBIT:  Accounts Receivable  ₹15,000
      CREDIT: Sales Income          ₹15,000
      DEBIT:  COGS                   ₹7,600
      CREDIT: Inventory              ₹7,600
   
   💰 Invoice INV-XXX - Total COGS: ₹7,600
   💰 Invoice INV-XXX - Sales: ₹15,000
   💰 Invoice INV-XXX - Gross Profit: ₹7,400
   ```

4. **Verify in Trial Balance:**
   - [ ] Accounts Receivable increased by ₹15,000
   - [ ] Sales Income increased by ₹15,000
   - [ ] COGS increased by ₹7,600
   - [ ] Inventory decreased by ₹7,600
   - [ ] Still balanced ✅

5. **Verify in Profit & Loss:**
   - [ ] Sales Income shows ₹15,000 more
   - [ ] COGS shows ₹7,600 more
   - [ ] Gross Profit increased by ₹7,400 ✅

---

## 💸 **TEST 8: PAY AN EXPENSE**

**Purpose:** Test Day 3 work - Expense accounting

### **Steps:**

1. **Go to:**
   ```
   Admin → Expenses → Add Expense
   ```

2. **Create test expense:**
   - Category: Rent (or Electricity)
   - Amount: ₹5,000
   - Description: Test expense payment
   - Payment From: Cash/Bank account
   - Save

3. **Check server terminal:**
   ```
   ✅ Double-entry for expense EXP-XXX
      DEBIT:  Rent Expense  ₹5,000
      CREDIT: Cash/Bank     ₹5,000
   ```

4. **Verify in Trial Balance:**
   - [ ] Rent Expense increased by ₹5,000 (debit)
   - [ ] Cash/Bank decreased by ₹5,000 (credit)
   - [ ] Still balanced ✅

5. **Verify in Profit & Loss:**
   - [ ] Operating Expenses increased by ₹5,000
   - [ ] Net Profit decreased by ₹5,000 ✅

---

## 👥 **TEST 9: PAY SALARY**

**Purpose:** Test Day 3 work - Salary accounting

### **Steps:**

1. **Go to:**
   ```
   Admin → Payroll → Pay Salary
   ```

2. **Pay salary:**
   - Select month/year
   - Select employees
   - Total: ₹20,000
   - Payment From: Bank account
   - Save

3. **Check server terminal:**
   ```
   ✅ Double-entry for salary payment SAL-2024-12
      DEBIT:  Salary Expense  ₹20,000
      CREDIT: Bank Account    ₹20,000
   ```

4. **Verify in Trial Balance:**
   - [ ] Salary Expenses increased by ₹20,000 (debit)
   - [ ] Bank balance decreased by ₹20,000 (credit)
   - [ ] Still balanced ✅

---

## 🎯 **TEST 10: COMPREHENSIVE VERIFICATION**

**Purpose:** Final check of all reports

### **Steps:**

1. **Trial Balance:**
   - [ ] Still balanced after all new transactions ✅
   - [ ] All accounts showing correctly ✅
   - [ ] No negative values (except normal credits) ✅

2. **Profit & Loss:**
   - [ ] Shows all income (Sales) ✅
   - [ ] Shows COGS ✅
   - [ ] Shows all expenses (Salary, Rent, etc.) ✅
   - [ ] Net Profit calculation is correct ✅

3. **Balance Sheet:**
   - [ ] Assets = Liabilities + Equity ✅
   - [ ] Cash/Bank balances match account balances ✅
   - [ ] Inventory value is accurate ✅

4. **Cashbook:**
   ```
   Admin → Accounts → Cash Book
   ```
   - [ ] All cash transactions recorded ✅
   - [ ] Opening balance + inflows - outflows = closing balance ✅

5. **Bank Book:**
   ```
   Admin → Accounts → Bank Book
   ```
   - [ ] All bank transactions recorded ✅
   - [ ] Balance matches Trial Balance ✅

---

## 📊 **EXPECTED RESULTS SUMMARY:**

### **✅ PASS Criteria:**

1. **Trial Balance:** Always balanced (Debits = Credits)
2. **Profit & Loss:** Correct profit calculation (Sales - COGS - Expenses)
3. **Balance Sheet:** Assets = Liabilities + Equity
4. **New Transactions:** All create proper double-entry
5. **Server Logs:** Show detailed accounting entries
6. **No Errors:** No critical errors in terminal or browser

### **❌ FAIL Criteria:**

1. Trial Balance out of balance
2. Missing accounts in reports
3. COGS not calculated for invoices
4. Negative balances where shouldn't be
5. Errors in terminal during transaction creation

---

## 🐛 **TROUBLESHOOTING:**

### **Issue: Trial Balance Still Out of Balance**

**Check:**
1. Did migration complete successfully?
2. Any errors in server terminal?
3. Try running migration again (it's safe!)

**Fix:**
```bash
# Re-run migration
http://ayushi.lvh.me:5001/migration/to-double-entry
```

---

### **Issue: COGS Shows Zero**

**Check:**
1. Do items have `cost_price` set?
2. Are invoice items linked to inventory items?

**Fix:**
1. Go to Admin → Items
2. Edit items and add cost_price
3. Create new invoice to test

---

### **Issue: Missing Accounts in Trial Balance**

**Check:**
1. Are there transactions for those account types?
2. Did migration run successfully?

**Fix:**
1. Create test transactions (purchase, sale, expense)
2. Verify they appear in Trial Balance

---

## 📸 **SCREENSHOTS TO CAPTURE:**

1. **Trial Balance BEFORE migration** (showing out of balance)
2. **Migration success message**
3. **Trial Balance AFTER migration** (showing balanced!)
4. **Profit & Loss Report** (showing correct profit)
5. **Balance Sheet** (showing balanced)
6. **Server terminal** showing double-entry logs for new transactions

---

## ✅ **TEST COMPLETION CHECKLIST:**

- [ ] Test 1: Trial Balance (Before) - Captured
- [ ] Test 2: Migration - Completed successfully
- [ ] Test 3: Trial Balance (After) - Balanced ✅
- [ ] Test 4: Profit & Loss - Correct calculation ✅
- [ ] Test 5: Balance Sheet - Balanced ✅
- [ ] Test 6: New Purchase Bill - Double-entry working ✅
- [ ] Test 7: New Invoice - COGS calculated ✅
- [ ] Test 8: Pay Expense - Double-entry working ✅
- [ ] Test 9: Pay Salary - Double-entry working ✅
- [ ] Test 10: Final Verification - All reports correct ✅

---

## 🎉 **SUCCESS!**

**If all tests pass:**
- ✅ Double-entry accounting is working correctly
- ✅ Migration script works as expected
- ✅ Trial Balance always balanced
- ✅ Reports show accurate financial data
- ✅ Ready for production deployment!

---

## 📞 **REPORT ISSUES:**

**If you find any problems:**
1. Note which test failed
2. Screenshot the error
3. Copy server terminal output
4. Note what you expected vs. what you got
5. Share with development team

---

**Testing By:** _________________  
**Date:** December 11, 2025  
**Status:** [ ] PASS  [ ] FAIL  [ ] NEEDS REVIEW  

**Notes:**
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________

