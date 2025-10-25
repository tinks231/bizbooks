# 🎯 BizBooks - Quick Reference Guide

**Your business management system is LIVE at: `bizbooks.co.in`**

---

## 📱 **URLs (Use These)**

### For Employees (Mark Attendance):
```
https://attendance.bizbooks.co.in/
```
QR Code: `WORKING_employee_attendance_qr.png`

### For Admin (Manage Everything):
```
https://attendance.bizbooks.co.in/admin/login
```
**Login:** admin / admin123  
QR Code: `WORKING_admin_login_qr.png`

---

## 🚀 **Managing Your System**

### Start BizBooks:
```bash
cd /Users/rishjain/Downloads/attendence_app
./manage_bizbooks.sh start
```

### Stop BizBooks:
```bash
./manage_bizbooks.sh stop
```

### Check Status:
```bash
./manage_bizbooks.sh status
```

### View Logs:
```bash
./manage_bizbooks.sh logs
```

---

## ⚙️ **Configuration**

### Location Settings:
Edit: `modular_app/config/settings.ini`

```ini
[LOCATION]
office_lat = YOUR_LATITUDE
office_lon = YOUR_LONGITUDE
allowed_radius_meters = 100
gps_required = False
```

### Admin Password:
Edit: `modular_app/config/settings.ini`

```ini
[ADMIN]
username = admin
password = YOUR_NEW_PASSWORD
```

---

## 🔧 **If Something Breaks**

1. **Restart everything:**
   ```bash
   ./manage_bizbooks.sh restart
   ```

2. **Check what's running:**
   ```bash
   ./manage_bizbooks.sh status
   ```

3. **View error logs:**
   ```bash
   ./manage_bizbooks.sh logs
   ```

---

## 📦 **What's Included**

- ✅ Attendance (Check-in/Check-out with selfie)
- ✅ Inventory Management
- ✅ Multi-Site Support
- ✅ Admin Dashboard
- ✅ Employee Management
- ✅ Stock Tracking
- ✅ Manual Entry (for forgot to mark)

---

## 🌐 **For Remote Testing**

Your friend anywhere can test:
```
https://attendance.bizbooks.co.in/
```

GPS is optional - they can mark attendance from anywhere during testing!

---

## 📞 **Quick Commands Card**

```
╔═══════════════════════════════════════╗
║       BIZBOOKS QUICK COMMANDS         ║
╠═══════════════════════════════════════╣
║                                       ║
║  START:  ./manage_bizbooks.sh start   ║
║  STOP:   ./manage_bizbooks.sh stop    ║
║  STATUS: ./manage_bizbooks.sh status  ║
║  LOGS:   ./manage_bizbooks.sh logs    ║
║                                       ║
║  Employee URL:                        ║
║  https://attendance.bizbooks.co.in/   ║
║                                       ║
║  Admin URL:                           ║
║  https://attendance.bizbooks.co.in    ║
║        /admin/login                   ║
║                                       ║
╚═══════════════════════════════════════╝
```

---

**That's it! Keep this file handy.** 📌

