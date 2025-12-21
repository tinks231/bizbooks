"""
Item Attribute Models for Variant Attributes System
Allows tenants to configure dynamic attributes (Size, Color, Brand, etc.)
"""
from models.database import db, TimestampMixin
from sqlalchemy import Index


class ItemAttribute(db.Model, TimestampMixin):
    """
    Master definition of available item attributes per tenant
    
    Example attributes:
    - Clothing: Size, Color, Brand, Style, Fit
    - Pharmacy: Batch Number, Expiry Date, Manufacturer
    - Electronics: IMEI, Serial Number, Model, Storage
    """
    __tablename__ = 'item_attributes'
    __table_args__ = (
        db.UniqueConstraint('tenant_id', 'attribute_name', name='uq_tenant_attribute_name'),
        Index('idx_item_attributes_tenant', 'tenant_id', 'is_active'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Attribute Definition
    attribute_name = db.Column(db.String(100), nullable=False)  # e.g., "Size", "Color", "Brand"
    attribute_type = db.Column(db.String(50), nullable=False)  # 'text', 'number', 'date', 'dropdown'
    is_required = db.Column(db.Boolean, default=False)
    display_order = db.Column(db.Integer, default=0)  # Order to show in forms
    is_active = db.Column(db.Boolean, default=True)
    
    # For dropdown types
    dropdown_options = db.Column(db.JSON)  # e.g., ["S", "M", "L", "XL", "XXL"]
    
    # For auto-generated item name
    include_in_item_name = db.Column(db.Boolean, default=True)
    name_position = db.Column(db.Integer)  # 1=first, 2=second, etc. in generated name
    
    # Relationships
    values = db.relationship('ItemAttributeValue', backref='attribute', lazy='dynamic', 
                            cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<ItemAttribute {self.attribute_name} ({self.attribute_type}) - Tenant: {self.tenant_id}>'
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'attribute_name': self.attribute_name,
            'attribute_type': self.attribute_type,
            'is_required': self.is_required,
            'display_order': self.display_order,
            'is_active': self.is_active,
            'dropdown_options': self.dropdown_options,
            'include_in_item_name': self.include_in_item_name,
            'name_position': self.name_position
        }


class ItemAttributeValue(db.Model, TimestampMixin):
    """
    Actual attribute values for each item
    
    Example:
    - item_id=123, attribute_id=1 (Size), value="32"
    - item_id=123, attribute_id=2 (Color), value="Blue"
    - item_id=123, attribute_id=3 (Brand), value="Levi's"
    
    Together these create: "Levi's Jeans 501 32 Blue"
    """
    __tablename__ = 'item_attribute_values'
    __table_args__ = (
        db.UniqueConstraint('item_id', 'attribute_id', name='uq_item_attribute'),
        Index('idx_item_attribute_values_item', 'item_id'),
        Index('idx_item_attribute_values_attribute', 'attribute_id'),
        Index('idx_item_attribute_values_tenant', 'tenant_id'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, index=True)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id', ondelete='CASCADE'), nullable=False)
    attribute_id = db.Column(db.Integer, db.ForeignKey('item_attributes.id', ondelete='CASCADE'), nullable=False)
    attribute_value = db.Column(db.Text)  # Stores the actual value
    
    # Relationships
    item = db.relationship('Item', backref='attribute_values')
    
    def __repr__(self):
        return f'<ItemAttributeValue Item:{self.item_id} Attr:{self.attribute_id} = {self.attribute_value}>'
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'item_id': self.item_id,
            'attribute_id': self.attribute_id,
            'attribute_name': self.attribute.attribute_name if self.attribute else None,
            'attribute_value': self.attribute_value
        }


class TenantAttributeConfig(db.Model, TimestampMixin):
    """
    Tenant's attribute system configuration
    
    Stores:
    - Industry type (clothing, pharmacy, electronics, etc.)
    - Item name format template
    - Whether attribute system is enabled
    """
    __tablename__ = 'tenant_attribute_config'
    __table_args__ = (
        Index('idx_tenant_attribute_config_tenant', 'tenant_id'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id', ondelete='CASCADE'), 
                         nullable=False, unique=True, index=True)
    
    # Configuration
    industry_type = db.Column(db.String(100))  # 'clothing', 'pharmacy', 'electronics', etc.
    item_name_format = db.Column(db.Text)  # Template: "{brand} {category} {product} {size} {color}"
    is_enabled = db.Column(db.Boolean, default=False)  # Has tenant enabled attribute system?
    
    # Relationships
    tenant = db.relationship('Tenant', backref=db.backref('attribute_config', uselist=False))
    
    def __repr__(self):
        return f'<TenantAttributeConfig Tenant:{self.tenant_id} Industry:{self.industry_type} Enabled:{self.is_enabled}>'
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'industry_type': self.industry_type,
            'item_name_format': self.item_name_format,
            'is_enabled': self.is_enabled
        }
    
    def get_attributes(self):
        """Get all active attributes for this tenant, ordered by display_order"""
        return ItemAttribute.query.filter_by(
            tenant_id=self.tenant_id,
            is_active=True
        ).order_by(ItemAttribute.display_order).all()

