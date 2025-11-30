"""
One-time migration routes for database updates
Access these URLs once after deployment to migrate the database
"""
from flask import Blueprint, jsonify
from models import db
from sqlalchemy import text
from datetime import datetime
from utils.tenant_middleware import get_current_tenant_id
import os

migration_bp = Blueprint('migration', __name__, url_prefix='/migrate')

@migration_bp.route('/add-email-verification')
def add_email_verification():
    """
    Add email verification fields to tenants table
    Safe migration - preserves existing data, marks old accounts as verified
    Access this URL once: /migrate/add-email-verification
    """
    try:
        # Check if we're using PostgreSQL
        db_url = db.engine.url.drivername
        
        if 'postgresql' in db_url:
            # PostgreSQL syntax
            add_verification_fields = text("""
                -- Add email verification fields if they don't exist
                DO $$ 
                BEGIN
                    -- Add email_verified column (default TRUE for existing accounts)
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='tenants' AND column_name='email_verified'
                    ) THEN
                        ALTER TABLE tenants ADD COLUMN email_verified BOOLEAN DEFAULT TRUE;
                    END IF;
                    
                    -- Add verification_token column
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='tenants' AND column_name='verification_token'
                    ) THEN
                        ALTER TABLE tenants ADD COLUMN verification_token VARCHAR(100);
                    END IF;
                    
                    -- Add token_expiry column
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='tenants' AND column_name='token_expiry'
                    ) THEN
                        ALTER TABLE tenants ADD COLUMN token_expiry TIMESTAMP;
                    END IF;
                END $$;
            """)
        else:
            # SQLite syntax
            add_verification_fields = text("""
                -- Add email_verified column (default 1/TRUE for existing accounts)
                ALTER TABLE tenants ADD COLUMN email_verified INTEGER DEFAULT 1;
                
                -- Add verification_token column
                ALTER TABLE tenants ADD COLUMN verification_token TEXT;
                
                -- Add token_expiry column
                ALTER TABLE tenants ADD COLUMN token_expiry TEXT;
            """)
        
        db.session.execute(add_verification_fields)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': '✅ Email verification fields added successfully!',
            'details': 'Existing accounts are automatically marked as verified.'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Migration failed: {str(e)}',
            'help': 'If columns already exist, this is safe to ignore.'
        })

@migration_bp.route('/add-category-group-link')
def add_category_group_link():
    """
    Add group_id column to item_categories table
    Safe migration - preserves existing data
    Access this URL once: /migrate/add-category-group-link
    """
    try:
        # Check if we're using PostgreSQL
        db_url = db.engine.url.drivername
        
        if 'postgresql' in db_url:
            # PostgreSQL syntax
            add_group_id = text("""
                -- Add group_id column to item_categories if it doesn't exist
                DO $$ 
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='item_categories' AND column_name='group_id'
                    ) THEN
                        ALTER TABLE item_categories 
                        ADD COLUMN group_id INTEGER REFERENCES item_groups(id);
                        
                        -- Add index for performance
                        CREATE INDEX IF NOT EXISTS idx_category_group 
                        ON item_categories(group_id);
                    END IF;
                END $$;
            """)
        else:
            # SQLite syntax
            add_group_id = text("""
                -- Add group_id column (SQLite doesn't support IF NOT EXISTS in ALTER)
                ALTER TABLE item_categories ADD COLUMN group_id INTEGER REFERENCES item_groups(id);
            """)
        
        db.session.execute(add_group_id)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': '✅ group_id column added to item_categories successfully!',
            'details': 'Categories can now be linked to groups for better organization.'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Migration failed: {str(e)}',
            'help': 'If column already exists, this is safe to ignore.'
        })

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


@migration_bp.route('/add-tasks')
def add_tasks():
    """
    Create task management tables
    Safe migration - preserves existing data
    Access this URL once: /migrate/add-tasks
    """
    try:
        # Create tasks table
        create_tasks_sql = text("""
            CREATE TABLE IF NOT EXISTS tasks (
                id SERIAL PRIMARY KEY,
                tenant_id INTEGER NOT NULL REFERENCES tenants(id),
                task_number VARCHAR(50) NOT NULL,
                title VARCHAR(200) NOT NULL,
                description TEXT,
                priority VARCHAR(20) DEFAULT 'medium',
                status VARCHAR(20) DEFAULT 'new',
                assigned_to INTEGER NOT NULL REFERENCES employees(id),
                site_id INTEGER REFERENCES sites(id),
                start_date DATE,
                deadline DATE,
                completed_at TIMESTAMP,
                created_by INTEGER REFERENCES employees(id),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (tenant_id, task_number)
            );
            
            CREATE INDEX IF NOT EXISTS idx_task_status ON tasks(tenant_id, status);
            CREATE INDEX IF NOT EXISTS idx_task_employee ON tasks(tenant_id, assigned_to);
        """)
        db.session.execute(create_tasks_sql)
        
        # Create task_updates table
        create_task_updates_sql = text("""
            CREATE TABLE IF NOT EXISTS task_updates (
                id SERIAL PRIMARY KEY,
                task_id INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
                status VARCHAR(20) NOT NULL,
                notes TEXT,
                progress_percentage INTEGER DEFAULT 0,
                worker_count INTEGER DEFAULT 1,
                hours_worked FLOAT DEFAULT 0,
                updated_by INTEGER NOT NULL REFERENCES employees(id),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE INDEX IF NOT EXISTS idx_task_update_task ON task_updates(task_id);
        """)
        db.session.execute(create_task_updates_sql)
        
        # Create task_materials table
        create_task_materials_sql = text("""
            CREATE TABLE IF NOT EXISTS task_materials (
                id SERIAL PRIMARY KEY,
                task_id INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
                material_name VARCHAR(200) NOT NULL,
                quantity FLOAT NOT NULL,
                unit VARCHAR(50) DEFAULT 'pcs',
                cost_per_unit FLOAT DEFAULT 0,
                total_cost FLOAT DEFAULT 0,
                added_by INTEGER NOT NULL REFERENCES employees(id),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE INDEX IF NOT EXISTS idx_task_material_task ON task_materials(task_id);
        """)
        db.session.execute(create_task_materials_sql)
        
        # Create task_media table
        create_task_media_sql = text("""
            CREATE TABLE IF NOT EXISTS task_media (
                id SERIAL PRIMARY KEY,
                task_id INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
                media_type VARCHAR(20) NOT NULL,
                file_path VARCHAR(500) NOT NULL,
                caption TEXT,
                uploaded_by INTEGER NOT NULL REFERENCES employees(id),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE INDEX IF NOT EXISTS idx_task_media_task ON task_media(task_id);
        """)
        db.session.execute(create_task_media_sql)
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': '✅ Task management tables created successfully!',
            'created_tables': ['tasks', 'task_updates', 'task_materials', 'task_media'],
            'next_step': 'Go to /admin/tasks to start managing tasks!'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Migration failed: {str(e)}',
            'details': str(e)
        }), 500


@migration_bp.route('/add-hsn-code-to-items')
def add_hsn_code_to_items():
    """
    Add hsn_code field to items table for GST compliance
    HSN = Harmonized System of Nomenclature (required for Indian GST)
    Access this URL once: /migrate/add-hsn-code-to-items
    """
    try:
        # Check if column already exists
        check_sql = text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='items' AND column_name='hsn_code'
        """)
        result = db.session.execute(check_sql).fetchone()
        
        if result:
            return jsonify({
                'status': 'success',
                'message': '✅ HSN Code column already exists in items table',
                'action': 'No changes needed'
            })
        
        # Add hsn_code column
        add_column_sql = text("""
            ALTER TABLE items 
            ADD COLUMN hsn_code VARCHAR(20)
        """)
        db.session.execute(add_column_sql)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': '✅ HSN Code column added to items table successfully!',
            'field_added': 'hsn_code VARCHAR(20)',
            'next_step': 'You can now create invoices with HSN codes'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Migration failed: {str(e)}',
            'details': str(e)
        }), 500


@migration_bp.route('/add-sales-order-module')
def add_sales_order_module():
    """
    Add Sales Order and Delivery Challan modules
    Creates new tables and updates existing tables with foreign key references
    Access this URL once: /migrate/add-sales-order-module
    """
    try:
        db_url = db.engine.url.drivername
        
        if 'postgresql' in db_url:
            # PostgreSQL syntax
            migration_sql = text("""
                -- Create sales_orders table
                CREATE TABLE IF NOT EXISTS sales_orders (
                    id SERIAL PRIMARY KEY,
                    tenant_id INTEGER NOT NULL REFERENCES tenants(id),
                    
                    -- Order Details
                    order_number VARCHAR(50) UNIQUE NOT NULL,
                    order_date DATE NOT NULL,
                    expected_delivery_date DATE,
                    
                    -- Customer
                    customer_id INTEGER REFERENCES customers(id),
                    customer_name VARCHAR(255) NOT NULL,
                    customer_phone VARCHAR(20),
                    customer_email VARCHAR(255),
                    customer_gstin VARCHAR(15),
                    
                    -- Addresses
                    billing_address TEXT,
                    shipping_address TEXT,
                    
                    -- Amounts
                    subtotal DECIMAL(15,2) DEFAULT 0,
                    discount_amount DECIMAL(15,2) DEFAULT 0,
                    tax_amount DECIMAL(15,2) DEFAULT 0,
                    total_amount DECIMAL(15,2) NOT NULL,
                    
                    -- Order Status
                    status VARCHAR(50) DEFAULT 'pending',
                    
                    -- Fulfillment Tracking
                    quantity_ordered INTEGER DEFAULT 0,
                    quantity_delivered INTEGER DEFAULT 0,
                    quantity_invoiced INTEGER DEFAULT 0,
                    
                    -- References
                    quotation_id INTEGER,  -- Will link to quotations table when implemented
                    
                    -- Notes
                    terms_and_conditions TEXT,
                    notes TEXT,
                    
                    -- Timestamps
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_by VARCHAR(255)
                );
                
                -- Create sales_order_items table
                CREATE TABLE IF NOT EXISTS sales_order_items (
                    id SERIAL PRIMARY KEY,
                    sales_order_id INTEGER NOT NULL REFERENCES sales_orders(id) ON DELETE CASCADE,
                    tenant_id INTEGER NOT NULL REFERENCES tenants(id),
                    
                    -- Item Details
                    item_id INTEGER REFERENCES items(id),
                    item_name VARCHAR(255) NOT NULL,
                    description TEXT,
                    hsn_code VARCHAR(20),
                    
                    -- Quantity & Pricing
                    quantity DECIMAL(15,3) NOT NULL,
                    unit VARCHAR(50) DEFAULT 'pcs',
                    rate DECIMAL(15,2) NOT NULL,
                    
                    -- Tax
                    gst_rate DECIMAL(5,2) DEFAULT 0,
                    price_inclusive BOOLEAN DEFAULT FALSE,
                    
                    -- Discount
                    discount_type VARCHAR(20),
                    discount_value DECIMAL(15,2) DEFAULT 0,
                    
                    -- Calculated Amounts
                    taxable_amount DECIMAL(15,2),
                    tax_amount DECIMAL(15,2),
                    total_amount DECIMAL(15,2),
                    
                    -- Fulfillment Tracking
                    quantity_delivered DECIMAL(15,3) DEFAULT 0,
                    quantity_invoiced DECIMAL(15,3) DEFAULT 0,
                    
                    -- Stock Reservation
                    stock_reserved BOOLEAN DEFAULT FALSE,
                    site_id INTEGER REFERENCES sites(id),
                    
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                -- Create delivery_challans table
                CREATE TABLE IF NOT EXISTS delivery_challans (
                    id SERIAL PRIMARY KEY,
                    tenant_id INTEGER NOT NULL REFERENCES tenants(id),
                    
                    -- Challan Details
                    challan_number VARCHAR(50) UNIQUE NOT NULL,
                    challan_date DATE NOT NULL,
                    
                    -- Customer
                    customer_id INTEGER REFERENCES customers(id),
                    customer_name VARCHAR(255) NOT NULL,
                    customer_phone VARCHAR(20),
                    customer_gstin VARCHAR(15),
                    
                    -- Addresses
                    billing_address TEXT,
                    shipping_address TEXT,
                    
                    -- Purpose
                    purpose VARCHAR(100) NOT NULL,
                    
                    -- Transport Details
                    transporter_name VARCHAR(255),
                    vehicle_number VARCHAR(50),
                    lr_number VARCHAR(100),
                    e_way_bill_number VARCHAR(50),
                    
                    -- Amounts
                    total_quantity DECIMAL(15,3),
                    total_value DECIMAL(15,2),
                    
                    -- Status
                    status VARCHAR(50) DEFAULT 'pending',
                    
                    -- References
                    sales_order_id INTEGER REFERENCES sales_orders(id),
                    
                    -- Expected Return
                    expected_return_date DATE,
                    actual_return_date DATE,
                    
                    -- Notes
                    notes TEXT,
                    terms_and_conditions TEXT,
                    
                    -- Timestamps
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_by VARCHAR(255)
                );
                
                -- Create delivery_challan_items table
                CREATE TABLE IF NOT EXISTS delivery_challan_items (
                    id SERIAL PRIMARY KEY,
                    delivery_challan_id INTEGER NOT NULL REFERENCES delivery_challans(id) ON DELETE CASCADE,
                    tenant_id INTEGER NOT NULL REFERENCES tenants(id),
                    
                    -- Item Details
                    item_id INTEGER REFERENCES items(id),
                    item_name VARCHAR(255) NOT NULL,
                    description TEXT,
                    hsn_code VARCHAR(20),
                    
                    -- Quantity
                    quantity DECIMAL(15,3) NOT NULL,
                    unit VARCHAR(50) DEFAULT 'pcs',
                    
                    -- Reference Value
                    rate DECIMAL(15,2),
                    amount DECIMAL(15,2),
                    
                    -- Serial Numbers
                    serial_numbers TEXT,
                    
                    -- Fulfillment Tracking
                    quantity_invoiced DECIMAL(15,3) DEFAULT 0,
                    quantity_returned DECIMAL(15,3) DEFAULT 0,
                    
                    -- Link to Sales Order Item
                    sales_order_item_id INTEGER REFERENCES sales_order_items(id),
                    
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                -- Add foreign keys to existing invoices table
                DO $$ 
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='invoices' AND column_name='sales_order_id'
                    ) THEN
                        ALTER TABLE invoices ADD COLUMN sales_order_id INTEGER REFERENCES sales_orders(id);
                    END IF;
                    
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='invoices' AND column_name='delivery_challan_id'
                    ) THEN
                        ALTER TABLE invoices ADD COLUMN delivery_challan_id INTEGER REFERENCES delivery_challans(id);
                    END IF;
                END $$;
                
                -- Add foreign keys to existing invoice_items table
                DO $$ 
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='invoice_items' AND column_name='sales_order_item_id'
                    ) THEN
                        ALTER TABLE invoice_items ADD COLUMN sales_order_item_id INTEGER REFERENCES sales_order_items(id);
                    END IF;
                    
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='invoice_items' AND column_name='delivery_challan_item_id'
                    ) THEN
                        ALTER TABLE invoice_items ADD COLUMN delivery_challan_item_id INTEGER REFERENCES delivery_challan_items(id);
                    END IF;
                END $$;
            """)
        else:
            # SQLite syntax (for local development)
            migration_sql = text("""
                -- Create sales_orders table
                CREATE TABLE IF NOT EXISTS sales_orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    order_number VARCHAR(50) UNIQUE NOT NULL,
                    order_date DATE NOT NULL,
                    expected_delivery_date DATE,
                    customer_id INTEGER,
                    customer_name VARCHAR(255) NOT NULL,
                    customer_phone VARCHAR(20),
                    customer_email VARCHAR(255),
                    customer_gstin VARCHAR(15),
                    billing_address TEXT,
                    shipping_address TEXT,
                    subtotal DECIMAL(15,2) DEFAULT 0,
                    discount_amount DECIMAL(15,2) DEFAULT 0,
                    tax_amount DECIMAL(15,2) DEFAULT 0,
                    total_amount DECIMAL(15,2) NOT NULL,
                    status VARCHAR(50) DEFAULT 'pending',
                    quantity_ordered INTEGER DEFAULT 0,
                    quantity_delivered INTEGER DEFAULT 0,
                    quantity_invoiced INTEGER DEFAULT 0,
                    quotation_id INTEGER,
                    terms_and_conditions TEXT,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_by VARCHAR(255),
                    FOREIGN KEY (tenant_id) REFERENCES tenants(id),
                    FOREIGN KEY (customer_id) REFERENCES customers(id),
                    -- FOREIGN KEY (quotation_id) REFERENCES quotations(id)  -- Disabled until quotations implemented
                );
                
                CREATE TABLE IF NOT EXISTS sales_order_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sales_order_id INTEGER NOT NULL,
                    tenant_id INTEGER NOT NULL,
                    item_id INTEGER,
                    item_name VARCHAR(255) NOT NULL,
                    description TEXT,
                    hsn_code VARCHAR(20),
                    quantity DECIMAL(15,3) NOT NULL,
                    unit VARCHAR(50) DEFAULT 'pcs',
                    rate DECIMAL(15,2) NOT NULL,
                    gst_rate DECIMAL(5,2) DEFAULT 0,
                    price_inclusive INTEGER DEFAULT 0,
                    discount_type VARCHAR(20),
                    discount_value DECIMAL(15,2) DEFAULT 0,
                    taxable_amount DECIMAL(15,2),
                    tax_amount DECIMAL(15,2),
                    total_amount DECIMAL(15,2),
                    quantity_delivered DECIMAL(15,3) DEFAULT 0,
                    quantity_invoiced DECIMAL(15,3) DEFAULT 0,
                    stock_reserved INTEGER DEFAULT 0,
                    site_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (sales_order_id) REFERENCES sales_orders(id) ON DELETE CASCADE,
                    FOREIGN KEY (tenant_id) REFERENCES tenants(id),
                    FOREIGN KEY (item_id) REFERENCES items(id),
                    FOREIGN KEY (site_id) REFERENCES sites(id)
                );
                
                CREATE TABLE IF NOT EXISTS delivery_challans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    challan_number VARCHAR(50) UNIQUE NOT NULL,
                    challan_date DATE NOT NULL,
                    customer_id INTEGER,
                    customer_name VARCHAR(255) NOT NULL,
                    customer_phone VARCHAR(20),
                    customer_gstin VARCHAR(15),
                    billing_address TEXT,
                    shipping_address TEXT,
                    purpose VARCHAR(100) NOT NULL,
                    transporter_name VARCHAR(255),
                    vehicle_number VARCHAR(50),
                    lr_number VARCHAR(100),
                    e_way_bill_number VARCHAR(50),
                    total_quantity DECIMAL(15,3),
                    total_value DECIMAL(15,2),
                    status VARCHAR(50) DEFAULT 'pending',
                    sales_order_id INTEGER,
                    expected_return_date DATE,
                    actual_return_date DATE,
                    notes TEXT,
                    terms_and_conditions TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_by VARCHAR(255),
                    FOREIGN KEY (tenant_id) REFERENCES tenants(id),
                    FOREIGN KEY (customer_id) REFERENCES customers(id),
                    FOREIGN KEY (sales_order_id) REFERENCES sales_orders(id)
                );
                
                CREATE TABLE IF NOT EXISTS delivery_challan_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    delivery_challan_id INTEGER NOT NULL,
                    tenant_id INTEGER NOT NULL,
                    item_id INTEGER,
                    item_name VARCHAR(255) NOT NULL,
                    description TEXT,
                    hsn_code VARCHAR(20),
                    quantity DECIMAL(15,3) NOT NULL,
                    unit VARCHAR(50) DEFAULT 'pcs',
                    rate DECIMAL(15,2),
                    amount DECIMAL(15,2),
                    serial_numbers TEXT,
                    quantity_invoiced DECIMAL(15,3) DEFAULT 0,
                    quantity_returned DECIMAL(15,3) DEFAULT 0,
                    sales_order_item_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (delivery_challan_id) REFERENCES delivery_challans(id) ON DELETE CASCADE,
                    FOREIGN KEY (tenant_id) REFERENCES tenants(id),
                    FOREIGN KEY (item_id) REFERENCES items(id),
                    FOREIGN KEY (sales_order_item_id) REFERENCES sales_order_items(id)
                );
            """)
        
        db.session.execute(migration_sql)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': '✅ Sales Order and Delivery Challan modules added successfully!',
            'tables_created': [
                'sales_orders',
                'sales_order_items',
                'delivery_challans',
                'delivery_challan_items'
            ],
            'tables_updated': [
                'invoices (added sales_order_id, delivery_challan_id)',
                'invoice_items (added sales_order_item_id, delivery_challan_item_id)'
            ],
            'next_steps': [
                'You can now create sales orders from quotations',
                'Create delivery challans from sales orders',
                'Convert orders/challans to invoices',
                'Track fulfillment status for all orders'
            ]
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Migration failed: {str(e)}',
            'details': str(e),
            'help': 'If tables already exist, this is safe to ignore.'
        }), 500

@migration_bp.route('/fix-delivery-challan-columns')
def fix_delivery_challan_columns():
    """
    Fix delivery_challans table by adding missing columns
    This updates the table to match the new DeliveryChallan model
    Access this URL once: /migrate/fix-delivery-challan-columns
    """
    try:
        db_url = db.engine.url.drivername
        
        if 'postgresql' in db_url:
            # PostgreSQL - Add missing columns
            fix_queries = [
                # Add customer_email
                """
                DO $$ 
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='delivery_challans' AND column_name='customer_email'
                    ) THEN
                        ALTER TABLE delivery_challans ADD COLUMN customer_email VARCHAR(120);
                    END IF;
                END $$;
                """,
                # Add customer_state
                """
                DO $$ 
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='delivery_challans' AND column_name='customer_state'
                    ) THEN
                        ALTER TABLE delivery_challans ADD COLUMN customer_state VARCHAR(50) DEFAULT 'Maharashtra';
                    END IF;
                END $$;
                """,
                # Rename billing_address to customer_billing_address
                """
                DO $$ 
                BEGIN
                    IF EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='delivery_challans' AND column_name='billing_address'
                    ) AND NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='delivery_challans' AND column_name='customer_billing_address'
                    ) THEN
                        ALTER TABLE delivery_challans RENAME COLUMN billing_address TO customer_billing_address;
                    END IF;
                END $$;
                """,
                # Rename shipping_address to customer_shipping_address
                """
                DO $$ 
                BEGIN
                    IF EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='delivery_challans' AND column_name='shipping_address'
                    ) AND NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='delivery_challans' AND column_name='customer_shipping_address'
                    ) THEN
                        ALTER TABLE delivery_challans RENAME COLUMN shipping_address TO customer_shipping_address;
                    END IF;
                END $$;
                """,
                # Add subtotal
                """
                DO $$ 
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='delivery_challans' AND column_name='subtotal'
                    ) THEN
                        ALTER TABLE delivery_challans ADD COLUMN subtotal NUMERIC(15,2) DEFAULT 0;
                    END IF;
                END $$;
                """,
                # Add cgst_amount
                """
                DO $$ 
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='delivery_challans' AND column_name='cgst_amount'
                    ) THEN
                        ALTER TABLE delivery_challans ADD COLUMN cgst_amount NUMERIC(15,2) DEFAULT 0;
                    END IF;
                END $$;
                """,
                # Add sgst_amount
                """
                DO $$ 
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='delivery_challans' AND column_name='sgst_amount'
                    ) THEN
                        ALTER TABLE delivery_challans ADD COLUMN sgst_amount NUMERIC(15,2) DEFAULT 0;
                    END IF;
                END $$;
                """,
                # Add igst_amount
                """
                DO $$ 
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='delivery_challans' AND column_name='igst_amount'
                    ) THEN
                        ALTER TABLE delivery_challans ADD COLUMN igst_amount NUMERIC(15,2) DEFAULT 0;
                    END IF;
                END $$;
                """,
                # Rename total_value to total_amount
                """
                DO $$ 
                BEGIN
                    IF EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='delivery_challans' AND column_name='total_value'
                    ) AND NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='delivery_challans' AND column_name='total_amount'
                    ) THEN
                        ALTER TABLE delivery_challans RENAME COLUMN total_value TO total_amount;
                    END IF;
                END $$;
                """,
                # Add delivery_note
                """
                DO $$ 
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='delivery_challans' AND column_name='delivery_note'
                    ) THEN
                        ALTER TABLE delivery_challans ADD COLUMN delivery_note TEXT;
                    END IF;
                END $$;
                """,
                # Add dispatched_at
                """
                DO $$ 
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='delivery_challans' AND column_name='dispatched_at'
                    ) THEN
                        ALTER TABLE delivery_challans ADD COLUMN dispatched_at TIMESTAMP;
                    END IF;
                END $$;
                """,
                # Add delivered_at
                """
                DO $$ 
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='delivery_challans' AND column_name='delivered_at'
                    ) THEN
                        ALTER TABLE delivery_challans ADD COLUMN delivered_at TIMESTAMP;
                    END IF;
                END $$;
                """,
                # Add invoiced_at
                """
                DO $$ 
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='delivery_challans' AND column_name='invoiced_at'
                    ) THEN
                        ALTER TABLE delivery_challans ADD COLUMN invoiced_at TIMESTAMP;
                    END IF;
                END $$;
                """,
                # Rename notes to terms (if exists)
                """
                DO $$ 
                BEGIN
                    IF EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='delivery_challans' AND column_name='terms_and_conditions'
                    ) AND NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='delivery_challans' AND column_name='terms'
                    ) THEN
                        ALTER TABLE delivery_challans RENAME COLUMN terms_and_conditions TO terms;
                    END IF;
                END $$;
                """,
                # Make purpose column nullable (NOT NULL in old schema, not used in new model)
                """
                DO $$ 
                BEGIN
                    IF EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='delivery_challans' AND column_name='purpose'
                    ) THEN
                        ALTER TABLE delivery_challans ALTER COLUMN purpose DROP NOT NULL;
                    END IF;
                END $$;
                """
            ]
            
            for query in fix_queries:
                db.session.execute(text(query))
        
        else:
            # SQLite - Add missing columns (no conditional ADD COLUMN in SQLite)
            fix_queries = []
            
            # Check and add columns one by one
            try:
                db.session.execute(text("ALTER TABLE delivery_challans ADD COLUMN customer_email VARCHAR(120)"))
            except:
                pass
            
            try:
                db.session.execute(text("ALTER TABLE delivery_challans ADD COLUMN customer_state VARCHAR(50) DEFAULT 'Maharashtra'"))
            except:
                pass
            
            try:
                db.session.execute(text("ALTER TABLE delivery_challans ADD COLUMN customer_billing_address TEXT"))
            except:
                pass
            
            try:
                db.session.execute(text("ALTER TABLE delivery_challans ADD COLUMN customer_shipping_address TEXT"))
            except:
                pass
            
            try:
                db.session.execute(text("ALTER TABLE delivery_challans ADD COLUMN subtotal NUMERIC(15,2) DEFAULT 0"))
            except:
                pass
            
            try:
                db.session.execute(text("ALTER TABLE delivery_challans ADD COLUMN cgst_amount NUMERIC(15,2) DEFAULT 0"))
            except:
                pass
            
            try:
                db.session.execute(text("ALTER TABLE delivery_challans ADD COLUMN sgst_amount NUMERIC(15,2) DEFAULT 0"))
            except:
                pass
            
            try:
                db.session.execute(text("ALTER TABLE delivery_challans ADD COLUMN igst_amount NUMERIC(15,2) DEFAULT 0"))
            except:
                pass
            
            try:
                db.session.execute(text("ALTER TABLE delivery_challans ADD COLUMN total_amount NUMERIC(15,2) DEFAULT 0"))
            except:
                pass
            
            try:
                db.session.execute(text("ALTER TABLE delivery_challans ADD COLUMN delivery_note TEXT"))
            except:
                pass
            
            try:
                db.session.execute(text("ALTER TABLE delivery_challans ADD COLUMN dispatched_at TIMESTAMP"))
            except:
                pass
            
            try:
                db.session.execute(text("ALTER TABLE delivery_challans ADD COLUMN delivered_at TIMESTAMP"))
            except:
                pass
            
            try:
                db.session.execute(text("ALTER TABLE delivery_challans ADD COLUMN invoiced_at TIMESTAMP"))
            except:
                pass
        
        # Make purpose column nullable (it's NOT NULL in old schema but not used in new model)
        if 'postgresql' in db_url:
            try:
                db.session.execute(text("ALTER TABLE delivery_challans ALTER COLUMN purpose DROP NOT NULL"))
            except:
                pass
        
        db.session.commit()
        
        # Also fix delivery_challan_items table
        if 'postgresql' in db_url:
            items_fix_queries = [
                # Add sales_order_id
                """
                DO $$ 
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='delivery_challan_items' AND column_name='sales_order_id'
                    ) THEN
                        ALTER TABLE delivery_challan_items ADD COLUMN sales_order_id INTEGER;
                    END IF;
                END $$;
                """,
                # Add sales_order_item_id
                """
                DO $$ 
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='delivery_challan_items' AND column_name='sales_order_item_id'
                    ) THEN
                        ALTER TABLE delivery_challan_items ADD COLUMN sales_order_item_id INTEGER;
                    END IF;
                END $$;
                """,
                # Add description
                """
                DO $$ 
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='delivery_challan_items' AND column_name='description'
                    ) THEN
                        ALTER TABLE delivery_challan_items ADD COLUMN description TEXT;
                    END IF;
                END $$;
                """,
                # Add taxable_value
                """
                DO $$ 
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='delivery_challan_items' AND column_name='taxable_value'
                    ) THEN
                        ALTER TABLE delivery_challan_items ADD COLUMN taxable_value NUMERIC(15,2) DEFAULT 0;
                    END IF;
                END $$;
                """,
                # Add gst_rate
                """
                DO $$ 
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='delivery_challan_items' AND column_name='gst_rate'
                    ) THEN
                        ALTER TABLE delivery_challan_items ADD COLUMN gst_rate NUMERIC(5,2) DEFAULT 0;
                    END IF;
                END $$;
                """,
                # Add cgst_amount
                """
                DO $$ 
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='delivery_challan_items' AND column_name='cgst_amount'
                    ) THEN
                        ALTER TABLE delivery_challan_items ADD COLUMN cgst_amount NUMERIC(15,2) DEFAULT 0;
                    END IF;
                END $$;
                """,
                # Add sgst_amount
                """
                DO $$ 
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='delivery_challan_items' AND column_name='sgst_amount'
                    ) THEN
                        ALTER TABLE delivery_challan_items ADD COLUMN sgst_amount NUMERIC(15,2) DEFAULT 0;
                    END IF;
                END $$;
                """,
                # Add igst_amount
                """
                DO $$ 
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='delivery_challan_items' AND column_name='igst_amount'
                    ) THEN
                        ALTER TABLE delivery_challan_items ADD COLUMN igst_amount NUMERIC(15,2) DEFAULT 0;
                    END IF;
                END $$;
                """,
                # Add total_amount
                """
                DO $$ 
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='delivery_challan_items' AND column_name='total_amount'
                    ) THEN
                        ALTER TABLE delivery_challan_items ADD COLUMN total_amount NUMERIC(15,2) DEFAULT 0;
                    END IF;
                END $$;
                """,
                # Add quantity_invoiced
                """
                DO $$ 
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='delivery_challan_items' AND column_name='quantity_invoiced'
                    ) THEN
                        ALTER TABLE delivery_challan_items ADD COLUMN quantity_invoiced NUMERIC(15,3) DEFAULT 0;
                    END IF;
                END $$;
                """,
                # Add batch_number
                """
                DO $$ 
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='delivery_challan_items' AND column_name='batch_number'
                    ) THEN
                        ALTER TABLE delivery_challan_items ADD COLUMN batch_number VARCHAR(50);
                    END IF;
                END $$;
                """,
                # Add serial_number
                """
                DO $$ 
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='delivery_challan_items' AND column_name='serial_number'
                    ) THEN
                        ALTER TABLE delivery_challan_items ADD COLUMN serial_number VARCHAR(100);
                    END IF;
                END $$;
                """,
                # Add notes
                """
                DO $$ 
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='delivery_challan_items' AND column_name='notes'
                    ) THEN
                        ALTER TABLE delivery_challan_items ADD COLUMN notes TEXT;
                    END IF;
                END $$;
                """,
                # Add created_at (TimestampMixin)
                """
                DO $$ 
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='delivery_challan_items' AND column_name='created_at'
                    ) THEN
                        ALTER TABLE delivery_challan_items ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
                    END IF;
                END $$;
                """,
                # Add updated_at (TimestampMixin)
                """
                DO $$ 
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='delivery_challan_items' AND column_name='updated_at'
                    ) THEN
                        ALTER TABLE delivery_challan_items ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
                    END IF;
                END $$;
                """
            ]
            
            for query in items_fix_queries:
                db.session.execute(text(query))
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': '✅ Delivery Challan tables updated successfully!',
            'tables_fixed': ['delivery_challans', 'delivery_challan_items'],
            'dc_columns_added': [
                'customer_email',
                'customer_state',
                'customer_billing_address',
                'customer_shipping_address',
                'subtotal',
                'cgst_amount',
                'sgst_amount',
                'igst_amount',
                'total_amount',
                'delivery_note',
                'dispatched_at',
                'delivered_at',
                'invoiced_at',
                'terms',
                'purpose (made nullable)'
            ],
            'dc_items_columns_added': [
                'sales_order_id',
                'sales_order_item_id',
                'description',
                'taxable_value',
                'gst_rate',
                'cgst_amount',
                'sgst_amount',
                'igst_amount',
                'total_amount',
                'quantity_invoiced',
                'batch_number',
                'serial_number',
                'notes',
                'created_at',
                'updated_at'
            ]
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Migration failed: {str(e)}',
            'details': str(e),
            'help': 'Some columns may already exist, which is safe to ignore.'
        }), 500

@migration_bp.route('/add-purchase-bills-module')
def add_purchase_bills_module():
    """
    Add Purchase Bills module - complete tables for purchase bill management
    Access: /migrate/add-purchase-bills-module
    """
    try:
        db_url = db.engine.url.drivername
        
        if 'postgresql' in db_url:
            # PostgreSQL
            queries = [
                # Create purchase_bills table
                """
                CREATE TABLE IF NOT EXISTS purchase_bills (
                    id SERIAL PRIMARY KEY,
                    tenant_id INTEGER NOT NULL REFERENCES tenants(id),
                    bill_number VARCHAR(50) UNIQUE NOT NULL,
                    bill_date DATE NOT NULL,
                    due_date DATE,
                    vendor_id INTEGER REFERENCES vendors(id),
                    vendor_name VARCHAR(255) NOT NULL,
                    vendor_phone VARCHAR(20),
                    vendor_email VARCHAR(120),
                    vendor_gstin VARCHAR(15),
                    vendor_address TEXT,
                    vendor_state VARCHAR(50) DEFAULT 'Maharashtra',
                    purchase_request_id INTEGER REFERENCES purchase_requests(id),
                    subtotal NUMERIC(15, 2) DEFAULT 0,
                    discount_amount NUMERIC(15, 2) DEFAULT 0,
                    cgst_amount NUMERIC(15, 2) DEFAULT 0,
                    sgst_amount NUMERIC(15, 2) DEFAULT 0,
                    igst_amount NUMERIC(15, 2) DEFAULT 0,
                    other_charges NUMERIC(15, 2) DEFAULT 0,
                    round_off NUMERIC(10, 2) DEFAULT 0,
                    total_amount NUMERIC(15, 2) NOT NULL,
                    payment_status VARCHAR(20) DEFAULT 'unpaid',
                    paid_amount NUMERIC(15, 2) DEFAULT 0,
                    balance_due NUMERIC(15, 2) DEFAULT 0,
                    payment_terms VARCHAR(100),
                    reference_number VARCHAR(100),
                    notes TEXT,
                    terms_conditions TEXT,
                    document_url VARCHAR(500),
                    status VARCHAR(20) DEFAULT 'draft',
                    approved_at TIMESTAMP,
                    approved_by INTEGER REFERENCES employees(id),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """,
                # Create purchase_bill_items table
                """
                CREATE TABLE IF NOT EXISTS purchase_bill_items (
                    id SERIAL PRIMARY KEY,
                    tenant_id INTEGER NOT NULL REFERENCES tenants(id),
                    purchase_bill_id INTEGER NOT NULL REFERENCES purchase_bills(id),
                    item_id INTEGER REFERENCES items(id),
                    item_name VARCHAR(255) NOT NULL,
                    description TEXT,
                    hsn_code VARCHAR(20),
                    quantity NUMERIC(15, 3) NOT NULL,
                    unit VARCHAR(20) DEFAULT 'pcs',
                    rate NUMERIC(15, 2) NOT NULL,
                    discount_percentage NUMERIC(5, 2) DEFAULT 0,
                    discount_amount NUMERIC(15, 2) DEFAULT 0,
                    taxable_value NUMERIC(15, 2) DEFAULT 0,
                    gst_rate NUMERIC(5, 2) DEFAULT 0,
                    cgst_amount NUMERIC(15, 2) DEFAULT 0,
                    sgst_amount NUMERIC(15, 2) DEFAULT 0,
                    igst_amount NUMERIC(15, 2) DEFAULT 0,
                    total_amount NUMERIC(15, 2) DEFAULT 0,
                    site_id INTEGER REFERENCES sites(id),
                    received_quantity NUMERIC(15, 3) DEFAULT 0,
                    batch_number VARCHAR(50),
                    expiry_date DATE,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """,
                # Create indices for better performance
                """
                CREATE INDEX IF NOT EXISTS idx_purchase_bills_tenant 
                ON purchase_bills(tenant_id);
                """,
                """
                CREATE INDEX IF NOT EXISTS idx_purchase_bills_vendor 
                ON purchase_bills(vendor_id);
                """,
                """
                CREATE INDEX IF NOT EXISTS idx_purchase_bills_status 
                ON purchase_bills(status);
                """,
                """
                CREATE INDEX IF NOT EXISTS idx_purchase_bills_payment_status 
                ON purchase_bills(payment_status);
                """,
                """
                CREATE INDEX IF NOT EXISTS idx_purchase_bills_bill_date 
                ON purchase_bills(bill_date);
                """,
                """
                CREATE INDEX IF NOT EXISTS idx_purchase_bill_items_bill 
                ON purchase_bill_items(purchase_bill_id);
                """,
                """
                CREATE INDEX IF NOT EXISTS idx_purchase_bill_items_item 
                ON purchase_bill_items(item_id);
                """
            ]
            
            for query in queries:
                db.session.execute(text(query))
                
        else:
            # SQLite
            queries = [
                # Create purchase_bills table
                """
                CREATE TABLE IF NOT EXISTS purchase_bills (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL REFERENCES tenants(id),
                    bill_number VARCHAR(50) UNIQUE NOT NULL,
                    bill_date DATE NOT NULL,
                    due_date DATE,
                    vendor_id INTEGER REFERENCES vendors(id),
                    vendor_name VARCHAR(255) NOT NULL,
                    vendor_phone VARCHAR(20),
                    vendor_email VARCHAR(120),
                    vendor_gstin VARCHAR(15),
                    vendor_address TEXT,
                    vendor_state VARCHAR(50) DEFAULT 'Maharashtra',
                    purchase_request_id INTEGER REFERENCES purchase_requests(id),
                    subtotal DECIMAL(15, 2) DEFAULT 0,
                    discount_amount DECIMAL(15, 2) DEFAULT 0,
                    cgst_amount DECIMAL(15, 2) DEFAULT 0,
                    sgst_amount DECIMAL(15, 2) DEFAULT 0,
                    igst_amount DECIMAL(15, 2) DEFAULT 0,
                    other_charges DECIMAL(15, 2) DEFAULT 0,
                    round_off DECIMAL(10, 2) DEFAULT 0,
                    total_amount DECIMAL(15, 2) NOT NULL,
                    payment_status VARCHAR(20) DEFAULT 'unpaid',
                    paid_amount DECIMAL(15, 2) DEFAULT 0,
                    balance_due DECIMAL(15, 2) DEFAULT 0,
                    payment_terms VARCHAR(100),
                    reference_number VARCHAR(100),
                    notes TEXT,
                    terms_conditions TEXT,
                    document_url VARCHAR(500),
                    status VARCHAR(20) DEFAULT 'draft',
                    approved_at TIMESTAMP,
                    approved_by INTEGER REFERENCES employees(id),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """,
                # Create purchase_bill_items table
                """
                CREATE TABLE IF NOT EXISTS purchase_bill_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL REFERENCES tenants(id),
                    purchase_bill_id INTEGER NOT NULL REFERENCES purchase_bills(id),
                    item_id INTEGER REFERENCES items(id),
                    item_name VARCHAR(255) NOT NULL,
                    description TEXT,
                    hsn_code VARCHAR(20),
                    quantity DECIMAL(15, 3) NOT NULL,
                    unit VARCHAR(20) DEFAULT 'pcs',
                    rate DECIMAL(15, 2) NOT NULL,
                    discount_percentage DECIMAL(5, 2) DEFAULT 0,
                    discount_amount DECIMAL(15, 2) DEFAULT 0,
                    taxable_value DECIMAL(15, 2) DEFAULT 0,
                    gst_rate DECIMAL(5, 2) DEFAULT 0,
                    cgst_amount DECIMAL(15, 2) DEFAULT 0,
                    sgst_amount DECIMAL(15, 2) DEFAULT 0,
                    igst_amount DECIMAL(15, 2) DEFAULT 0,
                    total_amount DECIMAL(15, 2) DEFAULT 0,
                    site_id INTEGER REFERENCES sites(id),
                    received_quantity DECIMAL(15, 3) DEFAULT 0,
                    batch_number VARCHAR(50),
                    expiry_date DATE,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """,
                # Create indices
                """
                CREATE INDEX IF NOT EXISTS idx_purchase_bills_tenant 
                ON purchase_bills(tenant_id);
                """,
                """
                CREATE INDEX IF NOT EXISTS idx_purchase_bills_vendor 
                ON purchase_bills(vendor_id);
                """,
                """
                CREATE INDEX IF NOT EXISTS idx_purchase_bills_status 
                ON purchase_bills(status);
                """,
                """
                CREATE INDEX IF NOT EXISTS idx_purchase_bills_payment_status 
                ON purchase_bills(payment_status);
                """,
                """
                CREATE INDEX IF NOT EXISTS idx_purchase_bills_bill_date 
                ON purchase_bills(bill_date);
                """,
                """
                CREATE INDEX IF NOT EXISTS idx_purchase_bill_items_bill 
                ON purchase_bill_items(purchase_bill_id);
                """,
                """
                CREATE INDEX IF NOT EXISTS idx_purchase_bill_items_item 
                ON purchase_bill_items(item_id);
                """
            ]
            
            for query in queries:
                db.session.execute(text(query))
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': '✅ Purchase Bills module created successfully!',
            'tables_created': ['purchase_bills', 'purchase_bill_items'],
            'features': [
                'Purchase bill management with GST',
                'Vendor tracking and integration',
                'Payment status tracking',
                'Inventory receipt tracking',
                'Link to purchase requests (optional)',
                'Document attachment support'
            ],
            'next_steps': [
                'Access /admin/purchase-bills to start creating purchase bills',
                'Bills can be created manually or from approved purchase requests',
                'Track Input Tax Credit (ITC) for GST-2 reporting'
            ]
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Migration failed: {str(e)}',
            'details': str(e)
        }), 500


@migration_bp.route('/fix-purchase-bill-approved-by')
def fix_purchase_bill_approved_by():
    """
    Fix approved_by foreign key constraint
    Remove FK to employees table since approver can be tenant admin
    Access: /migrate/fix-purchase-bill-approved-by
    """
    try:
        db_type = os.environ.get('DATABASE_URL', '').split(':')[0] if os.environ.get('DATABASE_URL') else 'sqlite'
        
        if db_type == 'postgresql':
            # Drop the foreign key constraint
            db.session.execute(text("""
                -- Drop the foreign key constraint if it exists
                DO $$ 
                BEGIN
                    IF EXISTS (
                        SELECT 1 FROM information_schema.table_constraints 
                        WHERE constraint_name = 'purchase_bills_approved_by_fkey'
                    ) THEN
                        ALTER TABLE purchase_bills DROP CONSTRAINT purchase_bills_approved_by_fkey;
                    END IF;
                END $$;
            """))
        else:
            # SQLite doesn't support dropping constraints directly
            # The constraint won't be enforced anyway in SQLite with default settings
            pass
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Fixed approved_by constraint - can now approve bills!',
            'details': 'Removed foreign key constraint on approved_by field'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Migration failed: {str(e)}',
            'details': str(e)
        }), 500


@migration_bp.route('/add-vendor-payment-tracking')
def add_vendor_payment_tracking():
    """
    Add Vendor Payment Tracking tables
    Access: /migrate/add-vendor-payment-tracking
    """
    try:
        db_type = os.environ.get('DATABASE_URL', '').split(':')[0] if os.environ.get('DATABASE_URL') else 'sqlite'
        
        if db_type == 'postgresql':
            # PostgreSQL syntax
            db.session.execute(text("""
                -- Vendor Payments table
                CREATE TABLE IF NOT EXISTS vendor_payments (
                    id SERIAL PRIMARY KEY,
                    tenant_id INTEGER NOT NULL REFERENCES tenants(id),
                    payment_number VARCHAR(50) UNIQUE NOT NULL,
                    payment_date DATE NOT NULL DEFAULT CURRENT_DATE,
                    vendor_id INTEGER NOT NULL REFERENCES vendors(id),
                    vendor_name VARCHAR(255) NOT NULL,
                    amount DECIMAL(15,2) NOT NULL,
                    payment_method VARCHAR(50) DEFAULT 'cash',
                    reference_number VARCHAR(100),
                    bank_account VARCHAR(100),
                    notes TEXT,
                    created_by VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                -- Payment Allocations table (link payments to bills)
                CREATE TABLE IF NOT EXISTS payment_allocations (
                    id SERIAL PRIMARY KEY,
                    payment_id INTEGER NOT NULL REFERENCES vendor_payments(id) ON DELETE CASCADE,
                    purchase_bill_id INTEGER NOT NULL REFERENCES purchase_bills(id) ON DELETE CASCADE,
                    amount_allocated DECIMAL(15,2) NOT NULL
                );
                
                -- Indexes for performance
                CREATE INDEX IF NOT EXISTS idx_vendor_payments_tenant ON vendor_payments(tenant_id);
                CREATE INDEX IF NOT EXISTS idx_vendor_payments_vendor ON vendor_payments(vendor_id);
                CREATE INDEX IF NOT EXISTS idx_vendor_payments_date ON vendor_payments(payment_date);
                CREATE INDEX IF NOT EXISTS idx_payment_allocations_payment ON payment_allocations(payment_id);
                CREATE INDEX IF NOT EXISTS idx_payment_allocations_bill ON payment_allocations(purchase_bill_id);
            """))
        else:
            # SQLite syntax
            db.session.execute(text("""
                -- Vendor Payments table
                CREATE TABLE IF NOT EXISTS vendor_payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL REFERENCES tenants(id),
                    payment_number VARCHAR(50) UNIQUE NOT NULL,
                    payment_date DATE NOT NULL DEFAULT (date('now')),
                    vendor_id INTEGER NOT NULL REFERENCES vendors(id),
                    vendor_name VARCHAR(255) NOT NULL,
                    amount DECIMAL(15,2) NOT NULL,
                    payment_method VARCHAR(50) DEFAULT 'cash',
                    reference_number VARCHAR(100),
                    bank_account VARCHAR(100),
                    notes TEXT,
                    created_by VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                -- Payment Allocations table (link payments to bills)
                CREATE TABLE IF NOT EXISTS payment_allocations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    payment_id INTEGER NOT NULL REFERENCES vendor_payments(id) ON DELETE CASCADE,
                    purchase_bill_id INTEGER NOT NULL REFERENCES purchase_bills(id) ON DELETE CASCADE,
                    amount_allocated DECIMAL(15,2) NOT NULL
                );
                
                -- Indexes for performance
                CREATE INDEX IF NOT EXISTS idx_vendor_payments_tenant ON vendor_payments(tenant_id);
                CREATE INDEX IF NOT EXISTS idx_vendor_payments_vendor ON vendor_payments(vendor_id);
                CREATE INDEX IF NOT EXISTS idx_vendor_payments_date ON vendor_payments(payment_date);
                CREATE INDEX IF NOT EXISTS idx_payment_allocations_payment ON payment_allocations(payment_id);
                CREATE INDEX IF NOT EXISTS idx_payment_allocations_bill ON payment_allocations(purchase_bill_id);
            """))
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Vendor Payment Tracking tables created successfully!',
            'tables': [
                'vendor_payments',
                'payment_allocations'
            ]
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Migration failed: {str(e)}',
            'details': str(e)
        }), 500

@migration_bp.route('/fix-vendor-payment-vendor-id')
def fix_vendor_payment_vendor_id():
    """
    Make vendor_id nullable in vendor_payments table
    This allows payments for manual vendor entries (not in vendor master)
    Access: /migrate/fix-vendor-payment-vendor-id
    """
    try:
        db_type = os.environ.get('DATABASE_URL', '').split(':')[0] if os.environ.get('DATABASE_URL') else 'sqlite'
        
        if db_type == 'postgresql':
            # PostgreSQL: Drop NOT NULL constraint
            db.session.execute(text("""
                ALTER TABLE vendor_payments 
                ALTER COLUMN vendor_id DROP NOT NULL;
            """))
        else:
            # SQLite: Need to recreate the table (SQLite doesn't support ALTER COLUMN)
            # But since we just created this table, we can check if any data exists
            result = db.session.execute(text("SELECT COUNT(*) FROM vendor_payments")).scalar()
            
            if result > 0:
                # Preserve data
                db.session.execute(text("""
                    -- Create temp table
                    CREATE TABLE vendor_payments_temp (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        tenant_id INTEGER NOT NULL REFERENCES tenants(id),
                        payment_number VARCHAR(50) UNIQUE NOT NULL,
                        payment_date DATE NOT NULL DEFAULT (date('now')),
                        vendor_id INTEGER REFERENCES vendors(id),
                        vendor_name VARCHAR(255) NOT NULL,
                        amount DECIMAL(15,2) NOT NULL,
                        payment_method VARCHAR(50) DEFAULT 'cash',
                        reference_number VARCHAR(100),
                        bank_account VARCHAR(100),
                        notes TEXT,
                        created_by VARCHAR(100),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                    
                    -- Copy data
                    INSERT INTO vendor_payments_temp 
                    SELECT * FROM vendor_payments;
                    
                    -- Drop old table
                    DROP TABLE vendor_payments;
                    
                    -- Rename temp to original
                    ALTER TABLE vendor_payments_temp RENAME TO vendor_payments;
                    
                    -- Recreate indexes
                    CREATE INDEX IF NOT EXISTS idx_vendor_payments_tenant ON vendor_payments(tenant_id);
                    CREATE INDEX IF NOT EXISTS idx_vendor_payments_vendor ON vendor_payments(vendor_id);
                    CREATE INDEX IF NOT EXISTS idx_vendor_payments_date ON vendor_payments(payment_date);
                """))
            else:
                # No data, just drop and recreate
                db.session.execute(text("DROP TABLE IF EXISTS vendor_payments"))
                db.session.execute(text("""
                    CREATE TABLE vendor_payments (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        tenant_id INTEGER NOT NULL REFERENCES tenants(id),
                        payment_number VARCHAR(50) UNIQUE NOT NULL,
                        payment_date DATE NOT NULL DEFAULT (date('now')),
                        vendor_id INTEGER REFERENCES vendors(id),
                        vendor_name VARCHAR(255) NOT NULL,
                        amount DECIMAL(15,2) NOT NULL,
                        payment_method VARCHAR(50) DEFAULT 'cash',
                        reference_number VARCHAR(100),
                        bank_account VARCHAR(100),
                        notes TEXT,
                        created_by VARCHAR(100),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                    
                    CREATE INDEX IF NOT EXISTS idx_vendor_payments_tenant ON vendor_payments(tenant_id);
                    CREATE INDEX IF NOT EXISTS idx_vendor_payments_vendor ON vendor_payments(vendor_id);
                    CREATE INDEX IF NOT EXISTS idx_vendor_payments_date ON vendor_payments(payment_date);
                """))
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Fixed vendor_id constraint - can now record payments for manual vendors!',
            'details': 'vendor_id is now nullable in vendor_payments table'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Migration failed: {str(e)}',
            'details': str(e)
        }), 500


@migration_bp.route('/add-gst-rate-to-items')
def add_gst_rate_to_items():
    """
    Add gst_rate column to items table for GST compliance
    Safe migration - preserves existing data, sets default 18% GST
    Access: /migrate/add-gst-rate-to-items
    """
    try:
        db_type = os.environ.get('DATABASE_URL', '').split(':')[0] if os.environ.get('DATABASE_URL') else 'sqlite'
        
        if db_type == 'postgresql':
            # PostgreSQL: Check if column exists
            check_sql = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='items' AND column_name='gst_rate'
            """)
            has_column = db.session.execute(check_sql).fetchone()
            
            if not has_column:
                # Add gst_rate column with default 18%
                db.session.execute(text("""
                    ALTER TABLE items 
                    ADD COLUMN gst_rate FLOAT DEFAULT 18.0;
                """))
                db.session.commit()
                
                return jsonify({
                    'status': 'success',
                    'message': '✅ GST Rate column added to items table!',
                    'details': 'All existing items now have default GST rate of 18%',
                    'next_step': 'You can now add/edit items with correct GST rates',
                    'features': [
                        'GST rate auto-fills in transactions',
                        'Correct GSTR-2 filtering (only GST bills)',
                        'GSTR-3B ITC calculation working',
                        'Bulk import now sets GST rates'
                    ]
                })
            else:
                return jsonify({
                    'status': 'info',
                    'message': 'ℹ️ GST Rate column already exists',
                    'details': 'No migration needed - column is already present'
                })
        
        else:
            # SQLite: Check if column exists
            columns_result = db.session.execute(text("PRAGMA table_info(items)")).fetchall()
            columns = [col[1] for col in columns_result]
            
            if 'gst_rate' not in columns:
                # SQLite doesn't support ADD COLUMN with default for existing rows
                # So we need to add column, then update all rows
                db.session.execute(text("""
                    ALTER TABLE items ADD COLUMN gst_rate FLOAT;
                """))
                
                # Set default 18% for all existing items
                db.session.execute(text("""
                    UPDATE items SET gst_rate = 18.0 WHERE gst_rate IS NULL;
                """))
                
                db.session.commit()
                
                return jsonify({
                    'status': 'success',
                    'message': '✅ GST Rate column added to items table!',
                    'details': 'All existing items now have default GST rate of 18%',
                    'database': 'SQLite (local development)'
                })
            else:
                return jsonify({
                    'status': 'info',
                    'message': 'ℹ️ GST Rate column already exists',
                    'details': 'No migration needed - column is already present'
                })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Migration failed: {str(e)}',
            'details': str(e),
            'help': 'Contact support if this error persists'
        }), 500


@migration_bp.route('/add-commission-tables')
def add_commission_tables():
    """
    Add commission tracking tables for sales agents
    
    Creates:
    - commission_agents table (tracks sales agents and their commission %)
    - invoice_commissions table (links invoices to agents with commission amounts)
    
    Safe migration - only creates new tables, no modification to existing data
    Access this URL once: /migrate/add-commission-tables
    """
    try:
        db_url = db.engine.url.drivername
        
        if 'postgresql' in db_url:
            # PostgreSQL syntax
            create_tables = text("""
                -- Create commission_agents table
                CREATE TABLE IF NOT EXISTS commission_agents (
                    id SERIAL PRIMARY KEY,
                    tenant_id INTEGER NOT NULL REFERENCES tenants(id),
                    name VARCHAR(200) NOT NULL,
                    code VARCHAR(50),
                    phone VARCHAR(20),
                    email VARCHAR(120),
                    default_commission_percentage FLOAT DEFAULT 1.0,
                    employee_id INTEGER REFERENCES employees(id),
                    agent_type VARCHAR(20) DEFAULT 'external',
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_by INTEGER REFERENCES users(id),
                    CONSTRAINT unique_tenant_employee_agent UNIQUE (tenant_id, employee_id),
                    CONSTRAINT unique_tenant_agent_code UNIQUE (tenant_id, code)
                );
                
                -- Create index for performance
                CREATE INDEX IF NOT EXISTS idx_tenant_active ON commission_agents(tenant_id, is_active);
                
                -- Create invoice_commissions table
                CREATE TABLE IF NOT EXISTS invoice_commissions (
                    id SERIAL PRIMARY KEY,
                    tenant_id INTEGER NOT NULL REFERENCES tenants(id),
                    invoice_id INTEGER NOT NULL REFERENCES invoices(id),
                    agent_id INTEGER NOT NULL REFERENCES commission_agents(id),
                    agent_name VARCHAR(200) NOT NULL,
                    agent_code VARCHAR(50),
                    commission_percentage FLOAT NOT NULL,
                    invoice_amount FLOAT NOT NULL,
                    commission_amount FLOAT NOT NULL,
                    is_paid BOOLEAN DEFAULT FALSE,
                    paid_date DATE,
                    payment_notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    CONSTRAINT unique_invoice_commission UNIQUE (invoice_id)
                );
                
                -- Create indexes for performance
                CREATE INDEX IF NOT EXISTS idx_tenant_agent_paid ON invoice_commissions(tenant_id, agent_id, is_paid);
                CREATE INDEX IF NOT EXISTS idx_tenant_paid_date ON invoice_commissions(tenant_id, paid_date);
            """)
            
            db.session.execute(create_tables)
            db.session.commit()
            
            return jsonify({
                'status': 'success',
                'message': '✅ Commission tracking tables created successfully!',
                'details': {
                    'tables_created': [
                        'commission_agents (Sales agents with commission %)',
                        'invoice_commissions (Commission records per invoice)'
                    ],
                    'indexes_created': [
                        'idx_tenant_active (commission_agents)',
                        'idx_tenant_agent_paid (invoice_commissions)',
                        'idx_tenant_paid_date (invoice_commissions)'
                    ]
                },
                'database': 'PostgreSQL (Production)',
                'next_steps': [
                    '1. Go to Admin > Parties > Commission Agents',
                    '2. Add commission agents (internal employees or external)',
                    '3. Edit employees to link them as commission agents',
                    '4. Commission section will appear on invoice creation'
                ]
            })
        
        else:
            # SQLite syntax
            create_tables = text("""
                -- Create commission_agents table
                CREATE TABLE IF NOT EXISTS commission_agents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    name VARCHAR(200) NOT NULL,
                    code VARCHAR(50),
                    phone VARCHAR(20),
                    email VARCHAR(120),
                    default_commission_percentage REAL DEFAULT 1.0,
                    employee_id INTEGER,
                    agent_type VARCHAR(20) DEFAULT 'external',
                    is_active INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_by INTEGER,
                    FOREIGN KEY (tenant_id) REFERENCES tenants(id),
                    FOREIGN KEY (employee_id) REFERENCES employees(id),
                    FOREIGN KEY (created_by) REFERENCES users(id),
                    UNIQUE (tenant_id, employee_id),
                    UNIQUE (tenant_id, code)
                );
                
                -- Create index for performance
                CREATE INDEX IF NOT EXISTS idx_tenant_active ON commission_agents(tenant_id, is_active);
                
                -- Create invoice_commissions table
                CREATE TABLE IF NOT EXISTS invoice_commissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    invoice_id INTEGER NOT NULL,
                    agent_id INTEGER NOT NULL,
                    agent_name VARCHAR(200) NOT NULL,
                    agent_code VARCHAR(50),
                    commission_percentage REAL NOT NULL,
                    invoice_amount REAL NOT NULL,
                    commission_amount REAL NOT NULL,
                    is_paid INTEGER DEFAULT 0,
                    paid_date DATE,
                    payment_notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (tenant_id) REFERENCES tenants(id),
                    FOREIGN KEY (invoice_id) REFERENCES invoices(id),
                    FOREIGN KEY (agent_id) REFERENCES commission_agents(id),
                    UNIQUE (invoice_id)
                );
                
                -- Create indexes for performance
                CREATE INDEX IF NOT EXISTS idx_tenant_agent_paid ON invoice_commissions(tenant_id, agent_id, is_paid);
                CREATE INDEX IF NOT EXISTS idx_tenant_paid_date ON invoice_commissions(tenant_id, paid_date);
            """)
            
            db.session.execute(create_tables)
            db.session.commit()
            
            return jsonify({
                'status': 'success',
                'message': '✅ Commission tracking tables created successfully!',
                'details': {
                    'tables_created': [
                        'commission_agents (Sales agents with commission %)',
                        'invoice_commissions (Commission records per invoice)'
                    ],
                    'indexes_created': [
                        'idx_tenant_active (commission_agents)',
                        'idx_tenant_agent_paid (invoice_commissions)',
                        'idx_tenant_paid_date (invoice_commissions)'
                    ]
                },
                'database': 'SQLite (Local Development)',
                'next_steps': [
                    '1. Go to Admin > Parties > Commission Agents',
                    '2. Add commission agents (internal employees or external)',
                    '3. Edit employees to link them as commission agents',
                    '4. Commission section will appear on invoice creation'
                ]
            })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Commission migration failed: {str(e)}',
            'details': str(e),
            'help': 'Check if tables already exist or contact support'
        }), 500


@migration_bp.route('/add-bank-accounts')
def add_bank_accounts():
    """
    PHASE 1: Add Bank/Cash Account Management
    
    Creates:
    - bank_accounts table (manage cash & bank accounts)
    - account_transactions table (track all money movements)
    
    Access this URL once: /migrate/add-bank-accounts
    """
    try:
        print("=" * 60)
        print("🚀 PHASE 1: Bank/Cash Account Management")
        print("=" * 60)
        
        # Create bank_accounts table
        print("\n📊 Creating bank_accounts table...")
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS bank_accounts (
                id SERIAL PRIMARY KEY,
                tenant_id INTEGER NOT NULL,
                
                -- Account Details
                account_name VARCHAR(100) NOT NULL,
                account_type VARCHAR(20) NOT NULL DEFAULT 'bank',
                -- Types: 'cash', 'bank', 'petty_cash'
                
                -- Bank Details (NULL for cash accounts)
                bank_name VARCHAR(100),
                account_number VARCHAR(50),
                ifsc_code VARCHAR(20),
                branch VARCHAR(100),
                
                -- Balance
                opening_balance DECIMAL(15, 2) DEFAULT 0.00,
                current_balance DECIMAL(15, 2) DEFAULT 0.00,
                
                -- Status
                is_active BOOLEAN DEFAULT TRUE,
                is_default BOOLEAN DEFAULT FALSE,
                
                -- Notes
                description TEXT,
                
                -- Timestamps
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                -- Foreign Keys
                CONSTRAINT fk_bank_account_tenant 
                    FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE
            )
        """))
        
        # Add indexes for performance
        print("📌 Adding indexes to bank_accounts...")
        db.session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_bank_accounts_tenant 
            ON bank_accounts(tenant_id, is_active)
        """))
        
        db.session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_bank_accounts_type 
            ON bank_accounts(tenant_id, account_type, is_active)
        """))
        
        db.session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_bank_accounts_default 
            ON bank_accounts(tenant_id, is_default)
        """))
        
        # Create account_transactions table
        print("\n📊 Creating account_transactions table...")
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS account_transactions (
                id SERIAL PRIMARY KEY,
                tenant_id INTEGER NOT NULL,
                
                -- Account Reference
                account_id INTEGER NOT NULL,
                
                -- Transaction Details
                transaction_date DATE NOT NULL,
                transaction_type VARCHAR(50) NOT NULL,
                -- Types: 'invoice_payment', 'bill_payment', 'expense', 
                --        'contra', 'employee_advance', 'opening_balance'
                
                -- Amount
                debit_amount DECIMAL(15, 2) DEFAULT 0.00,
                credit_amount DECIMAL(15, 2) DEFAULT 0.00,
                balance_after DECIMAL(15, 2) DEFAULT 0.00,
                
                -- Reference
                reference_type VARCHAR(50),
                -- Types: 'invoice', 'purchase_bill', 'expense', 'contra'
                reference_id INTEGER,
                voucher_number VARCHAR(50),
                
                -- Description
                narration TEXT,
                
                -- Timestamps
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by INTEGER,
                
                -- Foreign Keys
                CONSTRAINT fk_account_transaction_tenant 
                    FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE,
                CONSTRAINT fk_account_transaction_account 
                    FOREIGN KEY (account_id) REFERENCES bank_accounts(id) ON DELETE CASCADE,
                CONSTRAINT fk_account_transaction_user 
                    FOREIGN KEY (created_by) REFERENCES users(id)
            )
        """))
        
        # Add indexes for performance
        print("📌 Adding indexes to account_transactions...")
        db.session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_account_transactions_tenant 
            ON account_transactions(tenant_id, transaction_date DESC)
        """))
        
        db.session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_account_transactions_account 
            ON account_transactions(account_id, transaction_date DESC)
        """))
        
        db.session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_account_transactions_reference 
            ON account_transactions(reference_type, reference_id)
        """))
        
        db.session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_account_transactions_type 
            ON account_transactions(tenant_id, transaction_type)
        """))
        
        db.session.commit()
        print("\n✅ Tables created successfully!")
        
        # Create default "Cash in Hand" account for all existing tenants
        print("\n💵 Creating default 'Cash in Hand' accounts...")
        from models.tenant import Tenant
        import pytz
        
        tenants = Tenant.query.all()
        ist = pytz.timezone('Asia/Kolkata')
        now = datetime.now(ist)
        
        for tenant in tenants:
            # Check if cash account already exists
            existing = db.session.execute(
                text("SELECT id FROM bank_accounts WHERE tenant_id = :tenant_id AND account_type = 'cash'"),
                {'tenant_id': tenant.id}
            ).fetchone()
            
            if not existing:
                db.session.execute(text("""
                    INSERT INTO bank_accounts 
                    (tenant_id, account_name, account_type, opening_balance, 
                     current_balance, is_active, is_default, description, created_at, updated_at)
                    VALUES (:tenant_id, :name, :type, :opening, :current, :active, :default, :desc, :created, :updated)
                """), {
                    'tenant_id': tenant.id,
                    'name': 'Cash in Hand',
                    'type': 'cash',
                    'opening': 0.00,
                    'current': 0.00,
                    'active': True,
                    'default': True,
                    'desc': 'Default cash account for daily transactions',
                    'created': now,
                    'updated': now
                })
                print(f"  ✅ Created cash account for: {tenant.company_name}")
        
        db.session.commit()
        
        print("\n" + "=" * 60)
        print("✅ PHASE 1 DATABASE MIGRATION COMPLETED!")
        print("=" * 60)
        
        return jsonify({
            'status': 'success',
            'message': '✅ Phase 1: Bank/Cash Account Management - Database Created!',
            'details': {
                'tables_created': [
                    'bank_accounts (Manage cash & bank accounts)',
                    'account_transactions (Track all money movements)'
                ],
                'indexes_created': [
                    'idx_bank_accounts_tenant',
                    'idx_bank_accounts_type',
                    'idx_bank_accounts_default',
                    'idx_account_transactions_tenant',
                    'idx_account_transactions_account',
                    'idx_account_transactions_reference',
                    'idx_account_transactions_type'
                ],
                'default_accounts': f'Created "Cash in Hand" for {len(tenants)} tenants'
            },
            'next_steps': [
                '1. Go to Admin Dashboard',
                '2. New menu: 💰 Bank & Cash Accounts',
                '3. View your default "Cash in Hand" account',
                '4. Add your bank accounts (HDFC, ICICI, etc.)',
                '5. Ready for Phase 2: Contra Vouchers!'
            ]
        })
        
    except Exception as e:
        db.session.rollback()
        import traceback
        return jsonify({
            'status': 'error',
            'message': f'Bank accounts migration failed: {str(e)}',
            'traceback': traceback.format_exc(),
            'help': 'Check if tables already exist or contact support'
        }), 500


@migration_bp.route('/fix-employee-transactions')
def fix_employee_transactions():
    """
    Make account_id nullable in account_transactions for employee expenses
    Phase 3 Fix: Employee expenses don't need a bank account reference
    
    Access this URL once: /migrate/fix-employee-transactions
    """
    try:
        print("=" * 60)
        print("🔧 FIX: Make account_id nullable for employee transactions")
        print("=" * 60)
        
        # Check if column is already nullable
        inspector = db.inspect(db.engine)
        columns = inspector.get_columns('account_transactions')
        account_id_col = next((col for col in columns if col['name'] == 'account_id'), None)
        
        if account_id_col and not account_id_col['nullable']:
            print("\n📝 Making account_id nullable...")
            db.session.execute(text("""
                ALTER TABLE account_transactions 
                ALTER COLUMN account_id DROP NOT NULL
            """))
            db.session.commit()
            print("✅ account_id is now nullable!")
        else:
            print("✅ account_id is already nullable!")
        
        print("\n" + "=" * 60)
        print("✅ EMPLOYEE TRANSACTION FIX COMPLETED!")
        print("=" * 60)
        
        return jsonify({
            'status': 'success',
            'message': '✅ Employee transaction fix complete!',
            'details': {
                'change': 'account_id column in account_transactions is now nullable',
                'reason': 'Employee expenses do not require a bank/cash account reference'
            },
            'next_steps': [
                'Now you can record employee expenses without errors!',
                'Employee expenses will have account_id = NULL'
            ]
        })
        
    except Exception as e:
        db.session.rollback()
        import traceback
        return jsonify({
            'status': 'error',
            'message': f'Employee transaction fix failed: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500


@migration_bp.route('/clean-duplicate-employee-transactions')
def clean_duplicate_employee_transactions():
    """
    CLEANUP: Remove duplicate employee transactions from old data
    
    Problem: Old cash advances created 2 transactions with SAME voucher:
    - One with CREDIT (company giving money - the duplicate)
    - One with DEBIT (employee receiving money - the real one)
    
    Solution: Keep DEBIT transactions, delete CREDIT transactions
    
    Access this URL once: /migrate/clean-duplicate-employee-transactions
    """
    try:
        print("=" * 60)
        print("🧹 CLEANUP: Removing duplicate employee transactions (v2)")
        print("=" * 60)
        
        # Count duplicates before cleanup (CREDIT = company side = duplicate)
        print("\n🔍 Counting duplicate transactions...")
        duplicate_count = db.session.execute(text("""
            SELECT COUNT(*)
            FROM account_transactions
            WHERE transaction_type = 'employee_advance'
            AND reference_type = 'employee'
            AND credit_amount > 0
            AND debit_amount = 0
        """)).fetchone()[0]
        
        print(f"  Found {duplicate_count} duplicate cash advance transactions (CREDIT side)")
        
        if duplicate_count == 0:
            print("  ✅ No duplicates found! System is clean.")
            return jsonify({
                'status': 'success',
                'message': '✅ No duplicate transactions found!',
                'details': 'Employee ledgers are already clean'
            })
        
        # Delete company-side duplicates (CREDIT transactions for employee_advance)
        print(f"\n🗑️  Deleting {duplicate_count} company-side duplicates (CREDIT)...")
        db.session.execute(text("""
            DELETE FROM account_transactions
            WHERE transaction_type = 'employee_advance'
            AND reference_type = 'employee'
            AND credit_amount > 0
            AND debit_amount = 0
        """))
        
        db.session.commit()
        print(f"  ✅ Deleted {duplicate_count} duplicate transactions")
        
        # Count what remains (should be DEBIT = employee receiving money)
        remaining_advances = db.session.execute(text("""
            SELECT COUNT(*)
            FROM account_transactions
            WHERE transaction_type = 'employee_advance'
            AND reference_type = 'employee'
        """)).fetchone()[0]
        
        print("\n" + "=" * 60)
        print(f"✅ CLEANUP COMPLETED! Removed {duplicate_count} duplicates")
        print(f"   Remaining employee advances: {remaining_advances} (clean data)")
        print("=" * 60)
        
        return jsonify({
            'status': 'success',
            'message': f'✅ Cleanup complete! Removed {duplicate_count} duplicate transactions',
            'details': {
                'duplicates_removed': int(duplicate_count),
                'remaining_clean_transactions': int(remaining_advances),
                'logic': 'Kept DEBIT (employee receiving), deleted CREDIT (company giving - duplicate)',
                'why': 'Employee ledger should only show employee side, not company side'
            },
            'next_steps': [
                'Employee ledgers are now clean!',
                'No more duplicate voucher numbers',
                'Refresh any open employee ledger page to see clean data'
            ]
        })
        
    except Exception as e:
        db.session.rollback()
        import traceback
        return jsonify({
            'status': 'error',
            'message': f'Cleanup failed: {str(e)}',
            'traceback': traceback.format_exc(),
            'help': 'Contact support if this persists'
        }), 500


@migration_bp.route('/fix-account-balances')
def fix_account_balances():
    """Fix account balances by recalculating from last transaction"""
    try:
        tenant_id = get_current_tenant_id()
        
        print("=" * 60)
        print("🔧 FIX: Recalculating account balances from transactions")
        print("=" * 60)
        
        # Get all active accounts for this tenant
        accounts = db.session.execute(text("""
            SELECT id, account_name, current_balance
            FROM bank_accounts
            WHERE tenant_id = :tenant_id AND is_active = TRUE
        """), {'tenant_id': tenant_id}).fetchall()
        
        fixed_accounts = []
        
        for account in accounts:
            account_id = account[0]
            account_name = account[1]
            old_balance = account[2]
            
            # Get the last transaction for this account
            last_txn = db.session.execute(text("""
                SELECT balance_after
                FROM account_transactions
                WHERE tenant_id = :tenant_id AND account_id = :account_id
                ORDER BY transaction_date DESC, created_at DESC, id DESC
                LIMIT 1
            """), {'tenant_id': tenant_id, 'account_id': account_id}).fetchone()
            
            if last_txn:
                correct_balance = last_txn[0]
                
                if float(old_balance) != float(correct_balance):
                    # Update the account balance
                    db.session.execute(text("""
                        UPDATE bank_accounts
                        SET current_balance = :correct_balance, updated_at = CURRENT_TIMESTAMP
                        WHERE id = :account_id AND tenant_id = :tenant_id
                    """), {'correct_balance': correct_balance, 'account_id': account_id, 'tenant_id': tenant_id})
                    
                    fixed_accounts.append({
                        'account_name': account_name,
                        'old_balance': float(old_balance),
                        'new_balance': float(correct_balance),
                        'difference': float(correct_balance) - float(old_balance)
                    })
                    
                    print(f"✅ Fixed {account_name}: ₹{old_balance:,.2f} → ₹{correct_balance:,.2f}")
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': f'✅ Fixed {len(fixed_accounts)} account balance(s)!',
            'fixed_accounts': fixed_accounts,
            'total_fixed': len(fixed_accounts),
            'next_steps': [
                'Account balances now match transaction ledgers',
                'Refresh Bank & Cash Accounts page',
                'Refresh Cash Book report - closing balance will be correct'
            ]
        })
        
    except Exception as e:
        db.session.rollback()
        import traceback
        return jsonify({
            'status': 'error',
            'message': f'Fix failed: {str(e)}',
            'traceback': traceback.format_exc(),
            'help': 'Contact support if this persists'
        }), 500


@migration_bp.route('/find-orphaned-transactions')
def find_orphaned_transactions():
    """Find invoice payments not linked to any bank/cash account"""
    try:
        tenant_id = get_current_tenant_id()
        
        print("=" * 60)
        print("🔍 DIAGNOSTIC: Finding orphaned invoice transactions")
        print("=" * 60)
        
        # Find invoice payment transactions with NULL or invalid account_id
        orphaned = db.session.execute(text("""
            SELECT 
                at.id,
                at.transaction_date,
                at.transaction_type,
                at.debit_amount,
                at.credit_amount,
                at.account_id,
                at.voucher_number,
                at.narration,
                at.reference_id,
                ba.account_name
            FROM account_transactions at
            LEFT JOIN bank_accounts ba ON at.account_id = ba.id AND at.tenant_id = ba.tenant_id
            WHERE at.tenant_id = :tenant_id 
            AND at.transaction_type = 'invoice_payment'
            AND (at.account_id IS NULL OR ba.id IS NULL)
            ORDER BY at.transaction_date DESC
        """), {'tenant_id': tenant_id}).fetchall()
        
        orphaned_list = []
        for txn in orphaned:
            orphaned_list.append({
                'transaction_id': txn[0],
                'date': str(txn[1]),
                'type': txn[2],
                'debit': float(txn[3]),
                'credit': float(txn[4]),
                'account_id': txn[5],
                'voucher_number': txn[6],
                'narration': txn[7],
                'invoice_id': txn[8]
            })
        
        return jsonify({
            'status': 'success',
            'message': f'Found {len(orphaned_list)} orphaned transaction(s)',
            'orphaned_transactions': orphaned_list,
            'explanation': 'These transactions are not linked to any bank/cash account',
            'next_step': 'Use /migrate/fix-orphaned-transactions to fix them'
        })
        
    except Exception as e:
        import traceback
        return jsonify({
            'status': 'error',
            'message': f'Diagnostic failed: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500


@migration_bp.route('/fix-orphaned-transactions')
def fix_orphaned_transactions():
    """Fix orphaned invoice payment transactions by linking to Cash in Hand"""
    try:
        tenant_id = get_current_tenant_id()
        
        print("=" * 60)
        print("🔧 FIX: Linking orphaned transactions to Cash in Hand")
        print("=" * 60)
        
        # Get Cash in Hand account
        cash_account = db.session.execute(text("""
            SELECT id, account_name
            FROM bank_accounts
            WHERE tenant_id = :tenant_id AND account_type = 'cash'
            ORDER BY is_default DESC, id ASC
            LIMIT 1
        """), {'tenant_id': tenant_id}).fetchone()
        
        if not cash_account:
            return jsonify({
                'status': 'error',
                'message': 'No cash account found!'
            }), 400
        
        cash_account_id = cash_account[0]
        cash_account_name = cash_account[1]
        
        # Find orphaned invoice payment transactions
        orphaned = db.session.execute(text("""
            SELECT 
                at.id,
                at.voucher_number,
                at.debit_amount,
                at.transaction_date
            FROM account_transactions at
            LEFT JOIN bank_accounts ba ON at.account_id = ba.id AND at.tenant_id = ba.tenant_id
            WHERE at.tenant_id = :tenant_id 
            AND at.transaction_type = 'invoice_payment'
            AND (at.account_id IS NULL OR ba.id IS NULL)
        """), {'tenant_id': tenant_id}).fetchall()
        
        fixed_transactions = []
        
        for txn in orphaned:
            txn_id = txn[0]
            voucher = txn[1]
            amount = txn[2]
            
            # Update the transaction to link to Cash in Hand
            db.session.execute(text("""
                UPDATE account_transactions
                SET account_id = :account_id
                WHERE id = :txn_id AND tenant_id = :tenant_id
            """), {'account_id': cash_account_id, 'txn_id': txn_id, 'tenant_id': tenant_id})
            
            fixed_transactions.append({
                'voucher': voucher,
                'amount': float(amount),
                'linked_to': cash_account_name
            })
            
            print(f"✅ Fixed {voucher}: ₹{amount:,.2f} → {cash_account_name}")
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': f'✅ Fixed {len(fixed_transactions)} orphaned transaction(s)!',
            'fixed_transactions': fixed_transactions,
            'linked_to_account': cash_account_name,
            'next_steps': [
                'Now run /migrate/recalculate-account-balances to fix all balances',
                'Then refresh Cash in Hand statement',
                'Missing transactions will now appear!'
            ]
        })
        
    except Exception as e:
        db.session.rollback()
        import traceback
        return jsonify({
            'status': 'error',
            'message': f'Fix failed: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500


@migration_bp.route('/recalculate-account-balances')
def recalculate_account_balances():
    """Recalculate ALL balance_after values for all transactions in sequence"""
    try:
        tenant_id = get_current_tenant_id()
        
        print("=" * 60)
        print("🔧 RECALCULATING: All transaction balances from scratch")
        print("=" * 60)
        
        # Get all accounts
        accounts = db.session.execute(text("""
            SELECT id, account_name, opening_balance
            FROM bank_accounts
            WHERE tenant_id = :tenant_id AND is_active = TRUE
        """), {'tenant_id': tenant_id}).fetchall()
        
        recalculated_accounts = []
        
        for account in accounts:
            account_id = account[0]
            account_name = account[1]
            opening_balance = float(account[2])
            
            # Get all transactions for this account in chronological order
            # EXCLUDE opening_balance type - that's already in bank_accounts.opening_balance
            transactions = db.session.execute(text("""
                SELECT id, debit_amount, credit_amount
                FROM account_transactions
                WHERE tenant_id = :tenant_id 
                AND account_id = :account_id
                AND transaction_type != 'opening_balance'
                ORDER BY transaction_date ASC, created_at ASC, id ASC
            """), {'tenant_id': tenant_id, 'account_id': account_id}).fetchall()
            
            running_balance = opening_balance
            updated_count = 0
            
            for txn in transactions:
                txn_id = txn[0]
                debit = float(txn[1])
                credit = float(txn[2])
                
                # Calculate correct balance
                running_balance = running_balance + debit - credit
                
                # Update the transaction
                db.session.execute(text("""
                    UPDATE account_transactions
                    SET balance_after = :balance
                    WHERE id = :txn_id
                """), {'balance': running_balance, 'txn_id': txn_id})
                
                updated_count += 1
            
            # Update account's current_balance
            db.session.execute(text("""
                UPDATE bank_accounts
                SET current_balance = :balance, updated_at = CURRENT_TIMESTAMP
                WHERE id = :account_id AND tenant_id = :tenant_id
            """), {'balance': running_balance, 'account_id': account_id, 'tenant_id': tenant_id})
            
            recalculated_accounts.append({
                'account_name': account_name,
                'transactions_updated': updated_count,
                'final_balance': running_balance
            })
            
            print(f"✅ {account_name}: {updated_count} transactions, Final: ₹{running_balance:,.2f}")
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': f'✅ Recalculated balances for {len(recalculated_accounts)} account(s)!',
            'recalculated_accounts': recalculated_accounts,
            'next_steps': [
                'All transaction balances are now correct',
                'All account current_balance values are accurate',
                'Refresh all reports and statements',
                'Everything should now match!'
            ]
        })
        
    except Exception as e:
        db.session.rollback()
        import traceback
        return jsonify({
            'status': 'error',
            'message': f'Recalculation failed: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500


@migration_bp.route('/diagnose-invoice-payment/<invoice_number>')
def diagnose_invoice_payment(invoice_number):
    """Deep diagnostic for a specific invoice payment"""
    try:
        tenant_id = get_current_tenant_id()
        
        print("=" * 60)
        print(f"🔍 DEEP DIAGNOSTIC: Invoice {invoice_number}")
        print("=" * 60)
        
        # 1. Check if invoice exists
        invoice = db.session.execute(text("""
            SELECT 
                id, invoice_number, customer_name, total_amount, 
                payment_status, invoice_date
            FROM invoices
            WHERE tenant_id = :tenant_id AND invoice_number = :invoice_number
        """), {'tenant_id': tenant_id, 'invoice_number': invoice_number}).fetchone()
        
        if not invoice:
            return jsonify({
                'status': 'error',
                'message': f'Invoice {invoice_number} not found!'
            }), 404
        
        invoice_info = {
            'id': invoice[0],
            'invoice_number': invoice[1],
            'customer_name': invoice[2],
            'total_amount': float(invoice[3]),
            'payment_status': invoice[4],
            'invoice_date': str(invoice[5])
        }
        
        # 2. Check if account_transactions exists for this invoice
        transactions = db.session.execute(text("""
            SELECT 
                id, transaction_date, transaction_type, 
                debit_amount, credit_amount, balance_after,
                account_id, voucher_number, narration
            FROM account_transactions
            WHERE tenant_id = :tenant_id 
            AND reference_type = 'invoice'
            AND reference_id = :invoice_id
        """), {'tenant_id': tenant_id, 'invoice_id': invoice[0]}).fetchall()
        
        transaction_list = []
        for txn in transactions:
            # Get account name if account_id exists
            account_name = None
            if txn[6]:
                acc = db.session.execute(text("""
                    SELECT account_name FROM bank_accounts 
                    WHERE id = :account_id AND tenant_id = :tenant_id
                """), {'account_id': txn[6], 'tenant_id': tenant_id}).fetchone()
                account_name = acc[0] if acc else 'Account Not Found!'
            
            transaction_list.append({
                'transaction_id': txn[0],
                'date': str(txn[1]),
                'type': txn[2],
                'debit': float(txn[3]),
                'credit': float(txn[4]),
                'balance_after': float(txn[5]),
                'account_id': txn[6],
                'account_name': account_name,
                'voucher_number': txn[7],
                'narration': txn[8]
            })
        
        # 3. Check if payment_received is 'yes' but no transaction
        diagnosis = []
        
        if invoice[4] == 'paid' and len(transactions) == 0:
            diagnosis.append('⚠️ Invoice marked as PAID but NO account_transaction found!')
            diagnosis.append('This invoice payment was never recorded to any account')
            diagnosis.append('Need to manually create the transaction')
        
        if len(transactions) > 0 and transactions[0][6] is None:
            diagnosis.append('⚠️ Transaction exists but account_id is NULL!')
            diagnosis.append('Run /migrate/fix-orphaned-transactions to fix')
        
        if len(transactions) == 0 and invoice[4] != 'paid':
            diagnosis.append('✅ Invoice is unpaid - no transaction expected')
        
        if len(transactions) > 0 and transactions[0][6] is not None:
            diagnosis.append('✅ Transaction exists and is linked to an account')
            diagnosis.append(f'Linked to: {transaction_list[0]["account_name"]}')
        
        return jsonify({
            'status': 'success',
            'invoice': invoice_info,
            'transactions_found': len(transactions),
            'transactions': transaction_list,
            'diagnosis': diagnosis
        })
        
    except Exception as e:
        import traceback
        return jsonify({
            'status': 'error',
            'message': f'Diagnostic failed: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500


@migration_bp.route('/create-missing-invoice-payment/<invoice_number>')
def create_missing_invoice_payment(invoice_number):
    """Manually create missing account_transaction for a paid invoice"""
    try:
        tenant_id = get_current_tenant_id()
        
        print("=" * 60)
        print(f"🔧 CREATING: Missing payment transaction for {invoice_number}")
        print("=" * 60)
        
        # Get invoice details
        invoice = db.session.execute(text("""
            SELECT id, total_amount, invoice_date, customer_name
            FROM invoices
            WHERE tenant_id = :tenant_id AND invoice_number = :invoice_number
        """), {'tenant_id': tenant_id, 'invoice_number': invoice_number}).fetchone()
        
        if not invoice:
            return jsonify({
                'status': 'error',
                'message': f'Invoice {invoice_number} not found!'
            }), 404
        
        invoice_id = invoice[0]
        amount = invoice[1]
        invoice_date = invoice[2]
        customer_name = invoice[3]
        
        # Check if transaction already exists
        existing = db.session.execute(text("""
            SELECT COUNT(*) FROM account_transactions
            WHERE tenant_id = :tenant_id 
            AND reference_type = 'invoice'
            AND reference_id = :invoice_id
        """), {'tenant_id': tenant_id, 'invoice_id': invoice_id}).fetchone()[0]
        
        if existing > 0:
            return jsonify({
                'status': 'error',
                'message': 'Transaction already exists for this invoice!'
            }), 400
        
        # Get Cash in Hand account
        cash_account = db.session.execute(text("""
            SELECT id, account_name, current_balance
            FROM bank_accounts
            WHERE tenant_id = :tenant_id AND account_type = 'cash'
            ORDER BY is_default DESC, id ASC
            LIMIT 1
        """), {'tenant_id': tenant_id}).fetchone()
        
        if not cash_account:
            return jsonify({
                'status': 'error',
                'message': 'No cash account found!'
            }), 400
        
        account_id = cash_account[0]
        account_name = cash_account[1]
        current_balance = cash_account[2]
        
        # Get the last transaction before this invoice date to calculate correct balance
        last_txn = db.session.execute(text("""
            SELECT balance_after
            FROM account_transactions
            WHERE tenant_id = :tenant_id 
            AND account_id = :account_id
            AND transaction_date <= :invoice_date
            ORDER BY transaction_date DESC, created_at DESC, id DESC
            LIMIT 1
        """), {'tenant_id': tenant_id, 'account_id': account_id, 'invoice_date': invoice_date}).fetchone()
        
        # Calculate balance_after for this transaction
        if last_txn:
            balance_after = float(last_txn[0]) + float(amount)
        else:
            # No transactions before this date, use opening balance
            opening = db.session.execute(text("""
                SELECT opening_balance FROM bank_accounts
                WHERE id = :account_id AND tenant_id = :tenant_id
            """), {'account_id': account_id, 'tenant_id': tenant_id}).fetchone()[0]
            balance_after = float(opening) + float(amount)
        
        # Create the missing transaction
        from datetime import datetime
        import pytz
        ist = pytz.timezone('Asia/Kolkata')
        now = datetime.now(ist)
        
        db.session.execute(text("""
            INSERT INTO account_transactions
            (tenant_id, account_id, transaction_date, transaction_type,
             debit_amount, credit_amount, balance_after, reference_type, reference_id,
             voucher_number, narration, created_at, created_by)
            VALUES (:tenant_id, :account_id, :transaction_date, :transaction_type,
                    :debit_amount, :credit_amount, :balance_after, :reference_type, :reference_id,
                    :voucher_number, :narration, :created_at, :created_by)
        """), {
            'tenant_id': tenant_id,
            'account_id': account_id,
            'transaction_date': invoice_date,
            'transaction_type': 'invoice_payment',
            'debit_amount': amount,
            'credit_amount': 0,
            'balance_after': balance_after,
            'reference_type': 'invoice',
            'reference_id': invoice_id,
            'voucher_number': invoice_number,
            'narration': f'Payment received for {invoice_number} from {customer_name}',
            'created_at': now,
            'created_by': None
        })
        
        db.session.commit()
        
        print(f"✅ Created transaction: {invoice_number} → ₹{amount:,.2f} → {account_name}")
        
        return jsonify({
            'status': 'success',
            'message': f'✅ Created missing transaction for {invoice_number}!',
            'transaction_created': {
                'invoice_number': invoice_number,
                'amount': float(amount),
                'date': str(invoice_date),
                'account': account_name,
                'balance_after': balance_after
            },
            'next_steps': [
                'Now run: /migrate/recalculate-account-balances',
                'This will fix all subsequent transaction balances',
                'Then refresh Cash in Hand statement',
                f'{invoice_number} will appear in the ledger!'
            ]
        })
        
    except Exception as e:
        db.session.rollback()
        import traceback
        return jsonify({
            'status': 'error',
            'message': f'Failed to create transaction: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500


@migration_bp.route('/fix-opening-balances')
def fix_opening_balances():
    """
    FIX CRITICAL ACCOUNTING ISSUE: Opening balances causing Trial Balance imbalance
    
    PROBLEM:
    When bank/cash accounts were created with opening balances, they were recorded
    as single-sided entries (debits to Cash/Bank accounts) WITHOUT corresponding
    credit entries. This violates double-entry bookkeeping and causes Trial Balance
    to be out of balance.
    
    SOLUTION:
    1. Identify all opening balance transactions (transaction_type = 'opening_balance')
    2. Calculate total opening balance debits
    3. Create a single "Opening Balance - Equity" CREDIT entry to balance them
    4. This makes Trial Balance balanced and follows proper accounting principles
    
    Access: /migrate/fix-opening-balances
    """
    try:
        tenant_id = get_current_tenant_id()
        import pytz
        from decimal import Decimal
        
        ist = pytz.timezone('Asia/Kolkata')
        now = datetime.now(ist)
        
        print("=" * 80)
        print("🔧 FIXING OPENING BALANCE ACCOUNTING ISSUE")
        print("=" * 80)
        
        # Step 1: Check if there's already an opening balance equity entry
        existing_equity = db.session.execute(text("""
            SELECT id FROM account_transactions
            WHERE tenant_id = :tenant_id
            AND transaction_type = 'opening_balance_equity'
        """), {'tenant_id': tenant_id}).fetchone()
        
        if existing_equity:
            return jsonify({
                'status': 'info',
                'message': '✅ Opening balance equity entry already exists!',
                'details': 'No fix needed - opening balances are already properly recorded with double-entry.'
            })
        
        # Step 2: Get all opening balance transactions (the debit side)
        opening_balances = db.session.execute(text("""
            SELECT 
                at.id,
                at.account_id,
                ba.account_name,
                at.debit_amount,
                at.transaction_date
            FROM account_transactions at
            JOIN bank_accounts ba ON at.account_id = ba.id
            WHERE at.tenant_id = :tenant_id
            AND at.transaction_type = 'opening_balance'
            ORDER BY at.transaction_date, at.id
        """), {'tenant_id': tenant_id}).fetchall()
        
        if not opening_balances:
            return jsonify({
                'status': 'info',
                'message': 'ℹ️ No opening balance transactions found',
                'details': 'All opening balances appear to be set correctly or no accounts have been created yet.'
            })
        
        # Step 3: Calculate total opening balance (total debits)
        total_opening_balance = sum(Decimal(str(ob[3])) for ob in opening_balances)
        
        print(f"\n📊 OPENING BALANCE ANALYSIS:")
        print(f"{'='*80}")
        for ob in opening_balances:
            print(f"  {ob[2]:30} → Debit: ₹{ob[3]:>15,.2f}")
        print(f"{'='*80}")
        print(f"  {'TOTAL OPENING BALANCE (Debit)':30} → ₹{total_opening_balance:>15,.2f}")
        print(f"  {'Missing Credit Entry':30} → ₹{total_opening_balance:>15,.2f} ❌")
        print()
        
        # Step 4: Get the earliest opening balance date (for the equity entry)
        earliest_date = min(ob[4] for ob in opening_balances)
        
        # Step 5: Create a "virtual" Opening Balance - Equity account
        # We'll use account_id = None for equity (not a bank account)
        # The entry will be in account_transactions but linked to equity
        
        print("🔧 CREATING BALANCING ENTRY:")
        print(f"{'='*80}")
        print(f"  Date: {earliest_date}")
        print(f"  Type: Opening Balance - Equity (Credit)")
        print(f"  Amount: ₹{total_opening_balance:,.2f}")
        print(f"  Effect: This will balance the Trial Balance!")
        print()
        
        # Create the Opening Balance - Equity credit entry
        # NOTE: We use a special account_id = 0 to represent "Owner's Equity"
        # This is a placeholder - in future, create a proper equity accounts table
        
        db.session.execute(text("""
            INSERT INTO account_transactions (
                tenant_id, account_id, transaction_date, transaction_type,
                debit_amount, credit_amount, balance_after,
                reference_type, reference_id, voucher_number, narration,
                created_at, created_by
            )
            VALUES (
                :tenant_id, NULL, :transaction_date, 'opening_balance_equity',
                0, :credit_amount, :balance_after,
                'equity', NULL, 'OB-EQUITY-0001', 'Opening Balance - Owner Equity (Balancing Entry)',
                :created_at, NULL
            )
        """), {
            'tenant_id': tenant_id,
            'transaction_date': earliest_date,
            'credit_amount': float(total_opening_balance),
            'balance_after': float(total_opening_balance),  # Running balance for equity
            'created_at': now
        })
        
        db.session.commit()
        
        print("✅ OPENING BALANCE FIX COMPLETED!")
        print("=" * 80)
        
        # Step 6: Verify the fix by checking Trial Balance
        print("\n🔍 VERIFYING TRIAL BALANCE...")
        
        # Recalculate debits and credits
        totals = db.session.execute(text("""
            SELECT 
                SUM(debit_amount) as total_debit,
                SUM(credit_amount) as total_credit
            FROM account_transactions
            WHERE tenant_id = :tenant_id
        """), {'tenant_id': tenant_id}).fetchone()
        
        total_debit = Decimal(str(totals[0] or 0))
        total_credit = Decimal(str(totals[1] or 0))
        difference = total_debit - total_credit
        
        print(f"  Total Debits:  ₹{total_debit:,.2f}")
        print(f"  Total Credits: ₹{total_credit:,.2f}")
        print(f"  Difference:    ₹{difference:,.2f}")
        
        if difference == 0:
            print("  ✅ Trial Balance is NOW BALANCED! 🎉")
        else:
            print(f"  ⚠️ Still {difference:,.2f} difference (may need further investigation)")
        
        print("=" * 80)
        
        return jsonify({
            'status': 'success',
            'message': '✅ Opening balance fix applied successfully!',
            'opening_balances_fixed': [
                {
                    'account': ob[2],
                    'debit': float(ob[3]),
                    'date': str(ob[4])
                }
                for ob in opening_balances
            ],
            'equity_entry_created': {
                'type': 'Opening Balance - Equity',
                'credit_amount': float(total_opening_balance),
                'voucher': 'OB-EQUITY-0001',
                'narration': 'Opening Balance - Owner Equity (Balancing Entry)'
            },
            'trial_balance_status': {
                'total_debit': float(total_debit),
                'total_credit': float(total_credit),
                'difference': float(difference),
                'is_balanced': (difference == 0)
            },
            'next_steps': [
                'Go to Reports → Trial Balance',
                'It should now show: Total Debits = Total Credits',
                '✅ Trial Balance will be BALANCED!',
                'Balance Sheet will show correct Owner Equity',
                'All double-entry bookkeeping rules are now followed'
            ]
        })
        
    except Exception as e:
        db.session.rollback()
        import traceback
        return jsonify({
            'status': 'error',
            'message': f'❌ Failed to fix opening balances: {str(e)}',
            'traceback': traceback.format_exc(),
            'recommendation': 'Please contact support if this error persists'
        }), 500
