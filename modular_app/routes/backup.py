"""
Backup & Restore Module
Allows tenant to backup/restore business data locally
"""
from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify, send_file
from models import (
    db, Tenant, Customer, Vendor, Employee, Site,
    Item, ItemCategory, ItemGroup, ItemStock, ItemImage,
    Invoice, InvoiceItem, 
    PurchaseBill, PurchaseBillItem,
    PurchaseRequest,
    SalesOrder, SalesOrderItem,
    DeliveryChallan, DeliveryChallanItem,
    Expense, ExpenseCategory,
    Task, TaskUpdate,
    CommissionAgent, InvoiceCommission,
    VendorPayment, PaymentAllocation
)
from utils.tenant_middleware import require_tenant, get_current_tenant, get_current_tenant_id
from utils.license_check import check_license
from functools import wraps
from datetime import datetime
import json
import io
import pytz

backup_bp = Blueprint('backup', __name__, url_prefix='/admin/backup')

# Login required decorator
def login_required(f):
    """Decorator to require admin login (also checks license)"""
    @wraps(f)
    @check_license  # Check license/trial before allowing access
    def decorated_function(*args, **kwargs):
        if 'tenant_admin_id' not in session:
            flash('Please login first', 'error')
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function


@backup_bp.route('/')
@require_tenant
@login_required
def index():
    """Backup & Restore main page - redirects to download page"""
    return redirect(url_for('backup.backup_download_page'))


@backup_bp.route('/download-page')
@require_tenant
@login_required
def backup_download_page():
    """Backup to Computer page"""
    tenant = get_current_tenant()
    tenant_id = get_current_tenant_id()
    
    # Get backup statistics
    stats = {
        'customers': Customer.query.filter_by(tenant_id=tenant_id).count(),
        'vendors': Vendor.query.filter_by(tenant_id=tenant_id).count(),
        'items': Item.query.filter_by(tenant_id=tenant_id).count(),
        'invoices': Invoice.query.filter_by(tenant_id=tenant_id).count(),
        'purchase_bills': PurchaseBill.query.filter_by(tenant_id=tenant_id).count(),
        'sales_orders': SalesOrder.query.filter_by(tenant_id=tenant_id).count(),
        'delivery_challans': DeliveryChallan.query.filter_by(tenant_id=tenant_id).count(),
        'expenses': Expense.query.filter_by(tenant_id=tenant_id).count(),
        'employees': Employee.query.filter_by(tenant_id=tenant_id).count(),
        'sites': Site.query.filter_by(tenant_id=tenant_id).count(),
    }
    
    total_records = sum(stats.values())
    
    return render_template('admin/backup_download.html', 
                         tenant=tenant, 
                         stats=stats,
                         total_records=total_records)


@backup_bp.route('/restore-page')
@require_tenant
@login_required
def backup_restore_page():
    """Restore Backup page"""
    tenant = get_current_tenant()
    return render_template('admin/backup_restore.html', tenant=tenant)


@backup_bp.route('/sync-share')
@require_tenant
@login_required
def backup_sync_share_page():
    """Sync & Share page (premium feature placeholder)"""
    tenant = get_current_tenant()
    return render_template('admin/backup_sync_share.html', tenant=tenant)


@backup_bp.route('/download')
@require_tenant
@login_required
def download_backup():
    """Generate and download backup JSON file"""
    tenant = get_current_tenant()
    tenant_id = get_current_tenant_id()
    
    try:
        # Helper function to serialize model objects
        def serialize_model(obj, exclude_fields=None):
            """Convert SQLAlchemy model to dict"""
            if exclude_fields is None:
                exclude_fields = []
            
            from datetime import date
            from decimal import Decimal
            
            data = {}
            for column in obj.__table__.columns:
                if column.name not in exclude_fields:
                    value = getattr(obj, column.name)
                    # Handle datetime objects
                    if isinstance(value, datetime):
                        # Convert to IST and make it ISO format
                        if value.tzinfo is None:
                            value = pytz.UTC.localize(value)
                        ist = pytz.timezone('Asia/Kolkata')
                        value = value.astimezone(ist).isoformat()
                    # Handle date objects (invoice_date, bill_date, etc.)
                    elif isinstance(value, date):
                        value = value.isoformat()  # Convert to 'YYYY-MM-DD' string
                    # Handle Decimal objects (amounts, prices, etc.)
                    elif isinstance(value, Decimal):
                        value = float(value)  # Convert to float for JSON
                    data[column.name] = value
            return data
        
        # Build backup data structure
        backup_data = {
            "backup_info": {
                "created_at": datetime.now(pytz.timezone('Asia/Kolkata')).isoformat(),
                "tenant_id": tenant_id,
                "company_name": tenant.company_name,
                "subdomain": tenant.subdomain,
                "admin_email": tenant.admin_email,
                "backup_version": "1.0",
                "app_version": "2.0.0",
                "warnings": [
                    "⚠️ Item images NOT included (will be added in future version)",
                    "⚠️ Purchase bill attachments NOT included",
                    "⚠️ Task media NOT included",
                    "⚠️ Attendance records NOT included",
                    "⚠️ Admin password NOT included (for security)"
                ]
            },
            "metadata": {},
            "data": {}
        }
        
        # Customers
        customers = Customer.query.filter_by(tenant_id=tenant_id).all()
        backup_data["data"]["customers"] = [serialize_model(c) for c in customers]
        backup_data["metadata"]["customers_count"] = len(customers)
        
        # Vendors
        vendors = Vendor.query.filter_by(tenant_id=tenant_id).all()
        backup_data["data"]["vendors"] = [serialize_model(v) for v in vendors]
        backup_data["metadata"]["vendors_count"] = len(vendors)
        
        # Item Categories
        categories = ItemCategory.query.filter_by(tenant_id=tenant_id).all()
        backup_data["data"]["item_categories"] = [serialize_model(c) for c in categories]
        
        # Item Groups
        groups = ItemGroup.query.filter_by(tenant_id=tenant_id).all()
        backup_data["data"]["item_groups"] = [serialize_model(g) for g in groups]
        
        # Items (exclude image URLs for now)
        items = Item.query.filter_by(tenant_id=tenant_id).all()
        backup_data["data"]["items"] = [serialize_model(i) for i in items]
        backup_data["metadata"]["items_count"] = len(items)
        
        # Item Stock
        stock = ItemStock.query.filter_by(tenant_id=tenant_id).all()
        backup_data["data"]["item_stock"] = [serialize_model(s) for s in stock]
        
        # Sites
        sites = Site.query.filter_by(tenant_id=tenant_id).all()
        backup_data["data"]["sites"] = [serialize_model(s) for s in sites]
        backup_data["metadata"]["sites_count"] = len(sites)
        
        # Employees
        employees = Employee.query.filter_by(tenant_id=tenant_id).all()
        backup_data["data"]["employees"] = [serialize_model(e) for e in employees]
        backup_data["metadata"]["employees_count"] = len(employees)
        
        # Invoices
        invoices = Invoice.query.filter_by(tenant_id=tenant_id).all()
        backup_data["data"]["invoices"] = [serialize_model(inv) for inv in invoices]
        backup_data["metadata"]["invoices_count"] = len(invoices)
        
        # Invoice Items
        invoice_items = InvoiceItem.query.join(Invoice).filter(Invoice.tenant_id == tenant_id).all()
        backup_data["data"]["invoice_items"] = [serialize_model(ii) for ii in invoice_items]
        
        # Purchase Bills
        bills = PurchaseBill.query.filter_by(tenant_id=tenant_id).all()
        backup_data["data"]["purchase_bills"] = [serialize_model(b) for b in bills]
        backup_data["metadata"]["purchase_bills_count"] = len(bills)
        
        # Purchase Bill Items
        bill_items = PurchaseBillItem.query.join(PurchaseBill).filter(PurchaseBill.tenant_id == tenant_id).all()
        backup_data["data"]["purchase_bill_items"] = [serialize_model(bi) for bi in bill_items]
        
        # Sales Orders
        orders = SalesOrder.query.filter_by(tenant_id=tenant_id).all()
        backup_data["data"]["sales_orders"] = [serialize_model(o) for o in orders]
        backup_data["metadata"]["sales_orders_count"] = len(orders)
        
        # Sales Order Items
        order_items = SalesOrderItem.query.join(SalesOrder).filter(SalesOrder.tenant_id == tenant_id).all()
        backup_data["data"]["sales_order_items"] = [serialize_model(oi) for oi in order_items]
        
        # Delivery Challans
        challans = DeliveryChallan.query.filter_by(tenant_id=tenant_id).all()
        backup_data["data"]["delivery_challans"] = [serialize_model(c) for c in challans]
        backup_data["metadata"]["delivery_challans_count"] = len(challans)
        
        # Delivery Challan Items
        challan_items = DeliveryChallanItem.query.join(DeliveryChallan).filter(DeliveryChallan.tenant_id == tenant_id).all()
        backup_data["data"]["delivery_challan_items"] = [serialize_model(ci) for ci in challan_items]
        
        # Expense Categories
        exp_categories = ExpenseCategory.query.filter_by(tenant_id=tenant_id).all()
        backup_data["data"]["expense_categories"] = [serialize_model(ec) for ec in exp_categories]
        
        # Expenses
        expenses = Expense.query.filter_by(tenant_id=tenant_id).all()
        backup_data["data"]["expenses"] = [serialize_model(e) for e in expenses]
        backup_data["metadata"]["expenses_count"] = len(expenses)
        
        # Purchase Requests
        requests = PurchaseRequest.query.filter_by(tenant_id=tenant_id).all()
        backup_data["data"]["purchase_requests"] = [serialize_model(r) for r in requests]
        
        # Tasks (text only, no media)
        tasks = Task.query.filter_by(tenant_id=tenant_id).all()
        backup_data["data"]["tasks"] = [serialize_model(t) for t in tasks]
        
        # Task Updates
        task_updates = TaskUpdate.query.join(Task).filter(Task.tenant_id == tenant_id).all()
        backup_data["data"]["task_updates"] = [serialize_model(tu) for tu in task_updates]
        
        # Commission Agents
        agents = CommissionAgent.query.filter_by(tenant_id=tenant_id).all()
        backup_data["data"]["commission_agents"] = [serialize_model(a) for a in agents]
        
        # Invoice Commissions
        commissions = InvoiceCommission.query.filter_by(tenant_id=tenant_id).all()
        backup_data["data"]["invoice_commissions"] = [serialize_model(c) for c in commissions]
        
        # Vendor Payments
        payments = VendorPayment.query.filter_by(tenant_id=tenant_id).all()
        backup_data["data"]["vendor_payments"] = [serialize_model(p) for p in payments]
        
        # Payment Allocations
        allocations = PaymentAllocation.query.join(VendorPayment).filter(VendorPayment.tenant_id == tenant_id).all()
        backup_data["data"]["payment_allocations"] = [serialize_model(a) for a in allocations]
        
        # Bank & Cash Accounts (NEW - Accounting Module)
        from models.bank_cash_account import BankCashAccount
        accounts = BankCashAccount.query.filter_by(tenant_id=tenant_id).all()
        backup_data["data"]["bank_cash_accounts"] = [serialize_model(acc) for acc in accounts]
        backup_data["metadata"]["bank_cash_accounts_count"] = len(accounts)
        
        # Account Transactions (NEW - Accounting Module)
        from models.bank_cash_account import AccountTransaction
        transactions = AccountTransaction.query.filter_by(tenant_id=tenant_id).all()
        backup_data["data"]["account_transactions"] = [serialize_model(t) for t in transactions]
        backup_data["metadata"]["account_transactions_count"] = len(transactions)
        
        # Contra Vouchers (NEW - Accounting Module)
        from models.bank_cash_account import ContraVoucher
        contra = ContraVoucher.query.filter_by(tenant_id=tenant_id).all()
        backup_data["data"]["contra_vouchers"] = [serialize_model(c) for c in contra]
        
        # Employee Cash Advances (NEW - Accounting Module)
        from models.bank_cash_account import EmployeeCashAdvance
        advances = EmployeeCashAdvance.query.filter_by(tenant_id=tenant_id).all()
        backup_data["data"]["employee_cash_advances"] = [serialize_model(adv) for adv in advances]
        
        # Payroll Payments (NEW - Payroll Module)
        from models.payroll import PayrollPayment
        payroll_payments = PayrollPayment.query.filter_by(tenant_id=tenant_id).all()
        backup_data["data"]["payroll_payments"] = [serialize_model(pp) for pp in payroll_payments]
        backup_data["metadata"]["payroll_payments_count"] = len(payroll_payments)
        
        # Salary Slips (NEW - Payroll Module)
        from models.payroll import SalarySlip
        salary_slips = SalarySlip.query.filter_by(tenant_id=tenant_id).all()
        backup_data["data"]["salary_slips"] = [serialize_model(ss) for ss in salary_slips]
        backup_data["metadata"]["salary_slips_count"] = len(salary_slips)
        
        # Calculate total records
        total_records = sum([
            len(backup_data["data"].get(key, [])) 
            for key in backup_data["data"].keys()
        ])
        backup_data["backup_info"]["total_records"] = total_records
        
        # Generate filename
        timestamp = datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d_%H%M')
        filename = f"{tenant.subdomain}_backup_{timestamp}.json"
        
        # Create file in memory
        json_str = json.dumps(backup_data, indent=2, ensure_ascii=False)
        json_bytes = json_str.encode('utf-8')
        file_obj = io.BytesIO(json_bytes)
        
        print(f"✅ Backup created: {filename} ({len(json_bytes)/1024:.1f} KB, {total_records} records)")
        
        return send_file(
            file_obj,
            mimetype='application/json',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        print(f"❌ Backup failed: {str(e)}")
        import traceback
        traceback.print_exc()
        flash(f'❌ Backup failed: {str(e)}', 'error')
        return redirect(url_for('backup.index'))


@backup_bp.route('/restore', methods=['POST'])
@require_tenant
@login_required
def restore_backup():
    """Restore from backup file"""
    tenant = get_current_tenant()
    tenant_id = get_current_tenant_id()
    
    if 'backup_file' not in request.files:
        flash('❌ No file uploaded', 'error')
        return redirect(url_for('backup.index'))
    
    file = request.files['backup_file']
    
    if file.filename == '':
        flash('❌ No file selected', 'error')
        return redirect(url_for('backup.index'))
    
    if not file.filename.endswith('.json'):
        flash('❌ Invalid file type. Please upload a .json backup file', 'error')
        return redirect(url_for('backup.index'))
    
    try:
        # Read and parse JSON
        file_content = file.read()
        backup_data = json.loads(file_content)
        
        # Validate backup structure
        if "backup_info" not in backup_data or "data" not in backup_data:
            flash('❌ Invalid backup file format', 'error')
            return redirect(url_for('backup.index'))
        
        backup_info = backup_data["backup_info"]
        data = backup_data["data"]
        
        # Show confirmation info
        flash(f'📦 Backup file: {file.filename}', 'info')
        flash(f'📅 Created: {backup_info.get("created_at", "Unknown")}', 'info')
        flash(f'📊 Records: {backup_info.get("total_records", 0)}', 'info')
        
        # BEGIN TRANSACTION
        try:
            # Helper to convert ISO datetime/date string back to datetime/date object
            def parse_datetime(date_str):
                """Parse ISO format datetime or date string"""
                if date_str:
                    try:
                        from datetime import date
                        # Try parsing as datetime first
                        parsed = datetime.fromisoformat(date_str)
                        return parsed
                    except:
                        try:
                            # If that fails, try parsing as date
                            parsed = date.fromisoformat(date_str)
                            return parsed
                        except:
                            return None
                return None
            
            # Delete business data (PRESERVE Tenant!)
            print("🗑️  Deleting existing business data...")
            
            # Delete in correct order (foreign keys!)
            PaymentAllocation.query.filter(PaymentAllocation.payment_id.in_(
                db.session.query(VendorPayment.id).filter_by(tenant_id=tenant_id)
            )).delete(synchronize_session=False)
            
            VendorPayment.query.filter_by(tenant_id=tenant_id).delete()
            InvoiceCommission.query.filter_by(tenant_id=tenant_id).delete()
            CommissionAgent.query.filter_by(tenant_id=tenant_id).delete()
            TaskUpdate.query.filter(TaskUpdate.task_id.in_(
                db.session.query(Task.id).filter_by(tenant_id=tenant_id)
            )).delete(synchronize_session=False)
            Task.query.filter_by(tenant_id=tenant_id).delete()
            
            DeliveryChallanItem.query.filter(DeliveryChallanItem.challan_id.in_(
                db.session.query(DeliveryChallan.id).filter_by(tenant_id=tenant_id)
            )).delete(synchronize_session=False)
            DeliveryChallan.query.filter_by(tenant_id=tenant_id).delete()
            
            SalesOrderItem.query.filter(SalesOrderItem.order_id.in_(
                db.session.query(SalesOrder.id).filter_by(tenant_id=tenant_id)
            )).delete(synchronize_session=False)
            SalesOrder.query.filter_by(tenant_id=tenant_id).delete()
            
            PurchaseBillItem.query.filter(PurchaseBillItem.bill_id.in_(
                db.session.query(PurchaseBill.id).filter_by(tenant_id=tenant_id)
            )).delete(synchronize_session=False)
            PurchaseBill.query.filter_by(tenant_id=tenant_id).delete()
            
            InvoiceItem.query.filter(InvoiceItem.invoice_id.in_(
                db.session.query(Invoice.id).filter_by(tenant_id=tenant_id)
            )).delete(synchronize_session=False)
            Invoice.query.filter_by(tenant_id=tenant_id).delete()
            
            PurchaseRequest.query.filter_by(tenant_id=tenant_id).delete()
            Expense.query.filter_by(tenant_id=tenant_id).delete()
            ExpenseCategory.query.filter_by(tenant_id=tenant_id).delete()
            ItemStock.query.filter_by(tenant_id=tenant_id).delete()
            Item.query.filter_by(tenant_id=tenant_id).delete()
            ItemGroup.query.filter_by(tenant_id=tenant_id).delete()
            ItemCategory.query.filter_by(tenant_id=tenant_id).delete()
            Employee.query.filter_by(tenant_id=tenant_id).delete()
            Site.query.filter_by(tenant_id=tenant_id).delete()
            Vendor.query.filter_by(tenant_id=tenant_id).delete()
            Customer.query.filter_by(tenant_id=tenant_id).delete()
            
            db.session.flush()
            print("✅ Existing data deleted")
            
            # Import data from backup
            print("📥 Importing data from backup...")
            
            # Helper to create objects
            def create_objects(model_class, data_list):
                from decimal import Decimal
                objects = []
                for item_data in data_list:
                    # Convert datetime/date strings back to datetime/date objects
                    for key, value in item_data.items():
                        if isinstance(value, str) and ('_at' in key or '_date' in key):
                            item_data[key] = parse_datetime(value)
                        # Convert float back to Decimal for amount fields
                        elif isinstance(value, float) and any(x in key for x in ['amount', 'price', 'total', 'cost', 'rate', 'percentage', 'commission']):
                            item_data[key] = Decimal(str(value))
                    obj = model_class(**item_data)
                    objects.append(obj)
                if objects:
                    db.session.bulk_save_objects(objects)
                return len(objects)
            
            # Import in correct order (dependencies!)
            counts = {}
            
            if "customers" in data:
                counts['customers'] = create_objects(Customer, data["customers"])
            
            if "vendors" in data:
                counts['vendors'] = create_objects(Vendor, data["vendors"])
            
            if "sites" in data:
                counts['sites'] = create_objects(Site, data["sites"])
            
            if "employees" in data:
                counts['employees'] = create_objects(Employee, data["employees"])
            
            if "item_categories" in data:
                counts['item_categories'] = create_objects(ItemCategory, data["item_categories"])
            
            if "item_groups" in data:
                counts['item_groups'] = create_objects(ItemGroup, data["item_groups"])
            
            if "items" in data:
                counts['items'] = create_objects(Item, data["items"])
            
            if "item_stock" in data:
                counts['item_stock'] = create_objects(ItemStock, data["item_stock"])
            
            if "expense_categories" in data:
                counts['expense_categories'] = create_objects(ExpenseCategory, data["expense_categories"])
            
            if "expenses" in data:
                counts['expenses'] = create_objects(Expense, data["expenses"])
            
            if "invoices" in data:
                counts['invoices'] = create_objects(Invoice, data["invoices"])
            
            if "invoice_items" in data:
                counts['invoice_items'] = create_objects(InvoiceItem, data["invoice_items"])
            
            if "purchase_bills" in data:
                counts['purchase_bills'] = create_objects(PurchaseBill, data["purchase_bills"])
            
            if "purchase_bill_items" in data:
                counts['purchase_bill_items'] = create_objects(PurchaseBillItem, data["purchase_bill_items"])
            
            if "sales_orders" in data:
                counts['sales_orders'] = create_objects(SalesOrder, data["sales_orders"])
            
            if "sales_order_items" in data:
                counts['sales_order_items'] = create_objects(SalesOrderItem, data["sales_order_items"])
            
            if "delivery_challans" in data:
                counts['delivery_challans'] = create_objects(DeliveryChallan, data["delivery_challans"])
            
            if "delivery_challan_items" in data:
                counts['delivery_challan_items'] = create_objects(DeliveryChallanItem, data["delivery_challan_items"])
            
            if "purchase_requests" in data:
                counts['purchase_requests'] = create_objects(PurchaseRequest, data["purchase_requests"])
            
            if "tasks" in data:
                counts['tasks'] = create_objects(Task, data["tasks"])
            
            if "task_updates" in data:
                counts['task_updates'] = create_objects(TaskUpdate, data["task_updates"])
            
            if "commission_agents" in data:
                counts['commission_agents'] = create_objects(CommissionAgent, data["commission_agents"])
            
            if "invoice_commissions" in data:
                counts['invoice_commissions'] = create_objects(InvoiceCommission, data["invoice_commissions"])
            
            if "vendor_payments" in data:
                counts['vendor_payments'] = create_objects(VendorPayment, data["vendor_payments"])
            
            if "payment_allocations" in data:
                counts['payment_allocations'] = create_objects(PaymentAllocation, data["payment_allocations"])
            
            # COMMIT TRANSACTION
            db.session.commit()
            
            total_imported = sum(counts.values())
            print(f"✅ Restore complete! Imported {total_imported} records")
            
            flash(f'✅ Backup restored successfully!', 'success')
            flash(f'📊 Imported {total_imported} records', 'success')
            flash(f'📅 From backup dated: {backup_info.get("created_at", "Unknown")}', 'info')
            flash('🔄 Refresh your page to see restored data', 'info')
            
            return redirect(url_for('admin.dashboard'))
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Restore failed, rolled back: {str(e)}")
            import traceback
            traceback.print_exc()
            flash(f'❌ Restore failed: {str(e)}', 'error')
            flash('✅ No data was changed (transaction rolled back)', 'info')
            return redirect(url_for('backup.index'))
            
    except json.JSONDecodeError:
        flash('❌ Invalid JSON file', 'error')
        return redirect(url_for('backup.index'))
    except Exception as e:
        print(f"❌ Error reading backup file: {str(e)}")
        import traceback
        traceback.print_exc()
        flash(f'❌ Error: {str(e)}', 'error')
        return redirect(url_for('backup.index'))

