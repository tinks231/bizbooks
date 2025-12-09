# 🧪 Test Loyalty Program Migration

## 📋 Steps to Test

### **1. Start Local Server**
```bash
cd /Users/rishjain/Downloads/attendence_app
source venv/bin/activate
python3 run_local.py
```

### **2. Run Migration**
Open your browser and navigate to:
```
http://mahaveerelectricals.lvh.me:5001/run-loyalty-migration
```

Or use curl:
```bash
curl -X POST http://mahaveerelectricals.lvh.me:5001/run-loyalty-migration
```

### **3. Expected Success Response**
```json
{
  "status": "success",
  "message": "✅ Loyalty program migration completed successfully!",
  "details": {
    "tables_created": [
      "loyalty_programs",
      "customer_loyalty_points",
      "loyalty_transactions"
    ],
    "tables_updated": [
      "customers (added date_of_birth, anniversary_date)",
      "invoices (added loyalty_discount, loyalty_points_redeemed, loyalty_points_earned)"
    ],
    "indexes_created": 5,
    "note": "Loyalty program is OFF by default for all tenants. Enable in settings."
  }
}
```

### **4. Verify Tables Created**

You can check if tables exist by connecting to your database:

**For Local SQLite:**
```bash
sqlite3 instance/attendance.db

# Run this SQL:
.tables

# Should see:
# loyalty_programs
# customer_loyalty_points
# loyalty_transactions
```

**For PostgreSQL (Production):**
```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_name LIKE 'loyalty%';
```

Should return:
- `loyalty_programs`
- `customer_loyalty_points`
- `loyalty_transactions`

### **5. Check New Columns**

**Check customers table:**
```sql
-- SQLite
PRAGMA table_info(customers);

-- PostgreSQL
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'customers' 
AND column_name IN ('date_of_birth', 'anniversary_date');
```

**Check invoices table:**
```sql
-- SQLite
PRAGMA table_info(invoices);

-- PostgreSQL
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'invoices' 
AND column_name IN ('loyalty_discount', 'loyalty_points_redeemed', 'loyalty_points_earned');
```

---

## ✅ Success Criteria

After running migration, you should have:

1. ✅ 3 new tables created:
   - `loyalty_programs` (tenant settings)
   - `customer_loyalty_points` (customer balances)
   - `loyalty_transactions` (transaction history)

2. ✅ Customers table updated with:
   - `date_of_birth` (DATE, nullable)
   - `anniversary_date` (DATE, nullable)

3. ✅ Invoices table updated with:
   - `loyalty_discount` (NUMERIC, default 0)
   - `loyalty_points_redeemed` (INTEGER, default 0)
   - `loyalty_points_earned` (INTEGER, default 0)

4. ✅ Default loyalty program created for your tenant:
   - `is_active = false` (OFF by default)
   - Pre-configured with moderate settings
   - Ready to enable when needed

5. ✅ No errors in server logs

---

## 🐛 Troubleshooting

### **Error: "relation already exists"**
✅ This is OK! It means tables already exist (migration ran before).

### **Error: "column already exists"**
✅ This is OK! It means columns already exist (migration ran before).

### **Error: "could not serialize access"**
❌ Database transaction conflict. Wait and try again.

### **Error: "relation does not exist" for tenants/customers/invoices**
❌ Base tables missing. Run main migrations first.

---

## 📊 Next Steps After Successful Migration

Once migration succeeds, we'll build:
1. Model files (Python classes)
2. Loyalty service (business logic)
3. Admin settings page
4. Invoice integration
5. Customer profile updates

---

**Ready to test? Start your local server and run the migration!** 🚀

