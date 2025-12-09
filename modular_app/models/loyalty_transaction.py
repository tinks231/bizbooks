"""
Loyalty Transaction Model
Stores every points transaction (earn/redeem)
"""
from models import db
from datetime import datetime

class LoyaltyTransaction(db.Model):
    __tablename__ = 'loyalty_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    
    # Transaction Type
    transaction_type = db.Column(db.String(20), nullable=False)  # 'earned', 'redeemed', 'adjusted', 'bonus'
    
    # Points
    points = db.Column(db.Integer, nullable=False)  # Positive for earn, negative for redeem
    points_before = db.Column(db.Integer)
    points_after = db.Column(db.Integer)
    
    # Reference
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id'))
    invoice_number = db.Column(db.String(50))
    description = db.Column(db.Text)
    
    # Details
    base_points = db.Column(db.Integer)
    bonus_points = db.Column(db.Integer)
    invoice_amount = db.Column(db.Numeric(10, 2))
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    tenant = db.relationship('Tenant')
    customer = db.relationship('Customer', backref='loyalty_transactions')
    invoice = db.relationship('Invoice', backref='loyalty_transactions')
    user = db.relationship('User')
    
    def __repr__(self):
        return f'<LoyaltyTransaction {self.transaction_type} {self.points} pts - Customer {self.customer_id}>'
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'customer_id': self.customer_id,
            'transaction_type': self.transaction_type,
            'points': self.points,
            'points_before': self.points_before,
            'points_after': self.points_after,
            'invoice_id': self.invoice_id,
            'invoice_number': self.invoice_number,
            'description': self.description,
            'base_points': self.base_points,
            'bonus_points': self.bonus_points,
            'invoice_amount': float(self.invoice_amount) if self.invoice_amount else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'created_by': self.created_by
        }

