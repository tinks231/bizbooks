"""
Tier Benefits Migration
Adds earning/redemption multipliers and max discount overrides for each membership tier
"""
from flask import Blueprint, jsonify
from models.database import db
from sqlalchemy import text, inspect
import logging

logger = logging.getLogger(__name__)

tier_benefits_bp = Blueprint('tier_benefits_migration', __name__, url_prefix='/migration/tier-benefits')

@tier_benefits_bp.route('/run')
def run_migration():
    """Add tier benefit columns (earning/redemption multipliers) to loyalty_programs table"""
    
    try:
        # Check current database engine
        inspector = inspect(db.engine)
        
        # PostgreSQL / Supabase
        if db.engine.dialect.name == 'postgresql':
            logger.info("Running tier benefits migration for PostgreSQL...")
            
            # Get existing columns
            existing_columns = [col['name'] for col in inspector.get_columns('loyalty_programs')]
            
            columns_to_add = []
            
            # Bronze tier benefits
            if 'tier_bronze_earning_multiplier' not in existing_columns:
                columns_to_add.append("ALTER TABLE loyalty_programs ADD COLUMN tier_bronze_earning_multiplier NUMERIC(5, 2) DEFAULT 1.0;")
            if 'tier_bronze_redemption_multiplier' not in existing_columns:
                columns_to_add.append("ALTER TABLE loyalty_programs ADD COLUMN tier_bronze_redemption_multiplier NUMERIC(5, 2) DEFAULT 1.0;")
            if 'tier_bronze_max_discount_percent' not in existing_columns:
                columns_to_add.append("ALTER TABLE loyalty_programs ADD COLUMN tier_bronze_max_discount_percent NUMERIC(5, 2);")
            
            # Silver tier benefits
            if 'tier_silver_earning_multiplier' not in existing_columns:
                columns_to_add.append("ALTER TABLE loyalty_programs ADD COLUMN tier_silver_earning_multiplier NUMERIC(5, 2) DEFAULT 1.2;")
            if 'tier_silver_redemption_multiplier' not in existing_columns:
                columns_to_add.append("ALTER TABLE loyalty_programs ADD COLUMN tier_silver_redemption_multiplier NUMERIC(5, 2) DEFAULT 1.1;")
            if 'tier_silver_max_discount_percent' not in existing_columns:
                columns_to_add.append("ALTER TABLE loyalty_programs ADD COLUMN tier_silver_max_discount_percent NUMERIC(5, 2);")
            
            # Gold tier benefits
            if 'tier_gold_earning_multiplier' not in existing_columns:
                columns_to_add.append("ALTER TABLE loyalty_programs ADD COLUMN tier_gold_earning_multiplier NUMERIC(5, 2) DEFAULT 1.5;")
            if 'tier_gold_redemption_multiplier' not in existing_columns:
                columns_to_add.append("ALTER TABLE loyalty_programs ADD COLUMN tier_gold_redemption_multiplier NUMERIC(5, 2) DEFAULT 1.25;")
            if 'tier_gold_max_discount_percent' not in existing_columns:
                columns_to_add.append("ALTER TABLE loyalty_programs ADD COLUMN tier_gold_max_discount_percent NUMERIC(5, 2);")
            
            # Platinum tier benefits
            if 'tier_platinum_earning_multiplier' not in existing_columns:
                columns_to_add.append("ALTER TABLE loyalty_programs ADD COLUMN tier_platinum_earning_multiplier NUMERIC(5, 2) DEFAULT 2.0;")
            if 'tier_platinum_redemption_multiplier' not in existing_columns:
                columns_to_add.append("ALTER TABLE loyalty_programs ADD COLUMN tier_platinum_redemption_multiplier NUMERIC(5, 2) DEFAULT 1.5;")
            if 'tier_platinum_max_discount_percent' not in existing_columns:
                columns_to_add.append("ALTER TABLE loyalty_programs ADD COLUMN tier_platinum_max_discount_percent NUMERIC(5, 2);")
            
            if columns_to_add:
                for sql in columns_to_add:
                    db.session.execute(text(sql))
                db.session.commit()
                logger.info(f"✅ Added {len(columns_to_add)} tier benefit columns")
                return jsonify({
                    'success': True,
                    'message': f'✅ Tier benefits migration completed! Added {len(columns_to_add)} columns.',
                    'details': {
                        'columns_added': len(columns_to_add),
                        'features': [
                            'Earning multipliers per tier (Bronze 1.0x, Silver 1.2x, Gold 1.5x, Platinum 2.0x)',
                            'Redemption multipliers per tier (better value for higher tiers)',
                            'Max discount % override per tier (optional)'
                        ]
                    }
                })
            else:
                logger.info("All tier benefit columns already exist")
                return jsonify({
                    'success': True,
                    'message': 'ℹ️ Tier benefits already migrated',
                    'details': 'No action needed - all columns exist'
                })
        
        # SQLite (local development)
        elif db.engine.dialect.name == 'sqlite':
            logger.info("Running tier benefits migration for SQLite...")
            
            # For SQLite, try to check if columns exist
            try:
                db.session.execute(text("SELECT tier_bronze_earning_multiplier FROM loyalty_programs LIMIT 1")).fetchone()
                logger.info("All tier benefit columns already exist")
                return jsonify({
                    'success': True,
                    'message': 'ℹ️ Tier benefits already migrated',
                    'details': 'No action needed - all columns exist'
                })
            except:
                # Columns don't exist, add them
                columns_to_add = [
                    "ALTER TABLE loyalty_programs ADD COLUMN tier_bronze_earning_multiplier NUMERIC(5, 2) DEFAULT 1.0;",
                    "ALTER TABLE loyalty_programs ADD COLUMN tier_bronze_redemption_multiplier NUMERIC(5, 2) DEFAULT 1.0;",
                    "ALTER TABLE loyalty_programs ADD COLUMN tier_bronze_max_discount_percent NUMERIC(5, 2);",
                    "ALTER TABLE loyalty_programs ADD COLUMN tier_silver_earning_multiplier NUMERIC(5, 2) DEFAULT 1.2;",
                    "ALTER TABLE loyalty_programs ADD COLUMN tier_silver_redemption_multiplier NUMERIC(5, 2) DEFAULT 1.1;",
                    "ALTER TABLE loyalty_programs ADD COLUMN tier_silver_max_discount_percent NUMERIC(5, 2);",
                    "ALTER TABLE loyalty_programs ADD COLUMN tier_gold_earning_multiplier NUMERIC(5, 2) DEFAULT 1.5;",
                    "ALTER TABLE loyalty_programs ADD COLUMN tier_gold_redemption_multiplier NUMERIC(5, 2) DEFAULT 1.25;",
                    "ALTER TABLE loyalty_programs ADD COLUMN tier_gold_max_discount_percent NUMERIC(5, 2);",
                    "ALTER TABLE loyalty_programs ADD COLUMN tier_platinum_earning_multiplier NUMERIC(5, 2) DEFAULT 2.0;",
                    "ALTER TABLE loyalty_programs ADD COLUMN tier_platinum_redemption_multiplier NUMERIC(5, 2) DEFAULT 1.5;",
                    "ALTER TABLE loyalty_programs ADD COLUMN tier_platinum_max_discount_percent NUMERIC(5, 2);"
                ]
                
                for sql in columns_to_add:
                    try:
                        db.session.execute(text(sql))
                    except:
                        pass  # Column might already exist
                
                db.session.commit()
                logger.info("✅ Added tier benefit columns")
                return jsonify({
                    'success': True,
                    'message': '✅ Tier benefits migration completed!',
                    'details': {
                        'columns_added': len(columns_to_add),
                        'features': ['Earning multipliers per tier', 'Redemption multipliers per tier', 'Max discount overrides']
                    }
                })
        
        else:
            return jsonify({
                'success': False,
                'message': f'⚠️ Unsupported database: {db.engine.dialect.name}'
            }), 400
        
    except Exception as e:
        db.session.rollback()
        error_msg = f"Tier benefits migration failed: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return jsonify({
            'success': False,
            'message': f'❌ {error_msg}'
        }), 500

