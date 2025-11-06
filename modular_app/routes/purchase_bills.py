from flask import Blueprint, render_template, request, redirect, url_for, flash, g, jsonify, session
from models import db, PurchaseBill, PurchaseBillItem, Vendor, Item, ItemStock, Site, Tenant
from utils.tenant_middleware import get_current_tenant_id
from utils.license_check import check_license
from datetime import datetime, date
from decimal import Decimal
import pytz

purchase_bills_bp = Blueprint('purchase_bills', __name__, url_prefix='/admin/purchase-bills')

@purchase_bills_bp.before_request
def check_auth():
    """Ensure user is logged in for all purchase bill routes"""
    if 'tenant_admin_id' not in session:
        flash('Please login to access purchase bills', 'error')
        return redirect(url_for('admin.login'))
    
    # Load tenant into g for easy access
    g.tenant = Tenant.query.get(session['tenant_admin_id'])
    if not g.tenant:
        session.clear()
        flash('Session expired. Please login again.', 'error')
        return redirect(url_for('admin.login'))

@purchase_bills_bp.route('/')
@check_license
def list_bills():
    """List all purchase bills"""
    tenant_id = get_current_tenant_id()
    
    # Get filter parameters
    status_filter = request.args.get('status', 'all')
    payment_filter = request.args.get('payment', 'all')
    search_query = request.args.get('search', '').strip()
    
    # Base query
    query = PurchaseBill.query.filter_by(tenant_id=tenant_id)
    
    # Apply filters
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    
    if payment_filter != 'all':
        query = query.filter_by(payment_status=payment_filter)
    
    if search_query:
        query = query.filter(
            db.or_(
                PurchaseBill.bill_number.like(f'%{search_query}%'),
                PurchaseBill.vendor_name.like(f'%{search_query}%'),
                PurchaseBill.reference_number.like(f'%{search_query}%')
            )
        )
    
    # Get bills sorted by date (newest first)
    bills = query.order_by(PurchaseBill.bill_date.desc()).all()
    
    # Calculate summary stats
    total_bills = len(bills)
    total_amount = sum([bill.total_amount for bill in bills])
    total_paid = sum([bill.paid_amount for bill in bills])
    total_due = sum([bill.balance_due for bill in bills])
    
    return render_template('admin/purchase_bills/list.html',
                         tenant=g.tenant,
                         bills=bills,
                         status_filter=status_filter,
                         payment_filter=payment_filter,
                         search_query=search_query,
                         total_bills=total_bills,
                         total_amount=total_amount,
                         total_paid=total_paid,
                         total_due=total_due)

@purchase_bills_bp.route('/create', methods=['GET', 'POST'])
@check_license
def create_bill():
    """Create new purchase bill"""
    tenant_id = get_current_tenant_id()
    
    if request.method == 'POST':
        try:
            # Create bill
            bill = PurchaseBill()
            bill.tenant_id = tenant_id
            bill.bill_number = bill.generate_bill_number()
            
            # Bill details
            bill.bill_date = datetime.strptime(request.form.get('bill_date'), '%Y-%m-%d').date()
            if request.form.get('due_date'):
                bill.due_date = datetime.strptime(request.form.get('due_date'), '%Y-%m-%d').date()
            
            # Vendor details
            vendor_id = request.form.get('vendor_id')
            if vendor_id:
                vendor = Vendor.query.get(vendor_id)
                if vendor:
                    bill.vendor_id = vendor.id
                    bill.vendor_name = vendor.name
                    bill.vendor_phone = vendor.phone
                    bill.vendor_email = vendor.email
                    bill.vendor_gstin = vendor.gstin
                    bill.vendor_address = vendor.address
                    bill.vendor_state = vendor.state or 'Maharashtra'
            else:
                # Manual vendor entry
                bill.vendor_name = request.form.get('vendor_name')
                bill.vendor_phone = request.form.get('vendor_phone', '')
                bill.vendor_email = request.form.get('vendor_email', '')
                bill.vendor_gstin = request.form.get('vendor_gstin', '')
                bill.vendor_address = request.form.get('vendor_address', '')
                bill.vendor_state = request.form.get('vendor_state', 'Maharashtra')
            
            # Additional fields
            bill.reference_number = request.form.get('reference_number', '')
            bill.payment_terms = request.form.get('payment_terms', '')
            bill.notes = request.form.get('notes', '')
            bill.terms_conditions = request.form.get('terms_conditions', '')
            
            # Get line items
            item_ids = request.form.getlist('item_id[]')
            item_names = request.form.getlist('item_name[]')
            descriptions = request.form.getlist('description[]')
            hsn_codes = request.form.getlist('hsn_code[]')
            quantities = request.form.getlist('quantity[]')
            units = request.form.getlist('unit[]')
            rates = request.form.getlist('rate[]')
            gst_rates = request.form.getlist('gst_rate[]')
            
            # Calculate totals
            subtotal = Decimal('0')
            total_cgst = Decimal('0')
            total_sgst = Decimal('0')
            total_igst = Decimal('0')
            
            # Determine if IGST or CGST/SGST
            use_igst = (bill.vendor_state and bill.vendor_state.lower() != 'maharashtra')
            
            for i in range(len(item_names)):
                if not item_names[i].strip():
                    continue
                
                qty = Decimal(quantities[i]) if quantities[i] else Decimal('0')
                rate = Decimal(rates[i]) if rates[i] else Decimal('0')
                gst_rate = Decimal(gst_rates[i]) if gst_rates[i] else Decimal('0')
                
                # Calculate amounts
                line_total = qty * rate
                taxable_value = line_total
                
                if use_igst:
                    igst = (taxable_value * gst_rate / Decimal('100')).quantize(Decimal('0.01'))
                    cgst = Decimal('0')
                    sgst = Decimal('0')
                else:
                    cgst = (taxable_value * gst_rate / Decimal('200')).quantize(Decimal('0.01'))
                    sgst = cgst
                    igst = Decimal('0')
                
                item_total = taxable_value + cgst + sgst + igst
                
                # Create line item
                line_item = PurchaseBillItem()
                line_item.tenant_id = tenant_id
                
                # Link to inventory item if selected
                if item_ids[i] and item_ids[i].isdigit():
                    line_item.item_id = int(item_ids[i])
                
                line_item.item_name = item_names[i].strip()
                line_item.description = descriptions[i].strip() if i < len(descriptions) else ''
                line_item.hsn_code = hsn_codes[i].strip() if i < len(hsn_codes) else ''
                line_item.quantity = qty
                line_item.unit = units[i] if i < len(units) else 'pcs'
                line_item.rate = rate
                line_item.taxable_value = taxable_value
                line_item.gst_rate = gst_rate
                line_item.cgst_amount = cgst
                line_item.sgst_amount = sgst
                line_item.igst_amount = igst
                line_item.total_amount = item_total
                
                bill.items.append(line_item)
                
                # Add to totals
                subtotal += taxable_value
                total_cgst += cgst
                total_sgst += sgst
                total_igst += igst
            
            # Set bill totals
            bill.subtotal = subtotal
            bill.cgst_amount = total_cgst
            bill.sgst_amount = total_sgst
            bill.igst_amount = total_igst
            
            # Other charges and round-off
            other_charges = request.form.get('other_charges', '0')
            bill.other_charges = Decimal(other_charges) if other_charges else Decimal('0')
            
            # Calculate total
            calculated_total = subtotal + total_cgst + total_sgst + total_igst + bill.other_charges
            bill.total_amount = calculated_total.quantize(Decimal('0.01'))
            bill.balance_due = bill.total_amount
            
            # Set status
            bill.status = 'draft'
            bill.payment_status = 'unpaid'
            
            db.session.add(bill)
            db.session.commit()
            
            flash(f'✅ Purchase Bill {bill.bill_number} created successfully!', 'success')
            return redirect(url_for('purchase_bills.view_bill', bill_id=bill.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'❌ Error creating bill: {str(e)}', 'error')
            print(f"Error creating purchase bill: {str(e)}")
    
    # GET request - show form
    vendors = Vendor.query.filter_by(tenant_id=tenant_id, is_active=True).order_by(Vendor.name).all()
    sites = Site.query.filter_by(tenant_id=tenant_id).all()
    
    return render_template('admin/purchase_bills/create.html',
                         tenant=g.tenant,
                         vendors=vendors,
                         sites=sites,
                         today=date.today().strftime('%Y-%m-%d'))

@purchase_bills_bp.route('/<int:bill_id>')
@check_license
def view_bill(bill_id):
    """View purchase bill details"""
    tenant_id = get_current_tenant_id()
    bill = PurchaseBill.query.filter_by(id=bill_id, tenant_id=tenant_id).first_or_404()
    
    return render_template('admin/purchase_bills/view.html',
                         tenant=g.tenant,
                         bill=bill)

@purchase_bills_bp.route('/<int:bill_id>/edit', methods=['GET', 'POST'])
@check_license
def edit_bill(bill_id):
    """Edit purchase bill (only if draft)"""
    tenant_id = get_current_tenant_id()
    bill = PurchaseBill.query.filter_by(id=bill_id, tenant_id=tenant_id).first_or_404()
    
    if bill.status != 'draft':
        flash('⚠️ Only draft bills can be edited', 'warning')
        return redirect(url_for('purchase_bills.view_bill', bill_id=bill.id))
    
    if request.method == 'POST':
        try:
            # Update bill details
            bill.bill_date = datetime.strptime(request.form.get('bill_date'), '%Y-%m-%d').date()
            if request.form.get('due_date'):
                bill.due_date = datetime.strptime(request.form.get('due_date'), '%Y-%m-%d').date()
            
            # Update vendor details
            vendor_id = request.form.get('vendor_id')
            if vendor_id:
                vendor = Vendor.query.get(vendor_id)
                if vendor:
                    bill.vendor_id = vendor.id
                    bill.vendor_name = vendor.name
                    bill.vendor_phone = vendor.phone
                    bill.vendor_email = vendor.email
                    bill.vendor_gstin = vendor.gstin
                    bill.vendor_address = vendor.address
                    bill.vendor_state = vendor.state or 'Maharashtra'
            
            bill.reference_number = request.form.get('reference_number', '')
            bill.payment_terms = request.form.get('payment_terms', '')
            bill.notes = request.form.get('notes', '')
            bill.terms_conditions = request.form.get('terms_conditions', '')
            
            # Delete existing items
            PurchaseBillItem.query.filter_by(purchase_bill_id=bill.id).delete()
            
            # Re-add items (same logic as create)
            item_names = request.form.getlist('item_name[]')
            quantities = request.form.getlist('quantity[]')
            rates = request.form.getlist('rate[]')
            gst_rates = request.form.getlist('gst_rate[]')
            
            subtotal = Decimal('0')
            total_cgst = Decimal('0')
            total_sgst = Decimal('0')
            total_igst = Decimal('0')
            
            use_igst = (bill.vendor_state and bill.vendor_state.lower() != 'maharashtra')
            
            for i in range(len(item_names)):
                if not item_names[i].strip():
                    continue
                
                qty = Decimal(quantities[i]) if quantities[i] else Decimal('0')
                rate = Decimal(rates[i]) if rates[i] else Decimal('0')
                gst_rate = Decimal(gst_rates[i]) if gst_rates[i] else Decimal('0')
                
                taxable_value = qty * rate
                
                if use_igst:
                    igst = (taxable_value * gst_rate / Decimal('100')).quantize(Decimal('0.01'))
                    cgst = Decimal('0')
                    sgst = Decimal('0')
                else:
                    cgst = (taxable_value * gst_rate / Decimal('200')).quantize(Decimal('0.01'))
                    sgst = cgst
                    igst = Decimal('0')
                
                item_total = taxable_value + cgst + sgst + igst
                
                line_item = PurchaseBillItem()
                line_item.tenant_id = tenant_id
                line_item.purchase_bill_id = bill.id
                line_item.item_name = item_names[i].strip()
                line_item.quantity = qty
                line_item.rate = rate
                line_item.taxable_value = taxable_value
                line_item.gst_rate = gst_rate
                line_item.cgst_amount = cgst
                line_item.sgst_amount = sgst
                line_item.igst_amount = igst
                line_item.total_amount = item_total
                
                db.session.add(line_item)
                
                subtotal += taxable_value
                total_cgst += cgst
                total_sgst += sgst
                total_igst += igst
            
            bill.subtotal = subtotal
            bill.cgst_amount = total_cgst
            bill.sgst_amount = total_sgst
            bill.igst_amount = total_igst
            
            other_charges = request.form.get('other_charges', '0')
            bill.other_charges = Decimal(other_charges) if other_charges else Decimal('0')
            
            bill.total_amount = (subtotal + total_cgst + total_sgst + total_igst + bill.other_charges).quantize(Decimal('0.01'))
            bill.balance_due = bill.total_amount - bill.paid_amount
            
            db.session.commit()
            
            flash(f'✅ Purchase Bill {bill.bill_number} updated successfully!', 'success')
            return redirect(url_for('purchase_bills.view_bill', bill_id=bill.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'❌ Error updating bill: {str(e)}', 'error')
    
    vendors = Vendor.query.filter_by(tenant_id=tenant_id, is_active=True).order_by(Vendor.name).all()
    
    return render_template('admin/purchase_bills/edit.html',
                         tenant=g.tenant,
                         bill=bill,
                         vendors=vendors)

@purchase_bills_bp.route('/<int:bill_id>/approve', methods=['POST'])
@check_license
def approve_bill(bill_id):
    """Approve purchase bill"""
    tenant_id = get_current_tenant_id()
    bill = PurchaseBill.query.filter_by(id=bill_id, tenant_id=tenant_id).first_or_404()
    
    if bill.status != 'draft':
        flash('⚠️ Bill is already approved or cancelled', 'warning')
        return redirect(url_for('purchase_bills.view_bill', bill_id=bill.id))
    
    try:
        bill.status = 'approved'
        bill.approved_at = datetime.now(pytz.timezone('Asia/Kolkata'))
        bill.approved_by = session.get('tenant_admin_id')
        
        db.session.commit()
        
        flash(f'✅ Purchase Bill {bill.bill_number} approved successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error approving bill: {str(e)}', 'error')
    
    return redirect(url_for('purchase_bills.view_bill', bill_id=bill.id))

@purchase_bills_bp.route('/<int:bill_id>/delete', methods=['POST'])
@check_license
def delete_bill(bill_id):
    """Delete purchase bill (only if draft)"""
    tenant_id = get_current_tenant_id()
    bill = PurchaseBill.query.filter_by(id=bill_id, tenant_id=tenant_id).first_or_404()
    
    if bill.status != 'draft':
        flash('⚠️ Only draft bills can be deleted', 'warning')
        return redirect(url_for('purchase_bills.view_bill', bill_id=bill.id))
    
    try:
        db.session.delete(bill)
        db.session.commit()
        
        flash(f'✅ Purchase Bill {bill.bill_number} deleted successfully!', 'success')
        return redirect(url_for('purchase_bills.list_bills'))
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error deleting bill: {str(e)}', 'error')
        return redirect(url_for('purchase_bills.view_bill', bill_id=bill.id))

# API Endpoints

@purchase_bills_bp.route('/api/search-items')
def api_search_items():
    """API endpoint to search items"""
    tenant_id = get_current_tenant_id()
    query = request.args.get('q', '').strip()
    
    if len(query) < 2:
        return jsonify([])
    
    items = Item.query.filter_by(tenant_id=tenant_id).filter(
        db.or_(
            Item.name.like(f'%{query}%'),
            Item.item_code.like(f'%{query}%')
        )
    ).limit(20).all()
    
    results = []
    for item in items:
        # Extract GST rate from tax_preference
        gst_rate = 18  # default
        if item.tax_preference:
            try:
                if 'GST@' in item.tax_preference:
                    gst_rate = float(item.tax_preference.split('@')[1].replace('%', ''))
            except:
                pass
        
        results.append({
            'id': item.id,
            'name': item.name,
            'item_code': item.item_code,
            'unit': item.unit or 'pcs',
            'purchase_price': float(item.purchase_price or 0),
            'sale_price': float(item.sale_price or 0),
            'hsn_code': item.hsn_code or '',
            'gst_rate': gst_rate
        })
    
    return jsonify(results)

@purchase_bills_bp.route('/api/vendors/search')
def api_search_vendors():
    """API endpoint to search vendors"""
    tenant_id = get_current_tenant_id()
    query = request.args.get('q', '').strip()
    
    if len(query) < 2:
        return jsonify([])
    
    vendors = Vendor.query.filter_by(tenant_id=tenant_id, is_active=True).filter(
        db.or_(
            Vendor.name.like(f'%{query}%'),
            Vendor.vendor_code.like(f'%{query}%'),
            Vendor.company_name.like(f'%{query}%')
        )
    ).limit(20).all()
    
    results = []
    for vendor in vendors:
        results.append({
            'id': vendor.id,
            'name': vendor.name,
            'company_name': vendor.company_name or '',
            'phone': vendor.phone or '',
            'email': vendor.email or '',
            'gstin': vendor.gstin or '',
            'address': vendor.address or '',
            'state': vendor.state or 'Maharashtra',
            'payment_terms_days': vendor.payment_terms_days or 30
        })
    
    return jsonify(results)

