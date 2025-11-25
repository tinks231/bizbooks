"""
Subscription Management Routes

Handles subscription plans, member enrollment,
payment collection, and recurring billing.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, g
from models import db, SubscriptionPlan, CustomerSubscription, SubscriptionPayment, SubscriptionDelivery, Customer, Invoice, InvoiceItem
from utils.tenant_middleware import require_tenant, get_current_tenant, get_current_tenant_id
from utils.license_check import check_license
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy import func, or_, case
from sqlalchemy.orm import joinedload

subscriptions_bp = Blueprint('subscriptions', __name__, url_prefix='/admin/subscriptions')


# ============================================================
# DECORATORS
# ============================================================
def login_required(f):
    """Require login to access route"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import session
        if 'tenant_admin_id' not in session:
            flash('⚠️ Please login first', 'warning')
            return redirect(url_for('admin.login'))
        # Verify session tenant matches current tenant
        if session.get('tenant_admin_id') != get_current_tenant_id():
            flash('⚠️ Session expired. Please login again.', 'warning')
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function


# ============================================================
# TEST ROUTE (for debugging)
# ============================================================
@subscriptions_bp.route('/test', methods=['GET'])
def test_route():
    """Simple test route to verify blueprint is working"""
    return "✅ Subscriptions blueprint is working!", 200


# ============================================================
# DELIVERY SCHEDULE HELPER FUNCTIONS
# ============================================================
def should_deliver_on_date(date, pattern, custom_days=None, start_date=None):
    """
    Check if delivery should occur on a given date based on schedule pattern
    
    Args:
        date: The date to check
        pattern: 'daily', 'alternate', 'weekdays', 'weekends', 'custom'
        custom_days: Comma-separated weekday numbers (0=Mon, 6=Sun): '0,2,4' for Mon/Wed/Fri
        start_date: For 'alternate' pattern - day 1 of alternation
    
    Returns:
        bool: True if delivery should occur on this date
    """
    if pattern == 'daily':
        return True
    
    elif pattern == 'alternate':
        # Alternate days (every other day)
        if start_date:
            days_diff = (date - start_date).days
            return days_diff % 2 == 0
        return True  # Fallback to daily if no start_date
    
    elif pattern == 'weekdays':
        # Monday to Friday (0-4)
        return date.weekday() < 5
    
    elif pattern == 'weekends':
        # Saturday and Sunday (5-6)
        return date.weekday() >= 5
    
    elif pattern == 'custom' and custom_days:
        # Custom days (e.g., '0,2,4' for Mon/Wed/Fri)
        try:
            selected_days = [int(d.strip()) for d in custom_days.split(',')]
            return date.weekday() in selected_days
        except:
            return True  # Fallback to daily if parsing fails
    
    return True  # Default: deliver


# ============================================================
# DAILY DELIVERIES (METERED SUBSCRIPTIONS)
# ============================================================
@subscriptions_bp.route('/deliveries', methods=['GET'], strict_slashes=False)
@require_tenant
@login_required
def deliveries():
    """Daily Deliveries page - Shows exceptions and allows modifications"""
    tenant_id = get_current_tenant_id()
    
    # Get only exceptions (modified/paused deliveries)
    today = datetime.now().date()
    exceptions = SubscriptionDelivery.get_exceptions(
        tenant_id=tenant_id,
        date_from=today - timedelta(days=7),  # Past week
        date_to=today + timedelta(days=30)     # Next month
    )
    
    # Get all active metered subscriptions for dropdowns
    active_subscriptions = CustomerSubscription.query.join(
        CustomerSubscription.plan
    ).filter(
        CustomerSubscription.tenant_id == tenant_id,
        CustomerSubscription.status == 'active',
        SubscriptionPlan.plan_type == 'metered'
    ).options(
        joinedload(CustomerSubscription.customer),
        joinedload(CustomerSubscription.plan)
    ).all()
    
    return render_template('admin/subscriptions/deliveries.html',
                         exceptions=exceptions,
                         active_subscriptions=active_subscriptions,
                         now=datetime.now,
                         timedelta=timedelta)


@subscriptions_bp.route('/deliveries/tomorrow', methods=['GET'], strict_slashes=False)
@require_tenant
@login_required
def tomorrow_deliveries():
    """Tomorrow's Deliveries Report - Complete list for delivery personnel"""
    tenant_id = get_current_tenant_id()
    
    # Get target date (default: tomorrow, but allow date parameter)
    from datetime import datetime, timedelta
    date_param = request.args.get('date')
    if date_param:
        try:
            target_date = datetime.strptime(date_param, '%Y-%m-%d').date()
        except:
            target_date = (datetime.now().date() + timedelta(days=1))
    else:
        target_date = (datetime.now().date() + timedelta(days=1))
    
    # Get ALL deliveries for target date (regardless of status - we want the full list)
    all_deliveries = SubscriptionDelivery.query.join(
        CustomerSubscription
    ).join(
        CustomerSubscription.customer
    ).join(
        CustomerSubscription.plan
    ).filter(
        SubscriptionDelivery.tenant_id == tenant_id,
        SubscriptionDelivery.delivery_date == target_date,
        CustomerSubscription.status == 'active'  # Only active subscriptions
    ).options(
        joinedload(SubscriptionDelivery.subscription).joinedload(CustomerSubscription.customer),
        joinedload(SubscriptionDelivery.subscription).joinedload(CustomerSubscription.plan),
        joinedload(SubscriptionDelivery.assigned_to_employee),
        joinedload(SubscriptionDelivery.delivered_by_employee)
    ).order_by(
        Customer.name.asc()  # Sort by customer name (already joined)
    ).all()
    
    # Separate into deliveries and paused
    active_deliveries = [d for d in all_deliveries if d.status != 'paused' and d.quantity > 0]
    paused_deliveries = [d for d in all_deliveries if d.status == 'paused' or d.quantity == 0]
    
    # Calculate totals
    total_customers = len(active_deliveries)
    total_amount = sum(float(d.amount) for d in active_deliveries)
    
    # Group by product for summary
    from collections import defaultdict
    product_summary = defaultdict(lambda: {'quantity': 0, 'amount': 0, 'customers': 0})
    for delivery in active_deliveries:
        product_name = delivery.subscription.plan.name
        product_summary[product_name]['quantity'] += float(delivery.quantity)
        product_summary[product_name]['amount'] += float(delivery.amount)
        product_summary[product_name]['customers'] += 1
    
    # Get all employees for assignment dropdown
    from models.employee import Employee
    employees = Employee.query.filter_by(
        tenant_id=tenant_id,
        active=True
    ).order_by(Employee.name.asc()).all()
    
    return render_template('admin/subscriptions/tomorrow_deliveries.html',
                         target_date=target_date,
                         active_deliveries=active_deliveries,
                         paused_deliveries=paused_deliveries,
                         total_customers=total_customers,
                         total_amount=total_amount,
                         product_summary=dict(product_summary),
                         employees=employees,
                         tenant=g.tenant)


@subscriptions_bp.route('/deliveries/assign', methods=['POST'], strict_slashes=False)
@require_tenant
@login_required
def assign_delivery():
    """Assign a delivery to a specific employee"""
    tenant_id = get_current_tenant_id()
    
    try:
        delivery_id = int(request.form['delivery_id'])
        employee_id = request.form.get('employee_id')  # Can be None to unassign
        
        # Verify delivery belongs to tenant
        delivery = SubscriptionDelivery.query.filter_by(
            id=delivery_id,
            tenant_id=tenant_id
        ).first_or_404()
        
        # Verify employee belongs to tenant (if assigning)
        if employee_id:
            from models.employee import Employee
            employee = Employee.query.filter_by(
                id=int(employee_id),
                tenant_id=tenant_id,
                active=True
            ).first_or_404()
            delivery.assigned_to = employee.id
            flash(f'✅ Delivery assigned to {employee.name}', 'success')
        else:
            delivery.assigned_to = None
            flash('✅ Delivery unassigned', 'success')
        
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error assigning delivery: {str(e)}', 'error')
    
    # Redirect back to tomorrow's deliveries
    return redirect(url_for('subscriptions.tomorrow_deliveries'))


@subscriptions_bp.route('/deliveries/bulk-assign', methods=['POST'], strict_slashes=False)
@require_tenant
@login_required
def bulk_assign_deliveries():
    """Bulk assign all deliveries for a customer to an employee"""
    tenant_id = get_current_tenant_id()
    
    try:
        customer_id = int(request.form['customer_id'])
        employee_id = request.form.get('employee_id')  # Can be None to unassign
        date_str = request.form.get('date')  # Optional: specific date or all future
        
        # Verify customer belongs to tenant
        customer = Customer.query.filter_by(
            id=customer_id,
            tenant_id=tenant_id
        ).first_or_404()
        
        # Build query for deliveries to assign
        query = SubscriptionDelivery.query.join(
            CustomerSubscription
        ).filter(
            CustomerSubscription.customer_id == customer_id,
            CustomerSubscription.tenant_id == tenant_id
        )
        
        # If specific date, only assign that date
        if date_str:
            from datetime import datetime
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            query = query.filter(SubscriptionDelivery.delivery_date == target_date)
            date_desc = f" for {target_date.strftime('%b %d')}"
        else:
            # Otherwise, assign all future deliveries
            from datetime import datetime
            today = datetime.now().date()
            query = query.filter(SubscriptionDelivery.delivery_date >= today)
            date_desc = " (all future deliveries)"
        
        deliveries = query.all()
        
        # Verify employee (if assigning)
        if employee_id:
            from models.employee import Employee
            employee = Employee.query.filter_by(
                id=int(employee_id),
                tenant_id=tenant_id,
                active=True
            ).first_or_404()
            
            # Update all deliveries
            for delivery in deliveries:
                delivery.assigned_to = employee.id
            
            # Also update customer's default
            customer.default_delivery_employee = employee.id
            
            flash(f'✅ Assigned {len(deliveries)} deliveries for {customer.name} to {employee.name}{date_desc}', 'success')
        else:
            # Unassign
            for delivery in deliveries:
                delivery.assigned_to = None
            customer.default_delivery_employee = None
            flash(f'✅ Unassigned {len(deliveries)} deliveries for {customer.name}{date_desc}', 'success')
        
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error bulk assigning: {str(e)}', 'error')
    
    return redirect(url_for('subscriptions.tomorrow_deliveries'))


@subscriptions_bp.route('/deliveries/modify', methods=['POST'], strict_slashes=False)
@require_tenant
@login_required
def modify_delivery():
    """Modify a single delivery quantity (create if doesn't exist)"""
    tenant_id = get_current_tenant_id()
    
    try:
        subscription_id = int(request.form['subscription_id'])
        delivery_date = datetime.strptime(request.form['delivery_date'], '%Y-%m-%d').date()
        new_quantity = Decimal(request.form['quantity'])
        reason = request.form.get('reason', 'Modified by owner')
        
        # Verify subscription belongs to tenant
        subscription = CustomerSubscription.query.filter_by(
            id=subscription_id,
            tenant_id=tenant_id
        ).first_or_404()
        
        # Check if delivery already exists
        delivery = SubscriptionDelivery.query.filter_by(
            subscription_id=subscription_id,
            delivery_date=delivery_date
        ).first()
        
        if delivery:
            # Update existing delivery
            delivery.quantity = new_quantity
            delivery.amount = new_quantity * delivery.rate
            delivery.is_modified = (new_quantity != subscription.default_quantity)
            delivery.modification_reason = reason if delivery.is_modified else None
            delivery.status = 'paused' if new_quantity == 0 else 'delivered'
            delivery.updated_at = datetime.utcnow()
        else:
            # Create new delivery (for dates not yet auto-generated)
            delivery = SubscriptionDelivery(
                tenant_id=tenant_id,
                subscription_id=subscription_id,
                delivery_date=delivery_date,
                quantity=new_quantity,
                rate=subscription.plan.unit_rate,
                amount=new_quantity * subscription.plan.unit_rate,
                status='paused' if new_quantity == 0 else 'delivered',
                is_modified=(new_quantity != subscription.default_quantity),
                modification_reason=reason
            )
            db.session.add(delivery)
        
        db.session.commit()
        
        if new_quantity == 0:
            flash(f'✅ Delivery skipped for {subscription.customer.name} on {delivery_date.strftime("%b %d")}', 'success')
        else:
            flash(f'✅ Delivery updated for {subscription.customer.name} on {delivery_date.strftime("%b %d")}: {new_quantity} {subscription.plan.unit_name}', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error modifying delivery: {str(e)}', 'error')
    
    return redirect(url_for('subscriptions.deliveries'))


@subscriptions_bp.route('/deliveries/pause', methods=['POST'], strict_slashes=False)
@require_tenant
@login_required
def pause_deliveries():
    """Pause deliveries for a date range"""
    tenant_id = get_current_tenant_id()
    
    try:
        subscription_id = int(request.form['subscription_id'])
        date_from = datetime.strptime(request.form['date_from'], '%Y-%m-%d').date()
        date_to = datetime.strptime(request.form['date_to'], '%Y-%m-%d').date()
        reason = request.form.get('reason', 'Paused by customer')
        
        # Verify subscription belongs to tenant
        subscription = CustomerSubscription.query.filter_by(
            id=subscription_id,
            tenant_id=tenant_id
        ).first_or_404()
        
        # Pause deliveries using bulk_pause method
        updated_count = SubscriptionDelivery.bulk_pause(
            subscription_id=subscription_id,
            date_from=date_from,
            date_to=date_to,
            reason=reason
        )
        
        flash(f'✅ Paused {updated_count} deliveries for {subscription.customer.name} ({date_from.strftime("%b %d")} to {date_to.strftime("%b %d")})', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error pausing deliveries: {str(e)}', 'error')
    
    return redirect(url_for('subscriptions.deliveries'))


@subscriptions_bp.route('/deliveries/edit/<int:delivery_id>', methods=['POST'], strict_slashes=False)
@require_tenant
@login_required
def edit_delivery(delivery_id):
    """Edit a single delivery"""
    tenant_id = get_current_tenant_id()
    
    delivery = SubscriptionDelivery.query.filter_by(
        id=delivery_id,
        tenant_id=tenant_id
    ).first_or_404()
    
    try:
        new_quantity = Decimal(request.form['quantity'])
        reason = request.form.get('reason', 'Modified by owner')
        
        # Get original default quantity
        original_quantity = delivery.subscription.default_quantity
        
        # Update delivery
        delivery.quantity = new_quantity
        delivery.amount = new_quantity * delivery.rate
        delivery.is_modified = (new_quantity != original_quantity)
        delivery.modification_reason = reason if delivery.is_modified else None
        
        # Update status
        if new_quantity == 0:
            delivery.status = 'paused'
        else:
            delivery.status = 'delivered'
        
        delivery.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        flash(f'✅ Updated delivery for {delivery.delivery_date.strftime("%b %d")}', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error updating delivery: {str(e)}', 'error')
    
    return redirect(url_for('subscriptions.deliveries'))


@subscriptions_bp.route('/deliveries/resume/<int:delivery_id>', methods=['POST'], strict_slashes=False)
@require_tenant
@login_required
def resume_delivery(delivery_id):
    """Resume a paused delivery"""
    tenant_id = get_current_tenant_id()
    
    delivery = SubscriptionDelivery.query.filter_by(
        id=delivery_id,
        tenant_id=tenant_id
    ).first_or_404()
    
    try:
        # Restore to default quantity
        delivery.quantity = delivery.subscription.default_quantity
        delivery.amount = delivery.quantity * delivery.rate
        delivery.status = 'delivered'
        delivery.is_modified = False
        delivery.modification_reason = None
        delivery.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        flash(f'✅ Resumed delivery for {delivery.delivery_date.strftime("%b %d")}', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error resuming delivery: {str(e)}', 'error')
    
    return redirect(url_for('subscriptions.deliveries'))


# ============================================================
# SUBSCRIPTION PLANS CRUD
# ============================================================
@subscriptions_bp.route('/plans', methods=['GET'], strict_slashes=False)
@require_tenant
@login_required
def plans():
    """List all subscription plans"""
    tenant_id = get_current_tenant_id()
    
    # Get all plans
    plans_list = SubscriptionPlan.query.filter_by(tenant_id=tenant_id).order_by(
        SubscriptionPlan.is_active.desc(),
        SubscriptionPlan.price.asc()
    ).all()
    
    # Stats
    stats = {
        'total_plans': len(plans_list),
        'active_plans': sum(1 for p in plans_list if p.is_active),
        'total_members': CustomerSubscription.query.filter_by(
            tenant_id=tenant_id,
            status='active'
        ).count()
    }
    
    return render_template('admin/subscriptions/plans.html',
                         plans=plans_list,
                         stats=stats)


@subscriptions_bp.route('/plans/add', methods=['POST'], strict_slashes=False)
@require_tenant
@login_required
def add_plan():
    """Add new subscription plan (fixed or metered)"""
    tenant_id = get_current_tenant_id()
    
    try:
        plan_type = request.form.get('plan_type', 'fixed')
        
        # Common fields
        plan_data = {
            'tenant_id': tenant_id,
            'name': request.form['name'],
            'description': request.form.get('description', ''),
            'plan_type': plan_type,
            'is_active': True
        }
        
        # FIXED plan - use price and duration_days
        if plan_type == 'fixed':
            plan_data['price'] = Decimal(request.form['price'])
            plan_data['duration_days'] = int(request.form['duration_days'])
        
        # METERED plan - use unit_rate and unit_name
        else:
            plan_data['unit_rate'] = Decimal(request.form['unit_rate'])
            plan_data['unit_name'] = request.form['unit_name']
            # Billing cycle for metered plans (defaults to 30 days if not provided)
            plan_data['duration_days'] = int(request.form.get('billing_cycle_days', 30))
            # Delivery schedule pattern
            plan_data['delivery_pattern'] = request.form.get('delivery_pattern', 'daily')
            plan_data['custom_days'] = request.form.get('custom_days', '') if request.form.get('delivery_pattern') == 'custom' else None
        
        plan = SubscriptionPlan(**plan_data)
        
        db.session.add(plan)
        db.session.commit()
        
        plan_type_label = '📦 Fixed' if plan_type == 'fixed' else '📊 Metered'
        flash(f'✅ {plan_type_label} Plan "{plan.name}" created successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error creating plan: {str(e)}', 'error')
    
    return redirect(url_for('subscriptions.plans'))


@subscriptions_bp.route('/plans/edit/<int:plan_id>', methods=['POST'], strict_slashes=False)
@require_tenant
@login_required
def edit_plan(plan_id):
    """Edit subscription plan"""
    tenant_id = get_current_tenant_id()
    
    plan = SubscriptionPlan.query.filter_by(id=plan_id, tenant_id=tenant_id).first_or_404()
    
    try:
        plan.name = request.form['name']
        plan.description = request.form.get('description', '')
        plan.price = Decimal(request.form['price'])
        plan.duration_days = int(request.form['duration_days'])
        plan.is_active = request.form.get('is_active') == 'on'
        plan.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        flash(f'✅ Plan "{plan.name}" updated successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error updating plan: {str(e)}', 'error')
    
    return redirect(url_for('subscriptions.plans'))


@subscriptions_bp.route('/plans/delete/<int:plan_id>', methods=['POST'], strict_slashes=False)
@require_tenant
@login_required
def delete_plan(plan_id):
    """Delete subscription plan (soft delete - mark as inactive)"""
    tenant_id = get_current_tenant_id()
    
    plan = SubscriptionPlan.query.filter_by(id=plan_id, tenant_id=tenant_id).first_or_404()
    
    # Check if plan has active subscriptions
    active_count = CustomerSubscription.query.filter_by(
        plan_id=plan_id,
        status='active'
    ).count()
    
    if active_count > 0:
        flash(f'⚠️ Cannot delete plan "{plan.name}" - {active_count} active members are using it!', 'warning')
        return redirect(url_for('subscriptions.plans'))
    
    try:
        plan.is_active = False
        plan.updated_at = datetime.utcnow()
        db.session.commit()
        
        flash(f'✅ Plan "{plan.name}" deactivated successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error deactivating plan: {str(e)}', 'error')
    
    return redirect(url_for('subscriptions.plans'))


# ============================================================
# MEMBER ENROLLMENT
# ============================================================
@subscriptions_bp.route('/members', methods=['GET'], strict_slashes=False)
@require_tenant
@login_required
def members():
    """List all active members with subscriptions"""
    tenant_id = get_current_tenant_id()
    
    # Get filter parameters
    status_filter = request.args.get('status', 'active')
    search_query = request.args.get('search', '').strip()
    plan_filter = request.args.get('plan', '')
    
    # Base query with eager loading to prevent N+1 queries
    # NOTE: Only load customer and plan (payments not used in members list)
    query = CustomerSubscription.query.options(
        joinedload(CustomerSubscription.customer),
        joinedload(CustomerSubscription.plan)
    ).filter(
        CustomerSubscription.tenant_id == tenant_id
    )
    
    # Apply filters
    if status_filter == 'active':
        query = query.filter(CustomerSubscription.status == 'active')
    elif status_filter == 'pending_payment':
        query = query.filter(CustomerSubscription.status == 'pending_payment')
    elif status_filter == 'due_soon':
        today = datetime.now().date()
        three_days = today + timedelta(days=3)
        query = query.filter(
            CustomerSubscription.status == 'active',
            CustomerSubscription.current_period_end <= three_days
        )
    elif status_filter == 'overdue':
        today = datetime.now().date()
        query = query.filter(
            CustomerSubscription.status == 'active',
            CustomerSubscription.current_period_end < today
        )
    elif status_filter == 'expired':
        query = query.filter(CustomerSubscription.status == 'expired')
    elif status_filter == 'cancelled':
        query = query.filter(CustomerSubscription.status == 'cancelled')
    
    # Search filter
    if search_query:
        query = query.join(CustomerSubscription.customer).filter(
            or_(
                Customer.name.ilike(f'%{search_query}%'),
                Customer.phone.ilike(f'%{search_query}%')
            )
        )
    
    # Plan filter
    if plan_filter:
        query = query.filter(CustomerSubscription.plan_id == int(plan_filter))
    
    # Get subscriptions with pagination
    page = request.args.get('page', 1, type=int)
    per_page = 50
    pagination = query.order_by(
        CustomerSubscription.current_period_end.asc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    subscriptions_list = pagination.items
    
    # NOTE: Removed total_paid calculation - not displayed on members page
    # (Only needed for reports page where payment amounts are shown)
    
    # ============================================================
    # OPTIMIZED STATS: Calculate all counts in ONE query with CASE
    # ============================================================
    today = datetime.now().date()
    three_days = today + timedelta(days=3)
    
    stats_result = db.session.query(
        func.count(case((CustomerSubscription.status == 'active', 1))).label('active'),
        func.count(case((CustomerSubscription.status == 'pending_payment', 1))).label('pending_payment'),
        func.count(case((
            (CustomerSubscription.status == 'active') &
            (CustomerSubscription.current_period_end <= three_days) &
            (CustomerSubscription.current_period_end >= today), 1
        ))).label('due_soon'),
        func.count(case((
            (CustomerSubscription.status == 'active') &
            (CustomerSubscription.current_period_end < today), 1
        ))).label('overdue'),
        func.count(case((CustomerSubscription.status == 'expired', 1))).label('expired')
    ).filter(
        CustomerSubscription.tenant_id == tenant_id
    ).first()
    
    stats = {
        'active': stats_result.active or 0,
        'pending_payment': stats_result.pending_payment or 0,
        'due_soon': stats_result.due_soon or 0,
        'overdue': stats_result.overdue or 0,
        'expired': stats_result.expired or 0
    }
    
    # Get all active plans for filter dropdown
    active_plans = SubscriptionPlan.query.filter_by(tenant_id=tenant_id, is_active=True).all()
    
    return render_template('admin/subscriptions/members.html',
                         subscriptions=subscriptions_list,
                         pagination=pagination,
                         stats=stats,
                         active_plans=active_plans,
                         status_filter=status_filter,
                         search_query=search_query,
                         plan_filter=plan_filter)


@subscriptions_bp.route('/members/enroll', methods=['GET', 'POST'], strict_slashes=False)
@require_tenant
@login_required
def enroll_member():
    """Enroll a customer in a subscription plan"""
    tenant_id = get_current_tenant_id()
    
    if request.method == 'GET':
        # Show enrollment form
        customers = Customer.query.filter_by(tenant_id=tenant_id).order_by(Customer.name).all()
        plans = SubscriptionPlan.query.filter_by(tenant_id=tenant_id, is_active=True).order_by(SubscriptionPlan.price).all()
        
        return render_template('admin/subscriptions/enroll.html',
                             customers=customers,
                             plans=plans)
    
    # POST - Process enrollment
    try:
        customer_id = int(request.form['customer_id'])
        plan_id = int(request.form['plan_id'])
        start_date_str = request.form['start_date']
        payment_collected = request.form.get('payment_collected') == 'on'
        
        # Parse start date
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        
        # Get plan
        plan = SubscriptionPlan.query.filter_by(id=plan_id, tenant_id=tenant_id).first_or_404()
        
        # Calculate period end based on plan type
        if plan.plan_type == 'metered':
            # METERED: Always bill till end of CURRENT month
            # Examples:
            #   Nov 1 → Nov 30 (30 days)
            #   Nov 22 → Nov 30 (9 days) 
            #   Dec 1 → Dec 31 (31 days)
            #   Feb 15 → Feb 28 (13-14 days)
            
            # Calculate last day of current month
            if start_date.month == 12:
                # December → Last day is Dec 31
                period_end = datetime(start_date.year, 12, 31).date()
            else:
                # First day of next month - 1 day = Last day of current month
                period_end = datetime(start_date.year, start_date.month + 1, 1).date() - timedelta(days=1)
        else:
            # FIXED: Use duration_days as before
            period_end = start_date + timedelta(days=plan.duration_days)
        
        # Determine subscription status
        # For metered plans, always active (payment collected after consumption)
        # For fixed plans, depends on payment_collected
        if plan.plan_type == 'metered':
            subscription_status = 'active'
        else:
            subscription_status = 'active' if payment_collected else 'pending_payment'
        
        # Create subscription
        subscription_data = {
            'tenant_id': tenant_id,
            'customer_id': customer_id,
            'plan_id': plan_id,
            'start_date': start_date,
            'current_period_start': start_date,
            'current_period_end': period_end,
            'status': subscription_status,
            'auto_renew': True
        }
        
        # For metered plans, get default quantity
        if plan.plan_type == 'metered':
            default_quantity = Decimal(request.form.get('default_quantity', 0))
            subscription_data['default_quantity'] = default_quantity
        
        subscription = CustomerSubscription(**subscription_data)
        
        db.session.add(subscription)
        db.session.flush()  # Get subscription ID
        
        # AUTO-GENERATE DELIVERIES for metered plans (based on schedule pattern)
        if plan.plan_type == 'metered':
            current_date = start_date
            deliveries_created = 0
            skipped_days = 0
            
            # Get delivery schedule pattern
            delivery_pattern = plan.delivery_pattern or 'daily'
            custom_days = plan.custom_days
            
            # Include period_end (e.g., Nov 22-30 should include Nov 30)
            while current_date <= period_end:
                # Check if delivery should occur on this date based on schedule
                if should_deliver_on_date(current_date, delivery_pattern, custom_days, start_date):
                    # Get customer to check for default delivery employee
                    customer = Customer.query.get(customer_id)
                    
                    delivery = SubscriptionDelivery(
                        tenant_id=tenant_id,
                        subscription_id=subscription.id,
                        delivery_date=current_date,
                        quantity=subscription.default_quantity,
                        rate=plan.unit_rate,
                        amount=subscription.default_quantity * plan.unit_rate,
                        status='delivered',  # Will be updated only if exception occurs
                        is_modified=False,
                        assigned_to=customer.default_delivery_employee if customer else None  # Auto-assign
                    )
                    db.session.add(delivery)
                    deliveries_created += 1
                else:
                    skipped_days += 1
                
                current_date += timedelta(days=1)
            
            pattern_display = {
                'daily': 'Daily',
                'alternate': 'Alternate days',
                'weekdays': 'Weekdays only (Mon-Fri)',
                'weekends': 'Weekends only (Sat-Sun)',
                'custom': f'Custom schedule'
            }.get(delivery_pattern, 'Daily')
            
            flash(f'📊 Auto-generated {deliveries_created} deliveries ({pattern_display})!', 'info')
            if skipped_days > 0:
                flash(f'⏭️ Skipped {skipped_days} days based on schedule pattern', 'info')
        
        # Record payment and invoice only if payment collected (FIXED plans only)
        # Metered plans: Payment collected at end of billing cycle based on consumption
        if payment_collected and plan.plan_type == 'fixed':
            payment_amount = Decimal(request.form['payment_amount'])
            payment_mode = request.form['payment_mode']
            generate_invoice = request.form.get('generate_invoice') == 'on'
            
            billing_period_label = start_date.strftime('%b %Y') if plan.duration_days == 30 else f"{start_date.strftime('%b')}-{period_end.strftime('%b %Y')}"
            
            payment = SubscriptionPayment(
                tenant_id=tenant_id,
                subscription_id=subscription.id,
                payment_date=start_date,
                amount=payment_amount,
                payment_mode=payment_mode,
                period_start=start_date,
                period_end=period_end,
                billing_period_label=billing_period_label
            )
            
            db.session.add(payment)
            
            # Generate invoice if requested
            if generate_invoice:
                customer = Customer.query.get(customer_id)
                
                # Create invoice
                invoice = Invoice(
                    tenant_id=tenant_id,
                    customer_id=customer_id,
                    customer_name=customer.name,
                    customer_phone=customer.phone or '',
                    customer_email=customer.email or '',
                    invoice_date=start_date,
                    invoice_number=f"SUB-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    total_amount=float(payment_amount),
                    payment_status='paid',  # Paid in full
                    paid_amount=float(payment_amount),
                    payment_method=payment_mode,
                    status='paid'
                )
                
                db.session.add(invoice)
                db.session.flush()
                
                # Add invoice item
                item = InvoiceItem(
                    invoice_id=invoice.id,
                    item_name=f"Subscription - {plan.name}",
                    description=f"{plan.name} - {billing_period_label}",
                    quantity=1,
                    unit='Service',
                    rate=float(payment_amount),
                    taxable_value=float(payment_amount),
                    gst_rate=0,  # No GST on subscriptions
                    cgst_amount=0,
                    sgst_amount=0,
                    igst_amount=0,
                    total_amount=float(payment_amount)  # Total = taxable_value + GST (0 in this case)
                )
                
                db.session.add(item)
                
                # Link payment to invoice
                payment.invoice_id = invoice.id
        
        db.session.commit()
        
        # Success messages
        if plan.plan_type == 'metered':
            flash(f'✅ Customer enrolled in "{plan.name}" with {subscription.default_quantity} {plan.unit_name}/day! Daily deliveries auto-generated.', 'success')
        elif payment_collected:
            flash(f'✅ Customer enrolled successfully in "{plan.name}" and payment recorded!', 'success')
        else:
            flash(f'✅ Customer enrolled in "{plan.name}". Payment is PENDING - collect it later.', 'warning')
        
        return redirect(url_for('subscriptions.members'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error enrolling member: {str(e)}', 'error')
        return redirect(url_for('subscriptions.enroll_member'))


# ============================================================
# MEMBER DETAIL & PAYMENT HISTORY
# ============================================================
@subscriptions_bp.route('/members/<int:subscription_id>', methods=['GET'], strict_slashes=False)
@require_tenant
@login_required
def member_detail(subscription_id):
    """View member subscription details and payment history"""
    tenant_id = get_current_tenant_id()
    
    subscription = CustomerSubscription.query.filter_by(
        id=subscription_id,
        tenant_id=tenant_id
    ).first_or_404()
    
    # Get all payments for this subscription
    payments = SubscriptionPayment.query.filter_by(
        subscription_id=subscription_id
    ).order_by(SubscriptionPayment.payment_date.desc()).all()
    
    return render_template('admin/subscriptions/member_detail.html',
                         subscription=subscription,
                         payments=payments)


# ============================================================
# PAYMENT COLLECTION
# ============================================================
@subscriptions_bp.route('/members/<int:subscription_id>/collect-payment', methods=['GET', 'POST'], strict_slashes=False)
@require_tenant
@login_required
def collect_payment(subscription_id):
    """Collect payment and renew subscription"""
    tenant_id = get_current_tenant_id()
    
    subscription = CustomerSubscription.query.filter_by(
        id=subscription_id,
        tenant_id=tenant_id
    ).first_or_404()
    
    if request.method == 'GET':
        # Calculate next billing period for display
        next_period_start = subscription.current_period_end + timedelta(days=1)
        next_period_end = next_period_start + timedelta(days=subscription.plan.duration_days)
        
        # Show payment collection form
        return render_template('admin/subscriptions/collect_payment.html',
                             subscription=subscription,
                             next_period_start=next_period_start,
                             next_period_end=next_period_end)
    
    # POST - Process payment
    try:
        payment_amount = Decimal(request.form['payment_amount'])
        payment_mode = request.form['payment_mode']
        payment_date_str = request.form.get('payment_date', datetime.now().strftime('%Y-%m-%d'))
        generate_invoice = request.form.get('generate_invoice') == 'on'
        
        payment_date = datetime.strptime(payment_date_str, '%Y-%m-%d').date()
        
        # Check if this is the first payment (pending_payment status)
        is_first_payment = subscription.status == 'pending_payment'
        
        if is_first_payment:
            # First payment - use existing period
            period_start = subscription.current_period_start
            period_end = subscription.current_period_end
            
            # Activate subscription
            subscription.status = 'active'
        else:
            # Renewal payment - calculate new period
            period_start = subscription.current_period_end + timedelta(days=1)
            period_end = period_start + timedelta(days=subscription.plan.duration_days)
            
            # Renew subscription
            subscription.current_period_start = period_start
            subscription.current_period_end = period_end
        
        # Create billing label
        billing_period_label = period_start.strftime('%b %Y') if subscription.plan.duration_days == 30 else f"{period_start.strftime('%b')}-{period_end.strftime('%b %Y')}"
        
        # Record payment
        payment = SubscriptionPayment(
            tenant_id=tenant_id,
            subscription_id=subscription.id,
            payment_date=payment_date,
            amount=payment_amount,
            payment_mode=payment_mode,
            period_start=period_start,
            period_end=period_end,
            billing_period_label=billing_period_label
        )
        
        db.session.add(payment)
        
        # Generate invoice if requested
        if generate_invoice:
            customer = subscription.customer
            
            invoice = Invoice(
                tenant_id=tenant_id,
                customer_id=subscription.customer_id,
                customer_name=customer.name,
                customer_phone=customer.phone or '',
                customer_email=customer.email or '',
                invoice_date=payment_date,
                invoice_number=f"SUB-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                total_amount=float(payment_amount),
                payment_status='paid',
                paid_amount=float(payment_amount),
                payment_method=payment_mode,
                status='paid'
            )
            
            db.session.add(invoice)
            db.session.flush()
            
            # Add invoice item
            item = InvoiceItem(
                invoice_id=invoice.id,
                item_name=f"Subscription - {subscription.plan.name}",
                description=f"{subscription.plan.name} - {billing_period_label}",
                quantity=1,
                unit='Service',
                rate=float(payment_amount),
                taxable_value=float(payment_amount),
                gst_rate=0,  # No GST on subscriptions
                cgst_amount=0,
                sgst_amount=0,
                igst_amount=0,
                total_amount=float(payment_amount)  # Total = taxable_value + GST (0 in this case)
            )
            
            db.session.add(item)
            
            # Link payment to invoice
            payment.invoice_id = invoice.id
        
        db.session.commit()
        
        if is_first_payment:
            flash(f'✅ Payment collected! Subscription is now ACTIVE until {period_end.strftime("%d %b %Y")}', 'success')
        else:
            flash(f'✅ Payment collected successfully! Subscription renewed until {period_end.strftime("%d %b %Y")}', 'success')
        
        return redirect(url_for('subscriptions.member_detail', subscription_id=subscription.id))
        
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error collecting payment: {str(e)}', 'error')
        return redirect(url_for('subscriptions.collect_payment', subscription_id=subscription.id))


# ============================================================
# CANCEL SUBSCRIPTION
# ============================================================
@subscriptions_bp.route('/members/<int:subscription_id>/cancel', methods=['POST'], strict_slashes=False)
@require_tenant
@login_required
def cancel_subscription(subscription_id):
    """Cancel a customer subscription"""
    tenant_id = get_current_tenant_id()
    
    subscription = CustomerSubscription.query.filter_by(
        id=subscription_id,
        tenant_id=tenant_id
    ).first_or_404()
    
    try:
        reason = request.form.get('reason', 'No reason provided')
        subscription.cancel_subscription(reason)
        db.session.commit()
        
        flash(f'✅ Subscription cancelled successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error cancelling subscription: {str(e)}', 'error')
    
    return redirect(url_for('subscriptions.member_detail', subscription_id=subscription.id))


# ============================================================
# DELETE SUBSCRIPTION/MEMBER
# ============================================================
@subscriptions_bp.route('/members/<int:subscription_id>/delete', methods=['POST'], strict_slashes=False)
@require_tenant
@login_required
def delete_member(subscription_id):
    """Delete a subscription and all related data"""
    tenant_id = get_current_tenant_id()
    
    try:
        # Get subscription
        subscription = CustomerSubscription.query.filter_by(
            id=subscription_id,
            tenant_id=tenant_id
        ).first_or_404()
        
        customer_name = subscription.customer.name
        
        # Delete related payment records first (foreign key constraint)
        SubscriptionPayment.query.filter_by(subscription_id=subscription.id).delete()
        
        # Delete the subscription
        db.session.delete(subscription)
        db.session.commit()
        
        flash(f'✅ Subscription for "{customer_name}" has been permanently deleted!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error deleting subscription: {str(e)}', 'error')
        return redirect(url_for('subscriptions.member_detail', subscription_id=subscription_id))
    
    return redirect(url_for('subscriptions.members'))


# ============================================================
# SUBSCRIPTION REPORTS
# ============================================================
@subscriptions_bp.route('/reports', methods=['GET'], strict_slashes=False)
@require_tenant
@login_required
def reports():
    """Comprehensive subscription reports page"""
    tenant_id = get_current_tenant_id()
    
    # Get filter parameters
    start_date_str = request.args.get('start_date', '')
    end_date_str = request.args.get('end_date', '')
    plan_filter = request.args.get('plan', '')
    status_filter = request.args.get('status', 'all')
    
    # Calculate date constants
    today = datetime.now().date()
    three_days = today + timedelta(days=3)
    
    # ============================================================
    # OPTIMIZED STATS CALCULATION (SQL Aggregation)
    # ============================================================
    # Calculate total revenue from all payments (SQL aggregation)
    total_revenue = db.session.query(func.sum(SubscriptionPayment.amount)).filter(
        SubscriptionPayment.tenant_id == tenant_id
    ).scalar() or 0
    
    # Calculate MRR from active subscriptions (SQL aggregation with JOIN)
    mrr = db.session.query(func.sum(SubscriptionPlan.price)).join(
        CustomerSubscription, SubscriptionPlan.id == CustomerSubscription.plan_id
    ).filter(
        CustomerSubscription.tenant_id == tenant_id,
        CustomerSubscription.status == 'active'
    ).scalar() or 0
    
    # Count by status (simple counts, very fast with indexes)
    active_count = CustomerSubscription.query.filter_by(tenant_id=tenant_id, status='active').count()
    pending_payment_count = CustomerSubscription.query.filter_by(tenant_id=tenant_id, status='pending_payment').count()
    
    # Count due soon and overdue (fast with composite index)
    due_soon_count = CustomerSubscription.query.filter(
        CustomerSubscription.tenant_id == tenant_id,
        CustomerSubscription.status == 'active',
        CustomerSubscription.current_period_end <= three_days,
        CustomerSubscription.current_period_end >= today
    ).count()
    
    overdue_count = CustomerSubscription.query.filter(
        CustomerSubscription.tenant_id == tenant_id,
        CustomerSubscription.status == 'active',
        CustomerSubscription.current_period_end < today
    ).count()
    
    stats = {
        'total_revenue': total_revenue,
        'mrr': mrr,
        'active': active_count,
        'pending_payment': pending_payment_count,
        'due_soon': due_soon_count,
        'overdue': overdue_count
    }
    
    # ============================================================
    # OPTIMIZED SUBSCRIPTION QUERY (with Eager Loading)
    # ============================================================
    # Base query with eager loading to prevent N+1 queries
    query = CustomerSubscription.query.options(
        joinedload(CustomerSubscription.customer),
        joinedload(CustomerSubscription.plan),
        joinedload(CustomerSubscription.payments)
    ).filter(
        CustomerSubscription.tenant_id == tenant_id
    )
    
    # Apply date filter (enrollment date or due date based on context)
    if start_date_str:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        query = query.filter(CustomerSubscription.start_date >= start_date)
    
    if end_date_str:
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        query = query.filter(CustomerSubscription.start_date <= end_date)
    
    # Apply plan filter
    if plan_filter:
        query = query.filter(CustomerSubscription.plan_id == int(plan_filter))
    
    # Apply status filter
    if status_filter == 'active':
        query = query.filter(CustomerSubscription.status == 'active')
    elif status_filter == 'pending_payment':
        query = query.filter(CustomerSubscription.status == 'pending_payment')
    elif status_filter == 'due_soon':
        query = query.filter(
            CustomerSubscription.status == 'active',
            CustomerSubscription.current_period_end <= three_days,
            CustomerSubscription.current_period_end >= today
        )
    elif status_filter == 'overdue':
        query = query.filter(
            CustomerSubscription.status == 'active',
            CustomerSubscription.current_period_end < today
        )
    elif status_filter == 'expired':
        query = query.filter(CustomerSubscription.status == 'expired')
    elif status_filter == 'cancelled':
        query = query.filter(CustomerSubscription.status == 'cancelled')
    
    # Get subscriptions with pagination (reduced from 100 to 50 per page)
    page = request.args.get('page', 1, type=int)
    per_page = 50
    pagination = query.order_by(
        CustomerSubscription.start_date.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    subscriptions_list = pagination.items
    
    # ============================================================
    # FIX N+1: Pre-calculate total_paid for all subscriptions in ONE query
    # ============================================================
    if subscriptions_list:
        subscription_ids = [sub.id for sub in subscriptions_list]
        payment_totals = db.session.query(
            SubscriptionPayment.subscription_id,
            func.sum(SubscriptionPayment.amount).label('total_paid')
        ).filter(
            SubscriptionPayment.subscription_id.in_(subscription_ids)
        ).group_by(SubscriptionPayment.subscription_id).all()
        
        # Create a dictionary for quick lookup
        payment_totals_dict = {sub_id: total for sub_id, total in payment_totals}
        
        # Attach total_paid to each subscription (avoid calling the property)
        for sub in subscriptions_list:
            sub._cached_total_paid = payment_totals_dict.get(sub.id, 0)
    
    # Get all active plans for filter dropdown
    active_plans = SubscriptionPlan.query.filter_by(tenant_id=tenant_id, is_active=True).all()
    
    return render_template('admin/subscriptions/reports.html',
                         subscriptions=subscriptions_list,
                         pagination=pagination,
                         stats=stats,
                         active_plans=active_plans,
                         start_date=start_date_str,
                         end_date=end_date_str,
                         plan_filter=plan_filter,
                         status_filter=status_filter)


# ============================================================
# MONTHLY BILLING (METERED SUBSCRIPTIONS)
# ============================================================
@subscriptions_bp.route('/deliveries/generate-invoice/<int:subscription_id>', methods=['GET', 'POST'], strict_slashes=False)
@require_tenant
@login_required
def generate_invoice_metered(subscription_id):
    """Generate invoice for metered subscription based on actual deliveries"""
    tenant_id = get_current_tenant_id()
    
    subscription = CustomerSubscription.query.filter_by(
        id=subscription_id,
        tenant_id=tenant_id
    ).first_or_404()
    
    # Verify it's a metered plan
    if subscription.plan.plan_type != 'metered':
        flash('❌ This feature is only for metered subscriptions', 'error')
        return redirect(url_for('subscriptions.deliveries'))
    
    if request.method == 'GET':
        # Show invoice preview with delivery summary
        billing_start = subscription.current_period_start
        billing_end = subscription.current_period_end
        
        # Get all deliveries for this period
        deliveries = SubscriptionDelivery.query.filter_by(
            subscription_id=subscription_id,
            tenant_id=tenant_id
        ).filter(
            SubscriptionDelivery.delivery_date >= billing_start,
            SubscriptionDelivery.delivery_date <= billing_end
        ).order_by(SubscriptionDelivery.delivery_date.asc()).all()
        
        # Calculate totals
        total_quantity = sum(d.quantity for d in deliveries)
        total_amount = sum(d.amount for d in deliveries)
        total_days = len(deliveries)
        modified_days = sum(1 for d in deliveries if d.is_modified)
        
        summary = {
            'billing_start': billing_start,
            'billing_end': billing_end,
            'total_days': total_days,
            'modified_days': modified_days,
            'total_quantity': total_quantity,
            'total_amount': total_amount,
            'deliveries': deliveries
        }
        
        return render_template('admin/subscriptions/invoice_preview.html',
                             subscription=subscription,
                             summary=summary)
    
    # POST - Generate invoice
    try:
        billing_start = subscription.current_period_start
        billing_end = subscription.current_period_end
        
        # Get all deliveries for this period
        deliveries = SubscriptionDelivery.query.filter_by(
            subscription_id=subscription_id,
            tenant_id=tenant_id
        ).filter(
            SubscriptionDelivery.delivery_date >= billing_start,
            SubscriptionDelivery.delivery_date <= billing_end
        ).all()
        
        # Calculate total
        total_quantity = sum(d.quantity for d in deliveries)
        total_amount = float(sum(d.amount for d in deliveries))
        
        # Create invoice
        customer = subscription.customer
        invoice_number = f"SUB-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        invoice = Invoice(
            tenant_id=tenant_id,
            customer_id=customer.id,
            customer_name=customer.name,
            customer_phone=customer.phone or '',
            customer_email=customer.email or '',
            invoice_date=datetime.now().date(),
            invoice_number=invoice_number,
            total_amount=total_amount,
            payment_status='unpaid',
            paid_amount=0,
            status='pending'
        )
        
        db.session.add(invoice)
        db.session.flush()
        
        # Add invoice item with delivery summary
        billing_period_label = f"{billing_start.strftime('%b %d')} - {billing_end.strftime('%b %d, %Y')}"
        item_description = f"{subscription.plan.name}\n{billing_period_label}\nTotal: {total_quantity} {subscription.plan.unit_name}"
        
        item = InvoiceItem(
            invoice_id=invoice.id,
            item_name=f"Subscription - {subscription.plan.name}",
            description=item_description,
            quantity=float(total_quantity),
            unit=subscription.plan.unit_name,
            rate=float(subscription.plan.unit_rate),
            taxable_value=total_amount,
            gst_rate=0,  # No GST on subscriptions (adjust if needed)
            cgst_amount=0,
            sgst_amount=0,
            igst_amount=0,
            total_amount=total_amount
        )
        
        db.session.add(item)
        
        # Create payment record (mark as pending)
        payment = SubscriptionPayment(
            tenant_id=tenant_id,
            subscription_id=subscription.id,
            invoice_id=invoice.id,
            payment_date=datetime.now().date(),
            amount=Decimal(str(total_amount)),
            payment_mode='Pending',
            period_start=billing_start,
            period_end=billing_end,
            billing_period_label=billing_period_label
        )
        
        db.session.add(payment)
        
        # Update subscription status
        subscription.status = 'pending_payment'
        
        db.session.commit()
        
        flash(f'✅ Invoice {invoice_number} generated successfully! Amount: ₹{total_amount:,.2f} ({total_quantity} {subscription.plan.unit_name})', 'success')
        return redirect(url_for('invoices.view', invoice_id=invoice.id))
        
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error generating invoice: {str(e)}', 'error')
        return redirect(url_for('subscriptions.deliveries'))


@subscriptions_bp.route('/deliveries/generate-all-invoices', methods=['POST'], strict_slashes=False)
@require_tenant
@login_required
def generate_all_invoices():
    """Generate invoices for all metered subscriptions ending soon (bulk processing)"""
    tenant_id = get_current_tenant_id()
    
    try:
        # Get all metered subscriptions ending in next 3 days
        today = datetime.now().date()
        three_days = today + timedelta(days=3)
        
        ready_subscriptions = CustomerSubscription.query.join(
            CustomerSubscription.plan
        ).filter(
            CustomerSubscription.tenant_id == tenant_id,
            CustomerSubscription.status == 'active',
            SubscriptionPlan.plan_type == 'metered',
            CustomerSubscription.current_period_end <= three_days
        ).options(
            joinedload(CustomerSubscription.customer),
            joinedload(CustomerSubscription.plan)
        ).all()
        
        if not ready_subscriptions:
            flash('⚠️ No subscriptions ready for billing', 'warning')
            return redirect(url_for('subscriptions.deliveries'))
        
        success_count = 0
        error_count = 0
        total_amount = 0
        
        for subscription in ready_subscriptions:
            try:
                billing_start = subscription.current_period_start
                billing_end = subscription.current_period_end
                
                # Get all deliveries for this period
                deliveries = SubscriptionDelivery.query.filter_by(
                    subscription_id=subscription.id,
                    tenant_id=tenant_id
                ).filter(
                    SubscriptionDelivery.delivery_date >= billing_start,
                    SubscriptionDelivery.delivery_date <= billing_end
                ).all()
                
                # Calculate total
                total_quantity = sum(d.quantity for d in deliveries)
                invoice_amount = float(sum(d.amount for d in deliveries))
                
                # Create invoice
                customer = subscription.customer
                invoice_number = f"SUB-{datetime.now().strftime('%Y%m%d%H%M%S')}-{subscription.id}"
                
                invoice = Invoice(
                    tenant_id=tenant_id,
                    customer_id=customer.id,
                    customer_name=customer.name,
                    customer_phone=customer.phone or '',
                    customer_email=customer.email or '',
                    invoice_date=datetime.now().date(),
                    invoice_number=invoice_number,
                    total_amount=invoice_amount,
                    payment_status='unpaid',
                    paid_amount=0,
                    status='pending'
                )
                
                db.session.add(invoice)
                db.session.flush()
                
                # Add invoice item
                billing_period_label = f"{billing_start.strftime('%b %d')} - {billing_end.strftime('%b %d, %Y')}"
                item_description = f"{subscription.plan.name}\n{billing_period_label}\nTotal: {total_quantity} {subscription.plan.unit_name}"
                
                item = InvoiceItem(
                    invoice_id=invoice.id,
                    item_name=f"Subscription - {subscription.plan.name}",
                    description=item_description,
                    quantity=float(total_quantity),
                    unit=subscription.plan.unit_name,
                    rate=float(subscription.plan.unit_rate),
                    taxable_value=invoice_amount,
                    gst_rate=0,
                    cgst_amount=0,
                    sgst_amount=0,
                    igst_amount=0,
                    total_amount=invoice_amount
                )
                
                db.session.add(item)
                
                # Create payment record
                payment = SubscriptionPayment(
                    tenant_id=tenant_id,
                    subscription_id=subscription.id,
                    invoice_id=invoice.id,
                    payment_date=datetime.now().date(),
                    amount=Decimal(str(invoice_amount)),
                    payment_mode='Pending',
                    period_start=billing_start,
                    period_end=billing_end,
                    billing_period_label=billing_period_label
                )
                
                db.session.add(payment)
                
                # Update subscription status
                subscription.status = 'pending_payment'
                
                success_count += 1
                total_amount += invoice_amount
                
            except Exception as e:
                error_count += 1
                # Continue to next subscription even if one fails
                continue
        
        db.session.commit()
        
        if success_count > 0:
            flash(f'✅ Successfully generated {success_count} invoice(s)! Total: ₹{total_amount:,.2f}', 'success')
        
        if error_count > 0:
            flash(f'⚠️ Failed to generate {error_count} invoice(s). Please check individual subscriptions.', 'warning')
        
        return redirect(url_for('invoices.index'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error generating invoices: {str(e)}', 'error')
        return redirect(url_for('subscriptions.deliveries'))

