# 🧾 GST Invoice Feature Guide

## **✅ What We Built (So Far)**

### **Phase 1: Backend & Database (COMPLETE)**

**Database Models Created:**
1. **Invoice** - Main invoice table
2. **InvoiceItem** - Line items for each invoice

**Features Included:**
- ✅ GST calculations (CGST/SGST for same state, IGST for inter-state)
- ✅ Auto invoice numbering (INV-2024-0001, INV-2024-0002, etc.)
- ✅ Customer details (name, phone, email, address, GSTIN)
- ✅ Multiple payment statuses (unpaid, partial, paid)
- ✅ Draft and sent status
- ✅ Stock reduction when invoice is finalized
- ✅ Round-off calculation
- ✅ Payment tracking
- ✅ Tenant-specific settings (GST number, address, etc.)

---

## **📊 How GST Works in India**

### **GST Calculation Logic:**

#### **Same State Transaction:**
```
Customer State = Tenant State (e.g., both in Maharashtra)

Subtotal:        ₹1000
CGST (9%):       ₹90    (Central GST - Central Govt)
SGST (9%):       ₹90    (State GST - State Govt)
─────────────────────
Total:           ₹1180  (18% total GST)
```

#### **Inter-State Transaction:**
```
Customer State ≠ Tenant State (e.g., Maharashtra → Karnataka)

Subtotal:        ₹1000
IGST (18%):      ₹180   (Integrated GST - Central Govt)
─────────────────────
Total:           ₹1180  (18% total GST)
```

**Your system automatically:**
- Detects customer's state vs tenant's state
- Applies CGST+SGST or IGST accordingly
- Calculates all amounts correctly

---

## **🗂️ Database Structure**

### **invoices Table:**

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| tenant_id | Integer | Which business |
| invoice_number | String | INV-2024-0001 |
| invoice_date | Date | Date of invoice |
| due_date | Date | Payment due date (optional) |
| customer_name | String | Customer name |
| customer_phone | String | Contact number |
| customer_email | String | Email address |
| customer_address | Text | Full address |
| customer_gstin | String | Customer's GST number (optional) |
| customer_state | String | For GST calculation |
| subtotal | Float | Before tax amount |
| cgst_amount | Float | Central GST (same state) |
| sgst_amount | Float | State GST (same state) |
| igst_amount | Float | Integrated GST (inter-state) |
| discount_amount | Float | Any discount |
| round_off | Float | To make round number |
| total_amount | Float | Final amount |
| payment_status | String | unpaid/partial/paid |
| paid_amount | Float | Amount received |
| payment_method | String | Cash/UPI/Card/Bank |
| notes | Text | Terms & conditions |
| internal_notes | Text | Private notes |
| status | String | draft/sent/paid/cancelled |
| created_at | DateTime | Auto timestamp |
| updated_at | DateTime | Auto timestamp |

### **invoice_items Table:**

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| invoice_id | Integer | Links to invoice |
| item_id | Integer | From inventory (optional) |
| item_name | String | Product/service name |
| description | Text | Additional details |
| hsn_code | String | HSN/SAC code for GST |
| quantity | Float | Qty sold |
| unit | String | Nos/Kg/Ltr/Mtr |
| rate | Float | Price per unit |
| gst_rate | Float | 0/5/12/18/28% |
| taxable_value | Float | qty × rate |
| cgst_amount | Float | Central GST |
| sgst_amount | Float | State GST |
| igst_amount | Float | Integrated GST |
| total_amount | Float | With tax |

---

## **🎯 Routes Available**

### **Invoice Management:**

```
GET  /admin/invoices                    → List all invoices
GET  /admin/invoices/create             → Create new invoice form
POST /admin/invoices/create             → Save new invoice
GET  /admin/invoices/<id>               → View invoice details
GET  /admin/invoices/<id>/edit          → Edit invoice (draft only)
POST /admin/invoices/<id>/edit          → Update invoice
POST /admin/invoices/<id>/mark-sent     → Finalize invoice & reduce stock
POST /admin/invoices/<id>/record-payment → Record payment received
POST /admin/invoices/<id>/delete        → Delete draft invoice
GET  /admin/invoices/settings           → Configure GST, address, etc.
POST /admin/invoices/settings           → Save settings
```

---

## **⚙️ Invoice Settings (Tenant Configuration)**

**What's stored in `tenants.settings` (JSON):**

```json
{
  "gstin": "27XXXXX1234X1Z5",
  "pan": "ABCDE1234F",
  "address": "123 MG Road, Shivaji Nagar",
  "city": "Pune",
  "state": "Maharashtra",
  "pincode": "411001",
  "website": "www.mahaveerelectricals.com",
  "invoice_terms": "Payment due within 30 days",
  "invoice_footer": "Thank you for your business!"
}
```

**These appear on printed invoices automatically!**

---

## **🔄 Invoice Workflow**

### **Step 1: Create Draft Invoice**
```
Admin → Create Invoice → Add Items → Save as Draft
```
**Status:** `draft`
**Stock:** Not affected yet
**Can:** Edit, delete, add/remove items

### **Step 2: Finalize (Mark as Sent)**
```
Admin → View Invoice → Mark as Sent
```
**Status:** `sent`
**Stock:** Reduced automatically
**Can:** Record payments (cannot edit anymore!)

### **Step 3: Record Payments**
```
Admin → View Invoice → Record Payment
```
**Payment Status:** `unpaid` → `partial` → `paid`
**Tracks:** How much paid, payment method

---

## **💡 Key Features**

### **1. Inventory Integration**
- ✅ Items can be selected from inventory
- ✅ Auto-fills: Item name, current stock level, last selling price
- ✅ Stock reduces when invoice is finalized
- ✅ Or enter items manually (for services)

### **2. Automatic Calculations**
```python
# System automatically calculates:
taxable_value = quantity × rate
gst_amount = taxable_value × (gst_rate / 100)

if same_state:
    cgst = gst_amount / 2
    sgst = gst_amount / 2
    igst = 0
else:
    cgst = 0
    sgst = 0
    igst = gst_amount

total = taxable_value + cgst + sgst + igst
```

### **3. Smart Invoice Numbering**
```python
# Auto-generates:
INV-2024-0001  (First invoice of 2024)
INV-2024-0002  (Second invoice)
...
INV-2025-0001  (Resets for new year)
```

### **4. Payment Tracking**
- Supports partial payments
- Multiple payment methods (Cash, UPI, Bank, Card, Cheque)
- Tracks outstanding amounts
- Payment history

---

## **📝 What's Next? (Templates Needed)**

### **Phase 2: Frontend Templates (TODO)**

**Need to create these templates:**

1. **list.html** - Invoice listing page
   - Table view of all invoices
   - Filters (status, payment, date range)
   - Stats cards (total revenue, pending, paid)
   - Search functionality

2. **create.html** - Create new invoice
   - Customer details form
   - Dynamic item rows (add/remove)
   - Inventory dropdown (autocomplete)
   - Live GST calculation
   - Preview before saving

3. **view.html** - View invoice details
   - Print-ready layout
   - Company header (logo, GST, address)
   - Invoice items table
   - Tax breakdown (CGST/SGST or IGST)
   - Payment status
   - Actions (Mark sent, Record payment, Edit, Delete)

4. **edit.html** - Edit draft invoice
   - Same as create, but pre-filled
   - Only for draft invoices

5. **settings.html** - Configure invoice settings
   - Company details (name, address, GST)
   - Logo upload
   - Default terms & conditions
   - Invoice footer text

6. **PDF Generation** (Optional but recommended)
   - Generate PDF invoices
   - Professional format
   - Email to customer
   - Download option

---

## **🚀 Migration Guide**

### **For Existing Tenants:**

**Step 1: Run Migration**
```
Visit: https://yoursite.bizbooks.co.in/migrate/add-invoices
```

**Step 2: Configure Settings**
```
Visit: /admin/invoices/settings
Fill in:
- GST Number (GSTIN)
- PAN Card Number
- Business Address
- State (for GST calculation)
- Website, Email, Phone
- Invoice footer text
```

**Step 3: Start Creating Invoices!**
```
Visit: /admin/invoices/create
```

---

## **💰 Accounting Integration (Future)**

### **How Invoices Connect to Ledger:**

**When invoice is created:**
```
Customer Account         (Debit)   ₹2360
    Sales Revenue        (Credit)  ₹2000
    CGST Payable        (Credit)  ₹180
    SGST Payable        (Credit)  ₹180
```

**When payment is received:**
```
Cash/Bank Account        (Debit)   ₹2360
    Customer Account     (Credit)  ₹2360
```

**This will be implemented in Phase 3: Ledger Feature!**

---

## **📊 Reports (Can Be Added)**

### **Invoice Reports (Future Enhancement):**

1. **Sales Summary**
   - Daily/Monthly/Yearly sales
   - Revenue trends
   - Top customers

2. **GST Reports**
   - CGST collected
   - SGST collected
   - IGST collected
   - Ready for GST filing (GSTR-1)

3. **Outstanding Payments**
   - Pending invoices
   - Overdue invoices
   - Customer-wise outstanding

4. **Profitability**
   - Sales vs Cost of Goods Sold
   - Gross profit margin
   - Net profit

---

## **🎨 Invoice Print Format**

### **Standard Indian GST Invoice Format:**

```
┌──────────────────────────────────────────────────────────────┐
│                    [COMPANY LOGO]                            │
│                 MAHAVEER ELECTRICALS                         │
│            123 MG Road, Shivaji Nagar, Pune                  │
│            Maharashtra - 411001                              │
│            GSTIN: 27XXXXX1234X1Z5                           │
│            Tel: 020-12345678 | Email: info@example.com      │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│  TAX INVOICE                                                 │
├──────────────────────────────────────────────────────────────┤
│  Invoice No: INV-2024-0001        Date: 30-Oct-2024         │
│  Due Date: 29-Nov-2024                                       │
│                                                              │
│  Bill To:                                                    │
│  Sharma Builders                                             │
│  456 FC Road, Pune - 411004                                  │
│  GSTIN: 27YYYYY5678Y1Z9                                     │
│  Contact: 9876543210                                         │
├──────────────────────────────────────────────────────────────┤
│  Sr  Description      HSN    Qty  Unit  Rate    Amount      │
│  ──  ───────────────  ─────  ───  ────  ─────  ─────────   │
│  1   LED Bulb 9W      9405   10   Nos   100.00  1,000.00   │
│  2   Wire 2.5mm       8544   50   Mtr   20.00   1,000.00   │
│                                                              │
│                                   Subtotal:      2,000.00   │
│                                   CGST @ 9%:       180.00   │
│                                   SGST @ 9%:       180.00   │
│                                   Round Off:         0.00   │
│                                   ──────────────  ────────  │
│                                   Total Amount:   2,360.00  │
│                                                              │
│  Amount in Words: Two Thousand Three Hundred Sixty Only      │
│                                                              │
│  Payment Method: UPI                                         │
│  Status: Paid                                                │
├──────────────────────────────────────────────────────────────┤
│  Terms & Conditions:                                         │
│  - Payment due within 30 days                                │
│  - Goods once sold will not be taken back                    │
│                                                              │
│  Thank you for your business!                                │
│                                                              │
│  ___________________                                         │
│  Authorized Signature                                        │
└──────────────────────────────────────────────────────────────┘
```

---

## **❓ FAQs**

### **Q: Do I need to register for GST?**
**A:** If your annual turnover exceeds ₹40 lakhs (₹20 lakhs for services), GST registration is mandatory.

### **Q: What if my customer doesn't have GSTIN?**
**A:** No problem! Customer GSTIN is optional. You still charge GST and issue invoice.

### **Q: Can I edit invoices after sending?**
**A:** No. Once an invoice is marked as "sent", it's finalized (stock reduced). You can only record payments or cancel it.

### **Q: What if I made a mistake in a sent invoice?**
**A:** Create a credit note (future feature) or cancel and create new invoice with correct details.

### **Q: Can I use different GST rates for different items?**
**A:** Yes! Each item can have 0%, 5%, 12%, 18%, or 28% GST as per GST slabs.

### **Q: Do I need HSN codes?**
**A:** HSN codes are mandatory for goods if turnover > ₹5 crores. Optional but recommended for everyone.

### **Q: Can I add my company logo?**
**A:** Yes! Upload in Invoice Settings (template will support this).

---

## **🎯 Summary for You:**

### **What's Ready:**
✅ Complete backend logic
✅ Database tables
✅ All routes and calculations
✅ GST compliance built-in
✅ Inventory integration
✅ Payment tracking
✅ Migration script

### **What's Needed (Next Step):**
⏳ Templates (list, create, edit, view, settings)
⏳ PDF generation (optional)
⏳ Email invoice to customer (optional)

### **Timeline:**
📅 Templates: 2-3 hours of work
📅 PDF generation: 1 hour (if needed)
📅 Email feature: 30 minutes (already have email setup!)

---

## **🚀 Quick Start (After Templates Are Ready):**

1. **Run Migration:**
   ```
   Visit: /migrate/add-invoices
   ```

2. **Configure Your Business:**
   ```
   Go to: /admin/invoices/settings
   Add: GST number, address, etc.
   ```

3. **Create First Invoice:**
   ```
   Go to: /admin/invoices/create
   Select items from inventory or enter manually
   Save as draft → Review → Mark as sent
   ```

4. **Track Payments:**
   ```
   Go to: /admin/invoices
   Click invoice → Record Payment
   ```

---

## **💡 Business Value:**

**For Small Businesses:**
- ✅ Professional GST-compliant invoices
- ✅ Auto stock tracking
- ✅ Payment tracking
- ✅ No manual calculations
- ✅ Ready for GST filing

**For BizBooks (You):**
- ✅ Major competitive advantage
- ✅ Justifies higher pricing (₹999-1499/month)
- ✅ Reduces churn (businesses need invoicing!)
- ✅ Complete business management suite

---

**Want to proceed with creating the templates? Or do you have questions about the GST calculations / invoice logic?** 🎯

