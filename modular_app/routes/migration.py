"""
One-time migration routes for database updates
Access these URLs once after deployment to migrate the database
"""
from flask import Blueprint, jsonify
from models import db
from sqlalchemy import text

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
