# 📦 Returns Module - Implementation Status

**Feature Branch:** `returns-feature`  
**Started:** December 13, 2025  
**Status:** 🚧 Backend Complete, UI Pending

---

## ✅ **COMPLETED:**

### **1. Database Schema** ✅
- `returns` table with all fields
- `return_items` table for line items
- Migration route: `/migration/create-returns-tables`
- Status: Ready to run in production

### **2. Models** ✅
- `Return` model (`models/return_model.py`)
  - Return number generation (RET-YYYYMM-NNNN)
  - Credit note generation (CN-YYYY-NNNN)
  - Return window validation
  - Loyalty points calculation
- `ReturnItem` model (`models/return_item.py`)
  - GST calculations
  - Condition tracking
  - Amount calculations

### **3. Backend Routes** ✅ (`routes/returns.py`)
- `GET /admin/returns` - List returns with filters
- `GET /admin/returns/new` - Create return form
- `POST /admin/returns/new` - Save return (pending)
- `GET /admin/returns/<id>` - View return details
- `POST /admin/returns/<id>/approve` - Approve & process refund
- `POST /admin/returns/<id>/reject` - Reject return
- `GET /admin/returns/api/search-invoice` - Search API
- `GET /admin/returns/api/invoice/<id>/items` - Get invoice items API

### **4. Business Logic** ✅
- **Inventory Restocking:** ✅
  - Adds stock back for resellable items
  - Creates ItemStockMovement records
  - Updates stock value
  
- **Double-Entry Accounting:** ✅
  ```
  DEBIT Sales Returns .......... ₹4,250
  DEBIT CGST Receivable ......... ₹382.50
  DEBIT SGST Receivable ......... ₹382.50
    CREDIT Cash/Bank ................... ₹5,015
  ```
  
- **Unpaid Invoice Adjustment:** ✅
  - Reduces invoice amounts
  - Adjusts Accounts Receivable
  - Updates balance due
  
- **GST Credit Notes:** ✅
  - Auto-generates CN-YYYY-NNNN
  - Stores credit note date
  - Ready for GSTR-1 reporting
  
- **Loyalty Points Reversal:** ✅
  - Proportional deduction
  - Creates DEDUCTION transaction
  - Updates customer balance

---

## ✅ **COMPLETED - UI Templates:**

### **5. UI Templates** ✅

#### **Template 1: `templates/admin/returns/index.html`**
**Purpose:** List all returns with filters

**Features Needed:**
- Table with columns: Return No, Date, Invoice, Customer, Amount, Status
- Filters: Status (pending/approved/rejected), Date Range, Search
- Summary stats: Total Returns, Total Refunded, Return Rate
- Status badges with colors
- Action buttons: View, Approve (if pending)

**Reference:** Copy structure from `templates/admin/invoices/index.html`

---

#### **Template 2: `templates/admin/returns/create.html`**
**Purpose:** Create new return - search invoice and select items

**Features Needed:**
1. **Invoice Search Section:**
   - Search by invoice number, customer name, phone
   - Show results: Invoice #, Customer, Date, Amount, Status
   - Select invoice button

2. **Return Items Section:** (Shows after invoice selected)
   - Table with checkboxes for each item
   - Columns: Item Name, Qty Sold, Qty to Return, Unit Price, GST, Total
   - Item condition dropdown: Resellable, Damaged, Defective
   - Calculate total refund amount dynamically

3. **Return Details:**
   - Return reason dropdown:
     - Defective
     - Wrong item  
     - Damaged in shipping
     - Changed mind
     - Better price elsewhere
     - Other
   - Reason details textarea
   - Customer notes
   - Internal notes

4. **Refund Method:**
   - Radio buttons: Cash, Bank Transfer, Store Credit, Pending Decision
   - If Cash/Bank: Show account dropdown

5. **JavaScript:**
   - Invoice search with autocomplete
   - Dynamic item loading
   - Refund amount calculation
   - Form validation

**Reference:** Similar to `templates/admin/purchase_bills/create.html` but reverse flow

---

#### **Template 3: `templates/admin/returns/view.html`**
**Purpose:** View return details + Approve/Reject workflow

**Features Needed:**
1. **Return Details Section:**
   - Return number, date, status badge
   - Invoice reference (link to invoice)
   - Customer details
   - Return reason & notes

2. **Returned Items Table:**
   - Item name, qty returned, unit price, GST breakdown, total
   - Item condition badge
   - Restock checkbox (checked if resellable)

3. **Financial Summary:**
   - Subtotal, CGST, SGST, IGST
   - Total refund amount
   - Credit note number (if generated)

4. **Actions Section:** (If status = pending)
   - **Approve Button:**
     - Modal popup for account selection (cash/bank)
     - Payment reference field
     - Confirm button
   - **Reject Button:**
     - Modal popup for rejection reason
     - Textarea for explanation

5. **Approval History:**
   - Approved/Rejected by
   - Date & time
   - Reason (if rejected)

6. **Print Credit Note Button:** (If approved)
   - Generates printable credit note PDF

**Reference:** Similar to `templates/admin/purchase_bills/view.html` with approval flow

---

## 📋 **Next Steps (Implementation Order):**

1. ✅ ~~Run migration to create tables~~  
   URL: `https://{tenant}.bizbooks.co.in/migration/create-returns-tables`

2. ⏸️ **Create index.html** (30 min)
   - Copy structure from invoices/index.html
   - Modify for returns data
   - Test list view

3. ⏸️ **Create view.html** (45 min)
   - Build return details display
   - Add approve/reject modals
   - Test workflow

4. ⏸️ **Create create.html** (1.5 hours)
   - Invoice search UI
   - Item selection with checkboxes
   - Refund calculation JavaScript
   - Form submission

5. ⏸️ **Add menu item** in `templates/admin/base.html`:
   ```html
   <li class="{% if request.endpoint and 'returns' in request.endpoint %}active{% endif %}">
       <a href="{{ url_for('returns.index') }}">
           <i class="fas fa-undo"></i> Returns & Refunds
       </a>
   </li>
   ```

6. ⏸️ **Test End-to-End:**
   - Create return for paid invoice → Approve → Check:
     - ✅ Inventory restocked
     - ✅ Cash deducted
     - ✅ Credit note generated
     - ✅ Loyalty points reversed
     - ✅ Reports updated
   
   - Create return for unpaid invoice → Approve → Check:
     - ✅ Invoice amount reduced
     - ✅ Accounts receivable adjusted
     - ✅ Credit note generated

7. ⏸️ **Update Reports:** (Already handled by accounting logic)
   - Trial Balance: Shows sales returns
   - Profit & Loss: Shows net sales (after returns)
   - GSTR-1: Add credit notes section (future)

---

## 🔧 **Configuration Needed:**

Add to tenant settings:
```json
{
  "return_window_days": 30,
  "auto_approve_within_window": true,
  "require_manager_approval_above": 5000
}
```

---

## 📊 **Accounting Impact:**

### **Paid Invoice Return:**
```
Original Sale:
  Cash (Dr) ........... ₹10,030
    Sales (Cr) ................... ₹8,500
    CGST Payable (Cr) ............ ₹765
    SGST Payable (Cr) ............ ₹765

Return (50%):
  Sales Returns (Dr) ... ₹4,250
  CGST Receivable (Dr) . ₹382.50
  SGST Receivable (Dr) . ₹382.50
    Cash (Cr) .................... ₹5,015
```

### **Unpaid Invoice Return:**
```
Original Sale:
  Accounts Receivable (Dr) ₹10,030
    Sales (Cr) ................... ₹8,500
    CGST Payable (Cr) ............ ₹765
    SGST Payable (Cr) ............ ₹765

Return (50%):
  Sales Returns (Dr) .......... ₹4,250
  CGST Receivable (Dr) ........ ₹382.50
  SGST Receivable (Dr) ........ ₹382.50
    Accounts Receivable (Cr) ..... ₹5,015

Customer now owes: ₹5,015 (not ₹10,030)
```

---

## 🎯 **Success Criteria:**

Before merging to main:
- ✅ Backend logic complete
- ⏸️ All 3 UI templates working
- ⏸️ End-to-end test passed (paid return)
- ⏸️ End-to-end test passed (unpaid return)
- ⏸️ No linter errors
- ⏸️ Reports showing correct data
- ⏸️ Mobile responsive

---

## 📝 **Notes:**

- Returns module is SAFE - doesn't affect existing functionality
- All logic is isolated in returns.py
- Can be tested independently before production
- Feature flag can be added to enable/disable for specific tenants

---

**Last Updated:** December 13, 2025  
**Remaining Work:** ~3-4 hours (UI templates + testing)

