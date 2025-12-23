# GST Logic Clarification - User Requirements

## 🎯 Core Principle (USER'S RULE)

> **"No GST purchase = No GST sale. PERIOD."**

This document clarifies the GST logic based on user requirements and real-world shopkeeper practices.

---

## ✅ SIMPLIFIED RULES

### Rule 1: Purchase Determines Sales Options

```
Purchase WITHOUT GST bill:
└─ Can ONLY sell WITHOUT GST ✅
   └─ No credit adjustment option ❌
   └─ Period. Done. Simple.

Purchase WITH GST bill:
├─ Option A: Sell WITH GST (normal taxable invoice) ✅
└─ Option B: Sell WITHOUT GST (kaccha bill) ✅
              └─ Later create Credit Adjustment (for compliance) ✅
```

**Key Point:** No GST purchase = No GST sale. **EVER.**

---

### Rule 2: Vendor Registration ≠ All Items Have GST

```
Vendor: Mahaveer (GST Registered) ✅

Purchase Bill #1:
├─ Jeans: ₹10,000 + GST ✅ (has GST bill)
└─ Electrical Wire: ₹5,000 (no GST bill) ❌

Same vendor, different GST status per item!
```

**Key Point:** Track GST at **purchase bill level**, not vendor level.

---

### Rule 3: Item GST Rate Field = Capability Flag

```
Item: Jeans
GST Rate: 12% (from item master)

Purpose: Determines IF item CAN have GST invoice

Logic:
├─ gst_rate > 0:  Item CAN have GST invoice ✅
│                 (if purchased with GST)
│
└─ gst_rate = 0:  Item CANNOT have GST invoice ❌
                  (only kaccha bill allowed)
```

**Key Point:** GST rate = item classification, not purchase status.

---

## 📊 EXAMPLE SCENARIOS

### Scenario 1: Jeans purchased WITHOUT GST
```
Purchase:
├─ Item: Jeans (12% GST rate in item master)
├─ Vendor: Unregistered (no GST bill)
├─ Cost: ₹1000
└─ Batch: purchased_with_gst = FALSE ❌

Sales Options:
├─ Taxable invoice (GST): ❌ BLOCKED
├─ Non-taxable invoice (Kaccha): ✅ ALLOWED
└─ Credit Adjustment: ❌ NOT APPLICABLE

Why? No GST purchase = No GST sale!
```

### Scenario 2: Jeans purchased WITH GST
```
Purchase:
├─ Item: Jeans (12% GST rate in item master)
├─ Vendor: Registered (has GST bill)
├─ Cost: ₹1000 + ₹120 GST = ₹1120
└─ Batch: purchased_with_gst = TRUE ✅

Sales Options:
├─ Taxable invoice (GST): ✅ ALLOWED
├─ Non-taxable invoice (Kaccha): ✅ ALLOWED
└─ Credit Adjustment (later): ✅ ALLOWED
    └─ Only if sold via kaccha bill first

Why? GST purchase = Full flexibility!
```

### Scenario 3: Books (0% GST by law)
```
Item: Books
GST Rate: 0% (in item master)

Sales Options:
├─ Taxable invoice (GST): ❌ BLOCKED (gst_rate = 0)
└─ Non-taxable invoice (Kaccha): ✅ ALLOWED

Why? Item is GST-exempt by law!
```

### Scenario 4: Electrical Wire (same vendor, no GST bill)
```
Vendor: Mahaveer (GST Registered) ✅
Purchase Bill:
├─ Jeans: ₹10,000 + GST ✅
└─ Electrical Wire: ₹5,000 (no bill) ❌

Result:
├─ Jeans batch: purchased_with_gst = TRUE
└─ Wire batch: purchased_with_gst = FALSE

Sales:
├─ Jeans: Can create GST or non-GST invoice ✅
└─ Wire: Can ONLY create non-GST invoice ✅
```

---

## 💰 2-STEP PROCESS ACCOUNTING

### Step 1: Kaccha Bill (Non-taxable invoice) - Jan 1

**Customer pays: ₹1500 (cash collected)**
**Stock: -1 unit**

```
Accounting Entries:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Dr. Cash/AR           ₹1,500
    Cr. Sales Revenue          ₹1,500

Dr. COGS              ₹1,000
    Cr. Inventory              ₹1,000

If Commission (5%):
Dr. Commission Exp    ₹75
    Cr. Commission Payable     ₹75

If Loyalty (1%):
Dr. Loyalty Exp       ₹15
    Cr. Loyalty Points         ₹15
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Reports (After Step 1):
├─ P&L: Revenue ₹1500, COGS ₹1000, Gross Profit ₹500
├─ Balance Sheet: Cash +₹1500, Inventory -₹1000
├─ Trial Balance: All balanced
└─ GST Reports: NOTHING (non-taxable invoice) ❌
```

### Step 2: Credit Adjustment Invoice - Jan 5 (later)

**Customer pays: ₹0 (nothing - already paid)**
**Stock: No change (already reduced)**

```
Invoice shows:
├─ Taxable value: ₹1,339.29
├─ CGST @ 6%: ₹80.36
├─ SGST @ 6%: ₹80.36
└─ Total: ₹1,500.01

Accounting Entries:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Dr. Other Income (reversal) ₹160.72
    Cr. CGST Payable              ₹80.36
    Cr. SGST Payable              ₹80.36

Commission/Loyalty: NO (already processed in Step 1) ❌

Reports (After Step 2):
├─ P&L: Other Income -₹160.72, GST Payable +₹160.72
├─ Balance Sheet: GST Payable +₹160.72
├─ Trial Balance: Balanced
└─ GSTR-1: Show output tax ₹160.72 ✅
```

**Net Effect:**
- Shopkeeper collected: ₹1500 total
- Must pay GST to govt: ₹160.72
- Net benefit: ₹160.72 (recorded as "Other Income" offset by GST liability)

---

## 🔧 EXISTING INVENTORY HANDLING

For items added before batch tracking was implemented:

```python
if item.gst_rate > 0:
    # Taxable item - assume purchased WITH GST (benefit of doubt)
    classification = "GST stock"
    can_create_gst_invoice = True
else:
    # Exempt item - no GST applicable
    classification = "Non-GST stock"
    can_create_gst_invoice = False
```

**Rationale:**
- Most shopkeepers buy from registered wholesalers
- Safer to assume GST purchase for existing inventory
- Gradually transitions as new purchases create proper batches

---

## 📋 GST REPORTS

### GSTR-3B (Input Tax Credit)

```sql
-- Show ONLY purchases from GST-registered vendors
SELECT * FROM purchase_bills 
WHERE gst_applicable = TRUE  -- Registered vendor
AND status = 'approved'
```

**Ignores:**
- Purchases from unregistered vendors (gst_applicable = FALSE)
- Cash purchases without GST bill

---

### GSTR-1 (Sales/Output)

```sql
-- Show ONLY GST invoices
SELECT * FROM invoices 
WHERE invoice_type IN ('taxable', 'credit_adjustment')
AND status != 'draft'
```

**Ignores:**
- Non-taxable invoices (kaccha bills)
- Draft invoices

---

### Other Reports (P&L, Balance Sheet, Trial Balance)

```sql
-- Show EVERYTHING
- All purchases (with or without GST)
- All sales (with or without GST)
- Stock, expenses, income - everything
```

---

## ✅ IMPLEMENTATION SUMMARY

1. **No GST purchase = No GST sale** (blocked completely)
2. **GST purchase = Choose GST or non-GST sale** (flexible)
3. **Vendor registration ≠ All items have GST** (track per item per bill)
4. **Item GST rate field = Capability flag** (can this item have GST at all?)
5. **Batch tracking = Actual purchase status** (did we get GST bill for this batch?)
6. **Credit adjustment = No stock impact, no commission/loyalty**
7. **GSTR reports = ONLY real GST transactions**
8. **Other reports = Full business picture (all transactions)**

---

## 🚫 WHAT WE'RE BLOCKING

1. ❌ Creating GST invoice for items purchased without GST
2. ❌ Creating GST invoice for exempt items (gst_rate = 0)
3. ❌ Showing non-GST purchases in GSTR-3B
4. ❌ Showing non-taxable invoices in GSTR-1
5. ❌ Processing commission/loyalty for credit adjustment invoices

---

## ✅ WHAT WE'RE ALLOWING

1. ✅ Creating non-GST invoice for items purchased with GST (shopkeeper's choice)
2. ✅ Later creating credit adjustment invoice for compliance
3. ✅ Mixing GST and non-GST items in same purchase bill (per item basis)
4. ✅ Using existing inventory based on item's GST rate classification
5. ✅ Full flexibility for shopkeepers while maintaining compliance

---

**This is the CORRECT, SIMPLIFIED, and LEGALLY COMPLIANT approach!** 🎯

