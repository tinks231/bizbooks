"""
Attendance model
"""
from .database import db, TimestampMixin
from datetime import datetime
import pytz

class Attendance(db.Model, TimestampMixin):
    """Attendance record model"""
    __tablename__ = 'attendance'
    __table_args__ = (
        db.Index('idx_tenant_attendance', 'tenant_id', 'timestamp'),
        db.Index('idx_tenant_employee_date', 'tenant_id', 'employee_id', 'timestamp'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, index=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id', ondelete='CASCADE'), nullable=False)
    site_id = db.Column(db.Integer, db.ForeignKey('sites.id', ondelete='CASCADE'), nullable=False)
    employee_name = db.Column(db.String(100))  # Denormalized for quick access
    type = db.Column(db.String(20), nullable=False)  # 'check_in' or 'check_out'
    # Store timezone-aware datetime (IST)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(pytz.timezone('Asia/Kolkata')), nullable=False)
    
    # Location data
    latitude = db.Column(db.Float, default=0.0)
    longitude = db.Column(db.Float, default=0.0)
    distance = db.Column(db.Float, default=0.0)  # Distance from office (meters)
    
    # Photo and manual entry
    photo = db.Column(db.Text)  # Changed to Text to store URLs (can be long with query params)
    manual_entry = db.Column(db.Boolean, default=False)
    comment = db.Column(db.String(500))
    
    def __repr__(self):
        return f'<Attendance {self.employee_name} - {self.type} at {self.timestamp} (Tenant: {self.tenant_id})>'

