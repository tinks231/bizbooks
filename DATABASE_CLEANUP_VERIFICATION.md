# 🔍 Database Cleanup Verification Guide

## Purpose
Verify that tenant deletion properly cleaned up all data from PostgreSQL database.

---

## 📊 What SHOULD Remain in Database

After deleting all tenants, these records **SHOULD still exist**:

✅ **Superadmin Data:**
- Superadmin user account
- System configuration

❌ **What should be ZERO:**
- All tenant records
- All customer records
- All employee records
- All inventory items
- All invoices
- All tasks
- All attendance records
- Everything else!

---

## 🔌 How to Connect to PostgreSQL

### Option 1: Using Vercel Dashboard
1. Go to Vercel Dashboard
2. Select your project
3. Go to **Storage** tab
4. Click on your **Postgres** database
5. Click **"Data"** tab
6. Or use **Query** tab for SQL

### Option 2: Using psql (Terminal)
```bash
# Get connection string from Vercel dashboard or environment variables
psql "postgresql://username:password@host:5432/database_name?sslmode=require"
```

### Option 3: Using pgAdmin or TablePlus
- Install pgAdmin (free) or TablePlus (paid)
- Create new connection
- Use credentials from Vercel

---

## 🔍 Verification Queries

Run these SQL queries to check for leftover data:

### 1. Check Tenants (Should be 0)
```sql
SELECT COUNT(*) as tenant_count FROM tenants;
-- Expected: 0

-- If any exist, show them:
SELECT id, company_name, subdomain, created_at 
FROM tenants 
ORDER BY id;
```

### 2. Check Customers (Should be 0)
```sql
SELECT COUNT(*) as customer_count FROM customers;
-- Expected: 0

-- If any exist:
SELECT id, tenant_id, customer_code, name 
FROM customers 
ORDER BY id;
```

### 3. Check Employees (Should be 0)
```sql
SELECT COUNT(*) as employee_count FROM employees;
-- Expected: 0

-- If any exist:
SELECT id, tenant_id, name, phone 
FROM employees 
ORDER BY id;
```

### 4. Check Invoices (Should be 0)
```sql
SELECT COUNT(*) as invoice_count FROM invoices;
-- Expected: 0

SELECT COUNT(*) as invoice_item_count FROM invoice_items;
-- Expected: 0
```

### 5. Check Inventory Items (Should be 0)
```sql
-- New inventory system
SELECT COUNT(*) as item_count FROM items;
-- Expected: 0

SELECT COUNT(*) as item_stock_count FROM item_stocks;
-- Expected: 0

SELECT COUNT(*) as item_category_count FROM item_categories;
-- Expected: 0

SELECT COUNT(*) as item_group_count FROM item_groups;
-- Expected: 0

-- Old inventory system
SELECT COUNT(*) as material_count FROM materials;
-- Expected: 0

SELECT COUNT(*) as stock_count FROM stocks;
-- Expected: 0
```

### 6. Check Tasks (Should be 0)
```sql
SELECT COUNT(*) as task_count FROM tasks;
-- Expected: 0

SELECT COUNT(*) as task_update_count FROM task_updates;
-- Expected: 0

SELECT COUNT(*) as task_media_count FROM task_media;
-- Expected: 0

SELECT COUNT(*) as task_material_count FROM task_materials;
-- Expected: 0
```

### 7. Check Attendance (Should be 0)
```sql
SELECT COUNT(*) as attendance_count FROM attendances;
-- Expected: 0
```

### 8. Check Purchase Requests (Should be 0)
```sql
SELECT COUNT(*) as purchase_request_count FROM purchase_requests;
-- Expected: 0
```

### 9. Check Expenses (Should be 0)
```sql
SELECT COUNT(*) as expense_count FROM expenses;
-- Expected: 0

SELECT COUNT(*) as expense_category_count FROM expense_categories;
-- Expected: 0
```

### 10. Check Sites (Should be 0)
```sql
SELECT COUNT(*) as site_count FROM sites;
-- Expected: 0
```

---

## 🎯 Comprehensive Check (All Tables)

Run this single query to check all tables at once:

```sql
-- Count records in all major tables
SELECT 
    'tenants' as table_name, COUNT(*) as record_count FROM tenants
UNION ALL
SELECT 'customers', COUNT(*) FROM customers
UNION ALL
SELECT 'employees', COUNT(*) FROM employees
UNION ALL
SELECT 'sites', COUNT(*) FROM sites
UNION ALL
SELECT 'attendances', COUNT(*) FROM attendances
UNION ALL
SELECT 'invoices', COUNT(*) FROM invoices
UNION ALL
SELECT 'invoice_items', COUNT(*) FROM invoice_items
UNION ALL
SELECT 'items', COUNT(*) FROM items
UNION ALL
SELECT 'item_stocks', COUNT(*) FROM item_stocks
UNION ALL
SELECT 'item_categories', COUNT(*) FROM item_categories
UNION ALL
SELECT 'item_groups', COUNT(*) FROM item_groups
UNION ALL
SELECT 'materials', COUNT(*) FROM materials
UNION ALL
SELECT 'stocks', COUNT(*) FROM stocks
UNION ALL
SELECT 'stock_movements', COUNT(*) FROM stock_movements
UNION ALL
SELECT 'tasks', COUNT(*) FROM tasks
UNION ALL
SELECT 'task_updates', COUNT(*) FROM task_updates
UNION ALL
SELECT 'task_media', COUNT(*) FROM task_media
UNION ALL
SELECT 'task_materials', COUNT(*) FROM task_materials
UNION ALL
SELECT 'purchase_requests', COUNT(*) FROM purchase_requests
UNION ALL
SELECT 'expenses', COUNT(*) FROM expenses
UNION ALL
SELECT 'expense_categories', COUNT(*) FROM expense_categories
ORDER BY table_name;

-- Expected Result: ALL should show 0 records
```

---

## 🔍 Check for Orphaned Records

Sometimes deletion might fail partially. Check for orphaned records:

### Orphaned Customers (no tenant)
```sql
SELECT COUNT(*) FROM customers 
WHERE tenant_id IS NULL OR tenant_id NOT IN (SELECT id FROM tenants);
-- Expected: 0
```

### Orphaned Employees (no tenant)
```sql
SELECT COUNT(*) FROM employees 
WHERE tenant_id IS NULL OR tenant_id NOT IN (SELECT id FROM tenants);
-- Expected: 0
```

### Orphaned Items (no tenant)
```sql
SELECT COUNT(*) FROM items 
WHERE tenant_id IS NULL OR tenant_id NOT IN (SELECT id FROM tenants);
-- Expected: 0
```

### Orphaned Invoices (no tenant or no customer)
```sql
-- No tenant
SELECT COUNT(*) FROM invoices 
WHERE tenant_id IS NULL OR tenant_id NOT IN (SELECT id FROM tenants);
-- Expected: 0

-- No customer
SELECT COUNT(*) FROM invoices 
WHERE customer_id IS NOT NULL 
  AND customer_id NOT IN (SELECT id FROM customers);
-- Expected: 0
```

---

## 🧹 Manual Cleanup (If Needed)

If you find orphaned records, clean them up manually:

### ⚠️ DANGER ZONE - Only if needed!

```sql
-- Delete orphaned customers
DELETE FROM customers 
WHERE tenant_id IS NULL OR tenant_id NOT IN (SELECT id FROM tenants);

-- Delete orphaned employees
DELETE FROM employees 
WHERE tenant_id IS NULL OR tenant_id NOT IN (SELECT id FROM tenants);

-- Delete orphaned items
DELETE FROM items 
WHERE tenant_id IS NULL OR tenant_id NOT IN (SELECT id FROM tenants);

-- Continue for other tables...
```

**Better Approach:** If you find issues, it's better to fix the deletion code than manually cleanup!

---

## 📊 Database Size Check

Check how much space the database is using:

```sql
-- Total database size
SELECT pg_size_pretty(pg_database_size(current_database())) as database_size;

-- Size of each table
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

**Expected:** If all data is deleted, most tables should be very small (few KB).

---

## 🔐 Verify Vercel Blob Storage

Check if files are cleaned up from Vercel Blob:

### Using Vercel Dashboard:
1. Go to Vercel Dashboard
2. Select your project
3. Go to **Storage** tab
4. Click on **Blob** storage
5. Browse files - should be empty or minimal

### Using Vercel CLI:
```bash
# List all blobs
vercel blob ls

# Expected: Empty or only system files
```

---

## ✅ Expected Clean State

After deleting all tenants, database should show:

| Table | Expected Count | What It Means |
|-------|----------------|---------------|
| `tenants` | 0 | No businesses registered |
| `customers` | 0 | No customer records |
| `employees` | 0 | No employee records |
| `sites` | 0 | No site/location records |
| `attendances` | 0 | No attendance records |
| `invoices` | 0 | No invoices |
| `invoice_items` | 0 | No invoice line items |
| `items` | 0 | No inventory items |
| `item_stocks` | 0 | No stock records |
| `item_categories` | 0 | No categories |
| `item_groups` | 0 | No groups |
| `materials` | 0 | No old inventory |
| `stocks` | 0 | No old stock |
| `tasks` | 0 | No tasks |
| `task_updates` | 0 | No task updates |
| `purchase_requests` | 0 | No purchase orders |
| `expenses` | 0 | No expense records |

**Database Size:** Should be minimal (< 10 MB)

---

## 🚨 Red Flags

If you see these, something went wrong:

❌ **ANY tenant records remaining**  
❌ **ANY customer/employee records with tenant_id = NULL**  
❌ **ANY invoice items without invoices (orphaned)**  
❌ **ANY stock records without materials (orphaned)**  
❌ **Database size > 50 MB (with no tenants)**  

---

## 🎯 Quick Verification Script

Save this as `verify_cleanup.sql` and run it:

```sql
-- Quick verification script
\echo 'Database Cleanup Verification Report'
\echo '===================================='
\echo ''

\echo 'Core Tables:'
SELECT 'Tenants: ' || COUNT(*) FROM tenants;
SELECT 'Employees: ' || COUNT(*) FROM employees;
SELECT 'Customers: ' || COUNT(*) FROM customers;
SELECT 'Sites: ' || COUNT(*) FROM sites;
\echo ''

\echo 'Invoicing:'
SELECT 'Invoices: ' || COUNT(*) FROM invoices;
SELECT 'Invoice Items: ' || COUNT(*) FROM invoice_items;
\echo ''

\echo 'Inventory (New):'
SELECT 'Items: ' || COUNT(*) FROM items;
SELECT 'Item Stock: ' || COUNT(*) FROM item_stocks;
SELECT 'Categories: ' || COUNT(*) FROM item_categories;
SELECT 'Groups: ' || COUNT(*) FROM item_groups;
\echo ''

\echo 'Inventory (Old):'
SELECT 'Materials: ' || COUNT(*) FROM materials;
SELECT 'Stock: ' || COUNT(*) FROM stocks;
\echo ''

\echo 'Operations:'
SELECT 'Attendance: ' || COUNT(*) FROM attendances;
SELECT 'Tasks: ' || COUNT(*) FROM tasks;
SELECT 'Purchase Requests: ' || COUNT(*) FROM purchase_requests;
SELECT 'Expenses: ' || COUNT(*) FROM expenses;
\echo ''

\echo 'Database Size:'
SELECT pg_size_pretty(pg_database_size(current_database()));
\echo ''

\echo 'If ALL counts are 0, database is CLEAN! ✅'
```

Run it:
```bash
psql "your_connection_string" -f verify_cleanup.sql
```

---

## 🎉 Success Criteria

✅ **Perfect Cleanup:**
- All tenant-related tables show 0 records
- No orphaned records
- Database size < 10 MB
- Vercel Blob storage empty

✅ **You can now:**
- Start fresh with new test data
- Deploy to production with confidence
- Create real tenants without clutter

---

## 📝 Summary

**Quick Check:**
1. Connect to PostgreSQL
2. Run: `SELECT COUNT(*) FROM tenants;`
3. If 0 → ✅ Likely clean
4. Run comprehensive check for peace of mind

**Your deletion worked if:**
- Superadmin still works ✅
- No tenant can login ✅
- All data counts = 0 ✅
- Database small ✅

**Next Steps:**
- Verify database is clean (use queries above)
- Test bulk import feature
- Start fresh testing
- Ready for production! 🚀

