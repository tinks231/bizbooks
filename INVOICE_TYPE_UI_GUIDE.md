# Invoice Type Selection UI - User Guide

## 🎨 NEW UI (Just Added!)

You now have **3 clear options** instead of a hidden checkbox:

```
┌──────────────────────────────────────────────────────────────────────┐
│ 📋 Invoice Type                                                      │
│                                                                       │
│  ┌─────────────────┐  ┌──────────────────┐  ┌─────────────────────┐ │
│  │ ✅ Taxable      │  │ 📄 Non-Taxable   │  │ 🔄 Credit Adjust   │ │
│  │ (GST Invoice)   │  │ (Kaccha Bill)    │  │ (GST Compliance)   │ │
│  │                 │  │                  │  │                     │ │
│  │ Regular invoice │  │ Invoice without  │  │ GST compliance for │ │
│  │ with GST charges│  │ GST (cash sales) │  │ kaccha bills       │ │
│  │                 │  │                  │  │                     │ │
│  │ Requires GST    │  │ Can use any stock│  │ No stock impact    │ │
│  │ stock           │  │                  │  │                     │ │
│  └─────────────────┘  └──────────────────┘  └─────────────────────┘ │
│                                                                       │
└──────────────────────────────────────────────────────────────────────┘
```

---

## ✅ **Option 1: Taxable (GST Invoice)** - GREEN

**When to use:**
- Regular sales with GST
- B2B customers
- Customers who need GST invoice

**What happens:**
- GST calculated and shown (CGST/SGST or IGST)
- Stock reduced from **GST stock**
- Appears in **GSTR-1 report**
- Commission & Loyalty processed

**Visual:**
```
[●] ✅ Taxable (GST Invoice)
    Regular invoice with GST charges
    Requires GST stock
```

---

## 📄 **Option 2: Non-Taxable (Kaccha Bill)** - ORANGE

**When to use:**
- Cash sales
- Retail customers (no GST needed)
- Small purchases
- When you want to avoid GST paperwork

**What happens:**
- No GST calculated (₹0 CGST/SGST)
- Stock reduced from any stock (prefers non-GST first)
- **Does NOT appear in GSTR-1 report**
- Commission & Loyalty processed normally

**Visual:**
```
[●] 📄 Non-Taxable (Kaccha Bill)
    Invoice without GST (cash sales)
    Can use any stock
```

---

## 🔄 **Option 3: Credit Adjustment** - PURPLE

**When to use:**
- You already created a kaccha bill
- Customer already paid (via kaccha bill)
- Need to show GST breakdown for compliance
- Want to transfer ITC benefit

**What happens when selected:**
A new purple section appears below:

```
┌───────────────────────────────────────────────────────────────────┐
│ 🔄 Credit Adjustment Details                                      │
│                                                                    │
│ Create a GST-compliant invoice for a previous kaccha bill.        │
│ Stock will NOT be reduced (already reduced in original invoice).  │
│                                                                    │
│ ┌─────────────────────────┬────────────────────────────────────┐ │
│ │ Original Invoice        │ Commission Rate (%)                │ │
│ │ [--- Not Linked ---]▼   │ [5                    ]            │ │
│ │ Link to original kaccha │ Your benefit for GST compliance    │ │
│ │ bill (for reference)    │ work (recorded as "Other Income")  │ │
│ └─────────────────────────┴────────────────────────────────────┘ │
│                                                                    │
│ 💡 How Credit Adjustment Works:                                   │
│ • Customer already paid (via kaccha bill)                         │
│ • Create this invoice to show GST breakdown for compliance        │
│ • Stock is NOT reduced (already done in kaccha bill)              │
│ • Commission recorded as "Other Income" (your benefit)            │
│ • Appears in GSTR-1 report for CA filing                          │
└───────────────────────────────────────────────────────────────────┘
```

**Details:**

1. **Original Invoice (Optional):**
   - Dropdown to link to the kaccha bill (if you remember it)
   - **You can skip this** - system works without linking
   - Just for your reference/tracking

2. **Commission Rate (%):**
   - Default: 5%
   - This is YOUR benefit for doing GST compliance work
   - Example: If invoice total is ₹1500:
     - GST to govt: ₹160
     - Your commission: ₹88 (recorded as "Other Income")
     - This compensates you for paying GST but not receiving ITC

**What happens:**
- GST breakdown shown (CGST/SGST or IGST)
- **Stock NOT reduced** (already done in kaccha bill)
- Commission recorded as "Other Income"
- **Appears in GSTR-1 report**
- **No commission/loyalty** (already processed in kaccha bill)

**Visual:**
```
[●] 🔄 Credit Adjustment
    GST compliance for kaccha bills
    No stock impact
```

---

## 🎯 **How to Create Each Type:**

### **Create Taxable Invoice (GST):**
1. **Restart server** (model was updated)
2. Go to **Create Invoice**
3. **Select** "✅ Taxable (GST Invoice)" (Green)
4. Add items - you'll see **"GST: 22 units | Non-GST: 0 units"**
5. GST will auto-calculate
6. Save → Stock reduces, GST charged, appears in GSTR-1 ✅

---

### **Create Kaccha Bill (Non-GST):**
1. Go to **Create Invoice**
2. **Select** "📄 Non-Taxable (Kaccha Bill)" (Orange)
3. Add items
4. No GST shown (₹0 CGST/SGST)
5. Save → Stock reduces, no GST, does NOT appear in GSTR-1 ✅

---

### **Create Credit Adjustment:**
1. Go to **Create Invoice**
2. **Select** "🔄 Credit Adjustment" (Purple)
3. **Purple section appears** below
4. (Optional) Select original kaccha bill from dropdown
5. Set commission rate (default 5%)
6. Add items (same items as kaccha bill)
7. GST will auto-calculate
8. Save → NO stock reduction, GST shown, appears in GSTR-1 ✅

---

## 📊 **Stock Tracking - You Don't Need to Track Manually!**

### **Your Concern:**
> "Hard to track how many kaccha and GST bills were created"

### **Our Solution:**
**The system tracks it automatically!** You see badges:

```
Item: Allen Solly Shirt

[GST: 22 units] [Non-GST: 0 units]
    ↑               ↑
    Available       Available
    for GST         for non-GST
    invoices        invoices
```

**What this means:**
- You can create **maximum 22 GST invoices** (1 unit each)
- You **cannot** create non-GST invoices (0 stock)
- If you try to create 23rd GST invoice → **BLOCKED!** ✅

**Try it:**
1. Create 22 GST invoices (1 unit each)
2. Stock badge updates: `GST: 0 units`
3. Try creating 23rd → Error: "Insufficient GST stock" ✅

---

## ⚠️ **Validations (Already Built In):**

### **1. Insufficient GST Stock:**
```
❌ Cannot create GST invoice - insufficient GST stock.

Requested: 25 units
GST Stock Available: 22 units
Non-GST Stock: 0 units

⚠️ Items purchased WITHOUT GST cannot be sold WITH GST invoice.

Options:
1. Reduce quantity to 22 units (GST stock available)
2. Create non-GST invoice (kaccha bill) for this sale
3. Later create Credit Adjustment invoice for compliance
```

### **2. Exempt Item (GST Rate = 0):**
```
❌ Cannot create GST invoice for exempt item.

Item: Books
GST Rate: 0% (Exempt by law)

This item is GST-exempt. Only non-taxable invoices are allowed.
```

---

## 🚀 **Next Steps:**

1. **Restart your server** (model was updated):
   ```bash
   # Stop current server (Ctrl+C)
   python modular_app/app.py
   ```

2. **Go to Create Invoice** page

3. **You'll see the new radio buttons** (3 colored options)

4. **Test each type:**
   - ✅ Create Taxable invoice (Green) → See GST calculated
   - 📄 Create Kaccha bill (Orange) → See no GST
   - 🔄 Create Credit Adjustment (Purple) → See purple section appear

5. **Check reports:**
   - GSTR-1: Only taxable + credit adjustment ✅
   - P&L: ALL invoices (complete picture) ✅

---

## 💡 **Tips:**

1. **Don't worry about tracking manually** - badges show available stock automatically

2. **Commission rate (5%)** is your benefit for GST compliance work - adjust as needed

3. **Linking to original invoice is OPTIONAL** - skip if hard to track

4. **Credit Adjustment = No stock impact** - use it freely for compliance

5. **System prevents illegal transactions** - you can't create more GST invoices than GST stock

---

## 🎨 **Visual Summary:**

```
Regular Sales with GST?
  → Select GREEN (Taxable)
  → Stock: Uses GST stock
  → Reports: Appears in GSTR-1

Cash sales / No GST needed?
  → Select ORANGE (Non-Taxable)
  → Stock: Uses any stock
  → Reports: NOT in GSTR-1

Need GST compliance for kaccha bill?
  → Select PURPLE (Credit Adjustment)
  → Stock: NO reduction
  → Reports: Appears in GSTR-1
```

---

**Ready to test! Let me know how it looks!** 🚀

