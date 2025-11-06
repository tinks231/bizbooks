from datetime import datetime
from models.database import db
import pytz

class SalesOrderItem(db.Model):
    __tablename__ = 'sales_order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    sales_order_id = db.Column(db.Integer, db.ForeignKey('sales_orders.id', ondelete='CASCADE'), nullable=False)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    
    # Item Details
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'))
    item_name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    hsn_code = db.Column(db.String(20))
    
    # Quantity & Pricing
    quantity = db.Column(db.Numeric(15, 3), nullable=False)
    unit = db.Column(db.String(50), default='pcs')
    rate = db.Column(db.Numeric(15, 2), nullable=False)
    
    # Tax
    gst_rate = db.Column(db.Numeric(5, 2), default=0)
    price_inclusive = db.Column(db.Boolean, default=False)
    
    # Discount
    discount_type = db.Column(db.String(20))  # 'percentage' or 'amount'
    discount_value = db.Column(db.Numeric(15, 2), default=0)
    
    # Calculated Amounts
    taxable_amount = db.Column(db.Numeric(15, 2))
    tax_amount = db.Column(db.Numeric(15, 2))
    total_amount = db.Column(db.Numeric(15, 2))
    
    # Fulfillment Tracking
    quantity_delivered = db.Column(db.Numeric(15, 3), default=0)
    quantity_invoiced = db.Column(db.Numeric(15, 3), default=0)
    
    # Stock Reservation
    stock_reserved = db.Column(db.Boolean, default=False)
    site_id = db.Column(db.Integer, db.ForeignKey('sites.id'))
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(pytz.timezone('Asia/Kolkata')))
    
    # Relationships
    item = db.relationship('Item', backref='sales_order_items')
    site = db.relationship('Site', backref='sales_order_items')
    
    def __repr__(self):
        return f'<SalesOrderItem {self.item_name}>'
    
    @property
    def quantity_pending(self):
        """Calculate quantity pending delivery"""
        return float(self.quantity) - float(self.quantity_delivered)
    
    @property
    def quantity_pending_invoice(self):
        """Calculate quantity pending invoicing"""
        return float(self.quantity) - float(self.quantity_invoiced)
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'item_id': self.item_id,
            'item_name': self.item_name,
            'quantity': float(self.quantity),
            'unit': self.unit,
            'rate': float(self.rate),
            'gst_rate': float(self.gst_rate),
            'total_amount': float(self.total_amount) if self.total_amount else 0,
            'quantity_delivered': float(self.quantity_delivered),
            'quantity_invoiced': float(self.quantity_invoiced),
            'quantity_pending': self.quantity_pending,
            'quantity_pending_invoice': self.quantity_pending_invoice
        }

