# 🧪 BizBooks V1 - Testing Checklist

## Pre-Release Testing Guide
**Version:** 1.0  
**Last Updated:** November 1, 2025

---

## 🎯 Test Environment Setup

### Local Testing
- [ ] Fresh database migration
- [ ] Test data created (2-3 tenants, 5-10 employees each)
- [ ] All environment variables set
- [ ] Clear browser cache before testing

### Production Testing (Vercel)
- [ ] Deployment successful
- [ ] Environment variables configured
- [ ] PostgreSQL connected
- [ ] Vercel Blob storage configured

---

## 👤 1. Tenant Registration & Login

### Registration
- [ ] Register new tenant with valid data
- [ ] Try duplicate subdomain (should fail)
- [ ] Try invalid phone (should fail)
- [ ] Verify auto-login after registration
- [ ] Check tenant settings saved correctly

### Admin Login
- [ ] Login with correct credentials
- [ ] Try wrong password (should fail)
- [ ] Logout and login again
- [ ] Session persistence check
- [ ] Multi-tab login behavior

---

## 📍 2. Employee Management

### Add Employee
- [ ] Add employee with all fields
- [ ] Add employee with minimal fields
- [ ] Try duplicate phone (should warn)
- [ ] Generate 4-digit PIN automatically
- [ ] Verify employee active by default

### Edit Employee
- [ ] Edit name, designation, salary
- [ ] Change site assignment
- [ ] Update phone number
- [ ] Deactivate employee
- [ ] Reactivate employee

### Employee List
- [ ] View all employees
- [ ] Search by name
- [ ] Filter by site
- [ ] Sort by name/date
- [ ] Pagination (if >50 employees)

---

## 🏢 3. Sites/Locations

### Create Site
- [ ] Add site with GPS coordinates
- [ ] Add site without GPS (manual entry)
- [ ] Set allowed radius
- [ ] Assign manager

### Manage Sites
- [ ] Edit site details
- [ ] Update GPS location
- [ ] Change radius
- [ ] View employees at site
- [ ] Delete unused site

---

## ⏰ 4. Attendance System

### Employee Check-In/Out
- [ ] **Mobile:** Access `/employee/login`
- [ ] Login with phone + PIN
- [ ] Navigate to Attendance from dashboard
- [ ] Check-in within allowed radius
- [ ] Try check-in outside radius (should fail with distance)
- [ ] Check-out after check-in
- [ ] Try duplicate check-in (should prevent)
- [ ] View attendance history

### Admin Attendance View
- [ ] View today's attendance
- [ ] Filter by date range
- [ ] Filter by employee
- [ ] Filter by site
- [ ] Export attendance report
- [ ] See working hours calculation
- [ ] Check overtime calculation

---

## 📦 5. Inventory Management

### Items
- [ ] Add new item (with SKU auto-generate)
- [ ] Add item with manual SKU
- [ ] Add item with category
- [ ] Upload item image
- [ ] Set reorder level
- [ ] Edit item details
- [ ] Search items
- [ ] Filter by category
- [ ] View stock levels

### Categories
- [ ] Create category
- [ ] Edit category
- [ ] Delete empty category
- [ ] Assign items to category

### Stock Management
- [ ] Add stock (with reason)
- [ ] Remove stock (with reason)
- [ ] Transfer stock between sites
- [ ] View stock history
- [ ] Low stock alerts

---

## 🛒 6. Purchase Requests

### Employee Submit Request
- [ ] **Mobile:** Login to employee portal
- [ ] Navigate to Purchase Request
- [ ] Enter phone + PIN (if first time)
- [ ] Fill request form
- [ ] Add photo attachment
- [ ] Submit request
- [ ] View submitted message

### Admin Approve/Reject
- [ ] View pending requests
- [ ] Approve request (check email sent)
- [ ] Reject request with reason (check email sent)
- [ ] View approved/rejected history
- [ ] Filter by status
- [ ] Search by employee

---

## 💰 7. Expenses

### Add Expense
- [ ] Create expense with category
- [ ] Upload receipt
- [ ] Set expense date
- [ ] Assign to employee
- [ ] Save expense

### Manage Expenses
- [ ] View all expenses
- [ ] Filter by date range
- [ ] Filter by category
- [ ] Filter by employee
- [ ] Edit expense
- [ ] Delete expense
- [ ] Export expense report

---

## 📋 8. Task Management

### Admin - Create & Assign Tasks
- [ ] Create new task
- [ ] Assign to employee
- [ ] Set priority (low/medium/high)
- [ ] Set deadline
- [ ] Assign to site
- [ ] Add description
- [ ] Task notification sent (check email)

### Admin - Manage Tasks
- [ ] View all tasks
- [ ] Filter by status
- [ ] Filter by employee
- [ ] Filter by site
- [ ] Search tasks
- [ ] View task details
- [ ] Edit task
- [ ] Cancel task
- [ ] Delete completed task

### Employee - View & Update Tasks
- [ ] **Mobile:** Login to employee portal
- [ ] Navigate to My Tasks
- [ ] View assigned tasks
- [ ] See task details
- [ ] Update progress percentage
- [ ] Change status (new → in_progress → completed)
- [ ] Add notes
- [ ] Upload photo (test image compression)
- [ ] Upload multiple photos
- [ ] Add materials used
- [ ] Update worker count
- [ ] View task history

### Task Cleanup
- [ ] Manually delete completed task
- [ ] Bulk delete all completed tasks
- [ ] Run cleanup old media (30+ days)
- [ ] Verify storage freed

---

## 👥 9. Customer Management

### Add Customer
- [ ] Create customer with all fields
- [ ] Create customer with minimal fields
- [ ] Auto-generate customer code
- [ ] Try duplicate phone (should warn)

### Manage Customers
- [ ] Edit customer details
- [ ] View customer invoices
- [ ] View outstanding amount
- [ ] Search customers
- [ ] Filter by status

---

## 🧾 10. GST Invoicing

### Create Invoice
- [ ] Select existing customer
- [ ] Add invoice number (auto-increment)
- [ ] Add items from inventory
- [ ] Add custom items (manual entry)
- [ ] Set item quantity
- [ ] Set item price
- [ ] Toggle "Tax Inclusive" per item
- [ ] Select GST rate (5%, 12%, 18%, 28%)
- [ ] Auto-calculate CGST/SGST
- [ ] Select "Cash Sale" or "Credit Sale"
- [ ] Add notes/terms
- [ ] Save as draft
- [ ] Mark as sent

### Invoice Settings
- [ ] Upload company logo
- [ ] Set GSTIN
- [ ] Set company address
- [ ] Set phone/email
- [ ] Set invoice terms
- [ ] Verify settings saved

### View & Print Invoice
- [ ] View invoice
- [ ] Check logo appears
- [ ] Check company details appear
- [ ] Check customer details linked
- [ ] Switch themes (6 themes)
- [ ] **Desktop:** Print invoice (should fit 1 page A4)
- [ ] **Mobile:** Print invoice (should be 2-column, professional)
- [ ] Verify totals correct
- [ ] Verify GST calculations
- [ ] Edit invoice
- [ ] Record payment
- [ ] Generate PDF

### Invoice List
- [ ] View all invoices
- [ ] Filter by status
- [ ] Filter by payment status
- [ ] Search by invoice number
- [ ] Search by customer name
- [ ] Sort by date/amount

---

## 👷 11. Unified Employee Portal

### Portal Access
- [ ] **Mobile:** Scan QR code → Goes to `/employee/login`
- [ ] Enter phone + PIN
- [ ] Login successful

### Dashboard Navigation
- [ ] See 3 action cards (Attendance, Purchase Request, My Tasks)
- [ ] Check attendance status badge (today's status)
- [ ] Check tasks badge (pending count)
- [ ] Click Attendance → Goes to attendance page
- [ ] Click Purchase Request → Goes to request form
- [ ] Click My Tasks → Goes to tasks list
- [ ] Logout button works

### Session Sharing
- [ ] Login once
- [ ] Access all 3 features without re-login
- [ ] Switch between features
- [ ] Session persists across tabs
- [ ] Logout from one feature = logout from all

---

## 🔐 12. Security & Permissions

### Tenant Isolation
- [ ] Login as Tenant A
- [ ] Verify can't see Tenant B's data
- [ ] Try accessing Tenant B's URL directly (should fail)

### Admin Access
- [ ] Login as admin
- [ ] Access all admin features
- [ ] Logout
- [ ] Try accessing admin page (should redirect to login)

### Employee Access
- [ ] Login as employee
- [ ] Verify can only see own tasks
- [ ] Verify can only see own attendance
- [ ] Cannot access admin pages

---

## 🚀 13. Performance Testing

### Page Load Times
- [ ] Dashboard loads < 2 seconds
- [ ] Employee list loads < 2 seconds
- [ ] Attendance page loads < 2 seconds
- [ ] Task list loads < 2 seconds
- [ ] Invoice list loads < 2 seconds

### Mobile Performance
- [ ] Test on 3G network
- [ ] Image compression working (photos < 500KB)
- [ ] Forms responsive
- [ ] No layout shifts
- [ ] Touch targets adequate size

### Database Performance
- [ ] Test with 100+ employees
- [ ] Test with 500+ attendance records
- [ ] Test with 100+ tasks
- [ ] Test with 200+ invoices
- [ ] Check for N+1 queries (use Flask-DebugToolbar locally)

---

## 📱 14. Mobile Responsiveness

### Test on Different Devices
- [ ] iPhone (Safari)
- [ ] Android (Chrome)
- [ ] Tablet (iPad/Android)

### UI Elements
- [ ] Forms fit screen width
- [ ] Buttons large enough to tap
- [ ] Text readable (no zoom needed)
- [ ] Navigation menu accessible
- [ ] Tables scroll horizontally
- [ ] Images scale properly
- [ ] Print layout professional

---

## 🐛 15. Error Handling

### Form Validation
- [ ] Submit empty form (should show errors)
- [ ] Enter invalid phone (should validate)
- [ ] Enter invalid email (should validate)
- [ ] Upload too large file (should show size limit)

### Network Errors
- [ ] Disconnect internet, try action (should show error)
- [ ] Slow network (should show loading)
- [ ] Resume connection (should recover)

### Edge Cases
- [ ] Employee with no tasks
- [ ] Site with no employees
- [ ] Customer with no invoices
- [ ] Day with no attendance
- [ ] Empty inventory

---

## 📊 16. Reporting

### Attendance Reports
- [ ] Generate monthly report
- [ ] Export to CSV/Excel
- [ ] Filter by employee
- [ ] Filter by site
- [ ] Include working hours
- [ ] Include overtime

### Expense Reports
- [ ] Generate expense summary
- [ ] Group by category
- [ ] Group by employee
- [ ] Date range filtering
- [ ] Export functionality

### Invoice Reports
- [ ] Outstanding invoices
- [ ] Paid invoices
- [ ] Revenue by period
- [ ] Customer-wise revenue
- [ ] GST summary

---

## 🔄 17. Data Migration

### Existing Tenants
- [ ] Run `/migrate/add-tasks` for existing tenants
- [ ] Verify no data lost
- [ ] Verify new features accessible
- [ ] Check backward compatibility

---

## 📧 18. Email Notifications

### Task Assignment
- [ ] Employee receives email when task assigned
- [ ] Email contains task details
- [ ] Email formatted correctly
- [ ] Links work in email

### Purchase Requests
- [ ] Admin receives email on new request
- [ ] Employee receives email on approval
- [ ] Employee receives email on rejection
- [ ] Emails sent from correct address

---

## 💾 19. Storage Management

### Vercel Blob Storage
- [ ] Logo uploads to blob
- [ ] Task photos upload to blob
- [ ] Attendance photos upload to blob
- [ ] Files accessible via URL
- [ ] Cleanup deletes from blob
- [ ] Monitor storage usage

---

## 🧹 20. Cleanup & Maintenance

### Manual Cleanup
- [ ] Delete completed task individually
- [ ] Bulk delete all completed tasks
- [ ] Cleanup old media (30+ days)
- [ ] Verify files deleted from Vercel Blob

### Auto Cleanup
- [ ] Wait 24 hours
- [ ] Check auto-cleanup ran
- [ ] Verify old media deleted
- [ ] Check timestamp updated

---

## ✅ RELEASE CHECKLIST

### Code Quality
- [ ] No console errors in browser
- [ ] No Python errors in logs
- [ ] All linter warnings addressed (or documented)
- [ ] Code commented where needed
- [ ] No debug/test code left

### Documentation
- [ ] README updated with features
- [ ] Environment variables documented
- [ ] Deployment guide updated
- [ ] User guide created
- [ ] API endpoints documented (if any)

### Security
- [ ] No hardcoded credentials
- [ ] Environment variables secured
- [ ] SQL injection prevention verified
- [ ] XSS protection verified
- [ ] CSRF tokens enabled
- [ ] Rate limiting considered

### Performance
- [ ] Image compression enabled
- [ ] Database queries optimized
- [ ] No N+1 query problems
- [ ] Static files cached
- [ ] CDN for assets (if needed)

### Backup & Recovery
- [ ] Database backup enabled
- [ ] Backup restore tested
- [ ] Disaster recovery plan
- [ ] Data export functionality

### Monitoring
- [ ] Error tracking setup (Sentry/Rollbar)
- [ ] Performance monitoring
- [ ] Storage usage tracking
- [ ] User activity logs

### Final Steps
- [ ] All tests passed
- [ ] Demo video recorded
- [ ] Marketing materials ready
- [ ] Support documentation ready
- [ ] Pricing page updated
- [ ] Terms & Conditions updated
- [ ] Privacy Policy updated

---

## 🚨 Known Issues & Limitations

### Current Limitations
1. ⚠️ PostgreSQL RLS not enabled (see below)
2. Video compression not implemented (use native camera settings)
3. SMS requires DLT registration in India
4. WhatsApp requires Business API verification
5. 1GB free tier on Vercel Blob (upgrade recommended for production)

### PostgreSQL RLS Warning
**Status:** ⚠️ Not implemented yet  
**Impact:** Low (application-level tenant isolation in place)  
**Recommendation:** Enable RLS before scaling to >100 tenants  
**Priority:** Medium

---

## 📝 Bug Reporting Template

When reporting bugs, include:
```
**Environment:** Local / Production
**Tenant:** [subdomain]
**User Type:** Admin / Employee
**Browser:** Chrome / Safari / Firefox
**Device:** Desktop / Mobile

**Steps to Reproduce:**
1. 
2. 
3. 

**Expected Behavior:**


**Actual Behavior:**


**Screenshots:**
[Attach if applicable]

**Console Errors:**
[Copy from browser console]
```

---

## 🎉 Testing Tips

1. **Test on Real Mobile Devices:** Simulators don't catch all issues
2. **Test with Slow Network:** Use Chrome DevTools Network Throttling
3. **Test with Real Data:** Not just test data
4. **Test Edge Cases:** Empty states, max limits, invalid data
5. **Test User Workflows:** Complete end-to-end scenarios
6. **Test Across Browsers:** Chrome, Safari, Firefox
7. **Test Timezone Differences:** If multi-location deployment
8. **Take Screenshots:** Document bugs with visuals
9. **Note Response Times:** Track performance issues
10. **Get User Feedback:** Beta test with actual users

---

## 📞 Support

For testing support:
- Email: support@bizbooks.co.in
- Documentation: [Link to docs]
- Bug Reports: GitHub Issues
- Feature Requests: Product Board

---

**Happy Testing! 🚀**

