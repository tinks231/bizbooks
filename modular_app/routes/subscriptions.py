"""
Subscription Management Routes

Handles subscription plans, member enrollment,
payment collection, and recurring billing.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from models import db, SubscriptionPlan, CustomerSubscription, SubscriptionPayment, Customer, Invoice, InvoiceItem
from utils.tenant_utils import require_tenant, get_current_tenant, get_current_tenant_id
from utils.license_check import check_license
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy import func, or_

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
        if 'tenant_id' not in session:
            flash('⚠️ Please login first', 'warning')
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function


# ============================================================
# SUBSCRIPTION PLANS CRUD
# ============================================================
@subscriptions_bp.route('/plans', methods=['GET'], strict_slashes=False)
@require_tenant
@check_license
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
@check_license
@login_required
def add_plan():
    """Add new subscription plan"""
    tenant_id = get_current_tenant_id()
    
    try:
        plan = SubscriptionPlan(
            tenant_id=tenant_id,
            name=request.form['name'],
            description=request.form.get('description', ''),
            price=Decimal(request.form['price']),
            duration_days=int(request.form['duration_days']),
            is_active=True
        )
        
        db.session.add(plan)
        db.session.commit()
        
        flash(f'✅ Plan "{plan.name}" created successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error creating plan: {str(e)}', 'error')
    
    return redirect(url_for('subscriptions.plans'))


@subscriptions_bp.route('/plans/edit/<int:plan_id>', methods=['POST'], strict_slashes=False)
@require_tenant
@check_license
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
@check_license
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
@check_license
@login_required
def members():
    """List all active members with subscriptions"""
    tenant_id = get_current_tenant_id()
    
    # Get filter parameters
    status_filter = request.args.get('status', 'active')
    search_query = request.args.get('search', '').strip()
    plan_filter = request.args.get('plan', '')
    
    # Base query with eager loading
    query = CustomerSubscription.query.join(Customer).join(SubscriptionPlan).filter(
        CustomerSubscription.tenant_id == tenant_id
    )
    
    # Apply filters
    if status_filter == 'active':
        query = query.filter(CustomerSubscription.status == 'active')
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
        query = query.filter(
            or_(
                Customer.name.ilike(f'%{search_query}%'),
                Customer.phone.ilike(f'%{search_query}%')
            )
        )
    
    # Plan filter
    if plan_filter:
        query = query.filter(SubscriptionPlan.id == int(plan_filter))
    
    # Get subscriptions with pagination
    page = request.args.get('page', 1, type=int)
    per_page = 50
    pagination = query.order_by(
        CustomerSubscription.current_period_end.asc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    subscriptions_list = pagination.items
    
    # Stats
    today = datetime.now().date()
    three_days = today + timedelta(days=3)
    
    stats = {
        'active': CustomerSubscription.query.filter_by(tenant_id=tenant_id, status='active').count(),
        'due_soon': CustomerSubscription.query.filter(
            CustomerSubscription.tenant_id == tenant_id,
            CustomerSubscription.status == 'active',
            CustomerSubscription.current_period_end <= three_days
        ).count(),
        'overdue': CustomerSubscription.query.filter(
            CustomerSubscription.tenant_id == tenant_id,
            CustomerSubscription.status == 'active',
            CustomerSubscription.current_period_end < today
        ).count(),
        'expired': CustomerSubscription.query.filter_by(tenant_id=tenant_id, status='expired').count()
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
@check_license
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
        payment_amount = Decimal(request.form['payment_amount'])
        payment_mode = request.form['payment_mode']
        generate_invoice = request.form.get('generate_invoice') == 'on'
        
        # Parse start date
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        
        # Get plan
        plan = SubscriptionPlan.query.filter_by(id=plan_id, tenant_id=tenant_id).first_or_404()
        
        # Calculate period end
        period_end = start_date + timedelta(days=plan.duration_days)
        
        # Create subscription
        subscription = CustomerSubscription(
            tenant_id=tenant_id,
            customer_id=customer_id,
            plan_id=plan_id,
            start_date=start_date,
            current_period_start=start_date,
            current_period_end=period_end,
            status='active',
            auto_renew=True
        )
        
        db.session.add(subscription)
        db.session.flush()  # Get subscription ID
        
        # Record payment
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
                invoice_date=start_date,
                invoice_number=f"SUB-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                total_amount=payment_amount,
                balance_due=Decimal('0.00'),  # Paid in full
                status='paid',
                payment_mode=payment_mode
            )
            
            db.session.add(invoice)
            db.session.flush()
            
            # Add invoice item
            item = InvoiceItem(
                tenant_id=tenant_id,
                invoice_id=invoice.id,
                description=f"{plan.name} - {billing_period_label}",
                quantity=1,
                unit_price=payment_amount,
                total=payment_amount
            )
            
            db.session.add(item)
            
            # Link payment to invoice
            payment.invoice_id = invoice.id
        
        db.session.commit()
        
        flash(f'✅ Customer enrolled successfully in "{plan.name}"!', 'success')
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
@check_license
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
@check_license
@login_required
def collect_payment(subscription_id):
    """Collect payment and renew subscription"""
    tenant_id = get_current_tenant_id()
    
    subscription = CustomerSubscription.query.filter_by(
        id=subscription_id,
        tenant_id=tenant_id
    ).first_or_404()
    
    if request.method == 'GET':
        # Show payment collection form
        return render_template('admin/subscriptions/collect_payment.html',
                             subscription=subscription)
    
    # POST - Process payment
    try:
        payment_amount = Decimal(request.form['payment_amount'])
        payment_mode = request.form['payment_mode']
        payment_date_str = request.form.get('payment_date', datetime.now().strftime('%Y-%m-%d'))
        generate_invoice = request.form.get('generate_invoice') == 'on'
        
        payment_date = datetime.strptime(payment_date_str, '%Y-%m-%d').date()
        
        # Calculate new period
        new_period_start = subscription.current_period_end + timedelta(days=1)
        new_period_end = new_period_start + timedelta(days=subscription.plan.duration_days)
        
        # Create billing label
        billing_period_label = new_period_start.strftime('%b %Y') if subscription.plan.duration_days == 30 else f"{new_period_start.strftime('%b')}-{new_period_end.strftime('%b %Y')}"
        
        # Record payment
        payment = SubscriptionPayment(
            tenant_id=tenant_id,
            subscription_id=subscription.id,
            payment_date=payment_date,
            amount=payment_amount,
            payment_mode=payment_mode,
            period_start=new_period_start,
            period_end=new_period_end,
            billing_period_label=billing_period_label
        )
        
        db.session.add(payment)
        
        # Renew subscription
        subscription.renew_subscription()
        
        # Generate invoice if requested
        if generate_invoice:
            invoice = Invoice(
                tenant_id=tenant_id,
                customer_id=subscription.customer_id,
                invoice_date=payment_date,
                invoice_number=f"SUB-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                total_amount=payment_amount,
                balance_due=Decimal('0.00'),
                status='paid',
                payment_mode=payment_mode
            )
            
            db.session.add(invoice)
            db.session.flush()
            
            # Add invoice item
            item = InvoiceItem(
                tenant_id=tenant_id,
                invoice_id=invoice.id,
                description=f"{subscription.plan.name} - {billing_period_label}",
                quantity=1,
                unit_price=payment_amount,
                total=payment_amount
            )
            
            db.session.add(item)
            
            # Link payment to invoice
            payment.invoice_id = invoice.id
        
        db.session.commit()
        
        flash(f'✅ Payment collected successfully! Subscription renewed until {new_period_end.strftime("%d %b %Y")}', 'success')
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
@check_license
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

