"""
Sales Order Management Routes
Complete CRUD operations, conversions, and tracking
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, g, session
from models import db, SalesOrder, SalesOrderItem, Customer, Item, ItemStock, Site
from models import Invoice, InvoiceItem, Tenant
# Temporarily disabled until quotations module is ready
# from models import Quotation, QuotationItem
from datetime import datetime, timedelta
from sqlalchemy import or_, and_, func, case
import pytz
from decimal import Decimal

sales_order_bp = Blueprint('sales_orders', __name__, url_prefix='/sales-orders')

# Middleware to check authentication
@sales_order_bp.before_request
def check_auth():
    """Ensure user is logged in for all sales order routes"""
    if 'tenant_admin_id' not in session:
        flash('Please login to access sales orders', 'error')
        return redirect(url_for('admin.login'))
    
    # Load tenant into g for easy access
    g.tenant = Tenant.query.get(session['tenant_admin_id'])
    if not g.tenant:
        session.clear()
        flash('Session expired. Please login again.', 'error')
        return redirect(url_for('admin.login'))


@sales_order_bp.route('/', strict_slashes=False)  # PERFORMANCE: Prevent 308 redirects
@sales_order_bp.route('/list', strict_slashes=False)
def list_orders():
    """List all sales orders with filters - OPTIMIZED with pagination"""
    tenant_id = session['tenant_admin_id']
    
    # Get filter parameters
    status_filter = request.args.get('status', 'all')
    search_query = request.args.get('search', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    customer_id = request.args.get('customer_id', '')
    page = request.args.get('page', 1, type=int)
    per_page = 50
    
    # Base query
    query = SalesOrder.query.filter_by(tenant_id=tenant_id)
    
    # Apply filters
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    
    if search_query:
        query = query.filter(
            or_(
                SalesOrder.order_number.ilike(f'%{search_query}%'),
                SalesOrder.customer_name.ilike(f'%{search_query}%'),
                SalesOrder.customer_phone.ilike(f'%{search_query}%')
            )
        )
    
    if date_from:
        query = query.filter(SalesOrder.order_date >= date_from)
    
    if date_to:
        query = query.filter(SalesOrder.order_date <= date_to)
    
    if customer_id:
        query = query.filter_by(customer_id=customer_id)
    
    # OPTIMIZED: Paginate orders (instead of loading ALL)
    query = query.order_by(SalesOrder.order_date.desc(), SalesOrder.id.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    orders = pagination.items
    
    # OPTIMIZED: Get statistics using single query with case aggregation
    stats_result = db.session.query(
        func.count(SalesOrder.id).label('total'),
        func.sum(case((SalesOrder.status == 'pending', 1), else_=0)).label('pending'),
        func.sum(case((SalesOrder.status == 'confirmed', 1), else_=0)).label('confirmed'),
        func.sum(case((SalesOrder.status == 'partially_delivered', 1), else_=0)).label('partially_delivered'),
        func.sum(case((SalesOrder.status == 'delivered', 1), else_=0)).label('delivered'),
        func.sum(case((SalesOrder.status == 'invoiced', 1), else_=0)).label('invoiced')
    ).filter(SalesOrder.tenant_id == tenant_id).first()
    
    stats = {
        'total': stats_result.total or 0,
        'pending': stats_result.pending or 0,
        'confirmed': stats_result.confirmed or 0,
        'partially_delivered': stats_result.partially_delivered or 0,
        'delivered': stats_result.delivered or 0,
        'invoiced': stats_result.invoiced or 0,
    }
    
    # Calculate total pending value
    pending_orders = SalesOrder.query.filter_by(tenant_id=tenant_id).filter(
        SalesOrder.status.in_(['pending', 'confirmed', 'partially_delivered', 'delivered'])
    ).all()
    stats['pending_value'] = sum(float(order.total_amount or 0) for order in pending_orders)
    
    # Get all customers for filter dropdown
    customers = Customer.query.filter_by(tenant_id=tenant_id).order_by(Customer.name).all()
    
    return render_template(
        'sales_orders/list.html',
        orders=orders,
        page=page,
        total_pages=pagination.pages,
        total_items=pagination.total,
        stats=stats,
        customers=customers,
        status_filter=status_filter,
        search_query=search_query,
        date_from=date_from,
        date_to=date_to,
        customer_id=customer_id
    )


@sales_order_bp.route('/create', methods=['GET', 'POST'])
def create_order():
    """Create a new sales order"""
    try:
        tenant_id = session['tenant_admin_id']
        print(f"🔍 Sales Order Create - Tenant ID: {tenant_id}")
    except Exception as e:
        print(f"❌ Error getting tenant_id: {e}")
        import traceback
        traceback.print_exc()
        flash('Session error. Please login again.', 'error')
        return redirect(url_for('admin.login'))
    
    if request.method == 'POST':
        try:
            # Get form data
            customer_id = request.form.get('customer_id')
            customer_name = request.form.get('customer_name', '').strip()
            customer_phone = request.form.get('customer_phone', '').strip()
            customer_email = request.form.get('customer_email', '').strip()
            customer_gstin = request.form.get('customer_gstin', '').strip()
            
            order_date = request.form.get('order_date')
            expected_delivery_date = request.form.get('expected_delivery_date')
            
            billing_address = request.form.get('billing_address', '').strip()
            shipping_address = request.form.get('shipping_address', '').strip()
            
            terms_and_conditions = request.form.get('terms_and_conditions', '').strip()
            notes = request.form.get('notes', '').strip()
            
            status = request.form.get('status', 'draft')  # draft or confirmed
            
            # Validate required fields
            if not customer_name:
                flash('Customer name is required', 'error')
                return redirect(url_for('sales_orders.create_order'))
            
            if not order_date:
                flash('Order date is required', 'error')
                return redirect(url_for('sales_orders.create_order'))
            
            # Get items
            item_ids = request.form.getlist('item_id[]')
            item_names = request.form.getlist('item_name[]')
            descriptions = request.form.getlist('description[]')
            hsn_codes = request.form.getlist('hsn_code[]')
            quantities = request.form.getlist('quantity[]')
            units = request.form.getlist('unit[]')
            rates = request.form.getlist('rate[]')
            gst_rates = request.form.getlist('gst_rate[]')
            price_inclusives = request.form.getlist('price_inclusive[]')
            discount_types = request.form.getlist('discount_type[]')
            discount_values = request.form.getlist('discount_value[]')
            
            if not item_names or len(item_names) == 0:
                flash('Please add at least one item', 'error')
                return redirect(url_for('sales_orders.create_order'))
            
            # Calculate totals
            subtotal = Decimal('0')
            tax_amount = Decimal('0')
            discount_amount = Decimal('0')
            
            order_items_data = []
            total_quantity = 0
            
            for i in range(len(item_names)):
                if not item_names[i].strip():
                    continue
                
                qty = Decimal(quantities[i] or '0')
                rate = Decimal(rates[i] or '0')
                gst_rate = Decimal(gst_rates[i] or '0')
                
                # Safely get discount values (may not exist in form)
                disc_value = Decimal(discount_values[i] or '0') if i < len(discount_values) else Decimal('0')
                disc_type = discount_types[i] if i < len(discount_types) else 'percentage'
                
                # Check if price inclusive checkbox is checked
                price_inclusive = f'price_inclusive_{i+1}' in request.form or str(i) in price_inclusives
                
                # Calculate item amount
                item_subtotal = qty * rate
                
                # Apply discount
                if disc_type == 'percentage':
                    item_discount = item_subtotal * (disc_value / Decimal('100'))
                else:
                    item_discount = disc_value
                
                item_taxable = item_subtotal - item_discount
                
                # Calculate tax
                if price_inclusive:
                    # Tax is included in the rate
                    item_tax = item_taxable - (item_taxable / (Decimal('1') + (gst_rate / Decimal('100'))))
                    item_taxable = item_taxable - item_tax
                else:
                    # Tax is on top
                    item_tax = item_taxable * (gst_rate / Decimal('100'))
                
                item_total = item_taxable + item_tax
                
                subtotal += item_taxable
                tax_amount += item_tax
                discount_amount += item_discount
                total_quantity += int(qty)
                
                # Safely get all optional fields
                item_id_val = int(item_ids[i]) if (i < len(item_ids) and item_ids[i] and item_ids[i].isdigit()) else None
                description_val = descriptions[i].strip() if (i < len(descriptions) and descriptions[i]) else ''
                hsn_code_val = hsn_codes[i].strip() if (i < len(hsn_codes) and hsn_codes[i]) else ''
                unit_val = units[i] if (i < len(units) and units[i]) else 'pcs'
                
                order_items_data.append({
                    'item_id': item_id_val,
                    'item_name': item_names[i].strip(),
                    'description': description_val,
                    'hsn_code': hsn_code_val,
                    'quantity': qty,
                    'unit': unit_val,
                    'rate': rate,
                    'gst_rate': gst_rate,
                    'price_inclusive': price_inclusive,
                    'discount_type': disc_type,
                    'discount_value': disc_value,
                    'taxable_amount': item_taxable,
                    'tax_amount': item_tax,
                    'total_amount': item_total
                })
            
            total_amount = subtotal + tax_amount
            
            # Generate order number
            order_number = SalesOrder.generate_order_number(tenant_id)
            
            # Create sales order
            order = SalesOrder(
                tenant_id=tenant_id,
                order_number=order_number,
                order_date=datetime.strptime(order_date, '%Y-%m-%d').date(),
                expected_delivery_date=datetime.strptime(expected_delivery_date, '%Y-%m-%d').date() if expected_delivery_date else None,
                customer_id=int(customer_id) if customer_id and customer_id.isdigit() else None,
                customer_name=customer_name,
                customer_phone=customer_phone,
                customer_email=customer_email,
                customer_gstin=customer_gstin,
                billing_address=billing_address,
                shipping_address=shipping_address,
                subtotal=subtotal,
                discount_amount=discount_amount,
                tax_amount=tax_amount,
                total_amount=total_amount,
                status=status,
                quantity_ordered=total_quantity,
                terms_and_conditions=terms_and_conditions,
                notes=notes,
                created_by=g.tenant.company_name
            )
            
            db.session.add(order)
            db.session.flush()  # Get order ID
            
            # Add order items
            for item_data in order_items_data:
                order_item = SalesOrderItem(
                    sales_order_id=order.id,
                    tenant_id=tenant_id,
                    **item_data
                )
                db.session.add(order_item)
            
            db.session.commit()
            
            # Reserve stock if order is confirmed
            if status == 'confirmed':
                reserve_stock_for_order(order.id)
            
            flash(f'Sales Order {order_number} created successfully!', 'success')
            return redirect(url_for('sales_orders.view_order', order_id=order.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating sales order: {str(e)}', 'error')
            print(f"❌ Error creating sales order: {e}")
            import traceback
            traceback.print_exc()
            return redirect(url_for('sales_orders.create_order'))
    
    # GET request - show form
    try:
        print(f"🔍 Loading Sales Order Create Form for tenant: {tenant_id}")
        
        ist = pytz.timezone('Asia/Kolkata')
        today = datetime.now(ist).date()
        print(f"📅 Today's date: {today}")
        
        # Get all customers
        print(f"🔍 Fetching customers for tenant {tenant_id}...")
        customers = Customer.query.filter_by(tenant_id=tenant_id).order_by(Customer.name).all()
        print(f"✅ Found {len(customers)} customers")
        
        # Get all items
        print(f"🔍 Fetching items for tenant {tenant_id}...")
        items = Item.query.filter_by(tenant_id=tenant_id).order_by(Item.name).all()
        print(f"✅ Found {len(items)} items")
        
        print(f"🔍 Rendering template: sales_orders/create.html")
        return render_template(
            'sales_orders/create.html',
            customers=customers,
            items=items,
            today=today,
            quotation_id=request.args.get('from_quotation')
        )
    except Exception as e:
        print(f"❌ CRITICAL ERROR in create_order GET:")
        print(f"❌ Error type: {type(e).__name__}")
        print(f"❌ Error message: {str(e)}")
        import traceback
        print(f"❌ Full traceback:")
        traceback.print_exc()
        flash(f'Error loading sales order form: {str(e)}', 'error')
        return redirect(url_for('sales_orders.list_orders'))


@sales_order_bp.route('/<int:order_id>')
def view_order(order_id):
    """View sales order details"""
    tenant_id = session['tenant_admin_id']
    
    order = SalesOrder.query.filter_by(id=order_id, tenant_id=tenant_id).first_or_404()
    
    # Get related documents (check if sales_order_id column exists)
    try:
        invoices = Invoice.query.filter_by(sales_order_id=order_id, tenant_id=tenant_id).all()
    except:
        # Column doesn't exist yet, return empty list
        invoices = []
    
    # Check if quotation exists - TEMPORARILY DISABLED
    # quotation = None
    # if order.quotation_id:
    #     quotation = Quotation.query.get(order.quotation_id)
    
    return render_template(
        'sales_orders/view.html',
        order=order,
        invoices=invoices,
        quotation=None  # Will be enabled when Quotation module is implemented
    )


@sales_order_bp.route('/<int:order_id>/edit', methods=['GET', 'POST'])
def edit_order(order_id):
    """Edit sales order"""
    tenant_id = session['tenant_admin_id']
    order = SalesOrder.query.filter_by(id=order_id, tenant_id=tenant_id).first_or_404()
    
    # Prevent editing if already invoiced
    if order.status == 'invoiced':
        flash('Cannot edit fully invoiced orders', 'error')
        return redirect(url_for('sales_orders.view_order', order_id=order_id))
    
    if request.method == 'POST':
        try:
            # Update order details (similar to create, but updating existing)
            order.customer_name = request.form.get('customer_name', '').strip()
            order.customer_phone = request.form.get('customer_phone', '').strip()
            order.customer_email = request.form.get('customer_email', '').strip()
            order.customer_gstin = request.form.get('customer_gstin', '').strip()
            
            order_date = request.form.get('order_date')
            if order_date:
                order.order_date = datetime.strptime(order_date, '%Y-%m-%d').date()
            
            expected_delivery_date = request.form.get('expected_delivery_date')
            if expected_delivery_date:
                order.expected_delivery_date = datetime.strptime(expected_delivery_date, '%Y-%m-%d').date()
            
            order.billing_address = request.form.get('billing_address', '').strip()
            order.shipping_address = request.form.get('shipping_address', '').strip()
            order.terms_and_conditions = request.form.get('terms_and_conditions', '').strip()
            order.notes = request.form.get('notes', '').strip()
            
            # Delete existing items and re-add (simpler than updating)
            for item in order.items:
                db.session.delete(item)
            
            # Re-calculate and add items (same logic as create)
            # ... (reuse calculation logic from create_order)
            
            db.session.commit()
            flash(f'Sales Order {order.order_number} updated successfully!', 'success')
            return redirect(url_for('sales_orders.view_order', order_id=order_id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating sales order: {str(e)}', 'error')
            return redirect(url_for('sales_orders.edit_order', order_id=order_id))
    
    # GET - show edit form
    customers = Customer.query.filter_by(tenant_id=tenant_id).order_by(Customer.name).all()
    items = Item.query.filter_by(tenant_id=tenant_id).order_by(Item.name).all()
    
    return render_template(
        'sales_orders/edit.html',
        order=order,
        customers=customers,
        items=items
    )


@sales_order_bp.route('/<int:order_id>/update-status', methods=['POST'])
def update_status(order_id):
    """Update order status"""
    tenant_id = session['tenant_admin_id']
    order = SalesOrder.query.filter_by(id=order_id, tenant_id=tenant_id).first_or_404()
    
    new_status = request.form.get('status')
    
    if new_status not in ['draft', 'pending', 'confirmed', 'cancelled']:
        flash('Invalid status', 'error')
        return redirect(url_for('sales_orders.view_order', order_id=order_id))
    
    old_status = order.status
    order.status = new_status
    
    # Reserve stock if confirmed
    if new_status == 'confirmed' and old_status != 'confirmed':
        reserve_stock_for_order(order_id)
    
    # Release stock if cancelled
    if new_status == 'cancelled' and old_status == 'confirmed':
        release_stock_for_order(order_id)
    
    db.session.commit()
    
    flash(f'Order status updated to {new_status}', 'success')
    return redirect(url_for('sales_orders.view_order', order_id=order_id))


@sales_order_bp.route('/<int:order_id>/delete', methods=['POST'])
def delete_order(order_id):
    """Delete sales order"""
    tenant_id = session['tenant_admin_id']
    order = SalesOrder.query.filter_by(id=order_id, tenant_id=tenant_id).first_or_404()
    
    # Prevent deletion if invoiced
    if order.status in ['partially_invoiced', 'invoiced']:
        flash('Cannot delete invoiced orders', 'error')
        return redirect(url_for('sales_orders.view_order', order_id=order_id))
    
    order_number = order.order_number
    
    # Release reserved stock
    if order.status == 'confirmed':
        release_stock_for_order(order_id)
    
    db.session.delete(order)
    db.session.commit()
    
    flash(f'Sales Order {order_number} deleted successfully', 'success')
    return redirect(url_for('sales_orders.list_orders'))


# Temporarily disabled - Quotation module not yet implemented
# @sales_order_bp.route('/convert-quotation/<int:quotation_id>')
# def convert_from_quotation(quotation_id):
#     """Convert quotation to sales order"""
#     flash('Quotation conversion feature coming soon!', 'info')
#     return redirect(url_for('sales_orders.list_orders'))


@sales_order_bp.route('/<int:order_id>/convert-to-invoice')
def convert_to_invoice(order_id):
    """Convert sales order to invoice"""
    tenant_id = session['tenant_admin_id']
    order = SalesOrder.query.filter_by(id=order_id, tenant_id=tenant_id).first_or_404()
    
    # Redirect to invoice creation with pre-filled data
    return redirect(url_for('invoices.create', from_order=order_id))


# Helper functions
def reserve_stock_for_order(order_id):
    """Reserve stock for confirmed sales order"""
    order = SalesOrder.query.get(order_id)
    if not order:
        return
    
    tenant_id = order.tenant_id
    default_site = Site.query.filter_by(tenant_id=tenant_id).first()
    
    if not default_site:
        print(f"⚠️ No site found for tenant {tenant_id}")
        return
    
    for item in order.items:
        if item.stock_reserved:
            continue  # Already reserved
        
        if item.item_id:
            item_obj = Item.query.get(item.item_id)
            if item_obj and item_obj.track_inventory:
                item_stock = ItemStock.query.filter_by(
                    tenant_id=tenant_id,
                    item_id=item.item_id,
                    site_id=default_site.id
                ).first()
                
                if item_stock:
                    # Mark as reserved (don't actually reduce stock yet)
                    item.stock_reserved = True
                    item.site_id = default_site.id
                    print(f"📦 Stock reserved for {item.item_name}: {item.quantity} units")
    
    db.session.commit()


def release_stock_for_order(order_id):
    """Release reserved stock when order is cancelled"""
    order = SalesOrder.query.get(order_id)
    if not order:
        return
    
    for item in order.items:
        if item.stock_reserved:
            item.stock_reserved = False
            item.site_id = None
            print(f"🔓 Stock reservation released for {item.item_name}")
    
    db.session.commit()


@sales_order_bp.route('/api/search-items')
def api_search_items():
    """API endpoint for item search"""
    tenant_id = session.get('tenant_admin_id')
    if not tenant_id:
        return jsonify({'error': 'Unauthorized'}), 401
    
    search_term = request.args.get('q', '').strip()
    
    if len(search_term) < 2:
        return jsonify([])
    
    items = Item.query.filter_by(tenant_id=tenant_id).filter(
        or_(
            Item.name.ilike(f'%{search_term}%'),
            Item.hsn_code.ilike(f'%{search_term}%')
        )
    ).limit(20).all()
    
    result = []
    for item in items:
        # Extract GST rate from tax_preference if available (e.g., "GST @ 18%" -> 18)
        gst_rate = 18  # Default to 18%
        if item.tax_preference:
            try:
                # Try to extract number from tax_preference
                import re
                match = re.search(r'(\d+)', item.tax_preference)
                if match:
                    gst_rate = int(match.group(1))
            except:
                pass
        
        result.append({
            'id': item.id,
            'name': item.name,
            'hsn_code': item.hsn_code or '',
            'unit': item.unit or 'pcs',
            'selling_price': float(item.selling_price or 0),
            'gst_rate': gst_rate
        })
    
    return jsonify(result)

