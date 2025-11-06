from datetime import datetime
from models.database import db
import pytz

class SalesOrder(db.Model):
    __tablename__ = 'sales_orders'
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    
    # Order Details
    order_number = db.Column(db.String(50), unique=True, nullable=False)
    order_date = db.Column(db.Date, nullable=False)
    expected_delivery_date = db.Column(db.Date)
    
    # Customer
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    customer_name = db.Column(db.String(255), nullable=False)
    customer_phone = db.Column(db.String(20))
    customer_email = db.Column(db.String(255))
    customer_gstin = db.Column(db.String(15))
    
    # Addresses
    billing_address = db.Column(db.Text)
    shipping_address = db.Column(db.Text)
    
    # Amounts
    subtotal = db.Column(db.Numeric(15, 2), default=0)
    discount_amount = db.Column(db.Numeric(15, 2), default=0)
    tax_amount = db.Column(db.Numeric(15, 2), default=0)
    total_amount = db.Column(db.Numeric(15, 2), nullable=False)
    
    # Order Status
    status = db.Column(db.String(50), default='pending')
    # pending, confirmed, partially_delivered, delivered, partially_invoiced, invoiced, cancelled
    
    # Fulfillment Tracking
    quantity_ordered = db.Column(db.Integer, default=0)
    quantity_delivered = db.Column(db.Integer, default=0)
    quantity_invoiced = db.Column(db.Integer, default=0)
    
    # References
    # quotation_id = db.Column(db.Integer, db.ForeignKey('quotations.id'))  # Disabled until Quotation table exists
    quotation_id = db.Column(db.Integer)  # Temporary: No FK constraint until quotations table is created
    
    # Notes
    terms_and_conditions = db.Column(db.Text)
    notes = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(pytz.timezone('Asia/Kolkata')))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(pytz.timezone('Asia/Kolkata')), 
                          onupdate=lambda: datetime.now(pytz.timezone('Asia/Kolkata')))
    created_by = db.Column(db.String(255))
    
    # Relationships
    items = db.relationship('SalesOrderItem', backref='sales_order', lazy=True, cascade='all, delete-orphan')
    tenant = db.relationship('Tenant', backref='sales_orders')
    customer = db.relationship('Customer', backref='sales_orders', foreign_keys=[customer_id])
    # quotation = db.relationship('Quotation', backref='sales_orders')  # Disabled until Quotation model is implemented
    
    def __repr__(self):
        return f'<SalesOrder {self.order_number}>'
    
    @staticmethod
    def generate_order_number(tenant_id):
        """Generate unique order number for tenant"""
        ist = pytz.timezone('Asia/Kolkata')
        today = datetime.now(ist)
        prefix = f"SO-{today.strftime('%y%m')}"
        
        # Get the last order number for this month
        last_order = SalesOrder.query.filter(
            SalesOrder.tenant_id == tenant_id,
            SalesOrder.order_number.like(f'{prefix}%')
        ).order_by(SalesOrder.id.desc()).first()
        
        if last_order:
            try:
                last_num = int(last_order.order_number.split('-')[-1])
                new_num = last_num + 1
            except:
                new_num = 1
        else:
            new_num = 1
        
        return f"{prefix}-{new_num:04d}"
    
    def update_fulfillment_status(self):
        """Update order status based on delivery and invoice quantities"""
        total_ordered = sum(item.quantity for item in self.items)
        total_delivered = sum(item.quantity_delivered for item in self.items)
        total_invoiced = sum(item.quantity_invoiced for item in self.items)
        
        self.quantity_ordered = int(total_ordered)
        self.quantity_delivered = int(total_delivered)
        self.quantity_invoiced = int(total_invoiced)
        
        if total_invoiced >= total_ordered:
            self.status = 'invoiced'
        elif total_invoiced > 0:
            self.status = 'partially_invoiced'
        elif total_delivered >= total_ordered:
            self.status = 'delivered'
        elif total_delivered > 0:
            self.status = 'partially_delivered'
        elif self.status == 'draft':
            self.status = 'pending'
        
        db.session.commit()
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'order_number': self.order_number,
            'order_date': self.order_date.isoformat() if self.order_date else None,
            'customer_name': self.customer_name,
            'total_amount': float(self.total_amount),
            'status': self.status,
            'quantity_ordered': self.quantity_ordered,
            'quantity_delivered': self.quantity_delivered,
            'quantity_invoiced': self.quantity_invoiced
        }

