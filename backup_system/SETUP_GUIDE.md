# 🔐 BizBooks Backup System - Setup Guide

Complete guide to setup automated daily backups for BizBooks database.

---

## 📋 **What This System Does:**

- ✅ **Automatic daily backups** at 11:00 AM IST
- ✅ **Compressed storage** (saves 70-80% space)
- ✅ **30-day retention** (auto-deletes old backups)
- ✅ **One-click restore** from any backup
- ✅ **Detailed logging** of all operations
- ✅ **Email alerts** (optional) on failures

---

## 🚀 **Quick Start (5 Minutes)**

### **Step 1: Install PostgreSQL Client**

The backup system needs `pg_dump` and `psql` commands.

```bash
# macOS (using Homebrew)
brew install postgresql

# Verify installation
pg_dump --version
psql --version
```

**Expected output:**
```
pg_dump (PostgreSQL) 15.x
psql (PostgreSQL) 15.x
```

---

### **Step 2: Get Your Supabase Connection String**

1. Go to: https://supabase.com/dashboard
2. Select your BizBooks project
3. Click **Settings** (⚙️) → **Database**
4. Find **Connection string** → **URI**
5. Copy the full string (looks like):
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.xxxxx.supabase.co:5432/postgres
   ```

---

### **Step 3: Configure Backup System**

```bash
# Navigate to backup system folder
cd /Users/rishjain/Downloads/attendence_app/backup_system

# Copy example config
cp config.env.example config.env

# Edit config (add your DATABASE_URL)
nano config.env
```

**Edit `config.env`:**
```bash
# Paste your Supabase connection string here
DATABASE_URL=postgresql://postgres:YOUR_ACTUAL_PASSWORD@db.xxxxx.supabase.co:5432/postgres

# Backup location (already set)
BACKUP_DIR=/Users/rishjain/Downloads/bizbooks/backup

# Keep backups for 30 days
RETENTION_DAYS=30
```

**Save:** Press `Ctrl+O`, `Enter`, then `Ctrl+X`

---

### **Step 4: Test Backup (Manual Run)**

```bash
# Run backup once to test
python3 backup_manager.py
```

**Expected output:**
```
============================================================
🚀 BizBooks Database Backup Manager
============================================================
🔍 Checking prerequisites...
✅ PostgreSQL client found: pg_dump (PostgreSQL) 15.x
🔄 Starting backup process...
📊 Creating backup: bizbooks_backup_2024-11-02_11-00-00.sql
✅ Backup created: bizbooks_backup_2024-11-02_11-00-00.sql (2.45 MB)
🗜️  Compressing backup...
✅ Backup compressed: 0.52 MB (saved 78.8%)
🧹 Cleaning up backups older than 30 days...
✅ No old backups to clean up
✅ Backup process completed successfully!

📋 Available backups:
  📦 bizbooks_backup_2024-11-02_11-00-00.sql.gz - 0.52 MB - 2024-11-02 11:00:15

✅ Total backups: 1
============================================================
```

**✅ If you see this, backup is working!**

---

### **Step 5: Schedule Daily Automatic Backups**

```bash
# Run scheduler script
chmod +x schedule_backup.sh
./schedule_backup.sh
```

**Expected output:**
```
======================================
BizBooks Backup Scheduler
======================================

✅ Python 3 found: /usr/bin/python3
✅ Loading configuration from config.env
✅ Backup directory: /Users/rishjain/Downloads/bizbooks/backup
✅ Created wrapper script: run_backup.sh

Creating LaunchAgent for automatic backups...
✅ Created LaunchAgent: ~/Library/LaunchAgents/com.bizbooks.backup.plist
✅ LaunchAgent loaded successfully!

🎉 Backup scheduled successfully!
   ⏰ Daily backup at: 11:00 AM IST
   📁 Backup location: /Users/rishjain/Downloads/bizbooks/backup
   📝 Logs: /Users/rishjain/Downloads/bizbooks/backup/backup.log

💡 Useful commands:
   Test backup now:  python3 backup_manager.py
   View logs:        tail -f /Users/rishjain/Downloads/bizbooks/backup/backup.log
   Unschedule:       launchctl unload ~/Library/LaunchAgents/com.bizbooks.backup.plist
   Re-schedule:      launchctl load ~/Library/LaunchAgents/com.bizbooks.backup.plist

======================================
```

**🎉 Done! Backups will run automatically every day at 11:00 AM!**

---

## 🔄 **Restore Database**

### **List All Backups:**

```bash
python3 restore_manager.py --list
```

**Output:**
```
📋 Available backups:
  1. bizbooks_backup_2024-11-02_11-00-00.sql.gz
     Size: 0.52 MB | Date: 2024-11-02 11:00:15
  2. bizbooks_backup_2024-11-01_11-00-00.sql.gz
     Size: 0.48 MB | Date: 2024-11-01 11:00:00

✅ Total backups: 2
```

---

### **Restore from Latest Backup:**

```bash
python3 restore_manager.py --latest
```

**⚠️ Warning:** This will ask for confirmation and create a safety backup first!

---

### **Restore from Specific Backup:**

```bash
python3 restore_manager.py --restore bizbooks_backup_2024-11-01_11-00-00.sql.gz
```

---

## 📁 **Backup Location & Files**

**All backups are stored in:**
```
/Users/rishjain/Downloads/bizbooks/backup/
```

**Files you'll find:**
```
├── bizbooks_backup_2024-11-02_11-00-00.sql.gz  ← Compressed backup
├── bizbooks_backup_2024-11-01_11-00-00.sql.gz
├── bizbooks_backup_2024-10-31_11-00-00.sql.gz
├── backup.log                                   ← Backup logs
└── restore.log                                  ← Restore logs
```

**Backup file naming:**
```
bizbooks_backup_YYYY-MM-DD_HH-MM-SS.sql.gz

Example:
bizbooks_backup_2024-11-02_11-00-15.sql.gz
                │          │
                │          └─ Time: 11:00:15 AM
                └─ Date: November 2, 2024
```

---

## 📊 **Monitor Backups**

### **View Backup Logs:**

```bash
# Real-time log monitoring
tail -f /Users/rishjain/Downloads/bizbooks/backup/backup.log

# View last 50 lines
tail -50 /Users/rishjain/Downloads/bizbooks/backup/backup.log

# View today's backups only
grep "$(date +%Y-%m-%d)" /Users/rishjain/Downloads/bizbooks/backup/backup.log
```

---

### **Check Backup Size:**

```bash
du -sh /Users/rishjain/Downloads/bizbooks/backup/
```

**Example output:**
```
15M     /Users/rishjain/Downloads/bizbooks/backup/
```

*This shows total space used by all backups (30 days worth)*

---

### **Count Backups:**

```bash
ls -1 /Users/rishjain/Downloads/bizbooks/backup/bizbooks_backup_*.sql.gz | wc -l
```

**Expected:** ~30 backups (one per day for 30 days)

---

## ⚙️ **Advanced Configuration**

### **Change Backup Time:**

Edit the LaunchAgent file:
```bash
nano ~/Library/LaunchAgents/com.bizbooks.backup.plist
```

Find this section:
```xml
<key>StartCalendarInterval</key>
<dict>
    <key>Hour</key>
    <integer>11</integer>        <!-- Change this -->
    <key>Minute</key>
    <integer>0</integer>         <!-- And this -->
</dict>
```

**Examples:**
- `11:00 AM` → Hour: 11, Minute: 0
- `2:30 PM` → Hour: 14, Minute: 30
- `11:59 PM` → Hour: 23, Minute: 59

After editing:
```bash
launchctl unload ~/Library/LaunchAgents/com.bizbooks.backup.plist
launchctl load ~/Library/LaunchAgents/com.bizbooks.backup.plist
```

---

### **Change Retention Period:**

Edit `config.env`:
```bash
nano config.env
```

Change:
```
RETENTION_DAYS=30    # Keep 30 days (default)
RETENTION_DAYS=60    # Keep 60 days
RETENTION_DAYS=7     # Keep 7 days only
```

---

### **Enable Email Alerts:**

Edit `config.env`:
```bash
SEND_EMAIL_ALERTS=true
ALERT_EMAIL=rishi.jain@example.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-gmail-app-password
```

**To get Gmail App Password:**
1. Go to: https://myaccount.google.com/apppasswords
2. Generate new app password
3. Paste it in `SMTP_PASSWORD`

---

## 🧪 **Test Restore (Without Risk)**

### **Install PostgreSQL Locally:**

```bash
# macOS
brew install postgresql@15
brew services start postgresql@15

# Create test database
createdb bizbooks_test
```

---

### **Test Restore to Local DB:**

1. Edit `restore_manager.py` temporarily
2. Change `DATABASE_URL` to local:
   ```python
   DB_URL = "postgresql://localhost/bizbooks_test"
   ```
3. Run restore:
   ```bash
   python3 restore_manager.py --latest --no-safety-backup
   ```
4. Verify data:
   ```bash
   psql bizbooks_test
   \dt                    # List tables
   SELECT COUNT(*) FROM tenants;
   SELECT COUNT(*) FROM employees;
   \q                     # Quit
   ```

**✅ If you see data, restore is working!**

---

## 🛠️ **Troubleshooting**

### **Problem: pg_dump not found**

**Solution:**
```bash
# Install PostgreSQL client
brew install postgresql

# Verify
which pg_dump
```

---

### **Problem: Permission denied**

**Solution:**
```bash
# Make scripts executable
chmod +x schedule_backup.sh
chmod +x backup_manager.py
chmod +x restore_manager.py
```

---

### **Problem: DATABASE_URL not found**

**Solution:**
```bash
# Check if config.env exists
cat config.env

# If not, create it
cp config.env.example config.env
nano config.env
# Add your DATABASE_URL
```

---

### **Problem: Backup fails with connection error**

**Solution:**
1. Verify DATABASE_URL is correct
2. Test connection manually:
   ```bash
   psql "postgresql://postgres:PASSWORD@db.xxxxx.supabase.co:5432/postgres"
   ```
3. Check if Supabase project is paused (free tier pauses after 7 days inactivity)

---

### **Problem: LaunchAgent not running**

**Check status:**
```bash
launchctl list | grep bizbooks
```

**If not running:**
```bash
# Reload
launchctl unload ~/Library/LaunchAgents/com.bizbooks.backup.plist
launchctl load ~/Library/LaunchAgents/com.bizbooks.backup.plist
```

**Check logs:**
```bash
cat /Users/rishjain/Downloads/bizbooks/backup/scheduler.log
cat /Users/rishjain/Downloads/bizbooks/backup/scheduler_error.log
```

---

## 📌 **Important Notes**

### **Free Tier Considerations:**

**Supabase Free Tier:**
- ✅ 500MB storage (plenty for testing)
- ⚠️ Pauses after 7 days inactivity
- ⚠️ Can be deleted without notice

**Protection:**
- ✅ Daily backups to YOUR computer (safe!)
- ✅ 30-day retention (even if Supabase deletes)
- ✅ Can restore anytime

---

### **Backup Best Practices:**

1. **Test restore monthly** - Verify backups work!
2. **Keep multiple copies** - Local + Google Drive
3. **Monitor disk space** - Delete very old backups if needed
4. **Before major changes** - Take manual backup:
   ```bash
   python3 backup_manager.py
   ```

---

## 🎯 **Next Steps:**

### **After Setup:**

1. ✅ **Wait for tomorrow** - Let automatic backup run at 11:00 AM
2. ✅ **Check logs** next day:
   ```bash
   tail -20 /Users/rishjain/Downloads/bizbooks/backup/backup.log
   ```
3. ✅ **Install local PostgreSQL** (for testing restore)
4. ✅ **Test restore once** to local DB (verify it works!)

---

### **Optional Enhancements:**

1. **Google Drive backup** (next guide)
2. **Incremental backups** (faster, less space)
3. **Encrypted backups** (for sensitive data)
4. **Remote monitoring** (get alerts on phone)

---

## 📞 **Need Help?**

**Check logs first:**
```bash
tail -50 /Users/rishjain/Downloads/bizbooks/backup/backup.log
```

**Common issues:**
- ✅ Wrong DATABASE_URL → Check config.env
- ✅ pg_dump not found → Install PostgreSQL client
- ✅ Permission denied → chmod +x scripts
- ✅ Backup too large → Database has grown (upgrade Supabase plan)

---

## ✅ **Success Checklist:**

- [ ] PostgreSQL client installed (`pg_dump --version` works)
- [ ] config.env created with correct DATABASE_URL
- [ ] Manual backup successful (test run)
- [ ] LaunchAgent scheduled (runs at 11:00 AM daily)
- [ ] Backup log shows success
- [ ] At least 1 backup file exists in backup folder
- [ ] Local PostgreSQL installed (for testing)
- [ ] Test restore successful

**If all checked → You're fully protected! 🎉**

---

## 🚀 **Ready for Production:**

Once backups are working reliably:
1. Test with friends/family
2. Monitor for 1 week
3. Verify restore works
4. Then onboard real clients!

**Data safety = Business confidence!** 💪

