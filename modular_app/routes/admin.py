"""
Admin routes - Login, Dashboard, Management
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g, abort
from models import db, User, Employee, Site, Attendance, Material, Stock, StockMovement, Tenant
from datetime import datetime, timedelta
from sqlalchemy import func, text
from utils.tenant_middleware import require_tenant, get_current_tenant_id, get_current_tenant
from utils.license_check import check_license
import hashlib

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def login_required(f):
    """Decorator to require admin login (also checks license)"""
    from functools import wraps
    @wraps(f)
    @check_license  # ← Check license/trial before allowing access
    def decorated_function(*args, **kwargs):
        if 'tenant_admin_id' not in session:
            flash('Please login first', 'error')
            return redirect(url_for('admin.login'))
        # Verify session tenant matches current tenant
        if session.get('tenant_admin_id') != get_current_tenant_id():
            session.clear()
            flash('Session mismatch. Please login again.', 'error')
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/login', methods=['GET', 'POST'], strict_slashes=False)
@require_tenant
def login():
    """Tenant admin login page - PROFILED"""
    import time
    start_time = time.time()
    
    tenant = get_current_tenant()
    print(f"\n⏱️  LOGIN PERFORMANCE:")
    print(f"1. Get tenant: {(time.time() - start_time)*1000:.0f}ms")
    
    if request.method == 'POST':
        t1 = time.time()
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Hash password for comparison
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        print(f"2. Hash password: {(time.time() - t1)*1000:.0f}ms")
        
        # Check if credentials match tenant admin
        if tenant.admin_email == email and tenant.admin_password_hash == password_hash:
            # Check if email is verified
            if not tenant.email_verified:
                flash('⚠️ Please verify your email address before logging in', 'error')
                flash(f'📧 Check your inbox: {email}', 'info')
                flash('Didn\'t receive the email? <a href="/register/resend-verification" style="color: #667eea; text-decoration: underline;">Resend verification</a>', 'warning')
                return render_template('admin/login.html', tenant=tenant, email=email)
            
            # Make session permanent (lasts for PERMANENT_SESSION_LIFETIME)
            t2 = time.time()
            
            # Clear any existing session data (prevents flash message accumulation)
            session.clear()
            
            session.permanent = True
            session['tenant_admin_id'] = tenant.id
            session['tenant_subdomain'] = tenant.subdomain
            session['admin_name'] = tenant.admin_name
            
            # Update last login timestamp (for superadmin tracking)
            from datetime import datetime
            tenant.last_login_at = datetime.utcnow()
            db.session.commit()
            
            print(f"3. Update last_login_at: {(time.time() - t2)*1000:.0f}ms")
            print(f"✅ TOTAL LOGIN TIME: {(time.time() - start_time)*1000:.0f}ms\n")
            flash(f'Welcome back, {tenant.admin_name}!', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('admin/login.html', tenant=tenant)

@admin_bp.route('/forgot-password', methods=['GET', 'POST'])
@require_tenant
def forgot_password():
    """
    Step 1: Request password reset (sends email with token)
    SECURE: Only sends email, doesn't reset password immediately
    """
    tenant = get_current_tenant()
    
    if request.method == 'POST':
        email = request.form.get('email')
        
        # Verify email matches tenant admin
        if tenant.admin_email != email:
            # Still show success message (security: don't reveal if email exists)
            flash('✅ If that email is registered, you will receive a password reset link shortly.', 'success')
            return render_template('admin/forgot_password.html')
        
        # Generate secure token
        import secrets
        from datetime import datetime, timedelta
        import pytz
        
        token = secrets.token_urlsafe(32)  # Cryptographically secure random token
        
        # Set expiry (1 hour from now) - use UTC for database storage
        expires_at = datetime.utcnow() + timedelta(hours=1)
        
        # Save token to database (created_at defaults to CURRENT_TIMESTAMP in UTC)
        insert_token = text("""
            INSERT INTO password_reset_tokens 
            (tenant_id, token, expires_at, used, ip_address)
            VALUES (:tenant_id, :token, :expires_at, FALSE, :ip_address)
        """)
        
        db.session.execute(insert_token, {
            'tenant_id': tenant.id,
            'token': token,
            'expires_at': expires_at,
            'ip_address': request.remote_addr
        })
        db.session.commit()
        
        # Send email with reset link
        from utils.email_utils import send_password_reset_email
        reset_url = f"{request.scheme}://{request.host}/admin/reset-password/{token}"
        
        send_password_reset_email(
            admin_email=tenant.admin_email,
            admin_name=tenant.admin_name,
            company_name=tenant.company_name,
            reset_url=reset_url
        )
        
        flash('✅ If that email is registered, you will receive a password reset link shortly. Check your inbox!', 'success')
        return render_template('admin/forgot_password.html')
    
    return render_template('admin/forgot_password.html')


@admin_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
@require_tenant
def reset_password(token):
    """
    Step 2: Validate token and allow password reset
    SECURE: Checks token validity, expiry, and one-time use
    """
    from datetime import datetime
    import pytz
    from sqlalchemy import text
    
    tenant = get_current_tenant()
    now = datetime.utcnow()  # Use UTC for comparison
    
    # Validate token
    check_token = text("""
        SELECT id, tenant_id, expires_at, used
        FROM password_reset_tokens
        WHERE token = :token AND tenant_id = :tenant_id
    """)
    
    result = db.session.execute(check_token, {
        'token': token,
        'tenant_id': tenant.id
    }).fetchone()
    
    # Check if token exists
    if not result:
        flash('❌ Invalid password reset link. Please request a new one.', 'error')
        return redirect(url_for('admin.forgot_password'))
    
    token_id, token_tenant_id, expires_at, used = result
    
    # Check if token already used
    if used:
        flash('❌ This reset link has already been used. Please request a new one.', 'error')
        return redirect(url_for('admin.forgot_password'))
    
    # Check if token expired (both are naive UTC timestamps)
    if now > expires_at:
        flash('❌ This reset link has expired (valid for 1 hour). Please request a new one.', 'error')
        return redirect(url_for('admin.forgot_password'))
    
    # Token is valid! Show password reset form
    if request.method == 'POST':
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate passwords match
        if new_password != confirm_password:
            flash('Passwords do not match!', 'error')
            return render_template('admin/reset_password.html', token=token)
        
        # Validate password length
        if len(new_password) < 6:
            flash('Password must be at least 6 characters!', 'error')
            return render_template('admin/reset_password.html', token=token)
        
        # Update password
        tenant.admin_password_hash = hashlib.sha256(new_password.encode()).hexdigest()
        
        # Mark token as used
        mark_used = text("""
            UPDATE password_reset_tokens
            SET used = TRUE, used_at = :used_at
            WHERE id = :token_id
        """)
        
        db.session.execute(mark_used, {
            'used_at': datetime.utcnow(),
            'token_id': token_id
        })
        
        db.session.commit()
        
        # Send confirmation email
        from utils.email_utils import send_password_changed_notification
        send_password_changed_notification(
            admin_email=tenant.admin_email,
            admin_name=tenant.admin_name,
            company_name=tenant.company_name
        )
        
        flash('✅ Password reset successful! You can now login with your new password.', 'success')
        return redirect(url_for('admin.login'))
    
    return render_template('admin/reset_password.html', token=token)

@admin_bp.route('/logout')
def logout():
    """Logout"""
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('admin.login'))


@admin_bp.route('/profile', methods=['GET', 'POST'])
@require_tenant
@login_required
def profile():
    """Admin profile management - Edit email, phone, address, company details"""
    tenant_id = get_current_tenant_id()
    tenant = get_current_tenant()
    
    if request.method == 'POST':
        try:
            # Get form data
            admin_name = request.form.get('admin_name', '').strip()
            admin_email = request.form.get('admin_email', '').strip()
            admin_phone = request.form.get('admin_phone', '').strip()
            company_name = request.form.get('company_name', '').strip()
            company_address = request.form.get('company_address', '').strip()
            company_phone = request.form.get('company_phone', '').strip()
            gstin = request.form.get('gstin', '').strip()
            
            # Password change (optional)
            current_password = request.form.get('current_password', '').strip()
            new_password = request.form.get('new_password', '').strip()
            confirm_password = request.form.get('confirm_password', '').strip()
            
            # Validate required fields
            if not admin_name or not admin_email or not company_name:
                flash('❌ Name, Email, and Company Name are required!', 'error')
                return redirect(url_for('admin.profile'))
            
            # If changing password, validate current password
            if new_password:
                if not current_password:
                    flash('❌ Please enter your current password to change it!', 'error')
                    return redirect(url_for('admin.profile'))
                
                # Verify current password
                current_hash = hashlib.sha256(current_password.encode()).hexdigest()
                if tenant.admin_password_hash != current_hash:
                    flash('❌ Current password is incorrect!', 'error')
                    return redirect(url_for('admin.profile'))
                
                # Validate new passwords match
                if new_password != confirm_password:
                    flash('❌ New passwords do not match!', 'error')
                    return redirect(url_for('admin.profile'))
                
                # Validate password length
                if len(new_password) < 6:
                    flash('❌ New password must be at least 6 characters!', 'error')
                    return redirect(url_for('admin.profile'))
                
                # Update password
                tenant.admin_password_hash = hashlib.sha256(new_password.encode()).hexdigest()
                flash('✅ Password updated successfully!', 'success')
            
            # Update tenant details
            tenant.admin_name = admin_name
            tenant.admin_email = admin_email
            tenant.admin_phone = admin_phone
            tenant.company_name = company_name
            tenant.gstin = gstin if gstin else None
            
            # Update settings JSON with address and company phone
            import json
            settings = json.loads(tenant.settings) if tenant.settings else {}
            settings['company_address'] = company_address
            settings['company_phone'] = company_phone
            tenant.settings = json.dumps(settings)
            
            # Update session with new admin name
            session['admin_name'] = admin_name
            
            db.session.commit()
            flash('✅ Profile updated successfully!', 'success')
            return redirect(url_for('admin.profile'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'❌ Error updating profile: {str(e)}', 'error')
            print(f"Error updating profile: {str(e)}")
            import traceback
            traceback.print_exc()
    
    # GET - Load current settings
    import json
    settings = json.loads(tenant.settings) if tenant.settings else {}
    
    return render_template('admin/profile.html',
                         tenant=tenant,
                         company_address=settings.get('company_address', ''),
                         company_phone=settings.get('company_phone', ''))


@admin_bp.route('/dashboard', strict_slashes=False)
@require_tenant
@login_required
def dashboard():
    """Business dashboard with key metrics - OPTIMIZED + PROFILED"""
    import time
    start_time = time.time()
    
    from models import Invoice, PurchaseBill, Customer, Vendor, Item, ItemStock
    
    tenant_id = get_current_tenant_id()
    tenant = get_current_tenant()
    today = datetime.now()
    
    print(f"\n⏱️  DASHBOARD PERFORMANCE:")
    print(f"1. Imports + tenant: {(time.time() - start_time)*1000:.0f}ms")
    
    # MEGA-OPTIMIZATION: Batch ALL queries into ONE database round trip!
    # This is critical for Vercel (US) + Database (Mumbai) setup
    # Each query = India → US → Mumbai → US → India = 1.6s!
    # Solution: ONE query instead of 9 separate queries!
    
    t_batch = time.time()
    today_start = datetime.combine(today.date(), datetime.min.time())
    today_end = datetime.combine(today.date(), datetime.max.time())
    month_start = datetime(today.year, today.month, 1)
    
    from sqlalchemy import func, text
    
    # Execute ONE mega-query with all stats
    query_sql = text("""
        SELECT 
            -- Today's sales
            (SELECT COALESCE(SUM(total_amount), 0) FROM invoices 
             WHERE tenant_id = :tenant_id 
             AND invoice_date >= :today_start 
             AND invoice_date <= :today_end) as today_sales,
            (SELECT COUNT(*) FROM invoices 
             WHERE tenant_id = :tenant_id 
             AND invoice_date >= :today_start 
             AND invoice_date <= :today_end) as today_invoice_count,
            
            -- Month's sales  
            (SELECT COALESCE(SUM(total_amount), 0) FROM invoices 
             WHERE tenant_id = :tenant_id 
             AND invoice_date >= :month_start) as month_sales,
            (SELECT COUNT(*) FROM invoices 
             WHERE tenant_id = :tenant_id 
             AND invoice_date >= :month_start) as month_invoice_count,
            
            -- Pending receivables
            (SELECT COALESCE(SUM(total_amount), 0) FROM invoices 
             WHERE tenant_id = :tenant_id 
             AND payment_status != 'paid') as pending_receivables,
            
            -- Month's purchases
            (SELECT COALESCE(SUM(total_amount), 0) FROM purchase_bills 
             WHERE tenant_id = :tenant_id 
             AND bill_date >= :month_start 
             AND status = 'approved') as month_purchases,
            (SELECT COUNT(*) FROM purchase_bills 
             WHERE tenant_id = :tenant_id 
             AND bill_date >= :month_start 
             AND status = 'approved') as month_bill_count,
            
            -- Quick stats
            (SELECT COUNT(*) FROM items 
             WHERE tenant_id = :tenant_id 
             AND is_active = true) as total_items,
            (SELECT COUNT(*) FROM customers 
             WHERE tenant_id = :tenant_id 
             AND is_active = true) as total_customers,
            (SELECT COUNT(*) FROM vendors 
             WHERE tenant_id = :tenant_id 
             AND is_active = true) as total_vendors
    """)
    
    result = db.session.execute(query_sql, {
        'tenant_id': tenant_id,
        'today_start': today_start,
        'today_end': today_end,
        'month_start': month_start
    }).fetchone()
    
    # Unpack results
    today_sales = float(result[0] or 0)
    today_invoice_count = int(result[1] or 0)
    month_sales = float(result[2] or 0)
    month_invoice_count = int(result[3] or 0)
    pending_receivables = float(result[4] or 0)
    month_purchases = float(result[5] or 0)
    month_bill_count = int(result[6] or 0)
    total_items = int(result[7] or 0)
    total_customers = int(result[8] or 0)
    total_vendors = int(result[9] or 0)
    
    print(f"2. MEGA-QUERY (all stats): {(time.time() - t_batch)*1000:.0f}ms")
    
    # Low stock query (separate because complex logic)
    t6 = time.time()
    items_with_stock_query = db.session.query(
        Item.id,
        Item.reorder_point,
        func.sum(ItemStock.quantity_available).label('total_stock')
    ).join(
        ItemStock, Item.id == ItemStock.item_id, isouter=True
    ).filter(
        Item.tenant_id == tenant_id,
        Item.is_active == True,
        Item.track_inventory == True,
        Item.reorder_point.isnot(None)
    ).group_by(Item.id, Item.reorder_point).all()
    
    low_stock_items = sum(1 for item in items_with_stock_query if (item.total_stock or 0) < item.reorder_point)
    print(f"3. Low stock query: {(time.time() - t6)*1000:.0f}ms")
    
    # Recent activity (OPTIMIZED: only load essential fields, not full objects)
    t8 = time.time()
    from sqlalchemy import desc
    recent_invoices = db.session.query(
        Invoice.id,
        Invoice.invoice_number,
        Invoice.customer_name,
        Invoice.total_amount,
        Invoice.payment_status,
        Invoice.invoice_date
    ).filter(
        Invoice.tenant_id == tenant_id
    ).order_by(desc(Invoice.created_at)).limit(5).all()
    
    recent_bills = db.session.query(
        PurchaseBill.id,
        PurchaseBill.bill_number,
        PurchaseBill.vendor_name,
        PurchaseBill.total_amount,
        PurchaseBill.payment_status,
        PurchaseBill.bill_date
    ).filter(
        PurchaseBill.tenant_id == tenant_id
    ).order_by(desc(PurchaseBill.created_at)).limit(5).all()
    print(f"4. Recent activity queries: {(time.time() - t8)*1000:.0f}ms")
    
    t9 = time.time()
    html_result = render_template('admin/dashboard_v2.html',
                         tenant=tenant,
                         today=today,
                         today_sales=today_sales,
                         today_invoice_count=today_invoice_count,
                         month_sales=month_sales,
                         month_invoice_count=month_invoice_count,
                         pending_receivables=pending_receivables,
                         month_purchases=month_purchases,
                         month_bill_count=month_bill_count,
                         total_items=total_items,
                         low_stock_count=low_stock_items,
                         total_customers=total_customers,
                         total_vendors=total_vendors,
                         recent_invoices=recent_invoices,
                         recent_bills=recent_bills)
    print(f"5. Render template: {(time.time() - t9)*1000:.0f}ms")
    print(f"✅ TOTAL DASHBOARD TIME: {(time.time() - start_time)*1000:.0f}ms")
    print(f"🎯 IMPROVEMENT: 9 queries → 3 queries (70% fewer round trips!)\n")
    return html_result

# Employees Management
@admin_bp.route('/employees', strict_slashes=False)  # PERFORMANCE: Prevent 308 redirects
@require_tenant
@login_required
def employees():
    """Manage employees"""
    from models import CommissionAgent
    
    tenant_id = get_current_tenant_id()
    employees = Employee.query.filter_by(tenant_id=tenant_id).all()
    sites = Site.query.filter_by(tenant_id=tenant_id, active=True).all()
    
    # Fetch commission agents for each employee
    commission_agents = {}
    for emp in employees:
        agent = CommissionAgent.query.filter_by(tenant_id=tenant_id, employee_id=emp.id, is_active=True).first()
        if agent:
            commission_agents[emp.id] = agent
    
    return render_template('admin/employees.html', 
                         employees=employees, 
                         sites=sites, 
                         commission_agents=commission_agents,
                         tenant=g.tenant)

@admin_bp.route('/employee/add', methods=['POST'])
@require_tenant
@login_required
def add_employee():
    """Add new employee"""
    from models import CommissionAgent
    
    tenant_id = get_current_tenant_id()
    name = request.form.get('name')
    pin = request.form.get('pin')
    phone = request.form.get('phone')
    email = request.form.get('email')  # NEW: Email for purchase request notifications
    site_id = request.form.get('site_id')
    enable_commission = request.form.get('enable_commission') == '1'  # NEW: Commission checkbox
    commission_percentage = request.form.get('commission_percentage')  # NEW: Commission %
    
    # PAYROLL FIELDS
    monthly_salary = request.form.get('monthly_salary')
    designation = request.form.get('designation')
    date_of_joining = request.form.get('date_of_joining')
    
    # Convert empty string to None for site_id (PostgreSQL requirement)
    if site_id == '' or not site_id:
        site_id = None
    else:
        site_id = int(site_id)
    
    # Check if PIN already exists (within this tenant)
    existing = Employee.query.filter_by(tenant_id=tenant_id, pin=pin).first()
    if existing:
        flash('PIN already exists!', 'error')
        return redirect(url_for('admin.employees'))
    
    employee = Employee(
        tenant_id=tenant_id, 
        name=name, 
        pin=pin, 
        phone=phone, 
        email=email, 
        site_id=site_id,
        monthly_salary=float(monthly_salary) if monthly_salary else None,
        designation=designation if designation else None,
        date_of_joining=date_of_joining if date_of_joining else None
    )
    
    # Handle document upload (Aadhar, etc.)
    if 'document' in request.files:
        file = request.files['document']
        if file and file.filename:
            from utils.helpers import save_uploaded_file
            filename = save_uploaded_file(file, 'uploads/documents')
            if filename:
                employee.document_path = filename
    
    db.session.add(employee)
    db.session.commit()
    
    # Create Commission Agent if enabled
    if enable_commission:
        try:
            commission_rate = float(commission_percentage) if commission_percentage else 1.0
            agent = CommissionAgent(
                tenant_id=tenant_id,
                name=name,
                code=f"EMP-{pin}",  # Auto-generate code from PIN
                phone=phone,
                email=email,
                default_commission_percentage=commission_rate,
                employee_id=employee.id,
                agent_type='employee',
                is_active=True,
                created_by=g.user.id if hasattr(g, 'user') else None
            )
            db.session.add(agent)
            db.session.commit()
            flash(f'✅ Employee {name} added with {commission_rate}% commission!', 'success')
        except Exception as e:
            print(f"❌ Error creating commission agent: {str(e)}")
            flash(f'⚠️ Employee added but commission setup failed: {str(e)}', 'warning')
    else:
        flash(f'Employee {name} added successfully!', 'success')
    
    return redirect(url_for('admin.employees'))

@admin_bp.route('/employee/edit/<int:emp_id>', methods=['POST'])
@require_tenant
@login_required
def edit_employee(emp_id):
    """Edit employee details"""
    from models import CommissionAgent
    
    tenant_id = get_current_tenant_id()
    employee = Employee.query.filter_by(tenant_id=tenant_id, id=emp_id).first_or_404()
    
    # Update employee details
    new_pin = request.form.get('pin')
    
    # Check if new PIN is different and already exists (within this tenant)
    if new_pin != employee.pin:
        existing = Employee.query.filter_by(tenant_id=tenant_id, pin=new_pin).first()
        if existing:
            flash('PIN already exists!', 'error')
            return redirect(url_for('admin.employees'))
    
    employee.name = request.form.get('name')
    employee.pin = new_pin
    employee.phone = request.form.get('phone')
    employee.email = request.form.get('email')
    
    # PAYROLL FIELDS
    monthly_salary = request.form.get('monthly_salary')
    designation = request.form.get('designation')
    date_of_joining = request.form.get('date_of_joining')
    
    # DEBUG: Print what we received
    print(f"[PAYROLL DEBUG] Received data for {employee.name}:")
    print(f"  - monthly_salary (form): {monthly_salary}")
    print(f"  - designation (form): {designation}")
    print(f"  - date_of_joining (form): {date_of_joining}")
    
    try:
        employee.monthly_salary = float(monthly_salary) if monthly_salary else None
        employee.designation = designation if designation else None
        employee.date_of_joining = date_of_joining if date_of_joining else None
        
        print(f"[PAYROLL DEBUG] Setting employee attributes:")
        print(f"  - employee.monthly_salary: {employee.monthly_salary}")
        print(f"  - employee.designation: {employee.designation}")
        print(f"  - employee.date_of_joining: {employee.date_of_joining}")
    except Exception as e:
        print(f"[PAYROLL ERROR] Failed to set payroll fields: {str(e)}")
        flash(f"⚠️ Warning: Payroll fields may not have been saved: {str(e)}", 'warning')
    
    site_id = request.form.get('site_id')
    if site_id == '' or not site_id:
        employee.site_id = None
    else:
        employee.site_id = int(site_id)
    
    # Update commission if changed
    commission_percentage = request.form.get('commission_percentage')
    commission_agent = CommissionAgent.query.filter_by(tenant_id=tenant_id, employee_id=emp_id).first()
    
    if commission_percentage and float(commission_percentage) > 0:
        # Update or create commission agent
        if commission_agent:
            commission_agent.name = employee.name
            commission_agent.phone = employee.phone
            commission_agent.email = employee.email
            commission_agent.default_commission_percentage = float(commission_percentage)
            commission_agent.is_active = True
        else:
            # Create new commission agent
            agent = CommissionAgent(
                tenant_id=tenant_id,
                name=employee.name,
                code=f"EMP-{employee.pin}",
                phone=employee.phone,
                email=employee.email,
                default_commission_percentage=float(commission_percentage),
                employee_id=employee.id,
                agent_type='employee',
                is_active=True,
                created_by=g.user.id if hasattr(g, 'user') else None
            )
            db.session.add(agent)
    else:
        # Remove commission if percentage is 0 or empty
        if commission_agent:
            commission_agent.is_active = False
    
    db.session.commit()
    flash(f'✅ Employee "{employee.name}" updated successfully!', 'success')
    return redirect(url_for('admin.employees'))

@admin_bp.route('/employee/delete/<int:emp_id>')
@require_tenant
@login_required
def delete_employee(emp_id):
    """Deactivate employee (keeps records)"""
    tenant_id = get_current_tenant_id()
    employee = Employee.query.filter_by(tenant_id=tenant_id, id=emp_id).first_or_404()
    employee.active = False
    db.session.commit()
    flash('Employee deactivated successfully. All records are preserved.', 'success')
    return redirect(url_for('admin.employees'))

@admin_bp.route('/employee/document/<int:emp_id>')
@require_tenant
@login_required
def view_employee_document(emp_id):
    """View employee document"""
    from flask import send_from_directory, redirect
    import os
    tenant_id = get_current_tenant_id()
    employee = Employee.query.filter_by(tenant_id=tenant_id, id=emp_id).first_or_404()
    
    if employee.document_path:
        # If it's a Blob storage URL (starts with http), redirect to it
        if employee.document_path.startswith('http'):
            return redirect(employee.document_path)
        
        # For local files, serve from the correct directory
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        upload_dir = os.path.join(base_path, 'uploads', 'documents')
        return send_from_directory(upload_dir, employee.document_path)
    else:
        flash('No document found', 'error')
        return redirect(url_for('admin.employees'))

# Commission Agents Management
@admin_bp.route('/commission-agents')
@require_tenant
@login_required
def commission_agents():
    """Manage commission agents (external only - employees managed in employee section)"""
    from models import CommissionAgent
    
    tenant_id = get_current_tenant_id()
    
    # Get all external agents
    external_agents = CommissionAgent.query.filter_by(
        tenant_id=tenant_id,
        agent_type='external'
    ).order_by(CommissionAgent.created_at.desc()).all()
    
    # Get all employee agents (for reference)
    employee_agents = CommissionAgent.query.filter_by(
        tenant_id=tenant_id,
        agent_type='employee',
        is_active=True
    ).order_by(CommissionAgent.name).all()
    
    return render_template('admin/commission_agents.html',
                         external_agents=external_agents,
                         employee_agents=employee_agents,
                         tenant=g.tenant)

@admin_bp.route('/commission-agent/add', methods=['POST'])
@require_tenant
@login_required
def add_commission_agent():
    """Add external commission agent"""
    from models import CommissionAgent
    
    tenant_id = get_current_tenant_id()
    name = request.form.get('name')
    code = request.form.get('code')  # Optional unique code
    phone = request.form.get('phone')
    email = request.form.get('email')
    commission_percentage = request.form.get('commission_percentage')
    
    # Validate commission percentage
    try:
        commission_rate = float(commission_percentage) if commission_percentage else 1.0
    except:
        flash('Invalid commission percentage!', 'error')
        return redirect(url_for('admin.commission_agents'))
    
    # Check if code already exists (if provided)
    if code and code.strip():
        existing = CommissionAgent.query.filter_by(tenant_id=tenant_id, code=code).first()
        if existing:
            flash('Agent code already exists!', 'error')
            return redirect(url_for('admin.commission_agents'))
    
    # Create external agent
    agent = CommissionAgent(
        tenant_id=tenant_id,
        name=name,
        code=code if code and code.strip() else None,
        phone=phone,
        email=email,
        default_commission_percentage=commission_rate,
        employee_id=None,  # External agents don't link to employees
        agent_type='external',
        is_active=True,
        created_by=g.user.id if hasattr(g, 'user') else None
    )
    
    db.session.add(agent)
    db.session.commit()
    
    flash(f'✅ External agent "{name}" added with {commission_rate}% commission!', 'success')
    return redirect(url_for('admin.commission_agents'))

@admin_bp.route('/commission-agent/edit/<int:agent_id>', methods=['POST'])
@require_tenant
@login_required
def edit_commission_agent(agent_id):
    """Edit external commission agent"""
    from models import CommissionAgent
    
    tenant_id = get_current_tenant_id()
    agent = CommissionAgent.query.filter_by(tenant_id=tenant_id, id=agent_id).first_or_404()
    
    # Only allow editing of external agents from this page
    if agent.agent_type == 'employee':
        flash('⚠️ Employee agents must be managed from the Employee page.', 'warning')
        return redirect(url_for('admin.commission_agents'))
    
    # Update agent details
    new_code = request.form.get('code')
    
    # Check if new code is different and already exists (within this tenant)
    if new_code and new_code.strip() and new_code != agent.code:
        existing = CommissionAgent.query.filter_by(tenant_id=tenant_id, code=new_code).first()
        if existing:
            flash('Agent code already exists!', 'error')
            return redirect(url_for('admin.commission_agents'))
    
    agent.name = request.form.get('name')
    agent.code = new_code if new_code and new_code.strip() else None
    agent.phone = request.form.get('phone')
    agent.email = request.form.get('email')
    agent.default_commission_percentage = float(request.form.get('commission_percentage'))
    
    db.session.commit()
    
    flash(f'✅ Agent "{agent.name}" updated successfully!', 'success')
    return redirect(url_for('admin.commission_agents'))

@admin_bp.route('/commission-agent/delete/<int:agent_id>', methods=['POST'])
@require_tenant
@login_required
def delete_commission_agent(agent_id):
    """Deactivate commission agent (keeps records)"""
    from models import CommissionAgent
    
    tenant_id = get_current_tenant_id()
    agent = CommissionAgent.query.filter_by(tenant_id=tenant_id, id=agent_id).first_or_404()
    
    # Only allow deletion of external agents from this page
    if agent.agent_type == 'employee':
        flash('⚠️ Employee agents must be managed from the Employee page.', 'warning')
        return redirect(url_for('admin.commission_agents'))
    
    agent.is_active = False
    db.session.commit()
    
    flash(f'Agent "{agent.name}" deactivated successfully. All records are preserved.', 'success')
    return redirect(url_for('admin.commission_agents'))

# Commission Reports
@admin_bp.route('/commission-reports')
@require_tenant
@login_required
def commission_reports():
    """Commission reports and payment tracking"""
    from models import CommissionAgent, InvoiceCommission, Invoice
    from sqlalchemy import func
    from datetime import datetime, timedelta
    
    tenant_id = get_current_tenant_id()
    
    # Get date filters (default: current month)
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    agent_filter = request.args.get('agent_id')
    status_filter = request.args.get('status')  # 'paid', 'unpaid', or 'all'
    
    # Default to current month
    if not start_date_str:
        start_date = datetime.now().replace(day=1).date()
    else:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
    
    if not end_date_str:
        end_date = datetime.now().date()
    else:
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
    
    # Build query
    query = InvoiceCommission.query.filter_by(tenant_id=tenant_id)
    
    # Join with Invoice to get invoice_date for filtering
    query = query.join(Invoice, InvoiceCommission.invoice_id == Invoice.id)
    query = query.filter(Invoice.invoice_date >= start_date, Invoice.invoice_date <= end_date)
    
    # Apply filters
    if agent_filter and agent_filter != 'all':
        query = query.filter(InvoiceCommission.agent_id == int(agent_filter))
    
    if status_filter == 'paid':
        query = query.filter(InvoiceCommission.is_paid == True)
    elif status_filter == 'unpaid':
        query = query.filter(InvoiceCommission.is_paid == False)
    
    # Get all commissions
    commissions = query.order_by(Invoice.invoice_date.desc()).all()
    
    # Calculate summary stats (will be recalculated after agent_summary is built)
    total_earned = sum(c.commission_amount for c in commissions)
    total_returns = 0
    total_net = 0
    total_paid = 0
    total_unpaid = 0
    
    # Agent-wise summary with EARNED, RETURNS, NET, PAID calculations
    agent_summary = {}
    for comm in commissions:
        if comm.agent_id not in agent_summary:
            agent_summary[comm.agent_id] = {
                'agent_name': comm.agent_name,
                'agent_code': comm.agent_code,
                'earned': 0,  # Total commission earned from invoices
                'returns': 0,  # Commission lost due to returns
                'net': 0,      # earned - returns
                'paid': 0,     # Actually paid amount (from commission_payments table)
                'unpaid': 0,   # net - paid
                'count': 0
            }
        agent_summary[comm.agent_id]['earned'] += comm.commission_amount
        agent_summary[comm.agent_id]['count'] += 1
    
    # Calculate RETURNS (commission reversals) for each agent
    from sqlalchemy import text
    from decimal import Decimal
    
    # For each agent in the summary, calculate their returns in the date range
    for agent_id in agent_summary:
        agent_name = agent_summary[agent_id]['agent_name']
        
        # Query returns for this specific agent
        returns_result = db.session.execute(text("""
            SELECT COALESCE(SUM(credit_amount), 0) as total_returns
            FROM account_transactions
            WHERE tenant_id = :tenant_id
            AND transaction_type = 'commission_reversal'
            AND reference_type = 'return'
            AND narration LIKE :agent_pattern
            AND transaction_date >= :start_date
            AND transaction_date <= :end_date
        """), {
            'tenant_id': tenant_id,
            'agent_pattern': f'%{agent_name}%',
            'start_date': start_date,
            'end_date': end_date
        }).fetchone()
        
        if returns_result:
            agent_summary[agent_id]['returns'] = float(returns_result.total_returns or 0)
    
    # Calculate PAID (from commission_payments table)
    for agent_id in agent_summary:
        paid_result = db.session.execute(text("""
            SELECT COALESCE(SUM(amount), 0) as total_paid
            FROM commission_payments
            WHERE tenant_id = :tenant_id
            AND agent_id = :agent_id
            AND payment_date >= :start_date
            AND payment_date <= :end_date
        """), {
            'tenant_id': tenant_id,
            'agent_id': agent_id,
            'start_date': start_date,
            'end_date': end_date
        }).fetchone()
        
        if paid_result:
            agent_summary[agent_id]['paid'] = float(paid_result.total_paid or 0)
    
    # Calculate NET and UNPAID for each agent
    for agent_id in agent_summary:
        summary = agent_summary[agent_id]
        summary['net'] = summary['earned'] - summary['returns']
        summary['unpaid'] = summary['net'] - summary['paid']
        
        # Round to whole numbers (as per business logic)
        summary['earned'] = round(summary['earned'])
        summary['returns'] = round(summary['returns'])
        summary['net'] = round(summary['net'])
        summary['paid'] = round(summary['paid'])
        summary['unpaid'] = round(summary['unpaid'])
        
        # Add to overall totals
        total_returns += summary['returns']
        total_net += summary['net']
        total_paid += summary['paid']
        total_unpaid += summary['unpaid']
    
    # Get all active agents for filter dropdown
    all_agents = CommissionAgent.query.filter_by(tenant_id=tenant_id, is_active=True).order_by(CommissionAgent.name).all()
    
    # Get active accounts for payment selection
    from models import BankAccount
    # Separate cash and bank accounts
    cash_accounts = BankAccount.query.filter_by(
        tenant_id=tenant_id, 
        is_active=True,
        account_type='cash'
    ).order_by(BankAccount.account_name).all()
    
    bank_accounts = BankAccount.query.filter(
        BankAccount.tenant_id == tenant_id,
        BankAccount.is_active == True,
        BankAccount.account_type.in_(['bank', 'savings', 'current', 'overdraft'])
    ).order_by(BankAccount.account_name).all()
    
    from datetime import date
    return render_template('admin/commission_reports.html',
                         tenant=g.tenant,
                         commissions=commissions,
                         agent_summary=agent_summary,
                         all_agents=all_agents,
                         cash_accounts=cash_accounts,
                         bank_accounts=bank_accounts,
                         total_earned=total_earned,
                         total_returns=total_returns,
                         total_net=total_net,
                         total_paid=total_paid,
                         total_unpaid=total_unpaid,
                         start_date=start_date,
                         end_date=end_date,
                         selected_agent=agent_filter,
                         selected_status=status_filter or 'all',
                         today=date.today().strftime('%Y-%m-%d'))

@admin_bp.route('/commission/mark-paid/<int:commission_id>', methods=['POST'])
@require_tenant
@login_required
def mark_commission_paid(commission_id):
    """Mark commission as paid with double-entry accounting"""
    from models import InvoiceCommission, BankAccount
    from datetime import date
    from sqlalchemy import text
    import pytz
    
    tenant_id = get_current_tenant_id()
    commission = InvoiceCommission.query.filter_by(tenant_id=tenant_id, id=commission_id).first_or_404()
    
    if commission.is_paid:
        flash('⚠️ Commission is already marked as paid!', 'warning')
        return redirect(url_for('admin.commission_reports'))
    
    payment_date = request.form.get('payment_date')
    account_id = request.form.get('account_id')
    payment_notes = request.form.get('payment_notes')
    
    # Validate account_id
    if not account_id:
        flash('❌ Please select an account for payment!', 'error')
        return redirect(url_for('admin.commission_reports'))
    
    try:
        # Get account details to determine payment method automatically
        account = BankAccount.query.filter_by(id=account_id, tenant_id=tenant_id).first()
        if not account:
            flash('❌ Selected account not found!', 'error')
            return redirect(url_for('admin.commission_reports'))
        
        # Determine payment method based on account type
        payment_method = 'bank' if account.account_type in ['savings', 'current', 'bank'] else 'cash'
        account_name = account.account_name
        
        # Mark as paid
        commission.is_paid = True
        commission.paid_date = datetime.strptime(payment_date, '%Y-%m-%d').date() if payment_date else date.today()
        commission.payment_notes = payment_notes
        
        # ═══════════════════════════════════════════════════════════════════
        # DOUBLE-ENTRY ACCOUNTING FOR COMMISSION PAYMENT
        # ═══════════════════════════════════════════════════════════════════
        # Entry 1: DEBIT Commission Expense (Operating Expense increases)
        # Entry 2: CREDIT Cash/Bank (Asset decreases - money goes out)
        # ═══════════════════════════════════════════════════════════════════
        
        ist = pytz.timezone('Asia/Kolkata')
        now = datetime.now(ist)
        
        # Entry 1: DEBIT Commission Expense (Operating Expense)
        # NOTE: account_id is NULL for expense entries - they don't belong to a specific bank/cash account
        db.session.execute(text("""
            INSERT INTO account_transactions
            (tenant_id, account_id, transaction_date, transaction_type,
             debit_amount, credit_amount, balance_after, reference_type, reference_id,
             voucher_number, narration, created_at, created_by)
            VALUES (:tenant_id, NULL, :transaction_date, 'commission_expense',
                    :debit_amount, 0.00, :debit_amount, 'commission_payment', :commission_id,
                    :voucher, :narration, :created_at, NULL)
        """), {
            'tenant_id': tenant_id,
            'transaction_date': commission.paid_date,
            'debit_amount': float(commission.commission_amount),
            'commission_id': commission.id,
            'voucher': f'COMM-{commission.id}',
            'narration': f'Commission paid to {commission.agent_name} for Invoice #{commission.invoice_id}',
            'created_at': now
        })
        
        # Entry 2: CREDIT Cash/Bank (Asset - money out)
        db.session.execute(text("""
            INSERT INTO account_transactions
            (tenant_id, account_id, transaction_date, transaction_type,
             debit_amount, credit_amount, balance_after, reference_type, reference_id,
             voucher_number, narration, created_at, created_by)
            VALUES (:tenant_id, :account_id, :transaction_date, :transaction_type,
                    0.00, :credit_amount, :credit_amount, 'commission_payment', :commission_id,
                    :voucher, :narration, :created_at, NULL)
        """), {
            'tenant_id': tenant_id,
            'account_id': int(account_id),
            'transaction_date': commission.paid_date,
            'transaction_type': 'cash_payment' if payment_method == 'cash' else 'bank_payment',
            'credit_amount': float(commission.commission_amount),
            'commission_id': commission.id,
            'voucher': f'COMM-{commission.id}',
            'narration': f'Commission payment to {commission.agent_name} via {account_name}',
            'created_at': now
        })
        
        # Update account balance (reduce balance - money going out)
        db.session.execute(text("""
            UPDATE bank_accounts
            SET current_balance = current_balance - :amount,
                updated_at = :updated_at
            WHERE id = :account_id AND tenant_id = :tenant_id
        """), {
            'amount': float(commission.commission_amount),
            'account_id': int(account_id),
            'tenant_id': tenant_id,
            'updated_at': now
        })
        
        db.session.commit()
        
        # Auto-balance Trial Balance for any rounding differences < ₹1
        from utils.accounting_helpers import auto_balance_trial_balance
        from decimal import Decimal
        balance_result = auto_balance_trial_balance(tenant_id, f'COMM-{commission.id}', max_diff=Decimal('1.00'))
        if balance_result.get('adjustment_made'):
            print(f"✅ Auto-balanced: ₹{balance_result.get('adjustment_amount')} adjustment made")
        
        print(f"\n✅ Double-entry for commission payment:")
        print(f"   DEBIT:  Commission Expense  ₹{commission.commission_amount:.2f}")
        print(f"   CREDIT: {account_name}       ₹{commission.commission_amount:.2f}\n")
        
        flash(f'✅ Commission of ₹{commission.commission_amount:.2f} paid to {commission.agent_name}!', 'success')
        return redirect(url_for('admin.commission_reports'))
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error paying commission: {str(e)}")
        import traceback
        traceback.print_exc()
        flash(f'❌ Error paying commission: {str(e)}', 'error')
        return redirect(url_for('admin.commission_reports'))

@admin_bp.route('/commission/mark-unpaid/<int:commission_id>', methods=['POST'])
@require_tenant
@login_required
def mark_commission_unpaid(commission_id):
    """Mark commission as unpaid and reverse accounting entries"""
    from models import InvoiceCommission
    from sqlalchemy import text
    
    tenant_id = get_current_tenant_id()
    commission = InvoiceCommission.query.filter_by(tenant_id=tenant_id, id=commission_id).first_or_404()
    
    if not commission.is_paid:
        flash('⚠️ Commission is already marked as unpaid!', 'warning')
        return redirect(url_for('admin.commission_reports'))
    
    try:
        # Delete related accounting entries
        result = db.session.execute(text("""
            DELETE FROM account_transactions
            WHERE tenant_id = :tenant_id
            AND reference_type = 'commission_payment'
            AND reference_id = :commission_id
        """), {
            'tenant_id': tenant_id,
            'commission_id': commission.id
        })
        
        print(f"🗑️ Deleted {result.rowcount} accounting entries for commission #{commission.id}")
        
        # Mark as unpaid
        commission.is_paid = False
        commission.paid_date = None
        commission.payment_notes = None
        
        db.session.commit()
        
        flash(f'✅ Commission of ₹{commission.commission_amount:.2f} marked as unpaid (accounting entries reversed).', 'success')
        return redirect(url_for('admin.commission_reports'))
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error unmarking commission: {str(e)}")
        import traceback
        traceback.print_exc()
        flash(f'❌ Error unmarking commission: {str(e)}', 'error')
        return redirect(url_for('admin.commission_reports'))


@admin_bp.route('/commission/pay-agent/<int:agent_id>', methods=['POST'])
@require_tenant
@login_required
def pay_agent_commission(agent_id):
    """Pay commission to agent (supports partial payments)"""
    from models import CommissionAgent, BankAccount
    from sqlalchemy import text
    from decimal import Decimal
    from datetime import date, datetime
    import pytz
    
    tenant_id = get_current_tenant_id()
    
    # Get agent
    agent = CommissionAgent.query.filter_by(tenant_id=tenant_id, id=agent_id).first_or_404()
    
    # Get form data
    amount = request.form.get('amount')
    payment_date_str = request.form.get('payment_date')
    account_id = request.form.get('account_id')
    payment_notes = request.form.get('payment_notes')
    
    # Validation
    if not amount or not payment_date_str or not account_id:
        flash('❌ Please fill all required fields!', 'error')
        return redirect(url_for('admin.commission_reports'))
    
    try:
        amount = Decimal(amount)
        if amount <= 0:
            flash('❌ Payment amount must be greater than zero!', 'error')
            return redirect(url_for('admin.commission_reports'))
        
        payment_date = datetime.strptime(payment_date_str, '%Y-%m-%d').date()
        account = BankAccount.query.filter_by(id=int(account_id), tenant_id=tenant_id).first_or_404()
        
        ist = pytz.timezone('Asia/Kolkata')
        now = datetime.now(ist)
        
        # Generate voucher number
        voucher_number = f'COMM-PAY-{agent_id}-{int(now.timestamp())}'
        
        # Insert into commission_payments table
        db.session.execute(text("""
            INSERT INTO commission_payments
            (tenant_id, agent_id, payment_date, amount, account_id, 
             payment_method, voucher_number, payment_notes, created_at)
            VALUES
            (:tenant_id, :agent_id, :payment_date, :amount, :account_id,
             :payment_method, :voucher_number, :notes, :created_at)
        """), {
            'tenant_id': tenant_id,
            'agent_id': agent_id,
            'payment_date': payment_date,
            'amount': float(amount),
            'account_id': int(account_id),
            'payment_method': account.account_type,
            'voucher_number': voucher_number,
            'notes': payment_notes,
            'created_at': now
        })
        
        # ═══════════════════════════════════════════════════════════════════
        # 📊 DOUBLE-ENTRY ACCOUNTING: Commission Payment
        # ═══════════════════════════════════════════════════════════════════
        # When we pay commission to an agent:
        # 1. DEBIT:  Commission Expense (Expense increases)
        # 2. CREDIT: Cash/Bank (Asset decreases - money goes out)
        # ═══════════════════════════════════════════════════════════════════
        
        # Entry 1: DEBIT Commission Expense
        db.session.execute(text("""
            INSERT INTO account_transactions
            (tenant_id, account_id, transaction_date, transaction_type,
             debit_amount, credit_amount, balance_after, reference_type, reference_id,
             voucher_number, narration, created_at, created_by)
            VALUES (:tenant_id, NULL, :transaction_date, :transaction_type,
                    :debit_amount, 0.00, :debit_amount, 'commission_payment', :agent_id,
                    :voucher, :narration, :created_at, NULL)
        """), {
            'tenant_id': tenant_id,
            'transaction_date': payment_date,
            'transaction_type': 'commission_expense',
            'debit_amount': float(amount),
            'agent_id': agent_id,
            'voucher': voucher_number,
            'narration': f'Commission payment to {agent.name}',
            'created_at': now
        })
        
        # Entry 2: CREDIT Cash/Bank (Asset - money out)
        db.session.execute(text("""
            INSERT INTO account_transactions
            (tenant_id, account_id, transaction_date, transaction_type,
             debit_amount, credit_amount, balance_after, reference_type, reference_id,
             voucher_number, narration, created_at, created_by)
            VALUES (:tenant_id, :account_id, :transaction_date, :transaction_type,
                    0.00, :credit_amount, :credit_amount, 'commission_payment', :agent_id,
                    :voucher, :narration, :created_at, NULL)
        """), {
            'tenant_id': tenant_id,
            'account_id': int(account_id),
            'transaction_date': payment_date,
            'transaction_type': f'{account.account_type}_payment',
            'credit_amount': float(amount),
            'agent_id': agent_id,
            'voucher': voucher_number,
            'narration': f'Commission payment to {agent.name} via {account.account_name}',
            'created_at': now
        })
        
        # Update account balance (reduce balance - money going out)
        db.session.execute(text("""
            UPDATE bank_accounts
            SET current_balance = current_balance - :amount,
                updated_at = :updated_at
            WHERE id = :account_id AND tenant_id = :tenant_id
        """), {
            'amount': float(amount),
            'account_id': int(account_id),
            'tenant_id': tenant_id,
            'updated_at': now
        })
        
        db.session.commit()
        
        # Auto-balance Trial Balance for any rounding differences < ₹1
        from utils.accounting_helpers import auto_balance_trial_balance
        balance_result = auto_balance_trial_balance(tenant_id, voucher_number, max_diff=Decimal('1.00'))
        if balance_result.get('adjustment_made'):
            print(f"✅ Auto-balanced: ₹{balance_result.get('adjustment_amount')} adjustment made")
        
        print(f"\n✅ Commission payment recorded:")
        print(f"   DEBIT:  Commission Expense  ₹{amount}")
        print(f"   CREDIT: {account.account_name}  ₹{amount}\n")
        
        flash(f'✅ Paid ₹{amount} commission to {agent.name}!', 'success')
        return redirect(url_for('admin.commission_reports'))
        
    except ValueError as e:
        db.session.rollback()
        flash(f'❌ Invalid input: {str(e)}', 'error')
        return redirect(url_for('admin.commission_reports'))
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error paying commission: {str(e)}")
        import traceback
        traceback.print_exc()
        flash(f'❌ Error paying commission: {str(e)}', 'error')
        return redirect(url_for('admin.commission_reports'))


@admin_bp.route('/commission-agent/<int:agent_id>/ledger')
@require_tenant
@login_required
def commission_agent_ledger(agent_id):
    """View commission agent ledger with all transactions"""
    from models import CommissionAgent, InvoiceCommission, Invoice
    from sqlalchemy import text
    from decimal import Decimal
    from datetime import datetime, timedelta
    
    tenant_id = get_current_tenant_id()
    agent = CommissionAgent.query.filter_by(id=agent_id, tenant_id=tenant_id).first_or_404()
    
    # Get date range filters
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    
    # Default to last 3 months if no dates provided
    if not start_date:
        start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
    if not end_date:
        end_date = datetime.now().strftime('%Y-%m-%d')
    
    # Get all commission records for this agent (earned)
    commissions_query = InvoiceCommission.query.join(
        Invoice, InvoiceCommission.invoice_id == Invoice.id
    ).filter(
        InvoiceCommission.tenant_id == tenant_id,
        InvoiceCommission.agent_id == agent_id
    ).filter(
        Invoice.invoice_date >= datetime.strptime(start_date, '%Y-%m-%d').date()
    ).filter(
        Invoice.invoice_date <= datetime.strptime(end_date, '%Y-%m-%d').date()
    ).order_by(Invoice.invoice_date.asc())
    
    commissions = commissions_query.all()
    
    # Get all commission payments from account_transactions (paid)
    payments_result = db.session.execute(text("""
        SELECT 
            at.transaction_date,
            at.debit_amount as amount,
            at.voucher_number,
            at.narration,
            'payment' as type
        FROM account_transactions at
        WHERE at.tenant_id = :tenant_id
        AND at.transaction_type = 'commission_expense'
        AND at.narration LIKE :agent_name
        AND at.transaction_date >= :start_date
        AND at.transaction_date <= :end_date
        ORDER BY at.transaction_date ASC
    """), {
        'tenant_id': tenant_id,
        'agent_name': f'%{agent.name}%',
        'start_date': datetime.strptime(start_date, '%Y-%m-%d').date(),
        'end_date': datetime.strptime(end_date, '%Y-%m-%d').date()
    }).fetchall()
    
    # Get all commission reversals from returns
    reversals_result = db.session.execute(text("""
        SELECT 
            at.transaction_date,
            at.credit_amount as amount,
            at.voucher_number,
            at.narration,
            'reversal' as type
        FROM account_transactions at
        WHERE at.tenant_id = :tenant_id
        AND at.transaction_type = 'commission_reversal'
        AND at.narration LIKE :agent_name
        AND at.transaction_date >= :start_date
        AND at.transaction_date <= :end_date
        ORDER BY at.transaction_date ASC
    """), {
        'tenant_id': tenant_id,
        'agent_name': f'%{agent.name}%',
        'start_date': datetime.strptime(start_date, '%Y-%m-%d').date(),
        'end_date': datetime.strptime(end_date, '%Y-%m-%d').date()
    }).fetchall()
    
    # Combine all transactions
    transactions = []
    
    # Add commission earned entries
    for comm in commissions:
        transactions.append({
            'date': comm.invoice.invoice_date,
            'type': 'earned',
            'reference': comm.invoice.invoice_number,
            'invoice_id': comm.invoice_id,
            'description': f'Commission earned on Invoice {comm.invoice.invoice_number} to {comm.invoice.customer_name}',
            'debit': Decimal(str(comm.commission_amount)),  # Money earned (increase)
            'credit': Decimal('0'),
            'balance': Decimal('0'),  # Will calculate running balance below
            'is_paid': comm.is_paid,
            'paid_date': comm.paid_date
        })
    
    # Add payment entries
    for payment in payments_result:
        transactions.append({
            'date': payment[0],
            'type': 'payment',
            'reference': payment[2],  # voucher_number
            'invoice_id': None,
            'description': payment[3],  # narration
            'debit': Decimal('0'),
            'credit': Decimal(str(payment[1])),  # Money paid (decrease)
            'balance': Decimal('0'),
            'is_paid': True,
            'paid_date': payment[0]
        })
    
    # Add reversal entries
    for reversal in reversals_result:
        transactions.append({
            'date': reversal[0],
            'type': 'reversal',
            'reference': reversal[2],  # voucher_number (return number)
            'invoice_id': None,
            'description': reversal[3],  # narration
            'debit': Decimal('0'),
            'credit': Decimal(str(reversal[1])),  # Commission reversed (decrease)
            'balance': Decimal('0'),
            'is_paid': None,
            'paid_date': None
        })
    
    # Sort all transactions by date
    transactions.sort(key=lambda x: x['date'])
    
    # Calculate running balance
    balance = Decimal('0')
    for txn in transactions:
        balance = balance + txn['debit'] - txn['credit']
        txn['balance'] = balance
    
    # Calculate summary
    total_earned = sum(txn['debit'] for txn in transactions if txn['type'] == 'earned')
    total_paid = sum(txn['credit'] for txn in transactions if txn['type'] == 'payment')
    total_reversed = sum(txn['credit'] for txn in transactions if txn['type'] == 'reversal')
    net_earned = total_earned - total_reversed
    outstanding = net_earned - total_paid
    
    summary = {
        'total_earned': total_earned,
        'total_reversed': total_reversed,
        'net_earned': net_earned,
        'total_paid': total_paid,
        'outstanding': outstanding,
        'status': 'overpaid' if outstanding < 0 else ('outstanding' if outstanding > 0 else 'settled')
    }
    
    return render_template('admin/commission_agent_ledger.html',
                         agent=agent,
                         transactions=transactions,
                         summary=summary,
                         start_date=start_date,
                         end_date=end_date,
                         tenant=g.tenant)


# Sites Management
@admin_bp.route('/sites', strict_slashes=False)  # PERFORMANCE: Prevent 308 redirects
@require_tenant
@login_required
def sites():
    """Manage sites"""
    tenant_id = get_current_tenant_id()
    sites = Site.query.filter_by(tenant_id=tenant_id).all()
    return render_template('admin/sites.html', sites=sites, tenant=g.tenant)

@admin_bp.route('/site/add', methods=['POST'])
@require_tenant
@login_required
def add_site():
    """Add new site"""
    tenant_id = get_current_tenant_id()
    name = request.form.get('name')
    address = request.form.get('address')
    latitude = float(request.form.get('latitude', 0))
    longitude = float(request.form.get('longitude', 0))
    allowed_radius = float(request.form.get('allowed_radius', 100))
    
    site = Site(tenant_id=tenant_id, name=name, address=address, latitude=latitude, longitude=longitude, allowed_radius=allowed_radius)
    db.session.add(site)
    db.session.commit()
    
    flash(f'Site {name} added successfully!', 'success')
    return redirect(url_for('admin.sites'))

@admin_bp.route('/site/edit/<int:site_id>', methods=['GET', 'POST'])
@require_tenant
@login_required
def edit_site(site_id):
    """Edit site details"""
    tenant_id = get_current_tenant_id()
    site = Site.query.filter_by(tenant_id=tenant_id, id=site_id).first_or_404()
    
    if request.method == 'POST':
        site.name = request.form.get('name')
        site.address = request.form.get('address')
        site.latitude = float(request.form.get('latitude', 0))
        site.longitude = float(request.form.get('longitude', 0))
        site.allowed_radius = float(request.form.get('allowed_radius', 100))
        
        db.session.commit()
        flash(f'Site "{site.name}" updated successfully!', 'success')
        return redirect(url_for('admin.sites'))
    
    return render_template('admin/edit_site.html', site=site, tenant=g.tenant)

@admin_bp.route('/site/delete/<int:site_id>', methods=['POST'])
@require_tenant
@login_required
def delete_site(site_id):
    """Delete a site"""
    from models import ItemStock, Stock
    
    tenant_id = get_current_tenant_id()
    site = Site.query.filter_by(tenant_id=tenant_id, id=site_id).first_or_404()
    
    site_name = site.name
    
    # Check if site has inventory (ItemStock - new system)
    item_stock_count = ItemStock.query.filter_by(site_id=site_id).filter(
        ItemStock.quantity_available > 0
    ).count()
    
    # Check if site has materials (Stock - old system)
    material_stock_count = Stock.query.filter_by(site_id=site_id).filter(
        Stock.quantity > 0
    ).count()
    
    if item_stock_count > 0 or material_stock_count > 0:
        flash(
            f'⚠️ Cannot delete site "{site_name}" - it has {item_stock_count + material_stock_count} items with stock! '
            f'Please transfer all stock to another site first using Stock Transfer feature.',
            'warning'
        )
        return redirect(url_for('admin.sites'))
    
    # Check for other dependencies (attendance, tasks, etc.)
    # TODO: Add more dependency checks if needed
    
    try:
        db.session.delete(site)
        db.session.commit()
        flash(f'✅ Site "{site_name}" deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error deleting site: {str(e)}. This site may be referenced by other records.', 'error')
    
    return redirect(url_for('admin.sites'))

@admin_bp.route('/site/set-default/<int:site_id>', methods=['POST'])
@require_tenant
@login_required
def set_default_site(site_id):
    """Set a site as the default site for stock deduction"""
    tenant_id = get_current_tenant_id()
    site = Site.query.filter_by(tenant_id=tenant_id, id=site_id).first_or_404()
    
    # Unset all other sites as default (only one default per tenant)
    Site.query.filter_by(tenant_id=tenant_id).update({'is_default': False})
    
    # Set this site as default
    site.is_default = True
    
    try:
        db.session.commit()
        flash(f'✅ "{site.name}" is now the default site for stock deduction!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error setting default site: {str(e)}', 'error')
    
    return redirect(url_for('admin.sites'))

# Inventory Management
@admin_bp.route('/inventory')
@require_tenant
@login_required
def inventory():
    """Manage inventory"""
    tenant_id = get_current_tenant_id()
    materials = Material.query.filter_by(tenant_id=tenant_id, active=True).all()
    sites = Site.query.filter_by(tenant_id=tenant_id, active=True).all()
    return render_template('admin/inventory.html', materials=materials, sites=sites, tenant=g.tenant)

@admin_bp.route('/material/add', methods=['POST'])
@require_tenant
@login_required
def add_material():
    """Add new material with initial stock"""
    tenant_id = get_current_tenant_id()
    name = request.form.get('name')
    category = request.form.get('category')
    unit = request.form.get('unit', 'nos')
    description = request.form.get('description')
    initial_quantity = float(request.form.get('initial_quantity', 0))
    initial_site_id = request.form.get('site_id')
    
    material = Material(tenant_id=tenant_id, name=name, category=category, unit=unit, description=description)
    db.session.add(material)
    db.session.flush()  # Get material.id
    
    # Create stock records for all active sites (of this tenant)
    sites = Site.query.filter_by(tenant_id=tenant_id, active=True).all()
    for site in sites:
        # Set initial quantity for the selected site, 0 for others
        quantity = initial_quantity if str(site.id) == str(initial_site_id) else 0.0
        stock = Stock(tenant_id=tenant_id, material_id=material.id, site_id=site.id, quantity=quantity)
        db.session.add(stock)
    
    # Record the initial stock movement if quantity > 0
    if initial_quantity > 0:
        movement = StockMovement(
            tenant_id=tenant_id,
            material_id=material.id,
            site_id=initial_site_id,
            type='in',
            quantity=initial_quantity,
            reason='Initial stock'
        )
        db.session.add(movement)
    
    db.session.commit()
    
    flash(f'Material {name} added with {initial_quantity} {unit} at selected site!', 'success')
    return redirect(url_for('admin.inventory'))

@admin_bp.route('/material/edit/<int:material_id>', methods=['GET', 'POST'])
@require_tenant
@login_required
def edit_material(material_id):
    """Edit material details (name, category, unit)"""
    tenant_id = get_current_tenant_id()
    material = Material.query.filter_by(tenant_id=tenant_id, id=material_id).first_or_404()
    
    if request.method == 'POST':
        material.name = request.form.get('name')
        material.category = request.form.get('category')
        material.unit = request.form.get('unit')
        material.description = request.form.get('description')
        
        db.session.commit()
        flash(f'Material "{material.name}" updated successfully!', 'success')
        return redirect(url_for('admin.inventory'))
    
    # GET - show edit form
    sites = Site.query.filter_by(tenant_id=tenant_id, active=True).all()
    return render_template('admin/edit_material.html', material=material, sites=sites, tenant=g.tenant)

@admin_bp.route('/material/delete/<int:material_id>')
@require_tenant
@login_required
def delete_material(material_id):
    """Delete material and all associated records"""
    tenant_id = get_current_tenant_id()
    material = Material.query.filter_by(tenant_id=tenant_id, id=material_id).first_or_404()
    material_name = material.name
    
    # Delete all stock movements (for this tenant's material)
    StockMovement.query.filter_by(tenant_id=tenant_id, material_id=material_id).delete()
    
    # Delete all stock records (for this tenant's material)
    Stock.query.filter_by(tenant_id=tenant_id, material_id=material_id).delete()
    
    # Delete the material
    db.session.delete(material)
    db.session.commit()
    
    flash(f'Material "{material_name}" and all its records deleted successfully!', 'success')
    return redirect(url_for('admin.inventory'))

@admin_bp.route('/stock/update', methods=['POST'])
@require_tenant
@login_required
def update_stock():
    """Update stock (in/out)"""
    tenant_id = get_current_tenant_id()
    material_id = request.form.get('material_id')
    site_id = request.form.get('site_id')
    quantity = float(request.form.get('quantity'))
    action = request.form.get('action')  # 'in' or 'out'
    reason = request.form.get('reason', '')
    
    # Get or create stock record (scoped to tenant)
    stock = Stock.query.filter_by(tenant_id=tenant_id, material_id=material_id, site_id=site_id).first()
    if not stock:
        stock = Stock(tenant_id=tenant_id, material_id=material_id, site_id=site_id, quantity=0)
        db.session.add(stock)
    
    # Update quantity
    if action == 'in':
        stock.quantity += quantity
    else:
        stock.quantity -= quantity
        if stock.quantity < 0:
            stock.quantity = 0
    
    stock.last_updated = datetime.utcnow()
    
    # Record movement
    movement = StockMovement(
        tenant_id=tenant_id,
        material_id=material_id,
        site_id=site_id,
        type=action,
        quantity=quantity,
        reason=reason
    )
    db.session.add(movement)
    db.session.commit()
    
    flash('Stock updated successfully!', 'success')
    return redirect(url_for('admin.inventory'))

@admin_bp.route('/stock/transfer', methods=['POST'])
@require_tenant
@login_required
def transfer_stock():
    """Transfer stock between sites (doesn't affect Total In/Out)"""
    tenant_id = get_current_tenant_id()
    material_id = request.form.get('material_id')
    from_site_id = request.form.get('from_site_id')
    to_site_id = request.form.get('to_site_id')
    quantity = float(request.form.get('quantity'))
    reason = request.form.get('reason', 'Stock transfer')
    
    # Validate different sites
    if from_site_id == to_site_id:
        flash('Cannot transfer to the same site!', 'error')
        return redirect(url_for('admin.inventory'))
    
    # Get source stock
    from_stock = Stock.query.filter_by(tenant_id=tenant_id, material_id=material_id, site_id=from_site_id).first()
    if not from_stock or from_stock.quantity < quantity:
        flash(f'Insufficient stock at source site! Available: {from_stock.quantity if from_stock else 0}', 'error')
        return redirect(url_for('admin.inventory'))
    
    # Get or create destination stock
    to_stock = Stock.query.filter_by(tenant_id=tenant_id, material_id=material_id, site_id=to_site_id).first()
    if not to_stock:
        to_stock = Stock(tenant_id=tenant_id, material_id=material_id, site_id=to_site_id, quantity=0)
        db.session.add(to_stock)
    
    # Update quantities
    from_stock.quantity -= quantity
    to_stock.quantity += quantity
    from_stock.last_updated = datetime.utcnow()
    to_stock.last_updated = datetime.utcnow()
    
    # Record transfer movements (marked with 'transfer_out' and 'transfer_in' types)
    # These won't be counted in Total In/Out
    from_movement = StockMovement(
        tenant_id=tenant_id,
        material_id=material_id,
        site_id=from_site_id,
        type='transfer_out',
        quantity=quantity,
        reason=f"Transfer to {Site.query.get(to_site_id).name}: {reason}"
    )
    
    to_movement = StockMovement(
        tenant_id=tenant_id,
        material_id=material_id,
        site_id=to_site_id,
        type='transfer_in',
        quantity=quantity,
        reason=f"Transfer from {Site.query.get(from_site_id).name}: {reason}"
    )
    
    db.session.add(from_movement)
    db.session.add(to_movement)
    db.session.commit()
    
    material = Material.query.get(material_id)
    from_site = Site.query.get(from_site_id)
    to_site = Site.query.get(to_site_id)
    flash(f'✅ Transferred {quantity} {material.unit} of {material.name} from {from_site.name} to {to_site.name}!', 'success')
    return redirect(url_for('admin.inventory'))

# Attendance Management
@admin_bp.route('/attendance', strict_slashes=False)  # PERFORMANCE: Prevent 308 redirects
@require_tenant
@login_required
def attendance():
    """View all attendance records - Grouped by employee & date"""
    from collections import defaultdict
    import pytz
    
    tenant_id = get_current_tenant_id()
    ist = pytz.timezone('Asia/Kolkata')
    
    # Get all attendance records (for this tenant only)
    all_records = Attendance.query.filter_by(tenant_id=tenant_id).order_by(Attendance.timestamp.desc()).all()
    
    # Group by employee and date
    # Group by employee name only (not by date) for better cross-date pairing
    grouped_by_employee = defaultdict(list)
    for record in all_records:
        grouped_by_employee[record.employee_name].append(record)
    
    # Create pairs (check-in + check-out) - handles cross-midnight shifts
    attendance_pairs = []
    
    for employee_name in sorted(grouped_by_employee.keys()):
        # Sort in chronological order (oldest first) so check-ins are processed before check-outs
        employee_records = sorted(grouped_by_employee[employee_name], key=lambda x: x.timestamp)
        
        processed = set()
        
        for record in employee_records:
            if record.id in processed:
                continue
            
            if record.type == "check_in":
                # Look for the next check-out after this check-in (even if on different date)
                check_out = None
                for potential_checkout in employee_records:
                    if (potential_checkout.type == "check_out" and 
                        potential_checkout.timestamp > record.timestamp and
                        potential_checkout.id not in processed):
                        check_out = potential_checkout
                        break
                
                # Calculate duration (handles cross-day shifts)
                duration = None
                if check_out:
                    diff = check_out.timestamp - record.timestamp
                    total_seconds = diff.days * 86400 + diff.seconds  # Include days in calculation
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                    duration = f"{hours}h {minutes}m"
                    processed.add(check_out.id)
                
                # Mark check-in as processed
                processed.add(record.id)
                
                # Convert timestamps to IST for display
                def to_ist_string(timestamp):
                    if timestamp.tzinfo is None:
                        utc_time = pytz.UTC.localize(timestamp)
                    else:
                        utc_time = timestamp
                    return utc_time.astimezone(ist).strftime("%I:%M %p")
                
                # Get date from check-in for display
                if record.timestamp.tzinfo is None:
                    utc_time = pytz.UTC.localize(record.timestamp)
                else:
                    utc_time = record.timestamp
                ist_time = utc_time.astimezone(ist)
                display_date = ist_time.strftime("%Y-%m-%d")
                
                attendance_pairs.append({
                    'date': display_date,
                    'employee_name': employee_name,
                    'check_in_time': to_ist_string(record.timestamp),
                    'check_in_distance': f"{record.distance:.0f}m",
                    'check_in_photo': record.photo,
                    'check_in_id': record.id,
                    'check_in_comment': record.comment,
                    'check_in_manual': record.manual_entry,
                    'check_out_time': to_ist_string(check_out.timestamp) if check_out else None,
                    'check_out_distance': f"{check_out.distance:.0f}m" if check_out else None,
                    'check_out_photo': check_out.photo if check_out else None,
                    'check_out_id': check_out.id if check_out else None,
                    'check_out_comment': check_out.comment if check_out else None,
                    'check_out_manual': check_out.manual_entry if check_out else False,
                    'duration': duration
                })
            
            elif record.type == "check_out":
                # Orphaned check-out (no matching check-in found)
                processed.add(record.id)
                
                # Convert timestamp to IST
                def to_ist_string(timestamp):
                    if timestamp.tzinfo is None:
                        utc_time = pytz.UTC.localize(timestamp)
                    else:
                        utc_time = timestamp
                    return utc_time.astimezone(ist).strftime("%I:%M %p")
                
                # Get date from check-out for display
                if record.timestamp.tzinfo is None:
                    utc_time = pytz.UTC.localize(record.timestamp)
                else:
                    utc_time = record.timestamp
                ist_time = utc_time.astimezone(ist)
                display_date = ist_time.strftime("%Y-%m-%d")
                
                attendance_pairs.append({
                    'date': display_date,
                    'employee_name': employee_name,
                    'check_in_time': "—",
                    'check_in_distance': "—",
                    'check_in_photo': None,
                    'check_in_id': None,
                    'check_in_comment': None,
                    'check_in_manual': False,
                    'check_out_time': to_ist_string(record.timestamp),
                    'check_out_distance': f"{record.distance:.0f}m",
                    'check_out_photo': record.photo,
                    'check_out_id': record.id,
                    'check_out_comment': record.comment,
                    'check_out_manual': record.manual_entry,
                    'duration': None
                })
    
    # Reverse the list so newest records appear first
    attendance_pairs.reverse()
    
    return render_template('admin/attendance.html', attendance_pairs=attendance_pairs, tenant=g.tenant)

@admin_bp.route('/record/delete/<int:record_id>')
@require_tenant
@login_required
def delete_record(record_id):
    """Delete individual attendance record"""
    tenant_id = get_current_tenant_id()
    record = Attendance.query.filter_by(tenant_id=tenant_id, id=record_id).first_or_404()
    db.session.delete(record)
    db.session.commit()
    flash('Record deleted successfully', 'success')
    return redirect(url_for('admin.attendance'))

@admin_bp.route('/clear_attendance', methods=['POST'])
@require_tenant
@login_required
def clear_attendance():
    """Clear all attendance data (for this tenant only)"""
    tenant_id = get_current_tenant_id()
    Attendance.query.filter_by(tenant_id=tenant_id).delete()
    db.session.commit()
    flash('All attendance data cleared', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/export')
@require_tenant
@login_required
def export_csv():
    """Export attendance to CSV"""
    import csv
    import io
    from flask import Response
    
    tenant_id = get_current_tenant_id()
    records = Attendance.query.filter_by(tenant_id=tenant_id).order_by(Attendance.timestamp).all()
    
    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Date', 'Employee', 'Action', 'Time', 'Distance (m)', 'Comment', 'Manual Entry'])
    
    for record in records:
        writer.writerow([
            record.timestamp.strftime('%Y-%m-%d'),
            record.employee_name,
            record.type.replace('_', ' ').title(),
            record.timestamp.strftime('%H:%M:%S'),
            f"{record.distance:.0f}",
            record.comment or '',
            'Yes' if record.manual_entry else 'No'
        ])
    
    # Create response
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment;filename=attendance_{datetime.now().strftime("%Y%m%d")}.csv'}
    )

@admin_bp.route('/manual_entry', methods=['GET', 'POST'])
@require_tenant
@login_required
def manual_entry():
    """Manual attendance entry"""
    tenant_id = get_current_tenant_id()
    employees = Employee.query.filter_by(tenant_id=tenant_id, active=True).all()
    
    # Get unclosed check-ins for each employee (to show context)
    unclosed_checkins = {}
    for employee in employees:
        last_checkin = Attendance.query.filter(
            Attendance.tenant_id == tenant_id,
            Attendance.employee_id == employee.id,
            Attendance.type == 'check_in'
        ).order_by(Attendance.timestamp.desc()).first()
        
        if last_checkin:
            # Check if there's a checkout after this check-in
            checkout_after = Attendance.query.filter(
                Attendance.tenant_id == tenant_id,
                Attendance.employee_id == employee.id,
                Attendance.type == 'check_out',
                Attendance.timestamp > last_checkin.timestamp
            ).first()
            
            if not checkout_after:
                # This check-in is unclosed
                import pytz
                ist = pytz.timezone('Asia/Kolkata')
                if last_checkin.timestamp.tzinfo is None:
                    utc_time = pytz.UTC.localize(last_checkin.timestamp)
                else:
                    utc_time = last_checkin.timestamp
                ist_time = utc_time.astimezone(ist)
                unclosed_checkins[employee.id] = {
                    'time': ist_time.strftime('%I:%M %p'),
                    'date': ist_time.strftime('%b %d, %Y'),
                    'full_datetime': ist_time
                }
    
    if request.method == 'POST':
        employee_id = request.form.get('employee_id')
        action = request.form.get('action')  # 'check_in' or 'check_out'
        date = request.form.get('date')
        time = request.form.get('time')
        comment = request.form.get('comment', '').strip()
        
        if not employee_id or not action or not date or not time:
            flash('Please fill all required fields', 'error')
            return redirect(url_for('admin.manual_entry'))
        
        employee = Employee.query.get(employee_id)
        if not employee:
            flash('Employee not found', 'error')
            return redirect(url_for('admin.manual_entry'))
        
        # Create timestamp in IST (user enters time in IST, not UTC)
        import pytz
        ist = pytz.timezone('Asia/Kolkata')
        timestamp_str = f"{date} {time}:00"
        naive_timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
        # Localize to IST (tell Python this is IST time, not UTC)
        timestamp = ist.localize(naive_timestamp)
        
        # Create manual attendance record
        attendance = Attendance(
            tenant_id=tenant_id,
            employee_id=employee.id,
            site_id=employee.site_id or 1,
            employee_name=employee.name,
            type=action,
            timestamp=timestamp,
            photo='manual_entry.jpg',
            latitude=0.0,
            longitude=0.0,
            distance=0.0,
            manual_entry=True,
            comment=comment if comment else None
        )
        
        db.session.add(attendance)
        db.session.commit()
        
        action_text = "Check-In" if action == 'check_in' else "Check-Out"
        flash(f'Manual {action_text} added for {employee.name}', 'success')
        return redirect(url_for('admin.attendance'))
    
    return render_template('admin/manual_entry.html', employees=employees, unclosed_checkins=unclosed_checkins, tenant=g.tenant)

# QR Code Generation
@admin_bp.route('/generate_qr')
@require_tenant
@login_required
def generate_qr():
    """Generate QR code for tenant's unified employee portal"""
    import qrcode
    import io
    import base64
    
    tenant = get_current_tenant()
    # Updated to use unified employee portal (provides access to all features)
    employee_portal_url = f"https://{tenant.subdomain}.bizbooks.co.in/employee/login"
    
    # Create QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(employee_portal_url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64 for embedding in HTML
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    
    return render_template('admin/qr_code.html',
                         qr_image=img_base64,
                         url=employee_portal_url,
                         company=tenant.company_name,
                         subdomain=tenant.subdomain,
                         tenant=g.tenant)


# ============================================
# BULK IMPORT ROUTES
# ============================================

@admin_bp.route('/bulk-import')
@require_tenant
@login_required
def bulk_import():
    """Bulk import landing page"""
    from models import Employee, Item, Customer
    from models.subscription import CustomerSubscription
    tenant_id = get_current_tenant_id()
    
    stats = {
        'employees': Employee.query.filter_by(tenant_id=tenant_id).count(),
        'inventory': Item.query.filter_by(tenant_id=tenant_id).count(),
        'customers': Customer.query.filter_by(tenant_id=tenant_id).count(),
        'subscriptions': CustomerSubscription.query.filter_by(tenant_id=tenant_id, status='active').count()
    }
    
    return render_template('admin/bulk_import.html', stats=stats, tenant=g.tenant)


@admin_bp.route('/bulk-import/download/<template_type>')
@require_tenant
@login_required
def download_template(template_type):
    """Download Excel template for bulk import"""
    from flask import send_file
    from utils.excel_import import (
        create_employee_template, 
        create_inventory_template, 
        create_customer_template,
        create_subscription_enrollment_template
    )
    
    tenant_id = get_current_tenant_id()
    
    # Templates that don't need tenant context
    simple_templates = {
        'employees': (create_employee_template, 'BizBooks_Employee_Import_Template.xlsx'),
        'customers': (create_customer_template, 'BizBooks_Customer_Import_Template.xlsx')
    }
    
    # Special case: inventory template needs tenant_id for dynamic attributes (Phase 3)
    if template_type == 'inventory':
        excel_file = create_inventory_template(tenant_id)
        return send_file(
            excel_file,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='BizBooks_Inventory_Import_Template.xlsx'
        )
    
    # Special case: subscription enrollment needs tenant_id for dynamic data
    if template_type == 'subscriptions':
        excel_file = create_subscription_enrollment_template(tenant_id)
        return send_file(
            excel_file,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='BizBooks_Subscription_Enrollment_Template.xlsx'
        )
    
    if template_type not in simple_templates:
        flash('Invalid template type', 'error')
        return redirect(url_for('admin.bulk_import'))
    
    template_func, filename = simple_templates[template_type]
    excel_file = template_func()
    
    return send_file(
        excel_file,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=filename
    )


@admin_bp.route('/bulk-import/upload/<import_type>', methods=['POST'])
@require_tenant
@login_required
def upload_import(import_type):
    """Process bulk import upload"""
    from utils.excel_import import (
        import_employees_from_excel, 
        import_inventory_from_excel, 
        import_customers_from_excel,
        import_subscription_enrollments_from_excel
    )
    
    if 'file' not in request.files:
        flash('⚠️ No file uploaded', 'error')
        return redirect(url_for('admin.bulk_import'))
    
    file = request.files['file']
    
    if file.filename == '':
        flash('⚠️ No file selected', 'error')
        return redirect(url_for('admin.bulk_import'))
    
    if not file.filename.endswith(('.xlsx', '.xls')):
        flash('⚠️ Please upload an Excel file (.xlsx or .xls)', 'error')
        return redirect(url_for('admin.bulk_import'))
    
    tenant_id = get_current_tenant_id()
    
    try:
        if import_type == 'employees':
            success_count, errors = import_employees_from_excel(file, tenant_id)
            entity_name = 'employees'
        elif import_type == 'inventory':
            success_count, errors = import_inventory_from_excel(file, tenant_id)
            entity_name = 'items'
        elif import_type == 'customers':
            success_count, errors = import_customers_from_excel(file, tenant_id)
            entity_name = 'customers'
        elif import_type == 'subscriptions':
            success_count, skipped_count, errors = import_subscription_enrollments_from_excel(file, tenant_id)
            entity_name = 'subscriptions'
            
            # Custom messaging for subscription import
            if success_count > 0:
                flash(f'✅ Successfully enrolled {success_count} customer(s) in subscriptions!', 'success')
            
            if skipped_count > 0:
                flash(f'⏭️ Skipped {skipped_count} duplicate enrollment(s) (already enrolled in same plan)', 'info')
            
            if errors:
                # Filter out SKIPPED messages from error display (they're not real errors)
                real_errors = [e for e in errors if 'SKIPPED' not in e]
                if real_errors:
                    error_msg = f'⚠️ {len(real_errors)} issue(s):<br>' + '<br>'.join(real_errors[:10])
                    if len(real_errors) > 10:
                        error_msg += f'<br>...and {len(real_errors) - 10} more'
                    flash(error_msg, 'warning')
            
            if success_count == 0 and skipped_count == 0 and not errors:
                flash('⚠️ No data to import. Please check your file.', 'warning')
            
            return redirect(url_for('admin.bulk_import'))
        else:
            flash('⚠️ Invalid import type', 'error')
            return redirect(url_for('admin.bulk_import'))
        
        # Show results (for non-subscription imports)
        if success_count > 0:
            flash(f'✅ Successfully imported {success_count} {entity_name}!', 'success')
        
        if errors:
            error_msg = f'⚠️ {len(errors)} errors occurred:<br>' + '<br>'.join(errors[:10])
            if len(errors) > 10:
                error_msg += f'<br>...and {len(errors) - 10} more errors'
            flash(error_msg, 'warning')
        
        if success_count == 0 and not errors:
            flash('⚠️ No data to import. Please check your file.', 'warning')
        
    except Exception as e:
        flash(f'❌ Import failed: {str(e)}', 'error')
    
    return redirect(url_for('admin.bulk_import'))

