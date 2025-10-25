"""
Employee model
"""
from .database import db, TimestampMixin

class Employee(db.Model, TimestampMixin):
    """Employee model with PIN authentication"""
    __tablename__ = 'employees'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    pin = db.Column(db.String(10), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    document_path = db.Column(db.String(200))  # Aadhar, etc.
    site_id = db.Column(db.Integer, db.ForeignKey('sites.id'))
    active = db.Column(db.Boolean, default=True)
    
    # Relationships
    attendance_records = db.relationship('Attendance', backref='employee', lazy=True)
    
    def __repr__(self):
        return f'<Employee {self.name}>'

