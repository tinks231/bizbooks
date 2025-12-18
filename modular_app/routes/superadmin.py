"""
Super Admin Routes - View all tenants and their data
"""
from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify, render_template_string
from models import db, Tenant, Employee, Attendance, Site, Material, Stock
from models import Item, Customer, Vendor, Invoice, PurchaseBill, Expense, Task
from sqlalchemy import func, text
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
            session.permanent = True  # Make session persistent
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
        'total_items': 0,
        'total_customers': 0,
        'total_vendors': 0,
        'total_invoices': 0,
        'total_purchase_bills': 0,
        'total_expenses': 0,
        'total_tasks': 0
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
        
        # Calculate total sales value (last 30 days) - convert to float
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_sales = float(db.session.query(func.sum(Invoice.total_amount)).filter(
            Invoice.tenant_id == tenant.id,
            Invoice.invoice_date >= thirty_days_ago
        ).scalar() or 0)
        
        # Calculate total expenses (last 30 days) - convert to float
        recent_expenses = float(db.session.query(func.sum(Expense.amount)).filter(
            Expense.tenant_id == tenant.id,
            Expense.expense_date >= thirty_days_ago
        ).scalar() or 0)
        
        # Get last activity timestamp - track ALL business actions
        last_attendance = Attendance.query.filter_by(tenant_id=tenant.id).order_by(Attendance.timestamp.desc()).first()
        last_invoice = Invoice.query.filter_by(tenant_id=tenant.id).order_by(Invoice.created_at.desc()).first()
        last_expense = Expense.query.filter_by(tenant_id=tenant.id).order_by(Expense.created_at.desc()).first()
        last_item = Item.query.filter_by(tenant_id=tenant.id).order_by(Item.created_at.desc()).first()
        last_customer = Customer.query.filter_by(tenant_id=tenant.id).order_by(Customer.created_at.desc()).first()
        last_vendor = Vendor.query.filter_by(tenant_id=tenant.id).order_by(Vendor.created_at.desc()).first()
        last_purchase = PurchaseBill.query.filter_by(tenant_id=tenant.id).order_by(PurchaseBill.created_at.desc()).first()
        last_task = Task.query.filter_by(tenant_id=tenant.id).order_by(Task.created_at.desc()).first()
        
        activity_timestamps = [
            last_attendance.timestamp if last_attendance else None,
            last_invoice.created_at if last_invoice else None,
            last_expense.created_at if last_expense else None,
            last_item.created_at if last_item else None,
            last_customer.created_at if last_customer else None,
            last_vendor.created_at if last_vendor else None,
            last_purchase.created_at if last_purchase else None,
            last_task.created_at if last_task else None
        ]
        activity_timestamps = [ts for ts in activity_timestamps if ts]
        last_activity = max(activity_timestamps) if activity_timestamps else None
        
        # Add to totals
        total_stats['total_items'] += item_count
        total_stats['total_customers'] += customer_count
        total_stats['total_vendors'] += vendor_count
        total_stats['total_invoices'] += invoice_count
        total_stats['total_purchase_bills'] += purchase_bill_count
        total_stats['total_expenses'] += expense_count
        total_stats['total_tasks'] += task_count
        
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
    
    # Calculate summary stats (convert Decimal to float to avoid type errors)
    total_sales = float(db.session.query(func.sum(Invoice.total_amount)).filter(
        Invoice.tenant_id == tenant_id
    ).scalar() or 0)
    
    total_purchases = float(db.session.query(func.sum(PurchaseBill.total_amount)).filter(
        PurchaseBill.tenant_id == tenant_id
    ).scalar() or 0)
    
    total_expenses_amount = float(db.session.query(func.sum(Expense.amount)).filter(
        Expense.tenant_id == tenant_id
    ).scalar() or 0)
    
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
    
    # Step 2: Delete all tenant data (manual cleanup due to FK constraint issues)
    try:
        from sqlalchemy import text
        
        # Execute raw SQL to delete all related data
        # This avoids FK constraint issues with CASCADE
        db.session.execute(text("""
            -- Attendance & Payroll
            DELETE FROM attendance WHERE tenant_id = :tenant_id;
            DELETE FROM salary_slips WHERE tenant_id = :tenant_id;
            DELETE FROM payroll_payments WHERE tenant_id = :tenant_id;
            
            -- Loyalty Program
            DELETE FROM loyalty_transactions WHERE tenant_id = :tenant_id;
            DELETE FROM customer_loyalty_points WHERE tenant_id = :tenant_id;
            DELETE FROM loyalty_programs WHERE tenant_id = :tenant_id;
            
            -- Customer Orders & Subscriptions
            DELETE FROM customer_orders WHERE tenant_id = :tenant_id;
            DELETE FROM subscription_deliveries WHERE subscription_id IN (SELECT id FROM customer_subscriptions WHERE tenant_id = :tenant_id);
            DELETE FROM subscription_payments WHERE subscription_id IN (SELECT id FROM customer_subscriptions WHERE tenant_id = :tenant_id);
            DELETE FROM customer_subscriptions WHERE tenant_id = :tenant_id;
            DELETE FROM delivery_day_notes WHERE tenant_id = :tenant_id;
            
            -- Invoices
            DELETE FROM invoice_commissions WHERE tenant_id = :tenant_id;
            DELETE FROM invoices WHERE tenant_id = :tenant_id;
            
            -- Sales Orders
            DELETE FROM sales_order_items WHERE sales_order_id IN (SELECT id FROM sales_orders WHERE tenant_id = :tenant_id);
            DELETE FROM sales_orders WHERE tenant_id = :tenant_id;
            
            -- Delivery Challans
            DELETE FROM delivery_challan_items WHERE delivery_challan_id IN (SELECT id FROM delivery_challans WHERE tenant_id = :tenant_id);
            DELETE FROM delivery_challans WHERE tenant_id = :tenant_id;
            
            -- Purchase Bills & Requests
            DELETE FROM purchase_bill_items WHERE purchase_bill_id IN (SELECT id FROM purchase_bills WHERE tenant_id = :tenant_id);
            DELETE FROM purchase_bills WHERE tenant_id = :tenant_id;
            DELETE FROM purchase_requests WHERE tenant_id = :tenant_id;
            
            -- Vendor Payments
            DELETE FROM vendor_payments WHERE tenant_id = :tenant_id;
            
            -- Inventory & Stock
            DELETE FROM item_stock_movements WHERE tenant_id = :tenant_id;
            DELETE FROM item_stocks WHERE tenant_id = :tenant_id;
            DELETE FROM stock_movements WHERE tenant_id = :tenant_id;
            DELETE FROM stocks WHERE tenant_id = :tenant_id;
            DELETE FROM inventory_adjustments WHERE tenant_id = :tenant_id;
            DELETE FROM transfers WHERE tenant_id = :tenant_id;
            
            -- Expenses
            DELETE FROM expenses WHERE tenant_id = :tenant_id;
            DELETE FROM expense_categories WHERE tenant_id = :tenant_id;
            
            -- Tasks
            DELETE FROM tasks WHERE tenant_id = :tenant_id;
            
            -- Account Transactions
            DELETE FROM account_transactions WHERE tenant_id = :tenant_id;
            
            -- Items & Materials
            DELETE FROM items WHERE tenant_id = :tenant_id;
            DELETE FROM item_groups WHERE tenant_id = :tenant_id;
            DELETE FROM item_categories WHERE tenant_id = :tenant_id;
            DELETE FROM materials WHERE tenant_id = :tenant_id;
            
            -- Customers
            DELETE FROM customers WHERE tenant_id = :tenant_id;
            
            -- Vendors
            DELETE FROM vendors WHERE tenant_id = :tenant_id;
            
            -- Commission Agents
            DELETE FROM commission_agents WHERE tenant_id = :tenant_id;
            
            -- Employees
            DELETE FROM employees WHERE tenant_id = :tenant_id;
            
            -- Sites
            DELETE FROM sites WHERE tenant_id = :tenant_id;
            
            -- Bank Accounts
            DELETE FROM bank_accounts WHERE tenant_id = :tenant_id;
            
            -- Finally, delete the tenant
            DELETE FROM tenants WHERE id = :tenant_id;
        """), {'tenant_id': tenant_id})
        
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        from flask import flash
        flash(f'❌ Error deleting tenant: {str(e)}', 'error')
        return redirect(url_for('superadmin.dashboard'))
    
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

@superadmin_bp.route('/system-health')
def system_health():
    """System Health Monitoring - Database size, table stats, performance metrics"""
    if not is_superadmin():
        return redirect(url_for('superadmin.login'))
    
    print("🔬 SYSTEM HEALTH: Starting health check...")
    
    try:
        # 1. Total Database Size
        print("🔬 Executing database size query...")
        db_size_result = db.session.execute(text("""
            SELECT pg_size_pretty(pg_database_size(current_database())) as size_pretty,
                   pg_database_size(current_database()) as size_bytes
        """)).fetchone()
        print(f"🔬 Database size: {db_size_result[0] if db_size_result else 'None'}")
        
        total_db_size = {
            'pretty': db_size_result[0],
            'bytes': db_size_result[1],
            'mb': round(db_size_result[1] / (1024 * 1024), 2),
            'percent_used': round((db_size_result[1] / (500 * 1024 * 1024)) * 100, 1)  # 500 MB free plan
        }
        
        # 2. Table Sizes (sorted by largest)
        table_sizes_result = db.session.execute(text("""
            SELECT 
                tablename,
                pg_size_pretty(pg_total_relation_size('public.'||tablename)) AS size_pretty,
                pg_total_relation_size('public.'||tablename) AS size_bytes
            FROM pg_tables
            WHERE schemaname = 'public'
            ORDER BY size_bytes DESC
            LIMIT 20
        """)).fetchall()
        
        table_sizes = []
        for row in table_sizes_result:
            table_sizes.append({
                'table': row[0],
                'size_pretty': row[1],
                'size_bytes': row[2],
                'size_mb': round(row[2] / (1024 * 1024), 2)
            })
        
        # 3. Row Counts per Table
        row_counts_result = db.session.execute(text("""
            SELECT 
                schemaname,
                tablename,
                n_tup_ins - n_tup_del as row_count
            FROM pg_stat_user_tables
            WHERE schemaname = 'public'
            ORDER BY n_tup_ins - n_tup_del DESC
            LIMIT 20
        """)).fetchall()
        
        row_counts = []
        for row in row_counts_result:
            row_counts.append({
                'table': row[1],
                'count': row[2]
            })
        
        # 4. Index Sizes
        index_sizes_result = db.session.execute(text("""
            SELECT 
                tablename,
                indexname,
                pg_size_pretty(pg_relation_size(indexrelid)) AS index_size,
                pg_relation_size(indexrelid) AS size_bytes
            FROM pg_indexes
            JOIN pg_stat_user_indexes USING (schemaname, tablename, indexname)
            WHERE schemaname = 'public'
            ORDER BY pg_relation_size(indexrelid) DESC
            LIMIT 10
        """)).fetchall()
        
        index_sizes = []
        for row in index_sizes_result:
            index_sizes.append({
                'table': row[0],
                'index': row[1],
                'size_pretty': row[2],
                'size_mb': round(row[3] / (1024 * 1024), 2)
            })
        
        # 5. Growth Projection (based on current data)
        total_tenants = Tenant.query.count()
        total_items = Item.query.count()
        total_invoices = Invoice.query.count()
        total_customers = Customer.query.count()
        total_vendors = Vendor.query.count()
        total_purchase_bills = PurchaseBill.query.count()
        total_expenses = Expense.query.count()
        
        # Estimate space per record (bytes)
        space_estimates = {
            'items': total_items * 700,
            'invoices': total_invoices * 500,
            'customers': total_customers * 300,
            'vendors': total_vendors * 300,
            'purchase_bills': total_purchase_bills * 500,
            'expenses': total_expenses * 400
        }
        
        # Health Status
        if total_db_size['percent_used'] < 50:
            health_status = 'healthy'
            health_color = 'success'
            health_message = '✅ Database usage is healthy'
        elif total_db_size['percent_used'] < 70:
            health_status = 'good'
            health_color = 'info'
            health_message = '📊 Database usage is good'
        elif total_db_size['percent_used'] < 85:
            health_status = 'warning'
            health_color = 'warning'
            health_message = '⚠️ Consider monitoring growth closely'
        else:
            health_status = 'critical'
            health_color = 'danger'
            health_message = '🚨 Database approaching limit - upgrade recommended'
        
        return render_template('superadmin/system_health.html',
                             total_db_size=total_db_size,
                             table_sizes=table_sizes,
                             row_counts=row_counts,
                             index_sizes=index_sizes,
                             space_estimates=space_estimates,
                             health_status=health_status,
                             health_color=health_color,
                             health_message=health_message,
                             total_tenants=total_tenants,
                             total_items=total_items,
                             total_invoices=total_invoices,
                             total_customers=total_customers,
                             total_vendors=total_vendors,
                             total_purchase_bills=total_purchase_bills,
                             total_expenses=total_expenses,
                             now=datetime.utcnow())
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"🚨 SYSTEM HEALTH ERROR: {str(e)}")
        print(f"🚨 Traceback: {error_details}")
        
        from flask import flash
        flash(f'❌ Error fetching system health: {str(e)}', 'error')
        
        # Return error page with details for debugging
        return render_template_string('''
            <!DOCTYPE html>
            <html>
            <head>
                <title>System Health Error</title>
                <style>
                    body { font-family: Arial; padding: 40px; background: #f5f5f5; }
                    .error-box { background: white; padding: 30px; border-radius: 10px; max-width: 800px; margin: 0 auto; }
                    h1 { color: #e74c3c; }
                    pre { background: #f8f8f8; padding: 15px; border-radius: 5px; overflow-x: auto; }
                    .back-btn { display: inline-block; margin-top: 20px; padding: 10px 20px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; }
                </style>
            </head>
            <body>
                <div class="error-box">
                    <h1>🚨 System Health Monitor Error</h1>
                    <p><strong>Error:</strong> {{ error }}</p>
                    <h3>Details:</h3>
                    <pre>{{ details }}</pre>
                    <a href="/superadmin/dashboard" class="back-btn">← Back to Dashboard</a>
                </div>
            </body>
            </html>
        ''', error=str(e), details=error_details)

@superadmin_bp.route('/fix-last-logins')
def fix_last_logins():
    """One-time fix: Set last_login_at for tenants who have activity but no login timestamp"""
    if not is_superadmin():
        return redirect(url_for('superadmin.login'))
    
    from datetime import datetime
    
    # Find tenants without last_login_at
    tenants_without_login = Tenant.query.filter(Tenant.last_login_at == None).all()
    
    fixed_count = 0
    for tenant in tenants_without_login:
        # Check if they have any activity (created items, invoices, etc.)
        has_items = Item.query.filter_by(tenant_id=tenant.id).first()
        has_invoices = Invoice.query.filter_by(tenant_id=tenant.id).first()
        has_expenses = Expense.query.filter_by(tenant_id=tenant.id).first()
        has_customers = Customer.query.filter_by(tenant_id=tenant.id).first()
        has_vendors = Vendor.query.filter_by(tenant_id=tenant.id).first()
        has_tasks = Task.query.filter_by(tenant_id=tenant.id).first()
        has_attendance = Attendance.query.filter_by(tenant_id=tenant.id).first()
        
        # If they have any activity, they must have logged in
        if any([has_items, has_invoices, has_expenses, has_customers, has_vendors, has_tasks, has_attendance]):
            # Find their earliest activity as proxy for first login
            earliest_timestamps = []
            
            if has_items:
                earliest_timestamps.append(has_items.created_at)
            if has_invoices:
                earliest_timestamps.append(has_invoices.created_at)
            if has_expenses:
                earliest_timestamps.append(has_expenses.created_at)
            if has_customers:
                earliest_timestamps.append(has_customers.created_at)
            if has_vendors:
                earliest_timestamps.append(has_vendors.created_at)
            if has_tasks:
                earliest_timestamps.append(has_tasks.created_at)
            if has_attendance:
                earliest_timestamps.append(has_attendance.timestamp)
            
            if earliest_timestamps:
                # Set last_login_at to their earliest activity
                tenant.last_login_at = min(earliest_timestamps)
                fixed_count += 1
    
    db.session.commit()
    
    from flask import flash
    flash(f'✅ Fixed {fixed_count} accounts - set last_login_at based on their activity', 'success')
    return redirect(url_for('superadmin.dashboard'))

