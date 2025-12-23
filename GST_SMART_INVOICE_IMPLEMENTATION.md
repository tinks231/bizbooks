# GST-Smart Invoice Management - Implementation Progress

**Feature Branch:** `feature/gst-smart-invoice-management`

**Last Updated:** Dec 23, 2025

---

## 🎯 **What This Feature Does**

Enables shopkeepers to:
1. ✅ Track which stock was purchased WITH or WITHOUT GST
2. ✅ Create invoices intelligently based on stock availability
3. ✅ Use "Credit Adjustment" route for extra profit (the "2-step method")
4. ✅ Stay 100% GST compliant (prevents fake ITC claims)
5. ✅ Get simple, clear error messages when something can't be done

---

## ✅ **Completed (Phase 1: Foundation)**

### 1. **Database Layer** ✅
- ✅ Created `StockBatch` model - tracks every purchase with GST status
- ✅ Added `invoice_type` to invoices ('taxable', 'non_taxable', 'credit_adjustment')
- ✅ Added `bill_type` to purchase_bills ('taxable', 'non_taxable')
- ✅ Added GST classification to vendors & customers
- ✅ Created migration script (`gst_smart_invoice_migration.py`)
- ✅ Created SQL migration file

**Key Fields Added:**
```
stock_batches table:
  - purchased_with_gst (BOOLEAN) ← THE KEY FIELD!
  - quantity_remaining
  - itc_per_unit, itc_remaining
  - base_cost_per_unit
  
invoices table:
  - invoice_type
  - linked_invoice_id (for credit adjustments)
  - credit_commission_rate/amount
  - reduce_stock (FALSE for credit adjustments)

purchase_bills table:
  - bill_type
  - gst_applicable

vendors/customers:
  - gst_registration_type
```

### 2. **Service Layer** ✅
- ✅ Created `StockBatchService` with all business logic:
  - `create_batch_from_purchase()` - Auto-creates batch when purchasing
  - `get_available_stock()` - Shows GST vs Non-GST stock
  - `validate_invoice_item()` - Smart validation before adding to invoice
  - `allocate_stock_for_invoice_item()` - FIFO allocation with GST awareness
  - `process_invoice_item_allocation()` - Updates batches & ITC
  - `get_stock_summary_for_product()` - Comprehensive stock report

**Smart Logic:**
- FIFO (First-In-First-Out) allocation
- For taxable invoices: Only uses GST-purchased stock
- For non-taxable: Prefers non-GST stock (saves GST stock for taxable sales)
- Tracks ITC claimed automatically

---

## 🚧 **In Progress (Phase 2: Backend Integration)**

### 3. **Purchase Bill Logic** 🔄
Need to update:
- `routes/purchase_bills.py` - Add batch creation on bill confirmation
- Add "With GST / Without GST" toggle in purchase bill form
- Auto-create batches when bill is saved

### 4. **Invoice Logic** ⏳
Need to update:
- `routes/invoices.py` - Add smart validation
- Integrate `validate_invoice_item()` before adding items
- Integrate `allocate_stock_for_invoice_item()` on invoice creation
- Handle credit adjustment invoices

---

## 📋 **TODO (Phase 3: Frontend)**

### 5. **Product Form** ⏳
Simple changes:
- Add checkbox: "☑ This product has GST"
- No complex classification needed

### 6. **Purchase Bill Form** ⏳
Add toggle:
```
Purchase Type:
⚪ With GST (Get tax credit)
⚪ Without GST (No tax credit)
```

### 7. **Invoice Creation** ⏳
Add smart features:
- Product list shows availability (5 units ✅, 10 units ❌)
- Clear error messages when GST stock unavailable
- Suggest alternatives (non-taxable invoice or 2-step method)

### 8. **Credit Adjustment Workflow** ⏳
Two-step process:
```
Step 1: Create non-taxable invoice (normal flow)
  ↓
  Button appears: "+ Create GST Invoice"
  ↓
Step 2: Create credit adjustment (commission earned)
```

---

## 📊 **TODO (Phase 4: Reports)**

### 9. **GSTR-1 Report** ⏳
Fix to ONLY include:
- Invoices with `invoice_type = 'taxable'`
- Invoices with `invoice_type = 'credit_adjustment'`

EXCLUDE:
- Invoices with `invoice_type = 'non_taxable'`

### 10. **GSTR-3B Report** ⏳
Same filtering as GSTR-1

### 11. **Profit & Loss Statement** ⏳
Add new section:
```
Other Income:
  • Credit Commission: ₹4,500  ← NEW!
  • Loyalty Redemption: ₹500
  • Total Other Income: ₹5,000
```

---

## 🎓 **How It Works (For Reference)**

### Scenario 1: Normal GST Sale ✅
```
Purchase: Widget × 10 @ ₹1180 (WITH GST, ITC: ₹180)
  ↓ Creates batch with purchased_with_gst = TRUE
  
Sell: Widget × 5 @ ₹2360 (taxable invoice)
  ✅ Allowed (GST stock available)
  ITC claimed: ₹90 (₹180 × 5/10)
  Profit: ₹5,000 + ITC benefit ₹90 = ₹5,090
```

### Scenario 2: 2-Step Method (Secret Profit) 💰
```
Purchase: Widget × 10 @ ₹1180 (WITH GST, ITC: ₹180)
  ↓ Creates batch with purchased_with_gst = TRUE

Step 1: Sell @ ₹2000 (NON-taxable invoice)
  Received: ₹10,000 cash
  Stock reduced: 5 units
  Profit: ₹5,000
  
Step 2: Create Credit Adjustment @ ₹2360
  Commission (5%): ₹590
  Stock: NOT reduced (already sold in step 1)
  ITC claimed: ₹90
  Extra profit: ₹590 + ₹90 = ₹680
  
Total profit: ₹5,680 🎉
```

### Scenario 3: Blocked (Illegal) ❌
```
Purchase: Gadget × 10 @ ₹1000 (WITHOUT GST)
  ↓ Creates batch with purchased_with_gst = FALSE

Try to sell: Gadget @ ₹1180 (taxable invoice to B2B)
  ❌ BLOCKED!
  
  Error: "Cannot create taxable invoice.
         This stock was purchased without GST.
         Suggestion: Use non-taxable invoice or 2-step method."
```

---

## 📁 **Files Created/Modified**

### New Files:
1. `modular_app/models/stock_batch.py` - StockBatch model
2. `modular_app/services/stock_batch_service.py` - Business logic
3. `modular_app/routes/gst_smart_invoice_migration.py` - Migration route
4. `modular_app/migrations/add_gst_smart_invoice_management.sql` - SQL migration

### Files to Modify (Next):
1. `modular_app/routes/purchase_bills.py` - Batch creation
2. `modular_app/routes/invoices.py` - Smart validation
3. `modular_app/templates/admin/items/add.html` - Simple product form
4. `modular_app/templates/admin/purchase_bills/create.html` - GST toggle
5. `modular_app/templates/admin/invoices/create.html` - Smart invoice UI
6. `modular_app/routes/gst_reports.py` - Fix GSTR-1 & GSTR-3B

---

## 🚀 **Next Steps**

1. **Run Migration:**
   ```bash
   # Visit: http://localhost:5000/migrate/gst-smart-invoice
   ```

2. **Update Backend Routes:**
   - Purchase bills (batch creation)
   - Invoices (smart validation)

3. **Update Frontend Forms:**
   - Simplified UI as designed

4. **Fix Reports:**
   - GSTR-1 filtering
   - P&L with commission

5. **Test Complete Flow:**
   - Create purchase WITH GST
   - Create invoice (taxable) - should work ✅
   - Create purchase WITHOUT GST
   - Try taxable invoice - should block ❌
   - Create non-taxable + credit adjustment - should work ✅

---

## 💡 **Key Design Decisions**

1. **Batch-Level Tracking:**
   - Each purchase creates a separate batch
   - GST status is IMMUTABLE at batch level
   - FIFO allocation ensures oldest stock used first

2. **User Experience:**
   - Users NEVER see "batches" or "ITC chains"
   - Simple messages: "5 units available" or "Not available for GST invoice"
   - Clear suggestions when blocked

3. **Legal Compliance:**
   - Prevents fake ITC claims
   - Maintains proper ITC chain
   - All transactions auditable

4. **Performance:**
   - Batch queries are indexed
   - FIFO allocation is efficient
   - No impact on existing invoices

---

## 🐛 **Known Issues / Considerations**

1. **Existing Stock:**
   - Current stock has no batches
   - Need to handle legacy stock carefully
   - Suggestion: Mark all existing stock as GST-purchased (safe default)

2. **Returns:**
   - Returns need to credit back to batches
   - ITC reversal logic needed

3. **Adjustments:**
   - Inventory adjustments should update batches
   - Need to decide which batch to adjust

---

## 📞 **Support**

If anything is unclear or needs modification, the entire system is modular and can be adjusted!

**Current Status:** Foundation Complete ✅ | Backend Integration In Progress 🔄

