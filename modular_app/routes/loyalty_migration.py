"""
Loyalty Program Migration - Phase 1
Creates tables for loyalty program functionality
"""
from flask import Blueprint, jsonify, g
from sqlalchemy import text
from models import db
from datetime import datetime

loyalty_migration_bp = Blueprint('loyalty_migration', __name__)

@loyalty_migration_bp.route('/run-loyalty-migration', methods=['GET', 'POST'])
def run_loyalty_migration():
    """
    Migration to add loyalty program tables and update existing tables
    Phase 1: Core loyalty features
    """
    try:
        with db.engine.begin() as conn:
            
            # ============================================
            # TABLE 1: loyalty_programs
            # ============================================
            print("Creating loyalty_programs table...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS loyalty_programs (
                    id SERIAL PRIMARY KEY,
                    tenant_id INTEGER NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
                    
                    -- Basic Settings
                    program_name VARCHAR(100) DEFAULT 'Loyalty Program',
                    is_active BOOLEAN DEFAULT false,
                    
                    -- Earning Rules
                    points_per_100_rupees NUMERIC(5,2) DEFAULT 1.00,
                    minimum_purchase_for_points NUMERIC(10,2) DEFAULT 0,
                    maximum_points_per_invoice INTEGER,
                    
                    -- Threshold Bonuses
                    enable_threshold_bonuses BOOLEAN DEFAULT false,
                    threshold_1_amount NUMERIC(10,2),
                    threshold_1_bonus_points INTEGER,
                    threshold_2_amount NUMERIC(10,2),
                    threshold_2_bonus_points INTEGER,
                    threshold_3_amount NUMERIC(10,2),
                    threshold_3_bonus_points INTEGER,
                    
                    -- Redemption Rules
                    points_to_rupees_ratio NUMERIC(5,2) DEFAULT 1.00,
                    minimum_points_to_redeem INTEGER DEFAULT 10,
                    maximum_discount_percent NUMERIC(5,2),
                    maximum_points_per_redemption INTEGER,
                    
                    -- Display
                    show_points_on_invoice BOOLEAN DEFAULT true,
                    invoice_footer_text VARCHAR(255) DEFAULT 'Points Balance: {balance} pts | Next visit: ₹{value} off!',
                    
                    -- Timestamps
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    
                    UNIQUE(tenant_id)
                );
            """))
            
            # ============================================
            # TABLE 2: customer_loyalty_points
            # ============================================
            print("Creating customer_loyalty_points table...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS customer_loyalty_points (
                    id SERIAL PRIMARY KEY,
                    tenant_id INTEGER NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
                    customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
                    
                    -- Points Balance
                    current_points INTEGER DEFAULT 0,
                    lifetime_earned_points INTEGER DEFAULT 0,
                    lifetime_redeemed_points INTEGER DEFAULT 0,
                    
                    -- For Phase 2: Tier tracking
                    tier_level VARCHAR(20) DEFAULT 'bronze',
                    tier_updated_at TIMESTAMP,
                    
                    -- Timestamps
                    last_earned_at TIMESTAMP,
                    last_redeemed_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    
                    UNIQUE(tenant_id, customer_id)
                );
            """))
            
            print("Creating index on customer_loyalty_points...")
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_loyalty_points_customer 
                ON customer_loyalty_points(tenant_id, customer_id);
            """))
            
            # ============================================
            # TABLE 3: loyalty_transactions
            # ============================================
            print("Creating loyalty_transactions table...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS loyalty_transactions (
                    id SERIAL PRIMARY KEY,
                    tenant_id INTEGER NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
                    customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
                    
                    -- Transaction Type
                    transaction_type VARCHAR(20) NOT NULL,
                    
                    -- Points
                    points INTEGER NOT NULL,
                    points_before INTEGER,
                    points_after INTEGER,
                    
                    -- Reference
                    invoice_id INTEGER REFERENCES invoices(id) ON DELETE SET NULL,
                    invoice_number VARCHAR(50),
                    description TEXT,
                    
                    -- Details
                    base_points INTEGER,
                    bonus_points INTEGER,
                    invoice_amount NUMERIC(10,2),
                    
                    -- Metadata
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_by INTEGER REFERENCES users(id)
                );
            """))
            
            print("Creating indexes on loyalty_transactions...")
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_loyalty_transactions_customer 
                ON loyalty_transactions(tenant_id, customer_id, created_at DESC);
            """))
            
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_loyalty_transactions_invoice 
                ON loyalty_transactions(invoice_id);
            """))
            
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_loyalty_transactions_type 
                ON loyalty_transactions(tenant_id, transaction_type);
            """))
            
            # ============================================
            # UPDATE: customers table
            # ============================================
            print("Adding DOB and anniversary fields to customers...")
            conn.execute(text("""
                ALTER TABLE customers 
                ADD COLUMN IF NOT EXISTS date_of_birth DATE;
            """))
            
            conn.execute(text("""
                ALTER TABLE customers 
                ADD COLUMN IF NOT EXISTS anniversary_date DATE;
            """))
            
            # ============================================
            # UPDATE: invoices table
            # ============================================
            print("Adding loyalty fields to invoices...")
            conn.execute(text("""
                ALTER TABLE invoices 
                ADD COLUMN IF NOT EXISTS loyalty_discount NUMERIC(10,2) DEFAULT 0;
            """))
            
            conn.execute(text("""
                ALTER TABLE invoices 
                ADD COLUMN IF NOT EXISTS loyalty_points_redeemed INTEGER DEFAULT 0;
            """))
            
            conn.execute(text("""
                ALTER TABLE invoices 
                ADD COLUMN IF NOT EXISTS loyalty_points_earned INTEGER DEFAULT 0;
            """))
            
            print("Creating indexes on invoices...")
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_invoices_loyalty 
                ON invoices(tenant_id, loyalty_discount) 
                WHERE loyalty_discount > 0;
            """))
            
            # ============================================
            # Create default loyalty program for existing tenants (disabled)
            # ============================================
            print("Creating default loyalty programs for existing tenants...")
            conn.execute(text("""
                INSERT INTO loyalty_programs (
                    tenant_id,
                    program_name,
                    is_active,
                    points_per_100_rupees,
                    minimum_purchase_for_points,
                    enable_threshold_bonuses,
                    threshold_1_amount,
                    threshold_1_bonus_points,
                    threshold_2_amount,
                    threshold_2_bonus_points,
                    points_to_rupees_ratio,
                    minimum_points_to_redeem,
                    show_points_on_invoice
                )
                SELECT 
                    id as tenant_id,
                    'Loyalty Program' as program_name,
                    false as is_active,
                    1.00 as points_per_100_rupees,
                    0 as minimum_purchase_for_points,
                    false as enable_threshold_bonuses,
                    5000 as threshold_1_amount,
                    50 as threshold_1_bonus_points,
                    10000 as threshold_2_amount,
                    200 as threshold_2_bonus_points,
                    1.00 as points_to_rupees_ratio,
                    10 as minimum_points_to_redeem,
                    true as show_points_on_invoice
                FROM tenants
                WHERE id NOT IN (SELECT tenant_id FROM loyalty_programs)
                ON CONFLICT (tenant_id) DO NOTHING;
            """))
            
        return jsonify({
            "status": "success",
            "message": "✅ Loyalty program migration completed successfully!",
            "details": {
                "tables_created": [
                    "loyalty_programs",
                    "customer_loyalty_points",
                    "loyalty_transactions"
                ],
                "tables_updated": [
                    "customers (added date_of_birth, anniversary_date)",
                    "invoices (added loyalty_discount, loyalty_points_redeemed, loyalty_points_earned)"
                ],
                "indexes_created": 5,
                "note": "Loyalty program is OFF by default for all tenants. Enable in settings."
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": f"❌ Migration failed: {str(e)}"
        }), 500

