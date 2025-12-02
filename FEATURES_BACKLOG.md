# 📋 Features Backlog - To Implement After Dev Setup

**⚠️ DO NOT implement until local development environment is working!**

**Priority:** Implement AFTER security fixes are complete.

---

## 1. 💰 MRP (Maximum Retail Price) Field

### Current State
- Items have: `buying_price`, `selling_price`, `gst_rate`
- No MRP field

### Requirement
- Add MRP field to inventory
- Display MRP on labels/invoices
- Used for calculating discount % automatically

### Implementation

```python
# Database Migration
@app.route('/migrate/add-mrp-field')
def add_mrp_field():
    try:
        with db.engine.begin() as conn:
            # Add MRP column to items table
            conn.execute(text("""
                ALTER TABLE items 
                ADD COLUMN IF NOT EXISTS mrp NUMERIC(10, 2) DEFAULT 0;
            """))
        
        return jsonify({
            'status': 'success',
            'message': '✅ MRP field added to items table',
            'next_steps': [
                '1. Go to Inventory → Edit item',
                '2. Set MRP value',
                '3. MRP will show on invoices'
            ]
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'❌ Error: {str(e)}'
        })
```

```python
# Update Item Model (models/item.py)
class Item(db.Model):
    __tablename__ = 'items'
    
    id = db.Column(db.Integer, primary_key=True)
    # ... existing fields ...
    mrp = db.Column(db.Numeric(10, 2), default=0)  # NEW
    buying_price = db.Column(db.Numeric(10, 2), default=0)
    selling_price = db.Column(db.Numeric(10, 2), default=0)
```

```html
<!-- Update Item Form (templates/admin/items.html) -->
<div class="form-group">
    <label>MRP (Maximum Retail Price)</label>
    <input type="number" step="0.01" class="form-control" 
           name="mrp" id="mrp" placeholder="999.00">
    <small class="text-muted">Price printed on product package</small>
</div>

<div class="form-group">
    <label>Selling Price</label>
    <input type="number" step="0.01" class="form-control" 
           name="selling_price" id="selling_price" placeholder="899.00">
    <small class="text-muted">Actual selling price (after discount)</small>
</div>

<div class="form-group">
    <label>Discount %</label>
    <input type="number" step="0.01" class="form-control" 
           id="discount_percent" readonly>
    <small class="text-muted">Auto-calculated: ((MRP - Selling) / MRP) × 100</small>
</div>
```

### Use Cases
1. **Product Labels:** Show MRP as "M.R.P: ₹999"
2. **Invoices:** Display both MRP and selling price
3. **Discount Calculation:** Auto-calculate discount %
4. **Customer Transparency:** Legal requirement in India

### Estimated Time
⏱️ **4-6 hours**
- 2 hours: Database + Model
- 2 hours: UI updates
- 1-2 hours: Testing

---

## 2. 📊 Discount Percentage on Invoice

### Current State
- Invoice has flat discount: "Discount: ₹100"
- Applied to total invoice amount

### Requirement
- Change to **percentage-based discount**
- Apply per-item OR on total invoice
- Show: "Discount (10%): ₹100"
- Automatically calculate discount amount from %

### Implementation Options

#### Option A: Invoice-Level Discount % (Simpler)

```html
<!-- Invoice Form -->
<div class="form-row">
    <div class="col-md-6">
        <label>Discount Type</label>
        <select name="discount_type" id="discount_type" class="form-control">
            <option value="percentage">Percentage (%)</option>
            <option value="flat">Flat Amount (₹)</option>
        </select>
    </div>
    <div class="col-md-6">
        <label>Discount Value</label>
        <input type="number" step="0.01" class="form-control" 
               name="discount_value" id="discount_value" placeholder="10">
        <small class="text-muted" id="discount_hint">
            Enter percentage (e.g., 10 for 10%)
        </small>
    </div>
</div>

<div class="invoice-summary">
    <div>Subtotal: ₹<span id="subtotal">1000.00</span></div>
    <div>Discount (<span id="discount_percent">10</span>%): 
         ₹<span id="discount_amount">100.00</span>
    </div>
    <div>GST: ₹<span id="gst_amount">162.00</span></div>
    <div><strong>Total: ₹<span id="total">1062.00</span></strong></div>
</div>
```

```javascript
// Auto-calculate discount
function calculateDiscount() {
    const subtotal = parseFloat($('#subtotal').text());
    const discountType = $('#discount_type').val();
    const discountValue = parseFloat($('#discount_value').val()) || 0;
    
    let discountAmount = 0;
    
    if (discountType === 'percentage') {
        discountAmount = (subtotal * discountValue) / 100;
        $('#discount_hint').text(`${discountValue}% of ₹${subtotal.toFixed(2)}`);
    } else {
        discountAmount = discountValue;
        $('#discount_hint').text('Flat discount amount');
    }
    
    $('#discount_amount').text(discountAmount.toFixed(2));
    
    // Recalculate total
    const afterDiscount = subtotal - discountAmount;
    const gst = afterDiscount * 0.18; // Example GST rate
    const total = afterDiscount + gst;
    
    $('#gst_amount').text(gst.toFixed(2));
    $('#total').text(total.toFixed(2));
}

$('#discount_type, #discount_value').on('change keyup', calculateDiscount);
```

#### Option B: Item-Level Discount % (Advanced)

```html
<!-- Each invoice item row -->
<tr>
    <td>Bajaj Fan</td>
    <td>1</td>
    <td>₹2,500</td>
    <td>
        <input type="number" step="0.01" class="form-control item-discount" 
               placeholder="0" style="width: 80px;"> %
    </td>
    <td>₹2,500</td> <!-- After discount -->
</tr>
```

### Database Changes

```python
# For Invoice-Level Discount (Option A):
# Add to sales_invoices table:
discount_type = db.Column(db.String(20), default='percentage')  # 'percentage' or 'flat'
discount_value = db.Column(db.Numeric(10, 2), default=0)  # 10 (for 10%) or 100 (for ₹100)
discount_amount = db.Column(db.Numeric(10, 2), default=0)  # Calculated amount

# For Item-Level Discount (Option B):
# Add to sales_invoice_items table:
discount_percent = db.Column(db.Numeric(5, 2), default=0)  # Per item discount %
```

### Recommendation

**Start with Option A (Invoice-Level)** - simpler, covers 90% of use cases.
Can add Option B later if needed.

### Estimated Time
⏱️ **6-8 hours**
- 2 hours: Database changes
- 3 hours: UI + JavaScript
- 2 hours: Backend calculation logic
- 1 hour: Testing

---

## 3. 📦 Barcode System (COMPLETE SOLUTION)

### Overview

Complete barcode system with:
1. ✅ Barcode generation for items
2. ✅ Printable barcode labels
3. ✅ Mobile scanner portal (camera-based)
4. ✅ USB scanner support (future)
5. ✅ Integration with invoicing

### Phase 1: Barcode Generation & Storage

```python
# Database Migration
@app.route('/migrate/add-barcode-field')
def add_barcode_field():
    try:
        with db.engine.begin() as conn:
            # Add barcode column
            conn.execute(text("""
                ALTER TABLE items 
                ADD COLUMN IF NOT EXISTS barcode VARCHAR(50) UNIQUE;
            """))
            
            # Create index for fast lookup
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_items_barcode 
                ON items(barcode);
            """))
        
        return jsonify({
            'status': 'success',
            'message': '✅ Barcode field added!'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'❌ Error: {str(e)}'
        })
```

```python
# Update Item Model
class Item(db.Model):
    __tablename__ = 'items'
    
    id = db.Column(db.Integer, primary_key=True)
    # ... existing fields ...
    barcode = db.Column(db.String(50), unique=True, nullable=True)  # NEW
```

### Phase 2: Barcode Generation

```python
# requirements.txt - add these:
python-barcode==0.15.1
Pillow==10.0.0  # Already installed
```

```python
# routes/items.py - Add bulk barcode generation
import barcode
from barcode.writer import ImageWriter
import io
import base64

@app.route('/admin/items/generate-barcodes', methods=['POST'])
@require_tenant
def generate_barcodes():
    """Generate barcodes for all items without barcodes"""
    tenant_id = get_current_tenant_id()
    
    items_without_barcode = Item.query.filter_by(
        tenant_id=tenant_id,
        barcode=None
    ).all()
    
    generated_count = 0
    
    for item in items_without_barcode:
        # Generate unique barcode based on item ID
        # Format: 2[tenant_id][item_id] (EAN13 format)
        barcode_value = f"2{tenant_id:04d}{item.id:06d}"
        
        # Ensure it's valid EAN13 (12 digits + check digit)
        item.barcode = barcode_value
        generated_count += 1
    
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': f'✅ Generated {generated_count} barcodes!',
        'count': generated_count
    })

@app.route('/admin/items/barcode/<int:item_id>')
@require_tenant
def get_item_barcode_image(item_id):
    """Generate barcode image for item"""
    item = Item.query.get_or_404(item_id)
    
    if not item.barcode:
        return "No barcode", 404
    
    # Generate barcode image
    ean = barcode.get('ean13', item.barcode, writer=ImageWriter())
    
    # Save to BytesIO
    buffer = io.BytesIO()
    ean.write(buffer)
    buffer.seek(0)
    
    return send_file(buffer, mimetype='image/png')
```

### Phase 3: Printable Barcode Labels

```html
<!-- templates/admin/items/barcode_labels.html -->
<!DOCTYPE html>
<html>
<head>
    <title>Print Barcode Labels</title>
    <style>
        @media print {
            .no-print { display: none; }
            @page { margin: 0; }
        }
        
        .label-sheet {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10mm;
            padding: 10mm;
        }
        
        .barcode-label {
            width: 60mm;
            height: 40mm;
            border: 1px dashed #ccc;
            padding: 3mm;
            text-align: center;
            page-break-inside: avoid;
        }
        
        .barcode-label img {
            max-width: 100%;
            height: auto;
        }
        
        .item-name {
            font-size: 10pt;
            font-weight: bold;
            margin: 2mm 0;
        }
        
        .item-price {
            font-size: 12pt;
            color: #000;
        }
        
        .mrp {
            font-size: 8pt;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="no-print">
        <button onclick="window.print()">🖨️ Print Labels</button>
        <button onclick="window.close()">❌ Close</button>
    </div>
    
    <div class="label-sheet">
        {% for item in items %}
        <div class="barcode-label">
            <div class="item-name">{{ item.name }}</div>
            <img src="{{ url_for('get_item_barcode_image', item_id=item.id) }}" 
                 alt="Barcode">
            <div class="item-price">₹{{ item.selling_price }}</div>
            {% if item.mrp %}
            <div class="mrp">MRP: ₹{{ item.mrp }}</div>
            {% endif %}
        </div>
        {% endfor %}
    </div>
</body>
</html>
```

### Phase 4: Mobile Scanner Portal

```python
# routes/scanner_portal.py (NEW FILE)
from flask import Blueprint, render_template, request, jsonify
import secrets
from datetime import datetime, timedelta

scanner_bp = Blueprint('scanner', __name__, url_prefix='/admin/scanner')

# In-memory session store (or use Redis for production)
active_scanner_sessions = {}

@scanner_bp.route('/create-session', methods=['POST'])
@require_tenant
def create_scanner_session():
    """Create a scanner session for mobile device"""
    tenant_id = get_current_tenant_id()
    invoice_id = request.json.get('invoice_id')
    
    session_id = secrets.token_urlsafe(16)
    
    active_scanner_sessions[session_id] = {
        'tenant_id': tenant_id,
        'invoice_id': invoice_id,
        'scanned_items': [],
        'created_at': datetime.utcnow(),
        'expires_at': datetime.utcnow() + timedelta(hours=1)
    }
    
    # Clean old sessions (older than 1 hour)
    cleanup_expired_sessions()
    
    return jsonify({
        'status': 'success',
        'session_id': session_id,
        'qr_url': f"{request.host_url}admin/scanner-portal/{session_id}",
        'expires_in': 3600
    })

@scanner_bp.route('/scanner-portal/<session_id>')
def scanner_portal(session_id):
    """Mobile scanner interface (camera-based scanning)"""
    if session_id not in active_scanner_sessions:
        return "Session expired or invalid", 404
    
    session = active_scanner_sessions[session_id]
    
    # Check expiration
    if datetime.utcnow() > session['expires_at']:
        del active_scanner_sessions[session_id]
        return "Session expired", 404
    
    return render_template('scanner_portal.html',
                         session_id=session_id,
                         session=session)

@scanner_bp.route('/scan', methods=['POST'])
def scan_barcode():
    """Mobile device posts scanned barcode here"""
    session_id = request.json.get('session_id')
    barcode = request.json.get('barcode')
    
    if session_id not in active_scanner_sessions:
        return jsonify({'success': False, 'error': 'Invalid session'}), 404
    
    session = active_scanner_sessions[session_id]
    
    # Search item by barcode
    item = Item.query.filter_by(
        barcode=barcode,
        tenant_id=session['tenant_id']
    ).first()
    
    if item:
        # Add to session queue
        session['scanned_items'].append({
            'item_id': item.id,
            'name': item.name,
            'barcode': barcode,
            'price': float(item.selling_price),
            'scanned_at': datetime.utcnow().isoformat()
        })
        
        return jsonify({
            'success': True,
            'item': {
                'id': item.id,
                'name': item.name,
                'price': float(item.selling_price)
            }
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Item not found'
        }), 404

@scanner_bp.route('/poll', methods=['POST'])
def poll_scanned_items():
    """Laptop polls for newly scanned items"""
    session_id = request.json.get('session_id')
    
    if session_id not in active_scanner_sessions:
        return jsonify({'items': []})
    
    session = active_scanner_sessions[session_id]
    
    # Get all items and clear queue
    items = session['scanned_items']
    session['scanned_items'] = []
    
    return jsonify({'items': items})

def cleanup_expired_sessions():
    """Remove sessions older than 1 hour"""
    now = datetime.utcnow()
    expired = [sid for sid, sess in active_scanner_sessions.items() 
               if now > sess['expires_at']]
    for sid in expired:
        del active_scanner_sessions[sid]
```

### Phase 5: Invoice Integration

```javascript
// In create_invoice.html - Add scanner button
<button type="button" class="btn btn-primary" onclick="openScannerPortal()">
    📱 Scan with Mobile
</button>

<script>
let scannerSessionId = null;
let pollingInterval = null;

function openScannerPortal() {
    // Create scanner session
    fetch('/admin/scanner/create-session', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            invoice_id: currentInvoiceId || 'new'
        })
    })
    .then(r => r.json())
    .then(data => {
        scannerSessionId = data.session_id;
        
        // Show QR code modal
        $('#scannerQRCode').html(
            `<img src="https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(data.qr_url)}">`
        );
        $('#scannerURL').text(data.qr_url);
        $('#scannerModal').modal('show');
        
        // Start polling for scanned items
        startPolling();
    });
}

function startPolling() {
    // Poll every 500ms for new scans
    pollingInterval = setInterval(() => {
        if (!scannerSessionId) return;
        
        fetch('/admin/scanner/poll', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                session_id: scannerSessionId
            })
        })
        .then(r => r.json())
        .then(data => {
            // Add each scanned item to invoice
            data.items.forEach(item => {
                addItemToInvoice(item.item_id, item.name, item.price);
                showToast(`✅ ${item.name} added!`, 'success');
            });
        });
    }, 500);
}

function stopPolling() {
    if (pollingInterval) {
        clearInterval(pollingInterval);
        pollingInterval = null;
    }
    scannerSessionId = null;
}

// Stop polling when modal closes
$('#scannerModal').on('hidden.bs.modal', stopPolling);
</script>
```

### Estimated Timeline

```
Phase 1: Barcode field (2 hours)
Phase 2: Barcode generation (3 hours)
Phase 3: Printable labels (4 hours)
Phase 4: Mobile scanner (8 hours)
Phase 5: Invoice integration (4 hours)

TOTAL: ~21 hours (3-4 days)
```

### Testing Checklist

```
✅ Generate barcodes for existing items
✅ Print barcode labels (test on printer)
✅ Open scanner portal on mobile
✅ Scan physical barcode with mobile camera
✅ Verify item appears in laptop invoice
✅ Test scanning multiple items
✅ Test with invalid barcode
✅ Test session expiration
✅ Test USB scanner (plug & play, no code needed!)
```

---

## 🎯 IMPLEMENTATION ORDER

### Priority 1: Security Fixes (Week 1)
```
1. Forgot password email system
2. Rate limiting
3. Session security
⏱️ 2-3 days
```

### Priority 2: Quick Wins (Week 2)
```
1. MRP field (1 day)
2. Discount percentage (1 day)
⏱️ 2 days
```

### Priority 3: Barcode System (Week 3-4)
```
1. Barcode generation (1 day)
2. Printable labels (1 day)
3. Mobile scanner portal (2 days)
4. Testing & polish (1 day)
⏱️ 5 days
```

---

## ✅ READY TO START?

**Before implementing ANY of these:**

1. ✅ Local dev environment working
2. ✅ Can test on localhost:5000
3. ✅ Git feature branches working
4. ✅ Security fixes complete
5. ✅ Production backup taken

**Then proceed feature by feature!**

---

**Last Updated:** Dec 2, 2025
**Status:** Awaiting dev environment setup

