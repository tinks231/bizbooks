"""
Stock Batch Model for GST-aware inventory tracking
Each purchase creates a batch with GST status tracked
"""
from .database import db, TimestampMixin
from datetime import datetime
import pytz

class StockBatch(db.Model, TimestampMixin):
    """
    Stock batches track inventory by purchase with GST status
    This is the KEY to implementing GST-compliant invoice rules
    """
    __tablename__ = 'stock_batches'
    __table_args__ = (
        db.Index('idx_batch_tenant_item', 'tenant_id', 'item_id'),
        db.Index('idx_batch_purchase', 'purchase_bill_id'),
        db.Index('idx_batch_status', 'batch_status'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False, index=True)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    
    # Purchase reference
    purchase_bill_id = db.Column(db.Integer, db.ForeignKey('purchase_bills.id'))
    purchase_bill_item_id = db.Column(db.Integer, db.ForeignKey('purchase_bill_items.id'))
    purchase_bill_number = db.Column(db.String(50))
    purchase_date = db.Column(db.Date)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'))
    vendor_name = db.Column(db.String(200))
    
    # Site/location tracking
    site_id = db.Column(db.Integer, db.ForeignKey('sites.id'))
    
    # Quantity tracking
    quantity_purchased = db.Column(db.Numeric(15, 3), nullable=False)
    quantity_remaining = db.Column(db.Numeric(15, 3), nullable=False)
    quantity_sold = db.Column(db.Numeric(15, 3), default=0)
    quantity_adjusted = db.Column(db.Numeric(15, 3), default=0)  # For adjustments
    
    # 🔑 THE KEY FIELD - GST Status
    purchased_with_gst = db.Column(db.Boolean, nullable=False, default=False)
    # True = This batch has ITC backing, can be used for taxable sales
    # False = No ITC, can only be used for non-taxable sales
    
    # Cost tracking (per unit, base amount)
    base_cost_per_unit = db.Column(db.Numeric(15, 2), nullable=False)
    
    # GST details (only if purchased_with_gst = True)
    gst_rate = db.Column(db.Numeric(5, 2), default=0)
    gst_per_unit = db.Column(db.Numeric(15, 2), default=0)
    total_cost_per_unit = db.Column(db.Numeric(15, 2), nullable=False)
    
    # ITC tracking (only if purchased_with_gst = True)
    itc_per_unit = db.Column(db.Numeric(15, 2), default=0)
    itc_total_available = db.Column(db.Numeric(15, 2), default=0)
    itc_claimed = db.Column(db.Numeric(15, 2), default=0)
    itc_remaining = db.Column(db.Numeric(15, 2), default=0)
    
    # Batch tracking details
    batch_number = db.Column(db.String(50))  # From purchase bill (if any)
    expiry_date = db.Column(db.Date)  # For perishable items
    
    # Batch status
    batch_status = db.Column(db.String(20), default='active')
    # Values: 'active', 'depleted', 'expired', 'damaged'
    
    # Audit fields
    notes = db.Column(db.Text)
    created_by = db.Column(db.String(100))
    
    # Relationships
    item = db.relationship('Item', backref='stock_batches', lazy=True)
    purchase_bill = db.relationship('PurchaseBill', backref='stock_batches', lazy=True)
    purchase_bill_item = db.relationship('PurchaseBillItem', backref='stock_batches', lazy=True)
    vendor = db.relationship('Vendor', backref='stock_batches', lazy=True)
    site = db.relationship('Site', backref='stock_batches', lazy=True)
    
    def __repr__(self):
        gst_status = "GST" if self.purchased_with_gst else "Non-GST"
        return f'<StockBatch {self.id} - {gst_status} - {self.quantity_remaining} units remaining>'
    
    def is_available(self):
        """Check if batch has available stock"""
        return self.quantity_remaining > 0 and self.batch_status == 'active'
    
    def is_depleted(self):
        """Check if batch is fully used"""
        return self.quantity_remaining <= 0
    
    def is_expired(self):
        """Check if batch has expired"""
        if not self.expiry_date:
            return False
        today = datetime.now(pytz.timezone('Asia/Kolkata')).date()
        return self.expiry_date < today
    
    def allocate_quantity(self, quantity):
        """
        Allocate quantity from this batch
        Returns True if successful, False if insufficient quantity
        """
        if quantity > self.quantity_remaining:
            return False
        
        self.quantity_remaining -= quantity
        self.quantity_sold += quantity
        
        # Update ITC claimed if applicable
        if self.purchased_with_gst:
            itc_for_quantity = self.itc_per_unit * quantity
            self.itc_claimed += itc_for_quantity
            self.itc_remaining -= itc_for_quantity
        
        # Update status if depleted
        if self.quantity_remaining <= 0:
            self.batch_status = 'depleted'
        
        return True
    
    def return_quantity(self, quantity):
        """
        Return quantity back to this batch (for returns/adjustments)
        """
        self.quantity_remaining += quantity
        self.quantity_sold = max(0, self.quantity_sold - quantity)
        
        # Revert ITC if applicable
        if self.purchased_with_gst:
            itc_for_quantity = self.itc_per_unit * quantity
            self.itc_claimed = max(0, self.itc_claimed - itc_for_quantity)
            self.itc_remaining += itc_for_quantity
        
        # Reactivate if was depleted
        if self.batch_status == 'depleted' and self.quantity_remaining > 0:
            self.batch_status = 'active'
    
    def get_available_itc(self):
        """Get remaining ITC available for this batch"""
        return self.itc_remaining if self.purchased_with_gst else 0
    
    def calculate_cost_value(self):
        """Calculate total cost value of remaining stock"""
        return float(self.quantity_remaining * self.base_cost_per_unit)
    
    def calculate_itc_value(self):
        """Calculate total ITC value available"""
        return float(self.itc_remaining) if self.purchased_with_gst else 0

