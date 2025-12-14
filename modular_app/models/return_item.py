from models.database import db, TimestampMixin
from datetime import datetime
from decimal import Decimal
import pytz

class ReturnItem(db.Model, TimestampMixin):
    """
    Return Line Items
    Each item being returned in a return transaction
    """
    __tablename__ = 'return_items'
    __table_args__ = (
        db.Index('idx_return_item_return', 'return_id'),
    )

    id = db.Column(db.Integer, primary_key=True)
    return_id = db.Column(db.Integer, db.ForeignKey('returns.id', ondelete='CASCADE'), nullable=False)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    
    # Link to Original Sale
    invoice_item_id = db.Column(db.Integer, db.ForeignKey('invoice_items.id', ondelete='SET NULL'), nullable=True)
    
    # Product Details
    product_id = db.Column(db.Integer, db.ForeignKey('items.id', ondelete='SET NULL'), nullable=True)
    product_name = db.Column(db.String(255), nullable=False)
    product_code = db.Column(db.String(100))
    hsn_code = db.Column(db.String(20))
    
    # Quantities
    quantity_sold = db.Column(db.Integer, nullable=False)  # Original qty on invoice
    quantity_returned = db.Column(db.Integer, nullable=False)  # How many being returned
    unit = db.Column(db.String(20))  # pcs, kg, box, etc.
    
    # Pricing
    unit_price = db.Column(db.Numeric(10,2), nullable=False)
    
    # GST Breakdown
    taxable_amount = db.Column(db.Numeric(10,2), nullable=False)
    gst_rate = db.Column(db.Numeric(5,2), nullable=False)
    cgst_amount = db.Column(db.Numeric(10,2))
    sgst_amount = db.Column(db.Numeric(10,2))
    igst_amount = db.Column(db.Numeric(10,2))
    cess_amount = db.Column(db.Numeric(10,2))
    
    # Totals
    total_amount = db.Column(db.Numeric(10,2), nullable=False)
    
    # Item-specific Details
    item_condition = db.Column(db.String(50))
    # Values: resellable, damaged, defective, opened_package
    return_to_inventory = db.Column(db.Boolean, default=True)  # Should we restock?
    
    item_reason = db.Column(db.String(255))  # Why this specific item?
    
    # Relationships
    product = db.relationship('Item', backref='return_items', lazy=True)
    invoice_item = db.relationship('InvoiceItem', backref='return_items', foreign_keys=[invoice_item_id])
    
    def __repr__(self):
        return f'<ReturnItem {self.product_name} x{self.quantity_returned}>'
    
    def calculate_amounts(self, is_same_state=True):
        """Calculate all amounts based on quantity, rate, and GST"""
        # Ensure all calculations use Decimal for precision
        qty = Decimal(str(self.quantity_returned))
        price = Decimal(str(self.unit_price))
        gst_rate_dec = Decimal(str(self.gst_rate))
        
        # Calculate taxable amount
        self.taxable_amount = qty * price
        
        # Calculate GST
        gst_amount = self.taxable_amount * (gst_rate_dec / Decimal('100'))
        
        if is_same_state:
            # Same state: Split into CGST & SGST
            # Use proper rounding to avoid precision issues
            half_gst = gst_amount / Decimal('2')
            self.cgst_amount = half_gst.quantize(Decimal('0.01'))
            self.sgst_amount = half_gst.quantize(Decimal('0.01'))
            self.igst_amount = Decimal('0.00')
        else:
            # Different state: IGST
            self.igst_amount = gst_amount.quantize(Decimal('0.01'))
            self.cgst_amount = Decimal('0.00')
            self.sgst_amount = Decimal('0.00')
        
        # Calculate total (use the rounded GST amounts)
        total_gst = self.cgst_amount + self.sgst_amount + self.igst_amount
        self.total_amount = self.taxable_amount + total_gst
        
        return self.total_amount

