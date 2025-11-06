"""
Delivery Challan Management Routes
Handles creation, viewing, and management of delivery challans
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, g, session
from models import db, DeliveryChallan, DeliveryChallanItem, SalesOrder, SalesOrderItem, Customer, Item, ItemStock, Site, Tenant
from decimal import Decimal
from datetime import datetime, date
import pytz

delivery_challan_bp = Blueprint('delivery_challans', __name__, url_prefix='/delivery-challans')

def check_auth():
    """Check if user is logged in"""
    if 'tenant_admin_id' not in session:
        return redirect(url_for('admin.login'))
    return None

@delivery_challan_bp.route('/list')
def list_challans():
    """List all delivery challans"""
    auth_check = check_auth()
    if auth_check:
        return auth_check
    
    tenant_id = g.tenant.id
    
    # Get filter parameters
    status_filter = request.args.get('status', '')
    search = request.args.get('search', '')
    
    # Base query
    query = DeliveryChallan.query.filter_by(tenant_id=tenant_id)
    
    # Apply filters
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    if search:
        query = query.filter(
            (DeliveryChallan.challan_number.ilike(f'%{search}%')) |
            (DeliveryChallan.customer_name.ilike(f'%{search}%'))
        )
    
    # Order by most recent first
    challans = query.order_by(DeliveryChallan.challan_date.desc()).all()
    
    return render_template('delivery_challans/list.html',
                         tenant=g.tenant,
                         challans=challans,
                         status_filter=status_filter,
                         search=search)

@delivery_challan_bp.route('/create', methods=['GET'])
def create_challan_form():
    """Show create delivery challan form"""
    auth_check = check_auth()
    if auth_check:
        return auth_check
    
    # Check if creating from Sales Order
    from_order = request.args.get('from_order')
    sales_order = None
    
    if from_order:
        sales_order = SalesOrder.query.filter_by(
            id=from_order,
            tenant_id=g.tenant.id
        ).first()
        
        if not sales_order:
            flash('Sales Order not found', 'error')
            return redirect(url_for('delivery_challans.list_challans'))
    
    return render_template('delivery_challans/create.html',
                         tenant=g.tenant,
                         sales_order=sales_order,
                         today=date.today().strftime('%Y-%m-%d'))

@delivery_challan_bp.route('/create', methods=['POST'])
def create_challan():
    """Create a new delivery challan"""
    auth_check = check_auth()
    if auth_check:
        return auth_check
    
    try:
        tenant_id = g.tenant.id
        
        # Extract form data
        challan_date = request.form.get('challan_date')
        customer_id = request.form.get('customer_id') or None
        customer_name = request.form.get('customer_name')
        customer_phone = request.form.get('customer_phone', '')
        customer_email = request.form.get('customer_email', '')
        customer_gstin = request.form.get('customer_gstin', '')
        customer_billing_address = request.form.get('customer_billing_address', '')
        customer_shipping_address = request.form.get('customer_shipping_address', '')
        customer_state = request.form.get('customer_state', 'Maharashtra')
        
        # Delivery details
        vehicle_number = request.form.get('vehicle_number', '')
        lr_number = request.form.get('lr_number', '')
        transporter_name = request.form.get('transporter_name', '')
        delivery_note = request.form.get('delivery_note', '')
        notes = request.form.get('notes', '')
        terms = request.form.get('terms', '')
        
        # Sales Order reference
        sales_order_id = request.form.get('sales_order_id') or None
        
        # Purpose (for old schema compatibility)
        purpose = request.form.get('purpose', 'Sale')
        
        # Create delivery challan
        challan = DeliveryChallan(
            tenant_id=tenant_id,
            challan_date=datetime.strptime(challan_date, '%Y-%m-%d').date(),
            customer_id=int(customer_id) if customer_id and customer_id.isdigit() else None,
            customer_name=customer_name,
            customer_phone=customer_phone,
            customer_email=customer_email,
            customer_gstin=customer_gstin,
            customer_billing_address=customer_billing_address,
            customer_shipping_address=customer_shipping_address,
            customer_state=customer_state,
            sales_order_id=int(sales_order_id) if sales_order_id and sales_order_id.isdigit() else None,
            vehicle_number=vehicle_number,
            lr_number=lr_number,
            transporter_name=transporter_name,
            delivery_note=delivery_note,
            purpose=purpose,  # Temporary: for old schema compatibility
            notes=notes,
            terms=terms,
            status='draft'
        )
        
        # Generate DC number
        challan.challan_number = challan.generate_challan_number()
        
        # Add items
        item_ids = request.form.getlist('item_id[]')
        item_names = request.form.getlist('item_name[]')
        hsn_codes = request.form.getlist('hsn_code[]')
        quantities = request.form.getlist('quantity[]')
        units = request.form.getlist('unit[]')
        rates = request.form.getlist('rate[]')
        gst_rates = request.form.getlist('gst_rate[]')
        so_item_ids = request.form.getlist('so_item_id[]') if 'so_item_id[]' in request.form else []
        
        subtotal = Decimal('0')
        total_cgst = Decimal('0')
        total_sgst = Decimal('0')
        total_igst = Decimal('0')
        
        for i in range(len(item_names)):
            if not item_names[i].strip():
                continue
            
            item_id_val = int(item_ids[i]) if (i < len(item_ids) and item_ids[i] and item_ids[i].isdigit()) else None
            hsn_code_val = hsn_codes[i].strip() if (i < len(hsn_codes) and hsn_codes[i]) else ''
            unit_val = units[i] if (i < len(units) and units[i]) else 'Nos'
            so_item_id_val = int(so_item_ids[i]) if (i < len(so_item_ids) and so_item_ids[i] and so_item_ids[i].isdigit()) else None
            
            quantity = Decimal(quantities[i])
            rate = Decimal(rates[i])
            gst_rate = Decimal(gst_rates[i])
            
            # Calculate amounts
            taxable_value = quantity * rate
            
            # Calculate GST (assuming intrastate - CGST + SGST)
            is_interstate = (customer_state.upper() != 'MAHARASHTRA')
            
            if is_interstate:
                igst_amount = taxable_value * gst_rate / Decimal('100')
                cgst_amount = Decimal('0')
                sgst_amount = Decimal('0')
            else:
                cgst_amount = taxable_value * gst_rate / Decimal('200')
                sgst_amount = cgst_amount
                igst_amount = Decimal('0')
            
            total_amount = taxable_value + cgst_amount + sgst_amount + igst_amount
            
            # Create item
            dc_item = DeliveryChallanItem(
                tenant_id=tenant_id,
                sales_order_id=challan.sales_order_id,
                sales_order_item_id=so_item_id_val,
                item_id=item_id_val,
                item_name=item_names[i],
                hsn_code=hsn_code_val,
                quantity=quantity,
                unit=unit_val,
                rate=rate,
                taxable_value=taxable_value,
                gst_rate=gst_rate,
                cgst_amount=cgst_amount,
                sgst_amount=sgst_amount,
                igst_amount=igst_amount,
                total_amount=total_amount
            )
            
            challan.items.append(dc_item)
            
            subtotal += taxable_value
            total_cgst += cgst_amount
            total_sgst += sgst_amount
            total_igst += igst_amount
        
        # Update totals
        challan.subtotal = subtotal
        challan.cgst_amount = total_cgst
        challan.sgst_amount = total_sgst
        challan.igst_amount = total_igst
        challan.total_amount = subtotal + total_cgst + total_sgst + total_igst
        
        db.session.add(challan)
        db.session.commit()
        
        # Update Sales Order fulfillment if linked
        if sales_order_id:
            sales_order = SalesOrder.query.get(sales_order_id)
            if sales_order:
                # Update quantity_delivered on sales order items
                for dc_item in challan.items:
                    if dc_item.sales_order_item_id:
                        so_item = SalesOrderItem.query.get(dc_item.sales_order_item_id)
                        if so_item:
                            so_item.quantity_delivered += Decimal(str(dc_item.quantity))
                            print(f"📦 Updated SO item {so_item.item_name}: delivered {so_item.quantity_delivered}/{so_item.quantity}")
                
                # Update sales order status
                sales_order.update_fulfillment_status()
                db.session.commit()
                
                flash(f'✅ Delivery Challan {challan.challan_number} created! Linked to Sales Order {sales_order.order_number}', 'success')
        else:
            flash(f'✅ Delivery Challan {challan.challan_number} created successfully!', 'success')
        
        return redirect(url_for('delivery_challans.view_challan', challan_id=challan.id))
    
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error creating delivery challan: {str(e)}")
        import traceback
        traceback.print_exc()
        flash(f'Error creating delivery challan: {str(e)}', 'error')
        return redirect(url_for('delivery_challans.create_challan_form'))

@delivery_challan_bp.route('/<int:challan_id>')
def view_challan(challan_id):
    """View delivery challan details"""
    auth_check = check_auth()
    if auth_check:
        return auth_check
    
    challan = DeliveryChallan.query.filter_by(
        id=challan_id,
        tenant_id=g.tenant.id
    ).first()
    
    if not challan:
        flash('Delivery Challan not found', 'error')
        return redirect(url_for('delivery_challans.list_challans'))
    
    # Get linked sales order
    sales_order = None
    if challan.sales_order_id:
        sales_order = SalesOrder.query.get(challan.sales_order_id)
    
    # Get linked invoices
    from models import Invoice
    try:
        invoices = Invoice.query.filter_by(delivery_challan_id=challan_id, tenant_id=g.tenant.id).all()
    except:
        invoices = []
    
    return render_template('delivery_challans/view.html',
                         tenant=g.tenant,
                         challan=challan,
                         sales_order=sales_order,
                         invoices=invoices)

@delivery_challan_bp.route('/<int:challan_id>/update-status', methods=['POST'])
def update_status(challan_id):
    """Update delivery challan status"""
    auth_check = check_auth()
    if auth_check:
        return auth_check
    
    challan = DeliveryChallan.query.filter_by(
        id=challan_id,
        tenant_id=g.tenant.id
    ).first()
    
    if not challan:
        flash('Delivery Challan not found', 'error')
        return redirect(url_for('delivery_challans.list_challans'))
    
    new_status = request.form.get('status')
    now = datetime.now(pytz.timezone('Asia/Kolkata'))
    
    if new_status == 'dispatched':
        challan.status = 'dispatched'
        challan.dispatched_at = now
        flash(f'✅ Delivery Challan {challan.challan_number} marked as Dispatched', 'success')
    
    elif new_status == 'delivered':
        challan.status = 'delivered'
        challan.delivered_at = now
        flash(f'✅ Delivery Challan {challan.challan_number} marked as Delivered', 'success')
    
    elif new_status == 'cancelled':
        challan.status = 'cancelled'
        flash(f'Delivery Challan {challan.challan_number} cancelled', 'warning')
    
    db.session.commit()
    return redirect(url_for('delivery_challans.view_challan', challan_id=challan_id))

@delivery_challan_bp.route('/<int:challan_id>/delete', methods=['POST'])
def delete_challan(challan_id):
    """Delete delivery challan"""
    auth_check = check_auth()
    if auth_check:
        return auth_check
    
    challan = DeliveryChallan.query.filter_by(
        id=challan_id,
        tenant_id=g.tenant.id
    ).first()
    
    if not challan:
        flash('Delivery Challan not found', 'error')
        return redirect(url_for('delivery_challans.list_challans'))
    
    if challan.status not in ['draft', 'cancelled']:
        flash('Can only delete draft or cancelled delivery challans', 'error')
        return redirect(url_for('delivery_challans.view_challan', challan_id=challan_id))
    
    challan_number = challan.challan_number
    db.session.delete(challan)
    db.session.commit()
    
    flash(f'Delivery Challan {challan_number} deleted', 'info')
    return redirect(url_for('delivery_challans.list_challans'))

@delivery_challan_bp.route('/<int:challan_id>/convert-to-invoice')
def convert_to_invoice(challan_id):
    """Convert delivery challan to invoice"""
    auth_check = check_auth()
    if auth_check:
        return auth_check
    
    return redirect(url_for('invoices.create', from_challan=challan_id))

