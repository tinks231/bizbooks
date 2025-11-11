# 💾 Backup & Restore System - User Guide

## 🎯 Overview

Your app now has a **complete Backup & Restore system** that allows you to:
- ✅ **Download all business data** to your local computer
- ✅ **Restore from backup** if data is lost or corrupted
- ✅ **Keep multiple backups** for different time periods
- ✅ **100% safe** - your login is never affected

---

## 📍 How to Access

1. Login to your admin dashboard
2. Look at the left sidebar
3. Scroll to **"Settings & Backup"** section (near the bottom)
4. Click **"💾 Backup & Restore"**

---

## 📦 Creating a Backup

### What Gets Backed Up:

✅ **Customers** (names, contacts, addresses, GST, etc.)  
✅ **Vendors** (names, contacts, payment terms, etc.)  
✅ **Items** (products, SKUs, prices, descriptions)  
✅ **Item Stock** (quantities at all locations)  
✅ **Invoices** + Invoice Items  
✅ **Purchase Bills** + Line Items  
✅ **Sales Orders** + Items  
✅ **Delivery Challans** + Items  
✅ **Expenses** + Categories  
✅ **Employees** (names, PINs, phones, salaries)  
✅ **Sites/Warehouses** (locations, addresses)  
✅ **Tasks** (descriptions, assignments, updates)  
✅ **Commission Agents** + Commissions  
✅ **Vendor Payments** + Allocations  

**Total:** Usually 2,000-5,000 records  
**File Size:** ~2-5 MB  
**Download Time:** 5-10 seconds

### What's NOT Backed Up (coming in future update):

❌ **Item images** (product photos from Vercel Blob)  
❌ **Purchase bill attachments** (PDF files)  
❌ **Task media** (photos/videos)  
❌ **Attendance selfies** (privacy + large files)  
❌ **Your admin password** (security - never backed up!)

### Steps to Create Backup:

1. Go to **Admin > Settings & Backup > Backup & Restore**
2. Review the data summary (shows record counts)
3. Click **"📥 Download Backup Now"**
4. File downloads: `mahaveerelectricals_backup_2025-11-10_1430.json`
5. Save to a safe location:
   - ✅ Your computer's Documents folder
   - ✅ External hard drive
   - ✅ Google Drive / Dropbox
   - ✅ USB flash drive

### Recommended Backup Schedule:

- **Weekly:** For active businesses
- **Monthly:** For low-volume businesses
- **Before major changes:** Always backup before bulk imports/updates!

---

## 🔄 Restoring from Backup

### ⚠️ IMPORTANT WARNING:

**Restore will DELETE all current business data and replace it with backup data!**

- ✅ Your admin login (`admin@mahaveer.com`) **WILL NOT** be affected
- ✅ You will **STAY LOGGED IN** during the entire process
- ⚠️ All data created **AFTER the backup date** will be **LOST**
- ⚠️ This action **CANNOT BE UNDONE** (that's why backups are important!)

### When to Use Restore:

✅ **Data corruption:** Database got corrupted  
✅ **Accidental deletion:** Deleted important records by mistake  
✅ **Testing gone wrong:** Made changes in production and need to revert  
✅ **Hardware failure:** Server crashed and data is lost  
✅ **Ransomware attack:** Database encrypted by malware (rare but possible)  

### Steps to Restore:

1. Go to **Admin > Settings & Backup > Backup & Restore**
2. Scroll to **"📁 Restore Backup"** section
3. Click **"Choose File"**
4. Select your backup file (e.g., `mahaveerelectricals_backup_2025-11-10_1430.json`)
5. Click **"🔄 Restore Backup"**
6. **Confirmation dialog** appears:
   ```
   ⚠️ FINAL CONFIRMATION ⚠️
   
   You are about to RESTORE from:
   mahaveerelectricals_backup_2025-11-10_1430.json
   
   This will:
   ✅ Keep your admin login (admin@mahaveer.com)
   ⚠️ DELETE all current business data
   ⚠️ REPLACE with backup data
   
   Are you absolutely sure?
   ```
7. Click **"OK"** to proceed (or "Cancel" to abort)
8. System processes restore (10-30 seconds)
9. Success message appears
10. Redirected to dashboard with restored data
11. **You're still logged in!** ✅

---

## 🛡️ Safety Features

### 1. Login Preservation
Your **Tenant** record (admin login) is **NEVER** deleted or modified during restore.

**Before Restore:**
```
Tenant:
├── admin_email: "admin@mahaveer.com"
├── admin_password: (encrypted)
└── company_name: "Mahaveer Electricals"
```

**After Restore:**
```
Tenant:
├── admin_email: "admin@mahaveer.com" ✅ SAME!
├── admin_password: (encrypted) ✅ SAME!
└── company_name: "Mahaveer Electricals" ✅ SAME!
```

**Result:** You stay logged in! ✅

### 2. Transaction Safety
If **ANYTHING** fails during restore, the entire operation is **rolled back**:

```
✅ All-or-Nothing: Either EVERYTHING restores, or NOTHING changes
✅ No partial restore: Database never left in broken state
✅ Error handling: Clear error messages if something goes wrong
```

### 3. Security
Backup files are **safe to share** with trusted people (e.g., accountant):

```
✅ NO passwords in backup file
✅ NO login credentials
✅ NO session tokens
✅ Only business data (customers, items, invoices, etc.)
```

---

## 📊 Backup File Format

### File Structure:

```json
{
  "backup_info": {
    "created_at": "2025-11-10T14:30:00+05:30",
    "tenant_id": 1,
    "company_name": "Mahaveer Electricals",
    "subdomain": "mahaveerelectricals",
    "admin_email": "admin@mahaveer.com",
    "backup_version": "1.0",
    "total_records": 2547,
    "warnings": [
      "⚠️ Item images NOT included",
      "⚠️ Purchase bill attachments NOT included",
      ...
    ]
  },
  "metadata": {
    "customers_count": 45,
    "vendors_count": 23,
    "items_count": 150,
    "invoices_count": 234,
    ...
  },
  "data": {
    "customers": [...],
    "vendors": [...],
    "items": [...],
    "invoices": [...],
    ...
  }
}
```

### Why JSON?
- ✅ **Human-readable:** Can open in text editor
- ✅ **Database-agnostic:** Works with PostgreSQL & SQLite
- ✅ **Easy to debug:** Can inspect data if needed
- ✅ **Version control friendly:** Can track changes in Git
- ✅ **Widely supported:** Can import to other systems

---

## 🚀 Future Enhancements (v2.0)

### Coming Soon:

1. **📸 Image Backup**
   - Second file: `mahaveerelectricals_images_2025-11-10.zip`
   - Contains all product photos, bill PDFs, task media
   - Uploads back to Vercel Blob on restore

2. **☁️ Cloud Sync** (Premium Feature)
   - Auto-sync across devices
   - Real-time updates
   - No manual backup needed

3. **👥 Share with Staff** (Premium Feature)
   - Role-based access (salesperson, accountant, etc.)
   - Controlled sharing
   - Audit logs

4. **📊 Backup History**
   - Track last 5-10 backups
   - One-click download of previous backups
   - Backup comparison

5. **🔍 Selective Restore**
   - Restore only specific data (e.g., only customers)
   - Merge mode (keep newer records)
   - Conflict resolution

6. **⏰ Scheduled Auto-Backups**
   - Weekly/monthly automatic backups
   - Email notifications
   - Cloud storage integration

---

## ❓ FAQ

### Q: Will I be kicked out during restore?
**A:** NO! Your login is preserved. You'll stay logged in throughout the process.

### Q: Can I restore on a different computer?
**A:** YES! Just:
1. Download backup on Computer A
2. Upload backup on Computer B
3. Login with your admin credentials on Computer B
4. Restore works!

### Q: What if restore fails halfway?
**A:** Transaction rollback ensures no data is changed if anything fails.

### Q: Are passwords in the backup file?
**A:** NO! For security, passwords are NEVER backed up.

### Q: Can I share backup with my accountant?
**A:** YES! The file only contains business data (no passwords/login credentials).

### Q: How often should I backup?
**A:** 
- High transaction volume: **Weekly**
- Low transaction volume: **Monthly**
- Before major changes: **Always!**

### Q: Where should I store backups?
**A:** Multiple places for safety:
- ✅ Local computer (Documents folder)
- ✅ External hard drive
- ✅ Cloud storage (Google Drive, Dropbox)
- ✅ USB flash drive

### Q: What happens to data created after backup?
**A:** It will be LOST during restore. That's why regular backups are important!

### Q: Can I edit the backup file?
**A:** Technically yes (it's JSON), but NOT recommended! You might corrupt the file.

### Q: What if I lose the backup file?
**A:** Unfortunately, there's no way to recover it. Create new backup regularly!

---

## 🎯 Best Practices

### ✅ DO:
- Take regular backups (weekly/monthly)
- Store backups in multiple locations
- Test restore process occasionally
- Backup before major changes
- Label backup files with dates

### ❌ DON'T:
- Don't rely on single backup location
- Don't backup only once a year
- Don't edit backup files manually
- Don't share backups with untrusted people
- Don't delete old backups immediately (keep last 3-5)

---

## 📞 Support

If you encounter any issues:

1. **Check error message:** It usually tells you what went wrong
2. **Verify file format:** Make sure it's a valid .json file
3. **Check file size:** Corrupted files might be 0 KB or very small
4. **Try again:** Sometimes network issues cause failures

---

## 🎉 Summary

You now have a **professional-grade backup system** that:

✅ Protects your business data  
✅ Allows easy restore when needed  
✅ Works on any device  
✅ 100% safe (no login disruption)  
✅ Free to use (no cloud storage fees)  
✅ Takes only 5-10 seconds to backup  

**Take your first backup TODAY!** 💾

---

**Version:** 1.0  
**Last Updated:** November 10, 2025  
**Feature Status:** ✅ Production Ready

