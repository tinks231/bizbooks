# ⚡ Quick Migration Steps (10 Minutes)

## 🎯 **Goal:** Move Supabase from Mumbai → US East for 60% speed boost

---

## **STEP 1: Create New Supabase Project (2 min)**

1. Go to: https://supabase.com/dashboard
2. Click **"New Project"**
3. Settings:
   - Name: `bizbooks-us-east`
   - Password: (create strong one)
   - **Region: East US (North Virginia)** ⭐
4. Click "Create"
5. Wait 2 minutes

---

## **STEP 2: Backup Mumbai Data (3 min)**

1. Go to Mumbai project: https://supabase.com/dashboard/project/[OLD-PROJECT-ID]
2. Click **"Database"** → **"Backups"**
3. Click **"Download backup"** (or "Create" then download)
4. Save file as: `bizbooks_backup.sql`

**Alternative (if backup button missing):**
```bash
# Use Supabase SQL Editor
# Copy your Mumbai connection string from Settings → Database

# Then run this in terminal:
pg_dump "postgresql://postgres:[OLD-PASSWORD]@db.[OLD-REF].supabase.co:5432/postgres" \
  --clean --if-exists > bizbooks_backup.sql
```

---

## **STEP 3: Restore to US East (3 min)**

1. Go to new US East project
2. Go to **"SQL Editor"**
3. Click **"New Query"**
4. Paste contents of `bizbooks_backup.sql`
5. Click **"Run"**
6. Wait for completion (2-3 minutes)

**Alternative (using psql):**
```bash
# Get US East connection string from Settings → Database

psql "postgresql://postgres:[NEW-PASSWORD]@db.[NEW-REF].supabase.co:5432/postgres" \
  < bizbooks_backup.sql
```

---

## **STEP 4: Update Vercel (1 min)**

1. Go to: https://vercel.com/[your-project]/settings/environment-variables
2. Find `DATABASE_URL`
3. Click **"Edit"**
4. Replace with NEW connection string:
   ```
   postgresql://postgres:[NEW-PASSWORD]@db.[NEW-REF].supabase.co:5432/postgres
   ```
5. Select **all** environments (Production, Preview, Development)
6. Click **"Save"**

---

## **STEP 5: Redeploy (1 min)**

```bash
cd /Users/rishjain/Downloads/attendence_app
git commit --allow-empty -m "Move DB to US East"
git push origin main
```

Wait 2 minutes for deployment.

---

## **STEP 6: Test (1 min)**

```bash
# Visit your site
https://mahaveerelectricals.bizbooks.co.in/admin/login

# Login and check:
✅ Dashboard loads
✅ Customers list loads
✅ Can create invoice

# Run speed test:
cd /Users/rishjain/Downloads/attendence_app
source venv/bin/activate
python check_vercel_function_region.py

# Should see: 400-600ms (down from 1200ms!) ✅
```

---

## ✅ **DONE!** 🎉

**Result:**
- 60% faster page loads
- 1200ms → 400-600ms
- Zero cost
- 10 minutes total time

---

## 🆘 **If Something Goes Wrong:**

**Rollback:**
```bash
1. Go back to Vercel environment variables
2. Change DATABASE_URL back to Mumbai connection string
3. git push (redeploy)
4. System back to normal
```

**Your Mumbai data is still safe!** We didn't delete anything.

---

**Want me to help you through each step in real-time?** 🚀

