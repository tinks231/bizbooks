"""
Migration: Add Special Day Bonus Columns
Adds is_temporary and expires_at columns to loyalty_transactions table
"""

from flask import Blueprint, jsonify
import traceback as tb

add_special_day_columns_bp = Blueprint('add_special_day_columns', __name__)

@add_special_day_columns_bp.route('/migrate/add-special-day-bonus-columns', methods=['GET'])
def run_migration():
    """
    Add columns to loyalty_transactions table for birthday/anniversary bonuses:
    - is_temporary: Boolean flag for temporary points
    - expires_at: Datetime when temporary points expire
    """
    
    try:
        # Import here to avoid circular imports at module load time
        from models import db
        from sqlalchemy import text
        
        print("🔧 Starting migration: Add special day bonus columns...")
        
        results = {
            'is_temporary': 'pending',
            'expires_at': 'pending',
            'errors': []
        }
        
        # Add is_temporary column
        try:
            db.session.execute(text("""
                ALTER TABLE loyalty_transactions 
                ADD COLUMN IF NOT EXISTS is_temporary BOOLEAN DEFAULT FALSE
            """))
            db.session.commit()
            results['is_temporary'] = 'added'
            print("✅ Added is_temporary column")
        except Exception as e:
            error_msg = str(e)
            if 'already exists' in error_msg.lower() or 'duplicate column' in error_msg.lower():
                results['is_temporary'] = 'already_exists'
                print(f"⚠️  is_temporary column already exists")
            else:
                results['is_temporary'] = f'error: {error_msg}'
                results['errors'].append(f"is_temporary: {error_msg}")
                print(f"❌ Error adding is_temporary: {e}")
            db.session.rollback()
        
        # Add expires_at column
        try:
            db.session.execute(text("""
                ALTER TABLE loyalty_transactions 
                ADD COLUMN IF NOT EXISTS expires_at TIMESTAMP
            """))
            db.session.commit()
            results['expires_at'] = 'added'
            print("✅ Added expires_at column")
        except Exception as e:
            error_msg = str(e)
            if 'already exists' in error_msg.lower() or 'duplicate column' in error_msg.lower():
                results['expires_at'] = 'already_exists'
                print(f"⚠️  expires_at column already exists")
            else:
                results['expires_at'] = f'error: {error_msg}'
                results['errors'].append(f"expires_at: {error_msg}")
                print(f"❌ Error adding expires_at: {e}")
            db.session.rollback()
        
        print("✅ Migration completed!")
        
        success = (results['is_temporary'] in ['added', 'already_exists'] and 
                   results['expires_at'] in ['added', 'already_exists'])
        
        return jsonify({
            'success': success,
            'message': 'Migration completed' if success else 'Migration completed with errors',
            'results': results
        }), 200 if success else 500
        
    except Exception as e:
        print(f"❌ Migration crashed: {str(e)}")
        tb.print_exc()
        
        return jsonify({
            'error': 'Migration crashed',
            'message': str(e),
            'traceback': tb.format_exc()
        }), 500

