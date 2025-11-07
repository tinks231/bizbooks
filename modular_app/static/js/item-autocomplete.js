/**
 * Reusable Item Autocomplete Module
 * 
 * Usage:
 * 1. Load items in template: const items = {{ items|tojson }};
 * 2. Include this script
 * 3. Call setupItemAutocomplete(inputElement, rowId, options)
 */

/**
 * Search and filter items for autocomplete
 * @param {HTMLInputElement} input - The search input element
 * @param {string} rowId - The row identifier
 * @param {Array} itemsList - Array of item objects
 * @param {Object} options - Configuration options
 */
function searchItems(input, rowId, itemsList, options = {}) {
    const defaults = {
        priceField: 'selling_price',  // 'selling_price' or 'cost_price'
        maxResults: 10,
        onSelect: null  // Custom callback after selection
    };
    
    const config = { ...defaults, ...options };
    
    const searchTerm = input.value.toLowerCase().trim();
    const dropdown = document.getElementById(`dropdown_${rowId}`);
    
    if (!dropdown) {
        console.error('❌ Dropdown not found for row:', rowId);
        return;
    }
    
    if (!searchTerm) {
        dropdown.style.display = 'none';
        return;
    }
    
    // Filter items based on search term (name, code, or HSN)
    const filteredItems = itemsList.filter(item => 
        item.name.toLowerCase().includes(searchTerm) ||
        (item.item_code && item.item_code.toLowerCase().includes(searchTerm)) ||
        (item.sku && item.sku.toLowerCase().includes(searchTerm)) ||
        (item.hsn_code && item.hsn_code.toLowerCase().includes(searchTerm))
    );
    
    if (filteredItems.length === 0) {
        dropdown.innerHTML = `
            <div class="autocomplete-no-results" style="padding: 12px; color: #666; text-align: center; font-size: 14px;">
                No items found. You can type manually or add items to inventory first.
            </div>
        `;
        dropdown.style.display = 'block';
        return;
    }
    
    // Build dropdown HTML using data attributes (safer than inline onclick)
    let html = '';
    filteredItems.slice(0, config.maxResults).forEach(item => {
        // Escape for HTML display
        const escapedName = escapeHtml(item.name);
        const escapedCode = escapeHtml(item.item_code || item.sku || '');
        const escapedHsn = escapeHtml(item.hsn_code || '');
        const price = item[config.priceField] || 0;
        
        html += `
            <div class="autocomplete-item" 
                 data-row-id="${rowId}"
                 data-item-id="${item.id}"
                 data-item-name="${escapedName}"
                 data-item-code="${escapedCode}"
                 data-item-price="${price}"
                 data-item-hsn="${escapedHsn}"
                 data-item-unit="${escapeHtml(item.unit || 'pcs')}"
                 data-item-tax="${escapeHtml(item.tax_preference || 'GST@18%')}"
                 style="padding: 10px 12px; cursor: pointer; border-bottom: 1px solid #e9ecef; transition: all 0.2s ease;">
                <div style="font-weight: 600; color: #333; margin-bottom: 4px;">${escapedName}</div>
                <div style="display: flex; gap: 15px; font-size: 12px; color: #666;">
                    <span>💰 ₹${price}</span>
                    ${escapedCode ? `<span>📦 ${escapedCode}</span>` : ''}
                    ${escapedHsn ? `<span>📋 HSN: ${escapedHsn}</span>` : ''}
                </div>
            </div>
        `;
    });
    
    dropdown.innerHTML = html;
    
    // Add hover effect CSS if not already added
    if (!document.getElementById('autocomplete-hover-style')) {
        const style = document.createElement('style');
        style.id = 'autocomplete-hover-style';
        style.textContent = `
            .autocomplete-item:hover {
                background-color: #e3f2fd !important;
                border-left: 3px solid #007bff !important;
            }
        `;
        document.head.appendChild(style);
    }
    
    // Add click event listeners to all autocomplete items
    dropdown.querySelectorAll('.autocomplete-item').forEach(itemDiv => {
        itemDiv.addEventListener('click', function() {
            selectItemFromDropdown(this, config);
        });
    });
    
    dropdown.style.display = 'block';
}

/**
 * Handle item selection from dropdown
 */
function selectItemFromDropdown(itemDiv, config) {
    const rowId = itemDiv.dataset.rowId;
    const itemId = itemDiv.dataset.itemId;
    const itemName = itemDiv.dataset.itemName;
    const itemCode = itemDiv.dataset.itemCode;
    const price = itemDiv.dataset.itemPrice;
    const hsn = itemDiv.dataset.itemHsn;
    const unit = itemDiv.dataset.itemUnit;
    const tax = itemDiv.dataset.itemTax;
    
    console.log('🔍 Selecting item:', { rowId, itemId, itemName, price, hsn });
    
    const row = document.getElementById(`row_${rowId}`);
    if (!row) {
        console.error('❌ Row not found:', rowId);
        return;
    }
    
    // Set item name
    const itemInput = document.getElementById(`item_search_${rowId}`);
    if (itemInput) {
        itemInput.value = itemName;
    }
    
    // Set hidden item ID
    const itemIdInput = document.getElementById(`item_id_${rowId}`);
    if (itemIdInput) {
        itemIdInput.value = itemId;
    }
    
    // Set item name in hidden input (for form submission)
    const itemNameInput = row.querySelector('input[name="item_name[]"]');
    if (itemNameInput) {
        itemNameInput.value = itemName;
    }
    
    // Set HSN code
    const hsnInput = row.querySelector('input[name="hsn_code[]"]');
    if (hsnInput && hsn) {
        hsnInput.value = hsn;
    }
    
    // Set rate
    const rateInput = document.getElementById(`rate_${rowId}`) || row.querySelector('input[name="rate[]"]');
    if (rateInput) {
        rateInput.value = price || 0;
    }
    
    // Set unit
    const unitInput = row.querySelector('input[name="unit[]"]');
    if (unitInput && unit) {
        unitInput.value = unit;
    }
    
    // Extract GST rate from tax preference
    if (tax) {
        const gstInput = row.querySelector('input[name="gst_rate[]"]');
        if (gstInput) {
            const gstMatch = tax.match(/(\d+(?:\.\d+)?)/);
            if (gstMatch) {
                gstInput.value = gstMatch[1];
            }
        }
    }
    
    // Hide dropdown
    const dropdown = document.getElementById(`dropdown_${rowId}`);
    if (dropdown) {
        dropdown.style.display = 'none';
    }
    
    // Call custom callback if provided
    if (config.onSelect && typeof config.onSelect === 'function') {
        config.onSelect({
            rowId,
            itemId,
            itemName,
            itemCode,
            price,
            hsn,
            unit,
            tax
        });
    }
    
    // Trigger calculation if calculateRow function exists
    if (typeof calculateRow === 'function') {
        calculateRow(rowId);
    }
    
    console.log('✅ Item selected successfully');
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    if (!text) return '';
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.toString().replace(/[&<>"']/g, m => map[m]);
}

/**
 * Setup autocomplete for an input element
 * @param {string} inputId - ID of the input element
 * @param {string} rowId - Row identifier
 * @param {Array} itemsList - Array of item objects
 * @param {Object} options - Configuration options
 */
function setupItemAutocomplete(inputId, rowId, itemsList, options = {}) {
    const input = document.getElementById(inputId);
    if (!input) {
        console.error('❌ Input not found:', inputId);
        return;
    }
    
    input.addEventListener('input', function() {
        searchItems(this, rowId, itemsList, options);
    });
    
    // Hide dropdown when clicking outside
    document.addEventListener('click', function(e) {
        const dropdown = document.getElementById(`dropdown_${rowId}`);
        if (dropdown && !input.contains(e.target) && !dropdown.contains(e.target)) {
            dropdown.style.display = 'none';
        }
    });
}

