"""
Super Admin Routes - View all tenants and their data
"""
from flask import Blueprint, render_template, session, redirect, url_for, request
from models import db, Tenant, Employee, Attendance, Site, Material, Stock
from models import Item, Customer, Vendor, Invoice, PurchaseBill, Expense, Task
from sqlalchemy import func
from datetime import datetime, timedelta

superadmin_bp = Blueprint('superadmin', __name__, url_prefix='/superadmin')

# Super Admin Password (change this to something secure)
SUPERADMIN_PASSWORD = "bizbooks2025"  # TODO: Change this!

def is_superadmin():
    """Check if user is logged in as super admin"""
    return session.get('is_superadmin') == True

@superadmin_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Super admin login"""
    if request.method == 'POST':
        password = request.form.get('password')
        if password == SUPERADMIN_PASSWORD:
            session['is_superadmin'] = True
            return redirect(url_for('superadmin.dashboard'))
        else:
            return render_template('superadmin/login.html', error="Invalid password")
    
    return render_template('superadmin/login.html')

@superadmin_bp.route('/logout')
def logout():
    """Super admin logout"""
    session.pop('is_superadmin', None)
    return redirect(url_for('superadmin.login'))

@superadmin_bp.route('/dashboard')
def dashboard():
    """Super admin dashboard - view all tenants with comprehensive stats"""
    if not is_superadmin():
        return redirect(url_for('superadmin.login'))
    
    # Get all tenants with statistics
    tenants = Tenant.query.order_by(Tenant.created_at.desc()).all()
    
    tenant_stats = []
    total_stats = {
        'items': 0,
        'customers': 0,
        'vendors': 0,
        'invoices': 0,
        'purchase_bills': 0,
        'expenses': 0,
        'tasks': 0
    }
    
    for tenant in tenants:
        # Existing counts
        employee_count = Employee.query.filter_by(tenant_id=tenant.id).count()
        attendance_count = Attendance.query.filter_by(tenant_id=tenant.id).count()
        site_count = Site.query.filter_by(tenant_id=tenant.id).count()
        material_count = Material.query.filter_by(tenant_id=tenant.id).count()
        
        # NEW counts for business activity
        item_count = Item.query.filter_by(tenant_id=tenant.id).count()
        customer_count = Customer.query.filter_by(tenant_id=tenant.id).count()
        vendor_count = Vendor.query.filter_by(tenant_id=tenant.id).count()
        invoice_count = Invoice.query.filter_by(tenant_id=tenant.id).count()
        purchase_bill_count = PurchaseBill.query.filter_by(tenant_id=tenant.id).count()
        expense_count = Expense.query.filter_by(tenant_id=tenant.id).count()
        task_count = Task.query.filter_by(tenant_id=tenant.id).count()
        
        # Calculate total sales value (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_sales = db.session.query(func.sum(Invoice.total_amount)).filter(
            Invoice.tenant_id == tenant.id,
            Invoice.invoice_date >= thirty_days_ago
        ).scalar() or 0
        
        # Calculate total expenses (last 30 days)
        recent_expenses = db.session.query(func.sum(Expense.amount)).filter(
            Expense.tenant_id == tenant.id,
            Expense.expense_date >= thirty_days_ago
        ).scalar() or 0
        
        # Get last activity timestamp
        last_attendance = Attendance.query.filter_by(tenant_id=tenant.id).order_by(Attendance.timestamp.desc()).first()
        last_invoice = Invoice.query.filter_by(tenant_id=tenant.id).order_by(Invoice.created_at.desc()).first()
        last_expense = Expense.query.filter_by(tenant_id=tenant.id).order_by(Expense.created_at.desc()).first()
        
        activity_timestamps = [
            last_attendance.timestamp if last_attendance else None,
            last_invoice.created_at if last_invoice else None,
            last_expense.created_at if last_expense else None
        ]
        activity_timestamps = [ts for ts in activity_timestamps if ts]
        last_activity = max(activity_timestamps) if activity_timestamps else None
        
        # Add to totals
        total_stats['items'] += item_count
        total_stats['customers'] += customer_count
        total_stats['vendors'] += vendor_count
        total_stats['invoices'] += invoice_count
        total_stats['purchase_bills'] += purchase_bill_count
        total_stats['expenses'] += expense_count
        total_stats['tasks'] += task_count
        
        tenant_stats.append({
            'tenant': tenant,
            'employee_count': employee_count,
            'attendance_count': attendance_count,
            'site_count': site_count,
            'material_count': material_count,
            'item_count': item_count,
            'customer_count': customer_count,
            'vendor_count': vendor_count,
            'invoice_count': invoice_count,
            'purchase_bill_count': purchase_bill_count,
            'expense_count': expense_count,
            'task_count': task_count,
            'recent_sales': recent_sales,
            'recent_expenses': recent_expenses,
            'last_activity': last_activity
        })
    
    return render_template('superadmin/dashboard.html', 
                         tenant_stats=tenant_stats, 
                         total_tenants=len(tenants),
                         total_stats=total_stats,
                         now=datetime.utcnow())

@superadmin_bp.route('/tenant/<int:tenant_id>')
def view_tenant(tenant_id):
    """View detailed data for a specific tenant - comprehensive monitoring"""
    if not is_superadmin():
        return redirect(url_for('superadmin.login'))
    
    tenant = Tenant.query.get_or_404(tenant_id)
    
    # Original data
    employees = Employee.query.filter_by(tenant_id=tenant_id).all()
    attendance = Attendance.query.filter_by(tenant_id=tenant_id).order_by(Attendance.timestamp.desc()).limit(50).all()
    sites = Site.query.filter_by(tenant_id=tenant_id).all()
    materials = Material.query.filter_by(tenant_id=tenant_id).all()
    
    # NEW: Business activity data
    items = Item.query.filter_by(tenant_id=tenant_id).order_by(Item.created_at.desc()).limit(20).all()
    customers = Customer.query.filter_by(tenant_id=tenant_id).order_by(Customer.created_at.desc()).limit(10).all()
    vendors = Vendor.query.filter_by(tenant_id=tenant_id).order_by(Vendor.created_at.desc()).limit(10).all()
    invoices = Invoice.query.filter_by(tenant_id=tenant_id).order_by(Invoice.created_at.desc()).limit(20).all()
    purchase_bills = PurchaseBill.query.filter_by(tenant_id=tenant_id).order_by(PurchaseBill.created_at.desc()).limit(20).all()
    expenses = Expense.query.filter_by(tenant_id=tenant_id).order_by(Expense.created_at.desc()).limit(20).all()
    tasks = Task.query.filter_by(tenant_id=tenant_id).order_by(Task.created_at.desc()).limit(10).all()
    
    # Calculate summary stats
    total_sales = db.session.query(func.sum(Invoice.total_amount)).filter(
        Invoice.tenant_id == tenant_id
    ).scalar() or 0
    
    total_purchases = db.session.query(func.sum(PurchaseBill.total_amount)).filter(
        PurchaseBill.tenant_id == tenant_id
    ).scalar() or 0
    
    total_expenses_amount = db.session.query(func.sum(Expense.amount)).filter(
        Expense.tenant_id == tenant_id
    ).scalar() or 0
    
    return render_template('superadmin/tenant_detail.html', 
                         tenant=tenant,
                         employees=employees,
                         attendance=attendance,
                         sites=sites,
                         materials=materials,
                         items=items,
                         customers=customers,
                         vendors=vendors,
                         invoices=invoices,
                         purchase_bills=purchase_bills,
                         expenses=expenses,
                         tasks=tasks,
                         total_sales=total_sales,
                         total_purchases=total_purchases,
                         total_expenses_amount=total_expenses_amount)

@superadmin_bp.route('/tenant/<int:tenant_id>/delete', methods=['POST'])
def delete_tenant(tenant_id):
    """Delete a tenant and all their data (including Blob storage files)"""
    if not is_superadmin():
        return redirect(url_for('superadmin.login'))
    
    import os
    tenant = Tenant.query.get_or_404(tenant_id)
    company_name = tenant.company_name
    
    # Step 1: Delete Vercel Blob files (if deployed on Vercel)
    deleted_files = 0
    if os.environ.get('VERCEL'):
        import requests
        blob_token = os.environ.get('BLOB_READ_WRITE_TOKEN')
        
        if blob_token:
            # Delete attendance photos
            attendance_records = Attendance.query.filter_by(tenant_id=tenant_id).all()
            for record in attendance_records:
                if record.photo and record.photo.startswith('http'):
                    # It's a Blob URL, delete it
                    try:
                        response = requests.delete(
                            record.photo,
                            headers={'Authorization': f'Bearer {blob_token}'}
                        )
                        if response.status_code == 200:
                            deleted_files += 1
                    except Exception as e:
                        print(f"Failed to delete blob {record.photo}: {e}")
            
            # Delete employee documents
            employees = Employee.query.filter_by(tenant_id=tenant_id).all()
            for employee in employees:
                if employee.document_path and employee.document_path.startswith('http'):
                    # It's a Blob URL, delete it
                    try:
                        response = requests.delete(
                            employee.document_path,
                            headers={'Authorization': f'Bearer {blob_token}'}
                        )
                        if response.status_code == 200:
                            deleted_files += 1
                    except Exception as e:
                        print(f"Failed to delete blob {employee.document_path}: {e}")
            
            # Delete task media (photos/videos from task updates)
            from models import Task, TaskMedia
            tasks = Task.query.filter_by(tenant_id=tenant_id).all()
            for task in tasks:
                for media in task.media:
                    if media.file_path and media.file_path.startswith('http'):
                        # It's a Blob URL, delete it
                        try:
                            response = requests.delete(
                                media.file_path,
                                headers={'Authorization': f'Bearer {blob_token}'}
                            )
                            if response.status_code == 200:
                                deleted_files += 1
                        except Exception as e:
                            print(f"Failed to delete blob {media.file_path}: {e}")
    else:
        # Local development: Delete files from filesystem
        import os as os_module
        
        # Delete attendance photos
        attendance_records = Attendance.query.filter_by(tenant_id=tenant_id).all()
        for record in attendance_records:
            if record.photo and not record.photo.startswith('http') and record.photo != 'manual_entry.jpg':
                photo_path = os_module.path.join(os_module.path.dirname(os_module.path.abspath(__file__)), '..', 'uploads', 'selfies', record.photo)
                if os_module.path.exists(photo_path):
                    try:
                        os_module.remove(photo_path)
                        deleted_files += 1
                    except Exception as e:
                        print(f"Failed to delete file {photo_path}: {e}")
        
        # Delete employee documents
        employees = Employee.query.filter_by(tenant_id=tenant_id).all()
        for employee in employees:
            if employee.document_path and not employee.document_path.startswith('http'):
                doc_path = os_module.path.join(os_module.path.dirname(os_module.path.abspath(__file__)), '..', 'uploads', 'documents', employee.document_path)
                if os_module.path.exists(doc_path):
                    try:
                        os_module.remove(doc_path)
                        deleted_files += 1
                    except Exception as e:
                        print(f"Failed to delete file {doc_path}: {e}")
        
        # Delete task media (photos/videos from task updates)
        from models import Task, TaskMedia
        tasks = Task.query.filter_by(tenant_id=tenant_id).all()
        for task in tasks:
            for media in task.media:
                if media.file_path and not media.file_path.startswith('http'):
                    media_path = os_module.path.join(os_module.path.dirname(os_module.path.abspath(__file__)), '..', 'uploads', 'task_media', media.file_path)
                    if os_module.path.exists(media_path):
                        try:
                            os_module.remove(media_path)
                            deleted_files += 1
                        except Exception as e:
                            print(f"Failed to delete file {media_path}: {e}")
    
    # Step 2: Delete the tenant
    # ✅ CASCADE DELETE handles all related data automatically!
    # All relationships in Tenant model have cascade='all, delete-orphan'
    # This deletes: items, customers, invoices, employees, sites, tasks, etc.
    # No need for manual deletion anymore!
    
    db.session.delete(tenant)
    db.session.commit()
    
    from flask import flash
    if deleted_files > 0:
        flash(f'✅ Deleted {company_name} and all their data ({deleted_files} files removed from storage)', 'success')
    else:
        flash(f'✅ Deleted {company_name} and all their data', 'success')
    return redirect(url_for('superadmin.dashboard'))

@superadmin_bp.route('/tenant/<int:tenant_id>/extend-trial', methods=['POST'])
def extend_trial(tenant_id):
    """Extend trial by 30 days"""
    if not is_superadmin():
        return redirect(url_for('superadmin.login'))
    
    from datetime import datetime, timedelta
    tenant = Tenant.query.get_or_404(tenant_id)
    
    # Extend trial by 30 days
    if tenant.trial_ends_at < datetime.utcnow():
        # Already expired, extend from now
        tenant.trial_ends_at = datetime.utcnow() + timedelta(days=30)
    else:
        # Still active, extend from current end date
        tenant.trial_ends_at = tenant.trial_ends_at + timedelta(days=30)
    
    db.session.commit()
    
    from flask import flash
    flash(f'✅ Extended trial for {tenant.company_name} by 30 days', 'success')
    return redirect(url_for('superadmin.view_tenant', tenant_id=tenant_id))

@superadmin_bp.route('/tenant/<int:tenant_id>/activate', methods=['POST'])
def activate_tenant(tenant_id):
    """Activate tenant (unlimited access)"""
    if not is_superadmin():
        return redirect(url_for('superadmin.login'))
    
    from datetime import datetime, timedelta
    tenant = Tenant.query.get_or_404(tenant_id)
    
    tenant.status = 'active'
    tenant.plan = 'pro'
    tenant.subscription_ends_at = datetime.utcnow() + timedelta(days=365)  # 1 year
    
    db.session.commit()
    
    from flask import flash
    flash(f'✅ Activated {tenant.company_name} with Pro plan for 1 year', 'success')
    return redirect(url_for('superadmin.view_tenant', tenant_id=tenant_id))

@superadmin_bp.route('/tenant/<int:tenant_id>/suspend', methods=['POST'])
def suspend_tenant(tenant_id):
    """Suspend tenant access"""
    if not is_superadmin():
        return redirect(url_for('superadmin.login'))
    
    tenant = Tenant.query.get_or_404(tenant_id)
    tenant.status = 'suspended'
    db.session.commit()
    
    from flask import flash
    flash(f'⚠️ Suspended {tenant.company_name}', 'warning')
    return redirect(url_for('superadmin.view_tenant', tenant_id=tenant_id))

@superadmin_bp.route('/fix-licenses')
def fix_licenses():
    """One-time fix: Set trial_ends_at for existing accounts"""
    if not is_superadmin():
        return redirect(url_for('superadmin.login'))
    
    from datetime import datetime, timedelta
    
    # Find tenants without trial_ends_at
    tenants_without_license = Tenant.query.filter(Tenant.trial_ends_at == None).all()
    
    fixed_count = 0
    for tenant in tenants_without_license:
        # Give them 30 days from now
        tenant.trial_ends_at = datetime.utcnow() + timedelta(days=30)
        tenant.status = 'trial'
        tenant.plan = 'trial'
        fixed_count += 1
    
    db.session.commit()
    
    from flask import flash
    flash(f'✅ Fixed {fixed_count} accounts - gave them 30-day trial from today', 'success')
    return redirect(url_for('superadmin.dashboard'))

