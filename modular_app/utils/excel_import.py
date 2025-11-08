"""
Excel Import Utilities for Bulk Data Import
Handles validation, parsing, and importing from Excel/CSV files
"""

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Alignment
from io import BytesIO
from datetime import datetime
from models import db, Employee, Item, Customer, Site, ItemCategory, ItemGroup

def create_employee_template():
    """
    Create Excel template for employee bulk import
    Returns: BytesIO object with Excel file
    """
    wb = Workbook()
    ws = wb.active
    ws.title = "Employee Import"
    
    # Headers - match actual Employee model fields
    headers = ['Name*', 'PIN*', 'Phone', 'Email', 'Site Name']
    
    # Style headers
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF")
    
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num, value=header)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center")
    
    # Add sample data (row 2)
    sample_data = [
        'John Doe',
        '1234',
        '9876543210',
        'john@example.com',
        'Main Office'
    ]
    
    for col_num, value in enumerate(sample_data, 1):
        cell = ws.cell(row=2, column=col_num, value=value)
        cell.fill = PatternFill(start_color="E7E6E6", end_color="E7E6E6", fill_type="solid")
    
    # Add instructions
    ws.cell(row=4, column=1, value="INSTRUCTIONS:")
    ws.cell(row=5, column=1, value="1. Fields marked with * are required (Name, PIN)")
    ws.cell(row=6, column=1, value="2. PIN must be 4 digits")
    ws.cell(row=7, column=1, value="3. Phone should be 10 digits (optional)")
    ws.cell(row=8, column=1, value="4. Email is optional (for purchase request notifications)")
    ws.cell(row=9, column=1, value="5. If Site Name doesn't exist, it will be created")
    ws.cell(row=10, column=1, value="6. Delete row 2 (sample data) before uploading")
    ws.cell(row=11, column=1, value="7. You can add as many rows as you need")
    
    # Adjust column widths
    ws.column_dimensions['A'].width = 20
    ws.column_dimensions['B'].width = 10
    ws.column_dimensions['C'].width = 15
    ws.column_dimensions['D'].width = 25
    ws.column_dimensions['E'].width = 20
    
    # Save to BytesIO
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    
    return output


def create_inventory_template():
    """
    Create Excel template for inventory bulk import
    Returns: BytesIO object with Excel file
    """
    wb = Workbook()
    ws = wb.active
    ws.title = "Inventory Import"
    
    # Headers
    headers = ['Item Name*', 'SKU', 'Category*', 'Group*', 'Unit*', 'Stock Quantity*', 
               'Price', 'Tax Rate (%)', 'HSN Code', 'Description']
    
    # Style headers
    header_fill = PatternFill(start_color="70AD47", end_color="70AD47", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF")
    
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num, value=header)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center")
    
    # Add sample data (row 2)
    sample_data = [
        'Cement 50kg',
        'CEM-001',
        'Building Material',
        'Construction',
        'Bag',
        '100',
        '350',
        '12',
        '2523',
        'Premium quality cement'
    ]
    
    for col_num, value in enumerate(sample_data, 1):
        cell = ws.cell(row=2, column=col_num, value=value)
        cell.fill = PatternFill(start_color="E7E6E6", end_color="E7E6E6", fill_type="solid")
    
    # Add instructions
    ws.cell(row=4, column=1, value="INSTRUCTIONS:")
    ws.cell(row=5, column=1, value="1. Fields marked with * are required")
    ws.cell(row=6, column=1, value="2. If SKU is blank, it will be auto-generated")
    ws.cell(row=7, column=1, value="3. If Category/Group doesn't exist, it will be created")
    ws.cell(row=8, column=1, value="4. Unit examples: Pcs, Kg, Liter, Box, Bag, Meter")
    ws.cell(row=9, column=1, value="5. Tax Rate is optional (default 18%)")
    ws.cell(row=10, column=1, value="6. Delete row 2 (sample data) before uploading")
    
    # Adjust column widths
    ws.column_dimensions['A'].width = 25
    ws.column_dimensions['B'].width = 12
    ws.column_dimensions['C'].width = 20
    ws.column_dimensions['D'].width = 18
    ws.column_dimensions['E'].width = 10
    ws.column_dimensions['F'].width = 15
    ws.column_dimensions['G'].width = 12
    ws.column_dimensions['H'].width = 12
    ws.column_dimensions['I'].width = 12
    ws.column_dimensions['J'].width = 30
    
    # Save to BytesIO
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    
    return output


def create_customer_template():
    """
    Create Excel template for customer bulk import
    Returns: BytesIO object with Excel file
    """
    wb = Workbook()
    ws = wb.active
    ws.title = "Customer Import"
    
    # Headers - match Customer model fields
    headers = ['Customer Name*', 'Phone*', 'Email', 'GSTIN', 'Address', 'State', 'Credit Limit', 'Payment Terms (Days)', 'Opening Balance', 'Notes']
    
    # Style headers
    header_fill = PatternFill(start_color="FFC000", end_color="FFC000", fill_type="solid")
    header_font = Font(bold=True, color="000000")
    
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num, value=header)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center")
    
    # Add sample data (row 2)
    sample_data = [
        'ABC Corporation',
        '9876543210',
        'contact@abc.com',
        '27AABCU9603R1ZM',
        '123 Business Park, Mumbai, 400001',
        'Maharashtra',
        '50000',  # Credit Limit
        '30',  # Payment Terms (Days)
        '0',  # Opening Balance
        'VIP Customer'  # Notes
    ]
    
    for col_num, value in enumerate(sample_data, 1):
        cell = ws.cell(row=2, column=col_num, value=value)
        cell.fill = PatternFill(start_color="E7E6E6", end_color="E7E6E6", fill_type="solid")
    
    # Add instructions
    ws.cell(row=4, column=1, value="INSTRUCTIONS:")
    ws.cell(row=5, column=1, value="1. Fields marked with * are required (Name, Phone)")
    ws.cell(row=6, column=1, value="2. Phone must be 10 digits")
    ws.cell(row=7, column=1, value="3. GSTIN format: 15 characters (optional)")
    ws.cell(row=8, column=1, value="4. Customer code will be auto-generated (CUST-0001, CUST-0002, etc.)")
    ws.cell(row=9, column=1, value="5. Credit Limit, Payment Terms, Opening Balance are optional (default: 0, 30, 0)")
    ws.cell(row=10, column=1, value="6. Payment Terms is in days (e.g., 30 = payment due in 30 days)")
    ws.cell(row=11, column=1, value="7. Delete row 2 (sample data) before uploading")
    
    # Adjust column widths
    ws.column_dimensions['A'].width = 25  # Customer Name
    ws.column_dimensions['B'].width = 15  # Phone
    ws.column_dimensions['C'].width = 25  # Email
    ws.column_dimensions['D'].width = 20  # GSTIN
    ws.column_dimensions['E'].width = 40  # Address
    ws.column_dimensions['F'].width = 15  # State
    ws.column_dimensions['G'].width = 15  # Credit Limit
    ws.column_dimensions['H'].width = 20  # Payment Terms
    ws.column_dimensions['I'].width = 18  # Opening Balance
    ws.column_dimensions['J'].width = 25  # Notes
    
    # Save to BytesIO
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    
    return output


def validate_employee_row(row_data, row_num):
    """
    Validate a single employee row
    Returns: (is_valid, error_message)
    """
    name, pin, phone, email, site_name = row_data
    
    # Required fields
    if not name or str(name).strip() == '':
        return False, f"Row {row_num}: Name is required"
    
    if not pin:
        return False, f"Row {row_num}: PIN is required"
    
    # Handle PIN (might be float from Excel, e.g., 1111.0)
    try:
        if isinstance(pin, float):
            pin = int(pin)  # Convert 1111.0 → 1111
        pin_str = str(pin).strip()
    except:
        return False, f"Row {row_num}: PIN must be a valid number"
    
    if len(pin_str) != 4 or not pin_str.isdigit():
        return False, f"Row {row_num}: PIN must be exactly 4 digits"
    
    # Phone is optional, but if provided, validate it
    if phone and str(phone).strip():
        try:
            if isinstance(phone, float):
                phone = int(phone)  # Convert 9876543210.0 → 9876543210
            phone_str = str(phone).strip()
        except:
            return False, f"Row {row_num}: Phone must be a valid number"
        
        if len(phone_str) != 10 or not phone_str.isdigit():
            return False, f"Row {row_num}: Phone must be 10 digits (or leave blank)"
    
    return True, None


def validate_inventory_row(row_data, row_num):
    """
    Validate a single inventory row
    Returns: (is_valid, error_message)
    """
    item_name, sku, category, group, unit, stock, price, tax_rate, hsn, description = row_data
    
    # Required fields
    if not item_name or str(item_name).strip() == '':
        return False, f"Row {row_num}: Item Name is required"
    
    if not category or str(category).strip() == '':
        return False, f"Row {row_num}: Category is required"
    
    if not group or str(group).strip() == '':
        return False, f"Row {row_num}: Group is required"
    
    if not unit or str(unit).strip() == '':
        return False, f"Row {row_num}: Unit is required"
    
    if stock is None or str(stock).strip() == '':
        return False, f"Row {row_num}: Stock Quantity is required"
    
    try:
        stock_val = float(stock)
        if stock_val < 0:
            return False, f"Row {row_num}: Stock Quantity cannot be negative"
    except:
        return False, f"Row {row_num}: Stock Quantity must be a number"
    
    return True, None


def validate_customer_row(row_data, row_num):
    """
    Validate a single customer row
    Returns: (is_valid, error_message)
    """
    name, phone, email, gstin, address, state, credit_limit, payment_terms, opening_balance, notes = row_data
    
    # Required fields
    if not name or str(name).strip() == '':
        return False, f"Row {row_num}: Customer Name is required"
    
    if not phone:
        return False, f"Row {row_num}: Phone is required"
    
    # Handle phone as float (Excel issue)
    try:
        if isinstance(phone, float):
            phone = int(phone)
        phone_str = str(phone).strip()
    except:
        return False, f"Row {row_num}: Phone must be a valid number"
    
    if len(phone_str) != 10 or not phone_str.isdigit():
        return False, f"Row {row_num}: Phone must be 10 digits"
    
    # Validate GSTIN if provided
    if gstin and str(gstin).strip():
        gstin_str = str(gstin).strip()
        if len(gstin_str) != 15:
            return False, f"Row {row_num}: GSTIN must be 15 characters"
    
    # Validate numeric fields if provided
    if credit_limit and credit_limit != '':
        try:
            float(credit_limit)
        except:
            return False, f"Row {row_num}: Credit Limit must be a number"
    
    if payment_terms and payment_terms != '':
        try:
            int(payment_terms)
        except:
            return False, f"Row {row_num}: Payment Terms must be a number (days)"
    
    if opening_balance and opening_balance != '':
        try:
            float(opening_balance)
        except:
            return False, f"Row {row_num}: Opening Balance must be a number"
    
    return True, None


def import_employees_from_excel(file, tenant_id):
    """
    Import employees from Excel file
    Returns: (success_count, errors_list)
    """
    try:
        wb = load_workbook(file)
        ws = wb.active
        
        success_count = 0
        errors = []
        
        # Skip header row, start from row 2
        for row_num, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
            # Skip empty rows
            if all(cell is None or str(cell).strip() == '' for cell in row):
                continue
            
            # Extract data (pad with None if row is shorter)
            row_data = list(row) + [None] * (5 - len(row))
            name, pin, phone, email, site_name = row_data[:5]
            
            # Validate
            is_valid, error_msg = validate_employee_row(row_data[:5], row_num)
            if not is_valid:
                errors.append(error_msg)
                continue
            
            try:
                # Check if employee already exists (PIN is unique per tenant)
                existing = Employee.query.filter_by(
                    tenant_id=tenant_id,
                    pin=str(pin).strip()
                ).first()
                
                if existing:
                    errors.append(f"Row {row_num}: Employee with PIN {pin} already exists")
                    continue
                
                # Get or create site
                site = None
                if site_name and str(site_name).strip():
                    site = Site.query.filter_by(
                        tenant_id=tenant_id,
                        name=str(site_name).strip()
                    ).first()
                    
                    if not site:
                        site = Site(
                            tenant_id=tenant_id,
                            name=str(site_name).strip(),
                            address='',
                            latitude=0.0,
                            longitude=0.0
                        )
                        db.session.add(site)
                        db.session.flush()
                
                # Create employee (only with fields that exist in model)
                # Convert PIN and phone from float if needed
                pin_final = str(int(pin) if isinstance(pin, float) else pin).strip()
                phone_final = str(int(phone) if isinstance(phone, float) else phone).strip() if phone else None
                
                employee = Employee(
                    tenant_id=tenant_id,
                    name=str(name).strip(),
                    pin=pin_final,
                    phone=phone_final,
                    email=str(email).strip() if email else None,
                    site_id=site.id if site else None,
                    active=True
                )
                
                db.session.add(employee)
                success_count += 1
                
            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)}")
                continue
        
        if success_count > 0:
            db.session.commit()
        
        return success_count, errors
        
    except Exception as e:
        db.session.rollback()
        return 0, [f"File error: {str(e)}"]


def import_inventory_from_excel(file, tenant_id):
    """
    Import inventory items from Excel file
    Returns: (success_count, errors_list)
    """
    try:
        wb = load_workbook(file)
        ws = wb.active
        
        success_count = 0
        errors = []
        
        # Skip header row, start from row 2
        for row_num, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
            # Skip empty rows
            if all(cell is None or str(cell).strip() == '' for cell in row):
                continue
            
            # Extract data
            row_data = list(row) + [None] * (10 - len(row))
            item_name, sku, category, group, unit, stock, price, tax_rate, hsn, description = row_data[:10]
            
            # Validate
            is_valid, error_msg = validate_inventory_row(row_data[:10], row_num)
            if not is_valid:
                errors.append(error_msg)
                continue
            
            try:
                # Get or create group
                group_obj = ItemGroup.query.filter_by(
                    tenant_id=tenant_id,
                    name=str(group).strip()
                ).first()
                
                if not group_obj:
                    group_obj = ItemGroup(
                        tenant_id=tenant_id,
                        name=str(group).strip()
                    )
                    db.session.add(group_obj)
                    db.session.flush()
                
                # Get or create category
                category_obj = ItemCategory.query.filter_by(
                    tenant_id=tenant_id,
                    name=str(category).strip(),
                    group_id=group_obj.id
                ).first()
                
                if not category_obj:
                    category_obj = ItemCategory(
                        tenant_id=tenant_id,
                        name=str(category).strip(),
                        group_id=group_obj.id
                    )
                    db.session.add(category_obj)
                    db.session.flush()
                
                # Generate SKU if not provided
                if not sku or str(sku).strip() == '':
                    # Auto-generate SKU
                    prefix = str(item_name).strip()[:3].upper()
                    count = Item.query.filter_by(tenant_id=tenant_id).count()
                    sku = f"{prefix}-{count + 1:04d}"
                else:
                    sku = str(sku).strip()
                
                # Check if item already exists
                existing = Item.query.filter_by(
                    tenant_id=tenant_id,
                    sku=sku
                ).first()
                
                if existing:
                    errors.append(f"Row {row_num}: Item with SKU {sku} already exists")
                    continue
                
                # Create item
                item = Item(
                    tenant_id=tenant_id,
                    name=str(item_name).strip(),
                    sku=sku,
                    category_id=category_obj.id,
                    item_group_id=group_obj.id,
                    unit=str(unit).strip(),
                    opening_stock=float(stock) if stock else 0.0,
                    selling_price=float(price) if price else 0.0,
                    cost_price=float(price) if price else 0.0,  # Same as selling for now
                    hsn_code=str(hsn).strip() if hsn else None,  # NEW: HSN code from Excel
                    gst_rate=float(tax_rate) if tax_rate else 18.0,  # NEW: GST rate as float
                    tax_preference=f"GST {tax_rate}%" if tax_rate else "GST 18%",  # Keep for backward compatibility
                    sales_description=str(description).strip() if description else '',
                    purchase_description=str(description).strip() if description else ''
                )
                
                db.session.add(item)
                db.session.flush()  # Get item.id
                
                # Create stock record for default site
                from models import Site, ItemStock
                default_site = Site.query.filter_by(tenant_id=tenant_id).first()
                
                if default_site and item.track_inventory:
                    item_stock = ItemStock(
                        tenant_id=tenant_id,
                        item_id=item.id,
                        site_id=default_site.id,
                        quantity_available=float(stock) if stock else 0.0,
                        stock_value=(float(stock) if stock else 0.0) * (float(price) if price else 0.0)
                    )
                    db.session.add(item_stock)
                
                success_count += 1
                
            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)}")
                continue
        
        if success_count > 0:
            db.session.commit()
        
        return success_count, errors
        
    except Exception as e:
        db.session.rollback()
        return 0, [f"File error: {str(e)}"]


def import_customers_from_excel(file, tenant_id):
    """
    Import customers from Excel file
    Returns: (success_count, errors_list)
    """
    try:
        wb = load_workbook(file)
        ws = wb.active
        
        success_count = 0
        errors = []
        
        # Skip header row, start from row 2
        for row_num, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
            # Skip empty rows
            if all(cell is None or str(cell).strip() == '' for cell in row):
                continue
            
            # Extract data - match new template format
            row_data = list(row) + [None] * (10 - len(row))
            name, phone, email, gstin, address, state, credit_limit, payment_terms, opening_balance, notes = row_data[:10]
            
            # Validate
            is_valid, error_msg = validate_customer_row(row_data[:10], row_num)
            if not is_valid:
                errors.append(error_msg)
                continue
            
            try:
                # Check if customer already exists
                existing = Customer.query.filter_by(
                    tenant_id=tenant_id,
                    phone=str(phone).strip()
                ).first()
                
                if existing:
                    errors.append(f"Row {row_num}: Customer with phone {phone} already exists")
                    continue
                
                # Generate customer code
                last_customer = Customer.query.filter_by(tenant_id=tenant_id).order_by(Customer.id.desc()).first()
                if last_customer and last_customer.customer_code:
                    last_num = int(last_customer.customer_code.split('-')[-1])
                    next_num = last_num + 1
                else:
                    next_num = 1
                customer_code = f"CUST-{next_num:04d}"
                
                # Handle phone as float (Excel issue)
                phone_final = str(int(phone) if isinstance(phone, float) else phone).strip()
                
                # Create customer with all fields
                customer = Customer(
                    tenant_id=tenant_id,
                    customer_code=customer_code,
                    name=str(name).strip(),
                    phone=phone_final,
                    email=str(email).strip() if email else '',
                    gstin=str(gstin).strip() if gstin else '',
                    address=str(address).strip() if address else '',
                    state=str(state).strip() if state else '',
                    credit_limit=float(credit_limit) if credit_limit else 0,
                    payment_terms_days=int(payment_terms) if payment_terms else 30,
                    opening_balance=float(opening_balance) if opening_balance else 0,
                    notes=str(notes).strip() if notes else ''
                )
                
                db.session.add(customer)
                success_count += 1
                
            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)}")
                continue
        
        if success_count > 0:
            db.session.commit()
        
        return success_count, errors
        
    except Exception as e:
        db.session.rollback()
        return 0, [f"File error: {str(e)}"]

