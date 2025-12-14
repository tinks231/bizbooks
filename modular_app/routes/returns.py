"""
Returns & Refunds Management
Handles customer returns with refund processing and accounting integration
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, g, jsonify
from models import db, Return, ReturnItem, Invoice, InvoiceItem, Item, ItemStock, BankAccount, Customer
from models import AccountTransaction, LoyaltyTransaction, CustomerLoyaltyPoints
from utils.tenant_middleware import require_tenant, get_current_tenant_id
from sqlalchemy import text, func
from datetime import datetime, date
from decimal import Decimal
import pytz
import json

returns_bp = Blueprint('returns', __name__, url_prefix='/admin/returns')


@returns_bp.before_request
@require_tenant
def check_tenant():
    """Ensure tenant context exists for all return routes"""
    pass


@returns_bp.route('/')
def index():
    """List all returns with filtering"""
    tenant_id = get_current_tenant_id()
    
    # Get filter parameters
    status_filter = request.args.get('status', 'all')
    date_range = request.args.get('date_range', '30')  # Last 30 days
    search_query = request.args.get('search', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 50
    
    # Base query
    query = Return.query.filter_by(tenant_id=tenant_id)
    
    # Apply filters
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    
    # Date range filter
    if date_range != 'all':
        days = int(date_range)
        ist = pytz.timezone('Asia/Kolkata')
        cutoff_date = datetime.now(ist).date()
        from datetime import timedelta
        cutoff_date = cutoff_date - timedelta(days=days)
        query = query.filter(Return.return_date >= cutoff_date)
    
    # Search filter
    if search_query:
        query = query.filter(
            db.or_(
                Return.return_number.like(f'%{search_query}%'),
                Return.invoice_number.like(f'%{search_query}%'),
                Return.customer_name.like(f'%{search_query}%')
            )
        )
    
    # Paginate
    query = query.order_by(Return.return_date.desc(), Return.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    returns_list = pagination.items
    
    # Calculate summary stats
    total_returns = Return.query.filter_by(tenant_id=tenant_id).count()
    total_refunded = db.session.query(func.sum(Return.total_amount)).filter(
        Return.tenant_id == tenant_id,
        Return.status == 'completed'
    ).scalar() or 0
    
    # Calculate return rate (returns vs sales)
    total_sales = db.session.query(func.sum(Invoice.total_amount)).filter(
        Invoice.tenant_id == tenant_id
    ).scalar() or 1  # Avoid division by zero
    
    return_rate = (float(total_refunded) / float(total_sales)) * 100 if total_sales > 0 else 0
    
    return render_template('admin/returns/index.html',
                         tenant=g.tenant,
                         returns=returns_list,
                         pagination=pagination,
                         status_filter=status_filter,
                         date_range=date_range,
                         search_query=search_query,
                         total_returns=total_returns,
                         total_refunded=total_refunded,
                         return_rate=return_rate)


@returns_bp.route('/new', methods=['GET', 'POST'])
def create():
    """Create new return - search invoice and select items"""
    tenant_id = get_current_tenant_id()
    
    if request.method == 'POST':
        try:
            # Get form data
            invoice_id = request.form.get('invoice_id')
            return_reason = request.form.get('return_reason')
            reason_details = request.form.get('reason_details', '')
            refund_method = request.form.get('refund_method')
            customer_notes = request.form.get('customer_notes', '')
            notes = request.form.get('notes', '')
            
            # Get invoice
            invoice = Invoice.query.filter_by(id=invoice_id, tenant_id=tenant_id).first()
            if not invoice:
                flash('❌ Invoice not found', 'error')
                return redirect(url_for('returns.create'))
            
            # Create return record
            ret = Return()
            ret.tenant_id = tenant_id
            ret.generate_return_number()
            ret.invoice_id = invoice.id
            ret.invoice_number = invoice.invoice_number
            ret.customer_id = invoice.customer_id
            ret.customer_name = invoice.customer_name
            ret.return_date = date.today()
            ret.invoice_date = invoice.invoice_date
            ret.return_reason = return_reason
            ret.reason_details = reason_details
            ret.refund_method = refund_method
            ret.customer_notes = customer_notes
            ret.notes = notes
            ret.status = 'pending'  # Pending approval
            
            # Process return items
            item_ids = request.form.getlist('return_item_id[]')
            quantities = request.form.getlist('return_quantity[]')
            conditions = request.form.getlist('item_condition[]')
            
            total_amount = Decimal('0')
            taxable_amount = Decimal('0')
            cgst_amount = Decimal('0')
            sgst_amount = Decimal('0')
            igst_amount = Decimal('0')
            
            # Determine if same state for GST calculation
            tenant_settings = json.loads(g.tenant.settings) if g.tenant.settings else {}
            tenant_state = tenant_settings.get('state', 'Maharashtra')
            is_same_state = (invoice.customer_state == tenant_state)
            
            for idx, item_id in enumerate(item_ids):
                qty_returned = int(quantities[idx])
                if qty_returned <= 0:
                    continue
                
                # Get original invoice item
                invoice_item = InvoiceItem.query.get(item_id)
                if not invoice_item:
                    continue
                
                # Create return item
                return_item = ReturnItem()
                return_item.tenant_id = tenant_id
                return_item.invoice_item_id = invoice_item.id
                return_item.product_id = invoice_item.item_id
                return_item.product_name = invoice_item.item_name
                return_item.hsn_code = invoice_item.hsn_code or ''
                return_item.quantity_sold = int(invoice_item.quantity)
                return_item.quantity_returned = qty_returned
                return_item.unit = invoice_item.unit
                return_item.unit_price = Decimal(str(invoice_item.rate))
                return_item.gst_rate = Decimal(str(invoice_item.gst_rate))
                return_item.item_condition = conditions[idx] if idx < len(conditions) else 'resellable'
                return_item.return_to_inventory = (return_item.item_condition == 'resellable')
                
                # Calculate amounts
                return_item.calculate_amounts(is_same_state=is_same_state)
                
                # Add to return
                ret.items.append(return_item)
                
                # Accumulate totals
                total_amount += return_item.total_amount
                taxable_amount += return_item.taxable_amount
                cgst_amount += return_item.cgst_amount or Decimal('0')
                sgst_amount += return_item.sgst_amount or Decimal('0')
                igst_amount += return_item.igst_amount or Decimal('0')
            
            # Set return totals
            ret.total_amount = total_amount
            ret.taxable_amount = taxable_amount
            ret.cgst_amount = cgst_amount
            ret.sgst_amount = sgst_amount
            ret.igst_amount = igst_amount
            
            db.session.add(ret)
            db.session.commit()
            
            flash(f'✅ Return {ret.return_number} created! Status: Pending Approval', 'success')
            return redirect(url_for('returns.view', return_id=ret.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'❌ Error creating return: {str(e)}', 'error')
            print(f"Error creating return: {str(e)}")
            import traceback
            traceback.print_exc()
    
    # GET - show form
    # Get recent invoices for quick selection
    recent_invoices = Invoice.query.filter_by(
        tenant_id=tenant_id
    ).order_by(Invoice.invoice_date.desc()).limit(100).all()
    
    return render_template('admin/returns/create.html',
                         tenant=g.tenant,
                         recent_invoices=recent_invoices)


@returns_bp.route('/<int:return_id>')
def view(return_id):
    """View return details"""
    tenant_id = get_current_tenant_id()
    ret = Return.query.filter_by(id=return_id, tenant_id=tenant_id).first_or_404()
    
    # Get available bank/cash accounts for refund
    bank_accounts = BankAccount.query.filter_by(
        tenant_id=tenant_id,
        is_active=True
    ).order_by(BankAccount.account_type, BankAccount.account_name).all()
    
    return render_template('admin/returns/view.html',
                         tenant=g.tenant,
                         return_obj=ret,
                         bank_accounts=bank_accounts)


@returns_bp.route('/<int:return_id>/approve', methods=['POST'])
def approve(return_id):
    """Approve return and process refund"""
    tenant_id = get_current_tenant_id()
    ret = Return.query.filter_by(id=return_id, tenant_id=tenant_id).first_or_404()
    
    if ret.status != 'pending':
        flash('⚠️ Return is not pending approval', 'warning')
        return redirect(url_for('returns.view', return_id=return_id))
    
    try:
        # Get refund account if cash/bank refund
        payment_account_id = request.form.get('payment_account_id')
        payment_reference = request.form.get('payment_reference', '')
        
        # Get tenant settings for return window
        tenant_settings = json.loads(g.tenant.settings) if g.tenant.settings else {}
        return_window_days = int(tenant_settings.get('return_window_days', 30))
        
        # Check if within return window (auto-approve) or requires approval
        is_within_window = ret.is_within_return_window(return_window_days)
        
        from flask import session
        
        # STEP 1: Restock inventory for resellable items
        _restock_inventory(ret, tenant_id)
        
        # STEP 2: Process refund (if paid invoice)
        if ret.invoice and ret.invoice.payment_status == 'paid':
            if ret.refund_method in ['cash', 'bank']:
                _process_refund_payment(ret, tenant_id, payment_account_id, payment_reference)
        
        # STEP 3: Adjust invoice for unpaid returns
        if ret.invoice and ret.invoice.payment_status != 'paid':
            _adjust_unpaid_invoice(ret, tenant_id)
        
        # STEP 4: Generate credit note
        ret.generate_credit_note_number()
        
        # STEP 5: Reverse loyalty points
        _reverse_loyalty_points(ret, tenant_id)
        
        # STEP 6: Update return status
        ret.status = 'approved'
        ret.approved_at = datetime.now(pytz.timezone('Asia/Kolkata'))
        ret.approved_by = session.get('user_id')
        ret.refund_processed_date = date.today()
        
        if payment_account_id:
            ret.payment_account_id = payment_account_id
        ret.payment_reference = payment_reference
        
        db.session.commit()
        
        flash(f'✅ Return {ret.return_number} approved! Credit Note: {ret.credit_note_number}', 'success')
        return redirect(url_for('returns.view', return_id=return_id))
        
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error approving return: {str(e)}', 'error')
        print(f"Error approving return: {str(e)}")
        import traceback
        traceback.print_exc()
        return redirect(url_for('returns.view', return_id=return_id))


@returns_bp.route('/<int:return_id>/reject', methods=['POST'])
def reject(return_id):
    """Reject return"""
    tenant_id = get_current_tenant_id()
    ret = Return.query.filter_by(id=return_id, tenant_id=tenant_id).first_or_404()
    
    if ret.status != 'pending':
        flash('⚠️ Return is not pending approval', 'warning')
        return redirect(url_for('returns.view', return_id=return_id))
    
    try:
        rejection_reason = request.form.get('rejection_reason', '')
        
        ret.status = 'rejected'
        ret.rejection_reason = rejection_reason
        
        from flask import session
        ret.approved_by = session.get('user_id')
        ret.approved_at = datetime.now(pytz.timezone('Asia/Kolkata'))
        
        db.session.commit()
        
        flash(f'❌ Return {ret.return_number} rejected', 'info')
        return redirect(url_for('returns.view', return_id=return_id))
        
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error rejecting return: {str(e)}', 'error')
        return redirect(url_for('returns.view', return_id=return_id))


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def _restock_inventory(ret, tenant_id):
    """Restock inventory for returned items"""
    from models import Site, ItemStockMovement
    
    # Get default site
    default_site = Site.query.filter_by(tenant_id=tenant_id, active=True).first()
    if not default_site:
        default_site = Site.query.filter_by(tenant_id=tenant_id).first()
    
    if not default_site:
        raise Exception("No site found for inventory restocking")
    
    total_cost_value = Decimal('0')
    
    for return_item in ret.items:
        if not return_item.return_to_inventory or not return_item.product_id:
            continue
        
        # Get or create item stock
        item_stock = ItemStock.query.filter_by(
            item_id=return_item.product_id,
            site_id=default_site.id
        ).first()
        
        if not item_stock:
            item_stock = ItemStock()
            item_stock.item_id = return_item.product_id
            item_stock.site_id = default_site.id
            item_stock.tenant_id = tenant_id
            item_stock.quantity_available = 0
            item_stock.stock_value = Decimal('0')
            db.session.add(item_stock)
        
        # Increase stock
        item_stock.quantity_available += return_item.quantity_returned
        
        # Update stock value (add back the cost)
        item = Item.query.get(return_item.product_id)
        if item and item.cost_price:
            cost_value = Decimal(str(item.cost_price)) * return_item.quantity_returned
            item_stock.stock_value += cost_value
            total_cost_value += cost_value
        
        # Create stock movement record
        movement = ItemStockMovement()
        movement.item_id = return_item.product_id
        movement.site_id = default_site.id
        movement.tenant_id = tenant_id
        movement.movement_type = 'return_in'
        movement.quantity = return_item.quantity_returned
        movement.reference_type = 'return'
        movement.reference_id = ret.id
        movement.notes = f'Customer return: {ret.return_number}'
        movement.movement_date = ret.return_date
        
        db.session.add(movement)
    
    # Create accounting entry to balance the inventory increase
    # When inventory is restocked, we need to reverse the COGS that was recorded when sold
    # DEBIT Inventory (already reflected in item_stock.stock_value)
    # CREDIT COGS (reduce expense)
    if total_cost_value > 0:
        ist = pytz.timezone('Asia/Kolkata')
        now = datetime.now(ist)
        
        db.session.execute(text("""
            INSERT INTO account_transactions
            (tenant_id, account_id, transaction_date, transaction_type,
             debit_amount, credit_amount, balance_after, reference_type, reference_id,
             voucher_number, narration, created_at, created_by)
            VALUES (:tenant_id, NULL, :transaction_date, 'cogs_reversal',
                    0.00, :credit_amount, 0.00, 'return', :return_id,
                    :voucher, :narration, :created_at, NULL)
        """), {
            'tenant_id': tenant_id,
            'transaction_date': ret.return_date,
            'credit_amount': float(total_cost_value),
            'return_id': ret.id,
            'voucher': ret.return_number,
            'narration': f'COGS reversal for returned inventory - {ret.return_number}',
            'created_at': now
        })
        
        print(f"✅ Restocked {len(ret.items)} item(s) to inventory")
        print(f"✅ Created COGS reversal entry: ₹{total_cost_value}")
    else:
        print(f"✅ Restocked {len(ret.items)} item(s) to inventory")


def _process_refund_payment(ret, tenant_id, payment_account_id, payment_reference):
    """Process cash/bank refund and create accounting entries"""
    if not payment_account_id:
        raise Exception("Payment account is required for cash/bank refunds")
    
    account = BankAccount.query.get(payment_account_id)
    if not account or account.tenant_id != tenant_id:
        raise Exception("Invalid payment account")
    
    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.now(ist)
    
    # DOUBLE-ENTRY ACCOUNTING FOR REFUND
    # DEBIT Sales Returns (reduces income)
    # DEBIT CGST/SGST/IGST Receivable (reduces tax liability)
    # CREDIT Cash/Bank (money going out)
    
    # Entry 1: DEBIT Sales Returns
    db.session.execute(text("""
        INSERT INTO account_transactions
        (tenant_id, account_id, transaction_date, transaction_type,
         debit_amount, credit_amount, balance_after, reference_type, reference_id,
         voucher_number, narration, created_at, created_by)
        VALUES (:tenant_id, NULL, :transaction_date, 'sales_return',
                :debit_amount, 0.00, :debit_amount, 'return', :return_id,
                :voucher, :narration, :created_at, NULL)
    """), {
        'tenant_id': tenant_id,
        'transaction_date': ret.return_date,
        'debit_amount': float(ret.taxable_amount),
        'return_id': ret.id,
        'voucher': ret.return_number,
        'narration': f'Sales return from {ret.customer_name} - {ret.return_number}',
        'created_at': now
    })
    
    # Entry 2: DEBIT CGST/SGST/IGST Receivable
    if ret.cgst_amount and ret.cgst_amount > 0:
        db.session.execute(text("""
            INSERT INTO account_transactions
            (tenant_id, account_id, transaction_date, transaction_type,
             debit_amount, credit_amount, balance_after, reference_type, reference_id,
             voucher_number, narration, created_at, created_by)
            VALUES (:tenant_id, NULL, :transaction_date, 'gst_return_cgst',
                    :debit_amount, 0.00, :debit_amount, 'return', :return_id,
                    :voucher, :narration, :created_at, NULL)
        """), {
            'tenant_id': tenant_id,
            'transaction_date': ret.return_date,
            'debit_amount': float(ret.cgst_amount),
            'return_id': ret.id,
            'voucher': ret.return_number,
            'narration': f'CGST reversal on return {ret.return_number}',
            'created_at': now
        })
        
        db.session.execute(text("""
            INSERT INTO account_transactions
            (tenant_id, account_id, transaction_date, transaction_type,
             debit_amount, credit_amount, balance_after, reference_type, reference_id,
             voucher_number, narration, created_at, created_by)
            VALUES (:tenant_id, NULL, :transaction_date, 'gst_return_sgst',
                    :debit_amount, 0.00, :debit_amount, 'return', :return_id,
                    :voucher, :narration, :created_at, NULL)
        """), {
            'tenant_id': tenant_id,
            'transaction_date': ret.return_date,
            'debit_amount': float(ret.sgst_amount),
            'return_id': ret.id,
            'voucher': ret.return_number,
            'narration': f'SGST reversal on return {ret.return_number}',
            'created_at': now
        })
    
    if ret.igst_amount and ret.igst_amount > 0:
        db.session.execute(text("""
            INSERT INTO account_transactions
            (tenant_id, account_id, transaction_date, transaction_type,
             debit_amount, credit_amount, balance_after, reference_type, reference_id,
             voucher_number, narration, created_at, created_by)
            VALUES (:tenant_id, NULL, :transaction_date, 'gst_return_igst',
                    :debit_amount, 0.00, :debit_amount, 'return', :return_id,
                    :voucher, :narration, :created_at, NULL)
        """), {
            'tenant_id': tenant_id,
            'transaction_date': ret.return_date,
            'debit_amount': float(ret.igst_amount),
            'return_id': ret.id,
            'voucher': ret.return_number,
            'narration': f'IGST reversal on return {ret.return_number}',
            'created_at': now
        })
    
    # Entry 3: CREDIT Cash/Bank (money going out)
    new_balance = Decimal(str(account.current_balance)) - ret.total_amount
    
    db.session.execute(text("""
        INSERT INTO account_transactions
        (tenant_id, account_id, transaction_date, transaction_type,
         debit_amount, credit_amount, balance_after, reference_type, reference_id,
         voucher_number, narration, created_at, created_by)
        VALUES (:tenant_id, :account_id, :transaction_date, 'refund_payment',
                0.00, :credit_amount, :balance, 'return', :return_id,
                :voucher, :narration, :created_at, NULL)
    """), {
        'tenant_id': tenant_id,
        'account_id': payment_account_id,
        'transaction_date': ret.return_date,
        'credit_amount': float(ret.total_amount),
        'balance': float(new_balance),
        'return_id': ret.id,
        'voucher': ret.return_number,
        'narration': f'Refund to {ret.customer_name} via {account.account_name}',
        'created_at': now
    })
    
    # Update account balance
    db.session.execute(text("""
        UPDATE bank_accounts 
        SET current_balance = :new_balance, updated_at = :updated_at
        WHERE id = :account_id AND tenant_id = :tenant_id
    """), {
        'new_balance': new_balance,
        'updated_at': now,
        'account_id': payment_account_id,
        'tenant_id': tenant_id
    })
    
    print(f"✅ Refund processed: ₹{ret.total_amount} from {account.account_name}")


def _adjust_unpaid_invoice(ret, tenant_id):
    """Adjust unpaid invoice amounts for returns"""
    invoice = ret.invoice
    if not invoice:
        return
    
    # Reduce invoice amounts
    invoice.subtotal -= float(ret.taxable_amount)
    invoice.cgst_amount -= float(ret.cgst_amount or 0)
    invoice.sgst_amount -= float(ret.sgst_amount or 0)
    invoice.igst_amount -= float(ret.igst_amount or 0)
    invoice.total_amount -= float(ret.total_amount)
    
    # Update balance due if partially paid
    if invoice.payment_status == 'partial':
        invoice.balance_due = invoice.total_amount - invoice.paid_amount
    
    # Adjust Accounts Receivable (reduce customer debt)
    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.now(ist)
    
    db.session.execute(text("""
        INSERT INTO account_transactions
        (tenant_id, account_id, transaction_date, transaction_type,
         debit_amount, credit_amount, balance_after, reference_type, reference_id,
         voucher_number, narration, created_at, created_by)
        VALUES (:tenant_id, NULL, :transaction_date, 'accounts_receivable_adjustment',
                0.00, :credit_amount, :credit_amount, 'return', :return_id,
                :voucher, :narration, :created_at, NULL)
    """), {
        'tenant_id': tenant_id,
        'transaction_date': ret.return_date,
        'credit_amount': float(ret.total_amount),
        'return_id': ret.id,
        'voucher': ret.return_number,
        'narration': f'Reduce receivable for return {ret.return_number}',
        'created_at': now
    })
    
    print(f"✅ Adjusted invoice {invoice.invoice_number}: reduced by ₹{ret.total_amount}")


def _reverse_loyalty_points(ret, tenant_id):
    """Reverse loyalty points earned on returned items"""
    if not ret.invoice_id:
        return
    
    points_to_deduct = ret.calculate_loyalty_points_to_reverse()
    if points_to_deduct <= 0:
        return
    
    # Get customer loyalty record
    loyalty_points = CustomerLoyaltyPoints.query.filter_by(
        customer_id=ret.customer_id,
        tenant_id=tenant_id
    ).first()
    
    if not loyalty_points:
        return  # Customer doesn't have loyalty account
    
    # Deduct points
    loyalty_points.current_points -= points_to_deduct
    
    # Create transaction record
    loyalty_txn = LoyaltyTransaction()
    loyalty_txn.customer_id = ret.customer_id
    loyalty_txn.tenant_id = tenant_id
    loyalty_txn.transaction_type = 'DEDUCTION'
    loyalty_txn.points = -points_to_deduct  # Negative for deduction
    loyalty_txn.reference_type = 'return'
    loyalty_txn.reference_id = ret.id
    loyalty_txn.description = f'Points reversed for return {ret.return_number}'
    loyalty_txn.balance_after = loyalty_points.current_points
    
    db.session.add(loyalty_txn)
    
    print(f"✅ Reversed {points_to_deduct} loyalty points")


@returns_bp.route('/api/search-invoice')
def api_search_invoice():
    """API endpoint to search invoices for return creation"""
    tenant_id = get_current_tenant_id()
    query = request.args.get('q', '').strip()
    
    if not query or len(query) < 2:
        return jsonify([])
    
    # Search invoices
    invoices = Invoice.query.filter(
        Invoice.tenant_id == tenant_id,
        db.or_(
            Invoice.invoice_number.like(f'%{query}%'),
            Invoice.customer_name.like(f'%{query}%'),
            Invoice.customer_phone.like(f'%{query}%')
        )
    ).order_by(Invoice.invoice_date.desc()).limit(20).all()
    
    results = []
    for inv in invoices:
        results.append({
            'id': inv.id,
            'invoice_number': inv.invoice_number,
            'customer_name': inv.customer_name,
            'invoice_date': inv.invoice_date.strftime('%Y-%m-%d'),
            'total_amount': float(inv.total_amount),
            'payment_status': inv.payment_status,
            'items_count': len(inv.items)
        })
    
    return jsonify(results)


@returns_bp.route('/api/invoice/<int:invoice_id>/items')
def api_get_invoice_items(invoice_id):
    """API endpoint to get invoice items for return"""
    tenant_id = get_current_tenant_id()
    invoice = Invoice.query.filter_by(id=invoice_id, tenant_id=tenant_id).first()
    
    if not invoice:
        return jsonify({'error': 'Invoice not found'}), 404
    
    items = []
    for item in invoice.items:
        items.append({
            'id': item.id,
            'item_name': item.item_name,
            'hsn_code': item.hsn_code or '',
            'quantity': float(item.quantity),
            'unit': item.unit,
            'rate': float(item.rate),
            'gst_rate': float(item.gst_rate),
            'total_amount': float(item.total_amount)
        })
    
    return jsonify({
        'invoice_number': invoice.invoice_number,
        'customer_name': invoice.customer_name,
        'invoice_date': invoice.invoice_date.strftime('%Y-%m-%d'),
        'total_amount': float(invoice.total_amount),
        'payment_status': invoice.payment_status,
        'items': items
    })

