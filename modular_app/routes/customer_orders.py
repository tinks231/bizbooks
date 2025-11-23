"""
Customer Orders Admin Routes
For managing orders placed by customers through customer portal
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g, jsonify
from models import db, CustomerOrder, CustomerOrderItem, Customer
from utils.tenant_middleware import require_tenant, get_current_tenant_id
from utils.license_check import check_license
from utils.email_utils import send_order_confirmed_notification, send_order_fulfilled_notification, send_order_cancelled_notification
from functools import wraps
from datetime import datetime
from sqlalchemy import desc, and_, or_

customer_orders_bp = Blueprint('customer_orders', __name__, url_prefix='/admin/customer-orders')


# Login required decorator (matches admin.py pattern EXACTLY)
def login_required(f):
    @wraps(f)
    @check_license  # ← Check license INSIDE decorator (runs AFTER login check)
    def decorated_function(*args, **kwargs):
        if 'tenant_admin_id' not in session:
            flash('Please login first', 'error')
            return redirect(url_for('admin.login'))
        # Verify session tenant matches current tenant
        if session.get('tenant_admin_id') != get_current_tenant_id():
            session.clear()
            flash('Session mismatch. Please login again.', 'error')
            return redirect(url_for('admin.login'))
        session.permanent = True
        return f(*args, **kwargs)
    return decorated_function


@customer_orders_bp.route('/')
@require_tenant
@login_required
def index():
    """List all customer orders"""
    # Get filter params
    status_filter = request.args.get('status', '').strip()
    search_query = request.args.get('search', '').strip()
    
    # Base query
    query = CustomerOrder.query.filter_by(tenant_id=g.tenant.id)
    
    # Apply status filter
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    # Apply search
    if search_query:
        query = query.join(Customer).filter(
            or_(
                CustomerOrder.order_number.ilike(f'%{search_query}%'),
                Customer.name.ilike(f'%{search_query}%'),
                Customer.phone.ilike(f'%{search_query}%')
            )
        )
    
    orders = query.order_by(desc(CustomerOrder.order_date)).all()
    
    # Count by status
    pending_count = CustomerOrder.query.filter_by(tenant_id=g.tenant.id, status='pending').count()
    confirmed_count = CustomerOrder.query.filter_by(tenant_id=g.tenant.id, status='confirmed').count()
    fulfilled_count = CustomerOrder.query.filter_by(tenant_id=g.tenant.id, status='fulfilled').count()
    
    return render_template('admin/customer_orders/list.html',
                         tenant=g.tenant,
                         orders=orders,
                         status_filter=status_filter,
                         search_query=search_query,
                         pending_count=pending_count,
                         confirmed_count=confirmed_count,
                         fulfilled_count=fulfilled_count)


@customer_orders_bp.route('/<int:order_id>')
@require_tenant
@login_required
def view_order(order_id):
    """View order details"""
    print(f"\n🔍 VIEW ORDER DEBUG:")
    print(f"   Order ID: {order_id}")
    print(f"   Session tenant_admin_id: {session.get('tenant_admin_id')}")
    print(f"   Current tenant ID: {g.tenant.id}")
    print(f"   Session keys: {list(session.keys())}")
    
    order = CustomerOrder.query.filter_by(
        id=order_id,
        tenant_id=g.tenant.id
    ).first_or_404()
    
    return render_template('admin/customer_orders/view.html',
                         tenant=g.tenant,
                         order=order)


@customer_orders_bp.route('/<int:order_id>/update-status', methods=['POST'])
@require_tenant
@login_required
def update_status(order_id):
    """Update order status"""
    print(f"\n🔍 UPDATE STATUS DEBUG:")
    print(f"   Order ID: {order_id}")
    print(f"   Session tenant_admin_id: {session.get('tenant_admin_id')}")
    print(f"   Current tenant ID: {g.tenant.id}")
    print(f"   Session keys: {list(session.keys())}")
    print(f"   Form data: {request.form}")
    
    order = CustomerOrder.query.filter_by(
        id=order_id,
        tenant_id=g.tenant.id
    ).first_or_404()
    
    new_status = request.form.get('status', '').strip()
    admin_notes = request.form.get('admin_notes', '').strip()
    
    if new_status not in ['pending', 'confirmed', 'fulfilled', 'cancelled']:
        flash('❌ Invalid status', 'error')
        return redirect(url_for('customer_orders.view_order', order_id=order_id))
    
    try:
        old_status = order.status
        order.status = new_status
        if admin_notes:
            order.admin_notes = admin_notes
        
        # If fulfilled, set fulfilled date and user
        if new_status == 'fulfilled' and not order.fulfilled_date:
            order.fulfilled_date = datetime.now()
            # Note: tenant_admin_id is the tenant ID, not a user ID
            # For now, leave fulfilled_by as None (can be enhanced later)
            order.fulfilled_by = None
        
        order.updated_at = datetime.now()
        db.session.commit()
        
        # Send email notification to customer (if email exists and status changed)
        if order.customer.email and old_status != new_status:
            if new_status == 'confirmed':
                send_order_confirmed_notification(
                    customer_email=order.customer.email,
                    customer_name=order.customer.name,
                    order_number=order.order_number,
                    total_amount=float(order.total_amount),
                    items_count=len(order.items),
                    tenant_name=g.tenant.subdomain
                )
            elif new_status == 'fulfilled':
                send_order_fulfilled_notification(
                    customer_email=order.customer.email,
                    customer_name=order.customer.name,
                    order_number=order.order_number,
                    total_amount=float(order.total_amount),
                    items_count=len(order.items),
                    tenant_name=g.tenant.subdomain
                )
            elif new_status == 'cancelled':
                send_order_cancelled_notification(
                    customer_email=order.customer.email,
                    customer_name=order.customer.name,
                    order_number=order.order_number,
                    total_amount=float(order.total_amount),
                    items_count=len(order.items),
                    tenant_name=g.tenant.subdomain,
                    reason=admin_notes
                )
        
        flash(f'✅ Order status updated to {new_status.upper()}', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error updating order: {str(e)}', 'error')
    
    return redirect(url_for('customer_orders.view_order', order_id=order_id))


@customer_orders_bp.route('/<int:order_id>/delete', methods=['POST'])
@require_tenant
@login_required
def delete_order(order_id):
    """Delete order"""
    order = CustomerOrder.query.filter_by(
        id=order_id,
        tenant_id=g.tenant.id
    ).first_or_404()
    
    try:
        order_number = order.order_number
        db.session.delete(order)
        db.session.commit()
        flash(f'✅ Order {order_number} deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error deleting order: {str(e)}', 'error')
    
    return redirect(url_for('customer_orders.index'))


@customer_orders_bp.route('/count')
@require_tenant
def get_pending_count():
    """API endpoint to get pending orders count for badge"""
    try:
        if not g.tenant:
            return jsonify({'count': 0})
        
        count = CustomerOrder.query.filter_by(
            tenant_id=g.tenant.id,
            status='pending'
        ).count()
        
        return jsonify({'count': count})
    except:
        return jsonify({'count': 0})

