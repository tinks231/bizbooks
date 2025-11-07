# 📋 Purchase Bills - Future Enhancements

## 🎯 Priority Roadmap

### ✅ COMPLETED
- [x] Basic Purchase Bill CRUD
- [x] Vendor Management
- [x] Item Autocomplete
- [x] GST Calculation (CGST/SGST/IGST)
- [x] Multi-item Bills
- [x] Bill Numbering (Auto-increment)

### 🚀 IN PROGRESS / NEXT
- [ ] **Stock Receipt Integration (GRN)** - Critical for inventory accuracy
- [ ] **Payment Recording** - Track vendor payments and outstanding

---

## 📦 Stock Receipt Integration (Goods Receipt Note)

### Overview
Link Purchase Bills to actual inventory receipts. Track what was ordered vs. what arrived, handle partial deliveries, and automatically update stock levels.

### Features

#### 1. Goods Receipt Note (GRN) Creation
```
Purchase Bill #PB-001
├─ Item: LED Bulb 9W × 100 pcs @ ₹50 = ₹5,000
├─ Status: "Pending Receipt"
└─ Action: "Receive Goods" button

Create GRN #GRN-001
├─ Ordered: 100 pcs
├─ Received: 95 pcs
├─ Rejected: 5 pcs (damaged)
├─ Site: Main Warehouse
└─ QC Notes: "5 bulbs broken in transit"

Result:
├─ Stock Updated: +95 pcs at Main Warehouse
├─ Bill Status: "Received (Partial)"
└─ Movement History: Stock In (GRN-001)
```

#### 2. Database Schema
```sql
-- Goods Receipt Notes table
CREATE TABLE goods_receipt_notes (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL,
    grn_number VARCHAR(50) UNIQUE NOT NULL,
    grn_date DATE NOT NULL,
    purchase_bill_id INTEGER REFERENCES purchase_bills(id),
    site_id INTEGER REFERENCES sites(id),
    received_by VARCHAR(100),
    notes TEXT,
    status VARCHAR(20) DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- GRN Line Items
CREATE TABLE grn_items (
    id SERIAL PRIMARY KEY,
    grn_id INTEGER REFERENCES goods_receipt_notes(id),
    purchase_bill_item_id INTEGER REFERENCES purchase_bill_items(id),
    item_id INTEGER REFERENCES items(id),
    quantity_ordered DECIMAL(15,3),
    quantity_received DECIMAL(15,3),
    quantity_rejected DECIMAL(15,3),
    rejection_reason TEXT,
    notes TEXT
);
```

#### 3. UI Components
- **"Receive Goods"** button on Purchase Bill view page
- GRN creation form with:
  - Date of receipt
  - Site/Warehouse selection
  - Item-wise received/rejected quantities
  - QC notes per item
  - Photos of damaged goods (optional)
- **GRN List Page**: All goods receipts with filters
- **Pending Receipts Report**: Bills awaiting goods

#### 4. Business Logic
- Auto-create stock movement entries
- Update `ItemStock.quantity_available`
- Link to `ItemStockMovement` with `movement_type='stock_in'`
- Calculate stock value based on bill rate
- Handle partial receipts (multiple GRNs per bill)
- Update bill status: `pending_receipt` → `received` → `completed`

#### 5. Reports
- **Pending Goods Receipt**: Bills with no GRN
- **Rejected Goods Report**: Quality issues by vendor
- **Receipt Accuracy**: Ordered vs. Received analysis
- **Vendor Performance**: Delivery quality scorecard

---

## 💰 Payment Recording Feature

### Overview
Track payments made to vendors for purchase bills. Manage credit purchases, record partial payments, and maintain vendor ledgers.

### Features

#### 1. Payment Recording
```
Purchase Bill #PB-001
├─ Amount: ₹50,000
├─ Payment Terms: Net 30
├─ Due Date: 2025-12-07
└─ Status: "Unpaid"

Payment #PAY-001 (2025-11-20)
├─ Amount: ₹20,000
├─ Method: Bank Transfer
├─ Reference: NEFT123456
└─ Bill Status → "Partially Paid" (₹30,000 due)

Payment #PAY-002 (2025-12-05)
├─ Amount: ₹30,000
├─ Method: Cheque #123456
└─ Bill Status → "Paid" (₹0 due)
```

#### 2. Database Schema
```sql
-- Vendor Payments table
CREATE TABLE vendor_payments (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL,
    payment_number VARCHAR(50) UNIQUE NOT NULL,
    payment_date DATE NOT NULL,
    vendor_id INTEGER REFERENCES vendors(id),
    amount DECIMAL(15,2) NOT NULL,
    payment_method VARCHAR(50),
    reference_number VARCHAR(100),
    bank_account VARCHAR(100),
    notes TEXT,
    created_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Link payments to bills
CREATE TABLE payment_allocations (
    id SERIAL PRIMARY KEY,
    payment_id INTEGER REFERENCES vendor_payments(id),
    purchase_bill_id INTEGER REFERENCES purchase_bills(id),
    amount_allocated DECIMAL(15,2) NOT NULL
);
```

#### 3. UI Components
- **"Record Payment"** button on Purchase Bill view
- Payment form:
  - Payment date
  - Amount (max: outstanding amount)
  - Payment method dropdown (Cash/Cheque/Bank Transfer/UPI/Card)
  - Reference number (cheque #, transaction ID)
  - Bank account (for tracking)
  - Notes
- **Payment History**: Timeline on bill view page
- **Vendor Ledger**: All bills + payments per vendor
- **Payment Status Badges**: 
  - 🔴 Unpaid
  - 🟡 Partially Paid
  - 🟢 Paid
  - 🔵 Advance (overpaid)

#### 4. Business Logic
- Calculate outstanding amount per bill
- Handle partial payments
- Support advance payments (credit balance)
- Auto-allocate payments to oldest bills first (FIFO)
- Track vendor credit balance
- Payment due date alerts
- Overdue payment tracking

#### 5. Reports
- **Vendor Outstanding Report**: Unpaid bills by vendor
- **Payment Due Report**: Bills due in next N days
- **Payment History**: All payments with filters
- **Vendor Ledger**: Statement per vendor
- **Cash Flow**: Payment timeline (paid vs. due)
- **Aging Report**: 0-30 days, 30-60 days, 60+ days overdue

#### 6. Alerts & Notifications
- Payment due reminders (3 days before)
- Overdue payment alerts
- Large payment approval workflow (optional)
- Email notifications to accounts team

---

## 📊 GST-2 Report (Input Tax Credit)

### Overview
Government-mandated report for claiming input tax credit on purchases. Complements the existing GST-1 (sales) report.

### Features

#### 1. GSTR-2A/2B Reports
```
GST-2 Report (October 2025)
═══════════════════════════════════════════

1. B2B PURCHASES (Registered Vendors)
┌─────────────────────────────────────────┐
│ Vendor: ABC Suppliers (GSTIN: 27XXX)   │
│ Bill #PB-001 | ₹10,000 | GST: ₹1,800   │
│ Bill #PB-005 | ₹20,000 | GST: ₹3,600   │
└─────────────────────────────────────────┘
Subtotal: ₹30,000 | Tax: ₹5,400

2. IMPORT OF GOODS
Subtotal: ₹0 | Tax: ₹0

3. REVERSE CHARGE PURCHASES
Subtotal: ₹0 | Tax: ₹0

4. INPUT TAX CREDIT SUMMARY
╔═══════════════════════════════════════╗
║ Total Purchases:        ₹1,50,000     ║
║ CGST Paid:             ₹13,500        ║
║ SGST Paid:             ₹13,500        ║
║ IGST Paid:              ₹3,000        ║
║ Total ITC Claimable:   ₹30,000        ║
╚═══════════════════════════════════════╝

NET GST PAYABLE THIS MONTH
Output GST (Sales):      ₹45,000
Input GST (Purchases):  -₹30,000
───────────────────────────────────
Net Payable:             ₹15,000
```

#### 2. Report Components
- **B2B Purchases**: All bills from GSTIN vendors
- **B2C Purchases**: Bills without GSTIN (limited ITC)
- **Import Purchases**: Foreign suppliers
- **Reverse Charge**: Special GST cases
- **Tax Rate-wise Summary**: 5%, 12%, 18%, 28%
- **Vendor-wise ITC**: Credit per supplier
- **Month Comparison**: ITC trends

#### 3. Export Formats
- PDF (for filing)
- Excel (detailed analysis)
- JSON (for GST portal upload)

#### 4. Reconciliation
- Match with vendor GSTR-1
- Highlight mismatches
- ITC mismatch alerts

---

## 🔄 Purchase Orders (PO)

### Overview
Create formal purchase orders before receiving goods. Track PO status and convert to bills after delivery.

### Workflow
```
1. Request for Quotation (RFQ)
   └─ Send to multiple vendors

2. Vendor Quotes
   ├─ Vendor A: ₹50,000
   ├─ Vendor B: ₹48,000 ← Selected
   └─ Vendor C: ₹52,000

3. Purchase Order (PO-001)
   ├─ Vendor: B
   ├─ Items: LED Bulbs × 100
   ├─ Amount: ₹48,000
   ├─ Delivery: 15 days
   └─ Status: "Sent to Vendor"

4. Goods Receipt (GRN-001)
   └─ Received: 95 pcs (5 damaged)

5. Purchase Bill (PB-001)
   ├─ From PO: PO-001
   ├─ Amount: ₹45,600 (95 pcs)
   └─ Status: "Paid"
```

### Features
- PO creation from quotations
- PO approval workflow
- Email PO to vendor
- Track PO status (Pending/Partial/Fulfilled)
- Convert PO → Bill after delivery
- PO vs. Bill comparison

---

## 🔄 Recurring Bills

### Overview
Auto-generate bills for recurring purchases (rent, subscriptions, AMC).

### Features
```
Setup Recurring Bill
├─ Template: Office Rent
├─ Vendor: Landlord
├─ Amount: ₹10,000/month
├─ Start: 2025-11-01
├─ Frequency: Monthly (1st of month)
└─ End: 2026-10-31

Auto-Creation
├─ 2025-11-01: Bill #PB-101 created
├─ 2025-12-01: Bill #PB-125 created
└─ 2026-01-01: Bill #PB-151 created
```

- Templates for common recurring bills
- Auto-create on schedule
- Email notifications
- Pause/resume templates

---

## ✅ Approval Workflow

### Overview
Multi-level approval for purchase bills before payment.

### Workflow
```
Employee → Create Bill
    ↓
Manager → Review & Approve
    ↓
Accounts → Verify & Pay
    ↓
Completed
```

### Features
- Role-based approvals
- Approval limits (₹10k, ₹50k, ₹1L+)
- Email notifications
- Rejection with comments
- Approval history audit trail

---

## 📂 Expense Categorization

### Overview
Categorize purchases as Inventory, Expense, or Asset for accounting.

### Categories
```
Purchase Bill Types
├─ Inventory Purchase (Stock items for resale)
├─ Expense (Rent, Utilities, Salaries)
├─ Asset Purchase (Furniture, Equipment)
└─ Service Purchase (AMC, Repairs)
```

### Benefits
- Accurate P&L statements
- Asset depreciation tracking
- Expense budgeting
- Tax deductions

---

## 📎 Document Attachments

### Overview
Upload and store related documents with purchase bills.

### Features
- Upload vendor invoice PDF
- Attach delivery challan
- Store payment receipts
- QC photos (damaged goods)
- Email correspondence
- View/download attachments
- OCR to extract data (future AI feature)

---

## 📈 Advanced Reporting

### 1. Vendor Performance Dashboard
- Delivery time accuracy
- Quality rejection rate
- Price competitiveness
- Payment term compliance
- Vendor rating (1-5 stars)

### 2. Purchase Analytics
- Category-wise spending
- Monthly purchase trends
- Top vendors by volume
- Top items by spend
- Price variation alerts

### 3. Budget vs. Actual
- Set category budgets
- Track actual spend
- Variance alerts
- Forecast future spend

### 4. Procurement Insights
- Best time to buy (seasonal)
- Bulk purchase savings
- Vendor consolidation opportunities
- Stock-out prevention

---

## 🔐 Security & Audit

### Features
- Bill edit history (audit log)
- User action tracking
- IP address logging
- Data encryption
- Role-based access control
- Approval trail
- Payment authorization logs

---

## 🌐 Integration Features

### 1. Bank Integration
- Auto-fetch bank statements
- Match payments to bills
- Reconcile accounts

### 2. Email Integration
- Forward vendor invoices to email
- Auto-create bills from emails (AI)
- Send PO via email

### 3. Vendor Portal
- Vendors can submit invoices online
- Track payment status
- View purchase history

---

## 🚀 Implementation Priority

### Phase 1 (Current) ✅
- Basic Purchase Bills
- Vendor Management
- GST Calculation

### Phase 2 (Next 2 weeks) 🏗️
- Stock Receipt Integration (GRN)
- Payment Recording

### Phase 3 (1 month)
- GST-2 Report
- Purchase Orders

### Phase 4 (2 months)
- Recurring Bills
- Approval Workflow
- Document Attachments

### Phase 5 (3+ months)
- Advanced Analytics
- Vendor Portal
- Bank Integration

---

## 📝 Notes

- All features should maintain backward compatibility
- Database migrations for new tables
- Comprehensive testing before deployment
- User training materials for each feature
- Mobile-responsive UI for all new pages

---

**Last Updated**: November 7, 2025  
**Document Owner**: Development Team  
**Review Cycle**: Monthly

