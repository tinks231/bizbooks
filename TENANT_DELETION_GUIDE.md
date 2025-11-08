# 🗑️ Tenant Deletion Guide

## ⚠️ DANGER ZONE ⚠️

**This is a PERMANENT action that CANNOT be undone!**

Use this when you need to:
- Remove test data
- Delete a demo tenant
- Clean up before starting fresh
- Remove a closed business account

---

## 📋 What Gets Deleted

### **Database Records:**
- ✅ All Items (inventory)
- ✅ All Purchase Bills
- ✅ All Vendors
- ✅ All Invoices
- ✅ All Customers
- ✅ All Sales Orders
- ✅ All Delivery Challans
- ✅ All Expenses
- ✅ All Sites
- ✅ All Employees
- ✅ All Attendance Records
- ✅ All Purchase Requests
- ✅ All Vendor Payments
- ✅ **Everything** linked to that tenant

### **Files:**
- ✅ Employee selfies
- ✅ Purchase bill documents
- ✅ Item images
- ✅ Company logos
- ✅ Task media
- ✅ All uploaded files with tenant_id in filename

---

## 🚀 How to Delete a Tenant

### **Method 1: By Tenant ID**

```bash
cd modular_app
python delete_tenant.py 11
```

### **Method 2: By Subdomain**

```bash
cd modular_app
python delete_tenant.py --subdomain mahaveerelectricals
```

---

## 📊 Example Output

```
============================================================
🗑️  DELETING TENANT
============================================================
ID: 11
Company: Mahaveer Electricals
Subdomain: mahaveerelectricals
Admin Email: admin@mahaveer.com
============================================================

⚠️  Are you sure? This cannot be undone! (type 'DELETE' to confirm): DELETE

🔄 Deleting tenant data...

🔄 Deleting uploaded files...

============================================================
✅ DELETION COMPLETE
============================================================

📊 Database Records Deleted:
   • Purchase Bills: 5
   • Purchase Bill Items: 12
   • Vendors: 3
   • Items: 45
   • Employees: 8
   • Sites: 2
   • Invoices: 23
   • Invoice Items: 67
   • Customers: 15

📁 Files Deleted: 8
   • uploads/documents/tenant_11_bill_20251107.pdf
   • uploads/documents/tenant_11_bill_20251108.jpg
   • uploads/selfies/tenant_11_emp_123.jpg
   • uploads/inventory_images/tenant_11_item_456.png
   ...

📂 Folders Deleted: 1
   • uploads/documents/tenant_11/

✅ Tenant 'Mahaveer Electricals' has been completely removed!
============================================================
```

---

## 🔒 Safety Features

1. **Confirmation Required**: Must type 'DELETE' to confirm
2. **Shows Tenant Info**: See what you're deleting before confirmation
3. **Detailed Summary**: Lists everything that was deleted
4. **No Accidental Deletions**: Requires explicit tenant ID/subdomain

---

## 💾 Storage Savings

After deletion, you'll free up:
- **Database space**: All tenant records
- **Blob storage**: All uploaded files (images, documents, selfies)
- **Important for 1GB limit**: Clean up test data regularly!

---

## 🔄 After Deletion

1. **Register a new tenant** at `/register`
2. **Bulk import items** if starting fresh
3. **Set up company details** again

---

## ⚠️ IMPORTANT NOTES

### **What is NOT deleted:**
- ❌ Other tenants (multi-tenant safe)
- ❌ System tables
- ❌ Migration history

### **Before deleting:**
- 📥 **Export reports** if you need them later
- 📸 **Backup important data** (we don't have backups!)
- ✅ **Make sure** you're deleting the right tenant

---

## 🐛 Troubleshooting

### **"Tenant not found"**
```bash
# Check available tenants first:
cd modular_app
python -c "from app import app, db; from models import Tenant; app.app_context().push(); print([f'{t.id}: {t.subdomain}' for t in Tenant.query.all()])"
```

### **"Error deleting files"**
- Some files may be in use
- Check file permissions
- Files in subdirectories won't be deleted automatically

### **"Foreign key constraint error"**
- Script handles deletion order automatically
- If it fails, there's a missing model in the deletion list
- Contact support

---

## 📞 Need Help?

If deletion fails or you need to recover data:
- **Contact support immediately**
- **Don't delete anything else**
- **Provide error messages**

---

**Remember: This is PERMANENT. Triple-check before confirming!**

