from models.database import db, TimestampMixin
from datetime import datetime, date
from sqlalchemy import func
import pytz

class VendorPayment(db.Model, TimestampMixin):
    """
    Vendor Payment - Track payments made to vendors
    """
    __tablename__ = 'vendor_payments'
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    
    # Payment Details
    payment_number = db.Column(db.String(50), unique=True, nullable=False)  # PAY-0001
    payment_date = db.Column(db.Date, nullable=False, default=date.today)
    
    # Vendor
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'), nullable=False)
    vendor_name = db.Column(db.String(255), nullable=False)  # Snapshot
    
    # Amount
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    
    # Payment Method
    payment_method = db.Column(db.String(50), default='cash')
    # cash, cheque, bank_transfer, upi, card, online
    
    # Payment Reference
    reference_number = db.Column(db.String(100))  # Cheque number, transaction ID, etc.
    bank_account = db.Column(db.String(100))  # Which account payment came from
    
    # Additional Details
    notes = db.Column(db.Text)
    
    # Audit
    created_by = db.Column(db.String(100))
    
    # Relationships
    tenant = db.relationship('Tenant', backref='vendor_payments')
    vendor = db.relationship('Vendor', backref='payments')
    allocations = db.relationship('PaymentAllocation', backref='payment', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<VendorPayment {self.payment_number} - ₹{self.amount}>'
    
    def generate_payment_number(self):
        """Generate unique payment number like PAY-0001"""
        ist = pytz.timezone('Asia/Kolkata')
        today = datetime.now(ist).date()
        
        # Get last payment for this tenant
        last_payment = VendorPayment.query.filter_by(tenant_id=self.tenant_id)\
            .order_by(VendorPayment.id.desc()).first()
        
        if last_payment and last_payment.payment_number:
            try:
                last_num = int(last_payment.payment_number.split('-')[1])
                new_num = last_num + 1
            except:
                new_num = 1
        else:
            new_num = 1
        
        return f'PAY-{new_num:04d}'
    
    def get_allocated_amount(self):
        """Get total amount allocated to bills"""
        return sum([alloc.amount_allocated for alloc in self.allocations])
    
    def get_unallocated_amount(self):
        """Get unallocated amount (advance payment)"""
        return self.amount - self.get_allocated_amount()


class PaymentAllocation(db.Model):
    """
    Link payments to purchase bills (one payment can be split across multiple bills)
    """
    __tablename__ = 'payment_allocations'
    
    id = db.Column(db.Integer, primary_key=True)
    payment_id = db.Column(db.Integer, db.ForeignKey('vendor_payments.id'), nullable=False)
    purchase_bill_id = db.Column(db.Integer, db.ForeignKey('purchase_bills.id'), nullable=False)
    
    # Amount allocated from payment to this specific bill
    amount_allocated = db.Column(db.Numeric(15, 2), nullable=False)
    
    # Relationships
    purchase_bill = db.relationship('PurchaseBill', backref='payment_allocations')
    
    def __repr__(self):
        return f'<PaymentAllocation {self.payment_id} → Bill {self.purchase_bill_id}: ₹{self.amount_allocated}>'

