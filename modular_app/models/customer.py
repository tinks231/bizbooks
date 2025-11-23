from models.database import db
from datetime import datetime

class Customer(db.Model):
    """Customer master for managing customer database"""
    __tablename__ = 'customers'
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    
    # Customer Identification
    customer_code = db.Column(db.String(50), nullable=False)  # CUST-0001, CUST-0002
    name = db.Column(db.String(200), nullable=False)
    
    # Contact Details
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    address = db.Column(db.Text)
    
    # Portal Access (NEW - for customer portal login)
    pin = db.Column(db.String(10))  # Customer portal PIN (like employee portal)
    
    # GST Details
    gstin = db.Column(db.String(15))
    state = db.Column(db.String(50))
    
    # Credit Management
    credit_limit = db.Column(db.Float, default=0)  # Maximum credit allowed
    payment_terms_days = db.Column(db.Integer, default=30)  # Payment due in X days
    opening_balance = db.Column(db.Float, default=0)  # Starting balance
    
    # Additional Info
    notes = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tenant = db.relationship('Tenant', backref='customers')
    invoices = db.relationship('Invoice', backref='customer', lazy='dynamic')
    
    # Unique constraint: customer_code must be unique per tenant
    __table_args__ = (
        db.UniqueConstraint('tenant_id', 'customer_code', name='unique_customer_code_per_tenant'),
    )
    
    def __repr__(self):
        return f'<Customer {self.customer_code}: {self.name}>'
    
    def get_outstanding_balance(self):
        """Calculate total outstanding amount for this customer (unpaid invoices only)"""
        from models.invoice import Invoice
        unpaid_invoices = Invoice.query.filter_by(
            customer_id=self.id,
            payment_status='unpaid'
        ).all()
        
        total_outstanding = sum(inv.total_amount for inv in unpaid_invoices)
        return total_outstanding
    
    def get_total_dues(self):
        """Calculate total dues including opening balance + outstanding invoices"""
        outstanding = self.get_outstanding_balance()
        opening = self.opening_balance or 0
        return opening + outstanding
    
    def get_total_invoices(self):
        """Get count of all invoices for this customer"""
        return self.invoices.count()
    
    def get_unpaid_invoices(self):
        """Get all unpaid invoices for this customer"""
        from models.invoice import Invoice
        return Invoice.query.filter_by(
            customer_id=self.id,
            payment_status='unpaid'
        ).order_by(Invoice.invoice_date.desc()).all()
    
    def get_paid_invoices(self):
        """Get all paid invoices for this customer"""
        from models.invoice import Invoice
        return Invoice.query.filter_by(
            customer_id=self.id,
            payment_status='paid'
        ).order_by(Invoice.invoice_date.desc()).all()
    
    def is_credit_limit_exceeded(self, new_amount=0):
        """Check if adding new amount would exceed credit limit"""
        if self.credit_limit <= 0:
            return False  # No limit set
        
        current_outstanding = self.get_outstanding_balance()
        return (current_outstanding + new_amount) > self.credit_limit
    
    @staticmethod
    def generate_customer_code(tenant_id):
        """Generate next customer code for tenant"""
        last_customer = Customer.query.filter_by(tenant_id=tenant_id)\
            .order_by(Customer.id.desc()).first()
        
        if last_customer and last_customer.customer_code:
            # Extract number from CUST-0001 format
            try:
                last_number = int(last_customer.customer_code.split('-')[1])
                next_number = last_number + 1
            except (IndexError, ValueError):
                next_number = 1
        else:
            next_number = 1
        
        return f"CUST-{next_number:04d}"

