# ✅ CORRECT Migration URLs

## ⚠️ IMPORTANT: Use These EXACT URLs!

The migration routes are different from what was documented. Here are the **CORRECT** URLs:

---

## 🔧 **Migration 1: Fix Vendor Payment Constraint**

### **CORRECT URL:**
```
https://bizbooks.co.in/migration/fix-vendor-payment-constraint
```

**OR for specific tenant:**
```
https://mahaveerelectricals.bizbooks.co.in/migration/fix-vendor-payment-constraint
```

**What it does:**
- Makes payment numbers tenant-specific
- Allows PAY-0001 to exist for multiple tenants

---

## 🔧 **Migration 1.5: Fix Purchase Bill Constraint** 🆕

### **CORRECT URL:**
```
https://bizbooks.co.in/migration/fix-purchase-bill-constraint
```

**OR for specific tenant:**
```
https://mahaveerelectricals.bizbooks.co.in/migration/fix-purchase-bill-constraint
```

**What it does:**
- Makes bill numbers tenant-specific
- Allows PB-202512-0001 to exist for multiple tenants
- **CRITICAL:** This fixes the duplicate bill number error!

---

## 🔧 **Migration 2: Add Purchase Bill Item Fields**

### **CORRECT URL:**
```
https://bizbooks.co.in/migration/add-purchase-bill-item-fields
```

**OR for specific tenant:**
```
https://mahaveerelectricals.bizbooks.co.in/migration/add-purchase-bill-item-fields
```

**What it does:**
- Adds 5 new columns to purchase_bill_items
- Enables creating items from purchase bills

---

## 🔧 **Migration 3: Migrate to Double-Entry** ⭐ DATA MIGRATION

### **CORRECT URL (Must be logged in as tenant admin):**
```
https://mahaveerelectricals.bizbooks.co.in/migration/to-double-entry
https://ayushi.bizbooks.co.in/migration/to-double-entry
https://<other-tenant>.bizbooks.co.in/migration/to-double-entry
```

**⚠️ CRITICAL:**
- Must be logged in to each tenant BEFORE visiting URL
- Run ONCE per tenant
- Takes 2-3 minutes

**What it does:**
- Converts existing invoices → account_transactions
- Converts existing purchase bills → account_transactions
- Converts existing expenses → account_transactions
- Converts existing salaries → account_transactions

---

## 🔧 **Migration 4: Fix Inventory Equity** (If Needed)

### **CORRECT URL:**
```
https://bizbooks.co.in/migration/fix-inventory-equity
```

**OR for specific tenant:**
```
https://mahaveerelectricals.bizbooks.co.in/migration/fix-inventory-equity
```

**When to run:**
- After Migration 3, if Trial Balance is still "Out of Balance"
- Only needed for tenants with inventory

**What it does:**
- Creates missing Owner's Capital entries for inventory

---

## 📋 **STEP-BY-STEP PROCESS:**

### **Step 1: Migrations 1 & 2 (No Login Required)**
```bash
# Open these URLs in browser (can be main domain):
1. https://bizbooks.co.in/migration/fix-vendor-payment-constraint
2. https://bizbooks.co.in/migration/add-purchase-bill-item-fields
```

### **Step 2: Migration 3 (Per Tenant - Login Required)**
```bash
# For EACH tenant:
1. Login to: https://mahaveerelectricals.bizbooks.co.in/admin/login
2. After login, visit: https://mahaveerelectricals.bizbooks.co.in/migration/to-double-entry
3. Wait for completion (2-3 minutes)
4. Repeat for other tenants (ayushi, etc.)
```

### **Step 3: Verify Trial Balance**
```bash
# For EACH tenant:
Visit: https://mahaveerelectricals.bizbooks.co.in/admin/accounts/reports/trial-balance

Expected: ✅ Green banner "Trial Balance is Balanced!"
```

### **Step 4: Migration 4 (If Needed)**
```bash
# Only if Trial Balance is OUT of balance:
Visit: https://mahaveerelectricals.bizbooks.co.in/migration/fix-inventory-equity
```

---

## 🎯 **QUICK COPY-PASTE (Replace with your domain):**

**For mahaveerelectricals tenant:**
```
https://mahaveerelectricals.bizbooks.co.in/migration/fix-vendor-payment-constraint
https://mahaveerelectricals.bizbooks.co.in/migration/fix-purchase-bill-constraint
https://mahaveerelectricals.bizbooks.co.in/migration/add-purchase-bill-item-fields
https://mahaveerelectricals.bizbooks.co.in/migration/to-double-entry
https://mahaveerelectricals.bizbooks.co.in/migration/fix-inventory-equity
```

**For ayushi tenant:**
```
https://ayushi.bizbooks.co.in/migration/fix-vendor-payment-constraint
https://ayushi.bizbooks.co.in/migration/fix-purchase-bill-constraint
https://ayushi.bizbooks.co.in/migration/add-purchase-bill-item-fields
https://ayushi.bizbooks.co.in/migration/to-double-entry
https://ayushi.bizbooks.co.in/migration/fix-inventory-equity
```

---

## ✅ **SUCCESS INDICATORS:**

**Migration 1 & 2:**
```json
{
  "status": "success",
  "message": "Migration completed"
}
```

**Migration 3:**
```json
{
  "status": "success",
  "purchase_bills_migrated": 50,
  "invoices_migrated": 100,
  "expenses_migrated": 25,
  "salary_slips_migrated": 10,
  "total_entries_created": 500
}
```

**Migration 4:**
```json
{
  "status": "success",
  "items_found": 78,
  "equity_entries_created": 78,
  "total_equity_value": "1989400.00"
}
```

---

## 🚨 **COMMON ERRORS:**

### **Error: "Not Found"**
- ❌ Wrong: `/migration/migrate-double-entry`
- ✅ Correct: `/migration/to-double-entry`

### **Error: "Please login to run migrations"**
- You must be logged in as tenant admin
- Login first, THEN visit migration URL
- Migration 3 requires login, 1 & 2 don't

### **Error: "Tenant not found"**
- Make sure you're on correct subdomain
- Use tenant-specific URL, not main domain for Migration 3

---

## 📖 **REFERENCE:**

**Route definitions in code:**
- `routes/fix_vendor_payment_constraint.py`: `/migration/fix-vendor-payment-constraint`
- `routes/migration_add_purchase_bill_item_fields.py`: `/migration/add-purchase-bill-item-fields`
- `routes/migrate_double_entry.py`: `/migration/to-double-entry`
- `routes/fix_inventory_equity.py`: `/migration/fix-inventory-equity`

**Blueprint prefix:** All use `url_prefix='/migration'`

---

**START WITH THESE CORRECT URLS! 🚀**

