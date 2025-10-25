# 🧪 Local Multi-Tenant Testing Guide

## 📋 **Overview**

We'll test the multi-tenant system locally using **subdomain emulation**. You have two options:

---

## 🎯 **Option 1: Using lvh.me (Easiest - No Configuration!)**

`lvh.me` is a free service that automatically resolves all subdomains to `127.0.0.1` (localhost).

### **How it works:**
- `lvh.me:5001` → `127.0.0.1:5001`
- `client1.lvh.me:5001` → `127.0.0.1:5001` (with subdomain "client1")
- `client2.lvh.me:5001` → `127.0.0.1:5001` (with subdomain "client2")

### **No setup needed!** Just use these URLs directly in your browser.

---

## 🎯 **Option 2: Modify /etc/hosts File (Mac/Linux)**

Edit your hosts file to map custom subdomains to localhost.

```bash
sudo nano /etc/hosts

# Add these lines:
127.0.0.1 client1.local
127.0.0.1 client2.local
127.0.0.1 client3.local

# Save and exit (Ctrl+X, Y, Enter)
```

Then access:
- `http://client1.local:5001`
- `http://client2.local:5001`

---

## 🚀 **Testing Steps**

### **1. Initialize Database**
```bash
cd /Users/rishjain/Downloads/attendence_app/modular_app
python init_db.py
```

This will:
- Drop old tables
- Create new tables with Tenant support
- Clear all old data

### **2. Start the Application**
```bash
cd /Users/rishjain/Downloads/attendence_app/modular_app
python app.py
```

You should see:
```
🚀 Modular Business Management System
📍 Host: 0.0.0.0:5001
🗄️  Database: sqlite:///instance/app.db
👤 Default Admin: admin / admin123
```

### **3. Register First Tenant (Client 1)**

**Using lvh.me:**
1. Open browser: `http://lvh.me:5001/register/`

**Using /etc/hosts:**
1. Open browser: `http://localhost:5001/register/`

**Register as:**
- **Company Name:** Vijay Services
- **Subdomain:** `vijayservice`
- **Your Name:** Vijay Kumar
- **Email:** vijay@vijayservice.com
- **Phone:** +91 9876543210
- **Password:** test123
- **Confirm Password:** test123

Click **"Create My Account"**

You should be redirected to: `http://vijayservice.lvh.me:5001/admin/login`

### **4. Login as Client 1 Admin**

**URL:** `http://vijayservice.lvh.me:5001/admin/login`

**Credentials:**
- **Email:** vijay@vijayservice.com
- **Password:** test123

You should see the admin dashboard with "Vijay Services" displayed.

### **5. Generate QR Code**

1. Click **"📱 Generate QR Code"** button
2. You should see a QR code for `https://vijayservice.bizbooks.co.in/attendance`
3. Save/screenshot this page

### **6. Add Employees**

1. Go to **"Employees"** tab
2. Add Employee:
   - **Name:** Rahul Sharma
   - **PIN:** 1234
   - **Phone:** +91 9999999999
   - **Site:** Main Office
3. Click **"Add Employee"**

### **7. Test Attendance (From Phone)**

**Option A: Using Phone on Same WiFi**

1. Connect your phone to the same WiFi as your Mac
2. Find your Mac's local IP:
   ```bash
   ifconfig | grep "inet " | grep -v 127.0.0.1
   ```
   Example: `192.168.29.38`

3. On your phone browser, visit:
   `http://192.168.29.38:5001/attendance`
   
4. Enter PIN: `1234`
5. Take selfie
6. Click **"Check In"**

**Option B: Testing in Browser (Simulated)**

1. Open: `http://vijayservice.lvh.me:5001/attendance`
2. Enter PIN: `1234`
3. Upload a photo
4. Click **"Check In"**

### **8. Verify Attendance in Admin**

1. Go to: `http://vijayservice.lvh.me:5001/admin/attendance`
2. You should see Rahul's check-in record with photo

### **9. Register Second Tenant (Client 2)**

**IMPORTANT:** Open a **new incognito/private window** or **clear cookies**!

1. Go to: `http://lvh.me:5001/register/`
2. Register as:
   - **Company Name:** Raj Construction
   - **Subdomain:** `rajconstruction`
   - **Your Name:** Rajesh Patel
   - **Email:** rajesh@rajconstruction.com
   - **Password:** test123

### **10. Test Tenant Isolation**

**Login as Client 2:**
- URL: `http://rajconstruction.lvh.me:5001/admin/login`
- Email: rajesh@rajconstruction.com
- Password: test123

**Verify:**
- ✅ Dashboard shows "Raj Construction"
- ✅ Employee count = 0 (Rahul from Client 1 should NOT be visible)
- ✅ Attendance records = 0 (Client 1's data should NOT be visible)

**Try to hack (should fail):**
- While logged in as Client 2, try to access:
  `http://vijayservice.lvh.me:5001/admin/dashboard`
- **Expected:** Should show "Session mismatch" and redirect to login

### **11. Add Employee to Client 2**

1. Still as Client 2 (Raj Construction)
2. Add Employee:
   - **Name:** Suresh Yadav
   - **PIN:** 1234 (same as Client 1! This should work)
3. Verify employee added successfully

**This proves PIN uniqueness is per-tenant!**

### **12. Register Third Tenant (Client 3)**

Repeat the same process for:
- **Company Name:** Sharma Traders
- **Subdomain:** `sharmatraders`
- **Email:** sharma@sharmatraders.com

---

## 🧪 **Test Checklist**

### ✅ **Registration System**
- [ ] Registration form loads
- [ ] Real-time subdomain check works
- [ ] Validation shows errors
- [ ] Successful registration creates tenant
- [ ] Redirects to tenant subdomain

### ✅ **Admin Authentication**
- [ ] Login page shows company name
- [ ] Email + password works
- [ ] Wrong password fails
- [ ] Session persists across pages

### ✅ **Tenant Isolation**
- [ ] Client 1 cannot see Client 2's employees
- [ ] Client 1 cannot see Client 2's attendance
- [ ] Same PIN works for different tenants
- [ ] Cross-tenant admin access blocked

### ✅ **Attendance System**
- [ ] Employee can mark attendance with PIN
- [ ] Photo upload works
- [ ] GPS location captured (if allowed)
- [ ] Attendance appears in admin dashboard

### ✅ **QR Code Generation**
- [ ] QR code generates successfully
- [ ] QR code contains correct subdomain URL
- [ ] Page is printable

### ✅ **Inventory Management**
- [ ] Can add materials
- [ ] Stock updates work
- [ ] Materials are tenant-specific

---

## 🐛 **Troubleshooting**

### **Problem: "Tenant Not Found" error**
**Solution:** Make sure you're accessing via subdomain:
- ❌ Wrong: `http://localhost:5001/admin`
- ✅ Correct: `http://vijayservice.lvh.me:5001/admin`

### **Problem: lvh.me not working**
**Solution:** 
1. Check internet connection (lvh.me requires DNS lookup)
2. Try `ping lvh.me` to verify it resolves
3. Use /etc/hosts method instead

### **Problem: "No module named 'models'"**
**Solution:**
```bash
cd /Users/rishjain/Downloads/attendence_app/modular_app
python app.py
```
Make sure you're in the `modular_app` directory!

### **Problem: "Table doesn't exist" error**
**Solution:** Re-initialize database:
```bash
python init_db.py
```

### **Problem: Can't access from phone**
**Solution:**
1. Make sure phone is on same WiFi
2. Check Mac's firewall settings
3. Use Mac's local IP (not lvh.me) from phone
4. Try: `http://192.168.x.x:5001/attendance`

---

## 📱 **Testing from Mobile**

### **Method 1: Using Mac's Local IP**
```bash
# On Mac, get your local IP:
ifconfig | grep "inet " | grep -v 127.0.0.1

# Example output: 192.168.29.38
```

On phone browser:
- Registration: `http://192.168.29.38:5001/register/`
- Admin: `http://192.168.29.38:5001/admin/login`
- Attendance: `http://192.168.29.38:5001/attendance`

**Note:** Subdomains won't work with IP addresses directly. The middleware will treat it as "no subdomain" and show the registration page.

**Workaround for testing:**
For now, test attendance using:
1. Register tenant on Mac: `http://lvh.me:5001/register/`
2. Add employee on Mac: `http://vijayservice.lvh.me:5001/admin/employees`
3. Test attendance from phone: `http://192.168.29.38:5001/attendance`
   - This will work but won't show the correct tenant initially
   - For full subdomain testing, you need to deploy to a real domain

### **Method 2: Use Cloudflare Tunnel (Temporary)**
If you want to test with real subdomains before deploying:
```bash
cloudflared tunnel --url http://localhost:5001
```

Then use the generated URL (e.g., `https://random-name.trycloudflare.com`)

---

## 🎯 **What to Look For**

### **Good Signs ✅**
- Different tenants see different data
- Same PIN works for multiple tenants
- QR codes have correct subdomains
- Photos display correctly
- Session stays logged in
- Dashboard shows correct stats

### **Bad Signs ❌**
- Client 1 can see Client 2's data → **BUG!**
- PIN conflict across tenants → **BUG!**
- Session logs out randomly → **BUG!**
- Error messages instead of pages → **BUG!**

---

## 🚀 **After Testing**

Once everything works locally, we'll:
1. Update app.py for PostgreSQL
2. Push to GitHub
3. Deploy to Render
4. Configure Cloudflare DNS
5. Test with real subdomains!

---

## ❓ **Need Help?**

Just let me know what's not working and I'll help troubleshoot!

