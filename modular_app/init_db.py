"""
Initialize database for multi-tenant system
Creates all tables including new Tenant model
"""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db

def init_database():
    """Initialize database with all tables"""
    with app.app_context():
        print("🗄️  Dropping existing tables...")
        db.drop_all()
        
        print("🔨 Creating new tables...")
        db.create_all()
        
        print("✅ Database initialized successfully!")
        print("\nTables created:")
        print("  - tenants")
        print("  - employees")
        print("  - sites")
        print("  - attendance")
        print("  - materials")
        print("  - stocks")
        print("  - stock_movements")
        print("  - transfers")
        print("\n📝 Note: All old data has been cleared.")
        print("   You can now register tenants at: /register/")

if __name__ == '__main__':
    init_database()

