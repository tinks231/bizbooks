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
8. `/migrate/add-sales-order-module` - Sales Order & Delivery Challan modules ⭐ NEW!

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

## 🔧 For Purchase Request Image Issue:
**Run this migration NOW:**
```
https://YOUR-SUBDOMAIN.bizbooks-dun.vercel.app/migrate/add-purchase-requests
```

This will fix the "image not showing in admin view" issue!
