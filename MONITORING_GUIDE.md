# 📊 Database Monitoring Guide

## 🔍 Quick Health Check (Run in Supabase SQL Editor)

### 1. **Total Database Size**
```sql
SELECT pg_size_pretty(pg_database_size(current_database())) as database_size;
```

### 2. **Table Sizes (Sorted by Largest)**
```sql
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
    pg_total_relation_size(schemaname||'.'||tablename) AS size_bytes
FROM pg_tables
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY size_bytes DESC
LIMIT 20;
```

### 3. **Row Counts per Table**
```sql
SELECT 
    schemaname,
    tablename,
    n_tup_ins - n_tup_del as row_count
FROM pg_stat_user_tables
ORDER BY n_tup_ins - n_tup_del DESC;
```

### 4. **Index Sizes**
```sql
SELECT 
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_indexes
JOIN pg_stat_user_indexes USING (schemaname, tablename, indexname)
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY pg_relation_size(indexrelid) DESC
LIMIT 10;
```

### 5. **Growth Rate (Last 7 Days)**
```sql
-- Run this query weekly and compare results
SELECT 
    current_timestamp as check_date,
    pg_database_size(current_database()) as size_bytes,
    pg_size_pretty(pg_database_size(current_database())) as size_pretty;
```

---

## 🎯 **Critical Thresholds for Your Business**

### **Free Plan (500 MB) Alerts:**
- ⚠️ **350 MB (70%)** - Start planning upgrade
- 🚨 **400 MB (80%)** - Upgrade urgently
- 🔴 **450 MB (90%)** - Database writes may fail

### **Expected Usage (Clothing Business):**
```
Inventory (80K items):    ~60 MB
Invoices (50K):           ~25 MB
Customers (2K):            ~1 MB
Purchases (10K):          ~15 MB
Accounting Entries:       ~20 MB
Other tables:             ~10 MB
─────────────────────────────────
Total (1 year):          ~130 MB
Total (3 years):         ~250 MB
```

**Conclusion:** ✅ Free plan works for 2-3 years of operations!

---

## 🛠️ **Optimization Strategies**

### 1. **Archive Old Data (After 1 Year)**
```sql
-- Move old invoices to archive table
CREATE TABLE invoices_archive AS 
SELECT * FROM invoices 
WHERE invoice_date < NOW() - INTERVAL '1 year';

DELETE FROM invoices 
WHERE invoice_date < NOW() - INTERVAL '1 year';
```

### 2. **Delete Unnecessary Logs**
```sql
-- Clear old activity logs (keep last 90 days)
DELETE FROM activity_log 
WHERE created_at < NOW() - INTERVAL '90 days';
```

### 3. **Optimize Images**
- Don't store images in PostgreSQL (use Supabase Storage)
- Compress images before upload (max 100KB per image)
- Use lazy loading for product images

### 4. **Regular Vacuum**
```sql
-- Run monthly to reclaim space
VACUUM FULL ANALYZE;
```

---

## 🌍 **Multi-Region Strategy: Mumbai vs US**

### **Current Setup:**
- **Mumbai project:** Testing/Staging?
- **US project:** Production

### **Recommendation:**

**Option A: Delete Mumbai (Recommended if not needed)**
✅ Cost savings ($0 → $0 or $25 → $25)
✅ Simpler to manage
✅ Less confusion
✅ Single source of truth

**Option B: Keep Both (If needed)**
- **Mumbai:** For Indian customers (faster access from India)
- **US:** For international operations
- Cost: $25 × 2 = $50/month

### **Latency from India:**
- **Supabase Mumbai region:** ~20-50ms
- **Supabase US region:** ~200-400ms
- For inventory management, this difference is **negligible**

**Decision:** 🎯 **Delete Mumbai if it's just testing**. Keep US as production.

---

## 📱 **Monitoring Dashboard in BizBooks**

Would you like me to add a **"System Health"** page in admin panel showing:
- Database size usage
- Storage usage
- Number of records per table
- Growth trends
- Backup status

Let me know and I'll build it!

---

## 🚀 **Action Plan for Onboarding Your Cousin**

### **Before Onboarding:**
1. ✅ Test bulk import with 1,000 items
2. ✅ Measure database growth
3. ✅ Optimize images (compression)
4. ✅ Add monitoring queries

### **During Onboarding:**
1. Start with 5,000 items
2. Monitor database size daily
3. Check performance (invoice creation speed)
4. Collect feedback

### **After 30 Days:**
1. Analyze usage patterns
2. Decide if Pro plan needed
3. Optimize based on actual data

### **Upgrade Triggers:**
- Database > 350 MB → Upgrade to Pro
- Images > 800 MB → Use external CDN or Pro plan
- Users > 40K MAU → Upgrade to Pro

---

## 📞 **Need Help?**

If database size suddenly spikes:
1. Run table size query (Section 2)
2. Check for duplicate entries
3. Clear old logs/activity
4. Contact me for optimization

**Current Status:** ✅ **Healthy (7% used)**
**Estimated Runway:** 🎯 **2-3 years on free plan**

