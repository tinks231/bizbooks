# 🚀 GST Smart Invoice Migration - URLs

## ✅ Ready to Run!

The migration route is now registered and ready to use via browser.

---

## 📍 **Migration URLs**

### 1. **Run the Migration**
```
https://your-domain.com/migrate/gst-smart-invoice
```

**Example:**
- Production: `https://yoursite.bizbooks.co.in/migrate/gst-smart-invoice`
- Local: `http://localhost:5000/migrate/gst-smart-invoice`

**What it does:**
- ✅ Creates `stock_batches` table with indexes
- ✅ Creates `other_incomes` table with indexes
- ✅ Adds `invoice_type`, `linked_invoice_id`, `reduce_stock`, etc. to `invoices`
- ✅ Adds `bill_type`, `gst_applicable` to `purchase_bills`
- ✅ Adds `gst_classification` to `items`
- ✅ Adds `gst_registration_type` to `vendors` and `customers`
- ✅ Adds `stock_batch_id`, `uses_gst_stock` to `invoice_items`
- ✅ Updates existing data with safe defaults
- ✅ Works with both PostgreSQL and SQLite

---

### 2. **Check Migration Status** (Optional)
```
https://your-domain.com/migrate/gst-smart-invoice/status
```

**Example:**
- Production: `https://yoursite.bizbooks.co.in/migrate/gst-smart-invoice/status`
- Local: `http://localhost:5000/migrate/gst-smart-invoice/status`

**What it shows:**
```json
{
  "migrated": true,
  "details": {
    "stock_batches": true,
    "other_incomes": true,
    "invoices.invoice_type": true,
    "purchase_bills.bill_type": true,
    "vendors.gst_registration_type": true
  },
  "message": "✅ Migration complete!"
}
```

---

## 🎯 **Step-by-Step Instructions**

### **Step 1: Backup Your Database** 🔴 CRITICAL
Before running any migration:
```bash
# PostgreSQL
pg_dump -U your_username -d your_database > backup_before_gst_migration.sql

# Or use your Bizbooks backup feature
# Visit: https://yoursite.bizbooks.co.in/admin/backup
```

### **Step 2: Run the Migration**
1. Open your browser
2. Navigate to: `https://yoursite.bizbooks.co.in/migrate/gst-smart-invoice`
3. Wait for the response (should take 5-10 seconds)
4. You'll see a JSON response with all changes made

**Expected Response:**
```json
{
  "status": "success",
  "message": "🎉 GST Smart Invoice Migration Completed!",
  "changes": [
    "✅ Created stock_batches table",
    "✅ Created other_incomes table",
    "✅ Added invoices.invoice_type",
    "✅ Added purchase_bills.bill_type",
    "✅ Added vendors.gst_registration_type",
    "✅ Updated existing data with safe defaults"
  ],
  "next_steps": [
    "✅ Stock batch tracking enabled",
    "✅ Smart invoice validation ready",
    "✅ Credit adjustment feature available",
    "⚠️ Restart the application to load new models",
    "📝 Test purchase bill creation with GST toggle",
    "📝 Test invoice creation with smart validation"
  ]
}
```

### **Step 3: Restart Your Application**
If you're running on:

**Vercel:**
- The app will auto-reload on next request

**VPS/Server:**
```bash
# If using systemd
sudo systemctl restart bizbooks

# If using PM2
pm2 restart bizbooks

# If using screen/tmux
# Stop the current process (Ctrl+C)
# Start again: python modular_app/app.py
```

### **Step 4: Verify Everything Works**
1. Check migration status:
   - Visit: `/migrate/gst-smart-invoice/status`
   - Should say: `"migrated": true`

2. Check database:
   ```sql
   -- Check if tables exist
   SELECT table_name FROM information_schema.tables 
   WHERE table_name IN ('stock_batches', 'other_incomes');
   
   -- Check if columns exist
   SELECT column_name FROM information_schema.columns 
   WHERE table_name = 'invoices' AND column_name = 'invoice_type';
   ```

3. Test a purchase bill:
   - Go to purchase bills
   - Create a new one
   - Approve it
   - Check if a batch was created:
   ```sql
   SELECT * FROM stock_batches ORDER BY created_at DESC LIMIT 5;
   ```

---

## ⚠️ **Troubleshooting**

### **Error: Column already exists**
**Solution:** This is normal! The migration checks if columns exist before creating them. If you see messages like:
```
"ℹ️ invoices.invoice_type already exists"
```
This means the migration was already run (or partially run). It's safe.

---

### **Error: Permission denied**
**Solution:** Your database user needs `CREATE TABLE` and `ALTER TABLE` permissions.

```sql
-- Grant permissions (run as superuser)
GRANT CREATE ON DATABASE your_database TO your_username;
GRANT ALTER ON ALL TABLES IN SCHEMA public TO your_username;
```

---

### **Error: Foreign key constraint fails**
**Solution:** The migration creates foreign keys. Ensure the parent tables exist:
- `tenants`
- `items`
- `purchase_bills`
- `vendors`
- `sites`

If any are missing, check your database setup.

---

### **Error: Migration appears stuck**
**Solution:** The migration is running SQL commands. For large databases, it may take a minute. Wait up to 2 minutes before refreshing.

---

## 🎉 **After Successful Migration**

You can now:
1. ✅ Create purchase bills with GST toggle
2. ✅ System tracks GST vs non-GST stock in batches
3. ✅ Create invoices with smart GST validation
4. ✅ Use credit adjustment workflow (2-step method)
5. ✅ GST reports (GSTR-1, GSTR-3B) show accurate data

---

## 📊 **What Changed in the Database**

### **New Tables:**
| Table | Purpose |
|-------|---------|
| `stock_batches` | Tracks inventory by purchase with GST status |
| `other_incomes` | Records commission from credit adjustments |

### **New Columns:**
| Table | New Columns |
|-------|-------------|
| `invoices` | `invoice_type`, `linked_invoice_id`, `reduce_stock`, `credit_commission_rate`, `credit_commission_amount` |
| `invoice_items` | `stock_batch_id`, `uses_gst_stock`, `cost_base`, `cost_gst_paid` |
| `purchase_bills` | `bill_type`, `gst_applicable` |
| `items` | `gst_classification` |
| `vendors` | `gst_registration_type`, `composition_rate`, `gst_validated` |
| `customers` | `gst_registration_type`, `gst_validated` |

### **Data Changes:**
- All existing invoices marked as `'taxable'` (safe default)
- All existing purchase bills marked as `'taxable'` with `gst_applicable = true` (safe default)
- All existing items marked as `'gst_applicable'` (safe default)
- Vendors with GSTIN marked as `'registered'`, others as `'unregistered'`
- Customers with GSTIN marked as `'registered'`, others as `'unregistered'`

---

## 🔧 **Need Help?**

If you encounter issues:
1. Check the JSON response for specific error messages
2. Check your database logs
3. Verify database permissions
4. Ensure backup was taken before migration

**Branch:** `feature/gst-smart-invoice-management`

**Ready to merge to main after testing!** ✅

