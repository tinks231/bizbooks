"""
Customer Loyalty Points Model
Stores points balance for each customer
"""
from models import db
from datetime import datetime

class CustomerLoyaltyPoints(db.Model):
    __tablename__ = 'customer_loyalty_points'
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    
    # Points Balance
    current_points = db.Column(db.Integer, default=0)
    lifetime_earned_points = db.Column(db.Integer, default=0)
    lifetime_redeemed_points = db.Column(db.Integer, default=0)
    
    # For Phase 2: Tier tracking
    tier_level = db.Column(db.String(20), default='bronze')
    tier_updated_at = db.Column(db.DateTime)
    
    # Timestamps
    last_earned_at = db.Column(db.DateTime)
    last_redeemed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tenant = db.relationship('Tenant')
    customer = db.relationship('Customer', backref='loyalty_points', uselist=False)
    
    def __repr__(self):
        return f'<CustomerLoyaltyPoints Customer {self.customer_id} - {self.current_points} pts>'
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'customer_id': self.customer_id,
            'current_points': self.current_points,
            'lifetime_earned_points': self.lifetime_earned_points,
            'lifetime_redeemed_points': self.lifetime_redeemed_points,
            'tier_level': self.tier_level,
            'tier_updated_at': self.tier_updated_at.isoformat() if self.tier_updated_at else None,
            'last_earned_at': self.last_earned_at.isoformat() if self.last_earned_at else None,
            'last_redeemed_at': self.last_redeemed_at.isoformat() if self.last_redeemed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

