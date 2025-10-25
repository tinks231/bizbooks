# 🐍 Installing Python on Windows - Step by Step

## ✅ Quick Check: Is Python Already Installed?

**Open Command Prompt and type:**
```cmd
python --version
```

**Result:**
- ✅ Shows "Python 3.x.x" → Python is installed! Skip to [Dependencies](#install-dependencies)
- ❌ Shows error or "not recognized" → Follow installation steps below

---

## 📥 Method 1: Official Python Installer (Recommended)

### Step 1: Download Python

1. **Open browser** and go to:
   ```
   https://www.python.org/downloads/
   ```

2. **Click** the big yellow button: **"Download Python 3.x.x"**
   - Choose latest stable version (3.9 or higher)
   - File will be named like: `python-3.12.0-amd64.exe`

3. **Save** the installer to Desktop or Downloads

### Step 2: Run Installer

1. **Double-click** the downloaded `.exe` file

2. **⚠️ IMPORTANT - First Screen:**
   ```
   ☑️ MUST CHECK: "Add Python to PATH"
   ☐ Install launcher for all users (optional)
   ```
   **↑ THIS IS CRITICAL! ↑**
   Without this, Python won't work from Command Prompt!

3. **Click** "Install Now"
   - Default location: `C:\Users\YourName\AppData\Local\Programs\Python\`
   - This installs Python + pip (package manager)

4. **Wait** 2-3 minutes for installation

5. **Success screen** appears:
   ```
   Setup was successful
   ```

6. **Click** "Close"

### Step 3: Verify Installation

1. **Close** any open Command Prompt windows

2. **Open NEW Command Prompt:**
   - Press `Windows Key + R`
   - Type: `cmd`
   - Press Enter

3. **Test Python:**
   ```cmd
   python --version
   ```
   Should show: `Python 3.12.0` (or your version)

4. **Test pip:**
   ```cmd
   pip --version
   ```
   Should show: `pip 23.x.x from...`

✅ **Python is now installed!**

---

## 📥 Method 2: Microsoft Store (Easiest for Windows 10/11)

### Step 1: Open Microsoft Store

1. Click **Start Menu**
2. Search for: **"Microsoft Store"**
3. Click to open

### Step 2: Search and Install

1. In Store, search: **"Python"**
2. Look for: **"Python 3.12"** (or latest)
   - Published by: Python Software Foundation
3. Click **"Get"** or **"Install"**
4. Wait for installation (2-3 minutes)

### Step 3: Verify

1. Open Command Prompt
2. Type: `python --version`
3. Should show Python version

✅ **Python installed automatically with PATH set!**

---

## 📥 Method 3: Winget (Windows Package Manager)

**For Windows 10/11 with Winget:**

1. **Open PowerShell as Administrator:**
   - Right-click Start Menu
   - Click "Windows PowerShell (Admin)"

2. **Run command:**
   ```powershell
   winget install Python.Python.3.12
   ```

3. **Wait** for installation

4. **Verify:**
   ```cmd
   python --version
   ```

---

## 🔧 Install Dependencies

**After Python is installed:**

```cmd
pip install flask flask-sqlalchemy pillow geopy pyopenssl
```

**This installs:**
- `flask` - Web framework
- `flask-sqlalchemy` - Database
- `pillow` - Image handling
- `geopy` - GPS calculations
- `pyopenssl` - HTTPS certificates

**Installation time:** 1-2 minutes

---

## ❌ Troubleshooting

### Problem 1: "Python is not recognized"

**Cause:** PATH not set during installation

**Solution A - Reinstall Python:**
1. Uninstall Python (Settings → Apps)
2. Download installer again
3. ⚠️ **CHECK "Add Python to PATH"** this time!
4. Install

**Solution B - Add PATH Manually:**
1. Find Python installation folder:
   - Usually: `C:\Users\YourName\AppData\Local\Programs\Python\Python312\`
2. Copy the full path
3. Add to PATH:
   - Right-click "This PC" → Properties
   - Click "Advanced system settings"
   - Click "Environment Variables"
   - Under "System variables", find "Path"
   - Click "Edit"
   - Click "New"
   - Paste Python path
   - Click OK on all windows
4. Restart Command Prompt
5. Test: `python --version`

### Problem 2: "pip is not recognized"

**Solution:**
```cmd
python -m pip --version
```

Use `python -m pip install` instead of just `pip install`

### Problem 3: "Permission denied"

**Solution:**
Run Command Prompt as Administrator:
- Right-click Command Prompt
- Click "Run as administrator"
- Retry installation

### Problem 4: Old Python version

**Check version:**
```cmd
python --version
```

**If < 3.7:**
1. Uninstall old Python
2. Install latest Python (3.9+)

### Problem 5: SSL certificate error during pip install

**Solution:**
```cmd
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org flask flask-sqlalchemy pillow geopy pyopenssl
```

---

## 📋 Complete Setup Commands

**After Python is installed:**

```cmd
# Navigate to app folder
cd C:\attendence_app

# Install dependencies
pip install flask flask-sqlalchemy pillow geopy pyopenssl

# Configure app
python setup_wizard.py

# Start app
start_app.bat
```

---

## 🎯 Quick Reference Card

**For Non-Technical Users:**

```
┌─────────────────────────────────────────┐
│  INSTALLING PYTHON - SIMPLE STEPS       │
├─────────────────────────────────────────┤
│                                         │
│  1. Google: "download python"           │
│                                         │
│  2. Click: python.org link              │
│                                         │
│  3. Click: Download Python button       │
│                                         │
│  4. Run downloaded file                 │
│                                         │
│  5. ☑️ CHECK: "Add Python to PATH"     │
│                                         │
│  6. Click: Install Now                  │
│                                         │
│  7. Wait 2-3 minutes                    │
│                                         │
│  8. Done! ✅                            │
│                                         │
└─────────────────────────────────────────┘
```

---

## 🆘 Need Help?

**If installation fails:**

1. **Take screenshot** of error message
2. **Check Windows version:**
   - Press `Windows + R`
   - Type: `winver`
   - Press Enter
   - Note the version

3. **Common fixes:**
   - Restart computer
   - Run installer as Administrator
   - Disable antivirus temporarily
   - Check internet connection

4. **Alternative:**
   - Use Microsoft Store method (easiest)
   - No PATH issues
   - Automatic updates

---

## ✅ Verification Checklist

After installation, verify:

```cmd
# Check Python
python --version
✅ Should show: Python 3.x.x

# Check pip
pip --version
✅ Should show: pip version

# Check can install packages
pip install --upgrade pip
✅ Should complete without errors

# List installed packages
pip list
✅ Should show list

# Test Python works
python -c "print('Hello')"
✅ Should print: Hello
```

**All checks pass? Python is ready!** 🎉

---

## 🎓 For Technical Support Person

**Remote installation over phone:**

1. **Ask user to share screen** (TeamViewer/AnyDesk)
2. **Guide step-by-step** through installer
3. **Emphasize** the "Add to PATH" checkbox
4. **Verify** with `python --version` command
5. **Install dependencies** via pip
6. **Test** attendance app

**Estimated time:** 15-20 minutes for complete setup

---

## 📱 One-Line Installation (PowerShell Admin)

**For advanced users:**

```powershell
# Install Python
winget install Python.Python.3.12

# Install dependencies
pip install flask flask-sqlalchemy pillow geopy pyopenssl

# Done!
```

---

## 🔄 Updating Python

**To update to latest version:**

1. Download latest installer from python.org
2. Run installer
3. Choose "Upgrade Now"
4. Existing packages preserved

**Or via winget:**
```powershell
winget upgrade Python.Python.3.12
```

---

## 📝 Summary

**What you need:**
- ✅ Python 3.9 or higher
- ✅ pip (comes with Python)
- ✅ Internet connection (for downloading packages)

**Installation time:**
- Python: 2-3 minutes
- Dependencies: 1-2 minutes
- **Total: 5 minutes**

**Difficulty:**
- ⭐ Easy (if PATH checkbox is checked)
- ⭐⭐ Medium (if PATH not set, need manual fix)

---

**👉 After Python is installed, return to main README.md for app setup!**

