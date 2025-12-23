# Testing Guide - GST Logic Fixes

## 🎯 What Was Fixed

1. **GSTR-3B Filtering:** Now correctly filters by `gst_applicable` toggle (not GST amount)
2. **Existing Inventory:** Falls back to `item.opening_stock` and uses `item.gst_rate` to classify
3. **Exempt Items:** Blocks GST invoices for items with `gst_rate = 0`
4. **Credit Adjustment:** Excludes commission and loyalty (already in original bill)
5. **Opening Stock Allocation:** Properly reduces `opening_stock` for legacy items

---

## ✅ TEST CASES

### Test 1: Existing Inventory (Legacy Items)

**Setup:**
```
Item: Jeans (existing in inventory)
- Opening stock: 50 units
- GST rate: 12%
- Cost price: ₹1000
- No batches exist (legacy item)
```

**Test Steps:**
1. Go to **Create Invoice**
2. Select **Jeans** item
3. Check the badges below item name

**Expected Result:**
```
✅ GST: 50 units | Non-GST: 0 units

Why? gst_rate > 0, so assumed purchased with GST
```

**Test Invoice Creation:**
1. Try creating **Taxable invoice** for 10 units → ✅ Should work
2. Try creating **Non-taxable invoice** for 10 units → ✅ Should work
3. After approval, check item stock → Should reduce to 40 units

---

### Test 2: Exempt Item (GST Rate = 0)

**Setup:**
```
Create new item: Books
- GST rate: 0% (select from dropdown)
- Opening stock: 100 units
- Cost price: ₹500
```

**Test Steps:**
1. Go to **Create Invoice**
2. Add **Books** item
3. Select **Taxable** invoice type
4. Try to save

**Expected Result:**
```
❌ Error: Cannot create GST invoice for exempt item.

Item: Books
GST Rate: 0% (Exempt by law)

This item is GST-exempt. Only non-taxable invoices are allowed.
```

**Test Non-Taxable:**
1. Change invoice type to **Non-taxable**
2. Add Books item → ✅ Should work
3. Save and approve → ✅ Should succeed

---

### Test 3: Purchase Bill GST Toggle

**Setup:**
```
Vendor: Local Trader (Unregistered)
```

**Test Steps:**
1. Go to **Create Purchase Bill**
2. Select vendor
3. **Uncheck** "GST Applicable on this Purchase" toggle
4. Add items:
   - Jeans (₹1000 × 20 units) = ₹20,000
5. Save and approve

**Expected Result:**
```
✅ Batch created with purchased_with_gst = FALSE
✅ Item stock increased by 20 units
✅ In GSTR-3B: This purchase NOT shown ✅
```

**Now Test Invoice:**
1. Go to **Create Invoice**
2. Select **Jeans** item
3. Check badges

**Expected Result:**
```
GST: X units (old stock) | Non-GST: 20 units (new purchase)
```

4. Try creating **Taxable invoice** for 25 units (more than GST stock)

**Expected Result:**
```
❌ Error: Cannot create GST invoice - insufficient GST stock.

Requested: 25 units
GST Stock Available: X units
Non-GST Stock: 20 units

⚠️ Items purchased WITHOUT GST cannot be sold WITH GST invoice.

Options:
1. Reduce quantity to X units (GST stock available)
2. Create non-GST invoice (kaccha bill) for this sale
3. Later create Credit Adjustment invoice for compliance
```

---

### Test 4: GSTR-3B Report (Input Tax Credit)

**Setup:**
```
Purchase Bill #1:
- Vendor: Registered (GST toggle ON)
- Jeans: ₹10,000 + ₹1,200 GST

Purchase Bill #2:
- Vendor: Unregistered (GST toggle OFF)
- Shirts: ₹5,000 (no GST)
```

**Test Steps:**
1. Go to **GST Reports** → **GSTR-3B**
2. Select date range covering both purchases
3. Check **Inward Supplies (ITC)** section

**Expected Result:**
```
✅ Purchase Bill #1: Shown (₹10,000 + ₹1,200 GST)
❌ Purchase Bill #2: NOT shown (gst_applicable = FALSE)

Total ITC Available: ₹1,200 only
```

---

### Test 5: GSTR-1 Report (Output Tax)

**Setup:**
```
Invoice #1: Taxable (GST invoice)
- Total: ₹5,000 + ₹600 GST

Invoice #2: Non-taxable (Kaccha bill)
- Total: ₹3,000 (no GST)

Invoice #3: Credit Adjustment
- Taxable value: ₹2,500
- GST: ₹300
```

**Test Steps:**
1. Go to **GST Reports** → **GSTR-1**
2. Select date range covering all invoices
3. Check **Outward Supplies** section

**Expected Result:**
```
✅ Invoice #1: Shown (₹5,000 + ₹600)
❌ Invoice #2: NOT shown (non_taxable)
✅ Invoice #3: Shown (₹2,500 + ₹300)

Total Output Tax: ₹900 (₹600 + ₹300)
```

---

### Test 6: Commission/Loyalty Exclusion

**Setup:**
```
Customer: Rahul (Loyalty enabled)
Commission Agent: Agent A (5% commission)
```

**Test A: Normal Taxable Invoice**
1. Create taxable invoice for ₹10,000
2. Select commission agent (5%)
3. Save and approve

**Expected Result:**
```
✅ Commission: ₹500 recorded
✅ Loyalty: Points credited to customer
```

**Test B: Credit Adjustment Invoice**
1. Create credit adjustment invoice for ₹10,000
2. Select commission agent (5%)
3. Save and approve

**Expected Result:**
```
❌ Commission: NOT recorded (skipped)
❌ Loyalty: NO points credited (skipped)

Why? Already processed in original kaccha bill
```

---

### Test 7: Profit & Loss vs GST Reports

**Setup:**
```
Scenario: Buy and sell with mixed GST status

Purchase:
- Item A: ₹1,000 (WITH GST) → purchased_with_gst = TRUE
- Item B: ₹500 (WITHOUT GST) → purchased_with_gst = FALSE

Sales:
- Item A: Sold for ₹1,500 (Taxable invoice)
- Item B: Sold for ₹700 (Non-taxable invoice)
```

**Test Steps:**
1. Check **GSTR-3B:**

**Expected:**
```
Inward: Only Item A (₹1,000) ✅
```

2. Check **GSTR-1:**

**Expected:**
```
Outward: Only Item A sale (₹1,500) ✅
```

3. Check **Profit & Loss:**

**Expected:**
```
Revenue: ₹2,200 (₹1,500 + ₹700) ✅
COGS: ₹1,500 (₹1,000 + ₹500) ✅
Gross Profit: ₹700 ✅

Shows EVERYTHING (complete picture)
```

4. Check **Balance Sheet:**

**Expected:**
```
All transactions shown (both GST and non-GST) ✅
```

---

## 🚨 CRITICAL VALIDATIONS

### What Should Be BLOCKED:
1. ❌ GST invoice for items purchased without GST
2. ❌ GST invoice for exempt items (gst_rate = 0)
3. ❌ Showing non-GST purchases in GSTR-3B
4. ❌ Showing non-taxable invoices in GSTR-1
5. ❌ Commission/loyalty for credit adjustment

### What Should Be ALLOWED:
1. ✅ Non-GST invoice for items purchased with GST
2. ✅ Credit adjustment after kaccha bill
3. ✅ Mixing GST and non-GST items in same purchase bill
4. ✅ Using existing inventory based on gst_rate field
5. ✅ All transactions in P&L/Balance Sheet/Trial Balance

---

## 📊 REPORT VERIFICATION

### GSTR-3B (Input Tax Credit)
```sql
-- Should show ONLY:
- Purchases where gst_applicable = TRUE
- Approved purchase bills only
- No unregistered vendor purchases
```

### GSTR-1 (Output Tax)
```sql
-- Should show ONLY:
- invoice_type = 'taxable'
- invoice_type = 'credit_adjustment'
- No non_taxable invoices
```

### P&L / Balance Sheet / Trial Balance
```sql
-- Should show EVERYTHING:
- All purchases (GST + non-GST)
- All sales (taxable + non-taxable)
- All expenses and income
- Complete business picture
```

---

## ✅ SUCCESS CRITERIA

After all tests pass, you should see:

1. **Existing inventory works** (uses gst_rate for classification)
2. **Exempt items blocked** from GST invoices
3. **Non-GST purchases** don't appear in GSTR-3B
4. **Non-taxable invoices** don't appear in GSTR-1
5. **Credit adjustment** skips commission/loyalty
6. **P&L shows everything**, GST reports show only GST transactions
7. **No errors** when creating invoices with legacy inventory

---

## 🐛 If Something Fails

1. Check browser console for JavaScript errors
2. Check server logs for backend errors
3. Verify database migration ran successfully
4. Check if item has opening_stock > 0
5. Check if item.gst_rate is set correctly

---

**Ready to test! Start with Test 1 (Existing Inventory) as it's the most important for your current setup.** 🚀

