from models.database import db, TimestampMixin
from datetime import datetime, date
import pytz

class Return(db.Model, TimestampMixin):
    """
    Sales Return Model
    Represents items returned by customers with refund processing
    """
    __tablename__ = 'returns'
    __table_args__ = (
        db.Index('idx_return_tenant', 'tenant_id', 'return_date'),
        db.Index('idx_return_number', 'tenant_id', 'return_number'),
    )

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False, index=True)
    
    # Return Identification
    return_number = db.Column(db.String(50), unique=True, nullable=False)  # RET-2025-001
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id', ondelete='SET NULL'), nullable=True)
    invoice_number = db.Column(db.String(50))  # Store for reference
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id', ondelete='SET NULL'), nullable=True)
    customer_name = db.Column(db.String(255))  # Store for reference
    
    # Dates
    return_date = db.Column(db.Date, nullable=False, default=date.today)
    invoice_date = db.Column(db.Date)  # Original sale date
    
    # Status Workflow
    status = db.Column(db.String(20), nullable=False, default='pending')
    # Values: pending, approved, rejected, completed, cancelled
    
    # Financial Details
    total_amount = db.Column(db.Numeric(10,2), nullable=False)
    taxable_amount = db.Column(db.Numeric(10,2))
    cgst_amount = db.Column(db.Numeric(10,2))
    sgst_amount = db.Column(db.Numeric(10,2))
    igst_amount = db.Column(db.Numeric(10,2))
    
    # Refund Method
    refund_method = db.Column(db.String(20), nullable=False)
    # Values: cash, bank, credit_note, exchange, pending
    payment_account_id = db.Column(db.Integer, db.ForeignKey('bank_accounts.id', ondelete='SET NULL'))
    payment_reference = db.Column(db.String(100))
    refund_processed_date = db.Column(db.Date)
    
    # GST Compliance
    credit_note_number = db.Column(db.String(50), unique=True)
    credit_note_date = db.Column(db.Date)
    gst_rate = db.Column(db.Numeric(5,2))
    
    # Return Details
    return_reason = db.Column(db.String(50))
    # Values: defective, wrong_item, damaged, changed_mind, exchange, other
    reason_details = db.Column(db.Text)
    
    # Approval Workflow
    created_by = db.Column(db.Integer)
    approved_by = db.Column(db.Integer)
    approved_at = db.Column(db.DateTime)
    rejection_reason = db.Column(db.Text)
    
    # Additional
    notes = db.Column(db.Text)
    customer_notes = db.Column(db.Text)
    attachments_json = db.Column(db.Text)
    
    # Relationships
    tenant = db.relationship('Tenant', backref='returns', lazy=True)
    items = db.relationship('ReturnItem', backref='return', lazy=True, cascade='all, delete-orphan')
    invoice = db.relationship('Invoice', backref='returns', foreign_keys=[invoice_id])
    customer = db.relationship('Customer', backref='returns', foreign_keys=[customer_id])
    payment_account = db.relationship('BankAccount', backref='returns', foreign_keys=[payment_account_id])
    
    def __repr__(self):
        return f'<Return {self.return_number} - {self.customer_name} - ₹{self.total_amount}>'

    def generate_return_number(self):
        """Generate return number like RET-2025-001"""
        ist = pytz.timezone('Asia/Kolkata')
        now = datetime.now(ist)
        year = now.year
        month = now.strftime('%m')
        
        # Find the maximum existing return number for this month and tenant
        last_return = Return.query.filter(
            Return.tenant_id == self.tenant_id,
            Return.return_number.like(f'RET-{year}{month}-%')
        ).order_by(Return.return_number.desc()).first()
        
        if last_return:
            # Extract the sequential number and increment
            try:
                last_num = int(last_return.return_number.split('-')[-1])
                next_num = last_num + 1
            except ValueError:
                next_num = 1
        else:
            next_num = 1
        
        # Generate new return number: RET-YYYYMM-NNNN
        self.return_number = f'RET-{year}{month}-{next_num:04d}'
        return self.return_number

    def generate_credit_note_number(self):
        """Generate credit note number like CN-2025-001"""
        ist = pytz.timezone('Asia/Kolkata')
        now = datetime.now(ist)
        year = now.year
        
        # Find the maximum existing credit note number for this year and tenant
        last_cn = Return.query.filter(
            Return.tenant_id == self.tenant_id,
            Return.credit_note_number.like(f'CN-{year}-%')
        ).order_by(Return.credit_note_number.desc()).first()
        
        if last_cn:
            try:
                last_num = int(last_cn.credit_note_number.split('-')[-1])
                next_num = last_num + 1
            except ValueError:
                next_num = 1
        else:
            next_num = 1
        
        # Generate new credit note number: CN-YYYY-NNNN
        self.credit_note_number = f'CN-{year}-{next_num:04d}'
        self.credit_note_date = date.today()
        return self.credit_note_number

    def is_within_return_window(self, return_window_days=30):
        """Check if return is within configured return window"""
        if not self.invoice_date:
            return True  # No invoice date, allow return
        
        days_since_sale = (self.return_date - self.invoice_date).days
        return days_since_sale <= return_window_days

    def calculate_loyalty_points_to_reverse(self):
        """Calculate how many loyalty points should be reversed"""
        if not self.invoice_id:
            return 0
        
        from models import Invoice, LoyaltyTransaction
        
        invoice = Invoice.query.get(self.invoice_id)
        if not invoice or not invoice.loyalty_points_earned:
            return 0
        
        # Calculate proportional deduction
        return_percentage = float(self.total_amount) / float(invoice.total_amount)
        points_to_deduct = int(invoice.loyalty_points_earned * return_percentage)
        
        return points_to_deduct

