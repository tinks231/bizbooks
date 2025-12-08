"""
Barcode Migration Script
========================
Adds barcode field to items table

Run once to add:
- barcode column (VARCHAR(50), unique per tenant)
- index for fast barcode lookups

URL: /admin/migrate/barcode
"""

from flask import Blueprint, jsonify
from models import db
from sqlalchemy import text
import logging

barcode_migration_bp = Blueprint('barcode_migration', __name__)
logger = logging.getLogger(__name__)

@barcode_migration_bp.route('/admin/migrate/barcode')
def migrate_barcode():
    """Add barcode field to items table"""
    try:
        with db.engine.connect() as conn:
            # Start transaction
            trans = conn.begin()
            
            try:
                # Add barcode column
                logger.info("Adding barcode column to items table...")
                conn.execute(text("""
                    ALTER TABLE items 
                    ADD COLUMN IF NOT EXISTS barcode VARCHAR(50);
                """))
                
                # Create index for fast lookups
                logger.info("Creating index on barcode column...")
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_items_barcode 
                    ON items(tenant_id, barcode) 
                    WHERE barcode IS NOT NULL;
                """))
                
                # Add unique constraint per tenant
                logger.info("Adding unique constraint on barcode per tenant...")
                conn.execute(text("""
                    DO $$ 
                    BEGIN
                        IF NOT EXISTS (
                            SELECT 1 FROM pg_constraint 
                            WHERE conname = 'uq_items_barcode_tenant'
                        ) THEN
                            ALTER TABLE items 
                            ADD CONSTRAINT uq_items_barcode_tenant 
                            UNIQUE (tenant_id, barcode);
                        END IF;
                    END $$;
                """))
                
                # Commit all changes at once
                trans.commit()
                logger.info("✅ Barcode migration completed successfully!")
                
                return jsonify({
                    'status': 'success',
                    'message': '✅ Barcode field added successfully! Column: barcode (VARCHAR(50)), Index: idx_items_barcode, Constraint: unique per tenant'
                })
                
            except Exception as e:
                trans.rollback()
                raise e
                
    except Exception as e:
        error_msg = str(e)
        logger.error(f"❌ Migration failed: {error_msg}")
        return jsonify({
            'status': 'error',
            'message': f'❌ Migration failed: {error_msg}'
        }), 500

