# 📱 Attendance App - Complete Guide

Simple PIN + Selfie attendance system for small shops. Works on WiFi, no monthly cost!

**💻 Compatible with:** Windows, Mac, Linux  
**📱 Works on:** iPhone, Android, any phone with browser  
**📡 Network:** WiFi only (no internet needed!)  

---

## 🏢 **NEW! Enterprise Auto-Start Setup**

**Want zero daily maintenance?** Set up once, works forever!

### **🎯 Enterprise Features:**
- ✅ **Auto-starts on PC boot** (no manual startup!)
- ✅ **Fixed URL that never changes** (share once with employees)
- ✅ **Windows Service** (runs in background)
- ✅ **Zero daily intervention** (works like a real app!)
- ✅ **Free** ($0 monthly cost)

### **📋 One-Time Setup (30 minutes):**
```cmd
# Run as Administrator (Windows only):
setup_enterprise_autostart.bat
```

**That's it!** The app will now:
- Start automatically on PC boot
- Give you a fixed URL (e.g., `https://myshop-attendance.trycloudflare.com`)
- Run in background forever
- Require ZERO daily maintenance

**For details:** See `ENTERPRISE_AUTOSTART_GUIDE.md`

---

## 🚀 Quick Start (First Time - Manual Setup)

### ⚠️ **WINDOWS USERS: Install Python First!**

**Don't have Python?** 
```cmd
check_python.bat    ← Run this to check and get help!
```

**Or see:** `INSTALL_PYTHON_WINDOWS.md` for detailed Python installation guide

---

### After Python is Installed:

**Note:** Commands shown are for Mac/Linux. Windows users: Use `python` instead of `python3`.

```bash
# Step 0: Install dependencies (Windows - choose one)
install_dependencies.bat       # Windows: One-click install
# OR manually:
pip install flask flask-sqlalchemy pillow geopy pyopenssl

# Step 1: Configure your shop location
python3 setup_wizard.py        # Mac/Linux
python setup_wizard.py         # Windows

# Step 2: Generate QR code
python3 generate_qr.py         # Mac/Linux
python generate_qr.py          # Windows

# Step 3: Start the app
./start_app.sh                 # Mac/Linux
start_app.bat                  # Windows (double-click!)

# Done! Print the QR code and stick it on wall.
```

**Your URLs:**
- Employee: `https://YOUR_IP:5001`
- Admin: `https://YOUR_IP:5001/admin/login`

**Need Remote Access? (Optional - for testing from mobile data):**

### Install Cloudflared (Choose your OS):

**Windows:**
```cmd
# Download installer from:
https://github.com/cloudflare/cloudflared/releases/latest

# Download: cloudflared-windows-amd64.exe
# Rename to: cloudflared.exe
# Move to: C:\Windows\System32\

# Or install via command (PowerShell as Admin):
winget install --id Cloudflare.cloudflared
```

**Mac:**
```bash
brew install cloudflare/cloudflare/cloudflared
```

**Linux:**
```bash
# Debian/Ubuntu
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb

# Or use package manager
sudo apt install cloudflared
```

### Start Tunnel:
```bash
# Open new terminal/command prompt
cloudflared tunnel --url https://127.0.0.1:5001 --no-tls-verify

# You'll get a public URL like:
# https://random-words-here.trycloudflare.com
# Share this URL for remote access (changes every restart)
```

---

## 👤 For Employees (Daily Use)

### How to Mark Attendance:

1. **Connect to shop WiFi**
2. **Scan QR code** (or visit URL)
3. **Enter your 4-digit PIN**
4. **Take selfie** (camera opens automatically)
5. **Click Check In** (morning) or **Check Out** (evening)
6. **Done!** ✅

**Important:**
- ✅ Must be on **same WiFi** as computer
- ✅ Allow **camera** and **location** permission
- ✅ One person = One PIN (keep it secret!)

---

## 🔐 For Admin

### Login:
- URL: `https://YOUR_IP:5001/admin/login`
- Default: `admin` / `admin123` (change in `config.ini`)

### Dashboard Features:

| Feature | What It Does |
|---------|-------------|
| **View Records** | See all check-ins/outs grouped by employee |
| **Delete Record** | Fix mistakes (clicked wrong button) |
| **Export CSV** | Download data for Excel (monthly reports) |
| **Clear All** | Delete all test data (for distribution) |
| **Manage Employees** | Add/remove/deactivate employees |

### Common Tasks:

**Fix Wrong Button Click:**
1. Dashboard → Find wrong record
2. Click 🗑️ button
3. Ask employee to mark again

**Monthly Report:**
1. Click "Export CSV"
2. Open in Excel
3. Filter by employee + month
4. Count days/hours

**Prepare for Another Shopkeeper:**
```bash
python3 prepare_for_distribution.py
# Deletes all test data, keeps code intact
```

---

## 🔧 Configuration

### Change Office Location:
```bash
python3 setup_wizard.py
```

### Change Admin Password:
Edit `config.ini`:
```ini
[ADMIN]
USERNAME = your_username
PASSWORD = your_strong_password
```

### Change Allowed Radius:
Edit `config.ini`:
```ini
[OFFICE_LOCATION]
ALLOWED_RADIUS = 150  # meters
```

---

## 📱 Mobile Setup

### iPhone/iPad:
1. Safari → Visit URL
2. "Not Secure" warning → **Advanced** → **Proceed**
3. Settings → Safari → Location: **Allow**
4. Settings → Safari → Camera: **Allow**

### Android:
1. Chrome → Visit URL
2. "Not Secure" warning → **Advanced** → **Proceed to site**
3. Chrome → Settings → Site Settings → Location: **Allow**
4. Chrome → Settings → Site Settings → Camera: **Allow**

**Firewall Issue (Mac):**
If Android can't connect:
- System Preferences → Firewall → Turn OFF
- Or: Firewall → Options → Allow Python

---

## 📄 Important Files

```
attendenceApp.py          # Main app (don't edit unless you know Python)
config.ini                # Settings (location, password, radius)

Setup Scripts:
  setup_wizard.py         # First-time configuration
  generate_qr.py          # Create QR code
  prepare_for_distribution.py  # Clean for sharing

Mac/Linux Scripts:
  start_app.sh            # Start app (one-click)
  check_ip.sh             # Check if IP changed

Windows Scripts:
  check_python.bat        # Check Python installation ⭐ START HERE
  install_dependencies.bat # Install required packages ⭐ NEW
  start_app.bat           # Start app (one-click, auto-detects IP)
  check_ip.bat            # Check IP address and detect changes
  start_tunnel.bat        # Start Cloudflare tunnel for remote access

🏢 Enterprise Auto-Start (Windows): ⭐ NEW - ZERO DAILY MAINTENANCE!
  setup_enterprise_autostart.bat # One-time setup (30 min)
  manage_services.bat     # Start/stop/check services
  uninstall_services.bat  # Remove services if needed

Documentation:
  README.md               # This file
  ENTERPRISE_AUTOSTART_GUIDE.md # Enterprise setup guide ⭐ NEW
  ENTERPRISE_QUICK_REFERENCE.txt # Quick reference for client ⭐ NEW
  INSTALL_PYTHON_WINDOWS.md # Python installation guide
  DEPLOYMENT_CHECKLIST.md # Deployment steps
  QUICK_REFERENCE_PRINT_THIS.txt # Client reference card

Folders:
  instance/attendance.db  # Database (all records stored here)
  selfies/                # Attendance photos
  employee_documents/     # Employee ID documents (Aadhar, etc.)
```

---

## 💻 Windows Users - Quick Reference

### ⚠️ FIRST: Check Python Installation

```cmd
# Run this FIRST - it checks everything!
check_python.bat

# This script will:
# - Check if Python is installed
# - Show installation instructions if not
# - Check required packages
# - Offer to install missing packages
```

### If Python Not Installed:

**Option 1: Quick Check Script**
```cmd
check_python.bat    ← Shows installation steps
```

**Option 2: Read Detailed Guide**
```
Open: INSTALL_PYTHON_WINDOWS.md
```

**Option 3: Direct Install**
1. Go to: https://www.python.org/downloads/
2. Download Python
3. ⚠️ **IMPORTANT:** Check "Add Python to PATH"
4. Install

### After Python is Installed:

```cmd
# Install packages (one-click)
install_dependencies.bat

# Configure app
python setup_wizard.py

# Start app
start_app.bat
```

### Python Commands:
```cmd
# Use 'python' instead of 'python3'
python setup_wizard.py
python generate_qr.py
python attendenceApp.py
python prepare_for_distribution.py
```

### Start App on Windows:
```cmd
# Option 1: Double-click start_app.bat (Easiest!)
# Just double-click the start_app.bat file

# Option 2: Command Prompt
cd C:\path\to\attendence_app
start_app.bat

# Option 3: Direct Python
python attendenceApp.py
```

**start_app.bat does everything automatically:**
- ✅ Checks Python is installed
- ✅ Generates SSL certificates if missing
- ✅ **Auto-detects your WiFi IP address**
- ✅ Shows all URLs (phone, computer, admin)
- ✅ Saves IP to check for changes
- ✅ Starts the Flask app

### Check Your IP Address (Windows):
```cmd
# Double-click: check_ip.bat
# Or run from Command Prompt:
check_ip.bat
```

**What it does:**
- Shows your current WiFi IP address
- Detects if IP changed since last run
- Shows employee and admin URLs
- Reminds you to regenerate QR code if IP changed

### Start Cloudflare Tunnel (Windows):
```cmd
# First, make sure app is running (start_app.bat)
# Then in a NEW Command Prompt window:
start_tunnel.bat
```

**What it does:**
- Checks if cloudflared is installed
- Shows installation instructions if not installed
- Creates public URL for remote access
- Displays the URL to share with employees

### Firewall (Important!):
When you first run the app, Windows will ask:
- "Allow Python to access network?"
- **Click "Allow"** (both Private and Public networks)

### Find Your IP (Windows):
```cmd
# Option 1: Use helper script (recommended)
check_ip.bat

# Option 2: Manual check
ipconfig
# Look for "IPv4 Address" under your WiFi adapter
# Example: 192.168.1.100
```

---

## 🎯 Daily Routine

**Morning:**
```
1. Turn on computer (Mac/Windows/Linux)
2. Start app:
   - Mac/Linux: ./start_app.sh
   - Windows: Double-click start_app.bat
3. Employees scan QR and check in
```

**Evening:**
```
1. Employees check out
2. Admin checks dashboard
3. Close computer (app stops automatically)
```

**Weekly:**
```
1. Export CSV (backup)
2. Review attendance
```

---

## 🐛 Troubleshooting

### App Won't Start (Port in use):
```bash
# Find and kill process
lsof -i :5001
kill -9 <PID>

# Then start again
./start_app.sh
```

### IP Address Changed:
```bash
# Check new IP
./check_ip.sh

# Regenerate QR code
python3 generate_qr.py

# Print and replace old QR
```

### Database Corrupted:
```bash
# Backup first (if possible)
cp instance/attendance.db instance/attendance_backup.db

# Delete and restart (creates fresh database)
rm instance/attendance.db
./start_app.sh
```

### GPS Not Working:
- **Normal:** GPS weak indoors, WiFi still verifies location
- **Fix:** Go near window, or enable high-accuracy mode in phone

### Photos Not Loading:
```bash
# Check permissions
ls -la selfies/
chmod 755 selfies/
```

---

## 📦 Share with Another Shopkeeper

```bash
# Step 1: Clean your test data
python3 prepare_for_distribution.py

# Step 2: Zip the folder
cd ..
zip -r attendance_app.zip attendence_app/

# Step 3: Share zip file
# Send via email/USB/WhatsApp

# Step 4: They run
python3 setup_wizard.py  # Configure their location
python3 generate_qr.py   # Generate their QR
./start_app.sh          # Start
```

---

## ❓ FAQ

**Q: Do employees need to install anything?**
A: No! Just browser + WiFi.

**Q: Does it work without internet?**
A: Yes! Only needs WiFi (local network).

**Q: What if Mac restarts?**
A: Run `./start_app.sh` again. IP usually stays same.

**Q: Can I use mobile hotspot?**
A: Yes, but Mac and phones must connect to same hotspot.

**Q: How to backup data?**
A: Admin Dashboard → Export CSV (weekly)

**Q: What if I forget admin password?**
A: Check `config.ini` file.

**Q: Can employees mark from home?**
A: No! Must be on shop WiFi. That's the security!
   (Unless you use Cloudflare tunnel for special cases)

**Q: What is Cloudflare tunnel? Do I need it?**
A: Optional! Only for these cases:
   - Testing from mobile data (not WiFi)
   - No WiFi at shop (use mobile hotspot)
   - Employee works remotely sometimes
   
   **For normal WiFi usage: NOT NEEDED!**
   
   **How to install:**
   
   *Windows:*
   ```cmd
   # Method 1: Download directly
   1. Visit: https://github.com/cloudflare/cloudflared/releases/latest
   2. Download: cloudflared-windows-amd64.exe
   3. Rename to: cloudflared.exe
   4. Move to: C:\Windows\System32\
   
   # Method 2: PowerShell (as Admin)
   winget install --id Cloudflare.cloudflared
   ```
   
   *Mac:*
   ```bash
   brew install cloudflare/cloudflare/cloudflared
   ```
   
   *Linux:*
   ```bash
   wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
   sudo dpkg -i cloudflared-linux-amd64.deb
   ```
   
   **How to use:**
   ```bash
   # Terminal/CMD 1: Start app
   ./start_app.sh    # Mac/Linux
   start_app.bat     # Windows (if you create batch file)
   
   # Terminal/CMD 2: Start tunnel
   cloudflared tunnel --url https://127.0.0.1:5001 --no-tls-verify
   
   # Copy the URL shown (e.g., https://abc-def.trycloudflare.com)
   # Share with employees for remote access
   ```
   
   **Important:**
   - URL changes every time you restart tunnel
   - Free tier has no uptime guarantee
   - For production: Use same WiFi (more stable)
   - Windows users: Use Command Prompt or PowerShell

**Q: How to add new employee?**
A: Admin → Manage Employees → Add (enter name + PIN)

**Q: Monthly cost?**
A: ₹0! No cloud, no subscription. One-time setup only.

---

## 🎓 Pro Tips

1. **Change admin password** immediately (config.ini)
2. **Print QR code** in color and laminate it
3. **Weekly CSV export** for backup
4. **Check dashboard daily** to catch issues early
5. **Train employees** on first day
6. **Test from iPhone AND Android** before going live
7. **Keep Mac plugged in** during shop hours

---

## 🔒 Security

✅ **PIN Required:** Each employee has unique 4-digit PIN
✅ **Selfie Required:** Photo verification for every attendance
✅ **WiFi Required:** Must be at shop (not from home)
✅ **GPS Tracking:** Distance from office recorded (optional)
✅ **HTTPS:** Secure connection with SSL
✅ **Admin Protected:** Password-protected dashboard

---

## 🎉 Features Summary

| Feature | Status |
|---------|--------|
| PIN Authentication | ✅ |
| Photo Verification | ✅ |
| GPS Location | ✅ |
| Check In/Out | ✅ |
| Duration Calculation | ✅ |
| Admin Dashboard | ✅ |
| Delete Records | ✅ |
| Export CSV | ✅ |
| Employee Management | ✅ |
| QR Code Generator | ✅ |
| Mobile Friendly | ✅ |
| WiFi Only (Secure) | ✅ |
| No Monthly Cost | ✅ |

---

## 📞 Need Help?

**Quick Commands:**
```bash
./start_app.sh                    # Start app
./check_ip.sh                     # Check IP address
python3 generate_qr.py            # Generate QR code
python3 setup_wizard.py           # Change settings
python3 prepare_for_distribution.py  # Clean for sharing
```

**Check Status:**
```bash
lsof -i :5001              # Is app running?
ifconfig | grep inet        # What's my IP?
ls instance/attendance.db   # Database exists?
ls selfies/                 # Photos saved?
```

---

**🎊 That's it! Simple, secure, and zero monthly cost!** 🎊

Made with ❤️ for small business owners who want biometric-level attendance without biometric prices!
