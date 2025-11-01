"""
Unified Employee Portal
Single entry point for all employee actions: Attendance, Purchase Requests, Tasks
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g
from models import db, Employee
from utils.tenant_middleware import require_tenant
from datetime import datetime

employee_portal_bp = Blueprint('employee_portal', __name__, url_prefix='/employee')


@employee_portal_bp.route('/login', methods=['GET', 'POST'])
@require_tenant
def login():
    """Employee PIN login for unified portal"""
    if request.method == 'POST':
        phone = request.form.get('phone')
        pin = request.form.get('pin')
        
        if not phone or not pin:
            flash('Phone and PIN are required', 'error')
            return render_template('employee_portal/login.html', tenant=g.tenant)
        
        # Find employee
        employee = Employee.query.filter_by(
            tenant_id=g.tenant.id,
            phone=phone,
            pin=pin,
            active=True
        ).first()
        
        if employee:
            # Store employee ID in session
            session['employee_id'] = employee.id
            session['employee_name'] = employee.name
            flash(f'Welcome {employee.name}!', 'success')
            return redirect(url_for('employee_portal.dashboard'))
        else:
            flash('Invalid phone or PIN', 'error')
    
    return render_template('employee_portal/login.html', tenant=g.tenant)


@employee_portal_bp.route('/dashboard')
@require_tenant
def dashboard():
    """Unified employee dashboard with tabs for Attendance, Purchase Requests, Tasks"""
    if 'employee_id' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('employee_portal.login'))
    
    employee = Employee.query.get(session['employee_id'])
    if not employee or employee.tenant_id != g.tenant.id:
        session.clear()
        flash('Session expired. Please login again.', 'error')
        return redirect(url_for('employee_portal.login'))
    
    # Optimize: Get today's attendance with a single query
    from models import Attendance, Task
    from datetime import date, timedelta
    
    # Get start and end of today
    today_start = datetime.combine(date.today(), datetime.min.time())
    today_end = datetime.combine(date.today(), datetime.max.time())
    
    # Single query to get all today's attendance (more efficient)
    today_attendance = Attendance.query.filter(
        Attendance.employee_id == employee.id,
        Attendance.timestamp >= today_start,
        Attendance.timestamp <= today_end
    ).order_by(Attendance.timestamp.desc()).all()
    
    # Process in Python (faster than 2 separate queries)
    check_in = None
    check_out = None
    for record in today_attendance:
        if record.type == 'check_in' and not check_in:
            check_in = record
        elif record.type == 'check_out' and not check_out:
            check_out = record
        if check_in and check_out:
            break
    
    # Get pending tasks count (optimized with index)
    pending_tasks = Task.query.filter(
        Task.assigned_to == employee.id,
        Task.status.in_(['new', 'in_progress'])
    ).count()
    
    return render_template('employee_portal/dashboard.html',
                         tenant=g.tenant,
                         employee=employee,
                         check_in=check_in,
                         check_out=check_out,
                         pending_tasks=pending_tasks)


@employee_portal_bp.route('/logout')
def logout():
    """Logout employee"""
    session.pop('employee_id', None)
    session.pop('employee_name', None)
    flash('Logged out successfully', 'success')
    return redirect(url_for('employee_portal.login'))

