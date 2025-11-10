"""
Admin routes - Login, Dashboard, Management
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g, abort
from models import db, User, Employee, Site, Attendance, Material, Stock, StockMovement, Tenant
from datetime import datetime, timedelta
from sqlalchemy import func
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

@admin_bp.route('/login', methods=['GET', 'POST'])
@require_tenant
def login():
    """Tenant admin login page"""
    tenant = get_current_tenant()
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Hash password for comparison
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        # Check if credentials match tenant admin
        if tenant.admin_email == email and tenant.admin_password_hash == password_hash:
            # Check if email is verified
            if not tenant.email_verified:
                flash('⚠️ Please verify your email address before logging in', 'error')
                flash(f'📧 Check your inbox: {email}', 'info')
                flash('Didn\'t receive the email? <a href="/register/resend-verification" style="color: #667eea; text-decoration: underline;">Resend verification</a>', 'warning')
                return render_template('admin/login.html', tenant=tenant, email=email)
            
            # Make session permanent (lasts for PERMANENT_SESSION_LIFETIME)
            session.permanent = True
            session['tenant_admin_id'] = tenant.id
            session['tenant_subdomain'] = tenant.subdomain
            session['admin_name'] = tenant.admin_name
            tenant.last_login_at = datetime.utcnow()
            db.session.commit()
            flash(f'Welcome back, {tenant.admin_name}!', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('admin/login.html', tenant=tenant)

@admin_bp.route('/forgot-password', methods=['GET', 'POST'])
@require_tenant
def forgot_password():
    """Reset password"""
    tenant = get_current_tenant()
    
    if request.method == 'POST':
        email = request.form.get('email')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Verify email matches tenant admin
        if tenant.admin_email != email:
            flash('Email does not match our records for this account', 'error')
            return render_template('admin/forgot_password.html')
        
        # Validate passwords match
        if new_password != confirm_password:
            flash('Passwords do not match!', 'error')
            return render_template('admin/forgot_password.html')
        
        # Validate password length
        if len(new_password) < 6:
            flash('Password must be at least 6 characters!', 'error')
            return render_template('admin/forgot_password.html')
        
        # Update password
        tenant.admin_password_hash = hashlib.sha256(new_password.encode()).hexdigest()
        db.session.commit()
        
        flash('✅ Password reset successful! You can now login with your new password.', 'success')
        return redirect(url_for('admin.login'))
    
    return render_template('admin/forgot_password.html')

@admin_bp.route('/logout')
def logout():
    """Logout"""
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('admin.login'))

@admin_bp.route('/dashboard')
@require_tenant
@login_required
def dashboard():
    """Business dashboard with key metrics"""
    from models import Invoice, PurchaseBill, Customer, Vendor, Item, ItemStock
    
    tenant_id = get_current_tenant_id()
    tenant = get_current_tenant()
    today = datetime.now()
    
    # Today's sales (OPTIMIZED: SQL aggregation, no loading all records!)
    today_start = datetime.combine(today.date(), datetime.min.time())
    today_end = datetime.combine(today.date(), datetime.max.time())
    
    from sqlalchemy import func
    
    today_result = db.session.query(
        func.count(Invoice.id).label('count'),
        func.sum(Invoice.total_amount).label('total')
    ).filter(
        Invoice.tenant_id == tenant_id,
        Invoice.invoice_date >= today_start,
        Invoice.invoice_date <= today_end
    ).first()
    
    today_sales = today_result.total or 0
    today_invoice_count = today_result.count or 0
    
    # This month's sales (OPTIMIZED: SQL aggregation)
    month_start = datetime(today.year, today.month, 1)
    
    month_result = db.session.query(
        func.count(Invoice.id).label('count'),
        func.sum(Invoice.total_amount).label('total')
    ).filter(
        Invoice.tenant_id == tenant_id,
        Invoice.invoice_date >= month_start
    ).first()
    
    month_sales = month_result.total or 0
    month_invoice_count = month_result.count or 0
    
    # Pending receivables (OPTIMIZED: SQL aggregation)
    receivables_result = db.session.query(
        func.sum(Invoice.total_amount).label('total')
    ).filter(
        Invoice.tenant_id == tenant_id,
        Invoice.payment_status != 'paid'
    ).first()
    
    pending_receivables = receivables_result.total or 0
    
    # This month's purchases (OPTIMIZED: SQL aggregation)
    purchases_result = db.session.query(
        func.count(PurchaseBill.id).label('count'),
        func.sum(PurchaseBill.total_amount).label('total')
    ).filter(
        PurchaseBill.tenant_id == tenant_id,
        PurchaseBill.bill_date >= month_start,
        PurchaseBill.status == 'approved'
    ).first()
    
    month_purchases = purchases_result.total or 0
    month_bill_count = purchases_result.count or 0
    
    # Quick stats
    total_items = Item.query.filter_by(tenant_id=tenant_id, is_active=True).count()
    
    # OPTIMIZED: Low stock count using SQL aggregation (ONE query!)
    from sqlalchemy import func
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
    
    total_customers = Customer.query.filter_by(tenant_id=tenant_id, is_active=True).count()
    total_vendors = Vendor.query.filter_by(tenant_id=tenant_id, is_active=True).count()
    
    # Recent activity
    recent_invoices = Invoice.query.filter_by(tenant_id=tenant_id).order_by(
        Invoice.created_at.desc()
    ).limit(5).all()
    
    recent_bills = PurchaseBill.query.filter_by(tenant_id=tenant_id).order_by(
        PurchaseBill.created_at.desc()
    ).limit(5).all()
    
    return render_template('admin/dashboard.html',
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

# Employees Management
@admin_bp.route('/employees')
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
    
    employee = Employee(tenant_id=tenant_id, name=name, pin=pin, phone=phone, email=email, site_id=site_id)
    
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
    
    # Calculate summary stats
    total_commission = sum(c.commission_amount for c in commissions)
    paid_commission = sum(c.commission_amount for c in commissions if c.is_paid)
    unpaid_commission = total_commission - paid_commission
    
    # Agent-wise summary
    agent_summary = {}
    for comm in commissions:
        if comm.agent_id not in agent_summary:
            agent_summary[comm.agent_id] = {
                'agent_name': comm.agent_name,
                'agent_code': comm.agent_code,
                'total': 0,
                'paid': 0,
                'unpaid': 0,
                'count': 0
            }
        agent_summary[comm.agent_id]['total'] += comm.commission_amount
        if comm.is_paid:
            agent_summary[comm.agent_id]['paid'] += comm.commission_amount
        else:
            agent_summary[comm.agent_id]['unpaid'] += comm.commission_amount
        agent_summary[comm.agent_id]['count'] += 1
    
    # Get all active agents for filter dropdown
    all_agents = CommissionAgent.query.filter_by(tenant_id=tenant_id, is_active=True).order_by(CommissionAgent.name).all()
    
    from datetime import date
    return render_template('admin/commission_reports.html',
                         tenant=g.tenant,
                         commissions=commissions,
                         agent_summary=agent_summary,
                         all_agents=all_agents,
                         total_commission=total_commission,
                         paid_commission=paid_commission,
                         unpaid_commission=unpaid_commission,
                         start_date=start_date,
                         end_date=end_date,
                         selected_agent=agent_filter,
                         selected_status=status_filter or 'all',
                         today=date.today().strftime('%Y-%m-%d'))

@admin_bp.route('/commission/mark-paid/<int:commission_id>', methods=['POST'])
@require_tenant
@login_required
def mark_commission_paid(commission_id):
    """Mark commission as paid"""
    from models import InvoiceCommission
    from datetime import date
    
    tenant_id = get_current_tenant_id()
    commission = InvoiceCommission.query.filter_by(tenant_id=tenant_id, id=commission_id).first_or_404()
    
    payment_date = request.form.get('payment_date')
    payment_notes = request.form.get('payment_notes')
    
    commission.is_paid = True
    commission.paid_date = datetime.strptime(payment_date, '%Y-%m-%d').date() if payment_date else date.today()
    commission.payment_notes = payment_notes
    
    db.session.commit()
    
    flash(f'✅ Commission of ₹{commission.commission_amount:.2f} marked as paid to {commission.agent_name}!', 'success')
    return redirect(url_for('admin.commission_reports'))

@admin_bp.route('/commission/mark-unpaid/<int:commission_id>', methods=['POST'])
@require_tenant
@login_required
def mark_commission_unpaid(commission_id):
    """Mark commission as unpaid (undo payment)"""
    from models import InvoiceCommission
    
    tenant_id = get_current_tenant_id()
    commission = InvoiceCommission.query.filter_by(tenant_id=tenant_id, id=commission_id).first_or_404()
    
    commission.is_paid = False
    commission.paid_date = None
    commission.payment_notes = None
    
    db.session.commit()
    
    flash(f'Commission of ₹{commission.commission_amount:.2f} marked as unpaid.', 'success')
    return redirect(url_for('admin.commission_reports'))

# Sites Management
@admin_bp.route('/sites')
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
@admin_bp.route('/attendance')
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
    tenant_id = get_current_tenant_id()
    
    stats = {
        'employees': Employee.query.filter_by(tenant_id=tenant_id).count(),
        'inventory': Item.query.filter_by(tenant_id=tenant_id).count(),
        'customers': Customer.query.filter_by(tenant_id=tenant_id).count()
    }
    
    return render_template('admin/bulk_import.html', stats=stats, tenant=g.tenant)


@admin_bp.route('/bulk-import/download/<template_type>')
@require_tenant
@login_required
def download_template(template_type):
    """Download Excel template for bulk import"""
    from flask import send_file
    from utils.excel_import import create_employee_template, create_inventory_template, create_customer_template
    
    templates = {
        'employees': (create_employee_template, 'BizBooks_Employee_Import_Template.xlsx'),
        'inventory': (create_inventory_template, 'BizBooks_Inventory_Import_Template.xlsx'),
        'customers': (create_customer_template, 'BizBooks_Customer_Import_Template.xlsx')
    }
    
    if template_type not in templates:
        flash('Invalid template type', 'error')
        return redirect(url_for('admin.bulk_import'))
    
    template_func, filename = templates[template_type]
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
    from utils.excel_import import import_employees_from_excel, import_inventory_from_excel, import_customers_from_excel
    
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
        else:
            flash('⚠️ Invalid import type', 'error')
            return redirect(url_for('admin.bulk_import'))
        
        # Show results
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

