"""
Inventory routes - Public view (read-only)
"""
from flask import Blueprint, render_template
from models import Material, Stock, Site
from sqlalchemy import func

inventory_bp = Blueprint('inventory', __name__, url_prefix='/inventory')

@inventory_bp.route('/')
def index():
    """View inventory (read-only for employees)"""
    # Get all materials with their stock across all sites
    materials = Material.query.filter_by(active=True).all()
    sites = Site.query.filter_by(active=True).all()
    
    # Get stock information
    inventory_data = []
    for material in materials:
        total_stock = db.session.query(func.sum(Stock.quantity)).filter_by(material_id=material.id).scalar() or 0
        inventory_data.append({
            'material': material,
            'total_stock': total_stock,
            'stocks_by_site': Stock.query.filter_by(material_id=material.id).all()
        })
    
    return render_template('inventory/index.html', inventory_data=inventory_data, sites=sites)

# Import db at the end to avoid circular import
from models import db

