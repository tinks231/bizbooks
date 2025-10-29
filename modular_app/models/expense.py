"""
Expense tracking models
"""
from models import db
from datetime import datetime
import pytz

class ExpenseCategory(db.Model):
    """Expense categories for classification"""
    __tablename__ = 'expense_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(pytz.timezone('Asia/Kolkata')))
    
    # Relationships
    expenses = db.relationship('Expense', backref='category', lazy='dynamic')
    
    def __repr__(self):
        return f'<ExpenseCategory {self.name}>'


class Expense(db.Model):
    """Business expenses tracking"""
    __tablename__ = 'expenses'
    __table_args__ = (
        db.Index('idx_expense_tenant_date', 'tenant_id', 'expense_date'),
        db.Index('idx_expense_category', 'category_id'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False, index=True)
    
    # Expense Details
    expense_date = db.Column(db.Date, nullable=False, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey('expense_categories.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=False)
    
    # Payment Details
    payment_method = db.Column(db.String(50))  # Cash, Bank Transfer, UPI, Card, Cheque
    reference_number = db.Column(db.String(100))  # Transaction ID, Cheque number, etc.
    
    # Vendor/Payee
    vendor_name = db.Column(db.String(200))
    
    # Optional file attachment (invoice, bill, receipt)
    attachment_url = db.Column(db.String(500))
    
    # Audit
    created_by = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(pytz.timezone('Asia/Kolkata')))
    updated_at = db.Column(db.DateTime, onupdate=lambda: datetime.now(pytz.timezone('Asia/Kolkata')))
    
    def __repr__(self):
        return f'<Expense {self.description[:30]} - ₹{self.amount}>'

