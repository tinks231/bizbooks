"""
Employee model
"""
from .database import db, TimestampMixin

class Employee(db.Model, TimestampMixin):
    """Employee model with PIN authentication"""
    __tablename__ = 'employees'
    __table_args__ = (
        db.UniqueConstraint('tenant_id', 'pin', name='unique_tenant_pin'),
        db.Index('idx_tenant_employee', 'tenant_id', 'active'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    pin = db.Column(db.String(10), nullable=False)  # Unique per tenant
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))  # Optional - for purchase request notifications
    document_path = db.Column(db.Text)  # Changed to Text to store URLs
    site_id = db.Column(db.Integer, db.ForeignKey('sites.id'))
    active = db.Column(db.Boolean, default=True)
    
    # Relationships
    attendance_records = db.relationship('Attendance', backref='employee', lazy=True)
    
    def __repr__(self):
        return f'<Employee {self.name} (Tenant: {self.tenant_id})>'

