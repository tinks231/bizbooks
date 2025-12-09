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
            
        return jsonify({
            "status": "success",
            "message": "✅ Attendance CASCADE constraints fixed!",
            "details": {
                "fixed_constraints": [
                    "attendance.employee_id → ON DELETE CASCADE",
                    "attendance.site_id → ON DELETE CASCADE"
                ],
                "note": "Tenant deletion will now work properly. Attendance records will be deleted when employees/sites are deleted."
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": f"❌ Fix failed: {str(e)}"
        }), 500

