# 🎂 Birthday & Anniversary Bonus Points - Setup Guide

## 📋 Overview

This system automatically credits bonus points to customers on their birthdays and anniversaries, and removes them at midnight if not used.

---

## ✅ **What's Been Implemented**

### 1. **Automated Bonus Crediting**
- Daily task runs at **12:00 AM IST**
- Checks all customers with birthday/anniversary today
- Credits bonus points automatically
- Creates transaction records

### 2. **Automatic Expiry**
- Bonus points expire at **11:59 PM IST** on the same day
- Unused points are automatically removed
- Creates expiry transaction records

### 3. **Smart Tracking**
- Prevents double-crediting (if task runs multiple times)
- Tracks which points are temporary vs permanent
- Maintains full transaction history

### 4. **IST Timezone**
- All operations use **India Standard Time (IST)**
- Midnight = 12:00 AM IST
- Expiry = 11:59 PM IST

---

## 🔧 **Setup Instructions**

### **Step 1: Run Database Migration**

First, add the required columns to the database:

```
Visit: https://yourdomain.com/migrate/add-special-day-bonus-columns
```

This adds two new columns to `loyalty_transactions`:
- `is_temporary` - Boolean flag for temporary points
- `expires_at` - Datetime when points expire

---

### **Step 2: Configure Loyalty Settings**

1. Go to **Admin Panel → Loyalty Program → Settings**
2. Enable birthday bonus:
   - Check "Enable Birthday Bonus"
   - Set points (e.g., 100)
3. Enable anniversary bonus:
   - Check "Enable Anniversary Bonus"
   - Set points (e.g., 100)
4. Click **Save Settings**

---

### **Step 3: Add Customer Birthdays/Anniversaries**

For each customer:
1. Go to **Admin Panel → Customers → Edit Customer**
2. Fill in:
   - **Date of Birth** (optional)
   - **Anniversary Date** (optional)
3. Click **Save**

---

### **Step 4: Set Up Scheduled Task**

You need to schedule the task to run **daily at midnight IST**.

#### **Option A: Vercel Cron (Recommended for Vercel Deployment)**

Create/update `vercel.json` in your project root:

```json
{
  "crons": [
    {
      "path": "/scheduled-tasks/process-special-day-bonuses",
      "schedule": "30 18 * * *"
    }
  ]
}
```

**Why 18:30 UTC?**
- Midnight IST = 6:30 PM UTC (18:30)
- IST is UTC+5:30
- Schedule runs daily at 12:00 AM IST

**Security:**
Add this to your environment variables:
```
X_CRON_SECRET=bizbooks-cron-2025
```

---

#### **Option B: External Cron Service (Alternative)**

Use a service like **cron-job.org**:

1. Sign up at https://cron-job.org
2. Create a new cron job:
   - **URL:** `https://yourdomain.com/scheduled-tasks/process-special-day-bonuses`
   - **Method:** POST
   - **Schedule:** Daily at 00:00 IST (18:30 UTC)
   - **Custom Headers:**
     ```
     X-Cron-Secret: bizbooks-cron-2025
     ```
3. Save and activate

---

#### **Option C: Server Cron Job (Self-Hosted)**

If running on your own server, add to crontab:

```bash
# Run daily at midnight IST (adjust for your server's timezone)
30 18 * * * curl -X POST -H "X-Cron-Secret: bizbooks-cron-2025" https://yourdomain.com/scheduled-tasks/process-special-day-bonuses
```

---

### **Step 5: Test the System**

#### **Manual Test (No Wait Required)**

Visit this URL to test immediately:

```
https://yourdomain.com/scheduled-tasks/test-special-day-bonuses
```

This will:
- Process all tenants
- Credit bonuses for today's birthdays/anniversaries
- Show detailed results

**Example Response:**
```json
{
  "success": true,
  "test_execution_time": "2025-12-19T12:00:00+05:30",
  "results": {
    "tenants_processed": 1,
    "birthday_bonuses_credited": 2,
    "anniversary_bonuses_credited": 1,
    "expired_bonuses_removed": 0,
    "notifications_sent": 3,
    "errors": []
  }
}
```

---

## 📊 **How It Works**

### **Credit Flow (Midnight IST)**

```
12:00 AM IST
│
├─→ Find all customers with birthday/anniversary today
│   ├─→ Check if already credited (prevent duplicates)
│   ├─→ Credit bonus points
│   ├─→ Create transaction record
│   │   ├─→ type: 'special_day_bonus'
│   │   ├─→ is_temporary: true
│   │   ├─→ expires_at: 11:59 PM tonight
│   └─→ Send notification (SMS/Email)
│
└─→ Result: Customer has bonus points for the day!
```

### **Expiry Flow (Next Day Midnight)**

```
12:00 AM IST (Next Day)
│
├─→ Find all expired bonuses (yesterday's)
│   ├─→ Check if points were used in purchases
│   ├─→ Calculate unused points
│   ├─→ Deduct unused points
│   ├─→ Create expiry transaction record
│   │   ├─→ type: 'expired'
│   │   └─→ points: negative (removal)
│
└─→ Result: Unused bonus points removed!
```

---

## 🔍 **Verification**

### **Check if Bonus was Credited**

1. Go to **Admin Panel → Customers → View Customer**
2. Click **Points Ledger**
3. Look for transaction:
   - Type: "Special Day Bonus"
   - Description: "🎂 Birthday Bonus" or "🎉 Anniversary Bonus"
   - Points: +100 (or configured amount)
   - Expires: "11:59 PM tonight"

### **Check Customer's Current Balance**

```
Current Points = Lifetime Earned - Redeemed + Active Bonuses
```

Example:
- Lifetime earned: 500 pts
- Redeemed: 200 pts
- Birthday bonus today: 100 pts
- **Current balance: 400 pts** (500 - 200 + 100)

---

## 📱 **Customer Notifications**

### **Current Implementation**

The system prepares notifications but needs SMS/Email integration:

**Birthday Message:**
```
🎂 Happy Birthday [Name]! Enjoy 100 bonus points today! 
Use them on your next visit. - [Store Name]
```

**Anniversary Message:**
```
🎉 Happy Anniversary [Name]! Enjoy 100 bonus points today! 
Use them on your next visit. - [Store Name]
```

### **SMS Integration (Future)**

To send actual SMS, integrate with:
- **MSG91** (Indian SMS gateway)
- **Twilio**
- **AWS SNS**

Update `SpecialDayBonusService._send_notification()` method.

### **Email Integration (Future)**

To send emails, integrate with:
- **SendGrid**
- **Amazon SES**
- **Mailgun**

---

## 🛡️ **Security**

### **Scheduled Task Endpoint Security**

The `/scheduled-tasks/process-special-day-bonuses` endpoint requires:

**Header:**
```
X-Cron-Secret: bizbooks-cron-2025
```

**Without this header:**
```json
{
  "error": "Unauthorized",
  "message": "Invalid or missing X-Cron-Secret header"
}
```

**Best Practice:**
- Store secret in environment variable
- Use a strong, random secret in production
- Rotate secret periodically

---

## 🐛 **Troubleshooting**

### **Problem: Bonus Points Not Credited**

**Check:**
1. Is loyalty program active for the tenant?
2. Is birthday/anniversary bonus enabled in settings?
3. Are bonus points > 0 in settings?
4. Does customer have date_of_birth/anniversary_date set?
5. Is the date correct (check month and day)?
6. Has the scheduled task run today?

**View Logs:**
```
Check Vercel logs or server logs for:
"=== Special Day Bonus Task Started ==="
```

---

### **Problem: Points Not Expiring**

**Check:**
1. Is the scheduled task running the next day?
2. Are points actually unused? (Check transaction history)
3. Are transaction records marked with `is_temporary=true`?

---

### **Problem: Duplicate Credits**

**Should NOT happen!** System checks for existing credits today.

**If it does happen:**
1. Check transaction history for duplicates
2. Verify `created_at` dates
3. Check if task ran multiple times

---

## 📈 **Database Schema**

### **loyalty_transactions Table**

```sql
CREATE TABLE loyalty_transactions (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL,
    customer_id INTEGER NOT NULL,
    transaction_type VARCHAR(20),  -- 'special_day_bonus', 'expired'
    points INTEGER,  -- Positive for credit, negative for expiry
    points_before INTEGER,
    points_after INTEGER,
    description TEXT,  -- "🎂 Birthday Bonus", "Special day bonus expired"
    created_at TIMESTAMP,
    
    -- NEW: Special day bonus fields
    is_temporary BOOLEAN DEFAULT FALSE,  -- TRUE for birthday/anniversary
    expires_at TIMESTAMP  -- When temporary points expire
);
```

---

## 🎯 **Real-World Example**

### **Scenario: Ramesh's Birthday**

**Date:** 19th December 2025  
**Customer:** Ramesh (ID: 123)  
**DOB:** 19th December 1985  
**Loyalty Settings:** Birthday bonus = 100 pts

#### **Timeline:**

**19th Dec, 12:00 AM IST:**
```
✅ Scheduled task runs
✅ Detects Ramesh's birthday
✅ Credits 100 bonus points
✅ Transaction created:
   - Type: 'special_day_bonus'
   - Points: +100
   - Expires: 19th Dec, 11:59 PM IST
   - is_temporary: true
✅ SMS sent: "🎂 Happy Birthday Ramesh! Enjoy 100 bonus points today!"
```

**19th Dec, 3:00 PM:**
```
Ramesh visits store
Previous balance: 250 pts
Current balance: 350 pts (250 + 100 birthday bonus)
Uses 150 pts for ₹150 discount
Balance after: 200 pts
```

**20th Dec, 12:00 AM IST:**
```
✅ Scheduled task runs
✅ Finds yesterday's birthday bonus
✅ Checks usage: 150 pts used, 0 pts unused
✅ No points removed (all used!)
```

---

### **Scenario: Priya's Birthday (Unused)**

**Date:** 19th December 2025  
**Customer:** Priya (ID: 456)  
**DOB:** 19th December 1990  
**Loyalty Settings:** Birthday bonus = 100 pts

#### **Timeline:**

**19th Dec, 12:00 AM IST:**
```
✅ Scheduled task runs
✅ Detects Priya's birthday
✅ Credits 100 bonus points
✅ Balance: 450 pts (350 + 100)
```

**19th Dec (Entire Day):**
```
Priya doesn't visit store
Bonus points remain unused
```

**20th Dec, 12:00 AM IST:**
```
✅ Scheduled task runs
✅ Finds yesterday's birthday bonus
✅ Checks usage: 0 pts used, 100 pts unused
✅ Removes 100 unused bonus points
✅ Transaction created:
   - Type: 'expired'
   - Points: -100
   - Description: "Special day bonus expired (unused)"
✅ Balance: 350 pts (back to original)
```

---

## 📝 **Development Notes**

### **Files Created/Modified**

**New Files:**
- `services/special_day_bonus_service.py` - Core logic
- `routes/scheduled_tasks.py` - Scheduled task endpoints
- `routes/add_special_day_bonus_columns.py` - Database migration

**Modified Files:**
- `models/loyalty_transaction.py` - Added `is_temporary`, `expires_at`
- `app.py` - Registered new blueprints

---

## 🚀 **Deployment Checklist**

- [ ] Run database migration
- [ ] Configure loyalty settings (enable bonuses)
- [ ] Add customer birthdays/anniversaries
- [ ] Set up Vercel cron or external cron
- [ ] Add `X-Cron-Secret` to environment variables
- [ ] Test with `/test-special-day-bonuses` endpoint
- [ ] Wait for midnight IST to verify automatic execution
- [ ] Check transaction history the next morning
- [ ] Monitor logs for errors

---

## 💡 **Future Enhancements**

1. **SMS Integration**
   - Integrate MSG91/Twilio for actual SMS
   - Send at 9 AM IST (better timing than midnight)

2. **Email Notifications**
   - Send beautiful HTML email
   - Include personalized offer/coupon

3. **Advanced Rules**
   - Different bonus amounts by customer tier
   - Bonus multipliers on special occasions
   - "Birthday week" bonuses (7 days instead of 1)

4. **Reminder Notifications**
   - "1 hour left to use your birthday points!"
   - Push notification at 11 PM IST

5. **Analytics Dashboard**
   - How many customers used birthday bonus?
   - Average redemption rate
   - ROI on special day bonuses

---

## 📞 **Support**

For issues or questions, contact:
- **Email:** bizbooks.notifications@gmail.com
- **Phone:** +91 8983121201

---

**Last Updated:** 19th December 2025  
**Version:** 1.0  
**Status:** ✅ Ready for Production

