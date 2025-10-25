"""
Inventory models for multi-site inventory management
"""
from .database import db, TimestampMixin
from datetime import datetime

class Material(db.Model, TimestampMixin):
    """Material/Product model"""
    __tablename__ = 'materials'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))  # e.g., "Construction", "Hardware"
    unit = db.Column(db.String(20), default='nos')  # nos, kg, liters, bags, etc.
    description = db.Column(db.Text)
    image = db.Column(db.String(200))
    active = db.Column(db.Boolean, default=True)
    
    # Relationships
    stocks = db.relationship('Stock', backref='material', lazy=True)
    movements = db.relationship('StockMovement', backref='material', lazy=True)
    
    def __repr__(self):
        return f'<Material {self.name}>'


class Stock(db.Model, TimestampMixin):
    """Stock level per site"""
    __tablename__ = 'stocks'
    
    id = db.Column(db.Integer, primary_key=True)
    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'), nullable=False)
    site_id = db.Column(db.Integer, db.ForeignKey('sites.id'), nullable=False)
    quantity = db.Column(db.Float, default=0.0)
    min_stock_alert = db.Column(db.Float, default=10.0)  # Alert if below this
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Unique constraint: one stock record per material per site
    __table_args__ = (db.UniqueConstraint('material_id', 'site_id', name='_material_site_uc'),)
    
    def is_low_stock(self):
        """Check if stock is below minimum"""
        return self.quantity < self.min_stock_alert
    
    def __repr__(self):
        return f'<Stock {self.material.name if self.material else "Unknown"} at {self.site.name if self.site else "Unknown"}: {self.quantity}>'


class StockMovement(db.Model, TimestampMixin):
    """Stock in/out movement history"""
    __tablename__ = 'stock_movements'
    
    id = db.Column(db.Integer, primary_key=True)
    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'), nullable=False)
    site_id = db.Column(db.Integer, db.ForeignKey('sites.id'), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # 'in', 'out', 'transfer_out', 'transfer_in'
    quantity = db.Column(db.Float, nullable=False)
    reason = db.Column(db.String(255))  # Purchase, consumption, damaged, etc.
    reference = db.Column(db.String(100))  # PO number, bill number, etc.
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    transfer_id = db.Column(db.Integer, db.ForeignKey('transfers.id'))  # If part of transfer
    
    def __repr__(self):
        return f'<StockMovement {self.type} {self.quantity} of {self.material.name if self.material else "Unknown"}>'


class Transfer(db.Model, TimestampMixin):
    """Transfer between sites"""
    __tablename__ = 'transfers'
    
    id = db.Column(db.Integer, primary_key=True)
    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'), nullable=False)
    from_site_id = db.Column(db.Integer, db.ForeignKey('sites.id'), nullable=False)
    to_site_id = db.Column(db.Integer, db.ForeignKey('sites.id'), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    reason = db.Column(db.String(255))
    status = db.Column(db.String(20), default='pending')  # pending, in_transit, completed, cancelled
    initiated_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    completed_at = db.Column(db.DateTime)
    
    # Relationships
    material = db.relationship('Material', backref='transfers')
    from_site = db.relationship('Site', foreign_keys=[from_site_id], backref='transfers_out')
    to_site = db.relationship('Site', foreign_keys=[to_site_id], backref='transfers_in')
    movements = db.relationship('StockMovement', backref='transfer', lazy=True)
    
    def __repr__(self):
        return f'<Transfer {self.material.name if self.material else "Unknown"}: {self.from_site.name if self.from_site else "Unknown"} → {self.to_site.name if self.to_site else "Unknown"}>'

