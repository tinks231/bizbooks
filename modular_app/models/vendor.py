from models.database import db
from datetime import datetime

class Vendor(db.Model):
    """Vendor/Supplier master for managing vendor database"""
    __tablename__ = 'vendors'
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    
    # Vendor Identification
    vendor_code = db.Column(db.String(50), nullable=False)  # VEND-0001, VEND-0002
    name = db.Column(db.String(200), nullable=False)
    company_name = db.Column(db.String(200))  # Optional: Company name if different from name
    
    # Contact Details
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    address = db.Column(db.Text)
    
    # GST Details
    gstin = db.Column(db.String(15))
    state = db.Column(db.String(50))
    
    # Credit Management (for purchase bills)
    credit_limit = db.Column(db.Float, default=0)  # Maximum credit we can take
    payment_terms_days = db.Column(db.Integer, default=30)  # We pay in X days
    opening_balance = db.Column(db.Float, default=0)  # Starting balance (what we owe)
    
    # Additional Info
    notes = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tenant = db.relationship('Tenant', backref='vendors')
    
    # Unique constraint: vendor_code must be unique per tenant
    __table_args__ = (
        db.UniqueConstraint('tenant_id', 'vendor_code', name='unique_vendor_code_per_tenant'),
    )
    
    def __repr__(self):
        return f'<Vendor {self.vendor_code}: {self.name}>'
    
    def get_total_purchases(self):
        """Get count of all purchase requests/bills from this vendor"""
        from models.purchase_request import PurchaseRequest
        return PurchaseRequest.query.filter_by(
            tenant_id=self.tenant_id,
            vendor_name=self.name  # Currently using vendor_name, will link properly later
        ).count()
    
    @staticmethod
    def generate_vendor_code(tenant_id):
        """Generate next vendor code for tenant"""
        # Get all vendors for this tenant
        vendors = Vendor.query.filter_by(tenant_id=tenant_id).all()
        
        if not vendors:
            return "VEND-0001"
        
        # Find the highest vendor code number
        max_number = 0
        for vendor in vendors:
            if vendor.vendor_code and vendor.vendor_code.startswith('VEND-'):
                try:
                    # Extract number from VEND-0001 format
                    number = int(vendor.vendor_code.split('-')[1])
                    max_number = max(max_number, number)
                except (IndexError, ValueError):
                    continue
        
        next_number = max_number + 1
        return f"VEND-{next_number:04d}"

