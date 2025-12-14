"""
Modular Business Management System
Main application entry point

Features:
- Attendance Management
- Inventory Management
- Multi-Site Support
- Modular Architecture (Flask Blueprints)
"""

from flask import Flask, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import os

# Import configuration
from config import Config

# Import database
from models import db, init_db

# Create Flask app
app = Flask(__name__)

# Load configuration
config = Config()
app.config['SECRET_KEY'] = config.SECRET_KEY

# Session configuration
from datetime import timedelta
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)  # Session lasts 2 hours
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True only in production HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent JavaScript access
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # CSRF protection
app.config['SESSION_REFRESH_EACH_REQUEST'] = True  # Reset timer on each activity

# Database configuration
# Use PostgreSQL (Supabase) in production, SQLite for local development
import os as os_module
basedir = os_module.path.abspath(os_module.path.dirname(__file__))

# Get DATABASE_URL from environment (Vercel provides this)
database_url = os_module.environ.get('DATABASE_URL')

# Fix postgres:// to postgresql:// (required by SQLAlchemy 1.4+)
if database_url and database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

# Use PostgreSQL if available, otherwise SQLite for local development
if database_url:
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    # Local development uses SQLite
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os_module.path.join(basedir, "instance", "app.db")}'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configure upload folders
app.config['SELFIE_FOLDER'] = config.SELFIE_FOLDER
app.config['DOCUMENT_FOLDER'] = config.DOCUMENT_FOLDER
app.config['INVENTORY_IMAGES_FOLDER'] = config.INVENTORY_IMAGES_FOLDER

# Create upload folders (only for local development, not on Vercel)
if not os.environ.get('VERCEL'):
    try:
        os.makedirs(config.SELFIE_FOLDER, exist_ok=True)
        os.makedirs(config.DOCUMENT_FOLDER, exist_ok=True)
        os.makedirs(config.INVENTORY_IMAGES_FOLDER, exist_ok=True)
        os.makedirs('instance', exist_ok=True)
    except (OSError, PermissionError) as e:
        print(f"⚠️  Could not create upload folders: {e}")
        print("💡 This is normal on serverless platforms (Vercel)")
        print("📦 Files will be stored in database or cloud storage (S3/R2)")

# Initialize database
init_db(app)

# ============================================================
# Multi-tenant middleware
# ============================================================
from utils.tenant_middleware import load_tenant

@app.before_request
def before_request():
    """Load tenant on every request based on subdomain"""
    load_tenant()

# ============================================================
# Import and register blueprints
# ============================================================
from routes.registration import registration_bp
from routes.attendance import attendance_bp
from routes.inventory import inventory_bp
from routes.admin import admin_bp
from routes.migration import migration_bp
from routes.add_indexes import add_indexes_bp  # NEW: Performance optimization indexes
from routes.optimize_db import optimize_db_bp  # NEW: Database optimization & diagnostics
from routes.superadmin import superadmin_bp
from routes.items import items_bp  # NEW: Professional items management
from routes.expenses import expenses_bp  # NEW: Expenses tracking
from routes.purchase_requests import purchase_request_bp, admin_purchase_bp  # NEW: Purchase requests
from routes.customers import customers_bp  # NEW: Customer management
from routes.vendors import vendors_bp  # NEW: Vendor management
from routes.invoices import invoices_bp  # NEW: GST Invoicing
from routes.tasks import tasks_bp  # NEW: Task management (admin)
from routes.employee_tasks import employee_tasks_bp  # NEW: Task management (employee)
from routes.employee_portal import employee_portal_bp  # NEW: Unified employee portal
from routes.sales_orders import sales_order_bp  # NEW: Sales Order management
from routes.delivery_challans import delivery_challan_bp  # NEW: Delivery Challan management
from routes.gst_reports import gst_reports_bp  # NEW: GST Reports
from routes.purchase_bills import purchase_bills_bp  # NEW: Purchase Bills management
from routes.backup import backup_bp  # NEW: Backup & Restore
from routes.subscription_migration import subscription_migration_bp  # NEW: Subscription management migration
from routes.subscriptions import subscriptions_bp  # NEW: Subscription management
from routes.subscription_indexes import subscription_indexes_bp  # NEW: Subscription performance indexes
from routes.sku_migration import sku_migration_bp  # NEW: SKU constraint migration (global → per-tenant)
from routes.password_reset_migration import password_reset_migration_bp  # NEW: Secure password reset tokens
from routes.customer_portal import customer_portal_bp  # NEW: Customer self-service portal
from routes.customer_orders import customer_orders_bp  # NEW: Customer orders admin
from routes.employee_delivery import employee_delivery_bp  # NEW: Employee delivery portal with bottle tracking
from routes.accounts import accounts_bp  # NEW: Bank/Cash Account Management (Phase 1)
from routes.payroll import payroll_bp  # NEW: Payroll Management
from routes.mrp_discount_migration import mrp_discount_migration_bp  # NEW: MRP & Discount features
from routes.site_default_migration import site_default_migration_bp  # NEW: Default site feature
from routes.barcode_migration import barcode_migration_bp  # NEW: Barcode scanner feature
from routes.barcode_api import barcode_api_bp  # NEW: Barcode API endpoints
from routes.loyalty_migration import loyalty_migration_bp  # NEW: Loyalty program feature
from routes.loyalty import loyalty_bp  # NEW: Loyalty program API & admin pages
from routes.loyalty_features_migration import loyalty_features_bp  # NEW: Loyalty birthday/anniversary + tiers
from routes.tier_benefits_migration import tier_benefits_bp  # NEW: Tier benefits (earning/redemption multipliers)
from routes.vendor_performance_migration import vendor_performance_bp  # NEW: Vendor performance optimization
from routes.fix_attendance_cascade import fix_cascade_bp  # FIX: Attendance CASCADE delete

app.register_blueprint(registration_bp)
app.register_blueprint(employee_portal_bp)  # Register unified portal
app.register_blueprint(attendance_bp)
app.register_blueprint(inventory_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(migration_bp)
app.register_blueprint(add_indexes_bp)  # Performance optimization indexes
app.register_blueprint(optimize_db_bp)  # Database optimization & diagnostics
app.register_blueprint(superadmin_bp)
app.register_blueprint(items_bp)  # NEW: Register items blueprint
app.register_blueprint(expenses_bp)  # NEW: Register expenses blueprint
app.register_blueprint(purchase_request_bp)  # NEW: Employee purchase requests
app.register_blueprint(admin_purchase_bp)  # NEW: Admin purchase management
app.register_blueprint(customers_bp)  # NEW: Customer management
app.register_blueprint(vendors_bp)  # NEW: Vendor management
app.register_blueprint(invoices_bp)  # NEW: GST invoicing
from routes.returns import returns_bp
app.register_blueprint(returns_bp)  # NEW: Returns & Refunds management
app.register_blueprint(tasks_bp)  # NEW: Task management (admin)
app.register_blueprint(employee_tasks_bp)  # NEW: Task management (employee)
app.register_blueprint(sales_order_bp)  # NEW: Sales Order management
app.register_blueprint(delivery_challan_bp)  # NEW: Delivery Challan management
app.register_blueprint(gst_reports_bp)  # NEW: GST Reports
app.register_blueprint(purchase_bills_bp)  # NEW: Purchase Bills management
app.register_blueprint(backup_bp)  # NEW: Backup & Restore
app.register_blueprint(subscription_migration_bp)  # NEW: Subscription management migration
app.register_blueprint(subscriptions_bp)  # NEW: Subscription management
app.register_blueprint(subscription_indexes_bp)  # NEW: Subscription performance indexes
app.register_blueprint(sku_migration_bp)  # NEW: SKU constraint migration
app.register_blueprint(password_reset_migration_bp)  # NEW: Secure password reset tokens
app.register_blueprint(customer_portal_bp)  # NEW: Customer self-service portal
app.register_blueprint(customer_orders_bp)  # NEW: Customer orders admin
app.register_blueprint(employee_delivery_bp)  # NEW: Employee delivery portal  # NEW: Customer orders admin
app.register_blueprint(accounts_bp)  # NEW: Bank/Cash Account Management (Phase 1)
app.register_blueprint(payroll_bp)  # NEW: Payroll Management
app.register_blueprint(mrp_discount_migration_bp)  # NEW: MRP & Discount features
app.register_blueprint(site_default_migration_bp)  # NEW: Default site feature
app.register_blueprint(barcode_migration_bp)  # NEW: Barcode scanner feature
app.register_blueprint(barcode_api_bp)  # NEW: Barcode API endpoints
app.register_blueprint(loyalty_migration_bp)  # NEW: Loyalty program migration
app.register_blueprint(loyalty_bp)  # NEW: Loyalty program API & admin pages
app.register_blueprint(loyalty_features_bp)  # NEW: Loyalty birthday/anniversary + tiers
app.register_blueprint(tier_benefits_bp)  # NEW: Tier benefits (earning/redemption multipliers)
from routes.fix_inventory_equity import fix_inventory_equity_bp
app.register_blueprint(fix_inventory_equity_bp)  # FIX: Create missing inventory equity entries
app.register_blueprint(vendor_performance_bp)  # NEW: Vendor performance optimization
app.register_blueprint(fix_cascade_bp)  # FIX: Attendance CASCADE delete issue
from routes.migrate_double_entry import migrate_double_entry_bp
app.register_blueprint(migrate_double_entry_bp)  # MIGRATION: Convert to double-entry accounting
from routes.fix_vendor_payment_constraint import fix_vendor_payment_bp
app.register_blueprint(fix_vendor_payment_bp)  # FIX: Vendor payment constraint (tenant-specific)
from routes.fix_purchase_bill_constraint import fix_purchase_bill_bp
app.register_blueprint(fix_purchase_bill_bp)  # FIX: Purchase bill constraint (tenant-specific)
from routes.fix_return_accounting import fix_return_accounting_bp
app.register_blueprint(fix_return_accounting_bp)  # FIX: Add missing refund entries for returns
from routes.diagnose_returns import diagnose_returns_bp
app.register_blueprint(diagnose_returns_bp)  # DIAGNOSTIC: Check returns accounting status

from routes.diagnose_commission import diagnose_commission_bp
app.register_blueprint(diagnose_commission_bp)  # DIAGNOSTIC: Check commission status

from routes.fix_commission_for_returns import fix_commission_for_returns_bp
app.register_blueprint(fix_commission_for_returns_bp)  # MIGRATION: Fix commission amounts for existing returns

from routes.diagnose_return_amounts import diagnose_return_amounts_bp
app.register_blueprint(diagnose_return_amounts_bp)  # DIAGNOSTIC: Check return amounts and rounding
from routes.diagnose_trial_balance import diagnose_trial_bp
app.register_blueprint(diagnose_trial_bp)  # DIAGNOSTIC: Check trial balance components
from routes.migration_add_purchase_bill_item_fields import migration_purchase_bill_items_bp
app.register_blueprint(migration_purchase_bill_items_bp)  # MIGRATION: Add fields for creating items from purchase bills
from routes.migration_create_returns_tables import migration_returns_bp
app.register_blueprint(migration_returns_bp)  # MIGRATION: Create returns & refunds tables

# ============================================================
# Main route
# ============================================================
@app.route('/')
def index():
    """Main landing page"""
    from flask import g
    
    # Check if tenant subdomain is present
    tenant = getattr(g, 'tenant', None)
    
    if tenant:
        # If accessing with subdomain, redirect to admin dashboard
        return redirect(url_for('admin.dashboard'))
    
    # Base domain - show landing page
    return render_template('index.html')

@app.route('/selfie/<filename>')
def selfie(filename):
    """Serve selfie photos"""
    from flask import send_from_directory
    import os
    selfie_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads', 'selfies')
    return send_from_directory(selfie_dir, filename)

@app.route('/uploads/purchase_bills/<int:tenant_id>/<filename>')
def purchase_bill_document(tenant_id, filename):
    """Serve purchase bill documents"""
    from flask import send_from_directory
    import os
    upload_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads', 'purchase_bills', str(tenant_id))
    return send_from_directory(upload_dir, filename)

# ============================================================
# Health check endpoint (keep serverless function warm)
# ============================================================
@app.route('/health')
def health_check():
    """Simple health check endpoint - keeps Vercel function warm"""
    from flask import jsonify
    import datetime
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.datetime.utcnow().isoformat(),
        'message': 'BizBooks is running'
    }), 200

# Welcome page for documentation
@app.route('/welcome')
def welcome():
    """Welcome page with setup info"""
    return """
    <html>
    <head>
        <title>Modular Business Management System</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
                background: #f5f5f5;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 {
                color: #2c3e50;
                border-bottom: 3px solid #3498db;
                padding-bottom: 10px;
            }
            .success {
                background: #d4edda;
                border: 1px solid #c3e6cb;
                color: #155724;
                padding: 15px;
                border-radius: 5px;
                margin: 20px 0;
            }
            .info {
                background: #d1ecf1;
                border: 1px solid #bee5eb;
                color: #0c5460;
                padding: 15px;
                border-radius: 5px;
                margin: 20px 0;
            }
            .feature {
                background: #f8f9fa;
                padding: 15px;
                margin: 10px 0;
                border-left: 4px solid #3498db;
                border-radius: 3px;
            }
            code {
                background: #f4f4f4;
                padding: 2px 6px;
                border-radius: 3px;
                font-family: 'Courier New', monospace;
            }
            .command {
                background: #2c3e50;
                color: #ecf0f1;
                padding: 15px;
                border-radius: 5px;
                margin: 10px 0;
                font-family: 'Courier New', monospace;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎉 Modular Business Management System</h1>
            
            <div class="success">
                <strong>✅ System is Running!</strong><br>
                Database initialized successfully. Your modular app is ready!
            </div>
            
            <h2>📦 Features Available:</h2>
            <div class="feature">
                <strong>✅ Attendance Management</strong><br>
                PIN + Selfie authentication, Location tracking, Multi-site support
            </div>
            <div class="feature">
                <strong>✅ Inventory Management</strong><br>
                Material tracking, Stock in/out, Inter-site transfers, Low stock alerts
            </div>
            <div class="feature">
                <strong>✅ Multi-Site Support</strong><br>
                Manage multiple locations, Site-specific inventory and attendance
            </div>
            <div class="feature">
                <strong>✅ Modular Architecture</strong><br>
                Easy to add new features, Flask Blueprints, Organized code
            </div>
            
            <h2>🚀 Next Steps:</h2>
            <div class="info">
                <strong>1. Create Routes/Blueprints</strong><br>
                Create files in <code>routes/</code> folder for each feature:<br>
                <div class="command">
                    routes/auth.py         # Login/logout<br>
                    routes/attendance.py   # Attendance feature<br>
                    routes/inventory.py    # Inventory feature<br>
                    routes/admin.py        # Admin dashboard
                </div>
                
                <strong>2. Create Templates</strong><br>
                Create HTML files in <code>templates/</code> folder<br><br>
                
                <strong>3. Register Blueprints</strong><br>
                In <code>app.py</code>, import and register your blueprints<br><br>
                
                <strong>4. Test Everything</strong><br>
                Access your routes and verify functionality
            </div>
            
            <h2>📚 Documentation:</h2>
            <ul>
                <li><code>README.md</code> - Complete architecture overview</li>
                <li><code>WHAT_IM_CREATING.md</code> - Detailed explanation</li>
                <li><code>QUICK_START.md</code> - Quick start guide (coming next!)</li>
            </ul>
            
            <h2>🗄️ Database Status:</h2>
            <div class="info">
                <strong>Models Created:</strong><br>
                ✅ User (Admin authentication)<br>
                ✅ Site (Multiple locations)<br>
                ✅ Employee (PIN-based)<br>
                ✅ Attendance (Check-in/out)<br>
                ✅ Material (Inventory items)<br>
                ✅ Stock (Stock per site)<br>
                ✅ StockMovement (History)<br>
                ✅ Transfer (Inter-site)<br><br>
                
                <strong>Default Admin Created:</strong><br>
                Username: <code>admin</code><br>
                Password: <code>admin123</code> (⚠️ Change this!)
            </div>
            
            <h2>💡 Quick Example:</h2>
            <p>To add attendance feature, create <code>routes/attendance.py</code>:</p>
            <div class="command">
from flask import Blueprint<br>
<br>
attendance_bp = Blueprint('attendance', __name__)<br>
<br>
@attendance_bp.route('/attendance')<br>
def index():<br>
    return "Attendance page!"<br>
<br>
# Then register in app.py:<br>
# from routes.attendance import attendance_bp<br>
# app.register_blueprint(attendance_bp)
            </div>
            
            <hr>
            <p style="text-align: center; color: #7f8c8d;">
                <strong>Modular Business Management System v2.0</strong><br>
                Built with Flask + SQLAlchemy + Modular Architecture<br>
                Ready for enterprise deployment! 🚀
            </p>
        </div>
    </body>
    </html>
    """


# ============================================================
# Database inspection route (for development)
# ============================================================
@app.route('/db-info')
def db_info():
    """Show database information"""
    from models import User, Site, Employee, Material
    
    try:
        user_count = User.query.count()
        site_count = Site.query.count()
        employee_count = Employee.query.count()
        material_count = Material.query.count()
        
        return f"""
        <html>
        <body style="font-family: Arial; padding: 20px;">
            <h2>Database Information</h2>
            <ul>
                <li>Users: {user_count}</li>
                <li>Sites: {site_count}</li>
                <li>Employees: {employee_count}</li>
                <li>Materials: {material_count}</li>
            </ul>
            <p><a href="/">← Back to Home</a></p>
        </body>
        </html>
        """
    except Exception as e:
        return f"Error: {str(e)}"


# ============================================================
# Run application
# ============================================================
if __name__ == '__main__':
    # Get port from environment (for Render/Railway) or use config
    port = int(os.environ.get('PORT', config.PORT))
    host = os.environ.get('HOST', config.HOST)
    
    # SSL is handled by cloud platforms (Render/Railway)
    # Only use SSL for local development
    ssl_context = None
    if os.path.exists('cert.pem') and os.path.exists('key.pem'):
        ssl_context = ('cert.pem', 'key.pem')
        print("🔒 Running with HTTPS (SSL enabled)")
    else:
        print("⚠️  Running without HTTPS (SSL handled by hosting platform)")
    
    # Run app
    print(f"\n{'='*60}")
    print(f"🚀 Modular Business Management System")
    print(f"{'='*60}")
    print(f"📍 Host: {host}:{port}")
    print(f"🗄️  Database: {config.DATABASE_URI}")
    print(f"👤 Default Admin: admin / admin123")
    print(f"{'='*60}\n")
    
    app.run(
        host=host,
        port=port,
        debug=config.DEBUG,
        ssl_context=ssl_context
    )

