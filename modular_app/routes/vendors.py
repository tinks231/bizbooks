from flask import Blueprint, render_template, request, redirect, url_for, flash, g, jsonify
from models.database import db
from models.vendor import Vendor
from models.purchase_request import PurchaseRequest
from utils.tenant_middleware import require_tenant, get_current_tenant_id
from utils.license_check import check_license
from functools import wraps
from flask import session
from datetime import datetime
from sqlalchemy import func, desc

vendors_bp = Blueprint('vendors', __name__, url_prefix='/admin/vendors')

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'tenant_admin_id' not in session:
            flash('Please login first', 'error')
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function

@vendors_bp.route('/')
@require_tenant
@check_license
@login_required
def index():
    """List all vendors"""
    tenant_id = get_current_tenant_id()
    
    # Search and filter
    search = request.args.get('search', '').strip()
    status_filter = request.args.get('status', 'all')
    
    query = Vendor.query.filter_by(tenant_id=tenant_id)
    
    if search:
        query = query.filter(
            (Vendor.name.ilike(f'%{search}%')) |
            (Vendor.vendor_code.ilike(f'%{search}%')) |
            (Vendor.company_name.ilike(f'%{search}%')) |
            (Vendor.phone.ilike(f'%{search}%'))
        )
    
    if status_filter == 'active':
        query = query.filter_by(is_active=True)
    elif status_filter == 'inactive':
        query = query.filter_by(is_active=False)
    
    vendors = query.order_by(Vendor.vendor_code.desc()).all()
    
    # Calculate purchase count for each vendor
    for vendor in vendors:
        vendor.purchase_count = vendor.get_total_purchases()
    
    return render_template('admin/vendors/list.html',
                         tenant=g.tenant,
                         vendors=vendors,
                         search=search,
                         status_filter=status_filter)


@vendors_bp.route('/add', methods=['GET', 'POST'])
@require_tenant
@check_license
@login_required
def add():
    """Add new vendor"""
    tenant_id = get_current_tenant_id()
    
    if request.method == 'POST':
        try:
            # Check if vendor code is provided or auto-generate
            vendor_code = request.form.get('vendor_code', '').strip()
            if not vendor_code:
                vendor_code = Vendor.generate_vendor_code(tenant_id)
            
            # Check if vendor code already exists
            existing = Vendor.query.filter_by(
                tenant_id=tenant_id,
                vendor_code=vendor_code
            ).first()
            
            if existing:
                flash(f'Vendor code {vendor_code} already exists!', 'error')
                # If AJAX request, return JSON
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json or 'application/json' in request.headers.get('Accept', ''):
                    return jsonify({'success': False, 'error': f'Vendor code {vendor_code} already exists!'}), 400
                return redirect(url_for('vendors.add'))
            
            # Create vendor
            vendor = Vendor(
                tenant_id=tenant_id,
                vendor_code=vendor_code,
                name=request.form.get('name'),
                company_name=request.form.get('company_name'),
                phone=request.form.get('phone'),
                email=request.form.get('email'),
                address=request.form.get('address'),
                gstin=request.form.get('gstin'),
                state=request.form.get('state', 'Maharashtra'),
                credit_limit=float(request.form.get('credit_limit', 0) or 0),
                payment_terms_days=int(request.form.get('payment_terms_days', 30) or 30),
                opening_balance=float(request.form.get('opening_balance', 0) or 0),
                notes=request.form.get('notes'),
                is_active=True
            )
            
            db.session.add(vendor)
            db.session.commit()
            
            flash(f'Vendor {vendor.vendor_code} added successfully!', 'success')
            
            # If AJAX request, return JSON with success message and vendor data
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json or 'application/json' in request.headers.get('Accept', ''):
                return jsonify({
                    'success': True,
                    'message': f'Vendor {vendor.vendor_code} added successfully!',
                    'vendor': {
                        'id': vendor.id,
                        'vendor_code': vendor.vendor_code,
                        'name': vendor.name,
                        'phone': vendor.phone,
                        'email': vendor.email,
                        'gstin': vendor.gstin,
                        'state': vendor.state,
                        'address': vendor.address
                    }
                })
            
            return redirect(url_for('vendors.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding vendor: {str(e)}', 'error')
            # If AJAX request, return JSON error
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json or 'application/json' in request.headers.get('Accept', ''):
                return jsonify({'success': False, 'error': str(e)}), 500
    
    # GET request - show form
    next_vendor_code = Vendor.generate_vendor_code(tenant_id)
    
    return render_template('admin/vendors/add.html',
                         tenant=g.tenant,
                         next_vendor_code=next_vendor_code)


@vendors_bp.route('/<int:vendor_id>/edit', methods=['GET', 'POST'])
@require_tenant
@check_license
@login_required
def edit(vendor_id):
    """Edit vendor"""
    tenant_id = get_current_tenant_id()
    vendor = Vendor.query.filter_by(id=vendor_id, tenant_id=tenant_id).first_or_404()
    
    if request.method == 'POST':
        try:
            vendor.name = request.form.get('name')
            vendor.company_name = request.form.get('company_name')
            vendor.phone = request.form.get('phone')
            vendor.email = request.form.get('email')
            vendor.address = request.form.get('address')
            vendor.gstin = request.form.get('gstin')
            vendor.state = request.form.get('state', 'Maharashtra')
            vendor.credit_limit = float(request.form.get('credit_limit', 0) or 0)
            vendor.payment_terms_days = int(request.form.get('payment_terms_days', 30) or 30)
            vendor.opening_balance = float(request.form.get('opening_balance', 0) or 0)
            vendor.notes = request.form.get('notes')
            vendor.is_active = request.form.get('is_active') == 'on'
            vendor.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            flash(f'Vendor {vendor.vendor_code} updated successfully!', 'success')
            return redirect(url_for('vendors.view', vendor_id=vendor.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating vendor: {str(e)}', 'error')
    
    return render_template('admin/vendors/add.html',
                         tenant=g.tenant,
                         vendor=vendor,
                         edit_mode=True)


@vendors_bp.route('/<int:vendor_id>')
@require_tenant
@check_license
@login_required
def view(vendor_id):
    """View vendor details"""
    tenant_id = get_current_tenant_id()
    vendor = Vendor.query.filter_by(id=vendor_id, tenant_id=tenant_id).first_or_404()
    
    # Get recent purchase requests from this vendor
    purchase_requests = PurchaseRequest.query.filter_by(
        tenant_id=tenant_id,
        vendor_name=vendor.name
    ).order_by(PurchaseRequest.created_at.desc()).limit(10).all()
    
    return render_template('admin/vendors/view.html',
                         tenant=g.tenant,
                         vendor=vendor,
                         purchase_requests=purchase_requests)


@vendors_bp.route('/<int:vendor_id>/ledger')
@require_tenant
@check_license
@login_required
def ledger(vendor_id):
    """View vendor ledger/statement with all transactions"""
    from models.purchase_bill import PurchaseBill
    from models.vendor_payment import VendorPayment
    from datetime import datetime, timedelta
    from decimal import Decimal
    
    tenant_id = get_current_tenant_id()
    vendor = Vendor.query.filter_by(id=vendor_id, tenant_id=tenant_id).first_or_404()
    
    # Get date range filters
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    
    # Default to last 3 months if no dates provided
    if not start_date:
        start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
    if not end_date:
        end_date = datetime.now().strftime('%Y-%m-%d')
    
    # Get all APPROVED purchase bills for this vendor (drafts don't affect balance)
    bills_query = PurchaseBill.query.filter_by(
        tenant_id=tenant_id,
        vendor_id=vendor_id,
        status='approved'  # Only approved bills affect ledger
    )
    
    if start_date:
        bills_query = bills_query.filter(PurchaseBill.bill_date >= datetime.strptime(start_date, '%Y-%m-%d').date())
    if end_date:
        bills_query = bills_query.filter(PurchaseBill.bill_date <= datetime.strptime(end_date, '%Y-%m-%d').date())
    
    bills = bills_query.order_by(PurchaseBill.bill_date.asc()).all()
    
    # Get all payments for this vendor
    payments_query = VendorPayment.query.filter_by(
        tenant_id=tenant_id,
        vendor_id=vendor_id
    )
    
    if start_date:
        payments_query = payments_query.filter(VendorPayment.payment_date >= datetime.strptime(start_date, '%Y-%m-%d').date())
    if end_date:
        payments_query = payments_query.filter(VendorPayment.payment_date <= datetime.strptime(end_date, '%Y-%m-%d').date())
    
    payments = payments_query.order_by(VendorPayment.payment_date.asc()).all()
    
    # Combine transactions and sort by date
    transactions = []
    
    # Add bills as debit transactions
    for bill in bills:
        transactions.append({
            'date': bill.bill_date,
            'type': 'bill',
            'reference': bill.bill_number,
            'description': f'Purchase Bill - {len(bill.items)} items',
            'debit': float(bill.total_amount),
            'credit': 0,
            'status': bill.status,
            'payment_status': bill.payment_status,
            'id': bill.id
        })
    
    # Add payments as credit transactions
    for payment in payments:
        transactions.append({
            'date': payment.payment_date,
            'type': 'payment',
            'reference': payment.payment_number,
            'description': f'Payment - {payment.payment_method}',
            'debit': 0,
            'credit': float(payment.amount),
            'status': 'paid',
            'payment_status': None,
            'id': payment.id
        })
    
    # Sort by date
    transactions.sort(key=lambda x: x['date'])
    
    # Calculate running balance
    running_balance = float(vendor.opening_balance or 0)
    for txn in transactions:
        running_balance += txn['debit'] - txn['credit']
        txn['balance'] = running_balance
    
    # Calculate summary
    total_bills = sum([t['debit'] for t in transactions])
    total_payments = sum([t['credit'] for t in transactions])
    current_balance = running_balance
    
    return render_template('admin/vendors/ledger.html',
                         tenant=g.tenant,
                         vendor=vendor,
                         transactions=transactions,
                         start_date=start_date,
                         end_date=end_date,
                         opening_balance=float(vendor.opening_balance or 0),
                         total_bills=total_bills,
                         total_payments=total_payments,
                         current_balance=current_balance)


@vendors_bp.route('/<int:vendor_id>/delete', methods=['POST'])
@require_tenant
@check_license
@login_required
def delete(vendor_id):
    """Delete vendor"""
    tenant_id = get_current_tenant_id()
    vendor = Vendor.query.filter_by(id=vendor_id, tenant_id=tenant_id).first_or_404()
    
    try:
        # Check if vendor has any purchase requests
        purchase_count = PurchaseRequest.query.filter_by(
            tenant_id=tenant_id,
            vendor_name=vendor.name
        ).count()
        
        if purchase_count > 0:
            flash(f'Cannot delete vendor {vendor.vendor_code} - has {purchase_count} purchase request(s)', 'error')
            return redirect(url_for('vendors.view', vendor_id=vendor.id))
        
        db.session.delete(vendor)
        db.session.commit()
        
        flash(f'Vendor {vendor.vendor_code} deleted successfully!', 'success')
        return redirect(url_for('vendors.index'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting vendor: {str(e)}', 'error')
        return redirect(url_for('vendors.view', vendor_id=vendor.id))


@vendors_bp.route('/api/search')
@require_tenant
@login_required
def api_search():
    """API endpoint for vendor search (autocomplete)"""
    tenant_id = get_current_tenant_id()
    search_term = request.args.get('q', '').strip()
    
    if len(search_term) < 2:
        return jsonify([])
    
    vendors = Vendor.query.filter_by(tenant_id=tenant_id, is_active=True).filter(
        (Vendor.name.ilike(f'%{search_term}%')) |
        (Vendor.company_name.ilike(f'%{search_term}%')) |
        (Vendor.vendor_code.ilike(f'%{search_term}%')) |
        (Vendor.phone.ilike(f'%{search_term}%'))
    ).limit(10).all()
    
    result = []
    for vendor in vendors:
        result.append({
            'id': vendor.id,
            'vendor_code': vendor.vendor_code,
            'name': vendor.name,
            'company_name': vendor.company_name or '',
            'phone': vendor.phone or '',
            'email': vendor.email or '',
            'gstin': vendor.gstin or '',
            'address': vendor.address or '',
            'state': vendor.state or 'Maharashtra'
        })
    
    return jsonify(result)

