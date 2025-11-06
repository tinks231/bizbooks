"""
Invoice management routes
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, g, session
from models import db, Invoice, InvoiceItem, Item, ItemStock, ItemStockMovement, Site, Tenant
from utils.tenant_middleware import require_tenant, get_current_tenant_id
from utils.license_check import check_license
from sqlalchemy import func, desc
from datetime import datetime, date
import pytz
import json

# PDF generation (commented out for now - will add later)
# from io import BytesIO
# from reportlab.lib.pagesizes import A4
# from reportlab.lib.units import inch
# from reportlab.pdfgen import canvas
# from reportlab.lib import colors
# from reportlab.platypus import Table, TableStyle

invoices_bp = Blueprint('invoices', __name__, url_prefix='/admin/invoices')

def login_required(f):
    """Decorator to require admin login (also checks license)"""
    from functools import wraps
    @wraps(f)
    @check_license  # Check license/trial before allowing access
    def decorated_function(*args, **kwargs):
        if 'tenant_admin_id' not in session:
            flash('Please login first', 'error')
            return redirect(url_for('admin.login'))
        # Verify session tenant matches current tenant
        if session.get('tenant_admin_id') != get_current_tenant_id():
            session.clear()
            flash('Session mismatch. Please login again.', 'error')
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function

@invoices_bp.route('/')
@require_tenant
@login_required
def index():
    """List all invoices"""
    tenant_id = g.tenant.id
    
    # Filters
    status_filter = request.args.get('status', 'all')
    payment_filter = request.args.get('payment', 'all')
    search = request.args.get('search', '').strip()
    
    # Base query
    query = Invoice.query.filter_by(tenant_id=tenant_id)
    
    # Apply filters
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    if payment_filter != 'all':
        query = query.filter_by(payment_status=payment_filter)
    if search:
        query = query.filter(
            db.or_(
                Invoice.invoice_number.ilike(f'%{search}%'),
                Invoice.customer_name.ilike(f'%{search}%'),
                Invoice.customer_phone.ilike(f'%{search}%')
            )
        )
    
    # Get invoices
    invoices = query.order_by(desc(Invoice.invoice_date), desc(Invoice.id)).all()
    
    # Stats
    total_invoices = Invoice.query.filter_by(tenant_id=tenant_id, status='sent').count()
    total_revenue = db.session.query(func.sum(Invoice.total_amount)).filter_by(
        tenant_id=tenant_id, status='sent'
    ).scalar() or 0
    
    paid_revenue = db.session.query(func.sum(Invoice.paid_amount)).filter_by(
        tenant_id=tenant_id
    ).scalar() or 0
    
    pending_revenue = total_revenue - paid_revenue
    
    return render_template('admin/invoices/list.html',
                         tenant=g.tenant,
                         invoices=invoices,
                         total_invoices=total_invoices,
                         total_revenue=total_revenue,
                         paid_revenue=paid_revenue,
                         pending_revenue=pending_revenue,
                         status_filter=status_filter,
                         payment_filter=payment_filter,
                         search=search)


@invoices_bp.route('/create', methods=['GET', 'POST'])
@require_tenant
@login_required
def create():
    """Create new invoice"""
    tenant_id = g.tenant.id
    
    if request.method == 'POST':
        try:
            # Get form data
            customer_name = request.form.get('customer_name')
            customer_phone = request.form.get('customer_phone')
            customer_email = request.form.get('customer_email')
            customer_address = request.form.get('customer_address')
            customer_gstin = request.form.get('customer_gstin')
            customer_state = request.form.get('customer_state')
            invoice_date = request.form.get('invoice_date')
            due_date = request.form.get('due_date')
            notes = request.form.get('notes')
            
            # Payment status
            payment_received = request.form.get('payment_received', 'no')
            payment_method = request.form.get('payment_method')
            payment_reference = request.form.get('payment_reference')
            
            # Convert dates
            if invoice_date:
                invoice_date = datetime.strptime(invoice_date, '%Y-%m-%d').date()
            else:
                invoice_date = date.today()
            
            # Convert due_date, handling empty string
            if due_date and due_date.strip():
                due_date = datetime.strptime(due_date, '%Y-%m-%d').date()
            else:
                due_date = None
            
            # Determine status based on payment
            if payment_received == 'yes':
                status = 'sent'  # Auto-mark as sent if payment received
                payment_status = 'paid'
            else:
                status = 'draft'  # Keep as draft for credit sales
                payment_status = 'unpaid'
            
            # Create invoice
            # Get customer_id if provided (from customer selection)
            customer_id = request.form.get('customer_id')
            if customer_id and customer_id.strip():
                customer_id = int(customer_id)
            else:
                customer_id = None
            
            # Get sales_order_id if converting from order
            sales_order_id = request.form.get('sales_order_id')
            if sales_order_id and sales_order_id.strip():
                sales_order_id = int(sales_order_id)
            else:
                sales_order_id = None
            
            invoice = Invoice(
                tenant_id=tenant_id,
                customer_id=customer_id,  # NEW: Link to customer master
                # sales_order_id=sales_order_id,  # DISABLED: Need to run migration first
                customer_name=customer_name,
                customer_phone=customer_phone,
                customer_email=customer_email,
                customer_address=customer_address,
                customer_gstin=customer_gstin,
                customer_state=customer_state or 'Maharashtra',  # Default
                invoice_date=invoice_date,
                due_date=due_date,
                notes=notes,
                status=status,
                payment_status=payment_status,
                payment_method=payment_method if payment_received == 'yes' else None
            )
            
            # Generate invoice number
            invoice.invoice_number = invoice.generate_invoice_number()
            
            # Get tenant's state from settings
            tenant_settings = json.loads(g.tenant.settings) if g.tenant.settings else {}
            tenant_state = tenant_settings.get('state', 'Maharashtra')
            is_same_state = (customer_state or 'Maharashtra') == tenant_state
            
            # Process invoice items
            item_names = request.form.getlist('item_name[]')
            item_ids = request.form.getlist('item_id[]')
            descriptions = request.form.getlist('description[]')
            quantities = request.form.getlist('quantity[]')
            units = request.form.getlist('unit[]')
            rates = request.form.getlist('rate[]')
            gst_rates = request.form.getlist('gst_rate[]')
            hsn_codes = request.form.getlist('hsn_code[]')
            price_inclusives = request.form.getlist('price_inclusive[]')
            
            subtotal = 0
            total_cgst = 0
            total_sgst = 0
            total_igst = 0
            
            for i in range(len(item_names)):
                if not item_names[i] or not quantities[i] or not rates[i]:
                    continue
                
                item_id = int(item_ids[i]) if item_ids[i] and item_ids[i] != '' else None
                quantity = float(quantities[i])
                rate = float(rates[i])
                gst_rate = float(gst_rates[i]) if gst_rates[i] else 18
                
                # Check if price is inclusive of GST (MRP mode)
                # Checkboxes appear in list only if checked
                price_inclusive = i < len(price_inclusives) and price_inclusives[i] == 'on'
                
                # Calculate based on price mode
                if price_inclusive:
                    # Rate is INCLUSIVE of GST (like MRP)
                    total_amount = quantity * rate
                    divisor = 1 + (gst_rate / 100)
                    taxable_value = total_amount / divisor
                    gst_amount = total_amount - taxable_value
                else:
                    # Rate is EXCLUSIVE of GST (traditional)
                    taxable_value = quantity * rate
                    gst_amount = taxable_value * (gst_rate / 100)
                    total_amount = taxable_value + gst_amount
                
                # Create invoice item with calculated values
                invoice_item = InvoiceItem(
                    item_id=item_id,
                    item_name=item_names[i],
                    description=descriptions[i] if i < len(descriptions) else '',
                    hsn_code=hsn_codes[i] if i < len(hsn_codes) else '',
                    quantity=quantity,
                    unit=units[i] if i < len(units) else 'Nos',
                    rate=taxable_value / quantity,  # Store base rate (before GST)
                    gst_rate=gst_rate
                )
                
                # Manually set calculated amounts
                invoice_item.taxable_value = taxable_value
                invoice_item.total_amount = total_amount  # CRITICAL: Set total amount
                
                if is_same_state:
                    invoice_item.cgst_amount = gst_amount / 2
                    invoice_item.sgst_amount = gst_amount / 2
                    invoice_item.igst_amount = 0
                else:
                    invoice_item.cgst_amount = 0
                    invoice_item.sgst_amount = 0
                    invoice_item.igst_amount = gst_amount
                
                # Add to invoice
                invoice.items.append(invoice_item)
                
                # 🔥 REDUCE STOCK FOR THIS ITEM 🔥
                if item_id:  # Only reduce stock if item is from inventory (not manual entry)
                    item_obj = Item.query.get(item_id)
                    if item_obj and item_obj.track_inventory:
                        # Get default site (or first site)
                        default_site = Site.query.filter_by(tenant_id=tenant_id).first()
                        if default_site:
                            # Get or create stock record
                            item_stock = ItemStock.query.filter_by(
                                tenant_id=tenant_id,
                                item_id=item_id,
                                site_id=default_site.id
                            ).first()
                            
                            if item_stock:
                                # Check if sufficient stock available
                                if item_stock.quantity_available < quantity:
                                    # Allow negative stock but log warning
                                    print(f"⚠️  WARNING: Insufficient stock for {item_obj.name}! Available: {item_stock.quantity_available}, Requested: {quantity}")
                                
                                # Reduce stock (allow negative for flexibility)
                                old_qty = item_stock.quantity_available
                                item_stock.quantity_available -= quantity
                                new_qty = item_stock.quantity_available
                                
                                # Update stock value
                                if item_obj.cost_price:
                                    item_stock.stock_value = new_qty * item_obj.cost_price
                                
                                # Create stock movement record for audit trail
                                stock_movement = ItemStockMovement(
                                    tenant_id=tenant_id,
                                    item_id=item_id,
                                    site_id=default_site.id,
                                    movement_type='stock_out',
                                    quantity=quantity,  # Quantity sold (positive number)
                                    unit_cost=item_obj.cost_price or 0,
                                    total_value=quantity * (item_obj.cost_price or 0),
                                    reference_type='invoice',
                                    reference_number=None,  # Will be updated after invoice is saved
                                    reference_id=None,  # Will be updated after invoice is saved
                                    reason='Sale',
                                    notes=f'Sold via Invoice (Customer: {customer_name})',
                                    created_by=g.tenant.company_name
                                )
                                db.session.add(stock_movement)
                                
                                print(f"📦 Stock reduced: {item_obj.name} - {old_qty} → {new_qty} (Sold: {quantity})")
                
                # Update totals
                subtotal += invoice_item.taxable_value
                total_cgst += invoice_item.cgst_amount
                total_sgst += invoice_item.sgst_amount
                total_igst += invoice_item.igst_amount
            
            # Get discount
            discount = float(request.form.get('discount', 0) or 0)
            
            # Apply discount to subtotal and recalculate GST proportionally
            if discount > 0:
                discount_ratio = (subtotal - discount) / subtotal if subtotal > 0 else 1
                total_cgst = total_cgst * discount_ratio
                total_sgst = total_sgst * discount_ratio
                total_igst = total_igst * discount_ratio
                subtotal = subtotal - discount
            
            # Calculate invoice totals
            invoice.subtotal = subtotal
            invoice.discount_amount = discount
            invoice.cgst_amount = total_cgst
            invoice.sgst_amount = total_sgst
            invoice.igst_amount = total_igst
            
            # Round off to nearest rupee
            total_before_rounding = subtotal + total_cgst + total_sgst + total_igst
            invoice.total_amount = round(total_before_rounding)
            invoice.round_off = invoice.total_amount - total_before_rounding
            
            # Set paid amount if payment received
            if payment_received == 'yes':
                invoice.paid_amount = invoice.total_amount
            
            # Add payment reference to notes if provided
            if payment_reference and payment_received == 'yes':
                invoice.internal_notes = f"Payment Reference: {payment_reference}"
            
            # Save
            db.session.add(invoice)
            db.session.commit()
            
            # Update stock movement records with invoice reference
            ItemStockMovement.query.filter_by(
                reference_type='invoice',
                reference_number=None
            ).filter(
                ItemStockMovement.created_at >= datetime.now(pytz.timezone('Asia/Kolkata')).replace(second=0, microsecond=0)
            ).update({
                'reference_number': invoice.invoice_number,
                'reference_id': invoice.id
            })
            
            # Update sales order status if linked
            if sales_order_id:
                from models import SalesOrder
                sales_order = SalesOrder.query.get(sales_order_id)
                if sales_order:
                    # Update fulfillment tracking
                    sales_order.update_fulfillment_status()
                    flash(f'✅ Invoice created successfully! Linked to Sales Order {sales_order.order_number}', 'success')
                else:
                    flash('Invoice created successfully! Stock updated.', 'success')
            else:
                flash('Invoice created successfully! Stock updated.', 'success')
            
            db.session.commit()
            
            return redirect(url_for('invoices.view', invoice_id=invoice.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating invoice: {str(e)}', 'error')
    
    # GET request - show form
    # Get all items for autocomplete
    items = Item.query.filter_by(tenant_id=tenant_id, is_active=True).all()
    
    # Prepare items for JSON (only needed fields)
    items_json = [
        {
            'id': item.id,
            'name': item.name,
            'selling_price': item.selling_price or 0,
            'hsn_code': item.hsn_code or ''
        }
        for item in items
    ]
    
    # Check if converting from sales order
    from_order = request.args.get('from_order')
    sales_order = None
    if from_order:
        from models import SalesOrder
        sales_order = SalesOrder.query.filter_by(
            id=int(from_order), 
            tenant_id=tenant_id
        ).first()
    
    # Get tenant settings
    tenant_settings = json.loads(g.tenant.settings) if g.tenant.settings else {}
    
    return render_template('admin/invoices/create.html',
                         tenant=g.tenant,
                         items=items_json,
                         today=date.today().strftime('%Y-%m-%d'),
                         tenant_settings=tenant_settings,
                         sales_order=sales_order)


@invoices_bp.route('/<int:invoice_id>')
@require_tenant
@login_required
def view(invoice_id):
    """View invoice details"""
    tenant_id = g.tenant.id
    invoice = Invoice.query.filter_by(id=invoice_id, tenant_id=tenant_id).first_or_404()
    
    # Get tenant settings for invoice header
    tenant_settings = json.loads(g.tenant.settings) if g.tenant.settings else {}
    
    return render_template('admin/invoices/view.html',
                         tenant=g.tenant,
                         invoice=invoice,
                         tenant_settings=tenant_settings)


@invoices_bp.route('/<int:invoice_id>/edit', methods=['GET', 'POST'])
@require_tenant
@login_required
def edit(invoice_id):
    """Edit invoice"""
    tenant_id = g.tenant.id
    invoice = Invoice.query.filter_by(id=invoice_id, tenant_id=tenant_id).first_or_404()
    
    # Can only edit draft invoices
    if invoice.status != 'draft':
        flash('Only draft invoices can be edited', 'error')
        return redirect(url_for('invoices.view', invoice_id=invoice_id))
    
    if request.method == 'POST':
        try:
            # Update customer link
            customer_id = request.form.get('customer_id')
            if customer_id and customer_id.strip():
                invoice.customer_id = int(customer_id)
            else:
                invoice.customer_id = None
            
            # Update customer details
            invoice.customer_name = request.form.get('customer_name')
            invoice.customer_phone = request.form.get('customer_phone')
            invoice.customer_email = request.form.get('customer_email')
            invoice.customer_address = request.form.get('customer_address')
            invoice.customer_gstin = request.form.get('customer_gstin')
            invoice.customer_state = request.form.get('customer_state')
            invoice.notes = request.form.get('notes')
            
            # Update dates
            invoice_date = request.form.get('invoice_date')
            if invoice_date:
                invoice.invoice_date = datetime.strptime(invoice_date, '%Y-%m-%d').date()
            
            due_date = request.form.get('due_date')
            if due_date and due_date.strip():
                invoice.due_date = datetime.strptime(due_date, '%Y-%m-%d').date()
            else:
                invoice.due_date = None
            
            # Store payment info for later (after total is calculated)
            payment_received = request.form.get('payment_received', 'no')
            payment_method = request.form.get('payment_method')
            payment_reference = request.form.get('payment_reference')
            
            # Delete existing items
            InvoiceItem.query.filter_by(invoice_id=invoice.id).delete()
            
            # Add updated items (same logic as create)
            tenant_settings = json.loads(g.tenant.settings) if g.tenant.settings else {}
            tenant_state = tenant_settings.get('state', 'Maharashtra')
            is_same_state = (invoice.customer_state or 'Maharashtra') == tenant_state
            
            # Process invoice items (same as create)
            item_names = request.form.getlist('item_name[]')
            item_ids = request.form.getlist('item_id[]')
            descriptions = request.form.getlist('description[]')
            quantities = request.form.getlist('quantity[]')
            units = request.form.getlist('unit[]')
            rates = request.form.getlist('rate[]')
            gst_rates = request.form.getlist('gst_rate[]')
            hsn_codes = request.form.getlist('hsn_code[]')
            price_inclusives = request.form.getlist('price_inclusive[]')
            
            subtotal = 0
            total_cgst = 0
            total_sgst = 0
            total_igst = 0
            
            for i in range(len(item_names)):
                if not item_names[i] or not quantities[i] or not rates[i]:
                    continue
                
                item_id = int(item_ids[i]) if item_ids[i] and item_ids[i] != '' else None
                quantity = float(quantities[i])
                rate = float(rates[i])
                gst_rate = float(gst_rates[i]) if gst_rates[i] else 18
                
                # Check if price is inclusive of GST (MRP mode)
                # Checkboxes appear in list only if checked
                price_inclusive = i < len(price_inclusives) and price_inclusives[i] == 'on'
                
                # Calculate based on price mode
                if price_inclusive:
                    total_amount = quantity * rate
                    divisor = 1 + (gst_rate / 100)
                    taxable_value = total_amount / divisor
                    gst_amount = total_amount - taxable_value
                else:
                    taxable_value = quantity * rate
                    gst_amount = taxable_value * (gst_rate / 100)
                    total_amount = taxable_value + gst_amount
                
                invoice_item = InvoiceItem(
                    invoice_id=invoice.id,
                    item_id=item_id,
                    item_name=item_names[i],
                    description=descriptions[i] if i < len(descriptions) else '',
                    hsn_code=hsn_codes[i] if i < len(hsn_codes) else '',
                    quantity=quantity,
                    unit=units[i] if i < len(units) else 'Nos',
                    rate=taxable_value / quantity,
                    gst_rate=gst_rate
                )
                
                invoice_item.taxable_value = taxable_value
                invoice_item.total_amount = total_amount
                
                if is_same_state:
                    invoice_item.cgst_amount = gst_amount / 2
                    invoice_item.sgst_amount = gst_amount / 2
                    invoice_item.igst_amount = 0
                else:
                    invoice_item.cgst_amount = 0
                    invoice_item.sgst_amount = 0
                    invoice_item.igst_amount = gst_amount
                
                db.session.add(invoice_item)
                
                subtotal += invoice_item.taxable_value
                total_cgst += invoice_item.cgst_amount
                total_sgst += invoice_item.sgst_amount
                total_igst += invoice_item.igst_amount
            
            # Get discount
            discount = float(request.form.get('discount', 0) or 0)
            
            # Apply discount to subtotal and recalculate GST proportionally
            if discount > 0:
                discount_ratio = (subtotal - discount) / subtotal if subtotal > 0 else 1
                total_cgst = total_cgst * discount_ratio
                total_sgst = total_sgst * discount_ratio
                total_igst = total_igst * discount_ratio
                subtotal = subtotal - discount
            
            # Update invoice totals
            invoice.subtotal = subtotal
            invoice.discount_amount = discount
            invoice.cgst_amount = total_cgst
            invoice.sgst_amount = total_sgst
            invoice.igst_amount = total_igst
            
            total_before_rounding = subtotal + total_cgst + total_sgst + total_igst
            invoice.total_amount = round(total_before_rounding)
            invoice.round_off = invoice.total_amount - total_before_rounding
            
            # Update payment status (after total is calculated)
            if payment_received == 'yes':
                invoice.status = 'sent'
                invoice.payment_status = 'paid'
                invoice.payment_method = payment_method
                invoice.paid_amount = invoice.total_amount
                if payment_reference:
                    invoice.internal_notes = f"Payment Reference: {payment_reference}"
            else:
                invoice.status = 'draft'
                invoice.payment_status = 'unpaid'
                invoice.payment_method = None
                invoice.paid_amount = 0
                invoice.internal_notes = None
            
            db.session.commit()
            flash('Invoice updated successfully!', 'success')
            return redirect(url_for('invoices.view', invoice_id=invoice.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating invoice: {str(e)}', 'error')
    
    # GET - show edit form (using create template)
    try:
        items = Item.query.filter_by(tenant_id=tenant_id, is_active=True).all()
        items_json = [
            {
                'id': item.id,
                'name': item.name,
                'selling_price': item.selling_price or 0,
                'hsn_code': item.hsn_code or ''
            }
            for item in items
        ]
        tenant_settings = json.loads(g.tenant.settings) if g.tenant.settings else {}
        
        flash('Edit mode: Modify invoice details below', 'info')
        return render_template('admin/invoices/create.html',
                             tenant=g.tenant,
                             invoice=invoice,
                             items=items_json,
                             today=date.today().strftime('%Y-%m-%d'),
                             tenant_settings=tenant_settings,
                             edit_mode=True,
                             sales_order=None)  # Explicitly set sales_order to None for edit mode
    except Exception as e:
        print(f"❌ Error loading edit form: {e}")
        import traceback
        traceback.print_exc()
        flash(f'Error loading invoice for editing: {str(e)}', 'error')
        return redirect(url_for('invoices.view', invoice_id=invoice_id))


@invoices_bp.route('/<int:invoice_id>/mark-sent', methods=['POST'])
@require_tenant
@login_required
def mark_sent(invoice_id):
    """Mark invoice as sent (finalizes it)"""
    tenant_id = g.tenant.id
    invoice = Invoice.query.filter_by(id=invoice_id, tenant_id=tenant_id).first_or_404()
    
    if invoice.status == 'draft':
        invoice.status = 'sent'
        
        # Reduce stock for items
        for item in invoice.items:
            if item.item_id:
                stock = ItemStock.query.filter_by(
                    tenant_id=tenant_id,
                    item_id=item.item_id
                ).first()
                
                if stock:
                    stock.quantity_available -= item.quantity
        
        db.session.commit()
        flash('Invoice marked as sent and stock updated!', 'success')
    else:
        flash('Invoice is already sent', 'info')
    
    return redirect(url_for('invoices.view', invoice_id=invoice_id))


@invoices_bp.route('/<int:invoice_id>/record-payment', methods=['POST'])
@require_tenant
@login_required
def record_payment(invoice_id):
    """Record payment for invoice"""
    tenant_id = g.tenant.id
    invoice = Invoice.query.filter_by(id=invoice_id, tenant_id=tenant_id).first_or_404()
    
    try:
        amount = float(request.form.get('amount', 0))
        payment_method = request.form.get('payment_method', 'Cash')
        
        # Update paid amount
        invoice.paid_amount += amount
        invoice.payment_method = payment_method
        
        # Update payment status
        if invoice.paid_amount >= invoice.total_amount:
            invoice.payment_status = 'paid'
        elif invoice.paid_amount > 0:
            invoice.payment_status = 'partial'
        else:
            invoice.payment_status = 'unpaid'
        
        db.session.commit()
        flash(f'Payment of ₹{amount} recorded successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error recording payment: {str(e)}', 'error')
    
    return redirect(url_for('invoices.view', invoice_id=invoice_id))


@invoices_bp.route('/<int:invoice_id>/delete', methods=['POST'])
@require_tenant
@login_required
def delete(invoice_id):
    """Delete invoice (only drafts)"""
    tenant_id = g.tenant.id
    invoice = Invoice.query.filter_by(id=invoice_id, tenant_id=tenant_id).first_or_404()
    
    if invoice.status != 'draft':
        flash('Only draft invoices can be deleted', 'error')
        return redirect(url_for('invoices.view', invoice_id=invoice_id))
    
    try:
        db.session.delete(invoice)
        db.session.commit()
        flash('Invoice deleted successfully!', 'success')
        return redirect(url_for('invoices.index'))
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting invoice: {str(e)}', 'error')
        return redirect(url_for('invoices.view', invoice_id=invoice_id))


@invoices_bp.route('/settings', methods=['GET', 'POST'])
@require_tenant
@login_required
def settings():
    """Configure invoice settings (GST, address, etc.)"""
    tenant = g.tenant
    
    if request.method == 'POST':
        try:
            # Get current settings
            tenant_settings = json.loads(tenant.settings) if tenant.settings else {}
            
            # Handle logo upload
            if 'logo' in request.files:
                logo_file = request.files['logo']
                if logo_file and logo_file.filename:
                    from utils.helpers import save_uploaded_file
                    logo_url = save_uploaded_file(logo_file, 'uploads/logos')
                    if logo_url:
                        tenant_settings['logo_url'] = logo_url
                        flash('✅ Logo uploaded successfully!', 'success')
                    else:
                        flash('⚠️ Logo upload failed. Please try again.', 'warning')
            
            # Update invoice settings
            tenant_settings['gstin'] = request.form.get('gstin', '')
            tenant_settings['pan'] = request.form.get('pan', '')
            tenant_settings['address'] = request.form.get('address', '')
            tenant_settings['city'] = request.form.get('city', '')
            tenant_settings['state'] = request.form.get('state', 'Maharashtra')
            tenant_settings['pincode'] = request.form.get('pincode', '')
            tenant_settings['website'] = request.form.get('website', '')
            tenant_settings['phone'] = request.form.get('phone', tenant.admin_phone)
            tenant_settings['email'] = request.form.get('email', tenant.admin_email)
            tenant_settings['invoice_terms'] = request.form.get('invoice_terms', '')
            tenant_settings['invoice_footer'] = request.form.get('invoice_footer', 'Thank you for your business!')
            
            # Save
            tenant.settings = json.dumps(tenant_settings)
            db.session.commit()
            
            flash('Invoice settings updated successfully!', 'success')
            return redirect(url_for('invoices.settings'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating settings: {str(e)}', 'error')
    
    # GET - show form
    tenant_settings = json.loads(tenant.settings) if tenant.settings else {}
    
    return render_template('admin/invoices/settings.html',
                         tenant=tenant,
                         settings=tenant_settings)

