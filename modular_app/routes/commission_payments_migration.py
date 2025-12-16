"""
Migration: Create commission_payments table and migrate existing paid commissions
This enables partial payments and better tracking of commission payments
"""
from flask import Blueprint, jsonify, g, session, redirect, url_for, flash
from models.database import db
from utils.tenant_middleware import require_tenant, get_current_tenant_id
from functools import wraps
from sqlalchemy import text

commission_payments_migration_bp = Blueprint('commission_payments_migration', __name__, url_prefix='/migration')

def login_required(f):
    """Decorator to require admin login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'tenant_admin_id' not in session:
            flash('Please login first', 'error')
            return redirect(url_for('admin.login'))
        # Verify session tenant matches current tenant
        if session.get('tenant_admin_id') != get_current_tenant_id():
            session.clear()
            flash('Session mismatch. Please login again.', 'error')
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function

@commission_payments_migration_bp.route('/create-commission-payments-table', methods=['GET'])
@require_tenant
@login_required
def create_commission_payments_table():
    """Create commission_payments table to track individual payment transactions"""
    try:
        tenant_id = g.tenant.id
        
        # Step 1: Create commission_payments table
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS commission_payments (
                id SERIAL PRIMARY KEY,
                tenant_id INTEGER NOT NULL,
                agent_id INTEGER NOT NULL,
                payment_date DATE NOT NULL,
                amount NUMERIC(10,2) NOT NULL,
                account_id INTEGER NOT NULL,
                payment_method VARCHAR(50),
                voucher_number VARCHAR(50),
                payment_notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by INTEGER,
                
                CONSTRAINT fk_commission_payment_tenant 
                    FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE,
                CONSTRAINT fk_commission_payment_agent 
                    FOREIGN KEY (agent_id) REFERENCES commission_agents(id) ON DELETE CASCADE,
                CONSTRAINT fk_commission_payment_account 
                    FOREIGN KEY (account_id) REFERENCES bank_accounts(id) ON DELETE RESTRICT
            );
            
            CREATE INDEX IF NOT EXISTS idx_commission_payments_tenant 
                ON commission_payments(tenant_id);
            CREATE INDEX IF NOT EXISTS idx_commission_payments_agent 
                ON commission_payments(tenant_id, agent_id);
            CREATE INDEX IF NOT EXISTS idx_commission_payments_date 
                ON commission_payments(tenant_id, payment_date);
        """))
        
        db.session.commit()
        
        print("✅ Created commission_payments table with indexes")
        
        # Step 2: Migrate existing paid commissions
        # Find all paid commissions for this tenant
        result = db.session.execute(text("""
            SELECT 
                ic.id,
                ic.tenant_id,
                ic.agent_id,
                ic.commission_amount,
                ic.paid_date,
                ic.invoice_id,
                i.invoice_number,
                at.account_id,
                at.transaction_type
            FROM invoice_commissions ic
            JOIN invoices i ON ic.invoice_id = i.id
            LEFT JOIN account_transactions at ON (
                at.reference_type = 'commission_payment' 
                AND at.reference_id = ic.id
                AND at.transaction_type IN ('commission_expense')
                AND at.tenant_id = :tenant_id
            )
            WHERE ic.tenant_id = :tenant_id
            AND ic.is_paid = TRUE
            AND ic.paid_date IS NOT NULL
            ORDER BY ic.paid_date ASC
        """), {'tenant_id': tenant_id})
        
        paid_commissions = result.fetchall()
        migrated_count = 0
        
        for comm in paid_commissions:
            # Check if already migrated
            exists = db.session.execute(text("""
                SELECT id FROM commission_payments
                WHERE tenant_id = :tenant_id
                AND agent_id = :agent_id
                AND payment_date = :payment_date
                AND amount = :amount
                AND voucher_number = :voucher
            """), {
                'tenant_id': comm.tenant_id,
                'agent_id': comm.agent_id,
                'payment_date': comm.paid_date,
                'amount': float(comm.commission_amount),
                'voucher': f'COMM-{comm.id}'
            }).fetchone()
            
            if exists:
                print(f"⏭️  Skipping COMM-{comm.id} (already migrated)")
                continue
            
            # Determine payment method from account_id
            payment_method = 'cash'
            account_id = comm.account_id
            
            if not account_id:
                # Try to find a default cash account
                default_account = db.session.execute(text("""
                    SELECT id FROM bank_accounts
                    WHERE tenant_id = :tenant_id
                    AND account_type = 'cash'
                    AND is_active = TRUE
                    ORDER BY id ASC
                    LIMIT 1
                """), {'tenant_id': tenant_id}).fetchone()
                
                if default_account:
                    account_id = default_account.id
                else:
                    print(f"⚠️  Warning: No cash account found for COMM-{comm.id}, skipping")
                    continue
            
            # Get account details
            account_info = db.session.execute(text("""
                SELECT account_type, account_name
                FROM bank_accounts
                WHERE id = :account_id
            """), {'account_id': account_id}).fetchone()
            
            if account_info:
                payment_method = account_info.account_type
            
            # Insert into commission_payments
            db.session.execute(text("""
                INSERT INTO commission_payments
                (tenant_id, agent_id, payment_date, amount, account_id, 
                 payment_method, voucher_number, payment_notes, created_at)
                VALUES
                (:tenant_id, :agent_id, :payment_date, :amount, :account_id,
                 :payment_method, :voucher_number, :notes, :created_at)
            """), {
                'tenant_id': comm.tenant_id,
                'agent_id': comm.agent_id,
                'payment_date': comm.paid_date,
                'amount': float(comm.commission_amount),
                'account_id': account_id,
                'payment_method': payment_method,
                'voucher_number': f'COMM-{comm.id}',
                'notes': f'Migrated from invoice #{comm.invoice_number}',
                'created_at': comm.paid_date
            })
            
            migrated_count += 1
            print(f"✅ Migrated COMM-{comm.id}: ₹{comm.commission_amount} paid on {comm.paid_date}")
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': f'Created commission_payments table and migrated {migrated_count} existing payments',
            'table_created': True,
            'payments_migrated': migrated_count,
            'total_paid_commissions': len(paid_commissions)
        })
        
    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': str(e),
            'traceback': traceback.format_exc()
        }), 500

