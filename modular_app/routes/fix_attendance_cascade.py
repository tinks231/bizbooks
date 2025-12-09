"""
Fix attendance CASCADE delete issue
Allows tenant deletion to work without foreign key violations
"""
from flask import Blueprint, jsonify
from sqlalchemy import text
from models import db

fix_cascade_bp = Blueprint('fix_cascade', __name__)

@fix_cascade_bp.route('/fix-attendance-cascade', methods=['GET', 'POST'])
def fix_attendance_cascade():
    """
    Fix attendance foreign keys to CASCADE on delete
    Prevents "employee_id cannot be null" error when deleting tenants
    """
    try:
        with db.engine.begin() as conn:
            
            # Fix employee_id foreign key
            print("Fixing attendance.employee_id foreign key...")
            conn.execute(text("""
                ALTER TABLE attendance 
                DROP CONSTRAINT IF EXISTS attendance_employee_id_fkey;
            """))
            
            conn.execute(text("""
                ALTER TABLE attendance 
                ADD CONSTRAINT attendance_employee_id_fkey 
                FOREIGN KEY (employee_id) 
                REFERENCES employees(id) 
                ON DELETE CASCADE;
            """))
            
            # Fix site_id foreign key
            print("Fixing attendance.site_id foreign key...")
            conn.execute(text("""
                ALTER TABLE attendance 
                DROP CONSTRAINT IF EXISTS attendance_site_id_fkey;
            """))
            
            conn.execute(text("""
                ALTER TABLE attendance 
                ADD CONSTRAINT attendance_site_id_fkey 
                FOREIGN KEY (site_id) 
                REFERENCES sites(id) 
                ON DELETE CASCADE;
            """))
            
            # Fix loyalty_programs foreign key (if table exists)
            print("Fixing loyalty_programs.tenant_id foreign key...")
            conn.execute(text("""
                DO $$ 
                BEGIN
                    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'loyalty_programs') THEN
                        ALTER TABLE loyalty_programs 
                        DROP CONSTRAINT IF EXISTS loyalty_programs_tenant_id_fkey;
                        
                        ALTER TABLE loyalty_programs 
                        ADD CONSTRAINT loyalty_programs_tenant_id_fkey 
                        FOREIGN KEY (tenant_id) 
                        REFERENCES tenants(id) 
                        ON DELETE CASCADE;
                    END IF;
                END $$;
            """))
            
            # Fix customer_loyalty_points foreign key (if table exists)
            print("Fixing customer_loyalty_points.tenant_id foreign key...")
            conn.execute(text("""
                DO $$ 
                BEGIN
                    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'customer_loyalty_points') THEN
                        ALTER TABLE customer_loyalty_points 
                        DROP CONSTRAINT IF EXISTS customer_loyalty_points_tenant_id_fkey;
                        
                        ALTER TABLE customer_loyalty_points 
                        ADD CONSTRAINT customer_loyalty_points_tenant_id_fkey 
                        FOREIGN KEY (tenant_id) 
                        REFERENCES tenants(id) 
                        ON DELETE CASCADE;
                    END IF;
                END $$;
            """))
            
            # Fix loyalty_transactions foreign key (if table exists)
            print("Fixing loyalty_transactions.tenant_id foreign key...")
            conn.execute(text("""
                DO $$ 
                BEGIN
                    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'loyalty_transactions') THEN
                        ALTER TABLE loyalty_transactions 
                        DROP CONSTRAINT IF EXISTS loyalty_transactions_tenant_id_fkey;
                        
                        ALTER TABLE loyalty_transactions 
                        ADD CONSTRAINT loyalty_transactions_tenant_id_fkey 
                        FOREIGN KEY (tenant_id) 
                        REFERENCES tenants(id) 
                        ON DELETE CASCADE;
                    END IF;
                END $$;
            """))
            
        return jsonify({
            "status": "success",
            "message": "✅ All CASCADE constraints fixed!",
            "details": {
                "fixed_constraints": [
                    "attendance.employee_id → ON DELETE CASCADE",
                    "attendance.site_id → ON DELETE CASCADE",
                    "loyalty_programs.tenant_id → ON DELETE CASCADE",
                    "customer_loyalty_points.tenant_id → ON DELETE CASCADE",
                    "loyalty_transactions.tenant_id → ON DELETE CASCADE"
                ],
                "note": "Tenant deletion will now work properly. All related records will cascade delete."
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": f"❌ Fix failed: {str(e)}"
        }), 500

