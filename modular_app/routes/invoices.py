"""
Invoice management routes
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, g, session
from models import db, Invoice, InvoiceItem, Item, ItemStock, ItemStockMovement, Site, Tenant
from utils.tenant_middleware import require_tenant, get_current_tenant_id
from utils.license_check import check_license
from sqlalchemy import func, desc, text
from datetime import datetime, date
from decimal import Decimal
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

@invoices_bp.route('/', strict_slashes=False)  # PERFORMANCE: Prevent 308 redirects
@require_tenant
@login_required
def index():
    """List all invoices - OPTIMIZED with pagination"""
    tenant_id = g.tenant.id
    
    # Filters
    status_filter = request.args.get('status', 'all')
    payment_filter = request.args.get('payment', 'all')
    search = request.args.get('search', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 50
    
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
    
    # OPTIMIZED: Paginate invoices (instead of loading ALL)
    query = query.order_by(desc(Invoice.invoice_date), desc(Invoice.id))
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    invoices = pagination.items
    
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
                         page=page,
                         total_pages=pagination.pages,
                         total_items=pagination.total,
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
            
            # Commission data (optional)
            commission_agent_id = request.form.get('commission_agent_id')
            commission_percentage = request.form.get('commission_percentage')
            
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
            
            # Get delivery_challan_id if converting from challan
            delivery_challan_id = request.form.get('delivery_challan_id')
            if delivery_challan_id and delivery_challan_id.strip():
                delivery_challan_id = int(delivery_challan_id)
            else:
                delivery_challan_id = None
            
            invoice = Invoice(
                tenant_id=tenant_id,
                customer_id=customer_id,  # NEW: Link to customer master
                sales_order_id=sales_order_id,  # ✅ RE-ENABLED: Migration completed!
                delivery_challan_id=delivery_challan_id,  # Link to delivery challan if converting
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
            
            # Generate public access token
            invoice.public_token = invoice.generate_public_token()
            
            # Get tenant's state from settings
            tenant_settings = json.loads(g.tenant.settings) if g.tenant.settings else {}
            tenant_state = tenant_settings.get('state', 'Maharashtra')
            # Default customer state to tenant state (most common case - same state transaction)
            is_same_state = (customer_state or tenant_state) == tenant_state
            
            # Process invoice items
            item_names = request.form.getlist('item_name[]')
            item_ids = request.form.getlist('item_id[]')
            descriptions = request.form.getlist('description[]')
            quantities = request.form.getlist('quantity[]')
            units = request.form.getlist('unit[]')
            rates = request.form.getlist('rate[]')
            gst_rates = request.form.getlist('gst_rate[]')
            hsn_codes = request.form.getlist('hsn_code[]')
            
            # Check if GST is enabled on this invoice
            gst_enabled = request.form.get('gst_enabled') == '1'
            
            subtotal = 0
            total_cgst = 0
            total_sgst = 0
            total_igst = 0
            
            for i in range(len(item_names)):
                if not item_names[i] or not quantities[i] or not rates[i]:
                    continue
                
                item_id = int(item_ids[i]) if item_ids[i] and item_ids[i] != '' else None
                quantity = float(quantities[i])
                selling_price = float(rates[i])  # This is GST-inclusive selling price from inventory
                gst_rate = float(gst_rates[i]) if gst_rates[i] else 18
                
                # NEW LOGIC: Prices from inventory are ALWAYS GST-inclusive (MRP-based)
                # Calculate based on GST toggle
                if gst_enabled:
                    # GST ON: Reverse-calculate base price from GST-inclusive selling price
                    total_amount = quantity * selling_price  # Total is selling price × qty
                    divisor = 1 + (gst_rate / 100)
                    taxable_value = total_amount / divisor  # Reverse calculate base price
                    gst_amount = total_amount - taxable_value  # GST amount
                else:
                    # GST OFF: Use selling price directly, no GST calculation
                    total_amount = quantity * selling_price
                    taxable_value = total_amount  # Same as total when GST is off
                    gst_amount = 0  # No GST
                
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
                        # Get default site (marked as is_default=True)
                        default_site = Site.query.filter_by(
                            tenant_id=tenant_id,
                            is_default=True,
                            active=True
                        ).first()
                        
                        # Fallback to first active site if no default is set
                        if not default_site:
                            default_site = Site.query.filter_by(tenant_id=tenant_id, active=True).first()
                        
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
                                    # Show warning to user
                                    flash(f'⚠️ Warning: {item_obj.name} has insufficient stock! Available: {item_stock.quantity_available:.2f}, Selling: {quantity}. Stock will go negative.', 'warning')
                                    print(f"⚠️  WARNING: Insufficient stock for {item_obj.name}! Available: {item_stock.quantity_available}, Requested: {quantity}")
                                
                                # Reduce stock (allow negative but warn user)
                                old_qty = item_stock.quantity_available
                                item_stock.quantity_available -= quantity
                                new_qty = item_stock.quantity_available
                                
                                # Alert if stock went negative
                                if new_qty < 0:
                                    flash(f'🚨 {item_obj.name} is now OUT OF STOCK (Qty: {new_qty:.2f}). Please reorder!', 'danger')
                                
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
            
            # Get loyalty discount (separate from manual discount)
            loyalty_discount = float(request.form.get('loyalty_discount', 0) or 0)
            loyalty_points_redeemed = int(request.form.get('loyalty_points_redeemed', 0) or 0)
            
            # Calculate invoice totals
            invoice.subtotal = subtotal
            invoice.discount_amount = discount
            invoice.loyalty_discount = loyalty_discount  # NEW: Loyalty discount
            invoice.loyalty_points_redeemed = loyalty_points_redeemed  # NEW: Points redeemed
            invoice.cgst_amount = total_cgst
            invoice.sgst_amount = total_sgst
            invoice.igst_amount = total_igst
            invoice.gst_enabled = gst_enabled  # Save GST toggle state
            
            # Round off to nearest rupee (including loyalty discount)
            total_before_rounding = subtotal + total_cgst + total_sgst + total_igst - loyalty_discount
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
            db.session.flush()  # Get invoice ID before commit
            
            # ═══════════════════════════════════════════════════════════════════
            # 📊 DOUBLE-ENTRY ACCOUNTING: Sales Invoice Created
            # ═══════════════════════════════════════════════════════════════════
            # When an invoice is created (even if unpaid), we need to record:
            # 1. DEBIT:  Accounts Receivable OR Cash (Asset) - Money owed/received
            # 2. CREDIT: Sales Income (Income) - Revenue earned
            # 3. DEBIT:  Cost of Goods Sold (Expense) - Cost of items sold
            # 4. CREDIT: Inventory (Asset) - Stock reduction
            # ═══════════════════════════════════════════════════════════════════
            
            ist = pytz.timezone('Asia/Kolkata')
            now = datetime.now(ist)
            
            # STEP 1: Calculate COGS (Cost of Goods Sold)
            # Get the cost price of each item sold
            cogs_total = Decimal('0')
            
            for invoice_item in invoice.items:
                if invoice_item.item_id:  # Only for linked inventory items
                    item = Item.query.filter_by(
                        id=invoice_item.item_id,
                        tenant_id=tenant_id
                    ).first()
                    
                    if item and item.cost_price:
                        item_cogs = Decimal(str(item.cost_price)) * Decimal(str(invoice_item.quantity))
                        cogs_total += item_cogs
                        print(f"  📦 {item.name}: Qty {invoice_item.quantity} × Cost ₹{item.cost_price} = COGS ₹{item_cogs:,.2f}")
            
            print(f"\n💰 Invoice {invoice.invoice_number} - Total COGS: ₹{cogs_total:,.2f}")
            print(f"💰 Invoice {invoice.invoice_number} - Sales: ₹{invoice.total_amount:,.2f}")
            print(f"💰 Invoice {invoice.invoice_number} - Gross Profit: ₹{invoice.total_amount - float(cogs_total):,.2f}")
            
            # STEP 2: Create Double-Entry Accounting Transactions
            
            # Entry 1: DEBIT Accounts Receivable (if credit sale) OR Cash (if paid)
            if payment_received == 'yes':
                # Cash sale - will be handled below in the existing payment logic
                # We'll update that section to use proper double-entry
                pass
            else:
                # Credit sale - create receivable
                db.session.execute(text("""
                    INSERT INTO account_transactions
                    (tenant_id, account_id, transaction_date, transaction_type,
                     debit_amount, credit_amount, balance_after, reference_type, reference_id,
                     voucher_number, narration, created_at, created_by)
                    VALUES (:tenant_id, NULL, :transaction_date, 'accounts_receivable',
                            :debit_amount, 0.00, :debit_amount, 'invoice', :invoice_id,
                            :voucher, :narration, :created_at, NULL)
                """), {
                    'tenant_id': tenant_id,
                    'transaction_date': invoice_date,
                    'debit_amount': float(invoice.total_amount),
                    'invoice_id': invoice.id,
                    'voucher': invoice.invoice_number,
                    'narration': f'Credit sale to {invoice.customer_name} - {invoice.invoice_number}',
                    'created_at': now
                })
                print(f"   DEBIT:  Accounts Receivable  ₹{invoice.total_amount:,.2f}")
            
            # Entry 2: CREDIT Sales Income (for all sales - SUBTOTAL ONLY, NOT including GST!)
            db.session.execute(text("""
                INSERT INTO account_transactions
                (tenant_id, account_id, transaction_date, transaction_type,
                 debit_amount, credit_amount, balance_after, reference_type, reference_id,
                 voucher_number, narration, created_at, created_by)
                VALUES (:tenant_id, NULL, :transaction_date, 'sales_income',
                        0.00, :credit_amount, :credit_amount, 'invoice', :invoice_id,
                        :voucher, :narration, :created_at, NULL)
            """), {
                'tenant_id': tenant_id,
                'transaction_date': invoice_date,
                'credit_amount': float(invoice.subtotal),  # ✅ FIX: Use subtotal, not total!
                'invoice_id': invoice.id,
                'voucher': invoice.invoice_number,
                'narration': f'Sales income from {invoice.customer_name} - {invoice.invoice_number}',
                'created_at': now
            })
            print(f"   CREDIT: Sales Income         ₹{invoice.subtotal:,.2f}")
            
            # Entry 2.5: CREDIT GST Payable (CGST + SGST or IGST)
            total_gst = (invoice.cgst_amount or 0) + (invoice.sgst_amount or 0) + (invoice.igst_amount or 0)
            if total_gst > 0:
                db.session.execute(text("""
                    INSERT INTO account_transactions
                    (tenant_id, account_id, transaction_date, transaction_type,
                     debit_amount, credit_amount, balance_after, reference_type, reference_id,
                     voucher_number, narration, created_at, created_by)
                    VALUES (:tenant_id, NULL, :transaction_date, 'gst_payable',
                            0.00, :credit_amount, :credit_amount, 'invoice', :invoice_id,
                            :voucher, :narration, :created_at, NULL)
                """), {
                    'tenant_id': tenant_id,
                    'transaction_date': invoice_date,
                    'credit_amount': float(total_gst),
                    'invoice_id': invoice.id,
                    'voucher': invoice.invoice_number,
                    'narration': f'GST payable on {invoice.invoice_number}',
                    'created_at': now
                })
                print(f"   CREDIT: GST Payable          ₹{total_gst:,.2f}")
            
            # Entry 3: DEBIT Cost of Goods Sold (COGS)
            if cogs_total > 0:
                db.session.execute(text("""
                    INSERT INTO account_transactions
                    (tenant_id, account_id, transaction_date, transaction_type,
                     debit_amount, credit_amount, balance_after, reference_type, reference_id,
                     voucher_number, narration, created_at, created_by)
                    VALUES (:tenant_id, NULL, :transaction_date, 'cogs',
                            :debit_amount, 0.00, :debit_amount, 'invoice', :invoice_id,
                            :voucher, :narration, :created_at, NULL)
                """), {
                    'tenant_id': tenant_id,
                    'transaction_date': invoice_date,
                    'debit_amount': float(cogs_total),
                    'invoice_id': invoice.id,
                    'voucher': invoice.invoice_number,
                    'narration': f'COGS for {invoice.invoice_number}',
                    'created_at': now
                })
                print(f"   DEBIT:  COGS                 ₹{cogs_total:,.2f}")
                
                # Entry 4: CREDIT Inventory (reduce asset)
                db.session.execute(text("""
                    INSERT INTO account_transactions
                    (tenant_id, account_id, transaction_date, transaction_type,
                     debit_amount, credit_amount, balance_after, reference_type, reference_id,
                     voucher_number, narration, created_at, created_by)
                    VALUES (:tenant_id, NULL, :transaction_date, 'inventory_sale',
                            0.00, :credit_amount, 0.00, 'invoice', :invoice_id,
                            :voucher, :narration, :created_at, NULL)
                """), {
                    'tenant_id': tenant_id,
                    'transaction_date': invoice_date,
                    'credit_amount': float(cogs_total),
                    'invoice_id': invoice.id,
                    'voucher': invoice.invoice_number,
                    'narration': f'Inventory reduction for {invoice.invoice_number}',
                    'created_at': now
                })
                print(f"   CREDIT: Inventory            ₹{cogs_total:,.2f}\n")
            
            print(f"✅ Double-entry accounting created for invoice {invoice.invoice_number}")
            
            # STEP 3: Handle Cash/Bank Transaction (if payment received immediately)
            if payment_received == 'yes':
                from models import BankAccount
                
                account_id = request.form.get('payment_account_id')
                
                if account_id:
                    account = BankAccount.query.filter_by(
                        id=account_id,
                        tenant_id=tenant_id,
                        is_active=True
                    ).first()
                    
                    if account:
                        # For cash sales: DEBIT Cash/Bank (money received)
                        # Note: CREDIT Sales Income was already created above
                        amount = Decimal(str(invoice.total_amount))
                        new_balance = Decimal(str(account.current_balance)) + amount
                        
                        db.session.execute(text("""
                            INSERT INTO account_transactions
                            (tenant_id, account_id, transaction_date, transaction_type,
                             debit_amount, credit_amount, balance_after, reference_type, reference_id,
                             voucher_number, narration, created_at, created_by)
                            VALUES (:tenant_id, :account_id, :txn_date, 'invoice_payment',
                                    :debit, 0.00, :balance, 'invoice', :ref_id,
                                    :voucher, :narration, :created_at, NULL)
                        """), {
                            'tenant_id': tenant_id,
                            'account_id': account_id,
                            'txn_date': invoice_date,
                            'debit': float(amount),  # Money received = Debit
                            'balance': float(new_balance),
                            'ref_id': invoice.id,
                            'voucher': invoice.invoice_number,
                            'narration': f'Cash sale - {invoice.invoice_number} from {invoice.customer_name}',
                            'created_at': now
                        })
                        
                        # Update account balance
                        db.session.execute(text("""
                            UPDATE bank_accounts 
                            SET current_balance = :new_balance, updated_at = :updated_at
                            WHERE id = :account_id AND tenant_id = :tenant_id
                        """), {
                            'new_balance': float(new_balance),
                            'updated_at': now,
                            'account_id': account_id,
                            'tenant_id': tenant_id
                        })
                        
                        print(f"   DEBIT:  {account.account_name}  ₹{amount:,.2f} (Cash sale)")
            
            db.session.commit()
            
            # Process Loyalty Program (if enabled and customer linked)
            if customer_id and customer_id > 0:
                try:
                    from services.loyalty_service import LoyaltyService
                    
                    # Get loyalty settings
                    loyalty_settings = LoyaltyService.get_loyalty_program(tenant_id)
                    
                    if loyalty_settings and loyalty_settings.is_active:
                        # Process redemption if points were redeemed
                        if loyalty_points_redeemed > 0:
                            LoyaltyService.redeem_points(
                                customer_id=customer_id,
                                tenant_id=tenant_id,
                                points=loyalty_points_redeemed,
                                invoice_id=invoice.id,
                                invoice_number=invoice.invoice_number,
                                description=f'Points redeemed for invoice {invoice.invoice_number}',
                                invoice_subtotal=subtotal,
                                created_by=None
                            )
                            print(f"🎁 Loyalty: Redeemed {loyalty_points_redeemed} pts (₹{loyalty_discount}) for customer #{customer_id}")
                        
                        # Calculate and credit earned points (using final invoice total)
                        points_result = LoyaltyService.calculate_points_earned(
                            invoice.total_amount,
                            tenant_id
                        )
                        
                        points_earned = points_result['total_points'] if isinstance(points_result, dict) else points_result
                        
                        if points_earned > 0:
                            # Credit points using the service method (creates proper transaction record)
                            LoyaltyService.credit_points(
                                customer_id=customer_id,
                                tenant_id=tenant_id,
                                points=points_earned,
                                invoice_id=invoice.id,
                                invoice_number=invoice.invoice_number,
                                description=f'Points earned from invoice {invoice.invoice_number}',
                                base_points=points_result.get('base_points', points_earned),
                                bonus_points=points_result.get('bonus_points', 0),
                                invoice_amount=float(invoice.total_amount),
                                created_by=None  # tenant_admin_id is not a user_id
                            )
                            
                            # Update invoice with earned points
                            invoice.loyalty_points_earned = points_earned
                            db.session.commit()
                            print(f"🎁 Loyalty: Earned {points_earned} pts for customer #{customer_id} (₹{invoice.total_amount} invoice)")
                except Exception as e:
                    print(f"⚠️ Error processing loyalty: {str(e)}")
                    # Don't fail invoice creation if loyalty fails
                    import traceback
                    traceback.print_exc()
            
            # Save Commission Data (if agent selected)
            if commission_agent_id and commission_agent_id.strip() and commission_percentage:
                try:
                    from models import CommissionAgent, InvoiceCommission
                    from utils.accounting_helpers import calculate_commission, round_currency
                    
                    agent_id = int(commission_agent_id)
                    agent = CommissionAgent.query.get(agent_id)
                    
                    if agent and agent.tenant_id == tenant_id:
                        comm_percentage = Decimal(str(commission_percentage))
                        # Use helper function for precise commission calculation
                        commission_amount = calculate_commission(invoice.total_amount, comm_percentage)
                        
                        commission_record = InvoiceCommission(
                            tenant_id=tenant_id,
                            invoice_id=invoice.id,
                            agent_id=agent.id,
                            agent_name=agent.name,  # Denormalized
                            agent_code=agent.code,  # Denormalized
                            commission_percentage=float(comm_percentage),
                            invoice_amount=float(invoice.total_amount),
                            commission_amount=float(commission_amount),  # Store as float but calculated precisely
                            is_paid=False
                        )
                        
                        db.session.add(commission_record)
                        db.session.commit()
                        print(f"💰 Commission saved: {agent.name} will earn ₹{commission_amount} ({comm_percentage}% of ₹{invoice.total_amount})")
                except Exception as e:
                    print(f"⚠️ Error saving commission: {str(e)}")
                    # Don't fail invoice creation if commission save fails
            
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
                from models import SalesOrder, SalesOrderItem
                sales_order = SalesOrder.query.get(sales_order_id)
                if sales_order:
                    # 🔥 UPDATE SALES ORDER ITEMS WITH INVOICED QUANTITIES
                    for invoice_item in invoice.items:
                        # Find matching sales order item by item_id
                        if invoice_item.item_id:
                            so_item = SalesOrderItem.query.filter_by(
                                sales_order_id=sales_order_id,
                                item_id=invoice_item.item_id
                            ).first()
                            
                            if so_item:
                                # Increment quantity_invoiced (convert to Decimal to avoid type error)
                                so_item.quantity_invoiced += Decimal(str(invoice_item.quantity))
                                print(f"📋 Updated SO item {so_item.item_name}: invoiced {so_item.quantity_invoiced}/{so_item.quantity}")
                    
                    # Update fulfillment tracking
                    sales_order.update_fulfillment_status()
                    flash(f'✅ Invoice created successfully! Linked to Sales Order {sales_order.order_number}', 'success')
                else:
                    flash('Invoice created successfully! Stock updated.', 'success')
            else:
                flash('Invoice created successfully! Stock updated.', 'success')
            
            # Update delivery challan status if linked
            if delivery_challan_id:
                from models import DeliveryChallan
                delivery_challan = DeliveryChallan.query.get(delivery_challan_id)
                if delivery_challan:
                    # Update DC status to invoiced
                    delivery_challan.status = 'invoiced'
                    delivery_challan.invoiced_at = datetime.now(pytz.timezone('Asia/Kolkata'))
                    flash(f'✅ Invoice created successfully! Linked to Delivery Challan {delivery_challan.challan_number}', 'success')
                    print(f"📦 Delivery Challan {delivery_challan.challan_number} marked as invoiced")
            
            db.session.commit()
            
            return redirect(url_for('invoices.view', invoice_id=invoice.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating invoice: {str(e)}', 'error')
    
    # GET request - show form
    # PERFORMANCE OPTIMIZATION: Items are now loaded via API (/items/api/search)
    # This allows fast page load even with 20K+ items
    items_json = []  # Empty array - items loaded dynamically via API
    
    # Check if converting from sales order
    from_order = request.args.get('from_order')
    sales_order = None
    if from_order:
        from models import SalesOrder
        sales_order = SalesOrder.query.filter_by(
            id=int(from_order), 
            tenant_id=tenant_id
        ).first()
    
    # Check if converting from delivery challan
    from_challan = request.args.get('from_challan')
    delivery_challan = None
    if from_challan:
        from models import DeliveryChallan
        delivery_challan = DeliveryChallan.query.filter_by(
            id=int(from_challan),
            tenant_id=tenant_id
        ).first()
    
    # Get tenant settings
    tenant_settings = json.loads(g.tenant.settings) if g.tenant.settings else {}
    
    # Fetch commission agents (for commission dropdown)
    from models import CommissionAgent
    commission_agents_employee = CommissionAgent.query.filter_by(
        tenant_id=tenant_id,
        agent_type='employee',
        is_active=True
    ).all()
    
    commission_agents_external = CommissionAgent.query.filter_by(
        tenant_id=tenant_id,
        agent_type='external',
        is_active=True
    ).all()
    
    # Get active bank/cash accounts for payment recording
    from models import BankAccount
    bank_accounts = BankAccount.query.filter_by(
        tenant_id=tenant_id,
        is_active=True
    ).order_by(
        BankAccount.account_type,
        BankAccount.account_name
    ).all()
    
    return render_template('admin/invoices/create.html',
                         tenant=g.tenant,
                         items=items_json,
                         today=date.today().strftime('%Y-%m-%d'),
                         tenant_settings=tenant_settings,
                         sales_order=sales_order,
                         delivery_challan=delivery_challan,
                         commission_agents_employee=commission_agents_employee,
                         commission_agents_external=commission_agents_external,
                         bank_accounts=bank_accounts)


@invoices_bp.route('/<int:invoice_id>')
@require_tenant
@login_required
def view(invoice_id):
    """View invoice details"""
    tenant_id = g.tenant.id
    invoice = Invoice.query.filter_by(id=invoice_id, tenant_id=tenant_id).first_or_404()
    
    # Get tenant settings for invoice header
    tenant_settings = json.loads(g.tenant.settings) if g.tenant.settings else {}
    
    # Get active bank/cash accounts for payment recording
    from models import BankAccount
    bank_accounts = BankAccount.query.filter_by(
        tenant_id=tenant_id,
        is_active=True
    ).order_by(
        BankAccount.account_type,
        BankAccount.account_name
    ).all()
    
    # Check for loyalty footer note (same logic as public invoice for consistency)
    loyalty_footer_note = None
    try:
        if invoice.loyalty_points_earned and invoice.loyalty_points_earned > 0:
            loyalty_footer_note = f"🎉 You earned {invoice.loyalty_points_earned} loyalty points on this purchase!"
    except Exception as e:
        print(f"⚠️ Error fetching loyalty footer: {str(e)}")
        loyalty_footer_note = None
    
    return render_template('admin/invoices/view.html',
                         tenant=g.tenant,
                         invoice=invoice,
                         tenant_settings=tenant_settings,
                         bank_accounts=bank_accounts,
                         loyalty_footer_note=loyalty_footer_note,
                         today=date.today())


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
            # Default customer state to tenant state (most common case - same state transaction)
            is_same_state = (invoice.customer_state or tenant_state) == tenant_state
            
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
        # PERFORMANCE OPTIMIZATION: Items loaded via API for fast page load
        items_json = []  # Empty array - items loaded dynamically via /items/api/search
        
        # Convert invoice items to JSON-serializable format
        invoice_items_json = []
        for item in invoice.items:
            # Safely get MRP and discount from item master
            mrp = 0
            discount_percent = 0
            try:
                if item.item:
                    mrp = float(item.item.mrp) if item.item.mrp else 0
                    discount_percent = float(item.item.discount_percent) if item.item.discount_percent else 0
            except Exception as e:
                print(f"⚠️ Could not fetch MRP/discount for item {item.id}: {e}")
            
            invoice_items_json.append({
                'id': item.id,
                'item_id': item.item_id,
                'item_name': item.item_name,
                'description': item.description or '',
                'hsn_code': item.hsn_code or '',
                'quantity': float(item.quantity),
                'unit': item.unit or 'Nos',
                'rate': float(item.rate),
                'gst_rate': float(item.gst_rate),
                'taxable_value': float(item.taxable_value),
                'cgst_amount': float(item.cgst_amount),
                'sgst_amount': float(item.sgst_amount),
                'igst_amount': float(item.igst_amount),
                'total_amount': float(item.total_amount),
                'mrp': mrp,
                'discount_percent': discount_percent
            })
        
        # Create a serializable invoice object (without 'items' key to avoid dict.items() conflict)
        invoice_dict = {
            'id': invoice.id,
            'invoice_number': invoice.invoice_number,
            'invoice_date': invoice.invoice_date.strftime('%Y-%m-%d'),
            'due_date': invoice.due_date.strftime('%Y-%m-%d') if invoice.due_date else '',
            'customer_id': invoice.customer_id,
            'customer_name': invoice.customer_name,
            'customer_phone': invoice.customer_phone or '',
            'customer_email': invoice.customer_email or '',
            'customer_address': invoice.customer_address or '',
            'customer_gstin': invoice.customer_gstin or '',
            'customer_state': invoice.customer_state or 'Maharashtra',
            'subtotal': float(invoice.subtotal),
            'discount_amount': float(invoice.discount_amount),
            'cgst_amount': float(invoice.cgst_amount),
            'sgst_amount': float(invoice.sgst_amount),
            'igst_amount': float(invoice.igst_amount),
            'total_amount': float(invoice.total_amount),
            'round_off': float(invoice.round_off),
            'payment_status': invoice.payment_status,
            'status': invoice.status,
            'notes': invoice.notes or ''
        }
        
        tenant_settings = json.loads(g.tenant.settings) if g.tenant.settings else {}
        
        flash('Edit mode: Modify invoice details below', 'info')
        return render_template('admin/invoices/create.html',
                             tenant=g.tenant,
                             invoice=invoice_dict,  # Pass serializable dict (without 'items' key)
                             invoice_items=invoice_items_json,  # Pass items separately to avoid dict.items() conflict
                             items=items_json,  # Available items for autocomplete
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
        
        # Get default site (marked as is_default=True)
        from models.site import Site
        default_site = Site.query.filter_by(
            tenant_id=tenant_id,
            is_default=True,
            active=True
        ).first()
        
        # Fallback to first active site if no default is set
        if not default_site:
            default_site = Site.query.filter_by(tenant_id=tenant_id, active=True).first()
        
        if not default_site:
            flash('❌ No active site found! Please create a site first.', 'error')
            return redirect(url_for('invoices.view', invoice_id=invoice_id))
        
        # Reduce stock for items from default site
        for item in invoice.items:
            if item.item_id:
                stock = ItemStock.query.filter_by(
                    tenant_id=tenant_id,
                    item_id=item.item_id,
                    site_id=default_site.id  # FIXED: Use default site instead of .first()
                ).first()
                
                if stock:
                    old_qty = stock.quantity_available
                    stock.quantity_available -= item.quantity
                    new_qty = stock.quantity_available
                    
                    # Warn if stock goes negative
                    if new_qty < 0:
                        flash(f'⚠️ Warning: {item.item_name} is now OUT OF STOCK at {default_site.name} (Qty: {new_qty:.2f})', 'warning')
                else:
                    flash(f'⚠️ Warning: No stock record found for {item.item_name} at {default_site.name}', 'warning')
        
        db.session.commit()
        flash(f'✅ Invoice marked as sent! Stock deducted from: {default_site.name}', 'success')
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
        from decimal import Decimal
        from datetime import datetime
        import pytz
        from sqlalchemy import text
        from models import BankAccount
        
        amount = Decimal(str(request.form.get('amount_paid', 0)))
        payment_method = request.form.get('payment_method', 'Cash')
        account_id = request.form.get('account_id')  # NEW: Bank/Cash account
        
        # Validate account
        if not account_id:
            flash('⚠️ Please select a bank/cash account', 'warning')
            return redirect(url_for('invoices.view', invoice_id=invoice_id))
        
        account = BankAccount.query.filter_by(
            id=account_id, 
            tenant_id=tenant_id, 
            is_active=True
        ).first()
        
        if not account:
            flash('⚠️ Invalid bank/cash account selected', 'error')
            return redirect(url_for('invoices.view', invoice_id=invoice_id))
        
        # Update invoice paid amount
        invoice.paid_amount = (invoice.paid_amount or 0) + float(amount)
        invoice.payment_method = payment_method
        
        # Update payment status
        if invoice.paid_amount >= invoice.total_amount:
            invoice.payment_status = 'paid'
        elif invoice.paid_amount > 0:
            invoice.payment_status = 'partial'
        else:
            invoice.payment_status = 'unpaid'
        
        # ═══════════════════════════════════════════════════════════════════
        # 📊 DOUBLE-ENTRY ACCOUNTING: Customer Payment Received
        # ═══════════════════════════════════════════════════════════════════
        # When a customer pays for a credit sale:
        # 1. DEBIT:  Cash/Bank (Asset) - Money received
        # 2. CREDIT: Accounts Receivable (Asset) - Customer no longer owes
        # ═══════════════════════════════════════════════════════════════════
        
        ist = pytz.timezone('Asia/Kolkata')
        now = datetime.now(ist)
        today = now.date()
        
        # Entry 1: DEBIT Cash/Bank (Money IN)
        new_balance = Decimal(str(account.current_balance)) + amount
        
        db.session.execute(text("""
            INSERT INTO account_transactions
            (tenant_id, account_id, transaction_date, transaction_type,
             debit_amount, credit_amount, balance_after, reference_type, reference_id,
             voucher_number, narration, created_at, created_by)
            VALUES (:tenant_id, :account_id, :txn_date, 'invoice_payment',
                    :debit, 0.00, :balance, 'invoice', :ref_id,
                    :voucher, :narration, :created_at, NULL)
        """), {
            'tenant_id': tenant_id,
            'account_id': account_id,
            'txn_date': today,
            'debit': float(amount),  # Money received = Debit
            'balance': float(new_balance),
            'ref_id': invoice_id,
            'voucher': invoice.invoice_number,
            'narration': f'Payment received for {invoice.invoice_number} from {invoice.customer_name}',
            'created_at': now
        })
        
        # Entry 2: CREDIT Accounts Receivable (Customer paid, we owe them less)
        db.session.execute(text("""
            INSERT INTO account_transactions
            (tenant_id, account_id, transaction_date, transaction_type,
             debit_amount, credit_amount, balance_after, reference_type, reference_id,
             voucher_number, narration, created_at, created_by)
            VALUES (:tenant_id, NULL, :txn_date, 'accounts_receivable_payment',
                    0.00, :credit, 0.00, 'invoice', :ref_id,
                    :voucher, :narration, :created_at, NULL)
        """), {
            'tenant_id': tenant_id,
            'txn_date': today,
            'credit': float(amount),  # Reduce receivable = Credit
            'ref_id': invoice_id,
            'voucher': invoice.invoice_number,
            'narration': f'Received payment from {invoice.customer_name} for {invoice.invoice_number}',
            'created_at': now
        })
        
        print(f"✅ Double-entry for payment on {invoice.invoice_number}")
        print(f"   DEBIT:  {account.account_name}  ₹{amount:,.2f}")
        print(f"   CREDIT: Accounts Receivable  ₹{amount:,.2f}")
        
        # Update account balance
        db.session.execute(text("""
            UPDATE bank_accounts 
            SET current_balance = :new_balance, updated_at = :updated_at
            WHERE id = :account_id AND tenant_id = :tenant_id
        """), {
            'new_balance': new_balance,
            'updated_at': now,
            'account_id': account_id,
            'tenant_id': tenant_id
        })
        
        db.session.commit()
        flash(f'✅ Payment of ₹{amount:,.2f} recorded in {account.account_name}!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error recording payment: {str(e)}', 'error')
    
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

