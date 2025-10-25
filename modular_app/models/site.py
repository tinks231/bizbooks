"""
Site model for multi-location support
"""
from .database import db, TimestampMixin

class Site(db.Model, TimestampMixin):
    """Site/Shop/Location model"""
    __tablename__ = 'sites'
    __table_args__ = (
        db.Index('idx_tenant_site', 'tenant_id', 'active'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(255))
    latitude = db.Column(db.Float, default=0.0)
    longitude = db.Column(db.Float, default=0.0)
    allowed_radius = db.Column(db.Integer, default=100)  # meters (radius within which attendance is allowed)
    active = db.Column(db.Boolean, default=True)
    
    # Relationships
    employees = db.relationship('Employee', backref='site', lazy=True)
    attendance_records = db.relationship('Attendance', backref='site', lazy=True)
    stocks = db.relationship('Stock', backref='site', lazy=True)
    
    def __repr__(self):
        return f'<Site {self.name} (Tenant: {self.tenant_id})>'

