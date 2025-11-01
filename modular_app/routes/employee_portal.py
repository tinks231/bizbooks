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
    
    # Get today's attendance status
    from models import Attendance
    today = datetime.now().date()
    today_attendance = Attendance.query.filter_by(
        employee_id=employee.id,
        date=today
    ).first()
    
    # Get pending tasks count
    from models import Task
    pending_tasks = Task.query.filter_by(
        assigned_to=employee.id,
        status='in_progress'
    ).count()
    
    return render_template('employee_portal/dashboard.html',
                         tenant=g.tenant,
                         employee=employee,
                         today_attendance=today_attendance,
                         pending_tasks=pending_tasks)


@employee_portal_bp.route('/logout')
def logout():
    """Logout employee"""
    session.pop('employee_id', None)
    session.pop('employee_name', None)
    flash('Logged out successfully', 'success')
    return redirect(url_for('employee_portal.login'))

