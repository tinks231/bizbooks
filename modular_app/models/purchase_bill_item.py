from models.database import db, TimestampMixin
from decimal import Decimal

class PurchaseBillItem(db.Model, TimestampMixin):
    __tablename__ = 'purchase_bill_items'
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    purchase_bill_id = db.Column(db.Integer, db.ForeignKey('purchase_bills.id'), nullable=False)
    
    # Item Details (snapshot at time of purchase)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=True)
    item_name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    hsn_code = db.Column(db.String(20))
    
    # Quantity and Pricing
    quantity = db.Column(db.Numeric(15, 3), nullable=False)
    unit = db.Column(db.String(20), default='pcs')
    rate = db.Column(db.Numeric(15, 2), nullable=False)
    
    # Discount
    discount_percentage = db.Column(db.Numeric(5, 2), default=0)
    discount_amount = db.Column(db.Numeric(15, 2), default=0)
    
    # Tax Calculation
    taxable_value = db.Column(db.Numeric(15, 2), default=0)  # After discount
    gst_rate = db.Column(db.Numeric(5, 2), default=0)
    cgst_amount = db.Column(db.Numeric(15, 2), default=0)
    sgst_amount = db.Column(db.Numeric(15, 2), default=0)
    igst_amount = db.Column(db.Numeric(15, 2), default=0)
    total_amount = db.Column(db.Numeric(15, 2), default=0)
    
    # Inventory Tracking
    site_id = db.Column(db.Integer, db.ForeignKey('sites.id'), nullable=True)
    received_quantity = db.Column(db.Numeric(15, 3), default=0)  # For partial receipts
    
    # Additional Details
    batch_number = db.Column(db.String(50))
    expiry_date = db.Column(db.Date)
    notes = db.Column(db.Text)
    
    # NEW: Fields for creating new items from purchase bill
    is_new_item = db.Column(db.Boolean, default=False)  # Flag: Should this create a new item?
    sku = db.Column(db.String(100))  # SKU/Barcode for new item
    selling_price = db.Column(db.Numeric(15, 2))  # Selling price for new item
    mrp = db.Column(db.Numeric(15, 2))  # MRP for new item
    category_id = db.Column(db.Integer, db.ForeignKey('item_categories.id'), nullable=True)  # Category for new item
    group_id = db.Column(db.Integer, db.ForeignKey('item_groups.id'), nullable=True)  # Group for new item
    attribute_data_json = db.Column(db.Text)  # JSON string of attributes for new item
    
    # Relationships
    item = db.relationship('Item', backref='purchase_bill_items', foreign_keys=[item_id])
    site = db.relationship('Site', backref='purchase_bill_items', foreign_keys=[site_id])
    category = db.relationship('ItemCategory', backref='purchase_bill_items', foreign_keys=[category_id])
    group = db.relationship('ItemGroup', backref='purchase_bill_items', foreign_keys=[group_id])
    
    def __repr__(self):
        return f'<PurchaseBillItem {self.item_name} - {self.quantity}>'

