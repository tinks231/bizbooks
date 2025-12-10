"""
Loyalty Program Features Migration
Adds birthday/anniversary bonuses and membership tiers to loyalty programs
"""
from flask import Blueprint, jsonify, g
from models.database import db
from sqlalchemy import text, inspect
import logging

logger = logging.getLogger(__name__)

loyalty_features_bp = Blueprint('loyalty_features_migration', __name__, url_prefix='/migration/loyalty-features')

@loyalty_features_bp.route('/run')
def run_migration():
    """Add birthday/anniversary bonuses and membership tiers columns to loyalty_programs table"""
    
    try:
        # Check current database engine
        inspector = inspect(db.engine)
        
        # PostgreSQL / Supabase
        if db.engine.dialect.name == 'postgresql':
            logger.info("Running loyalty features migration for PostgreSQL...")
            
            # Get existing columns
            existing_columns = [col['name'] for col in inspector.get_columns('loyalty_programs')]
            
            columns_to_add = []
            
            # Birthday/Anniversary bonus columns (in POINTS, not rupees!)
            if 'enable_birthday_bonus' not in existing_columns:
                columns_to_add.append("ALTER TABLE loyalty_programs ADD COLUMN enable_birthday_bonus BOOLEAN DEFAULT false;")
            if 'birthday_bonus_points' not in existing_columns:
                columns_to_add.append("ALTER TABLE loyalty_programs ADD COLUMN birthday_bonus_points INTEGER DEFAULT 0;")
            if 'enable_anniversary_bonus' not in existing_columns:
                columns_to_add.append("ALTER TABLE loyalty_programs ADD COLUMN enable_anniversary_bonus BOOLEAN DEFAULT false;")
            if 'anniversary_bonus_points' not in existing_columns:
                columns_to_add.append("ALTER TABLE loyalty_programs ADD COLUMN anniversary_bonus_points INTEGER DEFAULT 0;")
            
            # Membership tier columns
            if 'enable_membership_tiers' not in existing_columns:
                columns_to_add.append("ALTER TABLE loyalty_programs ADD COLUMN enable_membership_tiers BOOLEAN DEFAULT false;")
            if 'tier_bronze_name' not in existing_columns:
                columns_to_add.append("ALTER TABLE loyalty_programs ADD COLUMN tier_bronze_name VARCHAR(50) DEFAULT 'Bronze';")
            if 'tier_bronze_min_points' not in existing_columns:
                columns_to_add.append("ALTER TABLE loyalty_programs ADD COLUMN tier_bronze_min_points INTEGER DEFAULT 0;")
            if 'tier_silver_name' not in existing_columns:
                columns_to_add.append("ALTER TABLE loyalty_programs ADD COLUMN tier_silver_name VARCHAR(50) DEFAULT 'Silver';")
            if 'tier_silver_min_points' not in existing_columns:
                columns_to_add.append("ALTER TABLE loyalty_programs ADD COLUMN tier_silver_min_points INTEGER DEFAULT 1000;")
            if 'tier_gold_name' not in existing_columns:
                columns_to_add.append("ALTER TABLE loyalty_programs ADD COLUMN tier_gold_name VARCHAR(50) DEFAULT 'Gold';")
            if 'tier_gold_min_points' not in existing_columns:
                columns_to_add.append("ALTER TABLE loyalty_programs ADD COLUMN tier_gold_min_points INTEGER DEFAULT 5000;")
            if 'tier_platinum_name' not in existing_columns:
                columns_to_add.append("ALTER TABLE loyalty_programs ADD COLUMN tier_platinum_name VARCHAR(50) DEFAULT 'Platinum';")
            if 'tier_platinum_min_points' not in existing_columns:
                columns_to_add.append("ALTER TABLE loyalty_programs ADD COLUMN tier_platinum_min_points INTEGER DEFAULT 10000;")
            
            if columns_to_add:
                for sql in columns_to_add:
                    db.session.execute(text(sql))
                db.session.commit()
                logger.info(f"✅ Added {len(columns_to_add)} columns to loyalty_programs")
                return jsonify({
                    'success': True,
                    'message': f'✅ Loyalty features migration completed! Added {len(columns_to_add)} columns.',
                    'details': {
                        'columns_added': len(columns_to_add),
                        'features': ['Birthday/Anniversary Bonuses', 'Membership Tiers']
                    }
                })
            else:
                logger.info("All columns already exist")
                return jsonify({
                    'success': True,
                    'message': 'ℹ️ Loyalty features already migrated',
                    'details': 'No action needed - all columns exist'
                })
        
        # SQLite (local development)
        elif db.engine.dialect.name == 'sqlite':
            logger.info("Running loyalty features migration for SQLite...")
            
            # For SQLite, we'll use a simpler approach - check if column exists
            try:
                # Try to select one of the new columns
                db.session.execute(text("SELECT enable_birthday_bonus FROM loyalty_programs LIMIT 1")).fetchone()
                # If we get here, columns already exist
                logger.info("All columns already exist")
                return jsonify({
                    'success': True,
                    'message': 'ℹ️ Loyalty features already migrated',
                    'details': 'No action needed - all columns exist'
                })
            except:
                # Columns don't exist, add them
                columns_to_add = [
                    "ALTER TABLE loyalty_programs ADD COLUMN enable_birthday_bonus BOOLEAN DEFAULT 0;",
                    "ALTER TABLE loyalty_programs ADD COLUMN birthday_bonus_points INTEGER DEFAULT 0;",
                    "ALTER TABLE loyalty_programs ADD COLUMN enable_anniversary_bonus BOOLEAN DEFAULT 0;",
                    "ALTER TABLE loyalty_programs ADD COLUMN anniversary_bonus_points INTEGER DEFAULT 0;",
                    "ALTER TABLE loyalty_programs ADD COLUMN enable_membership_tiers BOOLEAN DEFAULT 0;",
                    "ALTER TABLE loyalty_programs ADD COLUMN tier_bronze_name VARCHAR(50) DEFAULT 'Bronze';",
                    "ALTER TABLE loyalty_programs ADD COLUMN tier_bronze_min_points INTEGER DEFAULT 0;",
                    "ALTER TABLE loyalty_programs ADD COLUMN tier_silver_name VARCHAR(50) DEFAULT 'Silver';",
                    "ALTER TABLE loyalty_programs ADD COLUMN tier_silver_min_points INTEGER DEFAULT 1000;",
                    "ALTER TABLE loyalty_programs ADD COLUMN tier_gold_name VARCHAR(50) DEFAULT 'Gold';",
                    "ALTER TABLE loyalty_programs ADD COLUMN tier_gold_min_points INTEGER DEFAULT 5000;",
                    "ALTER TABLE loyalty_programs ADD COLUMN tier_platinum_name VARCHAR(50) DEFAULT 'Platinum';",
                    "ALTER TABLE loyalty_programs ADD COLUMN tier_platinum_min_points INTEGER DEFAULT 10000;"
                ]
                
                for sql in columns_to_add:
                    try:
                        db.session.execute(text(sql))
                    except:
                        pass  # Column might already exist
                
                db.session.commit()
                logger.info("✅ Added columns to loyalty_programs")
                return jsonify({
                    'success': True,
                    'message': '✅ Loyalty features migration completed!',
                    'details': {
                        'columns_added': len(columns_to_add),
                        'features': ['Birthday/Anniversary Bonuses', 'Membership Tiers']
                    }
                })
        
        else:
            return jsonify({
                'success': False,
                'message': f'⚠️ Unsupported database: {db.engine.dialect.name}'
            }), 400
        
    except Exception as e:
        db.session.rollback()
        error_msg = f"Loyalty features migration failed: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return jsonify({
            'success': False,
            'message': f'❌ {error_msg}'
        }), 500

