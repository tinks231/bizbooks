from models.database import db, TimestampMixin
from datetime import datetime, date
from sqlalchemy import func
import pytz

class PurchaseBill(db.Model, TimestampMixin):
    __tablename__ = 'purchase_bills'
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    
    # Bill Details
    bill_number = db.Column(db.String(50), unique=True, nullable=False)
    bill_date = db.Column(db.Date, nullable=False, default=date.today)
    due_date = db.Column(db.Date)
    
    # Vendor Details (snapshot at time of bill)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'), nullable=True)
    vendor_name = db.Column(db.String(255), nullable=False)
    vendor_phone = db.Column(db.String(20))
    vendor_email = db.Column(db.String(120))
    vendor_gstin = db.Column(db.String(15))
    vendor_address = db.Column(db.Text)
    vendor_state = db.Column(db.String(50), default='Maharashtra')
    
    # Purchase Request Reference (optional)
    purchase_request_id = db.Column(db.Integer, db.ForeignKey('purchase_requests.id'), nullable=True)
    
    # Amounts
    subtotal = db.Column(db.Numeric(15, 2), default=0)
    discount_amount = db.Column(db.Numeric(15, 2), default=0)
    cgst_amount = db.Column(db.Numeric(15, 2), default=0)
    sgst_amount = db.Column(db.Numeric(15, 2), default=0)
    igst_amount = db.Column(db.Numeric(15, 2), default=0)
    other_charges = db.Column(db.Numeric(15, 2), default=0)
    round_off = db.Column(db.Numeric(10, 2), default=0)
    total_amount = db.Column(db.Numeric(15, 2), nullable=False)
    
    # Payment Tracking
    payment_status = db.Column(db.String(20), default='unpaid')  # unpaid, partial, paid
    paid_amount = db.Column(db.Numeric(15, 2), default=0)
    balance_due = db.Column(db.Numeric(15, 2), default=0)
    
    # Additional Details
    payment_terms = db.Column(db.String(100))  # e.g., "Net 30 days"
    reference_number = db.Column(db.String(100))  # Vendor's invoice/reference number
    notes = db.Column(db.Text)
    terms_conditions = db.Column(db.Text)
    
    # Document Attachment
    document_url = db.Column(db.String(500))  # Scanned bill/invoice
    
    # Status
    status = db.Column(db.String(20), default='draft')  # draft, approved, paid, cancelled
    
    # Timestamps
    approved_at = db.Column(db.DateTime)
    approved_by = db.Column(db.Integer)  # Tenant admin ID (not FK - can be admin or employee)
    
    # Relationships
    tenant = db.relationship('Tenant', backref='purchase_bills', lazy=True)
    vendor = db.relationship('Vendor', backref='purchase_bills', foreign_keys=[vendor_id])
    items = db.relationship('PurchaseBillItem', backref='purchase_bill', lazy=True, cascade='all, delete-orphan')
    # purchase_request = db.relationship('PurchaseRequest', backref='purchase_bills', foreign_keys=[purchase_request_id])
    # payment_allocations backref is created by PaymentAllocation model
    
    def __repr__(self):
        return f'<PurchaseBill {self.bill_number} - {self.vendor_name}>'
    
    def generate_bill_number(self):
        """Generate next bill number for tenant - ROBUST VERSION with duplicate prevention"""
        ist = pytz.timezone('Asia/Kolkata')
        now = datetime.now(ist)
        
        # Format: PB-YYYYMM-XXXX (e.g., PB-202511-0001)
        prefix = f"PB-{now.strftime('%Y%m')}"
        
        # Strategy: Find the HIGHEST existing number, then add 1
        # This is more robust than relying on order_by ID
        existing_bills = PurchaseBill.query.filter(
            PurchaseBill.tenant_id == self.tenant_id,
            PurchaseBill.bill_number.like(f'{prefix}%')
        ).all()
        
        max_num = 0
        for bill in existing_bills:
            try:
                num = int(bill.bill_number.split('-')[-1])
                max_num = max(max_num, num)
            except (ValueError, IndexError):
                continue
        
        # Try up to 20 times to find a unique number (increased from 10)
        for attempt in range(20):
            new_num = max_num + 1 + attempt
            bill_number = f"{prefix}-{new_num:04d}"
            
            # CRITICAL: Check if this exact number already exists
            existing = PurchaseBill.query.filter_by(
                tenant_id=self.tenant_id,
                bill_number=bill_number
            ).first()
            
            if not existing:
                # DOUBLE CHECK: Query again to handle race conditions
                existing_check = PurchaseBill.query.filter_by(
                    tenant_id=self.tenant_id,
                    bill_number=bill_number
                ).first()
                
                if not existing_check:
                    return bill_number
        
        # Fallback: use timestamp-based unique number
        import time
        timestamp = int(time.time() % 10000)
        return f"{prefix}-{timestamp:04d}"
    
    def update_payment_status(self):
        """Update payment status based on paid amount"""
        if self.paid_amount >= self.total_amount:
            self.payment_status = 'paid'
            self.balance_due = 0
        elif self.paid_amount > 0:
            self.payment_status = 'partial'
            self.balance_due = self.total_amount - self.paid_amount
        else:
            self.payment_status = 'unpaid'
            self.balance_due = self.total_amount

