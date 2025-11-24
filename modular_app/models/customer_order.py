"""
Customer Order Models
For customers to place orders through the customer portal
"""
from .database import db
from datetime import datetime
from sqlalchemy import Index

class CustomerOrder(db.Model):
    """Customer orders placed through customer portal"""
    __tablename__ = 'customer_orders'
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    
    # Order details
    order_number = db.Column(db.String(50), nullable=False)  # AUTO-ORD-001
    order_date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    
    # Status: pending, confirmed, fulfilled, cancelled
    status = db.Column(db.String(20), nullable=False, default='pending')
    
    # Invoice link (if invoice generated)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id'), nullable=True)
    
    # Totals
    subtotal = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    tax_amount = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    
    # Additional info
    notes = db.Column(db.Text)  # Customer notes
    admin_notes = db.Column(db.Text)  # Internal notes
    
    # Fulfillment
    fulfilled_date = db.Column(db.DateTime)
    fulfilled_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    tenant = db.relationship('Tenant', backref='customer_orders')
    customer = db.relationship('Customer', backref='orders')
    items = db.relationship('CustomerOrderItem', back_populates='order', cascade='all, delete-orphan')
    fulfilled_by_user = db.relationship('User', foreign_keys=[fulfilled_by])
    invoice = db.relationship('Invoice', foreign_keys=[invoice_id])
    
    __table_args__ = (
        db.UniqueConstraint('tenant_id', 'order_number', name='unique_order_number_per_tenant'),
        Index('idx_customer_order_status', 'tenant_id', 'status'),
        Index('idx_customer_order_date', 'tenant_id', 'order_date'),
    )
    
    def __repr__(self):
        return f'<CustomerOrder {self.order_number}>'


class CustomerOrderItem(db.Model):
    """Line items in customer orders"""
    __tablename__ = 'customer_order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('customer_orders.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    
    # Order details
    quantity = db.Column(db.Numeric(10, 2), nullable=False)
    rate = db.Column(db.Numeric(10, 2), nullable=False)  # Price at time of order
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Tax
    tax_rate = db.Column(db.Numeric(5, 2), default=0)  # GST %
    tax_amount = db.Column(db.Numeric(10, 2), default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # Relationships
    order = db.relationship('CustomerOrder', back_populates='items')
    item = db.relationship('Item')
    
    def __repr__(self):
        return f'<CustomerOrderItem {self.item_id} x {self.quantity}>'

