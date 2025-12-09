"""
Loyalty Program API Routes
Admin and customer endpoints for loyalty program
"""
from flask import Blueprint, render_template, request, jsonify, g, redirect, url_for, flash
from functools import wraps
from models import db
from models.loyalty_program import LoyaltyProgram
from models.customer_loyalty_points import CustomerLoyaltyPoints
from models.loyalty_transaction import LoyaltyTransaction
from models.customer import Customer
from services.loyalty_service import LoyaltyService
from datetime import datetime

loyalty_bp = Blueprint('loyalty', __name__, url_prefix='/admin/loyalty')

def login_required(f):
    """Decorator to ensure user is logged in"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not hasattr(g, 'user') or not g.user:
            flash('Please login to access this page', 'error')
            return redirect(url_for('registration.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to ensure user is admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not hasattr(g, 'user') or not g.user or g.user.role != 'admin':
            flash('Admin access required', 'error')
            return redirect(url_for('admin.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# ============================================================
# Admin Settings Pages
# ============================================================

@loyalty_bp.route('/settings')
@login_required
@admin_required
def settings():
    """Loyalty program settings page"""
    tenant_id = g.tenant.id if hasattr(g, 'tenant') else None
    
    if not tenant_id:
        flash('Tenant not found', 'error')
        return redirect(url_for('admin.dashboard'))
    
    # Get or create loyalty program
    program = LoyaltyProgram.query.filter_by(tenant_id=tenant_id).first()
    
    if not program:
        # Create default program
        program = LoyaltyProgram(
            tenant_id=tenant_id,
            program_name='Loyalty Program',
            is_active=False,
            points_per_100_rupees=1.00,
            minimum_purchase_for_points=0,
            enable_threshold_bonuses=False,
            points_to_rupees_ratio=1.00,
            minimum_points_to_redeem=10,
            show_points_on_invoice=True
        )
        db.session.add(program)
        db.session.commit()
    
    return render_template('admin/loyalty/settings.html', program=program)

@loyalty_bp.route('/settings/update', methods=['POST'])
@login_required
@admin_required
def update_settings():
    """Update loyalty program settings"""
    tenant_id = g.tenant.id if hasattr(g, 'tenant') else None
    
    if not tenant_id:
        return jsonify({'error': 'Tenant not found'}), 400
    
    program = LoyaltyProgram.query.filter_by(tenant_id=tenant_id).first()
    
    if not program:
        return jsonify({'error': 'Loyalty program not found'}), 404
    
    try:
        # Basic settings
        program.program_name = request.form.get('program_name', 'Loyalty Program')
        program.is_active = request.form.get('is_active') == 'on'
        
        # Earning rules
        program.points_per_100_rupees = float(request.form.get('points_per_100_rupees', 1.0))
        program.minimum_purchase_for_points = float(request.form.get('minimum_purchase_for_points', 0))
        program.maximum_points_per_invoice = int(request.form.get('maximum_points_per_invoice')) if request.form.get('maximum_points_per_invoice') else None
        
        # Threshold bonuses
        program.enable_threshold_bonuses = request.form.get('enable_threshold_bonuses') == 'on'
        program.threshold_1_amount = float(request.form.get('threshold_1_amount')) if request.form.get('threshold_1_amount') else None
        program.threshold_1_bonus_points = int(request.form.get('threshold_1_bonus_points')) if request.form.get('threshold_1_bonus_points') else None
        program.threshold_2_amount = float(request.form.get('threshold_2_amount')) if request.form.get('threshold_2_amount') else None
        program.threshold_2_bonus_points = int(request.form.get('threshold_2_bonus_points')) if request.form.get('threshold_2_bonus_points') else None
        program.threshold_3_amount = float(request.form.get('threshold_3_amount')) if request.form.get('threshold_3_amount') else None
        program.threshold_3_bonus_points = int(request.form.get('threshold_3_bonus_points')) if request.form.get('threshold_3_bonus_points') else None
        
        # Redemption rules
        program.points_to_rupees_ratio = float(request.form.get('points_to_rupees_ratio', 1.0))
        program.minimum_points_to_redeem = int(request.form.get('minimum_points_to_redeem', 10))
        program.maximum_discount_percent = float(request.form.get('maximum_discount_percent')) if request.form.get('maximum_discount_percent') else None
        program.maximum_points_per_redemption = int(request.form.get('maximum_points_per_redemption')) if request.form.get('maximum_points_per_redemption') else None
        
        # Display
        program.show_points_on_invoice = request.form.get('show_points_on_invoice') == 'on'
        program.invoice_footer_text = request.form.get('invoice_footer_text', 'Points Balance: {balance} pts | Next visit: ₹{value} off!')
        
        program.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        flash('✅ Loyalty program settings updated successfully!', 'success')
        return redirect(url_for('loyalty.settings'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error updating settings: {str(e)}', 'error')
        return redirect(url_for('loyalty.settings'))

# ============================================================
# Admin Reports & Analytics
# ============================================================

@loyalty_bp.route('/reports')
@login_required
@admin_required
def reports():
    """Loyalty program reports and analytics"""
    tenant_id = g.tenant.id if hasattr(g, 'tenant') else None
    
    if not tenant_id:
        flash('Tenant not found', 'error')
        return redirect(url_for('admin.dashboard'))
    
    stats = LoyaltyService.get_loyalty_stats(tenant_id)
    
    if not stats:
        flash('Loyalty program not configured', 'warning')
        return redirect(url_for('loyalty.settings'))
    
    # Get top customers with full details
    top_customers_data = []
    for customer_data in stats['top_customers']:
        customer = Customer.query.get(customer_data['customer_id'])
        if customer:
            loyalty = CustomerLoyaltyPoints.query.filter_by(
                customer_id=customer.id,
                tenant_id=tenant_id
            ).first()
            top_customers_data.append({
                'customer': customer,
                'loyalty': loyalty
            })
    
    return render_template('admin/loyalty/reports.html', 
                         stats=stats, 
                         top_customers=top_customers_data)

# ============================================================
# Customer Points Management
# ============================================================

@loyalty_bp.route('/customer/<int:customer_id>/balance')
@login_required
def customer_balance(customer_id):
    """Get customer's loyalty points balance"""
    tenant_id = g.tenant.id if hasattr(g, 'tenant') else None
    
    if not tenant_id:
        return jsonify({'error': 'Tenant not found'}), 400
    
    loyalty = LoyaltyService.get_customer_balance(customer_id, tenant_id, auto_create=False)
    
    if not loyalty:
        return jsonify({
            'current_points': 0,
            'lifetime_earned': 0,
            'lifetime_redeemed': 0,
            'is_member': False
        })
    
    return jsonify({
        'current_points': loyalty.current_points,
        'lifetime_earned': loyalty.lifetime_earned_points,
        'lifetime_redeemed': loyalty.lifetime_redeemed_points,
        'is_member': True,
        'last_earned_at': loyalty.last_earned_at.isoformat() if loyalty.last_earned_at else None,
        'last_redeemed_at': loyalty.last_redeemed_at.isoformat() if loyalty.last_redeemed_at else None
    })

@loyalty_bp.route('/customer/<int:customer_id>/history')
@login_required
def customer_history(customer_id):
    """Get customer's loyalty transaction history"""
    tenant_id = g.tenant.id if hasattr(g, 'tenant') else None
    
    if not tenant_id:
        return jsonify({'error': 'Tenant not found'}), 400
    
    limit = request.args.get('limit', 50, type=int)
    transactions = LoyaltyService.get_transaction_history(customer_id, tenant_id, limit)
    
    return jsonify({'transactions': transactions})

@loyalty_bp.route('/customer/<int:customer_id>/adjust', methods=['POST'])
@login_required
@admin_required
def adjust_customer_points(customer_id):
    """Manually adjust customer points (admin only)"""
    tenant_id = g.tenant.id if hasattr(g, 'tenant') else None
    
    if not tenant_id:
        return jsonify({'error': 'Tenant not found'}), 400
    
    try:
        points = int(request.form.get('points', 0))
        description = request.form.get('description', 'Manual adjustment')
        
        if points == 0:
            return jsonify({'error': 'Points cannot be zero'}), 400
        
        loyalty = LoyaltyService.adjust_points(
            customer_id=customer_id,
            tenant_id=tenant_id,
            points=points,
            description=description,
            created_by=g.user.id if hasattr(g, 'user') else None
        )
        
        return jsonify({
            'success': True,
            'message': f'Points adjusted by {points}',
            'new_balance': loyalty.current_points
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# ============================================================
# API Endpoints (for AJAX calls from frontend)
# ============================================================

@loyalty_bp.route('/api/calculate-points', methods=['POST'])
@login_required
def calculate_points_api():
    """Calculate points for a given invoice amount"""
    tenant_id = g.tenant.id if hasattr(g, 'tenant') else None
    
    if not tenant_id:
        return jsonify({'error': 'Tenant not found'}), 400
    
    try:
        amount = float(request.json.get('amount', 0))
        result = LoyaltyService.calculate_points_earned(amount, tenant_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@loyalty_bp.route('/api/calculate-redemption', methods=['POST'])
@login_required
def calculate_redemption_api():
    """Calculate discount value for given points"""
    tenant_id = g.tenant.id if hasattr(g, 'tenant') else None
    
    if not tenant_id:
        return jsonify({'error': 'Tenant not found'}), 400
    
    try:
        points = int(request.json.get('points', 0))
        discount_value = LoyaltyService.calculate_redemption_value(points, tenant_id)
        return jsonify({'discount_value': discount_value})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@loyalty_bp.route('/api/validate-redemption', methods=['POST'])
@login_required
def validate_redemption_api():
    """Validate if redemption is possible"""
    tenant_id = g.tenant.id if hasattr(g, 'tenant') else None
    
    if not tenant_id:
        return jsonify({'error': 'Tenant not found'}), 400
    
    try:
        customer_id = int(request.json.get('customer_id'))
        points = int(request.json.get('points'))
        invoice_subtotal = float(request.json.get('invoice_subtotal', 0))
        
        # Get program and loyalty
        program = LoyaltyService.get_loyalty_program(tenant_id)
        loyalty = LoyaltyService.get_customer_balance(customer_id, tenant_id, auto_create=False)
        
        if not program or not program.is_active:
            return jsonify({'valid': False, 'error': 'Loyalty program not active'})
        
        if not loyalty:
            return jsonify({'valid': False, 'error': 'Customer has no loyalty account'})
        
        # Check minimum points
        if points < (program.minimum_points_to_redeem or 10):
            return jsonify({'valid': False, 'error': f'Minimum {program.minimum_points_to_redeem or 10} points required'})
        
        # Check sufficient balance
        if points > loyalty.current_points:
            return jsonify({'valid': False, 'error': f'Insufficient points. Available: {loyalty.current_points}'})
        
        # Check maximum points per redemption
        if program.maximum_points_per_redemption and points > program.maximum_points_per_redemption:
            return jsonify({'valid': False, 'error': f'Maximum {program.maximum_points_per_redemption} points per redemption'})
        
        # Calculate discount
        discount_value = LoyaltyService.calculate_redemption_value(points, tenant_id)
        
        # Check maximum discount percent
        if program.maximum_discount_percent and invoice_subtotal > 0:
            max_discount = invoice_subtotal * (float(program.maximum_discount_percent) / 100)
            if discount_value > max_discount:
                return jsonify({'valid': False, 'error': f'Discount exceeds maximum {program.maximum_discount_percent}% of invoice'})
        
        return jsonify({
            'valid': True,
            'discount_value': discount_value,
            'points_to_redeem': points
        })
        
    except Exception as e:
        return jsonify({'valid': False, 'error': str(e)})

@loyalty_bp.route('/api/program-status')
@login_required
def program_status_api():
    """Get loyalty program status for current tenant"""
    tenant_id = g.tenant.id if hasattr(g, 'tenant') else None
    
    if not tenant_id:
        return jsonify({'error': 'Tenant not found'}), 400
    
    program = LoyaltyService.get_loyalty_program(tenant_id)
    
    if not program:
        return jsonify({'is_active': False, 'exists': False})
    
    return jsonify({
        'is_active': program.is_active,
        'exists': True,
        'program_name': program.program_name,
        'points_per_100': float(program.points_per_100_rupees),
        'points_to_rupees': float(program.points_to_rupees_ratio)
    })

