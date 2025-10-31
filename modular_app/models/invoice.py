from models.database import db, TimestampMixin
from datetime import datetime
import pytz

class Invoice(db.Model, TimestampMixin):
    """
    Sales Invoice Model
    Represents a bill/receipt issued to customers
    """
    __tablename__ = 'invoices'
    __table_args__ = (
        db.Index('idx_invoice_tenant', 'tenant_id', 'invoice_date'),
        db.Index('idx_invoice_number', 'tenant_id', 'invoice_number'),
    )

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False, index=True)
    
    # Invoice Details
    invoice_number = db.Column(db.String(50), nullable=False)  # INV-2024-001
    invoice_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    due_date = db.Column(db.Date)  # For credit sales (optional)
    
    # Customer Reference (NEW: Link to customer master)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=True)  # Optional: Link to customer master
    
    # Customer Details (kept for backward compatibility and one-time customers)
    customer_name = db.Column(db.String(200), nullable=False)
    customer_phone = db.Column(db.String(20))
    customer_email = db.Column(db.String(120))
    customer_address = db.Column(db.Text)
    customer_gstin = db.Column(db.String(15))  # Customer's GST number (optional)
    customer_state = db.Column(db.String(50))  # For GST calculation (CGST+SGST vs IGST)
    
    # Amounts
    subtotal = db.Column(db.Float, nullable=False, default=0)  # Before tax
    cgst_amount = db.Column(db.Float, default=0)  # Central GST (for same state)
    sgst_amount = db.Column(db.Float, default=0)  # State GST (for same state)
    igst_amount = db.Column(db.Float, default=0)  # Integrated GST (for inter-state)
    discount_amount = db.Column(db.Float, default=0)
    round_off = db.Column(db.Float, default=0)  # To make total round number
    total_amount = db.Column(db.Float, nullable=False)
    
    # Payment
    payment_status = db.Column(db.String(20), default='unpaid')  # unpaid, partial, paid
    paid_amount = db.Column(db.Float, default=0)
    payment_method = db.Column(db.String(50))  # Cash, UPI, Card, Cheque, Bank Transfer
    
    # Notes
    notes = db.Column(db.Text)  # Terms & conditions, thank you note
    internal_notes = db.Column(db.Text)  # Private notes (not printed)
    
    # Status
    status = db.Column(db.String(20), default='draft')  # draft, sent, paid, cancelled
    cancelled_at = db.Column(db.DateTime)
    cancelled_reason = db.Column(db.Text)
    
    # Relationships
    tenant = db.relationship('Tenant', backref='invoices', lazy=True)
    items = db.relationship('InvoiceItem', backref='invoice', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Invoice {self.invoice_number} - {self.customer_name} - ₹{self.total_amount}>'

    def generate_invoice_number(self):
        """Generate invoice number like INV-2024-001"""
        ist = pytz.timezone('Asia/Kolkata')
        now = datetime.now(ist)
        year = now.year
        
        # Get last invoice number for this tenant and year
        last_invoice = Invoice.query.filter_by(
            tenant_id=self.tenant_id
        ).filter(
            Invoice.invoice_number.like(f'INV-{year}-%')
        ).order_by(Invoice.id.desc()).first()
        
        if last_invoice:
            # Extract sequence number and increment
            last_seq = int(last_invoice.invoice_number.split('-')[-1])
            new_seq = last_seq + 1
        else:
            new_seq = 1
        
        return f'INV-{year}-{new_seq:04d}'  # INV-2024-0001
    
    def amount_in_words(self):
        """Convert amount to words (Indian number system)"""
        ones = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine"]
        teens = ["Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", 
                "Sixteen", "Seventeen", "Eighteen", "Nineteen"]
        tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]
        
        def convert_less_than_thousand(n):
            if n == 0:
                return ""
            elif n < 10:
                return ones[n]
            elif n < 20:
                return teens[n - 10]
            elif n < 100:
                return tens[n // 10] + (" " + ones[n % 10] if n % 10 != 0 else "")
            else:
                return ones[n // 100] + " Hundred" + (" " + convert_less_than_thousand(n % 100) if n % 100 != 0 else "")
        
        def convert_indian_number(num):
            if num == 0:
                return "Zero Rupees Only"
            
            # Split into crores, lakhs, thousands, hundreds
            crores = num // 10000000
            num %= 10000000
            
            lakhs = num // 100000
            num %= 100000
            
            thousands = num // 1000
            num %= 1000
            
            hundreds = num
            
            result = []
            
            if crores > 0:
                result.append(convert_less_than_thousand(crores) + " Crore")
            
            if lakhs > 0:
                result.append(convert_less_than_thousand(lakhs) + " Lakh")
            
            if thousands > 0:
                result.append(convert_less_than_thousand(thousands) + " Thousand")
            
            if hundreds > 0:
                result.append(convert_less_than_thousand(hundreds))
            
            return " ".join(result) + " Rupees Only"
        
        # Round to integer
        amount = int(round(self.total_amount))
        return convert_indian_number(amount)


class InvoiceItem(db.Model):
    """
    Invoice Line Items
    Each row in the invoice table
    """
    __tablename__ = 'invoice_items'
    __table_args__ = (
        db.Index('idx_invoice_item_invoice', 'invoice_id'),
    )

    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id'), nullable=False)
    
    # Item Details
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'))  # If from inventory
    item_name = db.Column(db.String(200), nullable=False)  # Manual or from inventory
    description = db.Column(db.Text)  # Additional details
    hsn_code = db.Column(db.String(20))  # HSN/SAC code for GST
    
    # Quantity & Pricing
    quantity = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20), default='Nos')  # Nos, Kg, Ltr, Mtr, etc.
    rate = db.Column(db.Float, nullable=False)  # Price per unit
    
    # GST
    gst_rate = db.Column(db.Float, default=18)  # 0, 5, 12, 18, 28 (GST slabs)
    taxable_value = db.Column(db.Float, nullable=False)  # quantity × rate
    cgst_amount = db.Column(db.Float, default=0)
    sgst_amount = db.Column(db.Float, default=0)
    igst_amount = db.Column(db.Float, default=0)
    
    # Total
    total_amount = db.Column(db.Float, nullable=False)  # taxable_value + GST
    
    # Relationships
    item = db.relationship('Item', backref='invoice_items', lazy=True)
    
    def calculate_amounts(self, is_same_state=True):
        """Calculate all amounts based on quantity, rate, and GST"""
        self.taxable_value = self.quantity * self.rate
        
        if self.gst_rate > 0:
            gst_amount = self.taxable_value * (self.gst_rate / 100)
            
            if is_same_state:
                # Same state: CGST + SGST
                self.cgst_amount = gst_amount / 2
                self.sgst_amount = gst_amount / 2
                self.igst_amount = 0
            else:
                # Different state: IGST
                self.igst_amount = gst_amount
                self.cgst_amount = 0
                self.sgst_amount = 0
        else:
            self.cgst_amount = 0
            self.sgst_amount = 0
            self.igst_amount = 0
        
        self.total_amount = self.taxable_value + self.cgst_amount + self.sgst_amount + self.igst_amount
    
    def __repr__(self):
        return f'<InvoiceItem {self.item_name} × {self.quantity} = ₹{self.total_amount}>'

