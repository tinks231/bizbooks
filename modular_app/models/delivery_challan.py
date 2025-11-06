"""
Delivery Challan Model
Represents goods physically delivered to customers (before invoicing)
"""
from models.database import db, TimestampMixin
from datetime import datetime
import pytz

class DeliveryChallan(db.Model, TimestampMixin):
    """
    Delivery Challan (Delivery Note/Dispatch Note)
    Records physical delivery of goods to customer
    """
    __tablename__ = 'delivery_challans'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Tenant (Multi-tenancy)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    
    # DC Details
    challan_number = db.Column(db.String(50), unique=True, nullable=False)  # DC-2511-0001
    challan_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    
    # Customer Reference
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=True)
    
    # Customer Details (snapshot at time of DC)
    customer_name = db.Column(db.String(200), nullable=False)
    customer_phone = db.Column(db.String(20))
    customer_email = db.Column(db.String(120))
    customer_gstin = db.Column(db.String(15))
    customer_billing_address = db.Column(db.Text)
    customer_shipping_address = db.Column(db.Text)
    customer_state = db.Column(db.String(50), default='Maharashtra')
    
    # Source Document
    sales_order_id = db.Column(db.Integer, db.ForeignKey('sales_orders.id'), nullable=True)
    
    # Financial Details (for record keeping, not billing)
    subtotal = db.Column(db.Numeric(15, 2), default=0)
    cgst_amount = db.Column(db.Numeric(15, 2), default=0)
    sgst_amount = db.Column(db.Numeric(15, 2), default=0)
    igst_amount = db.Column(db.Numeric(15, 2), default=0)
    total_amount = db.Column(db.Numeric(15, 2), default=0)
    
    # Delivery Details
    vehicle_number = db.Column(db.String(20))  # Transport vehicle
    lr_number = db.Column(db.String(50))  # Lorry Receipt Number
    transporter_name = db.Column(db.String(200))
    delivery_note = db.Column(db.Text)  # Special instructions
    purpose = db.Column(db.String(100), default='Sale')  # Temporary: for old schema compatibility
    
    # Status Tracking
    status = db.Column(db.String(20), default='draft')  # draft, dispatched, delivered, invoiced, cancelled
    dispatched_at = db.Column(db.DateTime)
    delivered_at = db.Column(db.DateTime)
    invoiced_at = db.Column(db.DateTime)
    
    # Additional Info
    notes = db.Column(db.Text)  # Internal notes
    terms = db.Column(db.Text)  # Terms & conditions
    
    # Relationships
    tenant = db.relationship('Tenant', backref='delivery_challans')
    customer = db.relationship('Customer', backref='delivery_challans', foreign_keys=[customer_id])
    sales_order = db.relationship('SalesOrder', backref='delivery_challans', foreign_keys=[sales_order_id])
    items = db.relationship('DeliveryChallanItem', backref='challan', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<DeliveryChallan {self.challan_number} - {self.customer_name}>'
    
    def generate_challan_number(self):
        """Generate unique DC number: DC-YYMM-XXXX"""
        from datetime import datetime
        
        # Get current year-month
        now = datetime.now(pytz.timezone('Asia/Kolkata'))
        year_month = now.strftime('%y%m')  # e.g., 2511 for Nov 2025
        
        # Find the last DC number for this tenant and month
        prefix = f'DC-{year_month}-'
        last_challan = DeliveryChallan.query.filter(
            DeliveryChallan.tenant_id == self.tenant_id,
            DeliveryChallan.challan_number.like(f'{prefix}%')
        ).order_by(DeliveryChallan.id.desc()).first()
        
        if last_challan:
            # Extract the sequence number and increment
            last_number = int(last_challan.challan_number.split('-')[-1])
            new_number = last_number + 1
        else:
            new_number = 1
        
        return f'{prefix}{new_number:04d}'
    
    def update_fulfillment_status(self):
        """Update status based on items delivered and invoiced"""
        if not self.items:
            self.status = 'draft'
            return
        
        total_qty = sum(item.quantity for item in self.items)
        invoiced_qty = sum(item.quantity_invoiced for item in self.items)
        
        if invoiced_qty >= total_qty:
            self.status = 'invoiced'
        elif invoiced_qty > 0:
            self.status = 'partially_invoiced'
        elif self.delivered_at:
            self.status = 'delivered'
        elif self.dispatched_at:
            self.status = 'dispatched'
        else:
            self.status = 'draft'

