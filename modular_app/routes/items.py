"""
Items management routes (Professional inventory - Zoho style)
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from models import db, Item, ItemCategory, ItemGroup, ItemStock, ItemStockMovement
from utils.tenant_middleware import require_tenant, get_current_tenant_id
from utils.license_check import check_license
from functools import wraps
from datetime import datetime
import pytz
import os

# Create blueprint
items_bp = Blueprint('items', __name__, url_prefix='/admin/items')

def login_required(f):
    """Decorator to require admin login (also checks license)"""
    @wraps(f)
    @check_license  # Check license/trial before allowing access
    def decorated_function(*args, **kwargs):
        from flask import session
        if 'tenant_admin_id' not in session:
            flash('Please login first', 'error')
            return redirect(url_for('admin.login'))
        # Verify session tenant matches current tenant
        if session.get('tenant_admin_id') != get_current_tenant_id():
            session.clear()
            flash('Session mismatch. Please login again.', 'error')
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function


def generate_sku(tenant_id):
    """Auto-generate SKU for new items"""
    # Get the last item for this tenant
    last_item = Item.query.filter_by(tenant_id=tenant_id).order_by(Item.id.desc()).first()
    
    if last_item and last_item.sku:
        # Extract number from last SKU (e.g., ITEM-0012 -> 12)
        try:
            last_number = int(last_item.sku.split('-')[1])
            new_number = last_number + 1
        except:
            new_number = 1
    else:
        new_number = 1
    
    # Format as ITEM-0001, ITEM-0002, etc.
    return f"ITEM-{new_number:04d}"


# ===== ITEMS LISTING =====
@items_bp.route('/')
@require_tenant
@login_required
def index():
    """List all items"""
    tenant_id = get_current_tenant_id()
    
    # Get filter parameters
    category_id = request.args.get('category', type=int)
    group_id = request.args.get('group', type=int)
    search = request.args.get('search', '')
    status = request.args.get('status', 'active')  # 'active', 'inactive', 'all'
    
    # Build query
    query = Item.query.filter_by(tenant_id=tenant_id)
    
    # Apply filters
    if category_id:
        query = query.filter_by(category_id=category_id)
    if group_id:
        query = query.filter_by(item_group_id=group_id)
    if search:
        query = query.filter(Item.name.ilike(f'%{search}%') | Item.sku.ilike(f'%{search}%'))
    if status == 'active':
        query = query.filter_by(is_active=True)
    elif status == 'inactive':
        query = query.filter_by(is_active=False)
    
    # Get items
    items = query.order_by(Item.created_at.desc()).all()
    
    # Get categories and groups for filters
    categories = ItemCategory.query.filter_by(tenant_id=tenant_id).all()
    groups = ItemGroup.query.filter_by(tenant_id=tenant_id).all()
    
    return render_template('admin/items/list.html',
                         items=items,
                         categories=categories,
                         groups=groups,
                         tenant=g.tenant)


# ===== ADD NEW ITEM =====
@items_bp.route('/add', methods=['GET', 'POST'])
@require_tenant
@login_required
def add():
    """Add new item (like Zoho form)"""
    tenant_id = get_current_tenant_id()
    
    if request.method == 'POST':
        try:
            # Auto-generate SKU
            sku = generate_sku(tenant_id)
            
            # Create new item
            item = Item(
                tenant_id=tenant_id,
                sku=sku,
                name=request.form.get('name'),
                type=request.form.get('type', 'goods'),
                unit=request.form.get('unit', 'nos'),
                
                # Category & Group
                category_id=request.form.get('category_id') or None,
                item_group_id=request.form.get('item_group_id') or None,
                
                # Dimensions
                dimensions_length=float(request.form.get('dimensions_length') or 0),
                dimensions_width=float(request.form.get('dimensions_width') or 0),
                dimensions_height=float(request.form.get('dimensions_height') or 0),
                dimensions_unit=request.form.get('dimensions_unit', 'cm'),
                
                # Weight
                weight=float(request.form.get('weight') or 0),
                weight_unit=request.form.get('weight_unit', 'kg'),
                
                # Product Identifiers
                manufacturer=request.form.get('manufacturer'),
                brand=request.form.get('brand'),
                upc=request.form.get('upc'),
                ean=request.form.get('ean'),
                mpn=request.form.get('mpn'),
                isbn=request.form.get('isbn'),
                
                # Sales Information
                selling_price=float(request.form.get('selling_price') or 0),
                sales_description=request.form.get('sales_description'),
                sales_account=request.form.get('sales_account', 'Sales'),
                
                # Purchase Information
                cost_price=float(request.form.get('cost_price') or 0),
                purchase_description=request.form.get('purchase_description'),
                purchase_account=request.form.get('purchase_account', 'Cost of Goods Sold'),
                preferred_vendor=request.form.get('preferred_vendor'),
                
                # Inventory Tracking
                track_inventory='track_inventory' in request.form,
                opening_stock=float(request.form.get('opening_stock') or 0),
                opening_stock_value=float(request.form.get('opening_stock_value') or 0),
                reorder_point=float(request.form.get('reorder_point') or 0),
                
                # Flags
                is_returnable='is_returnable' in request.form,
                is_active=True,
                
                # Metadata
                created_by=request.form.get('created_by', 'Admin')
            )
            
            db.session.add(item)
            db.session.flush()  # Get the item ID
            
            # If tracking inventory and has opening stock, create stock records for all sites
            if item.track_inventory and item.opening_stock > 0:
                from models.site import Site
                sites = Site.query.filter_by(tenant_id=tenant_id, active=True).all()
                
                for site in sites:
                    # Create stock record
                    stock = ItemStock(
                        tenant_id=tenant_id,
                        item_id=item.id,
                        site_id=site.id,
                        quantity_available=item.opening_stock if site == sites[0] else 0,  # Put all opening stock in first site
                        stock_value=item.opening_stock_value if site == sites[0] else 0
                    )
                    db.session.add(stock)
                    
                    # Create opening stock movement
                    if site == sites[0]:
                        movement = ItemStockMovement(
                            tenant_id=tenant_id,
                            item_id=item.id,
                            site_id=site.id,
                            movement_type='opening_stock',
                            quantity=item.opening_stock,
                            unit_cost=item.cost_price,
                            total_value=item.opening_stock_value,
                            reason='Opening stock',
                            created_by='System'
                        )
                        db.session.add(movement)
            
            db.session.commit()
            
            flash(f'✅ Item "{item.name}" added successfully! SKU: {item.sku}', 'success')
            return redirect(url_for('items.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'❌ Error adding item: {str(e)}', 'error')
    
    # GET request - show form
    categories = ItemCategory.query.filter_by(tenant_id=tenant_id).all()
    groups = ItemGroup.query.filter_by(tenant_id=tenant_id).all()
    
    return render_template('admin/items/add.html',
                         categories=categories,
                         groups=groups,
                         tenant=g.tenant)


# ===== EDIT ITEM =====
@items_bp.route('/edit/<int:item_id>', methods=['GET', 'POST'])
@require_tenant
@login_required
def edit(item_id):
    """Edit existing item"""
    tenant_id = get_current_tenant_id()
    item = Item.query.filter_by(id=item_id, tenant_id=tenant_id).first_or_404()
    
    if request.method == 'POST':
        try:
            # Update item fields
            item.name = request.form.get('name')
            item.type = request.form.get('type', 'goods')
            item.unit = request.form.get('unit', 'nos')
            
            # Category & Group
            item.category_id = request.form.get('category_id') or None
            item.item_group_id = request.form.get('item_group_id') or None
            
            # Dimensions
            item.dimensions_length = float(request.form.get('dimensions_length') or 0)
            item.dimensions_width = float(request.form.get('dimensions_width') or 0)
            item.dimensions_height = float(request.form.get('dimensions_height') or 0)
            item.dimensions_unit = request.form.get('dimensions_unit', 'cm')
            
            # Weight
            item.weight = float(request.form.get('weight') or 0)
            item.weight_unit = request.form.get('weight_unit', 'kg')
            
            # Product Identifiers
            item.manufacturer = request.form.get('manufacturer')
            item.brand = request.form.get('brand')
            item.upc = request.form.get('upc')
            item.ean = request.form.get('ean')
            item.mpn = request.form.get('mpn')
            item.isbn = request.form.get('isbn')
            
            # Sales Information
            item.selling_price = float(request.form.get('selling_price') or 0)
            item.sales_description = request.form.get('sales_description')
            item.sales_account = request.form.get('sales_account', 'Sales')
            
            # Purchase Information
            item.cost_price = float(request.form.get('cost_price') or 0)
            item.purchase_description = request.form.get('purchase_description')
            item.purchase_account = request.form.get('purchase_account', 'Cost of Goods Sold')
            item.preferred_vendor = request.form.get('preferred_vendor')
            
            # Inventory Tracking
            item.track_inventory = 'track_inventory' in request.form
            item.reorder_point = float(request.form.get('reorder_point') or 0)
            
            # Flags
            item.is_returnable = 'is_returnable' in request.form
            item.is_active = 'is_active' in request.form
            
            db.session.commit()
            
            flash(f'✅ Item "{item.name}" updated successfully!', 'success')
            return redirect(url_for('items.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'❌ Error updating item: {str(e)}', 'error')
    
    # GET request - show form with current values
    categories = ItemCategory.query.filter_by(tenant_id=tenant_id).all()
    groups = ItemGroup.query.filter_by(tenant_id=tenant_id).all()
    
    return render_template('admin/items/edit.html',
                         item=item,
                         categories=categories,
                         groups=groups,
                         tenant=g.tenant)


# ===== DELETE ITEM =====
@items_bp.route('/delete/<int:item_id>', methods=['POST'])
@require_tenant
@login_required
def delete(item_id):
    """Delete item"""
    tenant_id = get_current_tenant_id()
    item = Item.query.filter_by(id=item_id, tenant_id=tenant_id).first_or_404()
    
    try:
        item_name = item.name
        db.session.delete(item)  # Cascade will delete related records
        db.session.commit()
        
        flash(f'✅ Item "{item_name}" deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error deleting item: {str(e)}', 'error')
    
    return redirect(url_for('items.index'))


# ===== ITEM CATEGORIES =====
@items_bp.route('/categories')
@require_tenant
@login_required
def categories():
    """Manage item categories"""
    tenant_id = get_current_tenant_id()
    categories = ItemCategory.query.filter_by(tenant_id=tenant_id).all()
    
    return render_template('admin/items/categories.html',
                         categories=categories,
                         tenant=g.tenant)


@items_bp.route('/categories/add', methods=['POST'])
@require_tenant
@login_required
def add_category():
    """Add new category"""
    tenant_id = get_current_tenant_id()
    
    try:
        category = ItemCategory(
            tenant_id=tenant_id,
            name=request.form.get('name'),
            description=request.form.get('description')
        )
        db.session.add(category)
        db.session.commit()
        
        flash(f'✅ Category "{category.name}" added successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error adding category: {str(e)}', 'error')
    
    return redirect(url_for('items.categories'))


@items_bp.route('/categories/delete/<int:category_id>', methods=['POST'])
@require_tenant
@login_required
def delete_category(category_id):
    """Delete category"""
    tenant_id = get_current_tenant_id()
    category = ItemCategory.query.filter_by(id=category_id, tenant_id=tenant_id).first_or_404()
    
    try:
        category_name = category.name
        db.session.delete(category)
        db.session.commit()
        
        flash(f'✅ Category "{category_name}" deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error deleting category: {str(e)}', 'error')
    
    return redirect(url_for('items.categories'))


# ===== ITEM GROUPS =====
@items_bp.route('/groups')
@require_tenant
@login_required
def groups():
    """Manage item groups"""
    tenant_id = get_current_tenant_id()
    groups = ItemGroup.query.filter_by(tenant_id=tenant_id).all()
    
    return render_template('admin/items/groups.html',
                         groups=groups,
                         tenant=g.tenant)


@items_bp.route('/groups/add', methods=['POST'])
@require_tenant
@login_required
def add_group():
    """Add new group"""
    tenant_id = get_current_tenant_id()
    
    try:
        group = ItemGroup(
            tenant_id=tenant_id,
            name=request.form.get('name'),
            description=request.form.get('description')
        )
        db.session.add(group)
        db.session.commit()
        
        flash(f'✅ Group "{group.name}" added successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error adding group: {str(e)}', 'error')
    
    return redirect(url_for('items.groups'))


@items_bp.route('/groups/delete/<int:group_id>', methods=['POST'])
@require_tenant
@login_required
def delete_group(group_id):
    """Delete group"""
    tenant_id = get_current_tenant_id()
    group = ItemGroup.query.filter_by(id=group_id, tenant_id=tenant_id).first_or_404()
    
    try:
        group_name = group.name
        db.session.delete(group)
        db.session.commit()
        
        flash(f'✅ Group "{group_name}" deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error deleting group: {str(e)}', 'error')
    
    return redirect(url_for('items.groups'))

