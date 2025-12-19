# 🔄 Data Migration Strategy - Converting Existing Items to Variants

**Scenario:** User has 10K simple items → Wants to enable variant system

---

## 🎯 **The Challenge**

```
Before Configuration:
Item 1: "Levi's 501 Blue 32" (SKU: LEV501-B-32)
Item 2: "Levi's 501 Blue 34" (SKU: LEV501-B-34)
Item 3: "Levi's 501 Black 32" (SKU: LEV501-BK-32)

After Enabling Variants:
Parent: "Levi's 501"
├─ Variant: Blue / 32
├─ Variant: Blue / 34
└─ Variant: Black / 32

Problem: How to migrate 10K items without breaking anything?
```

---

## ✅ **Solution 1: Hybrid Model (Zero Migration)**

### **Approach:** Allow both simple items AND variant items to coexist

**Database Changes:**
```sql
-- Items table already has:
ALTER TABLE items ADD COLUMN IF NOT EXISTS is_variant_parent BOOLEAN DEFAULT FALSE;
ALTER TABLE items ADD COLUMN IF NOT EXISTS parent_item_id INTEGER REFERENCES items(id);
ALTER TABLE items ADD COLUMN IF NOT EXISTS variant_attributes JSONB DEFAULT '{}'::jsonb;

-- No need to modify existing items!
-- They remain as simple items (is_variant_parent = FALSE, parent_item_id = NULL)
```

**How It Works:**
```python
# When creating new items after configuration

# Old items (existing 10K items):
Item {
    id: 1,
    name: "Levi's 501 Blue 32",
    sku: "LEV501-B-32",
    is_variant_parent: False,
    parent_item_id: None,
    variant_attributes: {}
}

# New items (after enabling variants):
Parent Item {
    id: 10001,
    name: "Nike T-Shirt",
    sku: "NIKE-TS-001",
    is_variant_parent: True,
    parent_item_id: None
}

Variant Item {
    id: 10002,
    name: "Nike T-Shirt",
    sku: "NIKE-TS-001-RED-M",
    is_variant_parent: False,
    parent_item_id: 10001,
    variant_attributes: {"color": "Red", "size": "M"}
}
```

**Pros:**
- ✅ Zero migration needed
- ✅ Zero risk of data loss
- ✅ Existing items continue to work
- ✅ New items get variant benefits
- ✅ Can migrate gradually over time

**Cons:**
- ⚠️ Two data models temporarily
- ⚠️ Reports need to handle both types

---

## ⭐ **Solution 2: Smart Migration Wizard (Recommended Long-term)**

### **Step-by-Step Migration Tool**

### **Phase 1: Pattern Detection (AI-powered)**

```python
# routes/migration_wizard.py

from fuzzywuzzy import fuzz
import re

def detect_variant_patterns(items):
    """
    Analyze item names to detect variant patterns
    
    Example inputs:
    - "Levi's 501 Blue 32"
    - "Levi's 501 Blue 34"
    - "Levi's 501 Black 32"
    
    Output:
    {
        "base_name": "Levi's 501",
        "pattern": "{base} {color} {size}",
        "variants": [
            {"color": "Blue", "size": "32"},
            {"color": "Blue", "size": "34"},
            {"color": "Black", "size": "32"}
        ],
        "items": [item_ids],
        "confidence": 0.95
    }
    """
    
    groups = {}
    
    for item in items:
        # Try to extract patterns from name
        name_parts = item.name.split()
        
        # Look for size patterns (numbers: 28, 30, 32, XS, S, M, L, XL)
        size_pattern = r'\b(2[0-9]|3[0-9]|4[0-9]|XS|S|M|L|XL|XXL|XXXL)\b'
        size_match = re.search(size_pattern, item.name, re.IGNORECASE)
        
        # Look for color patterns (common color words)
        color_keywords = ['red', 'blue', 'black', 'white', 'green', 'yellow', 
                         'grey', 'gray', 'brown', 'pink', 'purple', 'orange']
        color_match = None
        for color in color_keywords:
            if color.lower() in item.name.lower():
                color_match = color
                break
        
        if size_match or color_match:
            # Extract base name (remove size and color)
            base_name = item.name
            if size_match:
                base_name = base_name.replace(size_match.group(), '').strip()
            if color_match:
                base_name = base_name.replace(color_match, '').strip()
            
            # Group similar items
            if base_name not in groups:
                groups[base_name] = {
                    'base_name': base_name,
                    'items': [],
                    'sizes': set(),
                    'colors': set()
                }
            
            groups[base_name]['items'].append(item)
            if size_match:
                groups[base_name]['sizes'].add(size_match.group())
            if color_match:
                groups[base_name]['colors'].add(color_match)
    
    # Filter: Only groups with 2+ items and multiple variants
    variant_groups = []
    for base_name, data in groups.items():
        if len(data['items']) >= 2 and (len(data['sizes']) > 1 or len(data['colors']) > 1):
            variant_groups.append({
                'base_name': base_name,
                'item_count': len(data['items']),
                'sizes': list(data['sizes']),
                'colors': list(data['colors']),
                'items': data['items'],
                'confidence': calculate_confidence(data)
            })
    
    return variant_groups


def calculate_confidence(group_data):
    """Calculate confidence score for pattern detection"""
    score = 0.0
    
    # More items = higher confidence
    if len(group_data['items']) >= 5:
        score += 0.3
    elif len(group_data['items']) >= 3:
        score += 0.2
    
    # Multiple sizes = likely variants
    if len(group_data['sizes']) >= 3:
        score += 0.4
    elif len(group_data['sizes']) >= 2:
        score += 0.2
    
    # Multiple colors = likely variants
    if len(group_data['colors']) >= 2:
        score += 0.3
    
    return min(score, 1.0)
```

### **Phase 2: User Review & Approval**

```html
<!-- templates/admin/migration_wizard.html -->

<div class="migration-wizard">
    <h1>🔄 Convert Items to Variants</h1>
    <p>We've analyzed your inventory and found patterns that could be converted to variants.</p>
    
    <div class="detected-groups">
        {% for group in variant_groups %}
        <div class="variant-group-card">
            <div class="group-header">
                <h3>{{ group.base_name }}</h3>
                <span class="confidence-badge {{ 'high' if group.confidence > 0.7 else 'medium' }}">
                    {{ (group.confidence * 100)|int }}% confidence
                </span>
            </div>
            
            <div class="group-stats">
                <span>📦 {{ group.item_count }} items</span>
                <span>📏 {{ group.sizes|length }} sizes</span>
                <span>🎨 {{ group.colors|length }} colors</span>
            </div>
            
            <div class="preview">
                <strong>Will become:</strong>
                <ul>
                    <li>1 Parent Product: "{{ group.base_name }}"</li>
                    <li>{{ group.item_count }} Variants</li>
                </ul>
                
                <details>
                    <summary>Preview items ({{ group.item_count }})</summary>
                    <table>
                        <thead>
                            <tr>
                                <th>Current Name</th>
                                <th>→</th>
                                <th>Will Become</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for item in group.items[:10] %}
                            <tr>
                                <td>{{ item.name }}</td>
                                <td>→</td>
                                <td>{{ group.base_name }} ({{ item.detected_color }} / {{ item.detected_size }})</td>
                            </tr>
                            {% endfor %}
                            {% if group.items|length > 10 %}
                            <tr>
                                <td colspan="3">... and {{ group.items|length - 10 }} more</td>
                            </tr>
                            {% endif %}
                        </tbody>
                    </table>
                </details>
            </div>
            
            <div class="actions">
                <button class="btn-convert" onclick="convertGroup('{{ group.id }}')">
                    ✅ Convert to Variants
                </button>
                <button class="btn-skip" onclick="skipGroup('{{ group.id }}')">
                    ⏭️ Skip This Group
                </button>
                <button class="btn-manual" onclick="manualMapping('{{ group.id }}')">
                    ✏️ Manual Mapping
                </button>
            </div>
        </div>
        {% endfor %}
    </div>
    
    <div class="wizard-footer">
        <button class="btn-convert-all">Convert All High-Confidence Groups</button>
        <button class="btn-cancel">Cancel & Keep Items As-Is</button>
    </div>
</div>
```

### **Phase 3: Conversion Execution**

```python
# routes/migration_wizard.py

def convert_group_to_variants(group_id, tenant_id):
    """
    Convert a group of simple items into parent + variants
    
    IMPORTANT: This preserves all data!
    - Stock levels maintained
    - Invoice history preserved
    - Barcodes kept
    """
    
    group = get_variant_group(group_id)
    
    # Start transaction
    db.session.begin_nested()
    
    try:
        # Step 1: Create parent item
        parent = Item(
            tenant_id=tenant_id,
            name=group['base_name'],
            sku=generate_sku(group['base_name']),
            is_variant_parent=True,
            category=group['items'][0].category,  # Copy from first item
            # Parent doesn't have stock/price (variants do)
            stock_quantity=0,
            selling_price=0
        )
        db.session.add(parent)
        db.session.flush()  # Get parent.id
        
        # Step 2: Convert existing items to variants
        for item in group['items']:
            # Extract variant attributes
            detected_size = detect_size_from_name(item.name)
            detected_color = detect_color_from_name(item.name)
            
            # Update item to be a variant
            item.parent_item_id = parent.id
            item.is_variant_parent = False
            item.variant_attributes = {
                'size': detected_size,
                'color': detected_color
            }
            
            # Update SKU to include variant suffix
            if detected_size and detected_color:
                item.variant_sku_suffix = f"{detected_color[:3].upper()}-{detected_size}"
                item.sku = f"{parent.sku}-{item.variant_sku_suffix}"
            
            # Keep everything else (stock, price, barcode, history)
            # NO CHANGES to: stock_quantity, selling_price, mrp, barcode
        
        # Step 3: Update parent stock (sum of all variants)
        parent.stock_quantity = sum(v.stock_quantity for v in group['items'])
        
        # Step 4: Commit transaction
        db.session.commit()
        
        return {
            'success': True,
            'parent_id': parent.id,
            'variants_created': len(group['items']),
            'message': f"Converted {len(group['items'])} items into variants of '{parent.name}'"
        }
        
    except Exception as e:
        db.session.rollback()
        return {
            'success': False,
            'error': str(e)
        }
```

### **Phase 4: Rollback Safety**

```python
def rollback_variant_conversion(parent_item_id):
    """
    Undo variant conversion if user changes mind
    
    Converts: Parent + Variants → Simple items again
    """
    
    parent = Item.query.get(parent_item_id)
    if not parent or not parent.is_variant_parent:
        return {'error': 'Not a parent item'}
    
    variants = Item.query.filter_by(parent_item_id=parent_item_id).all()
    
    # Revert variants to simple items
    for variant in variants:
        variant.parent_item_id = None
        variant.variant_attributes = {}
        variant.is_variant_parent = False
        # Keep original SKU or regenerate
    
    # Delete parent
    db.session.delete(parent)
    db.session.commit()
    
    return {'success': True, 'items_restored': len(variants)}
```

---

## 🎯 **Solution 3: Manual Bulk Update Tool**

### **For items that don't match patterns**

```python
# routes/bulk_variant_update.py

@admin_bp.route('/items/bulk-add-variants', methods=['GET', 'POST'])
def bulk_add_variants():
    """
    Manual tool: Select items → Add variants
    
    Example:
    User selects 50 "Nike T-Shirt" items
    → System creates 1 parent + converts 50 to variants
    """
    
    if request.method == 'POST':
        selected_item_ids = request.form.getlist('item_ids')
        base_name = request.form.get('base_name')
        
        # Create parent + convert selected items
        ...
```

---

## 📋 **Migration Workflow Summary**

```
Step 1: User Enables Variant System
    ↓
Step 2: System Analyzes Existing Items
    ├─ AI detects patterns
    ├─ Groups similar items
    └─ Calculates confidence scores
    ↓
Step 3: User Reviews Suggestions
    ├─ See preview of conversions
    ├─ Approve/Skip/Edit each group
    └─ Can do manual mapping
    ↓
Step 4: System Converts Items
    ├─ Creates parent items
    ├─ Links existing items as variants
    ├─ Preserves all stock/history/invoices
    └─ Updates SKUs (optional)
    ↓
Step 5: Gradual Migration
    ├─ Can convert in batches
    ├─ Can rollback if needed
    └─ New items use variant system automatically
```

---

## ⚠️ **Critical Safety Measures**

### **1. Preserve Invoice History**

```python
# When converting items to variants, DON'T modify invoice_items table
# Old invoices still reference old item_id (now a variant)
# This is FINE because:

invoice_items table:
├─ invoice_id: 123
├─ item_id: 456  ← This item is now a variant (no problem!)
├─ quantity: 2
└─ price: 1500

# The item still exists, just has parent_item_id now
# All historical data intact! ✅
```

### **2. Barcode Preservation**

```python
# NEVER change barcodes during migration
# Each variant keeps its original barcode

Before:
Item "Levi's 501 Blue 32" → Barcode: 890123456

After:
Variant "Levi's 501 - Blue - 32" → Barcode: 890123456 (SAME!)

# Barcode scanning still works! ✅
```

### **3. Stock Tracking**

```python
# Stock remains at variant level (not parent)

Parent Item "Levi's 501":
├─ stock_quantity: 0 (or sum of variants for display)

Variant "Levi's 501 - Blue - 32":
├─ stock_quantity: 15 (ACTUAL stock)

Variant "Levi's 501 - Blue - 34":
├─ stock_quantity: 8 (ACTUAL stock)
```

---

## 🎯 **Recommended Migration Path**

### **Phase 1: Enable Hybrid Model**
- ✅ Allow both simple items and variant items
- ✅ New items can use variants
- ✅ Existing items stay as-is
- **Timeline:** Immediate (no migration needed)

### **Phase 2: Build Migration Wizard**
- ✅ AI pattern detection
- ✅ User review interface
- ✅ Gradual conversion
- **Timeline:** 1-2 weeks development

### **Phase 3: Migrate High-Value Items First**
- ✅ Convert best-selling products first
- ✅ Test with 100-200 items
- ✅ Verify reports/invoices still work
- **Timeline:** 1 week testing

### **Phase 4: Full Migration (Optional)**
- ✅ Convert remaining items in batches
- ✅ 1000 items at a time
- ✅ Monitor for issues
- **Timeline:** 2-3 weeks (gradual)

---

## 💡 **Best Practices**

1. **Start Small:** Convert 10 items first, verify everything works
2. **Backup Database:** Before any bulk conversion
3. **Test in Staging:** Use Mumbai DB for testing
4. **Gradual Rollout:** Don't convert all 10K items at once
5. **User Training:** Show cousin how new variant system works
6. **Monitor Reports:** Ensure sales reports still accurate
7. **Keep Rollback Option:** Can undo conversions if needed

---

## 🚀 **When to Use Each Approach**

| Scenario | Recommended Solution | Why |
|----------|---------------------|-----|
| Just enabled variants | **Hybrid Model** | Zero risk, works immediately |
| Clean naming patterns | **Migration Wizard** | AI can detect patterns |
| Messy data | **Manual Tool** | Human oversight needed |
| Small inventory (<1K) | **Migration Wizard** | Quick to convert |
| Large inventory (>5K) | **Gradual Hybrid** | Too risky to convert all |
| Customer unsure | **Hybrid Model** | Can decide later |

---

**File:** `DOCS_DATA_MIGRATION_STRATEGY.md`  
**Status:** Ready for reference  
**Next Step:** Choose Hybrid Model for safety, build Wizard later if needed

