"""
Item models for professional inventory management (Zoho-style)
"""
from .database import db, TimestampMixin
from datetime import datetime
import pytz

class ItemCategory(db.Model, TimestampMixin):
    """Item Categories for organizing products"""
    __tablename__ = 'item_categories'
    __table_args__ = (
        db.Index('idx_category_tenant', 'tenant_id'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    parent_category_id = db.Column(db.Integer, db.ForeignKey('item_categories.id'))
    
    # Relationships
    items = db.relationship('Item', backref='category', lazy=True)
    subcategories = db.relationship('ItemCategory', backref=db.backref('parent_category', remote_side=[id]))
    
    def __repr__(self):
        return f'<ItemCategory {self.name} (Tenant: {self.tenant_id})>'


class ItemGroup(db.Model, TimestampMixin):
    """Item Groups for variants (e.g., T-Shirt with sizes S, M, L)"""
    __tablename__ = 'item_groups'
    __table_args__ = (
        db.Index('idx_group_tenant', 'tenant_id'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    # Relationships
    items = db.relationship('Item', backref='item_group', lazy=True)
    
    def __repr__(self):
        return f'<ItemGroup {self.name} (Tenant: {self.tenant_id})>'


class Item(db.Model, TimestampMixin):
    """
    Item model - Professional product/service management
    Inspired by Zoho Inventory
    """
    __tablename__ = 'items'
    __table_args__ = (
        db.Index('idx_item_tenant', 'tenant_id', 'is_active'),
        db.Index('idx_item_sku', 'sku'),
        db.Index('idx_item_category', 'category_id'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False, index=True)
    
    # ===== Basic Information =====
    name = db.Column(db.String(200), nullable=False)
    sku = db.Column(db.String(100), unique=True, nullable=False)  # Auto-generated: ITEM-0001
    type = db.Column(db.String(20), default='goods')  # 'goods' or 'service'
    
    # ===== Classification =====
    category_id = db.Column(db.Integer, db.ForeignKey('item_categories.id'))
    item_group_id = db.Column(db.Integer, db.ForeignKey('item_groups.id'))
    
    # ===== Units & Measurements =====
    unit = db.Column(db.String(50), default='nos')  # kg, pcs, ltr, box, etc.
    
    # Dimensions
    dimensions_length = db.Column(db.Float)
    dimensions_width = db.Column(db.Float)
    dimensions_height = db.Column(db.Float)
    dimensions_unit = db.Column(db.String(10), default='cm')  # cm, m, inch
    
    # Weight
    weight = db.Column(db.Float)
    weight_unit = db.Column(db.String(10), default='kg')  # kg, g, lb
    
    # ===== Product Identifiers =====
    manufacturer = db.Column(db.String(200))
    brand = db.Column(db.String(100))
    upc = db.Column(db.String(50))  # Universal Product Code
    ean = db.Column(db.String(50))  # European Article Number
    mpn = db.Column(db.String(50))  # Manufacturer Part Number
    isbn = db.Column(db.String(50))  # For books
    
    # ===== Sales Information =====
    selling_price = db.Column(db.Float, default=0.0)
    sales_description = db.Column(db.Text)
    sales_account = db.Column(db.String(100), default='Sales')
    tax_preference = db.Column(db.String(50))
    
    # ===== Purchase Information =====
    cost_price = db.Column(db.Float, default=0.0)
    purchase_description = db.Column(db.Text)
    purchase_account = db.Column(db.String(100), default='Cost of Goods Sold')
    preferred_vendor = db.Column(db.String(200))
    
    # ===== Inventory Tracking =====
    track_inventory = db.Column(db.Boolean, default=True)
    opening_stock = db.Column(db.Float, default=0.0)
    opening_stock_value = db.Column(db.Float, default=0.0)
    reorder_point = db.Column(db.Float, default=0.0)  # Alert when stock below this
    
    # ===== Images =====
    primary_image = db.Column(db.Text)  # URL from Vercel Blob
    
    # ===== Status & Flags =====
    is_active = db.Column(db.Boolean, default=True)
    is_returnable = db.Column(db.Boolean, default=True)
    
    # ===== Metadata =====
    created_by = db.Column(db.String(100))
    
    # ===== Relationships =====
    images = db.relationship('ItemImage', backref='item', lazy=True, cascade='all, delete-orphan')
    stocks = db.relationship('ItemStock', backref='item', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Item {self.name} ({self.sku}) - Tenant: {self.tenant_id}>'
    
    def get_total_stock(self):
        """Get total stock across all sites"""
        return sum([stock.quantity_available for stock in self.stocks])
    
    def is_low_stock(self):
        """Check if any site has low stock"""
        if not self.track_inventory:
            return False
        total = self.get_total_stock()
        return total < self.reorder_point
    
    def get_stock_value(self):
        """Calculate total stock value"""
        return self.get_total_stock() * self.cost_price


class ItemImage(db.Model):
    """Multiple images per item"""
    __tablename__ = 'item_images'
    
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    image_url = db.Column(db.Text, nullable=False)  # Vercel Blob URL
    is_primary = db.Column(db.Boolean, default=False)
    display_order = db.Column(db.Integer, default=0)
    uploaded_at = db.Column(db.DateTime, default=lambda: datetime.now(pytz.timezone('Asia/Kolkata')))
    
    def __repr__(self):
        return f'<ItemImage {self.id} for Item {self.item_id}>'


class ItemStock(db.Model, TimestampMixin):
    """
    Stock level per site (per item)
    Replaces the old Stock model
    """
    __tablename__ = 'item_stocks'
    __table_args__ = (
        db.UniqueConstraint('tenant_id', 'item_id', 'site_id', name='_tenant_item_site_uc'),
        db.Index('idx_item_stock_tenant', 'tenant_id', 'site_id'),
        db.Index('idx_item_stock_item', 'item_id'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False, index=True)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    site_id = db.Column(db.Integer, db.ForeignKey('sites.id'), nullable=False)
    
    # ===== Quantities =====
    quantity_available = db.Column(db.Float, default=0.0)  # Physical stock
    quantity_committed = db.Column(db.Float, default=0.0)  # Reserved for orders (future feature)
    
    # ===== Valuation =====
    stock_value = db.Column(db.Float, default=0.0)
    valuation_method = db.Column(db.String(20), default='FIFO')  # FIFO, LIFO, Average
    
    # ===== Tracking =====
    last_stock_date = db.Column(db.DateTime, default=lambda: datetime.now(pytz.timezone('Asia/Kolkata')))
    
    def get_available_for_sale(self):
        """Available quantity after commitments"""
        return self.quantity_available - self.quantity_committed
    
    def is_low_stock(self):
        """Check if stock is below reorder point"""
        if self.item and self.item.reorder_point:
            return self.quantity_available < self.item.reorder_point
        return False
    
    def __repr__(self):
        return f'<ItemStock {self.item.name if self.item else "Unknown"} at Site {self.site_id}: {self.quantity_available}>'


class ItemStockMovement(db.Model, TimestampMixin):
    """
    Detailed stock movement history
    Replaces the old StockMovement model
    """
    __tablename__ = 'item_stock_movements'
    __table_args__ = (
        db.Index('idx_item_movement_tenant', 'tenant_id', 'created_at'),
        db.Index('idx_item_movement_item', 'item_id'),
        db.Index('idx_item_movement_site', 'site_id'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False, index=True)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    site_id = db.Column(db.Integer, db.ForeignKey('sites.id'), nullable=False)
    
    # ===== Movement Type =====
    movement_type = db.Column(db.String(50), nullable=False)
    # Types: 'stock_in', 'stock_out', 'transfer_in', 'transfer_out', 
    #        'adjustment_in', 'adjustment_out', 'return', 'damage', 'opening_stock'
    
    # ===== Quantity & Value =====
    quantity = db.Column(db.Float, nullable=False)
    unit_cost = db.Column(db.Float)
    total_value = db.Column(db.Float)
    
    # ===== References =====
    reference_number = db.Column(db.String(100))
    reference_type = db.Column(db.String(50))  # 'purchase', 'sale', 'adjustment', 'transfer', etc.
    reference_id = db.Column(db.Integer)  # ID of related record
    
    # ===== Transfer Details (if transfer) =====
    from_site_id = db.Column(db.Integer, db.ForeignKey('sites.id'))
    to_site_id = db.Column(db.Integer, db.ForeignKey('sites.id'))
    
    # ===== Audit =====
    reason = db.Column(db.Text)
    notes = db.Column(db.Text)
    created_by = db.Column(db.String(100))
    
    # ===== Relationships =====
    item = db.relationship('Item', backref='movements')
    site = db.relationship('Site', foreign_keys=[site_id], backref='item_movements')
    from_site = db.relationship('Site', foreign_keys=[from_site_id])
    to_site = db.relationship('Site', foreign_keys=[to_site_id])
    
    def __repr__(self):
        return f'<ItemStockMovement {self.movement_type} {self.quantity} of {self.item.name if self.item else "Unknown"}>'


class InventoryAdjustment(db.Model, TimestampMixin):
    """
    Inventory Adjustments (like Zoho)
    For correcting stock discrepancies
    """
    __tablename__ = 'inventory_adjustments'
    __table_args__ = (
        db.Index('idx_adjustment_tenant', 'tenant_id'),
        db.UniqueConstraint('tenant_id', 'adjustment_number', name='_tenant_adjustment_number_uc'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False, index=True)
    
    # ===== Adjustment Details =====
    adjustment_number = db.Column(db.String(100), nullable=False)  # ADJ-0001
    adjustment_date = db.Column(db.Date, nullable=False)
    mode = db.Column(db.String(20), nullable=False)  # 'quantity' or 'value'
    reason = db.Column(db.String(100))  # 'Damage', 'Theft', 'Found', 'Correction'
    description = db.Column(db.Text)
    
    # ===== Accounting =====
    account = db.Column(db.String(100), default='Cost of Goods Sold')
    
    # ===== Status =====
    status = db.Column(db.String(20), default='draft')  # 'draft' or 'adjusted'
    
    # ===== Metadata =====
    created_by = db.Column(db.String(100))
    adjusted_at = db.Column(db.DateTime)
    
    # ===== Relationships =====
    lines = db.relationship('InventoryAdjustmentLine', backref='adjustment', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<InventoryAdjustment {self.adjustment_number} - {self.status}>'


class InventoryAdjustmentLine(db.Model):
    """
    Individual items in an inventory adjustment
    """
    __tablename__ = 'inventory_adjustment_lines'
    
    id = db.Column(db.Integer, primary_key=True)
    adjustment_id = db.Column(db.Integer, db.ForeignKey('inventory_adjustments.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    site_id = db.Column(db.Integer, db.ForeignKey('sites.id'), nullable=False)
    
    # ===== Before Adjustment =====
    quantity_before = db.Column(db.Float)
    value_before = db.Column(db.Float)
    
    # ===== Adjustment Amount =====
    quantity_adjusted = db.Column(db.Float)  # Can be positive or negative
    value_adjusted = db.Column(db.Float)
    
    # ===== After Adjustment =====
    quantity_after = db.Column(db.Float)
    value_after = db.Column(db.Float)
    
    # ===== Relationships =====
    item = db.relationship('Item')
    site = db.relationship('Site')
    
    def __repr__(self):
        return f'<AdjustmentLine {self.item.name if self.item else "Unknown"}: {self.quantity_adjusted:+.2f}>'

