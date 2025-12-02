# 🚀 YOUR PERSONALIZED LOCAL DEV SETUP

**Created specifically for your macOS + Supabase + Vercel setup!**

**Time Required:** 30 minutes  
**Difficulty:** Easy (copy-paste commands)

---

## ✅ STEP 1: Install Docker Desktop (10 minutes)

Since you chose "easiest" - Docker is perfect!

### Option A: Using Homebrew (RECOMMENDED - you have this!)

```bash
# Install Docker Desktop via Homebrew
brew install --cask docker
```

### Option B: Manual Download (if Homebrew fails)

1. Download: https://www.docker.com/products/docker-desktop/
2. Open the downloaded `.dmg` file
3. Drag Docker to Applications folder
4. Open Docker from Applications

### Verify Installation

```bash
# After Docker Desktop starts (whale icon in menu bar):
docker --version

# Should show: Docker version 24.x.x or higher
```

**✅ Checkpoint:** Docker icon visible in macOS menu bar (top right)

---

## ✅ STEP 2: Create Local PostgreSQL Database (2 minutes)

Copy-paste this entire block:

```bash
# Create PostgreSQL container
docker run --name bizbooks-local-db \
  -e POSTGRES_PASSWORD=local_dev_password_123 \
  -e POSTGRES_USER=bizbooks_dev \
  -e POSTGRES_DB=bizbooks_dev \
  -p 5432:5432 \
  -d postgres:15

# Wait 5 seconds for startup
sleep 5

# Verify it's running
docker ps
```

**Expected Output:**
```
CONTAINER ID   IMAGE         STATUS        PORTS                    NAMES
abc123def456   postgres:15   Up 3 seconds  0.0.0.0:5432->5432/tcp   bizbooks-local-db
```

**✅ Checkpoint:** You see `bizbooks-local-db` with status "Up"

---

## ✅ STEP 3: Create Local Environment File (2 minutes)

```bash
# Navigate to your project
cd /Users/rishjain/Downloads/attendence_app

# Create .env.local file
cat > .env.local << 'EOF'
# ========================================
# LOCAL DEVELOPMENT ENVIRONMENT
# ========================================
# ⚠️ DO NOT COMMIT THIS FILE TO GIT!
# Already in .gitignore - you're safe!

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=1
PORT=5000

# Local PostgreSQL Database
DATABASE_URL=postgresql://bizbooks_dev:local_dev_password_123@localhost:5432/bizbooks_dev

# Secret Key (DIFFERENT from production!)
SECRET_KEY=local_dev_secret_key_change_this_in_production_12345

# Email Configuration (Optional - for testing forgot password)
# Using MailHog for local email testing
MAIL_SERVER=localhost
MAIL_PORT=1025
MAIL_USE_TLS=False
MAIL_USERNAME=
MAIL_PASSWORD=

# Debug Mode
DEBUG=True
EOF

# Verify file was created
ls -la .env.local
```

**✅ Checkpoint:** Command shows `.env.local` file exists

---

## ✅ STEP 4: Activate Virtual Environment (1 minute)

```bash
# Make sure you're in the project directory
cd /Users/rishjain/Downloads/attendence_app

# Activate venv
source venv/bin/activate

# Your prompt should now show: (venv) $
```

**✅ Checkpoint:** Terminal prompt shows `(venv)` at the beginning

---

## ✅ STEP 5: Install Dependencies (3 minutes)

```bash
# Ensure you're in venv (see "venv" in prompt)
# Install all required packages
pip install --upgrade pip
pip install -r requirements.txt

# Verify Flask is installed
python -c "import flask; print(f'Flask {flask.__version__} installed ✅')"
```

**Expected Output:**
```
Flask 3.x.x installed ✅
```

**✅ Checkpoint:** No error messages, Flask version displayed

---

## ✅ STEP 6: Initialize Local Database (2 minutes)

The database is empty right now. Let's initialize it:

```bash
# Still in venv, load environment variables
export $(cat .env.local | xargs)

# Start Flask app briefly to create tables
# (It will create tables on first run)
python modular_app/app.py &

# Wait 10 seconds for initialization
sleep 10

# Stop it (we'll restart it properly next)
pkill -f "python modular_app/app.py"
```

**Note:** This creates the database schema. You might see some output - that's normal!

---

## ✅ STEP 7: Start Local Server (2 minutes)

```bash
# Make sure venv is activated (see "venv" in prompt)
# Load environment variables
export $(cat .env.local | xargs)

# Start Flask development server
python modular_app/app.py
```

**Expected Output:**
```
 * Running on http://0.0.0.0:5000
 * Running on http://127.0.0.1:5000
 * Restarting with stat
 * Debugger is active!
```

**🎉 SERVER IS RUNNING!**

**Open your browser:** http://localhost:5000

**✅ Checkpoint:** BizBooks login/signup page appears

---

## ✅ STEP 8: Create Test Account (2 minutes)

1. **Open browser:** http://localhost:5000
2. **Click "Sign Up"** (or Register)
3. **Fill in the form:**
   - **Business Name:** `Local Testing Shop`
   - **Email:** `test@local.dev`
   - **Password:** `test123`
   - **Subdomain:** `localtesting`
4. **Click "Register"**
5. **Login** with same credentials

**✅ Checkpoint:** You're logged in and see the dashboard!

---

## ✅ STEP 9: Restore Production Data (Optional, 5 minutes)

If you want to test with your real Mahaveer Electricals data:

### Method 1: Using BizBooks Backup (EASIEST!)

```bash
# 1. Open production in browser:
#    https://mahaveerelectricals.bizbooks.co.in

# 2. Login to your production account

# 3. Go to: Settings & Backup → Backup & Download

# 4. Click "Create Backup" → Download JSON file
#    Example: backup_mahaveer_20250102_143022.json

# 5. Go to your local: http://localhost:5000

# 6. Login to your test account

# 7. Go to: Settings & Backup → Restore Backup

# 8. Upload the JSON file you downloaded

# 9. Wait for restore to complete (might take 1-2 minutes)

# 10. Refresh page - you now have production data locally!
```

### Method 2: Direct PostgreSQL Dump (ADVANCED)

```bash
# You'll need your Supabase password for this
# Get it from: https://supabase.com/dashboard/project/ymdbpprjagkdkwhkxrno/settings/database

# Replace [YOUR_PASSWORD] with actual password
SUPABASE_PASSWORD="[YOUR_PASSWORD]"

# Backup from Supabase
pg_dump "postgresql://postgres:${SUPABASE_PASSWORD}@db.ymdbpprjagkdkwhkxrno.supabase.co:5432/postgres" \
  --no-owner --no-acl > supabase_backup_$(date +%Y%m%d).sql

# Restore to local Docker database
docker exec -i bizbooks-local-db psql -U bizbooks_dev bizbooks_dev < supabase_backup_*.sql

# Note: You might need to update tenant_id manually
# Method 1 (BizBooks backup) is easier because it handles this!
```

**Recommendation:** Use **Method 1** - it's designed for cross-tenant restore!

**✅ Checkpoint:** Local system has your production data

---

## 🎯 DAILY WORKFLOW

### Starting Work (Every Morning)

```bash
# 1. Start Docker database
docker start bizbooks-local-db

# 2. Navigate to project
cd /Users/rishjain/Downloads/attendence_app

# 3. Activate venv
source venv/bin/activate

# 4. Load environment & start server
export $(cat .env.local | xargs)
python modular_app/app.py

# 5. Open browser: http://localhost:5000
```

**TIP:** Create an alias in your `~/.zshrc`:

```bash
# Add to ~/.zshrc:
alias start-bizbooks='docker start bizbooks-local-db && cd /Users/rishjain/Downloads/attendence_app && source venv/bin/activate && export $(cat .env.local | xargs) && python modular_app/app.py'

# Then just run:
start-bizbooks
```

### Making Changes

```bash
# 1. Create feature branch
git checkout -b feature/add-mrp-field

# 2. Make code changes in Cursor

# 3. Flask auto-reloads - just refresh browser!

# 4. Test thoroughly

# 5. Commit
git add .
git commit -m "feat: Add MRP field to inventory"

# 6. Push feature branch
git push origin feature/add-mrp-field
```

### Ending Work (Every Evening)

```bash
# 1. Commit your work
git add .
git commit -m "wip: End of day progress"
git push origin feature/my-branch

# 2. Stop server (Ctrl+C in terminal)

# 3. Stop Docker (optional, saves battery)
docker stop bizbooks-local-db

# 4. Deactivate venv
deactivate
```

### Deploying to Production (When Feature Ready)

```bash
# 1. Final testing on localhost ✅

# 2. Merge to main
git checkout main
git pull origin main
git merge feature/my-feature

# 3. Push to production (Vercel auto-deploys!)
git push origin main

# 4. Check Vercel dashboard for deployment status
#    https://vercel.com/dashboard

# 5. Test on production URL
#    https://mahaveerelectricals.bizbooks.co.in

# 6. If all good, delete feature branch
git branch -d feature/my-feature
git push origin --delete feature/my-feature
```

---

## 🔧 USEFUL COMMANDS

### Docker Management

```bash
# Start database
docker start bizbooks-local-db

# Stop database
docker stop bizbooks-local-db

# Check status
docker ps

# View logs
docker logs bizbooks-local-db

# Connect to database (psql)
docker exec -it bizbooks-local-db psql -U bizbooks_dev -d bizbooks_dev

# Inside psql:
\dt                    # List tables
\d items              # Describe items table
SELECT COUNT(*) FROM items;  # Count items
\q                    # Quit

# Backup local database
docker exec bizbooks-local-db pg_dump -U bizbooks_dev bizbooks_dev > local_backup.sql

# Restore local database
docker exec -i bizbooks-local-db psql -U bizbooks_dev bizbooks_dev < local_backup.sql

# NUCLEAR OPTION: Delete and recreate (deletes ALL data!)
docker stop bizbooks-local-db
docker rm bizbooks-local-db
# Then run the "Create PostgreSQL container" command from Step 2
```

### Python/Flask

```bash
# Check Python version
python3 --version

# List installed packages
pip list

# Install new package
pip install package-name

# Update requirements.txt
pip freeze > requirements.txt

# Check for import errors
python -c "import flask; import sqlalchemy; print('All imports OK ✅')"

# Run database migration
python modular_app/app.py
# Then visit: http://localhost:5000/migrate/add-mrp-field
```

### Git

```bash
# Check current status
git status

# See all branches
git branch -a

# Switch branch
git checkout branch-name

# Create new branch
git checkout -b feature/new-feature

# View commit history
git log --oneline --graph --all

# Undo unstaged changes
git checkout -- filename

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Stash changes temporarily
git stash
git stash pop  # Restore stashed changes
```

---

## 🚨 TROUBLESHOOTING

### Problem: "Port 5432 already in use"

```bash
# Check what's using port 5432
sudo lsof -i :5432

# If it's old Docker container:
docker stop bizbooks-local-db

# If it's something else:
# Stop that service or use different port in .env.local:
# DATABASE_URL=postgresql://bizbooks_dev:local_dev_password_123@localhost:5433/bizbooks_dev
```

### Problem: "Cannot connect to Docker daemon"

```bash
# Docker Desktop not running
# Solution: Open Docker Desktop app from Applications

# Verify Docker is running:
docker ps
```

### Problem: "Connection refused to localhost:5432"

```bash
# Database not started
docker start bizbooks-local-db

# Check status
docker ps
# Should show bizbooks-local-db as "Up"
```

### Problem: "Module not found" errors

```bash
# venv not activated
source venv/bin/activate

# Dependencies not installed
pip install -r requirements.txt

# Specific package missing
pip install flask-sqlalchemy psycopg2-binary
```

### Problem: "Port 5000 already in use"

```bash
# Find what's using port 5000
sudo lsof -i :5000

# Kill the process
kill -9 [PID]

# OR use different port
export PORT=5001
python modular_app/app.py
```

### Problem: Flask server won't auto-reload

```bash
# Check FLASK_DEBUG is set
echo $FLASK_DEBUG  # Should show: 1

# Reload environment
export $(cat .env.local | xargs)

# Restart server
# Ctrl+C, then: python modular_app/app.py
```

### Problem: Database tables don't exist

```bash
# Server needs to run once to create tables
export $(cat .env.local | xargs)
python modular_app/app.py

# Wait 10 seconds, then stop (Ctrl+C)
# Start again: python modular_app/app.py
```

### Problem: Email testing not working

```bash
# Install MailHog for local email testing
docker run -d -p 1025:1025 -p 8025:8025 mailhog/mailhog

# Update .env.local (already configured!)
# View test emails: http://localhost:8025
```

---

## 🎯 WHAT TO DO NEXT

### ✅ Setup Complete! Now:

1. **Read:** `SECURITY_ISSUES_TO_FIX.md`
   - ⚠️ CRITICAL: Fix forgot password vulnerability
   - 🔒 Add rate limiting
   - 🔐 Session security

2. **Then Read:** `FEATURES_BACKLOG.md`
   - 💰 MRP field
   - 📊 Discount percentage
   - 📦 Barcode system

3. **Create Feature Branch:**
   ```bash
   git checkout -b bugfix/forgot-password-security
   ```

4. **Implement Security Fixes** (Priority 1!)

5. **Test Thoroughly on localhost:5000**

6. **Merge to Main & Deploy**

---

## 📋 QUICK VERIFICATION CHECKLIST

```
✅ Docker Desktop installed and running
✅ PostgreSQL container running (docker ps shows it)
✅ .env.local file exists
✅ venv activated (prompt shows "venv")
✅ Dependencies installed (pip list shows Flask)
✅ Server starts without errors
✅ http://localhost:5000 shows BizBooks
✅ Can create test account
✅ Can login and see dashboard
✅ (Optional) Production backup restored
```

**If all ✅ - You're ready to code! 🚀**

---

## 💡 PRO TIPS FOR YOUR SETUP

### 1. macOS Shortcuts

```bash
# Open terminal quickly
Cmd + Space → type "terminal" → Enter

# New terminal tab
Cmd + T

# Split terminal (iTerm2)
Cmd + D (vertical) or Cmd + Shift + D (horizontal)
```

### 2. Homebrew Maintenance

```bash
# Update Homebrew itself
brew update

# Upgrade all packages
brew upgrade

# Clean up old versions
brew cleanup
```

### 3. Vercel Deployment Tips

```bash
# View deployment logs
# Go to: https://vercel.com/dashboard
# Click your project → Deployments → Click latest → View Logs

# Environment variables
# Vercel Dashboard → Project → Settings → Environment Variables
# Make sure production has:
# - DATABASE_URL (your Supabase connection)
# - SECRET_KEY (different from local!)
# - FLASK_ENV=production
```

### 4. Supabase Tips

```bash
# View database directly
# https://supabase.com/dashboard/project/ymdbpprjagkdkwhkxrno/editor

# View logs
# https://supabase.com/dashboard/project/ymdbpprjagkdkwhkxrno/logs

# Database connection pooling
# Use Transaction pool for better performance:
# postgresql://postgres:[PASSWORD]@db.ymdbpprjagkdkwhkxrno.supabase.co:6543/postgres
# (Note: port 6543 instead of 5432)
```

### 5. Testing Strategy

```
Before pushing to production:

✅ Test on localhost with test account
✅ Test on localhost with production data
✅ Test all existing features (regression)
✅ Check browser console (F12) for errors
✅ Check terminal for errors
✅ Test mobile view (F12 → Toggle Device)
✅ Commit with clear message
✅ Push to feature branch first
✅ Merge to main
✅ Monitor Vercel deployment
✅ Test on production URL
✅ Check Supabase logs for errors
```

---

## 🎉 SUCCESS!

**If you've reached this point:**

1. ✅ Local development environment is working
2. ✅ Docker PostgreSQL is running
3. ✅ BizBooks is accessible at localhost:5000
4. ✅ You can test safely without affecting production
5. ✅ You're ready to implement features!

**Next Priority:** Fix forgot password security issue!

**Read:** `SECURITY_ISSUES_TO_FIX.md` for complete implementation guide.

---

## 🆘 NEED HELP?

### Quick Help Resources

- **Full Guide:** `LOCAL_DEV_SETUP.md`
- **Security Fixes:** `SECURITY_ISSUES_TO_FIX.md`
- **Features:** `FEATURES_BACKLOG.md`
- **Summary:** `SETUP_SUMMARY.md`

### Common Commands Reference

```bash
# Morning routine
docker start bizbooks-local-db
cd /Users/rishjain/Downloads/attendence_app
source venv/bin/activate
export $(cat .env.local | xargs)
python modular_app/app.py

# Evening routine
# Ctrl+C (stop server)
git add . && git commit -m "wip: progress" && git push
docker stop bizbooks-local-db
deactivate
```

---

**You're all set! Happy coding! 🚀**

**Remember: Test locally first, then deploy to production!**

---

**Last Updated:** Dec 2, 2025  
**Your Setup:** macOS + Docker + Supabase (ymdbpprjagkdkwhkxrno) + Vercel  
**Status:** Ready to start! ✅

