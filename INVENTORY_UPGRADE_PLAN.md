# 🚀 Inventory System Upgrade Plan - Zoho Style

**Goal:** Transform basic inventory into professional system like Zoho Inventory

**Timeline:** 2-3 weeks (phased approach)

**Inspiration:** Zoho Inventory (shown in screenshots)

---

## 🎯 **What We're Building**

### **Phase 1: Foundation (Week 1)**
- ✅ New vertical sidebar navigation
- ✅ Items management (detailed product info)
- ✅ Item Groups & Categories
- ✅ SKU generation
- ✅ Improved database schema

### **Phase 2: Advanced Features (Week 2)**
- ✅ Inventory Adjustments
- ✅ Stock valuation methods (FIFO, LIFO, Avg)
- ✅ Barcode/QR generation for items
- ✅ Item images (multiple photos)
- ✅ Reorder point alerts

### **Phase 3: Professional Touch (Week 3)**
- ✅ Reports & Analytics
- ✅ Stock history tracking
- ✅ Composite items (bundles)
- ✅ Price lists
- ✅ Export to Excel

---

## 🗄️ **Complete Database Schema**

### **1. Items (Core Product Information)**

```sql
CREATE TABLE items (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL,
    
    -- Basic Info
    name VARCHAR(200) NOT NULL,
    sku VARCHAR(100) UNIQUE,
    type VARCHAR(20) DEFAULT 'goods', -- 'goods' or 'service'
    
    -- Classification
    category_id INTEGER REFERENCES item_categories(id),
    item_group_id INTEGER REFERENCES item_groups(id),
    
    -- Units & Measurements
    unit VARCHAR(50), -- kg, pcs, ltr, etc.
    dimensions_length DECIMAL(10, 2),
    dimensions_width DECIMAL(10, 2),
    dimensions_height DECIMAL(10, 2),
    dimensions_unit VARCHAR(10) DEFAULT 'cm',
    weight DECIMAL(10, 2),
    weight_unit VARCHAR(10) DEFAULT 'kg',
    
    -- Product Identifiers
    manufacturer VARCHAR(200),
    brand VARCHAR(100),
    upc VARCHAR(50), -- Universal Product Code
    ean VARCHAR(50), -- European Article Number
    mpn VARCHAR(50), -- Manufacturer Part Number
    isbn VARCHAR(50), -- For books
    
    -- Sales Information
    selling_price DECIMAL(10, 2),
    sales_description TEXT,
    sales_account VARCHAR(100),
    tax_preference VARCHAR(50),
    
    -- Purchase Information
    cost_price DECIMAL(10, 2),
    purchase_description TEXT,
    purchase_account VARCHAR(100) DEFAULT 'Cost of Goods Sold',
    preferred_vendor_id INTEGER,
    
    -- Inventory Tracking
    track_inventory BOOLEAN DEFAULT TRUE,
    opening_stock DECIMAL(10, 2) DEFAULT 0,
    opening_stock_value DECIMAL(10, 2) DEFAULT 0,
    reorder_point DECIMAL(10, 2) DEFAULT 0, -- Min quantity before alert
    
    -- Images
    primary_image VARCHAR(500),
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    is_returnable BOOLEAN DEFAULT TRUE,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(100),
    
    FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE
);

CREATE INDEX idx_items_tenant ON items(tenant_id);
CREATE INDEX idx_items_sku ON items(sku);
CREATE INDEX idx_items_category ON items(category_id);
CREATE INDEX idx_items_group ON items(item_group_id);
```

### **2. Item Categories**

```sql
CREATE TABLE item_categories (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    parent_category_id INTEGER REFERENCES item_categories(id),
    created_at TIMESTAMP DEFAULT NOW(),
    
    FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE
);

CREATE INDEX idx_categories_tenant ON item_categories(tenant_id);
```

### **3. Item Groups**

```sql
CREATE TABLE item_groups (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    attributes JSON, -- Store variant attributes (size, color, etc.)
    created_at TIMESTAMP DEFAULT NOW(),
    
    FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE
);

CREATE INDEX idx_item_groups_tenant ON item_groups(tenant_id);
```

### **4. Item Images**

```sql
CREATE TABLE item_images (
    id SERIAL PRIMARY KEY,
    item_id INTEGER NOT NULL,
    image_url VARCHAR(500),
    is_primary BOOLEAN DEFAULT FALSE,
    display_order INTEGER DEFAULT 0,
    uploaded_at TIMESTAMP DEFAULT NOW(),
    
    FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE
);
```

### **5. Stock (Per Site Inventory)**

```sql
CREATE TABLE stock (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL,
    item_id INTEGER NOT NULL,
    site_id INTEGER NOT NULL,
    
    -- Quantity
    quantity_available DECIMAL(10, 2) DEFAULT 0,
    quantity_committed DECIMAL(10, 2) DEFAULT 0, -- Reserved for orders
    quantity_available_for_sale DECIMAL(10, 2) GENERATED ALWAYS AS 
        (quantity_available - quantity_committed) STORED,
    
    -- Valuation
    stock_value DECIMAL(10, 2) DEFAULT 0,
    valuation_method VARCHAR(20) DEFAULT 'FIFO', -- FIFO, LIFO, Average
    
    -- Last updated
    last_stock_date TIMESTAMP DEFAULT NOW(),
    
    FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE,
    FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE,
    FOREIGN KEY (site_id) REFERENCES sites(id) ON DELETE CASCADE,
    
    UNIQUE(item_id, site_id)
);

CREATE INDEX idx_stock_tenant ON stock(tenant_id);
CREATE INDEX idx_stock_item ON stock(item_id);
CREATE INDEX idx_stock_site ON stock(site_id);
```

### **6. Stock Movements (Detailed History)**

```sql
CREATE TABLE stock_movements (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL,
    item_id INTEGER NOT NULL,
    site_id INTEGER NOT NULL,
    
    -- Movement Type
    movement_type VARCHAR(50) NOT NULL, 
    -- Types: 'stock_in', 'stock_out', 'transfer_in', 'transfer_out', 
    --        'adjustment_in', 'adjustment_out', 'return', 'damage'
    
    -- Quantity & Value
    quantity DECIMAL(10, 2) NOT NULL,
    unit_cost DECIMAL(10, 2),
    total_value DECIMAL(10, 2),
    
    -- References
    reference_number VARCHAR(100),
    reference_type VARCHAR(50), -- 'purchase', 'sale', 'adjustment', etc.
    reference_id INTEGER, -- ID of purchase/sale/adjustment
    
    -- Transfer details (if transfer)
    from_site_id INTEGER REFERENCES sites(id),
    to_site_id INTEGER REFERENCES sites(id),
    
    -- Audit
    reason TEXT,
    notes TEXT,
    created_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    
    FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE,
    FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE,
    FOREIGN KEY (site_id) REFERENCES sites(id) ON DELETE CASCADE
);

CREATE INDEX idx_movements_tenant ON stock_movements(tenant_id);
CREATE INDEX idx_movements_item ON stock_movements(item_id);
CREATE INDEX idx_movements_date ON stock_movements(created_at);
```

### **7. Inventory Adjustments**

```sql
CREATE TABLE inventory_adjustments (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL,
    
    -- Adjustment Details
    adjustment_number VARCHAR(100) UNIQUE,
    adjustment_date DATE NOT NULL,
    mode VARCHAR(20) NOT NULL, -- 'quantity' or 'value'
    reason VARCHAR(100),
    description TEXT,
    
    -- Accounting
    account VARCHAR(100) DEFAULT 'Cost of Goods Sold',
    
    -- Status
    status VARCHAR(20) DEFAULT 'draft', -- 'draft' or 'adjusted'
    
    -- Metadata
    created_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    adjusted_at TIMESTAMP,
    
    FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE
);

CREATE INDEX idx_adjustments_tenant ON inventory_adjustments(tenant_id);
```

### **8. Inventory Adjustment Lines**

```sql
CREATE TABLE inventory_adjustment_lines (
    id SERIAL PRIMARY KEY,
    adjustment_id INTEGER NOT NULL,
    item_id INTEGER NOT NULL,
    site_id INTEGER NOT NULL,
    
    -- Before Adjustment
    quantity_before DECIMAL(10, 2),
    value_before DECIMAL(10, 2),
    
    -- Adjustment Amount
    quantity_adjusted DECIMAL(10, 2), -- Can be positive or negative
    value_adjusted DECIMAL(10, 2),
    
    -- After Adjustment
    quantity_after DECIMAL(10, 2),
    value_after DECIMAL(10, 2),
    
    FOREIGN KEY (adjustment_id) REFERENCES inventory_adjustments(id) ON DELETE CASCADE,
    FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE,
    FOREIGN KEY (site_id) REFERENCES sites(id) ON DELETE CASCADE
);
```

### **9. Packages/Shipments (Future)**

```sql
CREATE TABLE packages (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL,
    package_number VARCHAR(100) UNIQUE,
    
    -- Shipment Details
    carrier VARCHAR(100), -- 'FedEx', 'Blue Dart', etc.
    tracking_number VARCHAR(200),
    
    -- Status
    status VARCHAR(50) DEFAULT 'not_shipped',
    -- Statuses: 'not_shipped', 'shipped', 'in_transit', 'delivered'
    
    -- Dates
    shipment_date DATE,
    expected_delivery_date DATE,
    actual_delivery_date DATE,
    
    -- From/To
    from_site_id INTEGER REFERENCES sites(id),
    to_address TEXT,
    
    -- Metadata
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    
    FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE
);
```

---

## 🎨 **Navigation Structure (Vertical Sidebar)**

### **New Navigation Layout:**

```
┌─────────────────┬────────────────────────────────────┐
│                 │                                    │
│  BizBooks       │   Dashboard / Content Area         │
│                 │                                    │
├─────────────────┤                                    │
│ 🏠 Home         │                                    │
│                 │                                    │
│ 📦 ITEMS        │                                    │
│  ├─ All Items   │                                    │
│  └─ Item Groups │                                    │
│                 │                                    │
│ 📊 INVENTORY    │                                    │
│  ├─ Stock       │                                    │
│  ├─ Adjustments │                                    │
│  └─ Transfers   │                                    │
│                 │                                    │
│ 👥 Employees    │                                    │
│                 │                                    │
│ ⏰ Attendance   │                                    │
│                 │                                    │
│ 📍 Sites        │                                    │
│                 │                                    │
│ 📈 Reports      │                                    │
│                 │                                    │
│ ⚙️  Settings    │                                    │
│                 │                                    │
│ 🚪 Logout       │                                    │
│                 │                                    │
└─────────────────┴────────────────────────────────────┘
```

---

## 📁 **File Structure**

```
modular_app/
├─ models/
│  ├─ item.py (NEW)
│  ├─ item_category.py (NEW)
│  ├─ item_group.py (NEW)
│  ├─ stock.py (UPGRADE - replace material_stock.py)
│  ├─ stock_movement.py (UPGRADE)
│  └─ inventory_adjustment.py (NEW)
│
├─ routes/
│  ├─ items.py (NEW)
│  ├─ inventory.py (UPGRADE - enhance existing)
│  └─ adjustments.py (NEW)
│
├─ templates/
│  ├─ base_sidebar.html (NEW - sidebar layout)
│  ├─ admin/
│  │  ├─ items/
│  │  │  ├─ list.html (All items)
│  │  │  ├─ add.html (Add new item - like Zoho)
│  │  │  ├─ edit.html
│  │  │  └─ groups.html
│  │  ├─ inventory/
│  │  │  ├─ stock_summary.html
│  │  │  ├─ adjustments.html
│  │  │  └─ transfers.html
│
└─ utils/
   ├─ sku_generator.py (NEW)
   └─ barcode_generator.py (NEW)
```

---

## 🚀 **Implementation Phases**

### **Phase 1: Foundation (Week 1, 8-10 hours)**

**Day 1-2: Database & Models (3 hours)**
- [ ] Create new database tables
- [ ] Create SQLAlchemy models for Items, Categories, Groups
- [ ] Migrate existing `materials` to new `items` table
- [ ] Update Stock model

**Day 3-4: Vertical Sidebar Navigation (2 hours)**
- [ ] Create `base_sidebar.html` template
- [ ] Update all admin pages to use sidebar
- [ ] Add responsive mobile menu (hamburger)
- [ ] Style like Zoho (professional look)

**Day 5-7: Items Management (5 hours)**
- [ ] Create Items blueprint (`routes/items.py`)
- [ ] Create "All Items" page (list view with filters)
- [ ] Create "Add New Item" form (like Zoho screenshot)
  - Name, SKU, Type
  - Category, Group
  - Unit, Dimensions, Weight
  - Selling price, Cost price
  - Track inventory toggle
  - Opening stock
  - Reorder point
- [ ] Create "Edit Item" page
- [ ] Create "Item Groups" page
- [ ] Auto-generate SKU (e.g., ITEM-001, ITEM-002)

---

### **Phase 2: Advanced Inventory (Week 2, 8-10 hours)**

**Day 1-2: Inventory Adjustments (4 hours)**
- [ ] Create Adjustments model
- [ ] Create Adjustments blueprint
- [ ] Create "New Adjustment" page (like Zoho screenshot)
  - Quantity adjustment
  - Value adjustment
  - Reason dropdown
  - Multi-item support
- [ ] Show before/after values
- [ ] Track adjustment history

**Day 3-4: Stock Management Enhancements (3 hours)**
- [ ] Create "Stock Summary" page
  - Show all items across all sites
  - Quantity available, committed, total
  - Stock value
  - Filters (by item, by site, low stock)
- [ ] Add reorder point alerts
- [ ] Add "Low Stock" dashboard widget

**Day 5-7: Item Details & Images (3 hours)**
- [ ] Add multiple image upload for items
- [ ] Add barcode/QR generation for items
- [ ] Add stock history view (all movements)
- [ ] Add price history

---

### **Phase 3: Polish & Reports (Week 3, 6-8 hours)**

**Day 1-2: Reports (3 hours)**
- [ ] Stock value report
- [ ] Stock movement report (date range)
- [ ] Item-wise sales report
- [ ] Reorder report
- [ ] Export to Excel

**Day 3-4: UI Polish (2 hours)**
- [ ] Add loading spinners
- [ ] Add success/error toasts
- [ ] Improve table sorting/filtering
- [ ] Add search functionality
- [ ] Mobile responsive fixes

**Day 5-7: Testing & Documentation (2 hours)**
- [ ] Test all features with real data
- [ ] Update user documentation
- [ ] Create video tutorial (items management)
- [ ] Performance optimization

---

## 🎨 **UI Components (Zoho-Inspired)**

### **1. Add Item Form (Inspired by Screenshot #3)**

```html
<!-- Key Features to Include: -->
- Type selector (Goods/Service) with radio buttons
- SKU auto-generation
- Unit dropdown (kg, ltr, pcs, box, etc.)
- Returnable item checkbox
- Dimensions fields (L x W x H)
- Weight field
- Sales Information section
  - Selling price (INR)
  - Account dropdown
- Purchase Information section
  - Cost price (INR)
  - Account dropdown
- Track Inventory toggle (prominent!)
- Opening stock fields
- Reorder point
- Image upload (drag & drop)
```

### **2. Inventory Adjustments Form (Screenshot #5)**

```html
<!-- Key Features: -->
- Mode selector (Quantity/Value adjustment)
- Reference number
- Date picker
- Account dropdown
- Reason dropdown
  - Damage
  - Theft
  - Loss
  - Found
  - Correction
- Item table with:
  - Item name (searchable)
  - Quantity available
  - New quantity on hand
  - Quantity adjusted (+10, -5, etc.)
- Add items in bulk
- Attach files (invoice, photos, etc.)
```

---

## 📊 **Key Differences from Current System**

| Feature | Current (Basic) | Upgraded (Professional) |
|---------|----------------|-------------------------|
| **Product Data** | Name, unit only | Name, SKU, category, dimensions, weight, barcode, images |
| **Stock Tracking** | Simple quantity | Quantity available, committed, on-hand, reorder point |
| **Stock Movement** | Basic in/out | Detailed history with reasons, references, audit trail |
| **Navigation** | Horizontal menu | Vertical sidebar (like Zoho) |
| **Forms** | Simple inputs | Multi-section forms with validation |
| **Reports** | Basic table | Excel export, filters, date ranges |
| **Images** | Single photo | Multiple images per item |
| **Inventory Management** | Manual only | Adjustments, transfers, automated alerts |

---

## 💡 **What to Keep from Current System**

✅ **Keep these (they're working well):**
- Multi-tenant architecture
- Site-based inventory
- Attendance system
- Employee management
- License management
- Vercel Blob storage
- IST timezone handling

✅ **Enhance these:**
- Inventory → Upgrade to Items + Stock
- Materials → Migrate to Items
- Stock movements → Add more detail

---

## 🎯 **Priority Features (Start Here!)**

### **High Priority (Week 1):**
1. ✅ Vertical sidebar navigation
2. ✅ Items table (database)
3. ✅ "Add Item" form (detailed, like Zoho)
4. ✅ Item listing page
5. ✅ Item categories

### **Medium Priority (Week 2):**
1. ✅ Inventory adjustments
2. ✅ Stock summary view
3. ✅ Reorder alerts
4. ✅ Item groups

### **Low Priority (Week 3):**
1. ✅ Multiple images
2. ✅ Barcode generation
3. ✅ Advanced reports
4. ✅ Price lists

---

## 🔄 **Migration Strategy**

### **How to Migrate Existing Data:**

```sql
-- Step 1: Create new tables
-- (Run all CREATE TABLE statements above)

-- Step 2: Migrate materials → items
INSERT INTO items (
    tenant_id, name, sku, unit,
    cost_price, selling_price,
    track_inventory, opening_stock,
    created_at
)
SELECT 
    tenant_id,
    name,
    CONCAT('ITEM-', LPAD(id::TEXT, 4, '0')) as sku,
    unit,
    0 as cost_price,
    0 as selling_price,
    TRUE as track_inventory,
    0 as opening_stock,
    NOW()
FROM materials;

-- Step 3: Migrate material_stock → stock
INSERT INTO stock (
    tenant_id, item_id, site_id,
    quantity_available, stock_value,
    last_stock_date
)
SELECT 
    ms.tenant_id,
    i.id as item_id,
    ms.site_id,
    ms.quantity,
    0 as stock_value,
    NOW()
FROM material_stock ms
JOIN materials m ON ms.material_id = m.id
JOIN items i ON i.name = m.name AND i.tenant_id = m.tenant_id;

-- Step 4: Migrate stock_movements
INSERT INTO stock_movements (
    tenant_id, item_id, site_id,
    movement_type, quantity,
    notes, created_at
)
SELECT 
    sm.tenant_id,
    i.id as item_id,
    sm.site_id,
    sm.movement_type,
    sm.quantity,
    sm.notes,
    sm.timestamp
FROM stock_movements sm
JOIN materials m ON sm.material_id = m.id
JOIN items i ON i.name = m.name AND i.tenant_id = m.tenant_id;

-- Step 5: (Optional) Drop old tables after verification
-- DROP TABLE material_stock;
-- DROP TABLE materials;
```

---

## ✅ **Next Steps**

### **What I'll Do:**
1. Create vertical sidebar template
2. Create Item model with full fields
3. Create "Add Item" form (exactly like Zoho)
4. Create Items listing page
5. Migrate existing materials

### **What You'll Do:**
1. Review this plan
2. Confirm which features to prioritize
3. Test as we build each phase
4. Provide feedback

---

## 📞 **Questions to Decide:**

1. **Start with Phase 1 immediately?** (Sidebar + Items management)
2. **Should I migrate existing materials to items automatically?**
3. **Do you want Barcode/QR for items?** (can scan items like attendance)
4. **Keep current inventory page or replace entirely?**
5. **Any Zoho features you DON'T want?** (simplify)

---

**Ready to start with Phase 1? I can begin with the vertical sidebar and Items model! 🚀**

Let me know what you think!

