"""
Migration: Add Special Day Bonus Columns
Adds is_temporary and expires_at columns to loyalty_transactions table
"""

from flask import Blueprint, jsonify
from models import db
from sqlalchemy import text

add_special_day_columns_bp = Blueprint('add_special_day_columns', __name__)

@add_special_day_columns_bp.route('/migrate/add-special-day-bonus-columns', methods=['GET'])
def run_migration():
    """
    Add columns to loyalty_transactions table for birthday/anniversary bonuses:
    - is_temporary: Boolean flag for temporary points
    - expires_at: Datetime when temporary points expire
    """
    
    try:
        print("🔧 Starting migration: Add special day bonus columns...")
        
        # Add is_temporary column
        try:
            db.session.execute(text("""
                ALTER TABLE loyalty_transactions 
                ADD COLUMN IF NOT EXISTS is_temporary BOOLEAN DEFAULT FALSE
            """))
            print("✅ Added is_temporary column")
        except Exception as e:
            print(f"⚠️  is_temporary column might already exist: {e}")
        
        # Add expires_at column
        try:
            db.session.execute(text("""
                ALTER TABLE loyalty_transactions 
                ADD COLUMN IF NOT EXISTS expires_at TIMESTAMP
            """))
            print("✅ Added expires_at column")
        except Exception as e:
            print(f"⚠️  expires_at column might already exist: {e}")
        
        # Commit changes
        db.session.commit()
        
        print("✅ Migration completed successfully!")
        
        return jsonify({
            'success': True,
            'message': 'Special day bonus columns added successfully',
            'columns_added': ['is_temporary', 'expires_at']
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'error': 'Migration failed',
            'message': str(e)
        }), 500

