"""
Delivery Challan Item Model
Represents individual items in a delivery challan
"""
from models.database import db, TimestampMixin

class DeliveryChallanItem(db.Model, TimestampMixin):
    """
    Items/products included in a delivery challan
    """
    __tablename__ = 'delivery_challan_items'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Tenant (Multi-tenancy)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    
    # Parent Delivery Challan
    delivery_challan_id = db.Column(db.Integer, db.ForeignKey('delivery_challans.id'), nullable=False)
    
    # Source Sales Order Item (if created from SO)
    sales_order_id = db.Column(db.Integer, nullable=True)
    sales_order_item_id = db.Column(db.Integer, nullable=True)
    
    # Item Reference
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=True)
    
    # Item Details (snapshot at time of delivery)
    item_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    hsn_code = db.Column(db.String(20))
    
    # Quantity & Unit
    quantity = db.Column(db.Numeric(15, 3), nullable=False)
    unit = db.Column(db.String(20), default='Nos')
    
    # Pricing (for record keeping)
    rate = db.Column(db.Numeric(15, 2), nullable=False)
    taxable_value = db.Column(db.Numeric(15, 2), default=0)
    
    # GST Details
    gst_rate = db.Column(db.Numeric(5, 2), default=0)
    cgst_amount = db.Column(db.Numeric(15, 2), default=0)
    sgst_amount = db.Column(db.Numeric(15, 2), default=0)
    igst_amount = db.Column(db.Numeric(15, 2), default=0)
    
    # Total
    total_amount = db.Column(db.Numeric(15, 2), default=0)
    
    # Fulfillment Tracking
    quantity_invoiced = db.Column(db.Numeric(15, 3), default=0)  # How much has been invoiced
    
    # Additional Info
    batch_number = db.Column(db.String(50))  # Batch/Lot number
    serial_number = db.Column(db.String(100))  # Serial number
    notes = db.Column(db.Text)
    
    # Relationships
    tenant = db.relationship('Tenant', backref='delivery_challan_items')
    item = db.relationship('Item', backref='delivery_challan_items')
    
    def __repr__(self):
        return f'<DeliveryChallanItem {self.item_name} x {self.quantity}>'

