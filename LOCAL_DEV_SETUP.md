# 🛠️ Local Development Environment Setup Guide

## 📋 Overview

This guide sets up a complete local development environment for BizBooks, allowing you to:
- ✅ Test new features locally before production
- ✅ Use feature branches safely
- ✅ Work with a local PostgreSQL database
- ✅ Debug without affecting live customers

---

## 🎯 Prerequisites

- macOS (your current system)
- Homebrew installed
- Git already configured
- Python 3.9+ (you have this)
- Terminal access

---

## 📦 OPTION A: Local PostgreSQL with Docker (RECOMMENDED)

### Why Docker?
- ✅ Isolated from your system
- ✅ Easy to reset/clean
- ✅ No conflicts with other software
- ✅ Can run multiple DB versions
- ✅ Easy to delete when done

### Step 1: Install Docker Desktop

```bash
# Install Docker using Homebrew
brew install --cask docker

# OR download from: https://www.docker.com/products/docker-desktop/
```

After installation:
1. Open Docker Desktop app
2. Wait for it to start (Docker icon in menu bar)
3. Accept any prompts

### Step 2: Create PostgreSQL Container

```bash
# Create a Docker container for PostgreSQL
docker run --name bizbooks-local-db \
  -e POSTGRES_PASSWORD=local_dev_password_123 \
  -e POSTGRES_USER=bizbooks_dev \
  -e POSTGRES_DB=bizbooks_dev \
  -p 5432:5432 \
  -d postgres:15

# Verify it's running
docker ps

# You should see: bizbooks-local-db ... Up ... 0.0.0.0:5432->5432/tcp
```

### Step 3: Connection String

Your local database connection string:
```
postgresql://bizbooks_dev:local_dev_password_123@localhost:5432/bizbooks_dev
```

### Docker Management Commands

```bash
# Start database (if stopped)
docker start bizbooks-local-db

# Stop database
docker stop bizbooks-local-db

# View logs
docker logs bizbooks-local-db

# Connect to database (psql)
docker exec -it bizbooks-local-db psql -U bizbooks_dev -d bizbooks_dev

# Reset database (delete all data)
docker stop bizbooks-local-db
docker rm bizbooks-local-db
# Then run the "Create PostgreSQL Container" command again

# Backup local database
docker exec bizbooks-local-db pg_dump -U bizbooks_dev bizbooks_dev > local_backup.sql

# Restore from backup
docker exec -i bizbooks-local-db psql -U bizbooks_dev bizbooks_dev < local_backup.sql
```

---

## 📦 OPTION B: Install PostgreSQL Directly (Alternative)

### Step 1: Install PostgreSQL

```bash
# Install PostgreSQL using Homebrew
brew install postgresql@15

# Start PostgreSQL service
brew services start postgresql@15

# Verify installation
psql --version
```

### Step 2: Create Database

```bash
# Create user
createuser -s bizbooks_dev

# Create database
createdb -O bizbooks_dev bizbooks_dev

# Set password (if needed)
psql -c "ALTER USER bizbooks_dev WITH PASSWORD 'local_dev_password_123';"
```

### Step 3: Connection String

```
postgresql://bizbooks_dev:local_dev_password_123@localhost:5432/bizbooks_dev
```

### PostgreSQL Management Commands

```bash
# Start PostgreSQL
brew services start postgresql@15

# Stop PostgreSQL
brew services stop postgresql@15

# Restart PostgreSQL
brew services restart postgresql@15

# Connect to database
psql -U bizbooks_dev -d bizbooks_dev

# Backup database
pg_dump -U bizbooks_dev bizbooks_dev > local_backup.sql

# Restore from backup
psql -U bizbooks_dev bizbooks_dev < local_backup.sql
```

---

## 🔄 Backup Supabase → Restore Locally

### Step 1: Get Supabase Backup

**Method A: Using BizBooks Built-in Backup (JSON format)**
```bash
# 1. Login to your BizBooks production
# 2. Go to: Settings & Backup → Backup & Download
# 3. Click "Create Backup"
# 4. Download JSON file (e.g., backup_mahaveer_20250102.json)
```

**Method B: Direct PostgreSQL Dump from Supabase (SQL format)**
```bash
# Get your Supabase connection string from:
# Supabase Dashboard → Project Settings → Database → Connection String (URI)

# It looks like:
# postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres

# Run pg_dump
pg_dump "postgresql://postgres:[PASSWORD]@db.[PROJECT].supabase.co:5432/postgres" \
  --no-owner --no-acl > supabase_backup.sql
```

### Step 2: Restore to Local Database

**If you used Method A (JSON backup):**
```bash
# 1. Start your local Flask app (see below)
# 2. Create a new tenant account on localhost:5000
# 3. Go to: Settings & Backup → Restore Backup
# 4. Upload the JSON file
# ✅ Data restored!
```

**If you used Method B (SQL dump):**
```bash
# For Docker:
docker exec -i bizbooks-local-db psql -U bizbooks_dev bizbooks_dev < supabase_backup.sql

# For direct PostgreSQL:
psql -U bizbooks_dev bizbooks_dev < supabase_backup.sql
```

---

## 🌿 Git Branching Strategy

### Branch Structure

```
main (production)
  ↓
  └── feature/mrp-and-discount
  └── feature/forgot-password-fix
  └── feature/barcode-system
  └── bugfix/employee-cash-duplicate
```

### Workflow

```bash
# 1. Always start from main
git checkout main
git pull origin main

# 2. Create feature branch
git checkout -b feature/add-mrp-field

# 3. Make changes, test locally
# ... code code code ...

# 4. Commit changes
git add .
git commit -m "feat: Add MRP field to inventory"

# 5. Push feature branch
git push origin feature/add-mrp-field

# 6. When ready for production:
git checkout main
git merge feature/add-mrp-field
git push origin main

# 7. Delete feature branch (cleanup)
git branch -d feature/add-mrp-field
git push origin --delete feature/add-mrp-field
```

---

## 🚀 Running Local Development Server

### Step 1: Create `.env.local` file

```bash
# Create local environment file
cat > .env.local << EOF
# Local Development Environment
FLASK_ENV=development
FLASK_DEBUG=1

# Local PostgreSQL (Docker)
DATABASE_URL=postgresql://bizbooks_dev:local_dev_password_123@localhost:5432/bizbooks_dev

# Secret keys (use different keys for local!)
SECRET_KEY=local_dev_secret_key_do_not_use_in_production

# Email (optional for local - can skip)
MAIL_SERVER=localhost
MAIL_PORT=1025
MAIL_USE_TLS=False
MAIL_USERNAME=
MAIL_PASSWORD=

# Local ports
PORT=5000
EOF
```

### Step 2: Activate Virtual Environment

```bash
cd /Users/rishjain/Downloads/attendence_app

# Activate venv
source venv/bin/activate

# Verify activation (should show venv path)
which python3
```

### Step 3: Install Dependencies

```bash
# Install/update all dependencies
pip install -r requirements.txt

# If you don't have a requirements.txt, create one:
pip freeze > requirements.txt
```

### Step 4: Run Local Server

```bash
# Load local environment variables
export $(cat .env.local | xargs)

# Run Flask app
python modular_app/app.py

# OR if you have flask command:
flask run --host=0.0.0.0 --port=5000

# Server should start at: http://localhost:5000
```

### Step 5: Access Local BizBooks

```
Open browser: http://localhost:5000

1. Create a new tenant account (for testing)
2. Or restore backup from production
3. Test your features!
```

---

## 🔄 Daily Development Workflow

### Morning (Starting Work)

```bash
# 1. Start Docker database (if using Docker)
docker start bizbooks-local-db

# 2. Navigate to project
cd /Users/rishjain/Downloads/attendence_app

# 3. Activate venv
source venv/bin/activate

# 4. Pull latest changes
git checkout main
git pull origin main

# 5. Create/switch to feature branch
git checkout -b feature/my-new-feature
# OR: git checkout feature/existing-feature

# 6. Start local server
export $(cat .env.local | xargs)
python modular_app/app.py

# 7. Open browser: http://localhost:5000
```

### During Work (Testing)

```bash
# Make code changes in VS Code/Cursor

# Flask auto-reloads (if FLASK_DEBUG=1)
# Just refresh browser to see changes!

# Check terminal for errors
# Check browser console (F12) for JS errors

# Commit frequently
git add .
git commit -m "wip: testing new feature"
```

### Evening (End of Day)

```bash
# 1. Commit all work
git add .
git commit -m "feat: Completed X feature"

# 2. Push feature branch (backup)
git push origin feature/my-new-feature

# 3. Stop local server (Ctrl+C)

# 4. Stop Docker (optional, saves battery)
docker stop bizbooks-local-db

# 5. Deactivate venv
deactivate
```

### When Feature is Ready

```bash
# 1. Final testing on local
# ... test everything ...

# 2. Merge to main
git checkout main
git merge feature/my-new-feature

# 3. Push to production
git push origin main

# 4. Monitor production deployment
# (Check your hosting platform - Render/Railway/etc)

# 5. Test on production URL
# https://mahaveerelectricals.bizbooks.co.in

# 6. If all good, delete feature branch
git branch -d feature/my-new-feature
git push origin --delete feature/my-new-feature
```

---

## 🧪 Testing Checklist (Before Pushing to Production)

```
Local Testing:
✅ Feature works on http://localhost:5000
✅ No console errors (F12 → Console)
✅ No terminal errors
✅ Database changes applied (migrations)
✅ All existing features still work
✅ Mobile responsive (F12 → Toggle Device Toolbar)
✅ Test with fresh tenant account
✅ Test with restored production backup

Code Quality:
✅ No hardcoded values
✅ No debug print statements
✅ Proper error handling
✅ User feedback messages (success/error)
✅ Commit message is clear

Git:
✅ All changes committed
✅ Feature branch pushed (backup)
✅ No merge conflicts with main
```

---

## 🚨 Emergency Rollback

If something breaks in production:

```bash
# 1. Find last working commit
git log --oneline

# Example output:
# a1b2c3d (HEAD -> main) feat: New feature (BROKEN)
# e4f5g6h feat: Previous feature (WORKING)

# 2. Revert to working commit
git revert a1b2c3d

# 3. Push revert
git push origin main

# 4. Fix issue locally on feature branch
git checkout -b bugfix/fix-broken-feature
# ... fix code ...
git add .
git commit -m "fix: Corrected issue with new feature"
git push origin bugfix/fix-broken-feature

# 5. Test thoroughly locally

# 6. Merge fix to main
git checkout main
git merge bugfix/fix-broken-feature
git push origin main
```

---

## 📊 Monitoring Local vs Production

### Local Development
- **URL:** http://localhost:5000
- **Database:** Local PostgreSQL (Docker or direct)
- **Data:** Test data / restored backup
- **Purpose:** Safe testing, no customer impact

### Production
- **URL:** https://mahaveerelectricals.bizbooks.co.in
- **Database:** Supabase PostgreSQL
- **Data:** Real customer data
- **Purpose:** Live operations

**NEVER test unfinished features on production!**

---

## 🔧 Troubleshooting

### "Port 5432 already in use"
```bash
# Check what's using port 5432
lsof -i :5432

# Stop the process
docker stop bizbooks-local-db
# OR
brew services stop postgresql@15
```

### "Connection refused to localhost:5432"
```bash
# Check if Docker is running
docker ps

# Start database
docker start bizbooks-local-db

# Check logs
docker logs bizbooks-local-db
```

### "Module not found" errors
```bash
# Ensure venv is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Flask server won't start
```bash
# Check if port 5000 is available
lsof -i :5000

# Kill process using port 5000
kill -9 [PID]

# Try different port
flask run --port=5001
```

### Database migrations fail
```bash
# Check current database schema
docker exec -it bizbooks-local-db psql -U bizbooks_dev bizbooks_dev -c "\dt"

# Drop and recreate database (CAUTION: deletes all data)
docker exec -it bizbooks-local-db psql -U bizbooks_dev -c "DROP DATABASE bizbooks_dev;"
docker exec -it bizbooks-local-db psql -U bizbooks_dev -c "CREATE DATABASE bizbooks_dev;"

# Restore from backup
# (see "Backup Supabase → Restore Locally" section above)
```

---

## 📚 Additional Resources

### Useful Commands Reference

```bash
# Python/Flask
python --version                    # Check Python version
pip list                           # List installed packages
pip freeze > requirements.txt      # Save dependencies
flask routes                       # List all routes

# Docker
docker ps                          # List running containers
docker ps -a                       # List all containers
docker images                      # List images
docker system prune                # Clean up unused Docker resources

# Git
git status                         # Check current changes
git log --oneline --graph          # Visual commit history
git branch -a                      # List all branches
git diff                          # Show unstaged changes
git stash                         # Temporarily save changes
git stash pop                     # Restore stashed changes

# PostgreSQL
\dt                               # List tables (in psql)
\d table_name                     # Describe table structure
\q                                # Quit psql
```

### File Structure

```
attendence_app/
├── .env.local              # Local environment variables (DON'T COMMIT!)
├── .gitignore             # Ignore .env.local, venv, etc.
├── requirements.txt       # Python dependencies
├── modular_app/
│   ├── app.py            # Main Flask app
│   ├── routes/           # All route files
│   ├── models/           # Database models
│   ├── templates/        # HTML templates
│   └── static/           # CSS, JS, images
├── venv/                 # Virtual environment
└── instance/             # SQLite (not used in production)
```

---

## ✅ Setup Complete Checklist

```
✅ PostgreSQL installed (Docker or direct)
✅ Database created and running
✅ .env.local file created
✅ Virtual environment activated
✅ Dependencies installed
✅ Local server starts successfully
✅ Can access http://localhost:5000
✅ Can create tenant account
✅ Git branches working
✅ Backup/restore tested
```

---

## 🎯 Next Steps

Once local development is working:

1. **Fix Critical Security Issues:**
   - Forgot password email verification
   - Password reset token system

2. **Add New Features:**
   - MRP field in inventory
   - Discount percentage on invoice
   - Barcode system

3. **Test Each Feature Locally First**
4. **Only Push to Production When Confident**

---

## 💡 Pro Tips

1. **Always work on feature branches** - never directly on main
2. **Commit frequently** - small commits are easier to revert
3. **Test with real data** - restore production backup to local
4. **Keep local and production separate** - use .env.local vs .env
5. **Document your changes** - clear commit messages
6. **Backup before major changes** - both local and production

---

## 🆘 Need Help?

If you encounter issues:
1. Check terminal output for error messages
2. Check browser console (F12) for JavaScript errors
3. Check Docker logs: `docker logs bizbooks-local-db`
4. Try restarting services
5. Check this troubleshooting guide

---

**Happy Coding! 🚀**

