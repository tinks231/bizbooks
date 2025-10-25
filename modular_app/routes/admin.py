"""
Admin routes - Login, Dashboard, Management
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g, abort
from models import db, User, Employee, Site, Attendance, Material, Stock, StockMovement, Tenant
from datetime import datetime, timedelta
from sqlalchemy import func
from utils.tenant_middleware import require_tenant, get_current_tenant_id, get_current_tenant
import hashlib

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def login_required(f):
    """Decorator to require admin login"""
    from functools import wraps
    @wraps(f)
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
    """Admin dashboard"""
    tenant_id = get_current_tenant_id()
    tenant = get_current_tenant()
    
    # Stats (filtered by tenant)
    total_employees = Employee.query.filter_by(tenant_id=tenant_id, active=True).count()
    total_sites = Site.query.filter_by(tenant_id=tenant_id, active=True).count()
    total_materials = Material.query.filter_by(tenant_id=tenant_id, active=True).count()
    
    # Recent attendance (filtered by tenant)
    recent_attendance = Attendance.query.filter_by(tenant_id=tenant_id).order_by(Attendance.timestamp.desc()).limit(10).all()
    
    # Low stock items (filtered by tenant)
    low_stock = Stock.query.filter(
        Stock.tenant_id == tenant_id,
        Stock.quantity < Stock.min_stock_alert
    ).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         tenant=tenant,
                         total_employees=total_employees,
                         total_sites=total_sites,
                         total_materials=total_materials,
                         recent_attendance=recent_attendance,
                         low_stock=low_stock)

# Employees Management
@admin_bp.route('/employees')
@require_tenant
@login_required
def employees():
    """Manage employees"""
    tenant_id = get_current_tenant_id()
    employees = Employee.query.filter_by(tenant_id=tenant_id).all()
    sites = Site.query.filter_by(tenant_id=tenant_id, active=True).all()
    return render_template('admin/employees.html', employees=employees, sites=sites)

@admin_bp.route('/employee/add', methods=['POST'])
@require_tenant
@login_required
def add_employee():
    """Add new employee"""
    tenant_id = get_current_tenant_id()
    name = request.form.get('name')
    pin = request.form.get('pin')
    phone = request.form.get('phone')
    site_id = request.form.get('site_id')
    
    # Check if PIN already exists (within this tenant)
    existing = Employee.query.filter_by(tenant_id=tenant_id, pin=pin).first()
    if existing:
        flash('PIN already exists!', 'error')
        return redirect(url_for('admin.employees'))
    
    employee = Employee(tenant_id=tenant_id, name=name, pin=pin, phone=phone, site_id=site_id)
    
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
    
    flash(f'Employee {name} added successfully!', 'success')
    return redirect(url_for('admin.employees'))

@admin_bp.route('/employee/delete/<int:emp_id>')
@require_tenant
@login_required
def delete_employee(emp_id):
    """Delete employee"""
    tenant_id = get_current_tenant_id()
    employee = Employee.query.filter_by(tenant_id=tenant_id, id=emp_id).first_or_404()
    employee.active = False
    db.session.commit()
    flash('Employee deactivated', 'success')
    return redirect(url_for('admin.employees'))

@admin_bp.route('/employee/document/<int:emp_id>')
@require_tenant
@login_required
def view_employee_document(emp_id):
    """View employee document"""
    from flask import send_from_directory
    import os
    tenant_id = get_current_tenant_id()
    employee = Employee.query.filter_by(tenant_id=tenant_id, id=emp_id).first_or_404()
    if employee.document_path:
        return send_from_directory('uploads/documents', employee.document_path)
    else:
        flash('No document found', 'error')
        return redirect(url_for('admin.employees'))

# Sites Management
@admin_bp.route('/sites')
@require_tenant
@login_required
def sites():
    """Manage sites"""
    tenant_id = get_current_tenant_id()
    sites = Site.query.filter_by(tenant_id=tenant_id).all()
    return render_template('admin/sites.html', sites=sites)

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
    
    return render_template('admin/edit_site.html', site=site)

# Inventory Management
@admin_bp.route('/inventory')
@require_tenant
@login_required
def inventory():
    """Manage inventory"""
    tenant_id = get_current_tenant_id()
    materials = Material.query.filter_by(tenant_id=tenant_id, active=True).all()
    sites = Site.query.filter_by(tenant_id=tenant_id, active=True).all()
    return render_template('admin/inventory.html', materials=materials, sites=sites)

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
            reason='Initial stock',
            user_id=session.get('tenant_admin_id')
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
    return render_template('admin/edit_material.html', material=material, sites=sites)

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
        reason=reason,
        user_id=session.get('tenant_admin_id')
    )
    db.session.add(movement)
    db.session.commit()
    
    flash('Stock updated successfully!', 'success')
    return redirect(url_for('admin.inventory'))

# Attendance Management
@admin_bp.route('/attendance')
@require_tenant
@login_required
def attendance():
    """View all attendance records - Grouped by employee & date"""
    from collections import defaultdict
    
    tenant_id = get_current_tenant_id()
    # Get all attendance records (for this tenant only)
    all_records = Attendance.query.filter_by(tenant_id=tenant_id).order_by(Attendance.timestamp.desc()).all()
    
    # Group by employee and date
    grouped = defaultdict(lambda: defaultdict(list))
    for record in all_records:
        date = record.timestamp.strftime("%Y-%m-%d")
        grouped[record.employee_name][date].append(record)
    
    # Create pairs (check-in + check-out)
    attendance_pairs = []
    
    for employee_name in grouped:
        for date in sorted(grouped[employee_name].keys(), reverse=True):
            day_records = sorted(grouped[employee_name][date], key=lambda x: x.timestamp)
            
            i = 0
            while i < len(day_records):
                record = day_records[i]
                
                if record.type == "check_in":
                    # Look for matching check-out
                    check_out = None
                    for j in range(i + 1, len(day_records)):
                        if day_records[j].type == "check_out":
                            check_out = day_records[j]
                            break
                    
                    # Calculate duration
                    duration = None
                    if check_out:
                        diff = check_out.timestamp - record.timestamp
                        hours = diff.seconds // 3600
                        minutes = (diff.seconds % 3600) // 60
                        duration = f"{hours}h {minutes}m"
                    
                    attendance_pairs.append({
                        'date': date,
                        'employee_name': employee_name,
                        'check_in_time': record.timestamp.strftime("%I:%M %p"),
                        'check_in_distance': f"{record.distance:.0f}m",
                        'check_in_photo': record.photo,
                        'check_in_id': record.id,
                        'check_in_comment': record.comment,
                        'check_in_manual': record.manual_entry,
                        'check_out_time': check_out.timestamp.strftime("%I:%M %p") if check_out else None,
                        'check_out_distance': f"{check_out.distance:.0f}m" if check_out else None,
                        'check_out_photo': check_out.photo if check_out else None,
                        'check_out_id': check_out.id if check_out else None,
                        'check_out_comment': check_out.comment if check_out else None,
                        'check_out_manual': check_out.manual_entry if check_out else False,
                        'duration': duration
                    })
                    
                    if check_out:
                        i += 2
                    else:
                        i += 1
                
                elif record.type == "check_out":
                    # Orphaned check-out
                    attendance_pairs.append({
                        'date': date,
                        'employee_name': employee_name,
                        'check_in_time': "—",
                        'check_in_distance': "—",
                        'check_in_photo': None,
                        'check_in_id': None,
                        'check_in_comment': None,
                        'check_in_manual': False,
                        'check_out_time': record.timestamp.strftime("%I:%M %p"),
                        'check_out_distance': f"{record.distance:.0f}m",
                        'check_out_photo': record.photo,
                        'check_out_id': record.id,
                        'check_out_comment': record.comment,
                        'check_out_manual': record.manual_entry,
                        'duration': None
                    })
                    i += 1
                else:
                    i += 1
    
    return render_template('admin/attendance.html', attendance_pairs=attendance_pairs)

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
        
        # Create timestamp
        timestamp_str = f"{date} {time}:00"
        timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
        
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
    
    return render_template('admin/manual_entry.html', employees=employees)

# QR Code Generation
@admin_bp.route('/generate_qr')
@require_tenant
@login_required
def generate_qr():
    """Generate QR code for tenant's attendance URL"""
    import qrcode
    import io
    import base64
    
    tenant = get_current_tenant()
    attendance_url = f"https://{tenant.subdomain}.bizbooks.co.in/attendance"
    
    # Create QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(attendance_url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64 for embedding in HTML
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    
    return render_template('admin/qr_code.html',
                         qr_image=img_base64,
                         url=attendance_url,
                         company=tenant.company_name,
                         subdomain=tenant.subdomain)

