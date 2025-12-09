"""
Purchase Request model
"""
from .database import db, TimestampMixin

class PurchaseRequest(db.Model, TimestampMixin):
    """Purchase requests submitted by employees"""
    __tablename__ = 'purchase_requests'
    __table_args__ = (
        db.Index('idx_tenant_status', 'tenant_id', 'status'),
        db.Index('idx_employee_requests', 'employee_id', 'created_at'),
        db.Index('idx_tenant_vendor', 'tenant_id', 'vendor_name'),  # PERFORMANCE: For vendor count queries
    )
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False, index=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    
    # Request Details
    item_name = db.Column(db.String(200), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    estimated_price = db.Column(db.Float, nullable=False)
    vendor_name = db.Column(db.String(200))
    
    # Type: 'expense' or 'inventory'
    request_type = db.Column(db.String(20), nullable=False, default='expense')
    
    # Category (expense category or item category depending on type)
    category_id = db.Column(db.Integer)  # Can be expense_category_id or item_category_id
    
    reason = db.Column(db.Text)
    document_url = db.Column(db.Text)  # Uploaded quotation/invoice/image
    
    # Status: 'pending', 'approved', 'rejected'
    status = db.Column(db.String(20), nullable=False, default='pending')
    
    # Admin action
    admin_notes = db.Column(db.Text)
    rejection_reason = db.Column(db.Text)
    processed_by = db.Column(db.String(100))  # Admin who processed
    processed_at = db.Column(db.DateTime)
    
    # Links to created records
    created_expense_id = db.Column(db.Integer, db.ForeignKey('expenses.id'))
    created_item_id = db.Column(db.Integer, db.ForeignKey('items.id'))
    
    # Relationships
    employee = db.relationship('Employee', backref='purchase_requests')
    
    def __repr__(self):
        return f'<PurchaseRequest {self.item_name} - {self.status}>'

