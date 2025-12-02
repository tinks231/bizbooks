# 🚀 Quick Start: Local Development Setup

**Goal:** Get local development environment running in 30 minutes!

---

## ✅ STEP-BY-STEP CHECKLIST

### Step 1: Install Docker Desktop (10 mins)

```bash
# Install Docker
brew install --cask docker

# OR download: https://www.docker.com/products/docker-desktop/

# Open Docker Desktop app
# Wait for Docker to start (Docker whale icon in menu bar)
```

✅ **Verify:** Run `docker ps` in terminal (should show no errors)

---

### Step 2: Create Local PostgreSQL Database (2 mins)

```bash
# Create and start PostgreSQL container
docker run --name bizbooks-local-db \
  -e POSTGRES_PASSWORD=local_dev_password_123 \
  -e POSTGRES_USER=bizbooks_dev \
  -e POSTGRES_DB=bizbooks_dev \
  -p 5432:5432 \
  -d postgres:15

# Verify it's running
docker ps
```

✅ **Verify:** You should see `bizbooks-local-db` in the list with status "Up"

---

### Step 3: Create Local Environment File (2 mins)

```bash
# Navigate to project
cd /Users/rishjain/Downloads/attendence_app

# Create .env.local file
cat > .env.local << 'EOF'
# Local Development Environment
FLASK_ENV=development
FLASK_DEBUG=1

# Local PostgreSQL
DATABASE_URL=postgresql://bizbooks_dev:local_dev_password_123@localhost:5432/bizbooks_dev

# Secret key (different from production!)
SECRET_KEY=local_dev_secret_key_change_this_in_production

# Email (optional - can configure later)
MAIL_SERVER=localhost
MAIL_PORT=1025
MAIL_USE_TLS=False

# Port
PORT=5000
EOF
```

✅ **Verify:** Run `ls -la .env.local` (file should exist)

---

### Step 4: Activate Virtual Environment (1 min)

```bash
# Make sure you're in project directory
cd /Users/rishjain/Downloads/attendence_app

# Activate venv
source venv/bin/activate

# Your prompt should show: (venv) $
```

✅ **Verify:** Run `which python3` (should show path inside venv/)

---

### Step 5: Install/Update Dependencies (3 mins)

```bash
# Install all dependencies
pip install -r requirements.txt

# If any missing packages, add them
pip install Flask-SQLAlchemy Flask-Migrate python-dotenv psycopg2-binary
```

✅ **Verify:** Run `pip list` (should show Flask, SQLAlchemy, etc.)

---

### Step 6: Start Local Server (2 mins)

```bash
# Load environment variables from .env.local
export $(cat .env.local | xargs)

# Start Flask app
python modular_app/app.py

# Server should start and show:
# * Running on http://0.0.0.0:5000
```

✅ **Verify:** Open browser to http://localhost:5000

---

### Step 7: Create Test Account (2 mins)

1. Go to: http://localhost:5000
2. Click "Sign Up" or "Register"
3. Create a new tenant account:
   - Business Name: "Local Testing Co"
   - Email: test@localhost.com
   - Password: test123
   - Subdomain: localtesting

✅ **Verify:** You can log in and see the dashboard

---

### Step 8: (Optional) Restore Production Backup (5 mins)

If you want to test with real data:

1. Go to production: https://mahaveerelectricals.bizbooks.co.in
2. Login
3. Go to: Settings & Backup → Backup & Download
4. Click "Create Backup" → Download JSON file
5. On local: http://localhost:5000
6. Go to: Settings & Backup → Restore Backup
7. Upload the JSON file
8. Wait for restore to complete

✅ **Verify:** Your local account now has production data!

---

## 🎯 DAILY WORKFLOW QUICK REFERENCE

### Starting Work (Every Morning)

```bash
# 1. Start Docker database
docker start bizbooks-local-db

# 2. Navigate to project
cd /Users/rishjain/Downloads/attendence_app

# 3. Activate venv
source venv/bin/activate

# 4. Start server
export $(cat .env.local | xargs)
python modular_app/app.py

# 5. Open browser: http://localhost:5000
```

---

### Making Changes

```bash
# 1. Create feature branch
git checkout -b feature/my-new-feature

# 2. Make code changes in Cursor/VS Code

# 3. Flask auto-reloads (just refresh browser!)

# 4. Test thoroughly on local

# 5. Commit changes
git add .
git commit -m "feat: Description of change"

# 6. Push feature branch
git push origin feature/my-new-feature
```

---

### Ending Work (Every Evening)

```bash
# 1. Commit all work
git add .
git commit -m "wip: End of day commit"
git push origin feature/my-new-feature

# 2. Stop server (Ctrl+C in terminal)

# 3. Stop Docker (optional)
docker stop bizbooks-local-db

# 4. Deactivate venv
deactivate
```

---

### Deploying to Production (When Feature Ready)

```bash
# 1. Final testing on local ✅

# 2. Merge to main
git checkout main
git pull origin main
git merge feature/my-new-feature

# 3. Push to production
git push origin main

# 4. Monitor deployment
# (Check your hosting platform)

# 5. Test on production URL
# https://mahaveerelectricals.bizbooks.co.in

# 6. If all good, delete feature branch
git branch -d feature/my-new-feature
git push origin --delete feature/my-new-feature
```

---

## 🔧 USEFUL COMMANDS

### Docker

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

# Reset database (delete all data!)
docker stop bizbooks-local-db
docker rm bizbooks-local-db
# Then create container again
```

### Git

```bash
# Check status
git status

# See all branches
git branch -a

# Switch branches
git checkout branch-name

# Create new branch
git checkout -b feature/new-feature

# See commit history
git log --oneline --graph

# Discard changes
git checkout -- filename
```

### Python/Flask

```bash
# Check Python version
python3 --version

# List installed packages
pip list

# Install new package
pip install package-name

# Save dependencies
pip freeze > requirements.txt

# Check for import errors
python -c "import flask; import sqlalchemy; print('OK')"
```

---

## 🚨 TROUBLESHOOTING

### "Port 5432 already in use"

```bash
# Stop the database
docker stop bizbooks-local-db

# OR check what's using the port
lsof -i :5432
```

### "Connection refused to localhost:5432"

```bash
# Start the database
docker start bizbooks-local-db

# Check if Docker is running
docker ps
```

### "Module not found" errors

```bash
# Make sure venv is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### "Port 5000 already in use"

```bash
# Find what's using port 5000
lsof -i :5000

# Kill it
kill -9 [PID]

# OR use different port
export PORT=5001
python modular_app/app.py
```

### Flask not reloading automatically

```bash
# Make sure FLASK_DEBUG=1 in .env.local
export FLASK_DEBUG=1

# Restart server
# Ctrl+C, then python modular_app/app.py
```

---

## 📋 PRE-PRODUCTION CHECKLIST

Before pushing to production:

```
✅ Feature works on http://localhost:5000
✅ Tested with test account
✅ Tested with production backup data
✅ No console errors (F12 → Console)
✅ No terminal errors
✅ Mobile responsive (F12 → Toggle Device)
✅ All existing features still work
✅ Commit message is clear
✅ Feature branch pushed (backup)
✅ Ready to merge to main
```

---

## 🆘 HELP

### Full Documentation
- **Complete Guide:** `LOCAL_DEV_SETUP.md`
- **Security Issues:** `SECURITY_ISSUES_TO_FIX.md`

### Quick Help Commands

```bash
# Docker help
docker --help

# Git help
git --help

# Flask help
flask --help

# Python help
python3 --help
```

---

## 🎯 WHAT'S NEXT?

After local development is working:

1. **Fix Security Issues (URGENT!):**
   - See `SECURITY_ISSUES_TO_FIX.md`
   - Forgot password vulnerability
   - Rate limiting
   - Session security

2. **Add New Features:**
   - MRP field in inventory
   - Discount percentage on invoice
   - Barcode system

3. **Test Everything Locally First!**
4. **Only Push to Production When Confident!**

---

**You're all set! Happy coding! 🚀**

**Questions? Check the full guide: LOCAL_DEV_SETUP.md**

