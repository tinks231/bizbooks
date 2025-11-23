"""
Customer Portal Routes
Allows customers to:
- View subscriptions and delivery logs
- Pause/Resume/Modify deliveries
- View invoices
- Change PIN
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g
from functools import wraps
from models import db, Customer, CustomerSubscription, SubscriptionDelivery, Invoice, SubscriptionPlan
from utils.tenant_middleware import require_tenant, get_current_tenant
from datetime import datetime, timedelta
from sqlalchemy import and_, or_

customer_portal_bp = Blueprint('customer_portal', __name__, url_prefix='/customer')


def customer_login_required(f):
    """Decorator to require customer login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'customer_id' not in session:
            flash('Please login to access this page', 'error')
            return redirect(url_for('customer_portal.login'))
        return f(*args, **kwargs)
    return decorated_function


@customer_portal_bp.route('/login', methods=['GET', 'POST'])
@require_tenant
def login():
    """Customer login with Phone + PIN"""
    if request.method == 'POST':
        phone = request.form.get('phone', '').strip()
        pin = request.form.get('pin', '').strip()
        
        if not phone or not pin:
            flash('Phone and PIN are required', 'error')
            return render_template('customer_portal/login.html', tenant=g.tenant)
        
        # Find customer by phone + PIN
        customer = Customer.query.filter_by(
            tenant_id=g.tenant.id,
            phone=phone,
            pin=pin,
            is_active=True
        ).first()
        
        if customer:
            # Store customer session
            session['customer_id'] = customer.id
            session['customer_name'] = customer.name
            session['customer_phone'] = customer.phone
            flash(f'Welcome back, {customer.name}!', 'success')
            return redirect(url_for('customer_portal.dashboard'))
        else:
            flash('Invalid phone number or PIN. Please try again.', 'error')
    
    return render_template('customer_portal/login.html', tenant=g.tenant)


@customer_portal_bp.route('/logout')
def logout():
    """Customer logout"""
    customer_name = session.get('customer_name', 'Customer')
    session.pop('customer_id', None)
    session.pop('customer_name', None)
    session.pop('customer_phone', None)
    flash(f'Goodbye, {customer_name}!', 'info')
    return redirect(url_for('customer_portal.login'))


@customer_portal_bp.route('/dashboard')
@require_tenant
@customer_login_required
def dashboard():
    """Customer dashboard - show active subscriptions and upcoming deliveries"""
    customer = Customer.query.get(session['customer_id'])
    
    # Get active subscriptions (including pending_payment - invoice generated but not paid yet)
    active_subscriptions = CustomerSubscription.query.filter(
        CustomerSubscription.customer_id == customer.id,
        CustomerSubscription.status.in_(['active', 'pending_payment'])
    ).all()
    
    # Get upcoming deliveries (next 7 days) for metered subscriptions
    today = datetime.now().date()
    next_week = today + timedelta(days=7)
    
    upcoming_deliveries = []
    for subscription in active_subscriptions:
        if subscription.plan.plan_type == 'metered':
            deliveries = SubscriptionDelivery.query.filter(
                and_(
                    SubscriptionDelivery.subscription_id == subscription.id,
                    SubscriptionDelivery.delivery_date >= today,
                    SubscriptionDelivery.delivery_date <= next_week
                )
            ).order_by(SubscriptionDelivery.delivery_date).all()
            upcoming_deliveries.extend(deliveries)
    
    # Get recent invoices (last 3)
    recent_invoices = Invoice.query.filter_by(
        customer_id=customer.id
    ).order_by(Invoice.invoice_date.desc()).limit(3).all()
    
    return render_template('customer_portal/dashboard.html',
                         tenant=g.tenant,
                         customer=customer,
                         active_subscriptions=active_subscriptions,
                         upcoming_deliveries=upcoming_deliveries,
                         recent_invoices=recent_invoices)


@customer_portal_bp.route('/subscriptions')
@require_tenant
@customer_login_required
def subscriptions():
    """View all subscriptions (active + expired)"""
    customer = Customer.query.get(session['customer_id'])
    
    subscriptions = CustomerSubscription.query.filter_by(
        customer_id=customer.id
    ).order_by(CustomerSubscription.created_at.desc()).all()
    
    return render_template('customer_portal/subscriptions.html',
                         tenant=g.tenant,
                         customer=customer,
                         subscriptions=subscriptions)


@customer_portal_bp.route('/subscriptions/<int:subscription_id>/deliveries')
@require_tenant
@customer_login_required
def view_deliveries(subscription_id):
    """View delivery log for a specific subscription"""
    customer = Customer.query.get(session['customer_id'])
    
    subscription = CustomerSubscription.query.filter_by(
        id=subscription_id,
        customer_id=customer.id
    ).first_or_404()
    
    # Get selected month (default: current month)
    try:
        year = int(request.args.get('year', datetime.now().year))
        month = int(request.args.get('month', datetime.now().month))
        view_date = datetime(year, month, 1).date()
    except (ValueError, TypeError):
        view_date = datetime.now().date().replace(day=1)
    
    # Get all deliveries for the month
    from calendar import monthrange
    last_day = monthrange(view_date.year, view_date.month)[1]
    month_start = view_date
    month_end = view_date.replace(day=last_day)
    
    deliveries = SubscriptionDelivery.query.filter(
        and_(
            SubscriptionDelivery.subscription_id == subscription_id,
            SubscriptionDelivery.delivery_date >= month_start,
            SubscriptionDelivery.delivery_date <= month_end
        )
    ).order_by(SubscriptionDelivery.delivery_date).all()
    
    # Create calendar structure
    delivery_dict = {d.delivery_date: d for d in deliveries}
    
    # Calculate month summary
    total_quantity = sum(d.quantity for d in deliveries if d.status == 'delivered')
    total_amount = sum(d.amount for d in deliveries if d.status == 'delivered')
    paused_days = len([d for d in deliveries if d.status == 'paused'])
    modified_days = len([d for d in deliveries if d.is_modified])
    
    return render_template('customer_portal/deliveries.html',
                         tenant=g.tenant,
                         customer=customer,
                         subscription=subscription,
                         view_date=view_date,
                         deliveries=delivery_dict,
                         total_quantity=total_quantity,
                         total_amount=total_amount,
                         paused_days=paused_days,
                         modified_days=modified_days,
                         timedelta=timedelta)  # For date calculations in template


@customer_portal_bp.route('/subscriptions/<int:subscription_id>/pause', methods=['POST'])
@require_tenant
@customer_login_required
def pause_deliveries(subscription_id):
    """Pause deliveries for a date range"""
    customer = Customer.query.get(session['customer_id'])
    
    subscription = CustomerSubscription.query.filter_by(
        id=subscription_id,
        customer_id=customer.id
    ).first_or_404()
    
    start_date_str = request.form.get('start_date')
    end_date_str = request.form.get('end_date')
    
    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)
        
        # Prevent modifying past dates (including today - milk already delivered!)
        if start_date < tomorrow:
            flash('❌ Cannot pause today or past deliveries. Today\'s milk is already on its way! You can only modify from tomorrow onwards.', 'error')
            return redirect(url_for('customer_portal.view_deliveries', subscription_id=subscription_id))
        
        if start_date > end_date:
            flash('Start date must be before end date', 'error')
            return redirect(url_for('customer_portal.view_deliveries', subscription_id=subscription_id))
        
        # Pause all deliveries in range
        deliveries = SubscriptionDelivery.query.filter(
            and_(
                SubscriptionDelivery.subscription_id == subscription_id,
                SubscriptionDelivery.delivery_date >= start_date,
                SubscriptionDelivery.delivery_date <= end_date,
                SubscriptionDelivery.status == 'delivered'
            )
        ).all()
        
        paused_count = 0
        for delivery in deliveries:
            delivery.status = 'paused'
            delivery.quantity = 0
            delivery.amount = 0
            delivery.is_modified = True
            delivery.modification_reason = 'Paused by customer'
            delivery.updated_at = datetime.now()
            paused_count += 1
        
        db.session.commit()
        flash(f'✅ Paused {paused_count} deliveries from {start_date.strftime("%d-%m-%Y")} to {end_date.strftime("%d-%m-%Y")}', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error pausing deliveries: {str(e)}', 'error')
    
    return redirect(url_for('customer_portal.view_deliveries', subscription_id=subscription_id))


@customer_portal_bp.route('/subscriptions/<int:subscription_id>/resume', methods=['POST'])
@require_tenant
@customer_login_required
def resume_deliveries(subscription_id):
    """Resume paused deliveries for a date range"""
    customer = Customer.query.get(session['customer_id'])
    
    subscription = CustomerSubscription.query.filter_by(
        id=subscription_id,
        customer_id=customer.id
    ).first_or_404()
    
    start_date_str = request.form.get('start_date')
    end_date_str = request.form.get('end_date')
    
    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)
        
        # Prevent modifying past dates (including today - milk already delivered!)
        if start_date < tomorrow:
            flash('❌ Cannot resume today or past deliveries. Today\'s milk is already on its way! You can only modify from tomorrow onwards.', 'error')
            return redirect(url_for('customer_portal.view_deliveries', subscription_id=subscription_id))
        
        # Resume all paused deliveries in range
        deliveries = SubscriptionDelivery.query.filter(
            and_(
                SubscriptionDelivery.subscription_id == subscription_id,
                SubscriptionDelivery.delivery_date >= start_date,
                SubscriptionDelivery.delivery_date <= end_date,
                SubscriptionDelivery.status == 'paused'
            )
        ).all()
        
        resumed_count = 0
        for delivery in deliveries:
            delivery.status = 'delivered'
            # Restore default quantity
            delivery.quantity = subscription.default_quantity
            delivery.amount = float(delivery.quantity) * float(subscription.plan.unit_rate)
            delivery.is_modified = False
            delivery.modification_reason = None
            delivery.updated_at = datetime.now()
            resumed_count += 1
        
        db.session.commit()
        flash(f'✅ Resumed {resumed_count} deliveries from {start_date.strftime("%d-%m-%Y")} to {end_date.strftime("%d-%m-%Y")}', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error resuming deliveries: {str(e)}', 'error')
    
    return redirect(url_for('customer_portal.view_deliveries', subscription_id=subscription_id))


@customer_portal_bp.route('/subscriptions/<int:subscription_id>/modify', methods=['POST'])
@require_tenant
@customer_login_required
def modify_delivery(subscription_id):
    """Modify quantity for a specific date"""
    customer = Customer.query.get(session['customer_id'])
    
    subscription = CustomerSubscription.query.filter_by(
        id=subscription_id,
        customer_id=customer.id
    ).first_or_404()
    
    delivery_date_str = request.form.get('delivery_date')
    new_quantity_str = request.form.get('new_quantity')
    
    try:
        delivery_date = datetime.strptime(delivery_date_str, '%Y-%m-%d').date()
        new_quantity = float(new_quantity_str)
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)
        
        # Prevent modifying past dates (including today - milk already delivered!)
        if delivery_date < tomorrow:
            flash('❌ Cannot modify today or past deliveries. Today\'s milk is already on its way! You can only modify from tomorrow onwards.', 'error')
            return redirect(url_for('customer_portal.view_deliveries', subscription_id=subscription_id))
        
        if new_quantity <= 0:
            flash('Quantity must be greater than 0', 'error')
            return redirect(url_for('customer_portal.view_deliveries', subscription_id=subscription_id))
        
        # Find delivery
        delivery = SubscriptionDelivery.query.filter_by(
            subscription_id=subscription_id,
            delivery_date=delivery_date
        ).first()
        
        if delivery:
            delivery.quantity = new_quantity
            delivery.amount = float(new_quantity) * float(subscription.plan.unit_rate)
            delivery.is_modified = True
            delivery.modification_reason = f'Quantity changed to {new_quantity} by customer'
            delivery.updated_at = datetime.now()
            db.session.commit()
            flash(f'✅ Modified delivery for {delivery_date.strftime("%d-%m-%Y")} to {new_quantity} {subscription.plan.unit_name}', 'success')
        else:
            flash('Delivery not found', 'error')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error modifying delivery: {str(e)}', 'error')
    
    return redirect(url_for('customer_portal.view_deliveries', subscription_id=subscription_id))


@customer_portal_bp.route('/invoices')
@require_tenant
@customer_login_required
def invoices():
    """View all invoices"""
    customer = Customer.query.get(session['customer_id'])
    
    all_invoices = Invoice.query.filter_by(
        customer_id=customer.id
    ).order_by(Invoice.invoice_date.desc()).all()
    
    # Separate by status
    unpaid_invoices = [inv for inv in all_invoices if inv.payment_status == 'unpaid']
    paid_invoices = [inv for inv in all_invoices if inv.payment_status == 'paid']
    
    return render_template('customer_portal/invoices.html',
                         tenant=g.tenant,
                         customer=customer,
                         unpaid_invoices=unpaid_invoices,
                         paid_invoices=paid_invoices)


@customer_portal_bp.route('/profile')
@require_tenant
@customer_login_required
def profile():
    """View and edit customer profile"""
    customer = Customer.query.get(session['customer_id'])
    
    return render_template('customer_portal/profile.html',
                         tenant=g.tenant,
                         customer=customer)


@customer_portal_bp.route('/profile/change-pin', methods=['POST'])
@require_tenant
@customer_login_required
def change_pin():
    """Change customer PIN"""
    customer = Customer.query.get(session['customer_id'])
    
    current_pin = request.form.get('current_pin', '').strip()
    new_pin = request.form.get('new_pin', '').strip()
    confirm_pin = request.form.get('confirm_pin', '').strip()
    
    # Validate current PIN
    if customer.pin != current_pin:
        flash('Current PIN is incorrect', 'error')
        return redirect(url_for('customer_portal.profile'))
    
    # Validate new PIN
    if not new_pin or len(new_pin) < 4:
        flash('New PIN must be at least 4 digits', 'error')
        return redirect(url_for('customer_portal.profile'))
    
    if new_pin != confirm_pin:
        flash('New PIN and confirmation do not match', 'error')
        return redirect(url_for('customer_portal.profile'))
    
    try:
        customer.pin = new_pin
        customer.updated_at = datetime.now()
        db.session.commit()
        flash('✅ PIN changed successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error changing PIN: {str(e)}', 'error')
    
    return redirect(url_for('customer_portal.profile'))

