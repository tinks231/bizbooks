"""
Item Attributes Settings
Allows tenants to configure variant attributes system
"""
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, g
from models import db, ItemAttribute, ItemAttributeValue, TenantAttributeConfig
from sqlalchemy import text
from utils.tenant_middleware import require_tenant
from datetime import datetime

item_attributes_settings_bp = Blueprint('item_attributes_settings', __name__)


# ============================================================
# INDUSTRY PRESETS - Pre-configured attribute templates
# ============================================================

INDUSTRY_PRESETS = {
    'clothing': {
        'name': 'Clothing & Apparel',
        'description': 'For retail clothing, footwear, and fashion stores',
        'attributes': [
            {'name': 'Brand', 'type': 'text', 'required': True, 'order': 1, 'in_name': True, 'position': 1},
            {'name': 'Category', 'type': 'text', 'required': True, 'order': 2, 'in_name': True, 'position': 2},
            {'name': 'Product', 'type': 'text', 'required': True, 'order': 3, 'in_name': True, 'position': 3},
            {'name': 'Size', 'type': 'dropdown', 'required': True, 'order': 4, 'in_name': True, 'position': 4,
             'options': ['XS', 'S', 'M', 'L', 'XL', 'XXL', '28', '30', '32', '34', '36', '38', '40', '42']},
            {'name': 'Color', 'type': 'dropdown', 'required': True, 'order': 5, 'in_name': True, 'position': 5,
             'options': ['Black', 'Blue', 'White', 'Red', 'Grey', 'Green', 'Yellow', 'Pink', 'Brown', 'Navy', 'Beige']},
            {'name': 'Style', 'type': 'text', 'required': False, 'order': 6, 'in_name': True, 'position': 6},
        ],
        'item_name_format': '{brand} {category} {product} {size} {color} {style}'
    },
    'pharmacy': {
        'name': 'Pharmacy & Medical',
        'description': 'For pharmacies and medical stores',
        'attributes': [
            {'name': 'Generic Name', 'type': 'text', 'required': True, 'order': 1, 'in_name': True, 'position': 1},
            {'name': 'Brand', 'type': 'text', 'required': True, 'order': 2, 'in_name': True, 'position': 2},
            {'name': 'Dosage', 'type': 'text', 'required': False, 'order': 3, 'in_name': True, 'position': 3},
            {'name': 'Batch Number', 'type': 'text', 'required': True, 'order': 4, 'in_name': True, 'position': 4},
            {'name': 'Expiry Date', 'type': 'date', 'required': True, 'order': 5, 'in_name': False, 'position': None},
            {'name': 'Manufacturer', 'type': 'text', 'required': False, 'order': 6, 'in_name': False, 'position': None},
        ],
        'item_name_format': '{generic_name} {brand} {dosage} {batch_number}'
    },
    'electronics': {
        'name': 'Electronics & Mobile',
        'description': 'For electronics and mobile phone stores',
        'attributes': [
            {'name': 'Brand', 'type': 'text', 'required': True, 'order': 1, 'in_name': True, 'position': 1},
            {'name': 'Model', 'type': 'text', 'required': True, 'order': 2, 'in_name': True, 'position': 2},
            {'name': 'Storage', 'type': 'dropdown', 'required': False, 'order': 3, 'in_name': True, 'position': 3,
             'options': ['64GB', '128GB', '256GB', '512GB', '1TB']},
            {'name': 'Color', 'type': 'dropdown', 'required': False, 'order': 4, 'in_name': True, 'position': 4,
             'options': ['Black', 'White', 'Blue', 'Silver', 'Gold', 'Green', 'Red']},
            {'name': 'IMEI', 'type': 'text', 'required': False, 'order': 5, 'in_name': False, 'position': None},
            {'name': 'Warranty (Months)', 'type': 'number', 'required': False, 'order': 6, 'in_name': False, 'position': None},
        ],
        'item_name_format': '{brand} {model} {storage} {color}'
    },
    'general': {
        'name': 'General Retail',
        'description': 'Basic setup for general stores',
        'attributes': [
            {'name': 'Brand', 'type': 'text', 'required': False, 'order': 1, 'in_name': True, 'position': 1},
            {'name': 'Category', 'type': 'text', 'required': True, 'order': 2, 'in_name': True, 'position': 2},
            {'name': 'Product', 'type': 'text', 'required': True, 'order': 3, 'in_name': True, 'position': 3},
        ],
        'item_name_format': '{brand} {category} {product}'
    }
}


# ============================================================
# MAIN SETTINGS PAGE
# ============================================================

@item_attributes_settings_bp.route('/admin/settings/item-attributes', methods=['GET'])
@require_tenant
def settings():
    """Main settings page for item attributes configuration"""
    tenant_id = g.tenant.id
    
    # Get tenant's configuration (if exists)
    config = TenantAttributeConfig.query.filter_by(tenant_id=tenant_id).first()
    
    # Get all attributes for this tenant
    attributes = ItemAttribute.query.filter_by(
        tenant_id=tenant_id,
        is_active=True
    ).order_by(ItemAttribute.display_order).all()
    
    # Check if any items have been created with attributes
    items_with_attributes = 0
    if attributes:
        items_with_attributes = db.session.execute(text("""
            SELECT COUNT(DISTINCT item_id)
            FROM item_attribute_values
            WHERE tenant_id = :tenant_id
        """), {'tenant_id': tenant_id}).fetchone()[0]
    
    return render_template('admin/settings/item_attributes.html',
        config=config,
        attributes=attributes,
        industry_presets=INDUSTRY_PRESETS,
        items_with_attributes=items_with_attributes
    )


# ============================================================
# ENABLE/DISABLE ATTRIBUTE SYSTEM
# ============================================================

@item_attributes_settings_bp.route('/admin/settings/item-attributes/toggle', methods=['POST'])
@require_tenant
def toggle_system():
    """Enable or disable the attribute system"""
    tenant_id = g.tenant.id
    enabled = request.form.get('enabled') == 'true'
    
    # Get or create config
    config = TenantAttributeConfig.query.filter_by(tenant_id=tenant_id).first()
    if not config:
        config = TenantAttributeConfig(tenant_id=tenant_id)
        db.session.add(config)
    
    config.is_enabled = enabled
    config.updated_at = datetime.now()
    db.session.commit()
    
    if enabled:
        flash('✅ Attribute system enabled! Configure your attributes below.', 'success')
    else:
        flash('⚠️ Attribute system disabled. Existing attributes are preserved.', 'warning')
    
    return redirect(url_for('item_attributes_settings.settings'))


# ============================================================
# APPLY INDUSTRY PRESET
# ============================================================

@item_attributes_settings_bp.route('/admin/settings/item-attributes/apply-preset', methods=['POST'])
@require_tenant
def apply_preset():
    """Apply an industry preset configuration"""
    tenant_id = g.tenant.id
    industry_type = request.form.get('industry_type')
    
    if industry_type not in INDUSTRY_PRESETS:
        flash('❌ Invalid industry type', 'error')
        return redirect(url_for('item_attributes_settings.settings'))
    
    preset = INDUSTRY_PRESETS[industry_type]
    
    try:
        # Get or create config
        config = TenantAttributeConfig.query.filter_by(tenant_id=tenant_id).first()
        if not config:
            config = TenantAttributeConfig(tenant_id=tenant_id)
            db.session.add(config)
        
        config.industry_type = industry_type
        config.item_name_format = preset['item_name_format']
        config.is_enabled = True
        config.updated_at = datetime.now()
        
        # Delete existing attributes (if user confirms)
        delete_existing = request.form.get('delete_existing') == 'true'
        if delete_existing:
            ItemAttribute.query.filter_by(tenant_id=tenant_id).delete()
        
        # Create attributes from preset
        for attr_data in preset['attributes']:
            attr = ItemAttribute(
                tenant_id=tenant_id,
                attribute_name=attr_data['name'],
                attribute_type=attr_data['type'],
                is_required=attr_data['required'],
                display_order=attr_data['order'],
                include_in_item_name=attr_data['in_name'],
                name_position=attr_data['position'],
                dropdown_options=attr_data.get('options'),
                is_active=True
            )
            db.session.add(attr)
        
        db.session.commit()
        
        flash(f'✅ {preset["name"]} preset applied successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error applying preset: {str(e)}', 'error')
    
    return redirect(url_for('item_attributes_settings.settings'))


# ============================================================
# ADD NEW ATTRIBUTE
# ============================================================

@item_attributes_settings_bp.route('/admin/settings/item-attributes/add', methods=['POST'])
@require_tenant
def add_attribute():
    """Add a new custom attribute"""
    tenant_id = g.tenant.id
    
    try:
        # Get form data
        attr_name = request.form.get('attribute_name')
        attr_type = request.form.get('attribute_type')
        is_required = request.form.get('is_required') == 'true'
        include_in_name = request.form.get('include_in_name') == 'true'
        dropdown_options_raw = request.form.get('dropdown_options', '')
        
        # Parse dropdown options (comma-separated)
        dropdown_options = None
        if attr_type == 'dropdown' and dropdown_options_raw:
            dropdown_options = [opt.strip() for opt in dropdown_options_raw.split(',') if opt.strip()]
        
        # Get next display order
        max_order = db.session.query(db.func.max(ItemAttribute.display_order))\
            .filter_by(tenant_id=tenant_id).scalar() or 0
        
        # Get next name position (if included in name)
        name_position = None
        if include_in_name:
            max_position = db.session.query(db.func.max(ItemAttribute.name_position))\
                .filter_by(tenant_id=tenant_id).scalar() or 0
            name_position = max_position + 1
        
        # Create attribute
        attr = ItemAttribute(
            tenant_id=tenant_id,
            attribute_name=attr_name,
            attribute_type=attr_type,
            is_required=is_required,
            display_order=max_order + 1,
            include_in_item_name=include_in_name,
            name_position=name_position,
            dropdown_options=dropdown_options,
            is_active=True
        )
        db.session.add(attr)
        db.session.commit()
        
        flash(f'✅ Attribute "{attr_name}" added successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error adding attribute: {str(e)}', 'error')
    
    return redirect(url_for('item_attributes_settings.settings'))


# ============================================================
# EDIT ATTRIBUTE
# ============================================================

@item_attributes_settings_bp.route('/admin/settings/item-attributes/<int:attr_id>/edit', methods=['POST'])
@require_tenant
def edit_attribute(attr_id):
    """Edit an existing attribute"""
    tenant_id = g.tenant.id
    
    try:
        attr = ItemAttribute.query.filter_by(id=attr_id, tenant_id=tenant_id).first_or_404()
        
        # Update fields
        attr.attribute_name = request.form.get('attribute_name', attr.attribute_name)
        attr.is_required = request.form.get('is_required') == 'true'
        attr.include_in_item_name = request.form.get('include_in_name') == 'true'
        
        # Update dropdown options (comes as JSON string from frontend)
        if attr.attribute_type == 'dropdown':
            dropdown_options_json = request.form.get('dropdown_options', '[]')
            try:
                import json
                options = json.loads(dropdown_options_json)
                attr.dropdown_options = [opt.strip() for opt in options if opt and opt.strip()]
            except:
                flash('⚠️ Invalid dropdown options format', 'warning')
        
        attr.updated_at = datetime.now()
        db.session.commit()
        
        flash(f'✅ Attribute "{attr.attribute_name}" updated successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error updating attribute: {str(e)}', 'error')
    
    return redirect(url_for('item_attributes_settings.settings'))


# ============================================================
# DELETE ATTRIBUTE
# ============================================================

@item_attributes_settings_bp.route('/admin/settings/item-attributes/delete/<int:attr_id>', methods=['POST'])
@require_tenant
def delete_attribute(attr_id):
    """Delete an attribute (soft delete)"""
    tenant_id = g.tenant.id
    
    try:
        attr = ItemAttribute.query.filter_by(id=attr_id, tenant_id=tenant_id).first_or_404()
        
        # Check if attribute has values
        values_count = ItemAttributeValue.query.filter_by(attribute_id=attr_id).count()
        
        if values_count > 0:
            # Soft delete (mark as inactive)
            attr.is_active = False
            attr.updated_at = datetime.now()
            flash(f'⚠️ Attribute "{attr.attribute_name}" deactivated ({values_count} items use it).', 'warning')
        else:
            # Hard delete (no items use it)
            db.session.delete(attr)
            flash(f'✅ Attribute "{attr.attribute_name}" deleted.', 'success')
        
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error deleting attribute: {str(e)}', 'error')
    
    return redirect(url_for('item_attributes_settings.settings'))


# ============================================================
# REORDER ATTRIBUTES
# ============================================================

@item_attributes_settings_bp.route('/admin/settings/item-attributes/reorder', methods=['POST'])
@require_tenant
def reorder_attributes():
    """Reorder attributes (for display and name generation)"""
    tenant_id = g.tenant.id
    
    try:
        # Get new order from JSON
        new_order = request.json.get('order', [])  # List of attribute IDs
        
        for idx, attr_id in enumerate(new_order):
            attr = ItemAttribute.query.filter_by(id=attr_id, tenant_id=tenant_id).first()
            if attr:
                attr.display_order = idx + 1
                if attr.include_in_item_name:
                    attr.name_position = idx + 1
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Attributes reordered successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================
# PREVIEW ITEM NAME
# ============================================================

@item_attributes_settings_bp.route('/admin/settings/item-attributes/preview', methods=['POST'])
@require_tenant
def preview_item_name():
    """Preview how item name will be generated"""
    tenant_id = g.tenant.id
    
    try:
        # Get sample values from request
        sample_values = request.json.get('values', {})
        
        # Get attributes that should be in name
        attributes = ItemAttribute.query.filter_by(
            tenant_id=tenant_id,
            is_active=True,
            include_in_item_name=True
        ).order_by(ItemAttribute.name_position).all()
        
        # Build item name
        name_parts = []
        for attr in attributes:
            value = sample_values.get(str(attr.id), '')
            if value:
                name_parts.append(value)
        
        generated_name = ' '.join(name_parts)
        
        return jsonify({
            'success': True,
            'generated_name': generated_name
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

