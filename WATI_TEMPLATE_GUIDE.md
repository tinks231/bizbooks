# 📱 WATI WhatsApp Template Setup Guide

## Overview
This guide shows you how to create WhatsApp message templates in WATI that BizBooks will use to send notifications.

---

## 🔧 Setup Steps

### Step 1: Log into WATI
1. Go to https://app.wati.io
2. Log in with your account (Rohit Jain's account)
3. Go to **"Message Templates"** section

### Step 2: Create Templates
You need to create **7 templates** for BizBooks. Copy these exactly:

---

## 📋 Template 1: Invoice Notification

**Template Name:** `invoice_notification`

**Category:** `UTILITY` (or `ACCOUNT_UPDATE`)

**Language:** English

**Message Body:**
```
Hi {{1}}! 📄

Your invoice {{2}} is ready!

💰 Amount: {{3}}
✅ Status: Ready to view

📎 View Invoice: {{4}}

Your invoice is attached as PDF above ⬆️

Thank you for your business! 🙏

- Mahaveer Electricals
Support: 8983121201
```

**Variables:**
- `{{1}}` = Customer Name
- `{{2}}` = Invoice Number
- `{{3}}` = Amount
- `{{4}}` = View URL

**Media:** Enable "Document" (PDF attachment)

---

## 📋 Template 2: Order Confirmation

**Template Name:** `order_confirmation`

**Category:** `UTILITY` (or `ORDER_UPDATE`)

**Language:** English

**Message Body:**
```
Hi {{1}}! 👋

Your order #{{2}} has been confirmed! 🎉

📦 Items: {{3}}
💰 Total: {{4}}
📅 Delivery: {{5}}

We'll notify you when your order is out for delivery.

Questions? Reply to this message!

- Mahaveer Electricals
```

**Variables:**
- `{{1}}` = Customer Name
- `{{2}}` = Order ID
- `{{3}}` = Items Summary
- `{{4}}` = Amount
- `{{5}}` = Delivery Date

---

## 📋 Template 3: Delivery Reminder

**Template Name:** `delivery_reminder`

**Category:** `UTILITY` (or `SHIPPING_UPDATE`)

**Language:** English

**Message Body:**
```
Hi {{1}}! 🌅

Your delivery is scheduled for {{3}}!

📦 Items: {{2}}
⏰ Expected Time: {{4}}

Please ensure someone is available to receive the order.

Questions? Reply to this message!

- Mahaveer Electricals
Support: 8983121201
```

**Variables:**
- `{{1}}` = Customer Name
- `{{2}}` = Items Summary
- `{{3}}` = Delivery Date
- `{{4}}` = Time Window

---

## 📋 Template 4: Subscription Paused

**Template Name:** `subscription_paused`

**Category:** `UTILITY` (or `ACCOUNT_UPDATE`)

**Language:** English

**Message Body:**
```
Hi {{1}}! ⏸️

Your {{2}} subscription has been PAUSED for:
📅 {{3}}

You can resume anytime from your customer portal or by replying to this message.

Need help? Call us at 8983121201

- Mahaveer Electricals
```

**Variables:**
- `{{1}}` = Customer Name
- `{{2}}` = Product Name
- `{{3}}` = Pause Date

---

## 📋 Template 5: Subscription Resumed

**Template Name:** `subscription_resumed`

**Category:** `UTILITY` (or `ACCOUNT_UPDATE`)

**Language:** English

**Message Body:**
```
Hi {{1}}! ▶️

Your {{2}} subscription has been RESUMED from:
📅 {{3}}

Deliveries will continue as scheduled.

Thank you for choosing us! 🙏

- Mahaveer Electricals
Support: 8983121201
```

**Variables:**
- `{{1}}` = Customer Name
- `{{2}}` = Product Name
- `{{3}}` = Resume Date

---

## 📋 Template 6: Subscription Modified

**Template Name:** `subscription_modified`

**Category:** `UTILITY` (or `ACCOUNT_UPDATE`)

**Language:** English

**Message Body:**
```
Hi {{1}}! 🔄

Your {{2}} subscription has been MODIFIED for {{3}}:

Changed from: {{4}} → {{5}}

Need further changes? Visit your customer portal or reply here.

- Mahaveer Electricals
Support: 8983121201
```

**Variables:**
- `{{1}}` = Customer Name
- `{{2}}` = Product Name
- `{{3}}` = Modify Date
- `{{4}}` = Old Quantity
- `{{5}}` = New Quantity

---

## 📋 Template 7: Payment Reminder

**Template Name:** `payment_reminder`

**Category:** `UTILITY` (or `PAYMENT_UPDATE`)

**Language:** English

**Message Body:**
```
Hi {{1}}! 💳

Friendly reminder: You have an outstanding balance of {{2}}

📅 Due Date: {{3}}

💰 Pay Now: {{4}}

Questions about your bill? Reply to this message or call 8983121201

Thank you for your business! 🙏

- Mahaveer Electricals
```

**Variables:**
- `{{1}}` = Customer Name
- `{{2}}` = Amount
- `{{3}}` = Due Date
- `{{4}}` = Payment URL

---

## ⚠️ Important Notes

### Template Approval Process
1. **Submit for Approval:** After creating each template, submit it to WhatsApp for approval
2. **Wait Time:** 1-24 hours (usually within 2 hours)
3. **Status Check:** Templates must show "APPROVED" status before BizBooks can use them
4. **Rejection Reasons:** If rejected:
   - Too promotional language → Make it transactional
   - Missing opt-out → Add "Reply STOP to unsubscribe"
   - Non-compliant → Follow WhatsApp's template guidelines

### Variable Naming
- Use `{{1}}`, `{{2}}`, `{{3}}` format (exactly as shown)
- WATI will map these to parameter names in the API
- BizBooks sends parameters in the same order

### Media Attachments
- **Invoice template:** Enable "Document" media type for PDF
- Other templates: No media needed (text only)

---

## 🚀 After Templates are Approved

### Add Credentials to BizBooks

Edit `.env` file:

```bash
# WhatsApp (WATI) Configuration
WATI_API_URL=https://live-server.wati.io
WATI_API_KEY=your_api_key_here
WATI_INSTANCE_ID=your_instance_id_here
```

### Where to Find Credentials

1. **WATI Dashboard** → **Settings** → **API**
2. Copy:
   - **API Endpoint** → `WATI_API_URL` (usually `https://live-server.wati.io`)
   - **Authorization Token** → `WATI_API_KEY`
   - **Instance ID** → `WATI_INSTANCE_ID`

### Test the Integration

I'll create a test script to verify everything works:

```bash
# From project root
python -c "from modular_app.utils.whatsapp_utils import get_whatsapp_service; print(get_whatsapp_service().enabled)"
```

Should print: `True` ✅

---

## 📞 Support

**Questions?**
- WATI Support: support@wati.io
- WATI Docs: https://docs.wati.io
- BizBooks Integration: Ask me (Cursor AI)! 🤖

---

## ✅ Checklist

Before going live, verify:

- [ ] WATI account created and verified
- [ ] WhatsApp Business number connected
- [ ] All 7 templates created in WATI
- [ ] All 7 templates APPROVED by WhatsApp
- [ ] API credentials added to `.env` file
- [ ] Test message sent successfully
- [ ] Invoice PDF attachment working
- [ ] Customer receives messages correctly

**When all checked → Ready to go live! 🚀**


