# 📥 Smart Import System - Minimum Data Requirements

**Goal:** Help merchants import inventory with minimal effort and data preparation

---

## 🎯 **The Challenge**

**Current Problem:**
```
Merchant has 5000 products to import
Current template requires: 15+ columns
Merchant spends: 40+ hours preparing data 😰
Many columns left blank anyway
High chance of errors
```

**Ideal Solution:**
```
Merchant provides: 5-7 essential columns
System auto-generates: Everything else
Time to import: 30 minutes ✨
Error rate: Near zero
```

---

## 📋 **Minimal Data Requirements**

### **Absolute Minimum (3 columns) - Basic Retail**

```excel
Item Name       | Selling Price | Stock Quantity
----------------|---------------|----------------
Levi's 501 Jeans| 2499         | 50
Nike T-Shirt    | 799          | 100
Adidas Shoes    | 3999         | 25
```

**What System Auto-Generates:**
- ✅ SKU (from item name)
- ✅ Barcode (random or sequential)
- ✅ Category (from name analysis)
- ✅ Unit (default: "pc")
- ✅ Reorder point (based on stock)
- ✅ MRP (= Selling Price if not provided)
- ✅ Discount (= 0%)

---

### **Recommended Minimum (5 columns) - Clothing Retail**

```excel
Item Name          | Size | Color | Selling Price | Stock
-------------------|------|-------|---------------|-------
Levi's 501 Jeans   | 32   | Blue  | 2499         | 15
Levi's 501 Jeans   | 34   | Blue  | 2499         | 12
Levi's 501 Jeans   | 32   | Black | 2499         | 8
Nike T-Shirt       | M    | Red   | 799          | 50
Nike T-Shirt       | L    | Red   | 799          | 30
```

**What System Auto-Generates:**
- ✅ Parent-child relationships (groups same product)
- ✅ SKU with variant suffix (LEV501-BLU-32)
- ✅ Unique barcodes per variant
- ✅ Variant attributes stored correctly

---

### **Optimal Data (8 columns) - Full Features**

```excel
Item Name          | Size | Color | MRP  | Selling Price | Stock | Barcode       | Reorder Point
-------------------|------|-------|------|---------------|-------|---------------|---------------
Levi's 501 Jeans   | 32   | Blue  | 3999 | 2499         | 15    | 8901234560001 | 5
Levi's 501 Jeans   | 34   | Blue  | 3999 | 2499         | 12    | 8901234560002 | 5
```

**Benefits:**
- ✅ Automatic discount calculation (MRP vs Selling Price)
- ✅ Low stock alerts configured
- ✅ Ready for barcode scanning
- ✅ Complete product data

---

## 🏗️ **Smart Import Architecture**

### **Phase 1: Template Generation**

```python
# routes/smart_import.py

def generate_smart_template(tenant_id, template_type='minimal'):
    """
    Generate Excel template based on business configuration
    
    Template Types:
    1. minimal: Name, Price, Stock (3 columns)
    2. clothing: Name, Size, Color, Price, Stock (5 columns)
    3. pharmacy: Name, Batch, Expiry, Price, Stock (5 columns)
    4. electronics: Name, Model, IMEI, Price, Stock (5 columns)
    5. full: All available columns (15+ columns)
    """
    
    tenant_config = get_tenant_settings(tenant_id)
    
    # Base columns (always present)
    columns = [
        ('Item Name*', 'text', 'Required. Product name'),
        ('Selling Price*', 'number', 'Required. Final price to customer'),
        ('Stock Quantity*', 'number', 'Required. Current stock')
    ]
    
    # Add industry-specific columns
    if tenant_config.has_feature('product_variants'):
        # Clothing retail
        size_values = tenant_config.variant_config.get('size', {}).get('values', [])
        color_values = tenant_config.variant_config.get('color', {}).get('values', [])
        
        columns.extend([
            ('Size', 'dropdown', f'Options: {", ".join(size_values)}'),
            ('Color', 'dropdown', f'Options: {", ".join(color_values)}')
        ])
    
    if tenant_config.has_feature('batch_tracking'):
        # Pharmacy
        columns.extend([
            ('Batch Number', 'text', 'Lot/batch identifier'),
            ('MFG Date', 'date', 'Manufacturing date')
        ])
    
    if tenant_config.has_feature('expiry_tracking'):
        # Pharmacy / Food
        columns.append(
            ('Expiry Date', 'date', 'Product expiry date')
        )
    
    # Optional but recommended columns
    if template_type != 'minimal':
        columns.extend([
            ('MRP', 'number', 'Optional. Maximum Retail Price. If blank, uses Selling Price'),
            ('Barcode', 'text', 'Optional. If blank, system generates'),
            ('SKU', 'text', 'Optional. If blank, system generates'),
            ('Category', 'text', 'Optional. E.g., Jeans, T-Shirts, Shoes'),
            ('Reorder Point', 'number', 'Optional. Low stock alert threshold')
        ])
    
    # Generate Excel file with formulas
    wb = create_smart_excel(columns, tenant_config)
    return wb


def create_smart_excel(columns, config):
    """Create Excel file with:
    - Column headers with descriptions
    - Data validation (dropdowns)
    - Excel formulas for auto-calculation
    - Example rows
    - Instructions sheet
    """
    
    wb = openpyxl.Workbook()
    
    # Sheet 1: Data Entry
    ws = wb.active
    ws.title = "Import Data"
    
    # Header row with styling
    for col_idx, (name, type, description) in enumerate(columns, start=1):
        cell = ws.cell(row=1, column=col_idx)
        cell.value = name
        cell.comment = Comment(description, "BizBooks")
        cell.font = Font(bold=True, size=12)
        cell.fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
        cell.font = Font(color="FFFFFF", bold=True)
    
    # Add data validation for dropdowns
    size_col_idx = get_column_index(columns, 'Size')
    if size_col_idx:
        size_values = config.variant_config['size']['values']
        dv = DataValidation(type="list", formula1=f'"{",".join(size_values)}"')
        ws.add_data_validation(dv)
        dv.add(f'{get_column_letter(size_col_idx)}2:{get_column_letter(size_col_idx)}10000')
    
    color_col_idx = get_column_index(columns, 'Color')
    if color_col_idx:
        color_values = config.variant_config['color']['values']
        dv = DataValidation(type="list", formula1=f'"{",".join(color_values)}"')
        ws.add_data_validation(dv)
        dv.add(f'{get_column_letter(color_col_idx)}2:{get_column_letter(color_col_idx)}10000')
    
    # Add Excel formulas for auto-calculation
    # If MRP column exists, add Discount % formula
    mrp_col_idx = get_column_index(columns, 'MRP')
    selling_col_idx = get_column_index(columns, 'Selling Price*')
    
    if mrp_col_idx and selling_col_idx:
        # Add Discount % column
        discount_col = len(columns) + 1
        ws.cell(row=1, column=discount_col, value="Discount % (Auto)")
        ws.cell(row=1, column=discount_col).font = Font(bold=True, color="00B050")
        
        # Add formula for each row
        for row in range(2, 10000):
            mrp_cell = f'{get_column_letter(mrp_col_idx)}{row}'
            selling_cell = f'{get_column_letter(selling_col_idx)}{row}'
            discount_cell = ws.cell(row=row, column=discount_col)
            discount_cell.value = f'=IF(AND({mrp_cell}>0,{selling_cell}>0),ROUND(({mrp_cell}-{selling_cell})/{mrp_cell}*100,2),0)'
            discount_cell.number_format = '0.00"%"'
    
    # Add example rows
    add_example_rows(ws, columns, config)
    
    # Sheet 2: Instructions
    add_instructions_sheet(wb, columns)
    
    # Sheet 3: Size/Color Reference (if applicable)
    if config.has_feature('product_variants'):
        add_variant_reference_sheet(wb, config)
    
    return wb


def add_example_rows(ws, columns, config):
    """Add 3-5 example rows showing correct data format"""
    
    examples = []
    
    if config.has_feature('product_variants'):
        # Clothing retail examples
        examples = [
            ["Levi's 501 Jeans", "32", "Blue", "3999", "2499", "15", "8901234560001", "5"],
            ["Levi's 501 Jeans", "34", "Blue", "3999", "2499", "12", "8901234560002", "5"],
            ["Nike T-Shirt", "M", "Red", "1299", "799", "50", "", "10"],
        ]
    else:
        # Simple retail examples
        examples = [
            ["Laptop Dell Inspiron", "45999", "10"],
            ["Mouse Logitech M235", "599", "50"],
            ["Keyboard HP K1500", "899", "30"]
        ]
    
    for row_idx, example_data in enumerate(examples, start=2):
        for col_idx, value in enumerate(example_data, start=1):
            cell = ws.cell(row=row_idx, column=col_idx)
            cell.value = value
            cell.fill = PatternFill(start_color="E7E6E6", end_color="E7E6E6", fill_type="solid")


def add_instructions_sheet(wb, columns):
    """Add detailed instructions on separate sheet"""
    
    ws = wb.create_sheet("Instructions")
    
    instructions = [
        ["📋 HOW TO USE THIS TEMPLATE", ""],
        ["", ""],
        ["Step 1: Fill Required Columns (marked with *)", ""],
        ["  • Item Name: Product name", ""],
        ["  • Selling Price: Price to customer", ""],
        ["  • Stock Quantity: Current stock", ""],
        ["", ""],
        ["Step 2: Fill Optional Columns (if available)", ""],
        ["  • MRP: If blank, system uses Selling Price", ""],
        ["  • Barcode: If blank, system generates unique barcode", ""],
        ["  • SKU: If blank, system generates from item name", ""],
        ["  • Category: For grouping items", ""],
        ["", ""],
        ["Step 3: For Products with Variants (Size/Color)", ""],
        ["  • Same product name with different sizes/colors", ""],
        ["  • System automatically groups them", ""],
        ["  • Example:", ""],
        ["    Row 1: Levi's 501 | 32 | Blue", ""],
        ["    Row 2: Levi's 501 | 34 | Blue", ""],
        ["    Result: 1 parent product with 2 variants", ""],
        ["", ""],
        ["Step 4: Save and Upload", ""],
        ["  • Don't modify column headers", ""],
        ["  • Delete example rows (greyed out)", ""],
        ["  • Save as .xlsx or .xls", ""],
        ["  • Upload on BizBooks import page", ""],
        ["", ""],
        ["💡 Tips:", ""],
        ["  • Use Excel dropdowns for Size and Color", ""],
        ["  • Discount % is auto-calculated (don't edit)", ""],
        ["  • Barcode can be scanned or typed", ""],
        ["  • Keep backup of your original file", ""],
    ]
    
    for row_idx, (text, value) in enumerate(instructions, start=1):
        ws.cell(row=row_idx, column=1, value=text)
        if "Step" in text or "HOW TO" in text:
            ws.cell(row=row_idx, column=1).font = Font(bold=True, size=14, color="0000FF")
    
    ws.column_dimensions['A'].width = 50
```

---

### **Phase 2: Smart Import Processing**

```python
# utils/smart_excel_import.py

def import_with_smart_defaults(file_path, tenant_id):
    """
    Import Excel file with minimal data and auto-generate missing fields
    
    Process:
    1. Read Excel file
    2. Validate required columns
    3. Auto-generate missing data
    4. Detect and create variants
    5. Import with error handling
    """
    
    wb = openpyxl.load_workbook(file_path)
    ws = wb.active
    
    # Read headers
    headers = [cell.value for cell in ws[1]]
    
    # Validate required columns
    required = ['Item Name', 'Selling Price', 'Stock Quantity']
    missing = [col for col in required if col not in headers]
    if missing:
        return {'error': f'Missing required columns: {", ".join(missing)}'}
    
    # Get tenant configuration
    config = get_tenant_settings(tenant_id)
    
    # Track statistics
    stats = {
        'total_rows': 0,
        'items_created': 0,
        'variants_created': 0,
        'skus_generated': 0,
        'barcodes_generated': 0,
        'errors': []
    }
    
    # Read data rows
    items_data = []
    for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
        if not row[0]:  # Skip empty rows
            continue
        
        stats['total_rows'] += 1
        
        # Map row to dictionary
        row_data = dict(zip(headers, row))
        
        # Apply smart defaults
        row_data = apply_smart_defaults(row_data, config, stats)
        
        # Validate data
        is_valid, error = validate_row_data(row_data)
        if not is_valid:
            stats['errors'].append(f"Row {row_idx}: {error}")
            continue
        
        items_data.append(row_data)
    
    # Detect and group variants
    if config.has_feature('product_variants'):
        items_data = group_variants(items_data, config, stats)
    
    # Import to database
    import_results = bulk_create_items(items_data, tenant_id, stats)
    
    return {
        'success': True,
        'stats': stats,
        'preview': import_results[:10]  # Show first 10 items
    }


def apply_smart_defaults(row_data, config, stats):
    """Auto-generate missing fields with smart defaults"""
    
    # 1. Auto-generate SKU
    if not row_data.get('SKU'):
        base_sku = generate_sku_from_name(row_data['Item Name'])
        
        # Add variant suffix if applicable
        if row_data.get('Size') and row_data.get('Color'):
            size = row_data['Size'][:3].upper()
            color = row_data['Color'][:3].upper()
            row_data['SKU'] = f"{base_sku}-{color}-{size}"
        else:
            row_data['SKU'] = base_sku
        
        stats['skus_generated'] += 1
    
    # 2. Auto-generate Barcode
    if not row_data.get('Barcode'):
        row_data['Barcode'] = generate_unique_barcode(config.tenant_id)
        stats['barcodes_generated'] += 1
    
    # 3. Set MRP (if not provided, use Selling Price)
    if not row_data.get('MRP'):
        row_data['MRP'] = row_data['Selling Price']
    
    # 4. Calculate Discount %
    if row_data.get('MRP') and row_data.get('Selling Price'):
        mrp = float(row_data['MRP'])
        selling = float(row_data['Selling Price'])
        if mrp > 0 and selling > 0 and selling <= mrp:
            row_data['Discount %'] = round(((mrp - selling) / mrp) * 100, 2)
        else:
            row_data['Discount %'] = 0
    
    # 5. Set Reorder Point (smart default based on stock)
    if not row_data.get('Reorder Point'):
        stock = float(row_data.get('Stock Quantity', 0))
        if stock > 100:
            row_data['Reorder Point'] = int(stock * 0.2)  # 20% of stock
        elif stock > 10:
            row_data['Reorder Point'] = int(stock * 0.3)  # 30% of stock
        else:
            row_data['Reorder Point'] = 1  # Minimum 1
    
    # 6. Auto-detect Category (from name)
    if not row_data.get('Category'):
        row_data['Category'] = auto_detect_category(row_data['Item Name'])
    
    # 7. Set default Unit
    if not row_data.get('Unit'):
        row_data['Unit'] = 'pc'  # pieces
    
    return row_data


def generate_sku_from_name(item_name):
    """Generate SKU from item name
    
    Examples:
    "Levi's 501 Jeans" → "LEV501"
    "Nike Air Max" → "NIKEAIR"
    "Samsung Galaxy S21" → "SAMGAL"
    """
    
    # Remove special characters
    clean_name = re.sub(r'[^a-zA-Z0-9\s]', '', item_name)
    
    # Split into words
    words = clean_name.split()
    
    if len(words) >= 2:
        # Take first 3 letters of first word + first 3 of second
        sku = words[0][:3] + words[1][:3]
    else:
        # Take first 6 letters
        sku = clean_name[:6]
    
    # Uppercase
    sku = sku.upper()
    
    # Ensure uniqueness (add suffix if exists)
    base_sku = sku
    counter = 1
    while Item.query.filter_by(sku=sku).first():
        sku = f"{base_sku}{counter}"
        counter += 1
    
    return sku


def generate_unique_barcode(tenant_id):
    """Generate unique barcode for item
    
    Format: {tenant_id}{sequential_number}
    Example: Tenant 5, Item 123 → "5000000123"
    """
    
    # Get last barcode for this tenant
    last_item = Item.query.filter_by(tenant_id=tenant_id).order_by(Item.id.desc()).first()
    
    if last_item and last_item.barcode:
        try:
            # Extract number and increment
            last_num = int(last_item.barcode)
            new_barcode = str(last_num + 1).zfill(10)
        except:
            # Fallback: Random
            new_barcode = f"{tenant_id}{random.randint(10000000, 99999999)}"
    else:
        # First item for this tenant
        new_barcode = f"{tenant_id}{'0' * 9}1"
    
    return new_barcode


def group_variants(items_data, config, stats):
    """
    Group items with same name but different size/color into variants
    
    Input:
    [
        {"Item Name": "Levi's 501", "Size": "32", "Color": "Blue", ...},
        {"Item Name": "Levi's 501", "Size": "34", "Color": "Blue", ...},
        {"Item Name": "Nike T-Shirt", "Size": "M", "Color": "Red", ...}
    ]
    
    Output:
    [
        {
            "type": "parent",
            "name": "Levi's 501",
            "variants": [
                {"Size": "32", "Color": "Blue", ...},
                {"Size": "34", "Color": "Blue", ...}
            ]
        },
        {
            "type": "parent",
            "name": "Nike T-Shirt",
            "variants": [
                {"Size": "M", "Color": "Red", ...}
            ]
        }
    ]
    """
    
    # Group by item name
    grouped = {}
    for item in items_data:
        name = item['Item Name'].strip()
        
        if name not in grouped:
            grouped[name] = []
        
        grouped[name].append(item)
    
    # Convert to parent-variant structure
    result = []
    for name, items in grouped.items():
        # Check if items have size/color variations
        has_variants = any(item.get('Size') or item.get('Color') for item in items)
        
        if has_variants and len(items) > 1:
            # Create parent + variants
            result.append({
                'type': 'parent',
                'name': name,
                'sku': items[0]['SKU'].rsplit('-', 2)[0],  # Remove variant suffix
                'category': items[0].get('Category'),
                'variants': items
            })
            stats['variants_created'] += len(items)
        else:
            # Simple items (no variants)
            for item in items:
                result.append({
                    'type': 'simple',
                    **item
                })
    
    return result


def auto_detect_category(item_name):
    """Auto-detect category from item name using keywords"""
    
    categories = {
        'Jeans': ['jeans', 'denim', '501', '511', 'bootcut'],
        'T-Shirts': ['tshirt', 't-shirt', 'tee', 'polo'],
        'Shoes': ['shoes', 'sneakers', 'boots', 'sandals', 'slippers'],
        'Shirts': ['shirt', 'formal'],
        'Electronics': ['laptop', 'mobile', 'phone', 'tablet', 'computer'],
        'Accessories': ['belt', 'wallet', 'watch', 'bag', 'backpack']
    }
    
    item_lower = item_name.lower()
    
    for category, keywords in categories.items():
        if any(keyword in item_lower for keyword in keywords):
            return category
    
    return 'General'  # Default category
```

---

### **Phase 3: Import Preview & Validation**

```python
# routes/import.py

@admin_bp.route('/items/import-preview', methods=['POST'])
def import_preview():
    """Show preview of import before committing to database"""
    
    file = request.files['file']
    
    # Process file but don't save to database
    preview_data = process_import_preview(file, g.tenant.id)
    
    return render_template('admin/items/import_preview.html',
        preview=preview_data,
        stats=preview_data['stats']
    )
```

```html
<!-- templates/admin/items/import_preview.html -->

<div class="import-preview">
    <h2>📋 Import Preview - Review Before Importing</h2>
    
    <div class="import-stats">
        <div class="stat-box">
            <div class="stat-number">{{ stats.total_rows }}</div>
            <div class="stat-label">Rows Found</div>
        </div>
        
        <div class="stat-box success">
            <div class="stat-number">{{ stats.items_to_create }}</div>
            <div class="stat-label">Items to Create</div>
        </div>
        
        <div class="stat-box warning">
            <div class="stat-number">{{ stats.skus_generated }}</div>
            <div class="stat-label">SKUs Auto-Generated</div>
        </div>
        
        <div class="stat-box warning">
            <div class="stat-number">{{ stats.barcodes_generated }}</div>
            <div class="stat-label">Barcodes Auto-Generated</div>
        </div>
        
        {% if stats.variants_created > 0 %}
        <div class="stat-box info">
            <div class="stat-number">{{ stats.variants_created }}</div>
            <div class="stat-label">Variants Detected</div>
        </div>
        {% endif %}
        
        {% if stats.errors %}
        <div class="stat-box danger">
            <div class="stat-number">{{ stats.errors|length }}</div>
            <div class="stat-label">Errors Found</div>
        </div>
        {% endif %}
    </div>
    
    <!-- Show errors if any -->
    {% if stats.errors %}
    <div class="errors-section">
        <h3>⚠️ Errors Found - Please Fix and Re-upload</h3>
        <ul>
            {% for error in stats.errors[:10] %}
            <li>{{ error }}</li>
            {% endfor %}
            {% if stats.errors|length > 10 %}
            <li>... and {{ stats.errors|length - 10 }} more errors</li>
            {% endif %}
        </ul>
    </div>
    {% endif %}
    
    <!-- Preview first 10 items -->
    <div class="preview-table">
        <h3>📦 Preview (First 10 Items)</h3>
        <table>
            <thead>
                <tr>
                    <th>Item Name</th>
                    <th>SKU</th>
                    <th>Barcode</th>
                    <th>Size</th>
                    <th>Color</th>
                    <th>Price</th>
                    <th>Stock</th>
                    <th>Auto-Generated</th>
                </tr>
            </thead>
            <tbody>
                {% for item in preview[:10] %}
                <tr>
                    <td>{{ item.name }}</td>
                    <td>
                        {{ item.sku }}
                        {% if item.sku_generated %}<span class="badge">Auto</span>{% endif %}
                    </td>
                    <td>
                        {{ item.barcode }}
                        {% if item.barcode_generated %}<span class="badge">Auto</span>{% endif %}
                    </td>
                    <td>{{ item.size or '-' }}</td>
                    <td>{{ item.color or '-' }}</td>
                    <td>₹{{ item.selling_price }}</td>
                    <td>{{ item.stock }}</td>
                    <td>
                        {% if item.sku_generated or item.barcode_generated %}
                        <ul>
                            {% if item.sku_generated %}<li>SKU</li>{% endif %}
                            {% if item.barcode_generated %}<li>Barcode</li>{% endif %}
                        </ul>
                        {% else %}
                        -
                        {% endif %}
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
    
    <!-- Confirm import -->
    <form method="POST" action="/admin/items/confirm-import">
        <input type="hidden" name="import_session_id" value="{{ session_id }}">
        
        <div class="actions">
            {% if not stats.errors %}
            <button type="submit" class="btn-primary">
                ✅ Confirm & Import {{ stats.items_to_create }} Items
            </button>
            {% endif %}
            
            <a href="/admin/items/import" class="btn-secondary">
                ← Back to Upload
            </a>
        </div>
    </form>
</div>
```

---

## 📊 **Comparison: Current vs Smart Import**

| Aspect | Current System | Smart Import System |
|--------|----------------|---------------------|
| **Required Columns** | 10-15 columns | 3 columns minimum |
| **Data Prep Time** | 40+ hours | 30 minutes |
| **Error Rate** | High (missing fields) | Low (auto-generated) |
| **SKU Generation** | Manual | Automatic |
| **Barcode Generation** | Manual | Automatic |
| **Variant Detection** | Manual grouping | Automatic |
| **Category** | Must specify | Auto-detected |
| **Reorder Point** | Manual calculation | Smart default |
| **Discount %** | Manual calculation | Auto-calculated |
| **User Experience** | Frustrating 😰 | Smooth ✨ |

---

## 🎯 **Recommended Templates by Industry**

### **1. Clothing Retail (Minimal)**
```
Columns: 5
- Item Name*
- Size
- Color  
- Selling Price*
- Stock Quantity*

Example:
Levi's 501 Jeans | 32 | Blue | 2499 | 15
```

### **2. Electronics (Minimal)**
```
Columns: 4
- Item Name*
- Model
- Selling Price*
- Stock Quantity*

Example:
Samsung Galaxy | S21 | 65999 | 5
```

### **3. Pharmacy (Minimal)**
```
Columns: 5
- Item Name*
- Batch Number
- Expiry Date
- Selling Price*
- Stock Quantity*

Example:
Paracetamol 500mg | BATCH123 | 31-Dec-2025 | 25 | 500
```

### **4. General Retail (Minimal)**
```
Columns: 3
- Item Name*
- Selling Price*
- Stock Quantity*

Example:
Product A | 999 | 50
```

---

## 💡 **Smart Features**

### **1. Intelligent SKU Generation**
```python
"Levi's 501 Jeans Blue 32" → "LEV501-BLU-32"
"Nike Air Max Shoes" → "NIKEAIR"
"Samsung Galaxy S21" → "SAMGAL"
```

### **2. Sequential Barcode Generation**
```python
Tenant 5, First item → "5000000001"
Tenant 5, Second item → "5000000002"
...
Tenant 5, 1000th item → "5000001000"

(Unique per tenant, easy to remember)
```

### **3. Auto-Category Detection**
```python
Keywords:
"Jeans" in name → Category: Jeans
"T-Shirt" in name → Category: T-Shirts
"Laptop" in name → Category: Electronics
```

### **4. Smart Reorder Point**
```python
Stock > 100 → Reorder = 20% of stock
Stock 10-100 → Reorder = 30% of stock
Stock < 10 → Reorder = 1 (minimum)
```

---

## 🚀 **Implementation Priority**

### **Phase 1: Basic Smart Import (Week 1)**
- ✅ 3-column minimal template
- ✅ Auto-generate SKU
- ✅ Auto-generate Barcode
- ✅ Set smart defaults

### **Phase 2: Variant Detection (Week 2)**
- ✅ Group same-name items with different size/color
- ✅ Create parent-child relationships
- ✅ Generate variant SKUs

### **Phase 3: Industry Templates (Week 3)**
- ✅ Clothing template (Size/Color dropdowns)
- ✅ Pharmacy template (Batch/Expiry)
- ✅ Electronics template (Model/IMEI)

### **Phase 4: Preview & Validation (Week 4)**
- ✅ Show import preview before committing
- ✅ Error detection and reporting
- ✅ Confirm screen with statistics

---

## 📋 **Success Metrics**

| Metric | Target |
|--------|--------|
| Data prep time | 40 hours → 30 minutes (98% reduction) |
| Required columns | 15 → 3 (80% reduction) |
| Import errors | 20% → 2% (90% reduction) |
| User satisfaction | 6/10 → 9/10 |
| Onboarding time | 1 week → 1 day |

---

**File:** `DOCS_SMART_IMPORT_SYSTEM.md`  
**Status:** Ready for implementation  
**Priority:** High (critical for user onboarding)  
**Effort:** 3-4 weeks  
**Impact:** 10x easier inventory setup! 🚀

