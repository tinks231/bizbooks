# ✅ Production Migration Checklist
## Run These Migrations in Production (IN ORDER!)

**Date:** December 12, 2025  
**Critical:** Follow the exact order below!

---

## 🎯 **QUICK SUMMARY:**

```
Total Migrations: 4
Time Required: 5-10 minutes
Downtime Required: NO (all migrations are backward-compatible)
Reversible: YES (see rollback section)
```

---

## 📝 **MIGRATION CHECKLIST:**

### ☑️ **MIGRATION 1: Fix Vendor Payment Constraint**

**Priority:** ⭐⭐⭐ CRITICAL (Do FIRST!)

**URL to visit:**
```
https://bizbooks-murex.vercel.app/migration/fix-vendor-payment-constraint
```

**What it does:**
- Changes `vendor_payments.payment_number` from globally unique to tenant-specific
- Allows different tenants to use same payment numbers (PAY-0001, etc.)

**SQL (Alternative method):**
```sql
ALTER TABLE vendor_payments 
DROP CONSTRAINT IF EXISTS vendor_payments_payment_number_key;

ALTER TABLE vendor_payments 
ADD CONSTRAINT vendor_payments_tenant_payment_number_key 
    UNIQUE (tenant_id, payment_number);
```

**Expected result:**
```
✓ Old constraint dropped
✓ New constraint added
```

**Verification:**
- Create vendor payment for different tenants
- Both should be able to use PAY-0001 without error

---

### ☑️ **MIGRATION 2: Add Purchase Bill Item Fields**

**Priority:** ⭐⭐⭐ CRITICAL (Do SECOND!)

**URL to visit:**
```
https://bizbooks-murex.vercel.app/migration/add-purchase-bill-item-fields
```

**What it does:**
- Adds 5 new columns to `purchase_bill_items` table
- Enables creating new inventory items from purchase bills

**SQL (Alternative method):**
```sql
ALTER TABLE purchase_bill_items 
ADD COLUMN IF NOT EXISTS is_new_item BOOLEAN DEFAULT FALSE;

ALTER TABLE purchase_bill_items 
ADD COLUMN IF NOT EXISTS sku VARCHAR(100);

ALTER TABLE purchase_bill_items 
ADD COLUMN IF NOT EXISTS selling_price NUMERIC(15, 2);

ALTER TABLE purchase_bill_items 
ADD COLUMN IF NOT EXISTS mrp NUMERIC(15, 2);

ALTER TABLE purchase_bill_items 
ADD COLUMN IF NOT EXISTS category_id INTEGER REFERENCES item_categories(id);
```

**Expected result:**
```
✓ Added is_new_item
✓ Added sku
✓ Added selling_price
✓ Added mrp
✓ Added category_id
```

**Verification:**
- Create purchase bill (old way still works)
- No errors on existing purchase bills

---

### ☑️ **MIGRATION 3: Migrate Existing Data to Double-Entry**

**Priority:** ⭐⭐⭐ CRITICAL (Do THIRD!)

**⚠️ WARNING:** This is a DATA migration!
- Will create 500-1000+ account_transaction records
- Takes 1-2 minutes per tenant
- **Run ONLY ONCE per tenant!**
- Creates accounting entries for existing invoices, purchases, expenses, salaries

**URL to visit (for EACH tenant):**
```
# Login as each tenant admin, then visit:
https://mahaveerelectricals.bizbooks-murex.vercel.app/migration/migrate-double-entry
https://ayushi.bizbooks-murex.vercel.app/migration/migrate-double-entry
https://<other-tenant>.bizbooks-murex.vercel.app/migration/migrate-double-entry
```

**What it does:**
- Scans all existing invoices, purchase bills, expenses, salary slips
- Creates double-entry account_transactions for each
- Does NOT modify original data (safe!)

**Expected result (per tenant):**
```
✓ Migrated X invoices → account_transactions (Sales, COGS, AR)
✓ Migrated Y purchase bills → account_transactions (Inventory, AP, ITC)
✓ Migrated Z expenses → account_transactions (Operating Expenses)
✓ Migrated W salary slips → account_transactions (Salary Expenses)

Total: XXX account_transactions created
```

**Verification after EACH tenant:**
1. Visit Trial Balance
2. Should show green: "Trial Balance is Balanced!"
3. If out of balance, see Migration 4 below

---

### ☑️ **MIGRATION 4: Fix Inventory Equity (If Needed)**

**Priority:** ⭐⭐ IMPORTANT (Only if Trial Balance is out of balance)

**When to run:**
- After Migration 3, if Trial Balance shows "Out of Balance"
- Only needed for tenants with inventory opening balances

**URL to visit (for EACH affected tenant):**
```
https://mahaveerelectricals.bizbooks-murex.vercel.app/migration/fix-inventory-equity
https://ayushi.bizbooks-murex.vercel.app/migration/fix-inventory-equity
```

**What it does:**
- Creates missing Owner's Capital entries for inventory opening stock
- Balances the Trial Balance

**Expected result:**
```
✓ Found X items with opening stock
✓ Created Y equity entries
✓ Total equity created: ₹ZZZ
```

**Verification:**
1. Visit Trial Balance
2. Should now show: "Trial Balance is Balanced!" ✅
3. Owner's Capital - Inventory Opening should appear

---

## 📊 **POST-MIGRATION TESTING:**

### **Test 1: Create New Invoice (mahaveerelectricals)**
```
1. Create invoice for ₹1,000 with 2 items
2. Check Trial Balance → Should be balanced
3. Check P&L → Sales income should increase by ₹1,000
4. Check Cash Book → If paid, cash should increase
```

### **Test 2: Create New Purchase Bill (ayushi)**
```
1. Create purchase bill: ₹500 + GST ₹60 = ₹560
2. Approve bill
3. Check Trial Balance → Should be balanced
4. Check ITC shows ₹60 as asset
5. Check Inventory increased by ₹500
6. Check AP shows ₹560
```

### **Test 3: Pay Commission (ayushi)**
```
1. Go to Commission Reports
2. Pay any unpaid commission
3. Select cash account
4. Check Cash Book → Balance reduced
5. Check P&L → Commission Expenses shows
6. Check Trial Balance → Still balanced
```

### **Test 4: All Reports for All Tenants**
```
For each tenant:
- [ ] Trial Balance: Balanced?
- [ ] Profit & Loss: Accurate?
- [ ] Balance Sheet: Assets = Liabilities + Equity?
- [ ] Cash Book: Transactions showing?
- [ ] Bank Book: Transactions showing?
```

---

## 🔥 **CRITICAL CHECKS:**

**Before declaring SUCCESS, verify:**

1. **All Tenants' Trial Balances are BALANCED** ✅
   - Green banner showing
   - Debits = Credits

2. **No Errors in Vercel Logs** ✅
   - Check Vercel dashboard
   - No 500 errors
   - No database errors

3. **Old Features Still Work** ✅
   - Creating invoices (old way)
   - Creating purchase bills (old way)
   - All existing functionality preserved

4. **New Features Work** ✅
   - Commission payments update balance
   - Purchase bills with GST balance correctly
   - Reports show accurate data

---

## 🆘 **ROLLBACK PROCEDURE (If Something Breaks):**

### **Quick Rollback (Revert Code):**
```bash
git checkout main
git revert HEAD~15..HEAD
git push origin main
# Vercel will redeploy old version in 2-3 minutes
```

### **Database Rollback (Remove New Entries):**
```sql
-- ONLY if accounting is completely broken
-- Removes all new account_transactions
DELETE FROM account_transactions 
WHERE created_at >= '2025-12-12 00:00:00';

-- Original data (invoices, expenses) remains intact
```

**⚠️ Use database rollback only as last resort!**

---

## 📱 **NOTIFICATION PLAN:**

**After deployment:**

1. **Inform Users:**
   ```
   Subject: BizBooks Upgraded - Professional Accounting System!
   
   We've upgraded BizBooks with professional double-entry accounting:
   - Trial Balance now always balanced
   - Accurate profit/loss tracking
   - GST compliance with Input Tax Credit
   - Commission payment tracking
   
   No action required from your side!
   All existing data has been automatically migrated.
   
   New features available now!
   ```

2. **Monitor for 24 Hours:**
   - Check Vercel logs hourly
   - Respond to any user reports quickly
   - Be ready to rollback if critical issues

3. **Declare Success After 24 Hours:**
   - If no issues reported
   - All tests passing
   - Users happy

---

## 🎯 **EXPECTED OUTCOMES:**

### **Immediate (After Migration):**
- ✅ All Trial Balances balanced
- ✅ Reports showing accurate data
- ✅ No errors in production

### **Short-term (1 Week):**
- ✅ Users creating invoices, purchases normally
- ✅ Commission payments working
- ✅ Reports trusted by business owners

### **Long-term (1 Month):**
- ✅ Month-end closing accurate
- ✅ GST returns filed correctly using ITC
- ✅ Accountants/CAs approve the system
- ✅ Business decisions made on accurate data

---

## 📋 **MIGRATION LOG TEMPLATE:**

**Use this to track migration progress:**

```
TENANT: mahaveerelectricals
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Migration 1 (Vendor Payment): ✅ Done at 3:15 PM
Migration 2 (Purchase Fields): ✅ Done at 3:15 PM
Migration 3 (Double-Entry):   ✅ Done at 3:20 PM
  - Created 487 account_transactions
Migration 4 (Inventory Equity): ✅ Done at 3:22 PM
  - Fixed inventory equity ₹1,989,400

Trial Balance: ✅ BALANCED (verified at 3:25 PM)
Profit & Loss: ✅ ACCURATE (verified at 3:25 PM)
Balance Sheet: ✅ BALANCED (verified at 3:25 PM)

TENANT: ayushi
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Migration 1 (Vendor Payment): ✅ Done at 3:30 PM
Migration 2 (Purchase Fields): ✅ Done at 3:30 PM
Migration 3 (Double-Entry):   ✅ Done at 3:32 PM
  - Created 15 account_transactions
Migration 4 (Inventory Equity): ⏭️ SKIPPED (already balanced)

Trial Balance: ✅ BALANCED (verified at 3:35 PM)
Profit & Loss: ✅ ACCURATE (verified at 3:35 PM)
Balance Sheet: ✅ BALANCED (verified at 3:35 PM)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DEPLOYMENT STATUS: ✅ SUCCESS!
Completed at: 3:40 PM on December 12, 2025
No errors, all tenants balanced
```

---

## 🎊 **YOU'RE READY TO DEPLOY!**

**Time estimate:**
- Push code: 1 minute
- Vercel deploy: 3 minutes
- Run migrations: 5 minutes (all tenants)
- Verification: 5 minutes
- **Total: ~15 minutes**

**Best time to deploy:**
- Off-peak hours (evening/night)
- When you can monitor for 1-2 hours after
- Have rollback plan ready

---

**GOOD LUCK! 🚀**

