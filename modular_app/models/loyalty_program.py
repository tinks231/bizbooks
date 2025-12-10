"""
Loyalty Program Model
Stores loyalty program settings per tenant
"""
from models import db
from datetime import datetime

class LoyaltyProgram(db.Model):
    __tablename__ = 'loyalty_programs'
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False)
    
    # Basic Settings
    program_name = db.Column(db.String(100), default='Loyalty Program')
    is_active = db.Column(db.Boolean, default=False)
    
    # Earning Rules
    points_per_100_rupees = db.Column(db.Numeric(5, 2), default=1.00)
    minimum_purchase_for_points = db.Column(db.Numeric(10, 2), default=0)
    maximum_points_per_invoice = db.Column(db.Integer)
    
    # Threshold Bonuses
    enable_threshold_bonuses = db.Column(db.Boolean, default=False)
    threshold_1_amount = db.Column(db.Numeric(10, 2))
    threshold_1_bonus_points = db.Column(db.Integer)
    threshold_2_amount = db.Column(db.Numeric(10, 2))
    threshold_2_bonus_points = db.Column(db.Integer)
    threshold_3_amount = db.Column(db.Numeric(10, 2))
    threshold_3_bonus_points = db.Column(db.Integer)
    
    # Redemption Rules
    points_to_rupees_ratio = db.Column(db.Numeric(5, 2), default=1.00)
    minimum_points_to_redeem = db.Column(db.Integer, default=10)
    maximum_discount_percent = db.Column(db.Numeric(5, 2))
    maximum_points_per_redemption = db.Column(db.Integer)
    
    # Display
    show_points_on_invoice = db.Column(db.Boolean, default=True)
    invoice_footer_text = db.Column(db.String(255), default='Points Balance: {balance} pts | Next visit: ₹{value} off!')
    
    # Birthday/Anniversary Bonuses (Temporary points - expires same day if not used)
    enable_birthday_bonus = db.Column(db.Boolean, default=False)
    birthday_bonus_points = db.Column(db.Integer, default=0)  # Bonus points on customer's birthday
    enable_anniversary_bonus = db.Column(db.Boolean, default=False)
    anniversary_bonus_points = db.Column(db.Integer, default=0)  # Bonus points on customer's anniversary
    
    # Membership Tiers (Based on lifetime earned points)
    enable_membership_tiers = db.Column(db.Boolean, default=False)
    tier_bronze_name = db.Column(db.String(50), default='Bronze')
    tier_bronze_min_points = db.Column(db.Integer, default=0)
    tier_bronze_earning_multiplier = db.Column(db.Numeric(5, 2), default=1.0)  # 1.0 = same as base rate
    tier_bronze_redemption_multiplier = db.Column(db.Numeric(5, 2), default=1.0)  # 1.0 = same redemption value
    tier_bronze_max_discount_percent = db.Column(db.Numeric(5, 2))  # Optional override
    
    tier_silver_name = db.Column(db.String(50), default='Silver')
    tier_silver_min_points = db.Column(db.Integer, default=1000)
    tier_silver_earning_multiplier = db.Column(db.Numeric(5, 2), default=1.2)  # 1.2 = 20% bonus
    tier_silver_redemption_multiplier = db.Column(db.Numeric(5, 2), default=1.1)  # 1.1 = 10% better value
    tier_silver_max_discount_percent = db.Column(db.Numeric(5, 2))  # Optional override
    
    tier_gold_name = db.Column(db.String(50), default='Gold')
    tier_gold_min_points = db.Column(db.Integer, default=5000)
    tier_gold_earning_multiplier = db.Column(db.Numeric(5, 2), default=1.5)  # 1.5 = 50% bonus
    tier_gold_redemption_multiplier = db.Column(db.Numeric(5, 2), default=1.25)  # 1.25 = 25% better value
    tier_gold_max_discount_percent = db.Column(db.Numeric(5, 2))  # Optional override
    
    tier_platinum_name = db.Column(db.String(50), default='Platinum')
    tier_platinum_min_points = db.Column(db.Integer, default=10000)
    tier_platinum_earning_multiplier = db.Column(db.Numeric(5, 2), default=2.0)  # 2.0 = double points!
    tier_platinum_redemption_multiplier = db.Column(db.Numeric(5, 2), default=1.5)  # 1.5 = 50% better value
    tier_platinum_max_discount_percent = db.Column(db.Numeric(5, 2))  # Optional override
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tenant = db.relationship('Tenant', backref=db.backref('loyalty_program', passive_deletes=True))
    
    def __repr__(self):
        return f'<LoyaltyProgram {self.program_name} - Tenant {self.tenant_id}>'
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'program_name': self.program_name,
            'is_active': self.is_active,
            'points_per_100_rupees': float(self.points_per_100_rupees) if self.points_per_100_rupees else 1.0,
            'minimum_purchase_for_points': float(self.minimum_purchase_for_points) if self.minimum_purchase_for_points else 0,
            'maximum_points_per_invoice': self.maximum_points_per_invoice,
            'enable_threshold_bonuses': self.enable_threshold_bonuses,
            'threshold_1_amount': float(self.threshold_1_amount) if self.threshold_1_amount else None,
            'threshold_1_bonus_points': self.threshold_1_bonus_points,
            'threshold_2_amount': float(self.threshold_2_amount) if self.threshold_2_amount else None,
            'threshold_2_bonus_points': self.threshold_2_bonus_points,
            'threshold_3_amount': float(self.threshold_3_amount) if self.threshold_3_amount else None,
            'threshold_3_bonus_points': self.threshold_3_bonus_points,
            'points_to_rupees_ratio': float(self.points_to_rupees_ratio) if self.points_to_rupees_ratio else 1.0,
            'minimum_points_to_redeem': self.minimum_points_to_redeem or 10,
            'maximum_discount_percent': float(self.maximum_discount_percent) if self.maximum_discount_percent else None,
            'maximum_points_per_redemption': self.maximum_points_per_redemption,
            'show_points_on_invoice': self.show_points_on_invoice,
            'invoice_footer_text': self.invoice_footer_text,
            'enable_birthday_bonus': self.enable_birthday_bonus,
            'birthday_bonus_points': self.birthday_bonus_points or 0,
            'enable_anniversary_bonus': self.enable_anniversary_bonus,
            'anniversary_bonus_points': self.anniversary_bonus_points or 0,
            'enable_membership_tiers': self.enable_membership_tiers,
            'tier_bronze_name': self.tier_bronze_name,
            'tier_bronze_min_points': self.tier_bronze_min_points or 0,
            'tier_bronze_earning_multiplier': float(self.tier_bronze_earning_multiplier) if self.tier_bronze_earning_multiplier else 1.0,
            'tier_bronze_redemption_multiplier': float(self.tier_bronze_redemption_multiplier) if self.tier_bronze_redemption_multiplier else 1.0,
            'tier_bronze_max_discount_percent': float(self.tier_bronze_max_discount_percent) if self.tier_bronze_max_discount_percent else None,
            'tier_silver_name': self.tier_silver_name,
            'tier_silver_min_points': self.tier_silver_min_points or 1000,
            'tier_silver_earning_multiplier': float(self.tier_silver_earning_multiplier) if self.tier_silver_earning_multiplier else 1.2,
            'tier_silver_redemption_multiplier': float(self.tier_silver_redemption_multiplier) if self.tier_silver_redemption_multiplier else 1.1,
            'tier_silver_max_discount_percent': float(self.tier_silver_max_discount_percent) if self.tier_silver_max_discount_percent else None,
            'tier_gold_name': self.tier_gold_name,
            'tier_gold_min_points': self.tier_gold_min_points or 5000,
            'tier_gold_earning_multiplier': float(self.tier_gold_earning_multiplier) if self.tier_gold_earning_multiplier else 1.5,
            'tier_gold_redemption_multiplier': float(self.tier_gold_redemption_multiplier) if self.tier_gold_redemption_multiplier else 1.25,
            'tier_gold_max_discount_percent': float(self.tier_gold_max_discount_percent) if self.tier_gold_max_discount_percent else None,
            'tier_platinum_name': self.tier_platinum_name,
            'tier_platinum_min_points': self.tier_platinum_min_points or 10000,
            'tier_platinum_earning_multiplier': float(self.tier_platinum_earning_multiplier) if self.tier_platinum_earning_multiplier else 2.0,
            'tier_platinum_redemption_multiplier': float(self.tier_platinum_redemption_multiplier) if self.tier_platinum_redemption_multiplier else 1.5,
            'tier_platinum_max_discount_percent': float(self.tier_platinum_max_discount_percent) if self.tier_platinum_max_discount_percent else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

