from flask import Blueprint, render_template, request, redirect, url_for, flash, g, jsonify
from models.database import db
from models.customer import Customer
from models.invoice import Invoice
from utils.tenant_middleware import require_tenant, get_current_tenant_id
from utils.license_check import check_license
from functools import wraps
from flask import session
from datetime import datetime, timedelta
from sqlalchemy import func, desc

customers_bp = Blueprint('customers', __name__, url_prefix='/admin/customers')

# Login required decorator (same pattern as other routes)
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'tenant_admin_id' not in session:
            flash('Please login first', 'error')
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function

@customers_bp.route('/')
@require_tenant
@check_license
@login_required
def index():
    """List all customers"""
    tenant_id = get_current_tenant_id()
    
    # Search and filter
    search = request.args.get('search', '').strip()
    status_filter = request.args.get('status', 'all')
    
    query = Customer.query.filter_by(tenant_id=tenant_id)
    
    if search:
        query = query.filter(
            (Customer.name.ilike(f'%{search}%')) |
            (Customer.customer_code.ilike(f'%{search}%')) |
            (Customer.phone.ilike(f'%{search}%'))
        )
    
    if status_filter == 'active':
        query = query.filter_by(is_active=True)
    elif status_filter == 'inactive':
        query = query.filter_by(is_active=False)
    
    customers = query.order_by(Customer.customer_code.desc()).all()
    
    # Calculate outstanding for each customer
    for customer in customers:
        customer.outstanding = customer.get_outstanding_balance()
        customer.invoice_count = customer.get_total_invoices()
    
    return render_template('admin/customers/list.html',
                         customers=customers,
                         search=search,
                         status_filter=status_filter)


@customers_bp.route('/add', methods=['GET', 'POST'])
@require_tenant
@check_license
@login_required
def add():
    """Add new customer"""
    tenant_id = get_current_tenant_id()
    
    if request.method == 'POST':
        try:
            # Check if customer code is provided or auto-generate
            customer_code = request.form.get('customer_code', '').strip()
            if not customer_code:
                customer_code = Customer.generate_customer_code(tenant_id)
            
            # Check if customer code already exists
            existing = Customer.query.filter_by(
                tenant_id=tenant_id,
                customer_code=customer_code
            ).first()
            
            if existing:
                flash(f'Customer code {customer_code} already exists!', 'error')
                return redirect(url_for('customers.add'))
            
            # Create customer
            customer = Customer(
                tenant_id=tenant_id,
                customer_code=customer_code,
                name=request.form.get('name'),
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
            
            db.session.add(customer)
            db.session.commit()
            
            flash(f'Customer {customer.customer_code} added successfully!', 'success')
            return redirect(url_for('customers.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding customer: {str(e)}', 'error')
    
    # GET request - show form
    next_customer_code = Customer.generate_customer_code(tenant_id)
    
    return render_template('admin/customers/add.html',
                         next_customer_code=next_customer_code)


@customers_bp.route('/<int:customer_id>/edit', methods=['GET', 'POST'])
@require_tenant
@check_license
@login_required
def edit(customer_id):
    """Edit customer"""
    tenant_id = get_current_tenant_id()
    customer = Customer.query.filter_by(id=customer_id, tenant_id=tenant_id).first_or_404()
    
    if request.method == 'POST':
        try:
            customer.name = request.form.get('name')
            customer.phone = request.form.get('phone')
            customer.email = request.form.get('email')
            customer.address = request.form.get('address')
            customer.gstin = request.form.get('gstin')
            customer.state = request.form.get('state', 'Maharashtra')
            customer.credit_limit = float(request.form.get('credit_limit', 0) or 0)
            customer.payment_terms_days = int(request.form.get('payment_terms_days', 30) or 30)
            customer.opening_balance = float(request.form.get('opening_balance', 0) or 0)
            customer.notes = request.form.get('notes')
            customer.is_active = request.form.get('is_active') == 'on'
            customer.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            flash(f'Customer {customer.customer_code} updated successfully!', 'success')
            return redirect(url_for('customers.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating customer: {str(e)}', 'error')
    
    return render_template('admin/customers/edit.html', customer=customer)


@customers_bp.route('/<int:customer_id>/ledger')
@require_tenant
@check_license
@login_required
def ledger(customer_id):
    """View customer ledger (all invoices)"""
    tenant_id = get_current_tenant_id()
    customer = Customer.query.filter_by(id=customer_id, tenant_id=tenant_id).first_or_404()
    
    # Get all invoices for this customer
    invoices = Invoice.query.filter_by(customer_id=customer_id)\
        .order_by(Invoice.invoice_date.desc()).all()
    
    # Calculate totals
    total_billed = sum(inv.total_amount for inv in invoices)
    total_paid = sum(inv.paid_amount for inv in invoices)
    total_outstanding = sum(inv.total_amount for inv in invoices if inv.payment_status == 'unpaid')
    
    # Get aging analysis (overdue invoices)
    today = datetime.now().date()
    aging_data = {
        '0-30': [],
        '31-60': [],
        '61-90': [],
        '90+': []
    }
    
    for invoice in invoices:
        if invoice.payment_status == 'unpaid' and invoice.due_date:
            days_overdue = (today - invoice.due_date).days
            if days_overdue > 0:
                if days_overdue <= 30:
                    aging_data['0-30'].append(invoice)
                elif days_overdue <= 60:
                    aging_data['31-60'].append(invoice)
                elif days_overdue <= 90:
                    aging_data['61-90'].append(invoice)
                else:
                    aging_data['90+'].append(invoice)
    
    return render_template('admin/customers/ledger.html',
                         customer=customer,
                         invoices=invoices,
                         total_billed=total_billed,
                         total_paid=total_paid,
                         total_outstanding=total_outstanding,
                         aging_data=aging_data)


@customers_bp.route('/outstanding')
@require_tenant
@check_license
@login_required
def outstanding():
    """Outstanding report - all customers with unpaid invoices"""
    tenant_id = get_current_tenant_id()
    
    # Get all customers with outstanding balance
    customers = Customer.query.filter_by(tenant_id=tenant_id, is_active=True)\
        .order_by(Customer.name).all()
    
    # Calculate outstanding for each
    customers_with_outstanding = []
    total_outstanding_all = 0
    
    for customer in customers:
        outstanding = customer.get_outstanding_balance()
        if outstanding > 0:
            unpaid_count = Invoice.query.filter_by(
                customer_id=customer.id,
                payment_status='unpaid'
            ).count()
            
            customers_with_outstanding.append({
                'customer': customer,
                'outstanding': outstanding,
                'unpaid_count': unpaid_count
            })
            total_outstanding_all += outstanding
    
    # Sort by outstanding amount (highest first)
    customers_with_outstanding.sort(key=lambda x: x['outstanding'], reverse=True)
    
    return render_template('admin/customers/outstanding.html',
                         customers_data=customers_with_outstanding,
                         total_outstanding_all=total_outstanding_all)


@customers_bp.route('/api/search')
@require_tenant
@login_required
def api_search():
    """API endpoint for customer autocomplete"""
    tenant_id = get_current_tenant_id()
    search = request.args.get('q', '').strip()
    
    if len(search) < 2:
        return jsonify([])
    
    customers = Customer.query.filter_by(tenant_id=tenant_id, is_active=True)\
        .filter(
            (Customer.name.ilike(f'%{search}%')) |
            (Customer.customer_code.ilike(f'%{search}%')) |
            (Customer.phone.ilike(f'%{search}%'))
        )\
        .limit(10).all()
    
    result = []
    for customer in customers:
        result.append({
            'id': customer.id,
            'customer_code': customer.customer_code,
            'name': customer.name,
            'phone': customer.phone or '',
            'email': customer.email or '',
            'address': customer.address or '',
            'gstin': customer.gstin or '',
            'state': customer.state or 'Maharashtra',
            'outstanding': customer.get_outstanding_balance()
        })
    
    return jsonify(result)

