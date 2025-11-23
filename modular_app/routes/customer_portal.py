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
from models import db, Customer, CustomerSubscription, SubscriptionDelivery, Invoice, SubscriptionPlan, Item, ItemCategory, CustomerOrder, CustomerOrderItem
from utils.tenant_middleware import require_tenant, get_current_tenant
from utils.email_utils import send_customer_order_notification
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
                         timedelta=timedelta,  # For date calculations in template
                         today=datetime.now().date(),  # Current date
                         tomorrow=datetime.now().date() + timedelta(days=1))  # Tomorrow's date


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


# ============================================================================
# PRODUCT ORDERING ROUTES
# ============================================================================

@customer_portal_bp.route('/products')
@require_tenant
@customer_login_required
def browse_products():
    """Browse products available for ordering"""
    customer = Customer.query.get(session['customer_id'])
    
    # Get search and filter params
    search_query = request.args.get('search', '').strip()
    category_id = request.args.get('category', type=int)
    
    # Base query - all active items
    query = Item.query.filter_by(tenant_id=g.tenant.id, is_active=True)
    
    # Apply search
    if search_query:
        query = query.filter(
            or_(
                Item.name.ilike(f'%{search_query}%'),
                Item.item_code.ilike(f'%{search_query}%'),
                Item.description.ilike(f'%{search_query}%')
            )
        )
    
    # Apply category filter
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    items = query.order_by(Item.name).all()
    
    # Get all categories for filter dropdown
    categories = ItemCategory.query.filter_by(tenant_id=g.tenant.id).order_by(ItemCategory.name).all()
    
    return render_template('customer_portal/products.html',
                         tenant=g.tenant,
                         customer=customer,
                         items=items,
                         categories=categories,
                         search_query=search_query,
                         selected_category=category_id)


@customer_portal_bp.route('/cart')
@require_tenant
@customer_login_required
def view_cart():
    """View shopping cart"""
    customer = Customer.query.get(session['customer_id'])
    
    # Cart stored in session
    cart = session.get('cart', {})
    cart_items = []
    subtotal = 0
    
    for item_id_str, qty in cart.items():
        item = Item.query.get(int(item_id_str))
        if item:
            amount = float(qty) * float(item.selling_price or 0)
            cart_items.append({
                'item': item,
                'quantity': qty,
                'rate': item.selling_price,
                'amount': amount
            })
            subtotal += amount
    
    return render_template('customer_portal/cart.html',
                         tenant=g.tenant,
                         customer=customer,
                         cart_items=cart_items,
                         subtotal=subtotal)


@customer_portal_bp.route('/cart/add/<int:item_id>', methods=['POST'])
@require_tenant
@customer_login_required
def add_to_cart(item_id):
    """Add item to cart"""
    quantity = float(request.form.get('quantity', 1))
    
    if quantity <= 0:
        flash('❌ Quantity must be greater than 0', 'error')
        return redirect(url_for('customer_portal.browse_products'))
    
    # Verify item exists
    item = Item.query.filter_by(id=item_id, tenant_id=g.tenant.id, is_active=True).first()
    if not item:
        flash('❌ Item not found', 'error')
        return redirect(url_for('customer_portal.browse_products'))
    
    # Get or create cart in session
    cart = session.get('cart', {})
    item_key = str(item_id)
    
    # Add or update quantity
    if item_key in cart:
        cart[item_key] = float(cart[item_key]) + quantity
    else:
        cart[item_key] = quantity
    
    session['cart'] = cart
    session.modified = True
    
    flash(f'✅ Added {quantity} x {item.name} to cart', 'success')
    return redirect(url_for('customer_portal.browse_products'))


@customer_portal_bp.route('/cart/remove/<int:item_id>', methods=['POST'])
@require_tenant
@customer_login_required
def remove_from_cart(item_id):
    """Remove item from cart"""
    cart = session.get('cart', {})
    item_key = str(item_id)
    
    if item_key in cart:
        del cart[item_key]
        session['cart'] = cart
        session.modified = True
        flash('✅ Item removed from cart', 'success')
    
    return redirect(url_for('customer_portal.view_cart'))


@customer_portal_bp.route('/cart/update', methods=['POST'])
@require_tenant
@customer_login_required
def update_cart():
    """Update cart quantities"""
    cart = session.get('cart', {})
    
    for item_id_str in list(cart.keys()):
        new_qty = request.form.get(f'qty_{item_id_str}', type=float)
        if new_qty and new_qty > 0:
            cart[item_id_str] = new_qty
        elif new_qty == 0:
            del cart[item_id_str]
    
    session['cart'] = cart
    session.modified = True
    flash('✅ Cart updated', 'success')
    return redirect(url_for('customer_portal.view_cart'))


@customer_portal_bp.route('/orders/place', methods=['POST'])
@require_tenant
@customer_login_required
def place_order():
    """Place order from cart"""
    customer = Customer.query.get(session['customer_id'])
    cart = session.get('cart', {})
    
    if not cart:
        flash('❌ Your cart is empty', 'error')
        return redirect(url_for('customer_portal.browse_products'))
    
    try:
        # Generate order number
        last_order = CustomerOrder.query.filter_by(tenant_id=g.tenant.id).order_by(CustomerOrder.id.desc()).first()
        if last_order and last_order.order_number:
            last_num = int(last_order.order_number.split('-')[-1])
            order_number = f'ORD-{last_num + 1:05d}'
        else:
            order_number = 'ORD-00001'
        
        # Create order
        order = CustomerOrder(
            tenant_id=g.tenant.id,
            customer_id=customer.id,
            order_number=order_number,
            order_date=datetime.now(),
            status='pending',
            notes=request.form.get('notes', '').strip()
        )
        
        # Add items
        subtotal = 0
        tax_total = 0
        
        for item_id_str, qty in cart.items():
            item = Item.query.get(int(item_id_str))
            if item:
                rate = float(item.selling_price or 0)
                amount = float(qty) * rate
                tax_rate = float(item.gst_rate or 0)
                tax_amt = amount * (tax_rate / 100)
                
                order_item = CustomerOrderItem(
                    item_id=item.id,
                    quantity=qty,
                    rate=rate,
                    amount=amount,
                    tax_rate=tax_rate,
                    tax_amount=tax_amt
                )
                order.items.append(order_item)
                
                subtotal += amount
                tax_total += tax_amt
        
        order.subtotal = subtotal
        order.tax_amount = tax_total
        order.total_amount = subtotal + tax_total
        
        db.session.add(order)
        db.session.commit()
        
        # Send email notification to admin
        if g.tenant.admin_email:
            send_customer_order_notification(
                admin_email=g.tenant.admin_email,
                customer_name=customer.name,
                order_number=order.order_number,
                total_amount=float(order.total_amount),
                items_count=len(order.items),
                tenant_name=g.tenant.subdomain
            )
        
        # Clear cart
        session['cart'] = {}
        session.modified = True
        
        flash(f'✅ Order #{order.order_number} placed successfully! We will fulfill it soon.', 'success')
        return redirect(url_for('customer_portal.view_orders'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error placing order: {str(e)}', 'error')
        return redirect(url_for('customer_portal.view_cart'))


@customer_portal_bp.route('/orders')
@require_tenant
@customer_login_required
def view_orders():
    """View order history"""
    customer = Customer.query.get(session['customer_id'])
    
    orders = CustomerOrder.query.filter_by(
        customer_id=customer.id
    ).order_by(CustomerOrder.order_date.desc()).all()
    
    return render_template('customer_portal/orders.html',
                         tenant=g.tenant,
                         customer=customer,
                         orders=orders)


@customer_portal_bp.route('/orders/<int:order_id>')
@require_tenant
@customer_login_required
def view_order_detail(order_id):
    """View order details"""
    customer = Customer.query.get(session['customer_id'])
    
    order = CustomerOrder.query.filter_by(
        id=order_id,
        customer_id=customer.id
    ).first_or_404()
    
    return render_template('customer_portal/order_detail.html',
                         tenant=g.tenant,
                         customer=customer,
                         order=order)

