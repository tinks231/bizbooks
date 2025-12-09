"""
Customer Orders Admin Routes
For managing orders placed by customers through customer portal
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g, jsonify
from models import db, CustomerOrder, CustomerOrderItem, Customer, Invoice, InvoiceItem, Item, ItemStock, ItemStockMovement, Site
from utils.tenant_middleware import require_tenant, get_current_tenant_id
from utils.license_check import check_license
from utils.email_utils import send_order_confirmed_notification, send_order_fulfilled_notification, send_order_cancelled_notification, send_invoice_email
from functools import wraps
from datetime import datetime, date
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


@customer_orders_bp.route('/', strict_slashes=False)  # PERFORMANCE: Prevent 308 redirects
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


@customer_orders_bp.route('/<int:order_id>/generate-invoice', methods=['POST'])
@require_tenant
@login_required
def generate_invoice(order_id):
    """Generate invoice from customer order (auto-deducts inventory)"""
    order = CustomerOrder.query.filter_by(
        id=order_id,
        tenant_id=g.tenant.id
    ).first_or_404()
    
    # Check if invoice already generated
    if order.invoice_id:
        flash('⚠️ Invoice already generated for this order!', 'warning')
        return redirect(url_for('customer_orders.view_order', order_id=order_id))
    
    try:
        # Generate invoice number (INV-YYYY-NNN)
        today = date.today()
        year = today.year
        existing_invoices = Invoice.query.filter(
            Invoice.tenant_id == g.tenant.id,
            Invoice.invoice_number.like(f'INV-{year}-%')
        ).count()
        invoice_number = f"INV-{year}-{existing_invoices + 1:03d}"
        
        # Create invoice
        invoice = Invoice(
            tenant_id=g.tenant.id,
            invoice_number=invoice_number,
            invoice_date=today,
            customer_id=order.customer_id,
            customer_name=order.customer.name,
            customer_phone=order.customer.phone,
            customer_email=order.customer.email,
            customer_address=order.customer.address,
            customer_gstin=order.customer.gstin,
            customer_state=order.customer.state,
            subtotal=float(order.subtotal),
            cgst_amount=0,  # Will calculate from items
            sgst_amount=0,
            igst_amount=0,
            total_amount=float(order.total_amount),
            payment_status='unpaid',
            status='sent',
            notes='Generated from customer order'
        )
        db.session.add(invoice)
        db.session.flush()  # Get invoice ID
        
        # Get default site for inventory deduction
        default_site = Site.query.filter_by(tenant_id=g.tenant.id).first()
        
        total_cgst = 0
        total_sgst = 0
        total_igst = 0
        
        # Create invoice items and deduct inventory
        for order_item in order.items:
            item = order_item.item
            quantity = float(order_item.quantity)
            rate = float(order_item.rate)
            gst_rate = float(order_item.tax_rate) if order_item.tax_rate else 0
            
            # Calculate GST split
            # Note: Since Tenant model doesn't have address_state, we default to same state (CGST+SGST)
            # You can add tenant state field later if needed for inter-state GST
            is_same_state = True  # Default to CGST+SGST
            
            if is_same_state:
                cgst = (quantity * rate * gst_rate) / 200  # Half of GST
                sgst = (quantity * rate * gst_rate) / 200  # Half of GST
                igst = 0
                total_cgst += cgst
                total_sgst += sgst
            else:
                cgst = 0
                sgst = 0
                igst = (quantity * rate * gst_rate) / 100
                total_igst += igst
            
            # Create invoice item
            taxable_value = quantity * rate
            total_amount = taxable_value + cgst + sgst + igst
            
            invoice_item = InvoiceItem(
                invoice_id=invoice.id,
                item_id=item.id,
                item_name=item.name,
                hsn_code=item.hsn_code or '',
                quantity=quantity,
                unit=item.unit or 'Nos',
                rate=rate,
                gst_rate=gst_rate,
                taxable_value=taxable_value,
                cgst_amount=cgst,
                sgst_amount=sgst,
                igst_amount=igst,
                total_amount=total_amount
            )
            db.session.add(invoice_item)
            
            # Deduct inventory (if item tracks inventory)
            if item.track_inventory and default_site:
                item_stock = ItemStock.query.filter_by(
                    tenant_id=g.tenant.id,
                    item_id=item.id,
                    site_id=default_site.id
                ).first()
                
                if item_stock:
                    # Check stock availability
                    if item_stock.quantity_available < quantity:
                        flash(f'⚠️ Warning: {item.name} has insufficient stock! Available: {item_stock.quantity_available:.2f}, Selling: {quantity}', 'warning')
                    
                    # Reduce stock
                    old_qty = item_stock.quantity_available
                    item_stock.quantity_available -= quantity
                    new_qty = item_stock.quantity_available
                    
                    # Update stock value
                    if item.cost_price:
                        item_stock.stock_value = new_qty * item.cost_price
                    
                    # Create stock movement record
                    stock_movement = ItemStockMovement(
                        tenant_id=g.tenant.id,
                        item_id=item.id,
                        site_id=default_site.id,
                        movement_type='stock_out',
                        quantity=quantity,
                        unit_cost=item.cost_price or 0,
                        total_value=quantity * (item.cost_price or 0),
                        reference_type='invoice',
                        reference_id=invoice.id,
                        reference_number=invoice_number,
                        notes=f'Sold via invoice {invoice_number} (Customer Order: {order.order_number})'
                    )
                    db.session.add(stock_movement)
        
        # Update invoice GST amounts
        invoice.cgst_amount = total_cgst
        invoice.sgst_amount = total_sgst
        invoice.igst_amount = total_igst
        
        # Link invoice to order
        order.invoice_id = invoice.id
        order.status = 'fulfilled'
        order.fulfilled_date = datetime.now()
        order.updated_at = datetime.now()
        
        # Check if payment should be recorded immediately
        mark_paid = request.form.get('mark_paid')
        if mark_paid:
            payment_method = request.form.get('payment_method', 'Cash')
            payment_notes = request.form.get('payment_notes', '')
            
            # Mark invoice as paid
            invoice.payment_status = 'paid'
            invoice.paid_amount = float(invoice.total_amount)
            invoice.payment_method = payment_method
            
            # Add payment notes
            if payment_notes:
                invoice.notes = f"{invoice.notes}\n\nPayment Notes: {payment_notes}" if invoice.notes else f"Payment Notes: {payment_notes}"
        
        db.session.commit()
        
        # Send invoice email to customer (with PDF attachment)
        if order.customer.email:
            try:
                send_invoice_email(
                    customer_email=order.customer.email,
                    customer_name=order.customer.name,
                    invoice_number=invoice_number,
                    invoice_id=invoice.id,
                    total_amount=float(invoice.total_amount),
                    tenant_name=g.tenant.company_name,
                    tenant_subdomain=g.tenant.subdomain,
                    invoice=invoice,  # Pass invoice object for PDF generation
                    tenant=g.tenant   # Pass tenant object for PDF generation
                )
                payment_status_msg = " and marked as PAID" if mark_paid else ""
                flash(f'✅ Invoice {invoice_number} generated{payment_status_msg} and emailed with PDF attachment!', 'success')
            except Exception as email_error:
                payment_status_msg = " and marked as PAID" if mark_paid else ""
                flash(f'✅ Invoice {invoice_number} generated{payment_status_msg}, but email failed: {str(email_error)}', 'warning')
                print(f"📧 Email error details: {email_error}")
                import traceback
                traceback.print_exc()
        else:
            payment_status_msg = " and marked as PAID" if mark_paid else ""
            flash(f'✅ Invoice {invoice_number} generated{payment_status_msg}! (Customer has no email)', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error generating invoice: {str(e)}', 'error')
        print(f"❌ Invoice generation error: {e}")
        import traceback
        traceback.print_exc()
    
    return redirect(url_for('customer_orders.view_order', order_id=order_id))


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

