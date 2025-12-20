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
                # Safety check: Ensure idx is within bounds for quantities list
                if idx >= len(quantities):
                    print(f"⚠️ Warning: Missing quantity for item_id {item_id} at index {idx}")
                    continue
                
                qty_returned = int(quantities[idx])
                
                # DEBUG: Log item processing
                print(f"Processing item {idx}: ID={item_id}, Qty={qty_returned}")
                
                if qty_returned <= 0:
                    print(f"  ⏭️ Skipping (qty <= 0)")
                    continue
                
                # Get original invoice item
                invoice_item = InvoiceItem.query.get(item_id)
                if not invoice_item:
                    print(f"  ⚠️ Invoice item not found!")
                    continue
                
                print(f"  ✅ Adding return item: {invoice_item.item_name} (qty: {qty_returned})")
                
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
                
                # Calculate amounts proportionally from original invoice to avoid rounding errors
                # This ensures the return amounts match exactly with the original invoice proportions
                qty_sold = Decimal(str(invoice_item.quantity))
                qty_ret = Decimal(str(qty_returned))
                proportion = qty_ret / qty_sold
                
                # Calculate and round each component
                return_item.taxable_amount = (Decimal(str(invoice_item.taxable_value)) * proportion).quantize(Decimal('0.01'))
                return_item.total_amount = (Decimal(str(invoice_item.total_amount)) * proportion).quantize(Decimal('0.01'))
                
                # Calculate total GST from the difference (ensures perfect balance)
                total_gst = return_item.total_amount - return_item.taxable_amount
                
                # Split GST ensuring components sum exactly to total_gst
                if Decimal(str(invoice_item.igst_amount or 0)) > 0:
                    # IGST case
                    return_item.igst_amount = total_gst
                    return_item.cgst_amount = Decimal('0.00')
                    return_item.sgst_amount = Decimal('0.00')
                else:
                    # CGST/SGST case - split evenly but adjust SGST to absorb rounding error
                    half_gst = (total_gst / Decimal('2')).quantize(Decimal('0.01'))
                    return_item.cgst_amount = half_gst
                    return_item.sgst_amount = total_gst - half_gst  # This absorbs any 0.01 rounding difference
                    return_item.igst_amount = Decimal('0.00')
                
                # Add to return
                ret.items.append(return_item)
                
                # Accumulate totals (ensure all are Decimal)
                total_amount += Decimal(str(return_item.total_amount))
                taxable_amount += Decimal(str(return_item.taxable_amount))
                cgst_amount += Decimal(str(return_item.cgst_amount or 0))
                sgst_amount += Decimal(str(return_item.sgst_amount or 0))
                igst_amount += Decimal(str(return_item.igst_amount or 0))
            
            # ============================================================
            # 🔧 CRITICAL FIX: Apply Proportional Round-Off Adjustment
            # ============================================================
            # Calculate what % of the invoice is being returned
            invoice_items_total = Decimal('0')
            for inv_item in invoice.items:
                invoice_items_total += Decimal(str(inv_item.total_amount))
            
            # Calculate proportion of invoice being returned
            return_proportion = total_amount / invoice_items_total if invoice_items_total > 0 else Decimal('0')
            
            # Apply proportional round-off adjustment
            invoice_round_off = Decimal(str(invoice.round_off)) if invoice.round_off else Decimal('0')
            proportional_round_off = (invoice_round_off * return_proportion).quantize(Decimal('0.01'))
            
            # Adjust total amount to include proportional round-off
            adjusted_total = (total_amount + proportional_round_off).quantize(Decimal('0.01'))
            
            print(f'📊 Return Calculation:')
            print(f'  - Items total (before round-off): ₹{total_amount}')
            print(f'  - Invoice round-off: ₹{invoice_round_off}')
            print(f'  - Return proportion: {return_proportion * 100:.2f}%')
            print(f'  - Proportional round-off: ₹{proportional_round_off}')
            print(f'  - Final return total: ₹{adjusted_total}')
            
            # Set return totals
            ret.total_amount = adjusted_total  # Use adjusted total with round-off
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
        
        # STEP 2.5: Reverse loyalty points BEFORE adjusting invoice
        # 🔧 CRITICAL FIX: Must be done BEFORE _adjust_unpaid_invoice!
        # Reason: calculate_loyalty_points_to_reverse() divides by invoice.total_amount
        # If we adjust first, total_amount becomes 0 → ZeroDivisionError!
        _reverse_loyalty_points(ret, tenant_id)
        
        # STEP 2.6: Reverse commission BEFORE adjusting invoice
        # Same reason - commission % calculations need original invoice amounts
        _reverse_commission(ret, tenant_id)
        
        # STEP 3: Adjust invoice for unpaid returns
        if ret.invoice and ret.invoice.payment_status != 'paid':
            _adjust_unpaid_invoice(ret, tenant_id)
        
        # STEP 4: Generate credit note
        ret.generate_credit_note_number()
        
        # STEP 7: Update return status
        ret.status = 'approved'
        ret.approved_at = datetime.now(pytz.timezone('Asia/Kolkata'))
        ret.approved_by = session.get('user_id')
        ret.refund_processed_date = date.today()
        
        if payment_account_id:
            ret.payment_account_id = payment_account_id
        ret.payment_reference = payment_reference
        
        db.session.commit()
        
        # STEP 8: Auto-balance Trial Balance for any rounding differences < ₹1
        from utils.accounting_helpers import auto_balance_trial_balance
        balance_result = auto_balance_trial_balance(tenant_id, ret.return_number, max_diff=Decimal('1.00'))
        if balance_result.get('adjustment_made'):
            print(f"✅ Auto-balanced: {balance_result.get('adjustment_amount')} adjustment made")
        
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


@returns_bp.route('/<int:return_id>/delete', methods=['POST'])
def delete(return_id):
    """Delete return (and reverse accounting if approved)"""
    tenant_id = get_current_tenant_id()
    ret = Return.query.filter_by(id=return_id, tenant_id=tenant_id).first_or_404()
    
    try:
        return_number = ret.return_number
        was_approved = (ret.status == 'approved')
        
        # If return was approved, we need to reverse everything
        if was_approved:
            # Reverse inventory restocking
            for return_item in ret.items:
                if return_item.return_to_inventory and return_item.product_id:
                    item_stock = ItemStock.query.filter_by(
                        item_id=return_item.product_id,
                        tenant_id=tenant_id
                    ).first()
                    
                    if item_stock:
                        # Reduce stock back
                        qty_to_remove = int(return_item.quantity_returned)
                        item_stock.quantity_available -= qty_to_remove
                        
                        # Reduce stock value
                        item = Item.query.get(return_item.product_id)
                        if item and item.cost_price:
                            cost_value = Decimal(str(item.cost_price)) * Decimal(str(return_item.quantity_returned))
                            item_stock.stock_value = Decimal(str(item_stock.stock_value)) - cost_value
            
            # Reverse refund (add money back to account)
            if ret.refund_method in ['cash', 'bank'] and ret.payment_account_id:
                account = BankAccount.query.get(ret.payment_account_id)
                if account:
                    account.current_balance = float(account.current_balance) + float(ret.total_amount)
            
            # Reverse invoice adjustment (add amounts back)
            if ret.invoice and ret.invoice.payment_status != 'paid':
                invoice = ret.invoice
                invoice.subtotal = float(invoice.subtotal) + float(ret.taxable_amount)
                invoice.cgst_amount = float(invoice.cgst_amount or 0) + float(ret.cgst_amount or 0)
                invoice.sgst_amount = float(invoice.sgst_amount or 0) + float(ret.sgst_amount or 0)
                invoice.igst_amount = float(invoice.igst_amount or 0) + float(ret.igst_amount or 0)
                invoice.total_amount = float(invoice.total_amount) + float(ret.total_amount)
                
                if invoice.payment_status == 'partial':
                    invoice.balance_due = invoice.total_amount - invoice.paid_amount
            
            # NOTE: We DO NOT modify invoice_commissions table when deleting returns!
            # The commission_amount in invoice_commissions should always be the ORIGINAL
            # commission on the ORIGINAL invoice. Reversals are tracked separately in
            # account_transactions (which we delete below at line 457-463).
            # This maintains data integrity and allows the ledger to show:
            # - Original earned amount (from invoice_commissions)
            # - Reversals (from account_transactions with type='commission_reversal')
            # - Net commission = earned - reversals
            
            # Reverse loyalty points deduction (add points back)
            if ret.customer_id:
                from models import CustomerLoyaltyPoints
                loyalty_points = CustomerLoyaltyPoints.query.filter_by(
                    customer_id=ret.customer_id,
                    tenant_id=tenant_id
                ).first()
                
                if loyalty_points:
                    # Calculate how many points were deducted
                    points_to_restore = ret.calculate_loyalty_points_to_reverse()
                    if points_to_restore > 0:
                        loyalty_points.current_points += points_to_restore
                        print(f"✅ Restored {points_to_restore} loyalty points to customer")
        
        # Delete all accounting entries related to this return
        from sqlalchemy import text
        db.session.execute(text("""
            DELETE FROM account_transactions
            WHERE tenant_id = :tenant_id
            AND reference_type = 'return'
            AND reference_id = :return_id
        """), {'tenant_id': tenant_id, 'return_id': ret.id})
        
        # Delete loyalty transaction if exists
        from models import LoyaltyTransaction
        if ret.customer_id:
            LoyaltyTransaction.query.filter(
                LoyaltyTransaction.tenant_id == tenant_id,
                LoyaltyTransaction.customer_id == ret.customer_id,
                LoyaltyTransaction.description.like(f'%{ret.return_number}%')
            ).delete(synchronize_session=False)
        
        # Delete stock movements
        from models import ItemStockMovement
        ItemStockMovement.query.filter_by(
            tenant_id=tenant_id,
            reference_type='return',
            reference_id=ret.id
        ).delete()
        
        # Delete the return (cascade will delete return_items)
        db.session.delete(ret)
        db.session.commit()
        
        flash(f'✅ Return {return_number} deleted successfully!', 'success')
        return redirect(url_for('returns.index'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error deleting return: {str(e)}', 'error')
        print(f"Error deleting return: {str(e)}")
        import traceback
        traceback.print_exc()
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
        quantity_to_add = int(return_item.quantity_returned) if isinstance(return_item.quantity_returned, (int, float)) else int(Decimal(str(return_item.quantity_returned)))
        item_stock.quantity_available += quantity_to_add
        
        # Update stock value (add back the cost)
        item = Item.query.get(return_item.product_id)
        if item and item.cost_price:
            cost_value = Decimal(str(item.cost_price)) * Decimal(str(return_item.quantity_returned))
            item_stock.stock_value = Decimal(str(item_stock.stock_value)) + cost_value
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
    
    # Create accounting entries to balance the inventory increase
    # When inventory is restocked, we need BOTH entries:
    # 1. DEBIT Inventory (increases asset)
    # 2. CREDIT COGS (reduces expense/reverses original COGS)
    if total_cost_value > 0:
        ist = pytz.timezone('Asia/Kolkata')
        now = datetime.now(ist)
        
        # Entry 1: DEBIT Inventory (increases asset)
        db.session.execute(text("""
            INSERT INTO account_transactions
            (tenant_id, account_id, transaction_date, transaction_type,
             debit_amount, credit_amount, balance_after, reference_type, reference_id,
             voucher_number, narration, created_at, created_by)
            VALUES (:tenant_id, NULL, :transaction_date, 'inventory_purchase',
                    :debit_amount, 0.00, :debit_amount, 'return', :return_id,
                    :voucher, :narration, :created_at, NULL)
        """), {
            'tenant_id': tenant_id,
            'transaction_date': ret.return_date,
            'debit_amount': float(total_cost_value),
            'return_id': ret.id,
            'voucher': ret.return_number,
            'narration': f'Inventory restocked from return - {ret.return_number}',
            'created_at': now
        })
        
        # Entry 2: CREDIT COGS (reduces expense)
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
        print(f"✅ Created accounting entries: DEBIT Inventory ₹{total_cost_value}, CREDIT COGS ₹{total_cost_value}")
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
    
    # Entry 3: Round-off adjustment (if any)
    # Calculate round-off = total - (taxable + gst)
    gross_before_roundoff = Decimal(str(ret.taxable_amount)) + \
                           Decimal(str(ret.cgst_amount or 0)) + \
                           Decimal(str(ret.sgst_amount or 0)) + \
                           Decimal(str(ret.igst_amount or 0))
    round_off = Decimal(str(ret.total_amount)) - gross_before_roundoff
    
    if round_off != 0:
        # CRITICAL FIX: Handle round-off sign correctly
        # If round_off is NEGATIVE (e.g., -0.10): CREDIT Round-off (reduces total)
        # If round_off is POSITIVE (e.g., +0.10): DEBIT Round-off (increases total)
        if round_off < 0:
            # Negative round-off: CREDIT entry
            db.session.execute(text("""
                INSERT INTO account_transactions
                (tenant_id, account_id, transaction_date, transaction_type,
                 debit_amount, credit_amount, balance_after, reference_type, reference_id,
                 voucher_number, narration, created_at, created_by)
                VALUES (:tenant_id, NULL, :transaction_date, 'round_off_expense',
                        0.00, :credit_amount, 0.00, 'return', :return_id,
                        :voucher, :narration, :created_at, NULL)
            """), {
                'tenant_id': tenant_id,
                'transaction_date': ret.return_date,
                'credit_amount': float(abs(round_off)),
                'return_id': ret.id,
                'voucher': ret.return_number,
                'narration': f'Round-off adjustment (negative) on return {ret.return_number}',
                'created_at': now
            })
            print(f"✅ Created round-off CREDIT entry: ₹{abs(round_off)}")
        else:
            # Positive round-off: DEBIT entry
            db.session.execute(text("""
                INSERT INTO account_transactions
                (tenant_id, account_id, transaction_date, transaction_type,
                 debit_amount, credit_amount, balance_after, reference_type, reference_id,
                 voucher_number, narration, created_at, created_by)
                VALUES (:tenant_id, NULL, :transaction_date, 'round_off_expense',
                        :debit_amount, 0.00, :debit_amount, 'return', :return_id,
                        :voucher, :narration, :created_at, NULL)
            """), {
                'tenant_id': tenant_id,
                'transaction_date': ret.return_date,
                'debit_amount': float(round_off),
                'return_id': ret.id,
                'voucher': ret.return_number,
                'narration': f'Round-off adjustment (positive) on return {ret.return_number}',
                'created_at': now
            })
            print(f"✅ Created round-off DEBIT entry: ₹{round_off}")
    
    # Entry 4: CREDIT Cash/Bank (money going out)
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
    
    # Reduce invoice amounts (ensure type consistency)
    invoice.subtotal = float(invoice.subtotal) - float(ret.taxable_amount)
    invoice.cgst_amount = float(invoice.cgst_amount or 0) - float(ret.cgst_amount or 0)
    invoice.sgst_amount = float(invoice.sgst_amount or 0) - float(ret.sgst_amount or 0)
    invoice.igst_amount = float(invoice.igst_amount or 0) - float(ret.igst_amount or 0)
    invoice.total_amount = float(invoice.total_amount) - float(ret.total_amount)
    
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
    loyalty_txn.invoice_id = ret.invoice_id  # Link to original invoice
    loyalty_txn.description = f'Points reversed for return {ret.return_number}'
    loyalty_txn.balance_after = loyalty_points.current_points
    
    db.session.add(loyalty_txn)
    
    print(f"✅ Reversed {points_to_deduct} loyalty points")


def _reverse_commission(ret, tenant_id):
    """Reverse commission for agents on returned items"""
    if not ret.invoice_id:
        return
    
    from models import InvoiceCommission
    from sqlalchemy import text
    
    # Find all commission entries for this invoice
    commissions = InvoiceCommission.query.filter_by(
        invoice_id=ret.invoice_id,
        tenant_id=tenant_id
    ).all()
    
    if not commissions:
        return  # No commission to reverse
    
    # Calculate commission on return amount
    for commission in commissions:
        from utils.accounting_helpers import calculate_commission
        
        # Calculate commission on the return amount using precise helper
        # Commission % is same as original invoice
        # IMPORTANT: Using ret.total_amount (the final return total including GST)
        print(f"🔍 DEBUG: Calculating commission reversal - Return total: ₹{ret.total_amount}, Percentage: {commission.commission_percentage}%")
        commission_on_return = calculate_commission(ret.total_amount, commission.commission_percentage)
        print(f"🔍 DEBUG: Commission reversal amount: ₹{commission_on_return}")
        
        # IMPORTANT: DON'T update the commission record!
        # We keep the original amounts in invoice_commissions table
        # and create commission_reversal entries to track adjustments
        # This way the ledger shows original earned amount + reversals separately
        
        # ALWAYS create commission reversal accounting entries (whether paid or not)
        # DOUBLE-ENTRY: Commission was overpaid, agent owes us money back
        import pytz
        ist = pytz.timezone('Asia/Kolkata')
        now = datetime.now(ist)
        
        # Entry 1: DEBIT Commission Recoverable (Asset - agent owes us)
        db.session.execute(text("""
            INSERT INTO account_transactions
            (tenant_id, account_id, transaction_date, transaction_type,
             debit_amount, credit_amount, balance_after, reference_type, reference_id,
             voucher_number, narration, created_at, created_by)
            VALUES (:tenant_id, NULL, :transaction_date, 'commission_recoverable',
                    :debit_amount, 0.00, :debit_amount, 'return', :return_id,
                    :voucher, :narration, :created_at, NULL)
        """), {
            'tenant_id': tenant_id,
            'transaction_date': ret.return_date,
            'debit_amount': float(commission_on_return),
            'return_id': ret.id,
            'voucher': ret.return_number,
            'narration': f'Commission recoverable from {commission.agent_name} - Return {ret.return_number}',
            'created_at': now
        })
        
        # Entry 2: CREDIT Commission Expense (reduce expense)
        db.session.execute(text("""
            INSERT INTO account_transactions
            (tenant_id, account_id, transaction_date, transaction_type,
             debit_amount, credit_amount, balance_after, reference_type, reference_id,
             voucher_number, narration, created_at, created_by)
            VALUES (:tenant_id, NULL, :transaction_date, 'commission_reversal',
                    0.00, :credit_amount, 0.00, 'return', :return_id,
                    :voucher, :narration, :created_at, NULL)
        """), {
            'tenant_id': tenant_id,
            'transaction_date': ret.return_date,
            'credit_amount': float(commission_on_return),
            'return_id': ret.id,
            'voucher': ret.return_number,
            'narration': f'Commission reversal for {commission.agent_name} - Return {ret.return_number} (Original Invoice: {ret.invoice.invoice_number})',
            'created_at': now
        })
        
        print(f"✅ Reversed commission: {commission.agent_name} - ₹{commission_on_return:.2f} (DEBIT Recoverable, CREDIT Expense)")


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
    from sqlalchemy import text
    from decimal import Decimal
    
    tenant_id = get_current_tenant_id()
    invoice = Invoice.query.filter_by(id=invoice_id, tenant_id=tenant_id).first()
    
    if not invoice:
        return jsonify({'error': 'Invoice not found'}), 404
    
    # Get all returned quantities for this invoice from APPROVED returns only
    returned_quantities_result = db.session.execute(text("""
        SELECT 
            ri.invoice_item_id,
            SUM(ri.quantity_returned) as total_returned
        FROM return_items ri
        JOIN returns r ON ri.return_id = r.id
        WHERE r.invoice_id = :invoice_id
        AND r.tenant_id = :tenant_id
        AND r.status = 'approved'
        GROUP BY ri.invoice_item_id
    """), {'invoice_id': invoice_id, 'tenant_id': tenant_id}).fetchall()
    
    # Create a dict for easy lookup: {invoice_item_id: total_returned}
    returned_quantities = {row[0]: float(row[1]) for row in returned_quantities_result}
    
    items = []
    for item in invoice.items:
        qty_sold = float(item.quantity)
        qty_already_returned = returned_quantities.get(item.id, 0.0)
        qty_available_for_return = qty_sold - qty_already_returned
        
        items.append({
            'id': item.id,
            'item_name': item.item_name,
            'hsn_code': item.hsn_code or '',
            'quantity': qty_sold,  # Original quantity sold
            'quantity_already_returned': qty_already_returned,  # Already returned
            'quantity_available': qty_available_for_return,  # Remaining returnable
            'unit': item.unit,
            'rate': float(item.rate),  # ORIGINAL invoice rate (not current item price!)
            'gst_rate': float(item.gst_rate),
            'total_amount': float(item.total_amount),  # ORIGINAL invoice amount
            'is_fully_returned': (qty_available_for_return <= 0)
        })
    
    return jsonify({
        'invoice_number': invoice.invoice_number,
        'customer_name': invoice.customer_name,
        'invoice_date': invoice.invoice_date.strftime('%Y-%m-%d'),
        'total_amount': float(invoice.total_amount),
        'round_off': float(invoice.round_off) if invoice.round_off else 0.0,  # CRITICAL: Send round-off to frontend
        'payment_status': invoice.payment_status,
        'items': items
    })

