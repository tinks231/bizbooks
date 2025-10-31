"""
One-time migration routes for database updates
Access these URLs once after deployment to migrate the database
"""
from flask import Blueprint, jsonify
from models import db
from sqlalchemy import text

migration_bp = Blueprint('migration', __name__, url_prefix='/migrate')

@migration_bp.route('/recreate-all-tables')
def recreate_all_tables():
    """
    DROP and RECREATE all tables with correct schema
    ⚠️ WARNING: This will DELETE ALL DATA!
    Access this URL once: /migrate/recreate-all-tables
    """
    try:
        # Drop all tables
        db.drop_all()
        
        # Recreate all tables with correct schema
        db.create_all()
        
        return jsonify({
            'status': 'success',
            'message': '✅ All tables recreated successfully!',
            'action': 'Tables dropped and recreated with latest schema',
            'next_step': 'Your app should work now! Go to /register to create a new account.'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Recreation failed: {str(e)}',
            'details': str(e)
        }), 500

@migration_bp.route('/rename-radius-to-allowed-radius')
def migrate_radius_column():
    """
    Rename 'radius' to 'allowed_radius' in sites table
    Access this URL once: /migrate/rename-radius-to-allowed-radius
    """
    try:
        # Check if we're using PostgreSQL
        db_url = db.engine.url.drivername
        
        if 'postgresql' in db_url:
            # Check if 'allowed_radius' already exists
            check_sql = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='sites' AND column_name='allowed_radius'
            """)
            result = db.session.execute(check_sql).fetchone()
            
            if result:
                return jsonify({
                    'status': 'success',
                    'message': '✅ Column "allowed_radius" already exists - migration not needed!',
                    'action': 'none'
                })
            
            # Check if 'radius' exists
            check_old_sql = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='sites' AND column_name='radius'
            """)
            old_result = db.session.execute(check_old_sql).fetchone()
            
            if old_result:
                # Rename column
                migrate_sql = text("""
                    ALTER TABLE sites 
                    RENAME COLUMN radius TO allowed_radius
                """)
                db.session.execute(migrate_sql)
                db.session.commit()
                
                return jsonify({
                    'status': 'success',
                    'message': '✅ Successfully renamed "radius" to "allowed_radius"!',
                    'action': 'renamed',
                    'next_step': 'Refresh your app - it should work now!'
                })
            else:
                # Neither column exists - add new one
                add_sql = text("""
                    ALTER TABLE sites 
                    ADD COLUMN allowed_radius INTEGER DEFAULT 100
                """)
                db.session.execute(add_sql)
                db.session.commit()
                
                return jsonify({
                    'status': 'success',
                    'message': '✅ Added "allowed_radius" column with default value 100!',
                    'action': 'added',
                    'next_step': 'Refresh your app - it should work now!'
                })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Not a PostgreSQL database',
                'db_type': db_url
            })
            
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Migration failed: {str(e)}',
            'details': str(e)
        }), 500

@migration_bp.route('/add-purchase-requests')
def add_purchase_requests():
    """
    SAFE MIGRATION: Add email column to employees and create purchase_requests table
    ✅ Does NOT delete any existing data!
    Access this URL once: /migrate/add-purchase-requests
    """
    try:
        changes_made = []
        
        # Check if we're using PostgreSQL
        db_url = db.engine.url.drivername
        
        if 'postgresql' not in db_url:
            return jsonify({
                'status': 'error',
                'message': 'This migration only works with PostgreSQL',
                'db_type': db_url
            }), 400
        
        # 1. Add email column to employees table (if it doesn't exist)
        check_email_sql = text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='employees' AND column_name='email'
        """)
        has_email = db.session.execute(check_email_sql).fetchone()
        
        if not has_email:
            add_email_sql = text("""
                ALTER TABLE employees 
                ADD COLUMN email VARCHAR(120)
            """)
            db.session.execute(add_email_sql)
            db.session.commit()
            changes_made.append('✅ Added "email" column to employees table')
        else:
            changes_made.append('ℹ️ Email column already exists in employees table')
        
        # 2. Create purchase_requests table (if it doesn't exist)
        check_table_sql = text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_name='purchase_requests'
        """)
        has_table = db.session.execute(check_table_sql).fetchone()
        
        if not has_table:
            create_table_sql = text("""
                CREATE TABLE purchase_requests (
                    id SERIAL PRIMARY KEY,
                    tenant_id INTEGER NOT NULL REFERENCES tenants(id),
                    employee_id INTEGER NOT NULL REFERENCES employees(id),
                    item_name VARCHAR(200) NOT NULL,
                    quantity FLOAT NOT NULL,
                    estimated_price FLOAT NOT NULL,
                    vendor_name VARCHAR(200),
                    request_type VARCHAR(20) NOT NULL DEFAULT 'expense',
                    category_id INTEGER,
                    reason TEXT,
                    document_url TEXT,
                    status VARCHAR(20) NOT NULL DEFAULT 'pending',
                    admin_notes TEXT,
                    rejection_reason TEXT,
                    processed_by VARCHAR(100),
                    processed_at TIMESTAMP,
                    created_expense_id INTEGER REFERENCES expenses(id),
                    created_item_id INTEGER REFERENCES items(id),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE INDEX idx_tenant_status ON purchase_requests(tenant_id, status);
                CREATE INDEX idx_employee_requests ON purchase_requests(employee_id, created_at);
            """)
            db.session.execute(create_table_sql)
            db.session.commit()
            changes_made.append('✅ Created "purchase_requests" table with indexes')
        else:
            changes_made.append('ℹ️ Purchase_requests table already exists')
        
        return jsonify({
            'status': 'success',
            'message': '✅ Migration completed successfully!',
            'changes': changes_made,
            'data_safety': '✅ All existing data is safe - no deletions performed',
            'next_step': 'Your app should work now! Try logging in again.'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Migration failed: {str(e)}',
            'details': str(e),
            'help': 'Contact support if this persists'
        }), 500


@migration_bp.route('/debug-emails')
def debug_emails():
    """Debug: Check if employee emails are saved and SMTP is configured"""
    import os
    from models import Employee, Tenant, PurchaseRequest
    
    try:
        # Check SMTP configuration
        smtp_email = os.getenv('SMTP_EMAIL')
        smtp_password = os.getenv('SMTP_PASSWORD')
        smtp_configured = bool(smtp_email and smtp_password)
        
        # Get all employees with emails
        employees_with_email = Employee.query.filter(Employee.email.isnot(None)).all()
        
        # Get all tenants with emails
        tenants = Tenant.query.all()
        
        # Get recent purchase requests
        recent_requests = PurchaseRequest.query.order_by(PurchaseRequest.created_at.desc()).limit(5).all()
        
        return jsonify({
            'status': 'success',
            'smtp_configured': smtp_configured,
            'smtp_email': smtp_email if smtp_email else 'NOT CONFIGURED',
            'smtp_password_set': '✅ Yes' if smtp_password else '❌ No',
            'total_employees_with_email': len(employees_with_email),
            'employees': [
                {
                    'id': emp.id,
                    'name': emp.name,
                    'email': emp.email,
                    'tenant_id': emp.tenant_id
                } for emp in employees_with_email
            ],
            'total_tenants': len(tenants),
            'tenants': [
                {
                    'id': t.id,
                    'company': t.company_name,
                    'email': t.admin_email,
                    'subdomain': t.subdomain
                } for t in tenants
            ],
            'recent_purchase_requests': [
                {
                    'id': pr.id,
                    'employee_name': pr.employee.name,
                    'employee_email': pr.employee.email or 'NO EMAIL',
                    'item': pr.item_name,
                    'status': pr.status,
                    'created_at': pr.created_at.strftime('%Y-%m-%d %H:%M:%S') if pr.created_at else None
                } for pr in recent_requests
            ]
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'details': str(e)
        }), 500


@migration_bp.route('/status')
def migration_status():
    """Check migration status"""
    try:
        check_sql = text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='sites' 
            ORDER BY ordinal_position
        """)
        result = db.session.execute(check_sql).fetchall()
        columns = [row[0] for row in result]
        
        has_radius = 'radius' in columns
        has_allowed_radius = 'allowed_radius' in columns
        
        return jsonify({
            'status': 'success',
            'sites_table_columns': columns,
            'has_old_radius': has_radius,
            'has_new_allowed_radius': has_allowed_radius,
            'migration_needed': has_radius and not has_allowed_radius,
            'migration_url': '/migrate/rename-radius-to-allowed-radius'
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@migration_bp.route('/add-invoices')
def add_invoices():
    """
    Create invoices and invoice_items tables
    Safe migration - doesn't affect existing data
    Access this URL once: /migrate/add-invoices
    """
    try:
        # Check if tables already exist
        check_sql = text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema='public' 
            AND table_name IN ('invoices', 'invoice_items')
        """)
        result = db.session.execute(check_sql).fetchall()
        existing_tables = [row[0] for row in result]
        
        if 'invoices' in existing_tables and 'invoice_items' in existing_tables:
            return jsonify({
                'status': 'success',
                'message': '✅ Invoice tables already exist!',
                'action': 'No migration needed',
                'existing_tables': existing_tables
            })
        
        # Create invoices table
        create_invoices_sql = text("""
            CREATE TABLE IF NOT EXISTS invoices (
                id SERIAL PRIMARY KEY,
                tenant_id INTEGER NOT NULL REFERENCES tenants(id),
                invoice_number VARCHAR(50) NOT NULL,
                invoice_date DATE NOT NULL DEFAULT CURRENT_DATE,
                due_date DATE,
                customer_name VARCHAR(200) NOT NULL,
                customer_phone VARCHAR(20),
                customer_email VARCHAR(120),
                customer_address TEXT,
                customer_gstin VARCHAR(15),
                customer_state VARCHAR(50),
                subtotal FLOAT NOT NULL DEFAULT 0,
                cgst_amount FLOAT DEFAULT 0,
                sgst_amount FLOAT DEFAULT 0,
                igst_amount FLOAT DEFAULT 0,
                discount_amount FLOAT DEFAULT 0,
                round_off FLOAT DEFAULT 0,
                total_amount FLOAT NOT NULL,
                payment_status VARCHAR(20) DEFAULT 'unpaid',
                paid_amount FLOAT DEFAULT 0,
                payment_method VARCHAR(50),
                notes TEXT,
                internal_notes TEXT,
                status VARCHAR(20) DEFAULT 'draft',
                cancelled_at TIMESTAMP,
                cancelled_reason TEXT,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            );
            
            CREATE INDEX IF NOT EXISTS idx_invoice_tenant ON invoices(tenant_id, invoice_date);
            CREATE INDEX IF NOT EXISTS idx_invoice_number ON invoices(tenant_id, invoice_number);
        """)
        
        db.session.execute(create_invoices_sql)
        
        # Create invoice_items table
        create_invoice_items_sql = text("""
            CREATE TABLE IF NOT EXISTS invoice_items (
                id SERIAL PRIMARY KEY,
                invoice_id INTEGER NOT NULL REFERENCES invoices(id) ON DELETE CASCADE,
                item_id INTEGER REFERENCES items(id),
                item_name VARCHAR(200) NOT NULL,
                description TEXT,
                hsn_code VARCHAR(20),
                quantity FLOAT NOT NULL,
                unit VARCHAR(20) DEFAULT 'Nos',
                rate FLOAT NOT NULL,
                gst_rate FLOAT DEFAULT 18,
                taxable_value FLOAT NOT NULL,
                cgst_amount FLOAT DEFAULT 0,
                sgst_amount FLOAT DEFAULT 0,
                igst_amount FLOAT DEFAULT 0,
                total_amount FLOAT NOT NULL
            );
            
            CREATE INDEX IF NOT EXISTS idx_invoice_item_invoice ON invoice_items(invoice_id);
        """)
        
        db.session.execute(create_invoice_items_sql)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': '✅ Invoice tables created successfully!',
            'created_tables': ['invoices', 'invoice_items'],
            'next_step': 'Configure invoice settings at /admin/invoices/settings'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Migration failed: {str(e)}',
            'details': str(e)
        }), 500


@migration_bp.route('/add-customers')
def add_customers_table():
    """
    Create customers table and add customer_id to invoices
    Safe migration - preserves existing data
    Access this URL once: /migrate/add-customers
    """
    try:
        # Create customers table
        create_customers_sql = text("""
            CREATE TABLE IF NOT EXISTS customers (
                id SERIAL PRIMARY KEY,
                tenant_id INTEGER NOT NULL REFERENCES tenants(id),
                customer_code VARCHAR(50) NOT NULL,
                name VARCHAR(200) NOT NULL,
                phone VARCHAR(20),
                email VARCHAR(120),
                address TEXT,
                gstin VARCHAR(15),
                state VARCHAR(50),
                credit_limit FLOAT DEFAULT 0,
                payment_terms_days INTEGER DEFAULT 30,
                opening_balance FLOAT DEFAULT 0,
                notes TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (tenant_id, customer_code)
            )
        """)
        
        db.session.execute(create_customers_sql)
        
        # Add customer_id to invoices table
        add_customer_id_sql = text("""
            ALTER TABLE invoices 
            ADD COLUMN IF NOT EXISTS customer_id INTEGER REFERENCES customers(id)
        """)
        
        db.session.execute(add_customer_id_sql)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': '✅ Customers table created and invoices updated!',
            'created': ['customers table', 'invoices.customer_id column'],
            'next_step': 'Go to /admin/customers to add your first customer!'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Migration failed: {str(e)}',
            'details': str(e)
        }), 500
