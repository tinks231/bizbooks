"""
Fix attendance foreign key to CASCADE on delete
This allows tenant deletion to work properly
"""
from flask import Flask
from models import db
from sqlalchemy import text

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://YOUR_DB_CONNECTION_STRING'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    with db.engine.begin() as conn:
        print("Fixing attendance.employee_id foreign key constraint...")
        
        # 1. Drop the existing foreign key constraint
        print("Step 1: Dropping old foreign key constraint...")
        conn.execute(text("""
            ALTER TABLE attendance 
            DROP CONSTRAINT IF EXISTS attendance_employee_id_fkey;
        """))
        
        # 2. Add new foreign key with CASCADE
        print("Step 2: Adding new foreign key with ON DELETE CASCADE...")
        conn.execute(text("""
            ALTER TABLE attendance 
            ADD CONSTRAINT attendance_employee_id_fkey 
            FOREIGN KEY (employee_id) 
            REFERENCES employees(id) 
            ON DELETE CASCADE;
        """))
        
        # 3. Fix site_id foreign key too (if it has the same issue)
        print("Step 3: Fixing site_id foreign key...")
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
        
        print("✅ Fixed! Attendance records will now CASCADE delete with employees/sites.")

print("\n🎉 Migration complete! Try deleting the tenant again.")

