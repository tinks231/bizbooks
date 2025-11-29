"""
Bank Account and Transaction models for accounting module
"""
from .database import db
from datetime import datetime
import pytz

class BankAccount(db.Model):
    """Bank/Cash Account model - tracks cash and bank accounts"""
    __tablename__ = 'bank_accounts'
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Account Details
    account_name = db.Column(db.String(100), nullable=False)
    account_type = db.Column(db.String(20), nullable=False, default='bank')  # 'cash', 'bank', 'petty_cash'
    
    # Bank Details (NULL for cash accounts)
    bank_name = db.Column(db.String(100))
    account_number = db.Column(db.String(50))
    ifsc_code = db.Column(db.String(20))
    branch = db.Column(db.String(100))
    
    # Balance
    opening_balance = db.Column(db.Numeric(15, 2), default=0.00)
    current_balance = db.Column(db.Numeric(15, 2), default=0.00)
    
    # Status
    is_active = db.Column(db.Boolean, default=True, index=True)
    is_default = db.Column(db.Boolean, default=False, index=True)
    
    # Notes
    description = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(pytz.timezone('Asia/Kolkata')))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(pytz.timezone('Asia/Kolkata')), onupdate=lambda: datetime.now(pytz.timezone('Asia/Kolkata')))
    
    # Relationships
    transactions = db.relationship('AccountTransaction', backref='account', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<BankAccount {self.account_name} ({self.account_type})>'


class AccountTransaction(db.Model):
    """Account Transaction model - tracks all money movements"""
    __tablename__ = 'account_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Account Reference
    account_id = db.Column(db.Integer, db.ForeignKey('bank_accounts.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Transaction Details
    transaction_date = db.Column(db.Date, nullable=False, index=True)
    transaction_type = db.Column(db.String(50), nullable=False, index=True)
    # Types: 'invoice_payment', 'bill_payment', 'expense', 'contra', 'employee_advance', 'opening_balance'
    
    # Amount
    debit_amount = db.Column(db.Numeric(15, 2), default=0.00)
    credit_amount = db.Column(db.Numeric(15, 2), default=0.00)
    balance_after = db.Column(db.Numeric(15, 2), default=0.00)
    
    # Reference
    reference_type = db.Column(db.String(50), index=True)  # 'invoice', 'purchase_bill', 'expense', 'contra'
    reference_id = db.Column(db.Integer, index=True)
    voucher_number = db.Column(db.String(50))
    
    # Description
    narration = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(pytz.timezone('Asia/Kolkata')))
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    def __repr__(self):
        return f'<AccountTransaction {self.transaction_type} - {self.transaction_date}>'

