# 🔧 Database Migrations Checklist

## What are Migrations?
When we add new features, we sometimes need to add new database columns or tables.
These are "migrations" - one-time updates to your database structure.

## ✅ Purchase Request Migration

### What it does:
- Adds `email` column to employees table
- Creates `purchase_requests` table (with `document_url` field!)

### How to run:
1. Go to: `https://YOUR-SUBDOMAIN.bizbooks-dun.vercel.app/migrate/add-purchase-requests`
2. You should see: `✅ Migration completed!`
3. Done! Images will now save properly.

### Example URL:
```
https://mahaveerelectricals.bizbooks-dun.vercel.app/migrate/add-purchase-requests
```

## 🔍 How to Check if Migration is Needed:

### Method 1: Try to upload
- If image uploads but doesn't show in admin view → **Migration needed!**

### Method 2: Check Supabase
1. Go to Supabase → Table Editor
2. Look at `purchase_requests` table
3. Check if `document_url` column exists
   - **No column?** → Run migration
   - **Column exists?** → Migration already done!

## 📋 All Available Migrations:

1. `/migrate/add-email-verification` - Email verification for signups
2. `/migrate/add-purchase-requests` - Purchase requests with document upload ⭐
3. `/migrate/add-category-group-link` - Item category groups
4. `/migrate/add-invoices` - Invoicing system
5. `/migrate/add-customers` - Customer management
6. `/migrate/add-tasks` - Task management
7. `/migrate/add-hsn-code-to-items` - HSN code for GST invoices ⭐
8. `/migrate/add-sales-order-module` - Sales Order & Delivery Challan modules ⭐
9. `/migrate/add-gst-rate-to-items` - GST Rate in Item Master for accurate reporting ⭐ **REQUIRED!**

## ⚠️ Important:
- Run each migration **ONLY ONCE** per database
- Safe to run multiple times (will skip if already done)
- Migrations **NEVER delete data** - only add new fields/tables

## 🎯 Latest Migration (November 2025):

### ✅ Sales Order & Delivery Challan Module

**What it adds:**
- `sales_orders` table - Track confirmed orders
- `sales_order_items` table - Order line items
- `delivery_challans` table - GST-compliant delivery documents
- `delivery_challan_items` table - Challan line items
- Updates to `invoices` and `invoice_items` tables for tracking

**How to run:**
```
https://YOUR-SUBDOMAIN.bizbooks-dun.vercel.app/migrate/add-sales-order-module
```

**What it enables:**
- Create sales orders from quotations
- Track order fulfillment status
- Create delivery challans for goods dispatch
- Convert orders/challans to invoices
- Complete audit trail from quote to payment

**Status:** Database ready, UI implementation in progress

---

## ✅ Purchase Bills Module Migration

### What it does:
- Creates `purchase_bills` table for vendor bill management
- Creates `purchase_bill_items` table for line items
- Tracks GST (CGST/SGST/IGST) for input tax credit
- Links to vendors and purchase requests

### How to run:
```
https://YOUR-SUBDOMAIN.bizbooks-dun.vercel.app/migrate/add-purchase-bills-module
```

**Status:** Completed - Purchase Bills UI live!

---

## ✅ Vendor Payment Tracking Migration

### What it does:
- Creates `vendor_payments` table to record payments made to vendors
- Creates `payment_allocations` table to link payments to specific bills
- Tracks payment methods (Cash/Cheque/Bank Transfer/UPI)
- Supports partial payments and advance payments
- Auto-generates payment numbers (PAY-0001)

### Features:
- **Record Payments**: Track cash/bank payments to vendors
- **Payment History**: See all payments per bill/vendor
- **Outstanding Reports**: Track unpaid & partially paid bills
- **Vendor Ledger**: Complete payment history per vendor

### How to run:
```
https://YOUR-SUBDOMAIN.bizbooks-dun.vercel.app/migrate/add-vendor-payment-tracking
```

### After Migration:
1. Visit any Purchase Bill view page
2. Click "Record Payment" button
3. Enter payment details and allocate to bills
4. View payment history timeline

**Status:** ✅ Ready - Migration available, UI coming next!

---

## ⚠️ **CRITICAL: GST Rate in Item Master Migration** ⚠️

### What it does:
- Adds `gst_rate` column to `items` table
- Sets default 18% GST for all existing items
- Required for accurate GST reports and compliance

### Why you need this:
**Without this migration, you'll see this error:**
```
psycopg2.errors.UndefinedColumn: column items.gst_rate does not exist
```

### What it enables:
- ✅ **Item Master**: Add/edit items with correct GST rates (0%, 5%, 12%, 18%, 28%)
- ✅ **Auto-fill**: GST rate auto-populates in transactions (invoices, purchase bills, etc.)
- ✅ **GSTR-2 Report**: Only GST bills appear (non-GST bills excluded automatically)
- ✅ **GSTR-3B ITC**: Accurate Input Tax Credit calculation
- ✅ **Bulk Import**: Excel import now sets GST rates correctly

### How to run:
```
https://YOUR-SUBDOMAIN.bizbooks-dun.vercel.app/migrate/add-gst-rate-to-items
```

### What to expect after migration:
- All existing items: 18% GST (most common rate in India)
- You can edit items to change rates (e.g., 0% for exempted goods, 5% for essentials)
- New items: Choose rate from dropdown when adding
- GST reports now correctly filter bills with/without GST

**Status:** ⚠️ **REQUIRED - Run immediately to fix item listing error!**

---

## ✅ Fix Purchase Bill Approve Error (URGENT!)

### What it fixes:
**Error:** `ForeignKeyViolation: Key (approved_by)=(1) is not present in table "employees"`

**Problem:** 
- The `approved_by` field had a foreign key constraint to `employees` table
- But tenant admins (who aren't employees) were trying to approve bills
- This caused the approval to fail

### What it does:
- Removes the foreign key constraint on `approved_by` field
- Allows both tenant admins AND employees to approve bills
- Stores approver ID as simple integer (no FK validation)

### How to run:
```
https://YOUR-SUBDOMAIN.bizbooks-dun.vercel.app/migrate/fix-purchase-bill-approved-by
```

### After Migration:
1. Try approving any draft purchase bill
2. Should work without errors now!
3. Both tenant admins and employees can approve

**Status:** 🚨 **RUN THIS NOW!** Required to approve any purchase bills!

---

## 🔧 For Purchase Request Image Issue:
**Run this migration NOW:**
```
https://YOUR-SUBDOMAIN.bizbooks-dun.vercel.app/migrate/add-purchase-requests
```

This will fix the "image not showing in admin view" issue!
