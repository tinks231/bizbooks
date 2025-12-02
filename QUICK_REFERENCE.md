# ⚡ Quick Reference - Copy-Paste Commands

**For when you need commands fast!**

---

## 🚀 SETUP (One-Time, 30 mins)

```bash
# 1. Install Docker
brew install --cask docker

# 2. Create PostgreSQL
docker run --name bizbooks-local-db \
  -e POSTGRES_PASSWORD=local_dev_password_123 \
  -e POSTGRES_USER=bizbooks_dev \
  -e POSTGRES_DB=bizbooks_dev \
  -p 5432:5432 \
  -d postgres:15

# 3. Create .env.local
cd /Users/rishjain/Downloads/attendence_app
cat > .env.local << 'EOF'
FLASK_ENV=development
FLASK_DEBUG=1
PORT=5000
DATABASE_URL=postgresql://bizbooks_dev:local_dev_password_123@localhost:5432/bizbooks_dev
SECRET_KEY=local_dev_secret_key_12345
MAIL_SERVER=localhost
MAIL_PORT=1025
EOF

# 4. Start server
source venv/bin/activate
export $(cat .env.local | xargs)
python modular_app/app.py

# 5. Open: http://localhost:5000
```

---

## 🌅 MORNING (Start Work)

```bash
docker start bizbooks-local-db
cd /Users/rishjain/Downloads/attendence_app
source venv/bin/activate
export $(cat .env.local | xargs)
python modular_app/app.py
```

**Then open:** http://localhost:5000

---

## 🛠️ DURING WORK (Feature Development)

```bash
# Create feature branch
git checkout -b feature/add-mrp

# Make changes, test on localhost:5000

# Commit frequently
git add .
git commit -m "feat: Add MRP field"

# Push (backup)
git push origin feature/add-mrp
```

---

## 🌆 EVENING (End Work)

```bash
# Commit work
git add .
git commit -m "wip: Progress on feature"
git push origin feature/my-branch

# Stop server: Ctrl+C

# Stop Docker (optional)
docker stop bizbooks-local-db

# Deactivate venv
deactivate
```

---

## 🚀 DEPLOY TO PRODUCTION

```bash
# 1. Final test on local ✅

# 2. Merge to main
git checkout main
git pull origin main
git merge feature/my-feature

# 3. Push (Vercel auto-deploys!)
git push origin main

# 4. Monitor: https://vercel.com/dashboard

# 5. Test: https://mahaveerelectricals.bizbooks.co.in

# 6. Delete feature branch
git branch -d feature/my-feature
git push origin --delete feature/my-feature
```

---

## 🔧 DOCKER COMMANDS

```bash
docker start bizbooks-local-db       # Start
docker stop bizbooks-local-db        # Stop
docker ps                            # Check status
docker logs bizbooks-local-db        # View logs
docker exec -it bizbooks-local-db psql -U bizbooks_dev -d bizbooks_dev  # Connect
```

---

## 💾 BACKUP & RESTORE

```bash
# Production → Download JSON
# https://mahaveerelectricals.bizbooks.co.in
# Settings & Backup → Create Backup → Download

# Local → Upload JSON
# http://localhost:5000
# Settings & Backup → Restore Backup → Upload
```

---

## 🚨 TROUBLESHOOTING

```bash
# Port 5432 in use
docker stop bizbooks-local-db

# Port 5000 in use
sudo lsof -i :5000
kill -9 [PID]

# Module not found
source venv/bin/activate
pip install -r requirements.txt

# Database connection failed
docker start bizbooks-local-db
```

---

## 📚 FULL GUIDES

- **Setup:** `YOUR_PERSONALIZED_SETUP.md`
- **Security:** `SECURITY_ISSUES_TO_FIX.md`
- **Features:** `FEATURES_BACKLOG.md`
- **Complete:** `LOCAL_DEV_SETUP.md`

---

## 🎯 NEXT PRIORITY

**Fix forgot password security!** (See: `SECURITY_ISSUES_TO_FIX.md`)

---

**Save this file for quick reference! 📌**

