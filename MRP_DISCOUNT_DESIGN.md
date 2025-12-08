# 💰 MRP & Discount Features - Design Discussion

**Created:** Dec 7, 2025  
**Branch:** `feature/mrp-and-discount`  
**Status:** Design & Discussion Phase

---

## 📊 Current State

### Items/Inventory:
- ✅ `cost_price` (buying price)
- ✅ `selling_price` (actual selling price)
- ✅ `gst_rate` (tax rate)
- ❌ **No MRP field**
- ❌ **No discount tracking**

### Invoices/Bills:
- ✅ Flat discount: "Discount: ₹100"
- ❌ No percentage-based discount
- ❌ No item-level discount
- ❌ No MRP display

---

## 🎯 Feature 1: MRP (Maximum Retail Price)

### What is MRP?
- **Legal Requirement in India:** Product packages must show MRP
- **Customer Transparency:** Customers know the maximum legal price
- **Discount Calculation:** Automatically calculate discount % from MRP

### Use Cases:

#### 1. Retail Store (Mahaveer Electricals)
```
Product: Bajaj Ceiling Fan
MRP: ₹2,500 (printed on box)
Selling Price: ₹2,200 (actual selling price)
Discount: 12% (auto-calculated)
```

#### 2. Invoice Display:
```
Item                MRP         Selling Price    Discount
----------------------------------------------------------
Bajaj Ceiling Fan   ₹2,500      ₹2,200          12% OFF
Havells Wire 100m   ₹1,200      ₹1,000          16.67% OFF
                                Subtotal:        ₹3,200
                                GST (18%):       ₹576
                                Total:           ₹3,776
```

### Design Questions:

**Q1: Should MRP be mandatory or optional?**
- **Option A (Recommended):** Optional - Not all products have MRP (services, bulk items)
- **Option B:** Mandatory - Strict compliance

**Q2: Should MRP be editable after setting?**
- **Option A (Recommended):** Yes - MRP can change when new stock arrives
- **Option B:** No - Lock MRP once set

**Q3: Should we show MRP on all invoices?**
- **Option A (Recommended):** Show only if MRP is set
- **Option B:** Always show (show "N/A" if not set)
- **Option C:** Admin setting to toggle MRP display

**Q4: Where to add MRP field?**
- ✅ Item Add/Edit form (main inventory)
- ✅ Quick edit in invoice creation
- ✅ Bulk import Excel template

---

## 🎯 Feature 2: Discount System

### Current System:
```
Invoice total: ₹10,000
Discount: -₹500 (flat amount)
After discount: ₹9,500
GST: ₹1,710
Total: ₹11,210
```

### Proposed System:

#### Option A: Invoice-Level Discount (Recommended - Simpler)
```
Invoice total: ₹10,000
Discount Type: Percentage
Discount Value: 5%
Discount Amount: -₹500
After discount: ₹9,500
GST: ₹1,710
Total: ₹11,210
```

**Pros:**
- ✅ Simple to implement
- ✅ Covers 90% of use cases
- ✅ Easy for users to understand
- ✅ Matches existing GST calculation

**Cons:**
- ❌ Can't apply different discounts to different items

#### Option B: Item-Level Discount (Advanced)
```
Item                Qty    Rate      Disc%    After Disc    GST      Total
---------------------------------------------------------------------------
Bajaj Fan           1      ₹2,500    10%      ₹2,250       ₹405     ₹2,655
Havells Wire        5      ₹200      15%      ₹850         ₹153     ₹1,003
                                              Subtotal:     ₹3,100
                                              Total:        ₹3,658
```

**Pros:**
- ✅ Flexible - different discount per item
- ✅ Useful for bulk orders
- ✅ Better for promotional offers

**Cons:**
- ❌ More complex UI
- ❌ Harder for users to understand
- ❌ More development time

#### Option C: Hybrid (Best of Both)
```
- Item-level discount for individual items
- PLUS invoice-level discount for overall deal
```

**Pros:**
- ✅ Maximum flexibility
- ✅ Real-world scenarios covered

**Cons:**
- ❌ Most complex to implement
- ❌ Can confuse users

### Design Questions:

**Q1: Which discount system to implement first?**
- **Recommended:** Option A (Invoice-Level) → Add Option B later if needed

**Q2: Should we support both % and flat amount?**
- **Option A (Recommended):** Support both - let user choose
- **Option B:** Percentage only
- **Option C:** Flat amount only (current system)

**Q3: How to handle discount + GST?**
```
Scenario: Item ₹1,000, Discount 10%, GST 18%

Method 1: Discount first, then GST
  Subtotal: ₹1,000
  Discount: -₹100
  After discount: ₹900
  GST (18%): ₹162
  Total: ₹1,062

Method 2: GST first, then discount
  Subtotal: ₹1,000
  GST (18%): ₹180
  Subtotal + GST: ₹1,180
  Discount: -₹118
  Total: ₹1,062
```

**Recommended:** Method 1 (standard accounting practice)

**Q4: Should we track discount for reporting?**
- ✅ Yes - Show "Total Discounts Given" in reports
- ✅ Useful for analyzing sales patterns
- ✅ Track which customers get most discounts

---

## 📐 Database Schema Changes

### 1. Add MRP to Items:
```sql
ALTER TABLE items 
ADD COLUMN IF NOT EXISTS mrp NUMERIC(10, 2) DEFAULT NULL;

-- Optional: Add index for reporting
CREATE INDEX IF NOT EXISTS idx_items_mrp ON items(mrp);
```

### 2. Enhance Discount in Invoices:

**Option A: Invoice-Level Only**
```sql
ALTER TABLE sales_invoices 
ADD COLUMN IF NOT EXISTS discount_type VARCHAR(20) DEFAULT 'flat';
-- 'flat' or 'percentage'

ALTER TABLE sales_invoices 
ADD COLUMN IF NOT EXISTS discount_value NUMERIC(10, 2) DEFAULT 0;
-- If type='percentage': stores 10 (for 10%)
-- If type='flat': stores 100 (for ₹100)

-- Keep existing discount_amount column (calculated value)
```

**Option B: Item-Level Discount**
```sql
ALTER TABLE sales_invoice_items 
ADD COLUMN IF NOT EXISTS discount_percent NUMERIC(5, 2) DEFAULT 0;

ALTER TABLE sales_invoice_items 
ADD COLUMN IF NOT EXISTS discount_amount NUMERIC(10, 2) DEFAULT 0;
```

---

## 🎨 UI/UX Mockups

### Invoice Creation - Discount Section:

**Current:**
```
┌─────────────────────────────────────────┐
│ Subtotal:               ₹10,000.00      │
│ Discount:               -₹500.00   [✎]  │
│ GST (18%):              ₹1,710.00       │
│ ─────────────────────────────────────   │
│ Total:                  ₹11,210.00      │
└─────────────────────────────────────────┘
```

**Proposed (Option A):**
```
┌─────────────────────────────────────────┐
│ Subtotal:               ₹10,000.00      │
│                                          │
│ Discount:                                │
│   Type: [% Percentage ▾] [10.00]        │
│   Amount: -₹1,000.00 (auto-calculated)  │
│                                          │
│ After Discount:         ₹9,000.00       │
│ GST (18%):              ₹1,620.00       │
│ ─────────────────────────────────────   │
│ Total:                  ₹10,620.00      │
└─────────────────────────────────────────┘
```

### Item Form - MRP Field:

```
┌────────────────────────────────────────────┐
│ Basic Information                          │
│ ─────────────────────────────────────────  │
│ Item Name: [Bajaj Ceiling Fan           ] │
│ SKU:       [ITEM-00123] (auto-generated)   │
│ Category:  [Fans ▾]                        │
│                                            │
│ Pricing Information                        │
│ ─────────────────────────────────────────  │
│ Cost Price:    [₹1,800.00] (buying price)  │
│ MRP:           [₹2,500.00] ⓘ Optional      │
│ Selling Price: [₹2,200.00]                 │
│                                            │
│ 💡 Discount: 12% OFF from MRP              │
│    (Auto-calculated when MRP is set)       │
│                                            │
│ GST Rate: [18% ▾]                          │
└────────────────────────────────────────────┘
```

---

## 🚀 Implementation Plan

### Phase 1: MRP Field (2-3 hours)
1. ✅ Database migration (add `mrp` column)
2. ✅ Update Item model
3. ✅ Update Item Add/Edit forms
4. ✅ Update bulk import template
5. ✅ Test locally

### Phase 2: Invoice-Level Discount (3-4 hours)
1. ✅ Database migration (add `discount_type` and `discount_value`)
2. ✅ Update Invoice model
3. ✅ Update invoice creation UI
4. ✅ Update JavaScript calculations
5. ✅ Update invoice PDF/print template
6. ✅ Test all scenarios

### Phase 3: Display & Reports (2-3 hours)
1. ✅ Show MRP on invoices (if set)
2. ✅ Show discount % on invoices
3. ✅ Add discount column to sales reports
4. ✅ Add "Total Discounts Given" metric

### Total Estimated Time: 7-10 hours

---

## ✅ Testing Scenarios

### MRP Testing:
- [ ] Add item with MRP
- [ ] Add item without MRP (leave blank)
- [ ] Edit existing item to add MRP
- [ ] Bulk import items with MRP
- [ ] Create invoice - MRP should show if set
- [ ] Check discount % calculation

### Discount Testing:
- [ ] Invoice with percentage discount (10%)
- [ ] Invoice with flat discount (₹500)
- [ ] Invoice with 0% discount
- [ ] Invoice with 100% discount (free)
- [ ] Multiple items with invoice-level discount
- [ ] Verify GST calculation after discount
- [ ] Print invoice - discount should show correctly

---

## 🤔 Questions for You:

1. **MRP Field:**
   - Should it be optional or mandatory?
   - Do you want to show MRP on printed invoices?

2. **Discount System:**
   - Start with **Invoice-Level** (simpler) or **Item-Level** (advanced)?
   - Support both % and ₹ or just %?

3. **UI Preferences:**
   - Any specific design you prefer for discount input?
   - Should we show "You saved ₹X" message to customers?

4. **Business Logic:**
   - Can selling price be > MRP? (usually not allowed in India)
   - Minimum/maximum discount limits?

---

## 📝 Next Steps:

Once you confirm the design decisions above, we'll:
1. ✅ **COMPLETED:** Implement in this feature branch
2. 🔄 **IN PROGRESS:** Test locally at `http://mahaveerelectricals.bizbooks.local:5001`
3. Review and refine
4. Merge to main
5. Deploy to production

---

## ✅ Implementation Status (Dec 7, 2025)

### Completed Features:

#### 1. MRP Field ✅
- ✅ Database migration created (`/migrate/add-mrp-discount-gst-fields`)
- ✅ Item model updated with `mrp` field (nullable)
- ✅ Item add form: MRP input with validation
- ✅ Item edit form: MRP input with validation
- ✅ JavaScript validation: Blocks selling price > MRP
- ✅ Auto-calculates discount % from MRP
- ✅ Backend routes save MRP correctly

#### 2. Enhanced Discount System ✅
- ✅ Invoice model: Added `discount_type` and `discount_value`
- ✅ Invoice UI: Dropdown selector (% or ₹)
- ✅ JavaScript: Auto-calculates discount amount
- ✅ Supports both percentage and flat amount
- ✅ Hidden field stores calculated `discount_amount`
- ✅ Applies discount before GST calculation

#### 3. GST Toggle ✅
- ✅ Invoice model: Added `gst_enabled` field
- ✅ Customer model: Added `is_gst_customer` field
- ✅ Invoice UI: Checkbox to enable/disable GST
- ✅ JavaScript: Hides GST rows when disabled
- ✅ Calculation skips GST when unchecked
- ✅ Clean invoice for non-GST customers

### Files Modified:
1. `modular_app/routes/mrp_discount_migration.py` - Migration endpoint
2. `modular_app/models/item.py` - Added MRP field
3. `modular_app/models/invoice.py` - Added discount & GST fields
4. `modular_app/models/customer.py` - Added is_gst_customer
5. `modular_app/templates/admin/items/add.html` - MRP input & validation
6. `modular_app/templates/admin/items/edit.html` - MRP input & validation
7. `modular_app/routes/items.py` - Handle MRP in add/edit
8. `modular_app/templates/admin/invoices/create.html` - Enhanced discount & GST toggle
9. `modular_app/app.py` - Registered migration blueprint

### Testing Required:
- [ ] Run migration on local database
- [ ] Test MRP validation (selling price > MRP should be blocked)
- [ ] Test percentage discount (10% of ₹1000 = ₹100)
- [ ] Test flat discount (₹500 discount)
- [ ] Test GST toggle (enable/disable)
- [ ] Test non-GST invoice (no GST rows shown)
- [ ] Create invoice and verify database fields saved correctly

**Ready to test!** 🚀

