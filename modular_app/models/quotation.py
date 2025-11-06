"""
Quotation Model
Handles customer quotations/estimates
"""
from datetime import datetime
from models.database import db
import pytz

class Quotation(db.Model):
    __tablename__ = 'quotations'
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    
    # Quotation Details
    quotation_number = db.Column(db.String(50), unique=True, nullable=False)
    quotation_date = db.Column(db.Date, nullable=False)
    valid_until = db.Column(db.Date)
    
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
    
    # Status
    status = db.Column(db.String(50), default='draft')
    # draft, sent, accepted, rejected, expired
    
    # Notes
    terms_and_conditions = db.Column(db.Text)
    notes = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(pytz.timezone('Asia/Kolkata')))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(pytz.timezone('Asia/Kolkata')), 
                          onupdate=lambda: datetime.now(pytz.timezone('Asia/Kolkata')))
    created_by = db.Column(db.String(255))
    
    # Relationships
    items = db.relationship('QuotationItem', backref='quotation', lazy=True, cascade='all, delete-orphan')
    tenant = db.relationship('Tenant', backref='quotations')
    
    def __repr__(self):
        return f'<Quotation {self.quotation_number}>'


class QuotationItem(db.Model):
    __tablename__ = 'quotation_items'
    
    id = db.Column(db.Integer, primary_key=True)
    quotation_id = db.Column(db.Integer, db.ForeignKey('quotations.id', ondelete='CASCADE'), nullable=False)
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
    discount_type = db.Column(db.String(20))
    discount_value = db.Column(db.Numeric(15, 2), default=0)
    
    # Calculated Amounts
    taxable_amount = db.Column(db.Numeric(15, 2))
    tax_amount = db.Column(db.Numeric(15, 2))
    total_amount = db.Column(db.Numeric(15, 2))
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(pytz.timezone('Asia/Kolkata')))
    
    def __repr__(self):
        return f'<QuotationItem {self.item_name}>'

