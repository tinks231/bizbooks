"""
Commission Agent Model
======================
Tracks sales agents (internal employees or external referrals) who earn commission on sales.

Features:
- Can be linked to an Employee (internal) or standalone (external)
- Stores default commission percentage
- Tracks commission earnings per invoice
- Supports marking commissions as paid
"""

from datetime import datetime
from .database import db


class CommissionAgent(db.Model):
    """
    Commission Agent - Can be employee or external referral
    """
    __tablename__ = 'commission_agents'
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    
    # Agent Information
    name = db.Column(db.String(200), nullable=False)
    code = db.Column(db.String(50))  # Unique agent code (e.g., AGT-001)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    
    # Commission Settings
    default_commission_percentage = db.Column(db.Float, default=1.0)  # Default: 1%
    
    # Employee Linkage (NULL for external agents)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=True)
    
    # Agent Type
    agent_type = db.Column(db.String(20), default='external')  # 'employee' or 'external'
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    tenant = db.relationship('Tenant', backref='commission_agents')
    employee = db.relationship('Employee', backref='commission_agent', uselist=False)
    
    # Unique constraint: One agent per employee per tenant
    __table_args__ = (
        db.UniqueConstraint('tenant_id', 'employee_id', name='unique_tenant_employee_agent'),
        db.UniqueConstraint('tenant_id', 'code', name='unique_tenant_agent_code'),
        db.Index('idx_tenant_active', 'tenant_id', 'is_active'),
    )
    
    def __repr__(self):
        return f'<CommissionAgent {self.name} ({self.code})>'
    
    def get_total_commission_earned(self, start_date=None, end_date=None):
        """Calculate total commission earned by this agent"""
        from modular_app.models.invoice_commission import InvoiceCommission
        
        query = InvoiceCommission.query.filter_by(
            tenant_id=self.tenant_id,
            agent_id=self.id
        )
        
        if start_date:
            query = query.filter(InvoiceCommission.created_at >= start_date)
        if end_date:
            query = query.filter(InvoiceCommission.created_at <= end_date)
        
        total = db.session.query(db.func.sum(InvoiceCommission.commission_amount)).filter(
            InvoiceCommission.tenant_id == self.tenant_id,
            InvoiceCommission.agent_id == self.id
        ).scalar()
        
        return total or 0.0
    
    def get_total_commission_paid(self, start_date=None, end_date=None):
        """Calculate total commission paid to this agent"""
        from modular_app.models.invoice_commission import InvoiceCommission
        
        query = InvoiceCommission.query.filter_by(
            tenant_id=self.tenant_id,
            agent_id=self.id,
            is_paid=True
        )
        
        if start_date:
            query = query.filter(InvoiceCommission.created_at >= start_date)
        if end_date:
            query = query.filter(InvoiceCommission.created_at <= end_date)
        
        total = db.session.query(db.func.sum(InvoiceCommission.commission_amount)).filter(
            InvoiceCommission.tenant_id == self.tenant_id,
            InvoiceCommission.agent_id == self.id,
            InvoiceCommission.is_paid == True
        ).scalar()
        
        return total or 0.0
    
    def get_pending_commission(self, start_date=None, end_date=None):
        """Calculate pending (unpaid) commission"""
        earned = self.get_total_commission_earned(start_date, end_date)
        paid = self.get_total_commission_paid(start_date, end_date)
        return earned - paid


class InvoiceCommission(db.Model):
    """
    Invoice Commission Record
    Links invoices to agents and tracks commission amounts
    """
    __tablename__ = 'invoice_commissions'
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    
    # Links
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id'), nullable=False)
    agent_id = db.Column(db.Integer, db.ForeignKey('commission_agents.id'), nullable=False)
    
    # Denormalized Agent Data (for performance and historical accuracy)
    agent_name = db.Column(db.String(200), nullable=False)
    agent_code = db.Column(db.String(50))
    
    # Commission Details
    commission_percentage = db.Column(db.Float, nullable=False)  # % used for this invoice
    invoice_amount = db.Column(db.Float, nullable=False)  # Invoice total
    commission_amount = db.Column(db.Float, nullable=False)  # Calculated commission
    
    # Payment Tracking
    is_paid = db.Column(db.Boolean, default=False)
    paid_date = db.Column(db.Date, nullable=True)
    payment_notes = db.Column(db.Text)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tenant = db.relationship('Tenant', backref='invoice_commissions')
    invoice = db.relationship('Invoice', backref='commission_record', uselist=False)
    agent = db.relationship('CommissionAgent', backref='commission_records')
    
    # Indexes
    __table_args__ = (
        db.UniqueConstraint('invoice_id', name='unique_invoice_commission'),
        db.Index('idx_tenant_agent_paid', 'tenant_id', 'agent_id', 'is_paid'),
        db.Index('idx_tenant_paid_date', 'tenant_id', 'paid_date'),
    )
    
    def __repr__(self):
        return f'<InvoiceCommission Invoice#{self.invoice_id} Agent:{self.agent_name} ₹{self.commission_amount}>'

