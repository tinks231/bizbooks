# Purchase Bill UI Implementation Guide
## Smart Item Entry with Link/Create New Options

---

## 🎯 **FEATURE OVERVIEW:**

When adding items to a purchase bill:
1. Search for existing items
2. If found: Choose to "Link" or "Create New"
3. Auto-detect MRP changes and warn
4. Full shopkeeper control over decision

---

## 📋 **UI CHANGES NEEDED:**

### **1. Enhanced Item Row Structure**

**Current:**
```
[Search Item] [HSN] [Qty] [Unit] [Rate] [GST%] [Amount] [×]
```

**New:**
```
[Search Item or Create New]
  └─> When existing found:
      ┌──────────────────────────────────────┐
      │ 📦 Found: Levi Baggy Jeans          │
      │ SKU: LEVI-001 | MRP: ₹1,999         │
      │ Stock: 10 pcs                        │
      │                                       │
      │ ○ Link to existing (update stock)    │
      │   □ Update Selling: [₹1,799]         │
      │   □ Update MRP: [₹1,999]             │
      │                                       │
      │ ● Create as NEW item (separate)      │
      │   Name: [Levi Baggy Jeans (Dec 25)] │
      │   Selling: [₹1,899] *                │
      │   MRP: [₹2,199] *                    │
      │   SKU: [LEVI-002] (auto)             │
      │   Category: [Jeans ▼]                │
      │                                       │
      │ ⚠️ MRP changed! Create new recommended│
      └──────────────────────────────────────┘

[HSN] [Qty] [Unit] [Rate/Cost] [GST%] [Amount] [×]
```

---

## 🔧 **IMPLEMENTATION STEPS:**

### **Step 1: Add Hidden Fields to Item Row**

Add these hidden inputs to each `.item-row`:

```html
<!-- Existing -->
<input type="hidden" name="item_id[]" class="item-id">
<input type="hidden" name="item_name[]" class="item-name">

<!-- NEW: Item Action -->
<input type="hidden" name="item_action[]" class="item-action" value="link">
<!-- Values: "link", "create_new", or "new" (no existing item) -->

<!-- NEW: For Creating New Items -->
<input type="hidden" name="is_new_item[]" class="is-new-item" value="0">
<input type="hidden" name="new_item_sku[]" class="new-item-sku">
<input type="hidden" name="new_item_selling[]" class="new-item-selling">
<input type="hidden" name="new_item_mrp[]" class="new-item-mrp">
<input type="hidden" name="new_item_category[]" class="new-item-category">

<!-- NEW: For Updating Existing Items -->
<input type="hidden" name="update_selling_price[]" class="update-selling" value="0">
<input type="hidden" name="update_mrp[]" class="update-mrp" value="0">
<input type="hidden" name="updated_selling_value[]" class="updated-selling-value">
<input type="hidden" name="updated_mrp_value[]" class="updated-mrp-value">

<!-- NEW: Store existing item data for comparison -->
<input type="hidden" class="existing-cost" data-value="">
<input type="hidden" class="existing-selling" data-value="">
<input type="hidden" class="existing-mrp" data-value="">
<input type="hidden" class="existing-stock" data-value="">
```

---

### **Step 2: Add Item Action Choice Modal**

Add this modal after the form (before `</form>`):

```html
<!-- Item Action Choice Modal -->
<div class="modal fade" id="itemActionModal" tabindex="-1">
    <div class="modal-dialog modal-lg">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Item Found: <span id="modal_item_name"></span></h5>
                <button type="button" class="close" data-dismiss="modal">&times;</button>
            </div>
            <div class="modal-body">
                <!-- Current Item Info -->
                <div class="alert alert-info">
                    <strong>📦 Current Item Details:</strong><br>
                    SKU: <span id="modal_existing_sku"></span> | 
                    Barcode: <span id="modal_existing_barcode"></span><br>
                    Cost: ₹<span id="modal_existing_cost"></span> | 
                    Selling: ₹<span id="modal_existing_selling"></span> | 
                    MRP: ₹<span id="modal_existing_mrp"></span><br>
                    Current Stock: <span id="modal_existing_stock"></span> pcs
                </div>
                
                <!-- Auto-Detection Warning -->
                <div id="modal_mrp_warning" class="alert alert-warning" style="display:none;">
                    <strong>⚠️ MRP Changed!</strong><br>
                    Old MRP: ₹<span id="modal_old_mrp"></span> → 
                    New MRP: ₹<span id="modal_new_mrp"></span><br>
                    <span id="modal_stock_warning"></span>
                    <br><br>
                    <strong>Recommendation: Create as NEW item</strong><br>
                    <small>Reason: Old stock has different MRP printed on tags. Creating separate item prevents invoice confusion.</small>
                </div>
                
                <!-- Action Choice -->
                <div class="form-group">
                    <label><strong>How do you want to add this item?</strong></label>
                    
                    <!-- Option 1: Link to Existing -->
                    <div class="card mb-3" style="border: 2px solid #ddd;">
                        <div class="card-body">
                            <label>
                                <input type="radio" name="modal_item_action" value="link" 
                                       id="modal_action_link" checked>
                                <strong>Link to existing item</strong>
                            </label>
                            <p class="text-muted small mb-2">
                                ✅ Updates cost (weighted average)<br>
                                ✅ Adds to existing stock<br>
                                ✅ Same SKU, same barcode
                            </p>
                            
                            <div id="link_options" style="margin-left: 30px;">
                                <label>
                                    <input type="checkbox" id="modal_update_selling">
                                    Update Selling Price: ₹
                                    <input type="number" id="modal_new_selling_input" 
                                           step="0.01" style="width: 100px;" disabled>
                                </label>
                                <br>
                                <label>
                                    <input type="checkbox" id="modal_update_mrp">
                                    Update MRP: ₹
                                    <input type="number" id="modal_new_mrp_input" 
                                           step="0.01" style="width: 100px;" disabled>
                                </label>
                                <div id="modal_update_mrp_warning" class="text-danger small" 
                                     style="display:none; margin-left: 20px;">
                                    ⚠️ Warning: Old stock exists with different MRP printed!
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Option 2: Create New -->
                    <div class="card" style="border: 2px solid #ddd;">
                        <div class="card-body">
                            <label>
                                <input type="radio" name="modal_item_action" value="create_new"
                                       id="modal_action_create">
                                <strong>Create as NEW item</strong>
                            </label>
                            <p class="text-muted small mb-2">
                                ✅ New SKU (auto-generated)<br>
                                ✅ New barcode (auto-generated)<br>
                                ✅ Separate inventory entry
                            </p>
                            
                            <div id="create_new_options" style="margin-left: 30px; display:none;">
                                <div class="form-group">
                                    <label>New Item Name <span class="text-danger">*</span></label>
                                    <input type="text" id="modal_new_item_name" 
                                           class="form-control" placeholder="Item name">
                                </div>
                                <div class="row">
                                    <div class="col-md-6">
                                        <label>Cost Price (from bill)</label>
                                        <input type="number" id="modal_new_cost" 
                                               class="form-control" readonly>
                                    </div>
                                    <div class="col-md-6">
                                        <label>SKU (auto-generated)</label>
                                        <input type="text" id="modal_new_sku" 
                                               class="form-control" readonly>
                                    </div>
                                </div>
                                <div class="row mt-2">
                                    <div class="col-md-6">
                                        <label>Selling Price <span class="text-danger">*</span></label>
                                        <input type="number" id="modal_new_selling" 
                                               class="form-control" step="0.01" required>
                                    </div>
                                    <div class="col-md-6">
                                        <label>MRP <span class="text-danger">*</span></label>
                                        <input type="number" id="modal_new_mrp" 
                                               class="form-control" step="0.01" required>
                                    </div>
                                </div>
                                <div class="form-group mt-2">
                                    <label>Category</label>
                                    <select id="modal_new_category" class="form-control">
                                        <option value="">Select Category</option>
                                        {% for cat in categories %}
                                        <option value="{{ cat.id }}">{{ cat.name }}</option>
                                        {% endfor %}
                                    </select>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-dismiss="modal">Cancel</button>
                <button type="button" class="btn btn-primary" onclick="applyItemAction()">Apply</button>
            </div>
        </div>
    </div>
</div>
```

---

### **Step 3: JavaScript Functions**

Add these JavaScript functions:

```javascript
// Global variable to track which row we're working with
let currentItemRow = null;

// When item is selected from search dropdown
function selectItem(elem, id, name, hsn, unit, cost, selling, mrp, stock, sku, barcode) {
    const row = elem.closest('.item-row');
    currentItemRow = row;
    
    // Store existing item data
    row.querySelector('.existing-cost').dataset.value = cost;
    row.querySelector('.existing-selling').dataset.value = selling;
    row.querySelector('.existing-mrp').dataset.value = mrp;
    row.querySelector('.existing-stock').dataset.value = stock;
    
    // Get the rate (cost) entered by user
    const enteredRate = parseFloat(row.querySelector('.rate-input').value) || cost;
    
    // Check if this is truly a new purchase or just searching
    // If rate is already entered and different, might indicate price change
    const hasRateEntered = row.querySelector('.rate-input').value !== '';
    
    // Open modal to choose action
    showItemActionModal(id, name, cost, selling, mrp, stock, sku, barcode, enteredRate);
    
    // Hide dropdown
    document.getElementById(elem.closest('.autocomplete-dropdown').id).style.display = 'none';
}

// Show the item action choice modal
function showItemActionModal(itemId, itemName, cost, selling, mrp, stock, sku, barcode, newRate) {
    // Populate modal with item details
    document.getElementById('modal_item_name').textContent = itemName;
    document.getElementById('modal_existing_sku').textContent = sku || 'N/A';
    document.getElementById('modal_existing_barcode').textContent = barcode || 'N/A';
    document.getElementById('modal_existing_cost').textContent = parseFloat(cost).toFixed(2);
    document.getElementById('modal_existing_selling').textContent = parseFloat(selling).toFixed(2);
    document.getElementById('modal_existing_mrp').textContent = parseFloat(mrp).toFixed(2);
    document.getElementById('modal_existing_stock').textContent = stock;
    
    // Pre-fill new selling/MRP inputs
    document.getElementById('modal_new_selling_input').value = selling;
    document.getElementById('modal_new_mrp_input').value = mrp;
    
    // For create new mode
    document.getElementById('modal_new_item_name').value = itemName + ' (Dec 2025)';
    document.getElementById('modal_new_cost').value = newRate;
    document.getElementById('modal_new_selling').value = (newRate * 1.25).toFixed(2); // 25% markup suggestion
    document.getElementById('modal_new_mrp').value = (newRate * 1.40).toFixed(2); // 40% markup suggestion
    
    // Auto-generate SKU for new item
    const lastSku = sku || 'ITM-00000';
    const skuNum = parseInt(lastSku.split('-').pop()) + 1;
    document.getElementById('modal_new_sku').value = `ITM-${String(skuNum).padStart(5, '0')}`;
    
    // Check for MRP change
    const existingMrp = parseFloat(mrp);
    const newMrpEntered = parseFloat(document.getElementById('modal_new_mrp').value);
    
    // Reset warnings
    document.getElementById('modal_mrp_warning').style.display = 'none';
    document.getElementById('modal_update_mrp_warning').style.display = 'none';
    
    // Set default action
    document.getElementById('modal_action_link').checked = true;
    document.getElementById('link_options').style.display = 'block';
    document.getElementById('create_new_options').style.display = 'none';
    
    // Show modal
    $('#itemActionModal').modal('show');
}

// Toggle between link and create new options
document.addEventListener('DOMContentLoaded', function() {
    const linkRadio = document.getElementById('modal_action_link');
    const createRadio = document.getElementById('modal_action_create');
    
    if (linkRadio) {
        linkRadio.addEventListener('change', function() {
            document.getElementById('link_options').style.display = 'block';
            document.getElementById('create_new_options').style.display = 'none';
        });
    }
    
    if (createRadio) {
        createRadio.addEventListener('change', function() {
            document.getElementById('link_options').style.display = 'none';
            document.getElementById('create_new_options').style.display = 'block';
        });
    }
    
    // Enable/disable selling price input
    const updateSellingCheckbox = document.getElementById('modal_update_selling');
    if (updateSellingCheckbox) {
        updateSellingCheckbox.addEventListener('change', function() {
            document.getElementById('modal_new_selling_input').disabled = !this.checked;
        });
    }
    
    // Enable/disable MRP input and show warning
    const updateMrpCheckbox = document.getElementById('modal_update_mrp');
    if (updateMrpCheckbox) {
        updateMrpCheckbox.addEventListener('change', function() {
            document.getElementById('modal_new_mrp_input').disabled = !this.checked;
            const stock = parseFloat(document.getElementById('modal_existing_stock').textContent);
            if (this.checked && stock > 0) {
                document.getElementById('modal_update_mrp_warning').style.display = 'block';
            } else {
                document.getElementById('modal_update_mrp_warning').style.display = 'none';
            }
        });
    }
});

// Apply the selected action
function applyItemAction() {
    if (!currentItemRow) return;
    
    const action = document.querySelector('input[name="modal_item_action"]:checked').value;
    const itemId = document.getElementById('modal_existing_sku').textContent; // temporary, need actual ID
    const itemName = document.getElementById('modal_item_name').textContent;
    
    // Set hidden fields based on action
    if (action === 'link') {
        // Link to existing item
        currentItemRow.querySelector('.item-action').value = 'link';
        currentItemRow.querySelector('.is-new-item').value = '0';
        currentItemRow.querySelector('.item-name').value = itemName;
        
        // Check if updating prices
        const updateSelling = document.getElementById('modal_update_selling').checked;
        const updateMrp = document.getElementById('modal_update_mrp').checked;
        
        currentItemRow.querySelector('.update-selling').value = updateSelling ? '1' : '0';
        currentItemRow.querySelector('.update-mrp').value = updateMrp ? '1' : '0';
        
        if (updateSelling) {
            const newSelling = document.getElementById('modal_new_selling_input').value;
            currentItemRow.querySelector('.updated-selling-value').value = newSelling;
        }
        
        if (updateMrp) {
            const newMrp = document.getElementById('modal_new_mrp_input').value;
            currentItemRow.querySelector('.updated-mrp-value').value = newMrp;
        }
        
        // Show visual indicator
        currentItemRow.querySelector('.item-search').value = '🔗 ' + itemName + ' (linked)';
        currentItemRow.querySelector('.item-search').style.backgroundColor = '#e8f5e9';
        
    } else if (action === 'create_new') {
        // Create new item
        currentItemRow.querySelector('.item-action').value = 'create_new';
        currentItemRow.querySelector('.is-new-item').value = '1';
        
        const newName = document.getElementById('modal_new_item_name').value;
        const newSku = document.getElementById('modal_new_sku').value;
        const newSelling = document.getElementById('modal_new_selling').value;
        const newMrp = document.getElementById('modal_new_mrp').value;
        const newCategory = document.getElementById('modal_new_category').value;
        
        currentItemRow.querySelector('.item-name').value = newName;
        currentItemRow.querySelector('.new-item-sku').value = newSku;
        currentItemRow.querySelector('.new-item-selling').value = newSelling;
        currentItemRow.querySelector('.new-item-mrp').value = newMrp;
        currentItemRow.querySelector('.new-item-category').value = newCategory;
        
        // Show visual indicator
        currentItemRow.querySelector('.item-search').value = '🆕 ' + newName;
        currentItemRow.querySelector('.item-search').style.backgroundColor = '#fff3cd';
    }
    
    // Close modal
    $('#itemActionModal').modal('hide');
    currentItemRow = null;
}
```

---

## 📦 **BACKEND CHANGES NEEDED:**

Update `purchase_bills.py` create_bill() to handle new form fields:

```python
# Get line items with new fields
item_ids = request.form.getlist('item_id[]')
item_names = request.form.getlist('item_name[]')
item_actions = request.form.getlist('item_action[]')  # NEW
is_new_items = request.form.getlist('is_new_item[]')  # NEW

# NEW: For creating new items
new_item_skus = request.form.getlist('new_item_sku[]')
new_item_sellings = request.form.getlist('new_item_selling[]')
new_item_mrps = request.form.getlist('new_item_mrp[]')
new_item_categories = request.form.getlist('new_item_category[]')

# NEW: For updating existing items
update_selling_flags = request.form.getlist('update_selling_price[]')
update_mrp_flags = request.form.getlist('update_mrp[]')
updated_selling_values = request.form.getlist('updated_selling_value[]')
updated_mrp_values = request.form.getlist('updated_mrp_value[]')

for i in range(len(item_names)):
    line_item = PurchaseBillItem()
    # ... existing fields ...
    
    # NEW: Set new item flags and data
    line_item.is_new_item = (is_new_items[i] == '1')
    
    if line_item.is_new_item:
        line_item.sku = new_item_skus[i]
        line_item.selling_price = Decimal(new_item_sellings[i]) if new_item_sellings[i] else None
        line_item.mrp = Decimal(new_item_mrps[i]) if new_item_mrps[i] else None
        line_item.category_id = int(new_item_categories[i]) if new_item_categories[i] else None
    else:
        # Existing item - check if updating prices
        if update_selling_flags[i] == '1':
            line_item.selling_price = Decimal(updated_selling_values[i])
        if update_mrp_flags[i] == '1':
            line_item.mrp = Decimal(updated_mrp_values[i])
```

---

## ✅ **TESTING CHECKLIST:**

- [ ] Search existing item → Modal opens
- [ ] Choose "Link" → Updates cost only
- [ ] Choose "Link" + Update MRP → Shows warning if stock > 0
- [ ] Choose "Create New" → All fields required
- [ ] MRP change detection → Auto-suggests "Create New"
- [ ] Create bill with new item → Saves correctly
- [ ] Approve bill → Creates new item in inventory
- [ ] Approve bill → Updates existing item correctly

---

## 🚀 **NEXT STEPS:**

1. Update purchase_bills/create.html template
2. Add modal HTML
3. Update JavaScript functions
4. Test with various scenarios
5. Add barcode generation (separate feature)
6. Update edit.html template similarly

---

**STATUS: Ready for implementation** ✅

