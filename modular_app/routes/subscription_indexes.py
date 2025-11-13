"""
Add Performance Indexes for Subscription Tables

This migration adds critical database indexes to speed up
subscription queries (plans, members, payments, reports).
"""

from flask import Blueprint, jsonify
from models import db
from sqlalchemy import text

subscription_indexes_bp = Blueprint('subscription_indexes', __name__)


@subscription_indexes_bp.route('/migrate/add-subscription-indexes', methods=['GET'])
def add_subscription_indexes():
    """Add performance indexes to subscription tables"""
    
    try:
        # Detect database type
        db_url = str(db.engine.url)
        is_postgres = 'postgresql' in db_url
        
        indexes_created = []
        
        # ============================================================
        # SUBSCRIPTION PLANS INDEXES
        # ============================================================
        
        # Index 1: tenant_id (for filtering by tenant)
        try:
            if is_postgres:
                db.session.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_subscription_plans_tenant 
                    ON subscription_plans(tenant_id);
                """))
            else:  # SQLite
                db.session.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_subscription_plans_tenant 
                    ON subscription_plans(tenant_id);
                """))
            indexes_created.append("idx_subscription_plans_tenant")
        except Exception as e:
            print(f"Index idx_subscription_plans_tenant: {e}")
        
        # Index 2: tenant_id + is_active (for active plans query)
        try:
            if is_postgres:
                db.session.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_subscription_plans_tenant_active 
                    ON subscription_plans(tenant_id, is_active);
                """))
            else:  # SQLite
                db.session.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_subscription_plans_tenant_active 
                    ON subscription_plans(tenant_id, is_active);
                """))
            indexes_created.append("idx_subscription_plans_tenant_active")
        except Exception as e:
            print(f"Index idx_subscription_plans_tenant_active: {e}")
        
        
        # ============================================================
        # CUSTOMER SUBSCRIPTIONS INDEXES
        # ============================================================
        
        # Index 3: tenant_id
        try:
            if is_postgres:
                db.session.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_customer_subscriptions_tenant 
                    ON customer_subscriptions(tenant_id);
                """))
            else:
                db.session.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_customer_subscriptions_tenant 
                    ON customer_subscriptions(tenant_id);
                """))
            indexes_created.append("idx_customer_subscriptions_tenant")
        except Exception as e:
            print(f"Index idx_customer_subscriptions_tenant: {e}")
        
        # Index 4: customer_id (for looking up customer's subscriptions)
        try:
            if is_postgres:
                db.session.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_customer_subscriptions_customer 
                    ON customer_subscriptions(customer_id);
                """))
            else:
                db.session.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_customer_subscriptions_customer 
                    ON customer_subscriptions(customer_id);
                """))
            indexes_created.append("idx_customer_subscriptions_customer")
        except Exception as e:
            print(f"Index idx_customer_subscriptions_customer: {e}")
        
        # Index 5: plan_id (for plan analytics)
        try:
            if is_postgres:
                db.session.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_customer_subscriptions_plan 
                    ON customer_subscriptions(plan_id);
                """))
            else:
                db.session.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_customer_subscriptions_plan 
                    ON customer_subscriptions(plan_id);
                """))
            indexes_created.append("idx_customer_subscriptions_plan")
        except Exception as e:
            print(f"Index idx_customer_subscriptions_plan: {e}")
        
        # Index 6: tenant_id + status (critical for filtering active/pending/overdue)
        try:
            if is_postgres:
                db.session.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_customer_subscriptions_tenant_status 
                    ON customer_subscriptions(tenant_id, status);
                """))
            else:
                db.session.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_customer_subscriptions_tenant_status 
                    ON customer_subscriptions(tenant_id, status);
                """))
            indexes_created.append("idx_customer_subscriptions_tenant_status")
        except Exception as e:
            print(f"Index idx_customer_subscriptions_tenant_status: {e}")
        
        # Index 7: current_period_end (critical for due date queries)
        try:
            if is_postgres:
                db.session.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_customer_subscriptions_period_end 
                    ON customer_subscriptions(current_period_end);
                """))
            else:
                db.session.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_customer_subscriptions_period_end 
                    ON customer_subscriptions(current_period_end);
                """))
            indexes_created.append("idx_customer_subscriptions_period_end")
        except Exception as e:
            print(f"Index idx_customer_subscriptions_period_end: {e}")
        
        # Index 8: tenant_id + status + current_period_end (composite for "due soon" queries)
        try:
            if is_postgres:
                db.session.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_customer_subscriptions_due_soon 
                    ON customer_subscriptions(tenant_id, status, current_period_end);
                """))
            else:
                db.session.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_customer_subscriptions_due_soon 
                    ON customer_subscriptions(tenant_id, status, current_period_end);
                """))
            indexes_created.append("idx_customer_subscriptions_due_soon")
        except Exception as e:
            print(f"Index idx_customer_subscriptions_due_soon: {e}")
        
        
        # ============================================================
        # SUBSCRIPTION PAYMENTS INDEXES
        # ============================================================
        
        # Index 9: tenant_id
        try:
            if is_postgres:
                db.session.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_subscription_payments_tenant 
                    ON subscription_payments(tenant_id);
                """))
            else:
                db.session.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_subscription_payments_tenant 
                    ON subscription_payments(tenant_id);
                """))
            indexes_created.append("idx_subscription_payments_tenant")
        except Exception as e:
            print(f"Index idx_subscription_payments_tenant: {e}")
        
        # Index 10: subscription_id (for payment history lookup)
        try:
            if is_postgres:
                db.session.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_subscription_payments_subscription 
                    ON subscription_payments(subscription_id);
                """))
            else:
                db.session.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_subscription_payments_subscription 
                    ON subscription_payments(subscription_id);
                """))
            indexes_created.append("idx_subscription_payments_subscription")
        except Exception as e:
            print(f"Index idx_subscription_payments_subscription: {e}")
        
        # Index 11: payment_date (for date range reports)
        try:
            if is_postgres:
                db.session.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_subscription_payments_date 
                    ON subscription_payments(payment_date);
                """))
            else:
                db.session.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_subscription_payments_date 
                    ON subscription_payments(payment_date);
                """))
            indexes_created.append("idx_subscription_payments_date")
        except Exception as e:
            print(f"Index idx_subscription_payments_date: {e}")
        
        # Index 12: tenant_id + payment_date (for revenue reports)
        try:
            if is_postgres:
                db.session.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_subscription_payments_tenant_date 
                    ON subscription_payments(tenant_id, payment_date);
                """))
            else:
                db.session.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_subscription_payments_tenant_date 
                    ON subscription_payments(tenant_id, payment_date);
                """))
            indexes_created.append("idx_subscription_payments_tenant_date")
        except Exception as e:
            print(f"Index idx_subscription_payments_tenant_date: {e}")
        
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': f'✅ Created {len(indexes_created)} subscription indexes!',
            'database': 'PostgreSQL' if is_postgres else 'SQLite',
            'indexes_created': indexes_created,
            'performance_impact': {
                'subscription_plans': 'Faster plan listing and filtering',
                'customer_subscriptions': 'Much faster member lists, due date queries, status filtering',
                'subscription_payments': 'Faster payment history and revenue reports',
                'estimated_speedup': '5-10x faster for large datasets'
            },
            'next_steps': [
                '1. Go to /admin/subscriptions/plans (should be faster)',
                '2. Go to /admin/subscriptions/members (should load quickly)',
                '3. Go to /admin/subscriptions/reports (should be instant)',
                '4. Test filters and search (should be very fast)'
            ]
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'❌ Error creating indexes: {str(e)}'
        }), 500

