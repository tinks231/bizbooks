# 🔐 BizBooks Backup System

Automated daily backup and restore system for BizBooks PostgreSQL database.

---

## ✨ Features

- ✅ **Automatic daily backups** at 11:00 AM IST
- ✅ **Compression** (saves 70-80% disk space)
- ✅ **30-day retention** (auto-cleanup old backups)
- ✅ **One-click restore** from any backup
- ✅ **Detailed logging** of all operations
- ✅ **Email alerts** (optional) on failures
- ✅ **Safety backup** before restore
- ✅ **Validation** of backup files

---

## 📁 Files

```
backup_system/
├── backup_manager.py         # Main backup script
├── restore_manager.py         # Restore script
├── schedule_backup.sh         # Scheduler for macOS
├── config.env.example         # Configuration template
├── SETUP_GUIDE.md             # Detailed setup instructions
└── README.md                  # This file
```

---

## 🚀 Quick Start

### **1. Install Prerequisites**

```bash
# Install PostgreSQL client (for pg_dump/psql)
brew install postgresql

# Verify
pg_dump --version
```

---

### **2. Configure**

```bash
# Copy config template
cp config.env.example config.env

# Edit and add your DATABASE_URL
nano config.env
```

**Required setting:**
```bash
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@db.xxxxx.supabase.co:5432/postgres
```

---

### **3. Test Backup**

```bash
# Run backup once
python3 backup_manager.py
```

**Expected output:**
```
✅ Backup created: bizbooks_backup_2024-11-02_11-00-00.sql (2.45 MB)
✅ Backup compressed: 0.52 MB (saved 78.8%)
✅ Backup process completed successfully!
```

---

### **4. Schedule Daily Backups**

```bash
# Run scheduler
chmod +x schedule_backup.sh
./schedule_backup.sh
```

**Result:**
```
✅ LaunchAgent loaded successfully!
🎉 Backup scheduled successfully!
   ⏰ Daily backup at: 11:00 AM IST
   📁 Backup location: /Users/rishjain/Downloads/bizbooks/backup
```

---

## 🔄 Restore Database

### **List Backups:**

```bash
python3 restore_manager.py --list
```

---

### **Restore Latest:**

```bash
python3 restore_manager.py --latest
```

---

### **Restore Specific:**

```bash
python3 restore_manager.py --restore bizbooks_backup_2024-11-01_11-00-00.sql.gz
```

---

## 📊 Monitor

### **View Logs:**

```bash
# Real-time
tail -f /Users/rishjain/Downloads/bizbooks/backup/backup.log

# Last 50 lines
tail -50 /Users/rishjain/Downloads/bizbooks/backup/backup.log
```

---

### **Check Backup Size:**

```bash
du -sh /Users/rishjain/Downloads/bizbooks/backup/
```

---

### **Count Backups:**

```bash
ls -1 /Users/rishjain/Downloads/bizbooks/backup/bizbooks_backup_*.sql.gz | wc -l
```

---

## 📋 Backup Schedule

**Default:** Daily at 11:00 AM IST

**To change time:** Edit `~/Library/LaunchAgents/com.bizbooks.backup.plist`

```xml
<key>Hour</key>
<integer>11</integer>    <!-- Change this -->
<key>Minute</key>
<integer>0</integer>     <!-- And this -->
```

Then reload:
```bash
launchctl unload ~/Library/LaunchAgents/com.bizbooks.backup.plist
launchctl load ~/Library/LaunchAgents/com.bizbooks.backup.plist
```

---

## 🛠️ Troubleshooting

### **Problem: pg_dump not found**

```bash
brew install postgresql
which pg_dump
```

---

### **Problem: Permission denied**

```bash
chmod +x schedule_backup.sh
chmod +x backup_manager.py
chmod +x restore_manager.py
```

---

### **Problem: DATABASE_URL not found**

```bash
# Check config
cat config.env

# If missing, create it
cp config.env.example config.env
nano config.env
```

---

### **Problem: Connection error**

1. Verify DATABASE_URL is correct
2. Test connection:
   ```bash
   psql "your-database-url-here"
   ```
3. Check if Supabase project is paused

---

## 📞 Support

- **Setup Guide:** See `SETUP_GUIDE.md` for detailed instructions
- **Docker/K8s:** See `DOCKER_KUBERNETES_GUIDE.md` for containerization
- **Logs:** Check `/Users/rishjain/Downloads/bizbooks/backup/backup.log`

---

## ✅ Success Checklist

- [ ] PostgreSQL client installed
- [ ] config.env created with DATABASE_URL
- [ ] Manual backup successful
- [ ] LaunchAgent scheduled
- [ ] At least 1 backup file exists
- [ ] Logs show success

**If all checked → You're protected! 🎉**

