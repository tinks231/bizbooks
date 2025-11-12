"""
Subscription Management - Database Migration
Creates tables for subscription management
"""

from flask import Blueprint, jsonify
from models import db
from sqlalchemy import text

subscription_migration_bp = Blueprint('subscription_migration', __name__, url_prefix='/migrate')


@subscription_migration_bp.route('/add-subscription-tables')
def add_subscription_tables():
    """
    Creates subscription management tables
    
    Tables:
    1. subscription_plans - Membership/subscription plans
    2. customer_subscriptions - Active/expired customer subscriptions
    3. subscription_payments - Payment history for subscriptions
    """
    try:
        # Detect database type
        db_url = str(db.engine.url)
        is_postgres = 'postgresql' in db_url
        
        tables_created = []
        indexes_created = []
        
        # ================================================
        # TABLE 1: subscription_plans
        # ================================================
        if is_postgres:
            db.session.execute(text("""
                CREATE TABLE IF NOT EXISTS subscription_plans (
                    id SERIAL PRIMARY KEY,
                    tenant_id INTEGER NOT NULL REFERENCES tenants(id),
                    name VARCHAR(100) NOT NULL,
                    description TEXT,
                    price NUMERIC(10, 2) NOT NULL,
                    duration_days INTEGER NOT NULL,
                    is_active BOOLEAN DEFAULT true NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
        else:  # SQLite
            db.session.execute(text("""
                CREATE TABLE IF NOT EXISTS subscription_plans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    name VARCHAR(100) NOT NULL,
                    description TEXT,
                    price DECIMAL(10, 2) NOT NULL,
                    duration_days INTEGER NOT NULL,
                    is_active BOOLEAN DEFAULT 1 NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (tenant_id) REFERENCES tenants(id)
                )
            """))
        
        tables_created.append('subscription_plans (Membership/subscription plans)')
        
        # Index for tenant lookup
        db.session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_subscription_plans_tenant 
            ON subscription_plans(tenant_id, is_active)
        """))
        indexes_created.append('idx_subscription_plans_tenant')
        
        # ================================================
        # TABLE 2: customer_subscriptions
        # ================================================
        if is_postgres:
            db.session.execute(text("""
                CREATE TABLE IF NOT EXISTS customer_subscriptions (
                    id SERIAL PRIMARY KEY,
                    tenant_id INTEGER NOT NULL REFERENCES tenants(id),
                    customer_id INTEGER NOT NULL REFERENCES customers(id),
                    plan_id INTEGER NOT NULL REFERENCES subscription_plans(id),
                    start_date DATE NOT NULL,
                    current_period_start DATE NOT NULL,
                    current_period_end DATE NOT NULL,
                    status VARCHAR(20) DEFAULT 'active',
                    auto_renew BOOLEAN DEFAULT true,
                    cancelled_at TIMESTAMP,
                    cancellation_reason TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
        else:  # SQLite
            db.session.execute(text("""
                CREATE TABLE IF NOT EXISTS customer_subscriptions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    customer_id INTEGER NOT NULL,
                    plan_id INTEGER NOT NULL,
                    start_date DATE NOT NULL,
                    current_period_start DATE NOT NULL,
                    current_period_end DATE NOT NULL,
                    status VARCHAR(20) DEFAULT 'active',
                    auto_renew BOOLEAN DEFAULT 1,
                    cancelled_at TIMESTAMP,
                    cancellation_reason TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (tenant_id) REFERENCES tenants(id),
                    FOREIGN KEY (customer_id) REFERENCES customers(id),
                    FOREIGN KEY (plan_id) REFERENCES subscription_plans(id)
                )
            """))
        
        tables_created.append('customer_subscriptions (Active/expired subscriptions)')
        
        # Indexes for performance
        db.session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_customer_subscriptions_tenant_status 
            ON customer_subscriptions(tenant_id, status)
        """))
        indexes_created.append('idx_customer_subscriptions_tenant_status')
        
        db.session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_customer_subscriptions_due_date 
            ON customer_subscriptions(tenant_id, current_period_end)
        """))
        indexes_created.append('idx_customer_subscriptions_due_date')
        
        db.session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_customer_subscriptions_customer 
            ON customer_subscriptions(customer_id)
        """))
        indexes_created.append('idx_customer_subscriptions_customer')
        
        # ================================================
        # TABLE 3: subscription_payments
        # ================================================
        if is_postgres:
            db.session.execute(text("""
                CREATE TABLE IF NOT EXISTS subscription_payments (
                    id SERIAL PRIMARY KEY,
                    tenant_id INTEGER NOT NULL REFERENCES tenants(id),
                    subscription_id INTEGER NOT NULL REFERENCES customer_subscriptions(id),
                    invoice_id INTEGER REFERENCES invoices(id),
                    payment_date DATE NOT NULL,
                    amount NUMERIC(10, 2) NOT NULL,
                    payment_mode VARCHAR(50),
                    period_start DATE NOT NULL,
                    period_end DATE NOT NULL,
                    billing_period_label VARCHAR(50),
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
        else:  # SQLite
            db.session.execute(text("""
                CREATE TABLE IF NOT EXISTS subscription_payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    subscription_id INTEGER NOT NULL,
                    invoice_id INTEGER,
                    payment_date DATE NOT NULL,
                    amount DECIMAL(10, 2) NOT NULL,
                    payment_mode VARCHAR(50),
                    period_start DATE NOT NULL,
                    period_end DATE NOT NULL,
                    billing_period_label VARCHAR(50),
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (tenant_id) REFERENCES tenants(id),
                    FOREIGN KEY (subscription_id) REFERENCES customer_subscriptions(id),
                    FOREIGN KEY (invoice_id) REFERENCES invoices(id)
                )
            """))
        
        tables_created.append('subscription_payments (Payment history)')
        
        # Indexes
        db.session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_subscription_payments_subscription 
            ON subscription_payments(subscription_id)
        """))
        indexes_created.append('idx_subscription_payments_subscription')
        
        db.session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_subscription_payments_tenant_date 
            ON subscription_payments(tenant_id, payment_date)
        """))
        indexes_created.append('idx_subscription_payments_tenant_date')
        
        # Commit all changes
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': '✅ Subscription management tables created successfully!',
            'details': {
                'tables_created': tables_created,
                'indexes_created': indexes_created
            },
            'next_steps': [
                '1. Go to Admin > Subscriptions > Plans',
                '2. Create subscription plans (Monthly, Quarterly, etc.)',
                '3. Enroll customers in plans',
                '4. Track payments and renewals!'
            ]
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'❌ Migration failed: {str(e)}'
        }), 500

