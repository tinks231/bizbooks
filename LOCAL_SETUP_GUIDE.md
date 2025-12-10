# 🚀 LOCAL SETUP GUIDE - BizBooks
**For testing on a new laptop (MacOS/Windows/Linux)**

---

## 📋 PREREQUISITES

### **1. Install Python 3.9+**
**Check if already installed:**
```bash
python3 --version
```

**If not installed:**
- **MacOS:** 
  ```bash
  brew install python3
  ```
- **Windows:** Download from https://www.python.org/downloads/
- **Linux:** 
  ```bash
  sudo apt install python3 python3-pip
  ```

### **2. Install Git** (if not already)
```bash
git --version
```
If not installed: https://git-scm.com/downloads

---

## 🔧 STEP-BY-STEP SETUP

### **Step 1: Clone the Repository** ✅
(Already done if you cloned from GitHub)

```bash
cd ~/Downloads
git clone https://github.com/tinks231/bizbooks.git
cd bizbooks
```

---

### **Step 2: Create Virtual Environment**

**MacOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**You should see `(venv)` in your terminal now!**

---

### **Step 3: Install Dependencies**

```bash
pip install -r requirements.txt
```

This installs all Python packages (Flask, SQLAlchemy, etc.)

**⏱️ Takes 2-3 minutes**

---

### **Step 4: Configure Database**

**IMPORTANT:** For local testing, we use **SQLite** (no PostgreSQL setup needed!)

**Check `modular_app/app.py`:**
The code already handles this automatically:
```python
# Uses SQLite for local development (no setup required)
# Uses PostgreSQL only in production (Vercel)
```

**SQLite database will be auto-created at:**
```
modular_app/instance/app.db
```

**No database setup required!** ✅

---

### **Step 5: Initialize Database**

**ONLY FIRST TIME:**
```bash
cd modular_app
python3 init_db.py
```

**Output:**
```
✅ Database initialized successfully!
   All tables created.
   You can now register tenants at: /register/
```

**This creates all tables (tenants, sites, items, customers, etc.)**

---

### **Step 6: Run the Application**

**From the `modular_app` folder:**
```bash
python3 run_local.py
```

**OR use the helper script from project root:**
```bash
cd /path/to/bizbooks
python3 run_local.py
```

**Output:**
```
 * Running on http://127.0.0.1:5001
 * Running on http://your-laptop.local:5001
```

**✅ App is running!**

---

### **Step 7: Access the Application**

**Open browser and go to:**
```
http://127.0.0.1:5001
```

**OR:**
```
http://localhost:5001
```

---

## 🏪 ACCESSING THE CLOTHING RETAIL TENANT

### **Option A: Use Existing Production Data** (RECOMMENDED)

**Problem:** Local SQLite is empty. Production data is on Supabase PostgreSQL.

**Solution:** Connect to production database from local:

**1. Get Production Database URL:**
From Vercel environment variables, get the `DATABASE_URL`

**2. Set Environment Variable:**

**MacOS/Linux:**
```bash
export DATABASE_URL="postgresql://user:pass@host.supabase.co:5432/database"
python3 run_local.py
```

**Windows:**
```bash
set DATABASE_URL=postgresql://user:pass@host.supabase.co:5432/database
python run_local.py
```

**3. Access with Production Credentials:**
```
URL: http://localhost:5001/login
Subdomain: ayushi (or your clothing tenant subdomain)
Email: your-email@example.com
Password: your-password
```

---

### **Option B: Create New Local Tenant** (FRESH START)

**1. Go to registration:**
```
http://localhost:5001/register
```

**2. Fill the form:**
```
Company Name: Fashion Hub Test
Subdomain: fashionhub
Admin Name: Your Wife's Name
Email: test@example.com
Phone: 9876543210
Password: test123
```

**3. Skip email verification (local mode):**
- Check the terminal output for the verification link
- OR directly update the database:

```bash
cd modular_app
python3
```

```python
from models import db, Tenant
from app import app

with app.app_context():
    tenant = Tenant.query.filter_by(subdomain='fashionhub').first()
    tenant.email_verified = True
    tenant.status = 'active'
    db.session.commit()
    print("✅ Tenant activated!")
```

**4. Login:**
```
http://localhost:5001/login
Subdomain: fashionhub
Email: test@example.com
Password: test123
```

**5. Import Dataset:**
- Go to `/admin/bulk-import`
- Upload the branded clothing dataset (90 products)
- Upload customer dataset (15 customers)

---

## 📂 PROJECT STRUCTURE

```
bizbooks/
├── modular_app/           ← Main application folder
│   ├── app.py            ← Flask app initialization
│   ├── run_local.py      ← Run script for local development
│   ├── init_db.py        ← Database initialization
│   ├── models/           ← Database models
│   ├── routes/           ← API routes
│   ├── templates/        ← HTML templates
│   ├── static/           ← CSS, JS, images
│   ├── utils/            ← Helper functions
│   └── instance/         ← Local SQLite database (auto-created)
│       └── app.db        ← SQLite file
├── venv/                 ← Virtual environment (created by you)
├── requirements.txt      ← Python dependencies
└── run_local.py          ← Alternative run script (project root)
```

---

## 🔧 CONFIGURATION

### **Local vs Production:**

| Feature | Local Development | Production (Vercel) |
|---------|-------------------|---------------------|
| Database | SQLite (`instance/app.db`) | PostgreSQL (Supabase) |
| Port | 5001 | 443 (HTTPS) |
| Subdomain | Uses `lvh.me` hack | Real subdomains |
| Email | Printed to console | Actual SMTP |
| Storage | Local filesystem | Vercel Blob Storage |

### **Environment Variables (Optional):**

Create `.env` file in `modular_app/`:
```bash
DATABASE_URL=sqlite:///instance/app.db
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-here
```

---

## 🎯 TESTING THE CLOTHING TENANT

### **Scenario 1: Testing Locally with Fresh Data**

```bash
# Step 1: Initialize database
cd modular_app
python3 init_db.py

# Step 2: Run app
python3 run_local.py

# Step 3: Open browser
http://localhost:5001/register

# Step 4: Create tenant "fashionhub"

# Step 5: Login and import datasets
```

### **Scenario 2: Testing Locally with Production Data**

```bash
# Step 1: Get DATABASE_URL from Vercel

# Step 2: Set environment variable
export DATABASE_URL="postgresql://..."

# Step 3: Run app
python3 run_local.py

# Step 4: Login with production credentials
http://localhost:5001/login
Subdomain: ayushi
```

---

## 🐛 TROUBLESHOOTING

### **Issue 1: "Module not found" errors**
```bash
# Activate virtual environment first!
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### **Issue 2: "Port 5001 already in use"**
```bash
# Kill existing process
lsof -ti:5001 | xargs kill -9

# OR change port in run_local.py
app.run(port=5002)  # Use different port
```

### **Issue 3: Database errors**
```bash
# Delete and recreate database
rm -rf modular_app/instance/app.db
cd modular_app
python3 init_db.py
```

### **Issue 4: "No module named 'models'"**
```bash
# Make sure you're in the modular_app folder
cd modular_app
python3 run_local.py
```

### **Issue 5: Can't access subdomains locally**
**Use `lvh.me` instead of `localhost`:**
```
http://fashionhub.lvh.me:5001
```

`lvh.me` is a magic domain that always resolves to 127.0.0.1 and supports subdomains!

---

## 📝 QUICK REFERENCE

### **Start App:**
```bash
cd modular_app
source venv/bin/activate  # Mac/Linux only
python3 run_local.py
```

### **Stop App:**
```
Press Ctrl+C in terminal
```

### **Reset Database:**
```bash
rm -rf modular_app/instance/app.db
cd modular_app
python3 init_db.py
```

### **Access URLs:**
```
Registration: http://localhost:5001/register
Login:        http://localhost:5001/login
Admin:        http://localhost:5001/admin/dashboard
Superadmin:   http://localhost:5001/superadmin/login
```

### **Test Credentials (After creating tenant):**
```
Subdomain: fashionhub
Email:     test@example.com
Password:  test123
```

---

## 🎁 BONUS: VS Code Setup

If using VS Code:

**1. Install Python extension**

**2. Select virtual environment:**
- Press `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows)
- Type "Python: Select Interpreter"
- Choose `./venv/bin/python`

**3. Run/Debug:**
- Press F5
- Select "Flask"
- App starts automatically!

---

## 📚 NEXT STEPS AFTER SETUP

1. ✅ **Import Branded Clothing Dataset**
   - `/admin/bulk-import`
   - Upload `BizBooks_BRANDED_Clothing_90_Products.xlsx`

2. ✅ **Import Customer Dataset**
   - `/admin/bulk-import`
   - Upload `BizBooks_Customer_Sample_15.xlsx`

3. ✅ **Configure Loyalty Program**
   - `/admin/loyalty/settings`
   - Enable birthday/anniversary bonuses
   - Set up membership tiers

4. ✅ **Test Invoice Creation**
   - Create invoice with customer who has birthday/anniversary
   - Check loyalty points calculation
   - Verify stock deduction

5. ✅ **Test Returns** (Future feature)
   - Use the `RETURNS_REFUNDS_DESIGN.md` as reference

---

## 🆘 NEED HELP?

**Common Commands:**
```bash
# Check Python version
python3 --version

# Check if virtual environment is active
which python  # Should show venv/bin/python

# View app logs
# (Logs appear in terminal where app is running)

# Check database contents (SQLite)
sqlite3 modular_app/instance/app.db
.tables  # List all tables
SELECT * FROM tenants;  # View tenants
.quit
```

---

## ✅ SETUP CHECKLIST

- [ ] Python 3.9+ installed
- [ ] Repository cloned
- [ ] Virtual environment created
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Database initialized (`python3 init_db.py`)
- [ ] App running (`python3 run_local.py`)
- [ ] Can access http://localhost:5001
- [ ] Tenant created/logged in
- [ ] Datasets imported

---

**Last Updated:** December 10, 2025  
**File:** LOCAL_SETUP_GUIDE.md

═══════════════════════════════════════════════════════════════

**Good luck with testing!** 🎉

