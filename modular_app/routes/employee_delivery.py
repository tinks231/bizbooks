"""
Employee Delivery Portal Routes
For delivery personnel to mark deliveries and track bottles
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g
from models import db, Employee, SubscriptionDelivery, Customer, CustomerSubscription
from utils.tenant_middleware import require_tenant, get_current_tenant_id
from datetime import datetime, date
from sqlalchemy import and_
from sqlalchemy.orm import joinedload
from functools import wraps
import pytz
import math

employee_delivery_bp = Blueprint('employee_delivery', __name__, url_prefix='/employee/delivery')

# Login required decorator for employee portal
def employee_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'employee_id' not in session:
            flash('Please login first', 'error')
            return redirect(url_for('employee_delivery.login'))
        session.permanent = True
        return f(*args, **kwargs)
    return decorated_function


@employee_delivery_bp.route('/login', methods=['GET', 'POST'])
@require_tenant
def login():
    """Employee login with PIN"""
    if request.method == 'POST':
        pin = request.form.get('pin', '').strip()
        
        if not pin:
            flash('Please enter your PIN', 'error')
            return redirect(url_for('employee_delivery.login'))
        
        # Find employee by PIN and tenant
        employee = Employee.query.filter_by(
            tenant_id=g.tenant.id,
            pin=pin,
            active=True
        ).first()
        
        if employee:
            session['employee_id'] = employee.id
            session['employee_name'] = employee.name
            session['employee_tenant_id'] = employee.tenant_id
            session.permanent = True
            
            flash(f'Welcome, {employee.name}!', 'success')
            return redirect(url_for('employee_delivery.today_deliveries'))
        else:
            flash('Invalid PIN or inactive employee', 'error')
            return redirect(url_for('employee_delivery.login'))
    
    return render_template('employee_delivery/login.html', tenant=g.tenant)


@employee_delivery_bp.route('/logout')
def logout():
    """Employee logout"""
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('employee_delivery.login'))


@employee_delivery_bp.route('/today', methods=['GET'])
@require_tenant
@employee_login_required
def today_deliveries():
    """Today's delivery list for employee"""
    tenant_id = get_current_tenant_id()
    employee_id = session.get('employee_id')
    
    # Get today's date in IST
    ist = pytz.timezone('Asia/Kolkata')
    today = datetime.now(ist).date()
    
    # Get all deliveries for today ASSIGNED TO THIS EMPLOYEE
    deliveries = SubscriptionDelivery.query.join(
        CustomerSubscription
    ).join(
        CustomerSubscription.customer
    ).join(
        CustomerSubscription.plan
    ).filter(
        SubscriptionDelivery.tenant_id == tenant_id,
        SubscriptionDelivery.delivery_date == today,
        CustomerSubscription.status == 'active',
        SubscriptionDelivery.status != 'paused',
        SubscriptionDelivery.quantity > 0,
        SubscriptionDelivery.assigned_to == employee_id  # ONLY ASSIGNED DELIVERIES
    ).options(
        joinedload(SubscriptionDelivery.subscription).joinedload(CustomerSubscription.customer),
        joinedload(SubscriptionDelivery.subscription).joinedload(CustomerSubscription.plan)
    ).order_by(
        Customer.name.asc()
    ).all()
    
    # Separate completed and pending
    pending_deliveries = [d for d in deliveries if not d.delivered_at]
    completed_deliveries = [d for d in deliveries if d.delivered_at]
    
    # Calculate stats
    total_deliveries = len(deliveries)
    completed_count = len(completed_deliveries)
    pending_count = len(pending_deliveries)
    
    return render_template('employee_delivery/today_deliveries.html',
                         tenant=g.tenant,
                         employee_name=session.get('employee_name'),
                         pending_deliveries=pending_deliveries,
                         completed_deliveries=completed_deliveries,
                         total_deliveries=total_deliveries,
                         completed_count=completed_count,
                         pending_count=pending_count,
                         today=today)


@employee_delivery_bp.route('/mark/<int:delivery_id>', methods=['POST'])
@require_tenant
@employee_login_required
def mark_delivery(delivery_id):
    """Mark a delivery as completed and track bottles"""
    tenant_id = get_current_tenant_id()
    employee_id = session.get('employee_id')
    
    delivery = SubscriptionDelivery.query.filter_by(
        id=delivery_id,
        tenant_id=tenant_id
    ).first_or_404()
    
    try:
        # Get bottle data from form
        bottles_collected = int(request.form.get('bottles_collected', 0))
        
        # Mark delivery as completed
        ist = pytz.timezone('Asia/Kolkata')
        delivery.delivered_by = employee_id
        delivery.delivered_at = datetime.now(ist)
        
        # Calculate bottles delivered: Round UP for decimals (2.5L = 3 bottles)
        delivery.bottles_delivered = math.ceil(delivery.quantity)
        delivery.bottles_collected = bottles_collected
        
        # Update customer bottle balance
        customer = delivery.subscription.customer
        customer.bottles_in_possession += delivery.bottles_delivered - bottles_collected
        
        db.session.commit()
        
        flash(f'✅ Delivery marked complete! Bottles collected: {bottles_collected}', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error: {str(e)}', 'error')
    
    return redirect(url_for('employee_delivery.today_deliveries'))


@employee_delivery_bp.route('/undo/<int:delivery_id>', methods=['POST'])
@require_tenant
@employee_login_required
def undo_delivery(delivery_id):
    """Undo a completed delivery (in case of mistake)"""
    tenant_id = get_current_tenant_id()
    
    delivery = SubscriptionDelivery.query.filter_by(
        id=delivery_id,
        tenant_id=tenant_id
    ).first_or_404()
    
    if not delivery.delivered_at:
        flash('⚠️ Delivery was not marked as completed', 'warning')
        return redirect(url_for('employee_delivery.today_deliveries'))
    
    try:
        # Revert customer bottle balance
        customer = delivery.subscription.customer
        customer.bottles_in_possession -= (delivery.bottles_delivered - delivery.bottles_collected)
        
        # Clear delivery tracking
        delivery.delivered_by = None
        delivery.delivered_at = None
        delivery.bottles_delivered = 0
        delivery.bottles_collected = 0
        
        db.session.commit()
        
        flash(f'↩️ Delivery unmarked successfully', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error: {str(e)}', 'error')
    
    return redirect(url_for('employee_delivery.today_deliveries'))

