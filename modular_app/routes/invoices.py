"""
Invoice management routes
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, g, session
from models import db, Invoice, InvoiceItem, Item, ItemStock, Tenant
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
            
            # Convert dates
            if invoice_date:
                invoice_date = datetime.strptime(invoice_date, '%Y-%m-%d').date()
            else:
                invoice_date = date.today()
            
            if due_date:
                due_date = datetime.strptime(due_date, '%Y-%m-%d').date()
            
            # Create invoice
            invoice = Invoice(
                tenant_id=tenant_id,
                customer_name=customer_name,
                customer_phone=customer_phone,
                customer_email=customer_email,
                customer_address=customer_address,
                customer_gstin=customer_gstin,
                customer_state=customer_state or 'Maharashtra',  # Default
                invoice_date=invoice_date,
                due_date=due_date,
                notes=notes,
                status='draft'
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
                
                # Create invoice item
                invoice_item = InvoiceItem(
                    item_id=item_id,
                    item_name=item_names[i],
                    description=descriptions[i] if i < len(descriptions) else '',
                    hsn_code=hsn_codes[i] if i < len(hsn_codes) else '',
                    quantity=quantity,
                    unit=units[i] if i < len(units) else 'Nos',
                    rate=rate,
                    gst_rate=gst_rate
                )
                
                # Calculate amounts
                invoice_item.calculate_amounts(is_same_state=is_same_state)
                
                # Add to invoice
                invoice.items.append(invoice_item)
                
                # Update totals
                subtotal += invoice_item.taxable_value
                total_cgst += invoice_item.cgst_amount
                total_sgst += invoice_item.sgst_amount
                total_igst += invoice_item.igst_amount
            
            # Calculate invoice totals
            invoice.subtotal = subtotal
            invoice.cgst_amount = total_cgst
            invoice.sgst_amount = total_sgst
            invoice.igst_amount = total_igst
            
            # Round off to nearest rupee
            total_before_rounding = subtotal + total_cgst + total_sgst + total_igst
            invoice.total_amount = round(total_before_rounding)
            invoice.round_off = invoice.total_amount - total_before_rounding
            
            # Save
            db.session.add(invoice)
            db.session.commit()
            
            flash('Invoice created successfully!', 'success')
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
    
    # Get tenant settings
    tenant_settings = json.loads(g.tenant.settings) if g.tenant.settings else {}
    
    return render_template('admin/invoices/create.html',
                         tenant=g.tenant,
                         items=items_json,
                         today=date.today().strftime('%Y-%m-%d'),
                         tenant_settings=tenant_settings)


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
            if due_date:
                invoice.due_date = datetime.strptime(due_date, '%Y-%m-%d').date()
            
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
                
                invoice_item = InvoiceItem(
                    invoice_id=invoice.id,
                    item_id=item_id,
                    item_name=item_names[i],
                    description=descriptions[i] if i < len(descriptions) else '',
                    hsn_code=hsn_codes[i] if i < len(hsn_codes) else '',
                    quantity=quantity,
                    unit=units[i] if i < len(units) else 'Nos',
                    rate=rate,
                    gst_rate=gst_rate
                )
                
                invoice_item.calculate_amounts(is_same_state=is_same_state)
                db.session.add(invoice_item)
                
                subtotal += invoice_item.taxable_value
                total_cgst += invoice_item.cgst_amount
                total_sgst += invoice_item.sgst_amount
                total_igst += invoice_item.igst_amount
            
            # Update invoice totals
            invoice.subtotal = subtotal
            invoice.cgst_amount = total_cgst
            invoice.sgst_amount = total_sgst
            invoice.igst_amount = total_igst
            
            total_before_rounding = subtotal + total_cgst + total_sgst + total_igst
            invoice.total_amount = round(total_before_rounding)
            invoice.round_off = invoice.total_amount - total_before_rounding
            
            db.session.commit()
            flash('Invoice updated successfully!', 'success')
            return redirect(url_for('invoices.view', invoice_id=invoice.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating invoice: {str(e)}', 'error')
    
    # GET - show edit form
    items = Item.query.filter_by(tenant_id=tenant_id, is_active=True).all()
    tenant_settings = json.loads(g.tenant.settings) if g.tenant.settings else {}
    
    return render_template('admin/invoices/edit.html',
                         tenant=g.tenant,
                         invoice=invoice,
                         items=items,
                         tenant_settings=tenant_settings)


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
            
            # Update invoice settings
            tenant_settings['gstin'] = request.form.get('gstin', '')
            tenant_settings['pan'] = request.form.get('pan', '')
            tenant_settings['address'] = request.form.get('address', '')
            tenant_settings['city'] = request.form.get('city', '')
            tenant_settings['state'] = request.form.get('state', 'Maharashtra')
            tenant_settings['pincode'] = request.form.get('pincode', '')
            tenant_settings['website'] = request.form.get('website', '')
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

