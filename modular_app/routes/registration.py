"""
Tenant registration routes
Allows new businesses to sign up for BizBooks
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, Tenant, Site
import hashlib
import re

registration_bp = Blueprint('registration', __name__, url_prefix='/register')

def is_valid_subdomain(subdomain):
    """Check if subdomain is valid (lowercase letters, numbers, hyphens only)"""
    # Only allow lowercase letters, numbers, and hyphens
    # Must start with a letter, 3-20 characters
    pattern = r'^[a-z][a-z0-9-]{2,19}$'
    return bool(re.match(pattern, subdomain))

def subdomain_exists(subdomain):
    """Check if subdomain already exists"""
    return Tenant.query.filter_by(subdomain=subdomain).first() is not None

def email_exists(email):
    """Check if email already registered"""
    return Tenant.query.filter_by(admin_email=email).first() is not None

@registration_bp.route('/', methods=['GET', 'POST'])
def index():
    """Registration form"""
    if request.method == 'POST':
        # Get form data
        company_name = request.form.get('company_name', '').strip()
        subdomain = request.form.get('subdomain', '').strip().lower()
        admin_name = request.form.get('admin_name', '').strip()
        admin_email = request.form.get('admin_email', '').strip().lower()
        admin_phone = request.form.get('admin_phone', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validation
        errors = []
        
        if not company_name or len(company_name) < 2:
            errors.append("Company name must be at least 2 characters")
        
        if not subdomain:
            errors.append("Please choose a subdomain")
        elif not is_valid_subdomain(subdomain):
            errors.append("Subdomain must be 3-20 characters, start with a letter, and contain only lowercase letters, numbers, and hyphens")
        elif subdomain in ['www', 'admin', 'api', 'app', 'mail', 'ftp', 'test', 'staging', 'dev', 'prod']:
            errors.append("This subdomain is reserved")
        elif subdomain_exists(subdomain):
            errors.append(f"Subdomain '{subdomain}' is already taken. Try '{subdomain}2' or '{subdomain}-{company_name.split()[0].lower()}'")
        
        if not admin_name or len(admin_name) < 2:
            errors.append("Admin name must be at least 2 characters")
        
        if not admin_email or '@' not in admin_email:
            errors.append("Please enter a valid email address")
        elif email_exists(admin_email):
            errors.append("This email is already registered")
        
        if not password or len(password) < 6:
            errors.append("Password must be at least 6 characters")
        elif password != confirm_password:
            errors.append("Passwords do not match")
        
        # If errors, show them
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('registration/form.html',
                                 company_name=company_name,
                                 subdomain=subdomain,
                                 admin_name=admin_name,
                                 admin_email=admin_email,
                                 admin_phone=admin_phone)
        
        # Hash password
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        # Create tenant
        try:
            tenant = Tenant(
                company_name=company_name,
                subdomain=subdomain,
                admin_name=admin_name,
                admin_email=admin_email,
                admin_phone=admin_phone,
                admin_password_hash=password_hash,
                plan='trial',
                status='active',
                max_employees=50,  # Free trial: 50 employees
                max_sites=5
            )
            db.session.add(tenant)
            db.session.flush()  # Get tenant.id
            
            # Create default site for tenant
            default_site = Site(
                tenant_id=tenant.id,
                name=f"{company_name} - Main Office",
                address="",
                latitude=0.0,
                longitude=0.0,
                radius=100,
                active=True
            )
            db.session.add(default_site)
            
            db.session.commit()
            
            flash(f'🎉 Welcome to BizBooks! Your account has been created successfully!', 'success')
            flash(f'Trial period: {tenant.days_remaining} days remaining', 'info')
            
            # Redirect to their subdomain (use current host's base domain)
            # For local testing: subdomain.lvh.me:5001
            # For production: subdomain.bizbooks.co.in
            current_host = request.host  # e.g., "lvh.me:5001" or "bizbooks.co.in"
            scheme = request.scheme  # http or https
            
            # If accessing via localhost, use lvh.me for subdomain
            if 'localhost' in current_host or '127.0.0.1' in current_host:
                base_domain = 'lvh.me:5001'
            else:
                base_domain = current_host.split('.', 1)[1] if '.' in current_host else current_host
            
            return redirect(f"{scheme}://{subdomain}.{base_domain}/admin/login")
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating account: {str(e)}', 'error')
            return render_template('registration/form.html',
                                 company_name=company_name,
                                 subdomain=subdomain,
                                 admin_name=admin_name,
                                 admin_email=admin_email,
                                 admin_phone=admin_phone)
    
    # GET - show form
    return render_template('registration/form.html')


@registration_bp.route('/check-subdomain', methods=['POST'])
def check_subdomain():
    """AJAX endpoint to check if subdomain is available"""
    import json
    subdomain = request.form.get('subdomain', '').strip().lower()
    
    if not subdomain:
        return json.dumps({'available': False, 'message': 'Please enter a subdomain'})
    
    if not is_valid_subdomain(subdomain):
        return json.dumps({'available': False, 'message': 'Invalid format (3-20 chars, letters/numbers/hyphens only)'})
    
    if subdomain in ['www', 'admin', 'api', 'app', 'mail', 'ftp', 'test', 'staging', 'dev', 'prod']:
        return json.dumps({'available': False, 'message': 'This subdomain is reserved'})
    
    if subdomain_exists(subdomain):
        return json.dumps({'available': False, 'message': f'"{subdomain}" is already taken'})
    
    return json.dumps({'available': True, 'message': f'✓ {subdomain}.bizbooks.co.in is available!'})

