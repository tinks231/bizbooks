"""
Vendor Performance Migration - Add vendor_name index to purchase_requests
This migration adds a critical index to optimize vendor count queries
"""
from flask import Blueprint, render_template, flash, redirect, url_for, jsonify, g, request
from models.database import db
from sqlalchemy import text, inspect
import logging

logger = logging.getLogger(__name__)

vendor_performance_bp = Blueprint('vendor_performance_migration', __name__, url_prefix='/migration/vendor-performance')

@vendor_performance_bp.route('/run')
def run_migration():
    """Add vendor_name index to purchase_requests for performance optimization"""
    
    try:
        # Check current database engine
        inspector = inspect(db.engine)
        
        # PostgreSQL / Supabase
        if db.engine.dialect.name == 'postgresql':
            logger.info("Running vendor performance migration for PostgreSQL...")
            
            # Check if index already exists
            indexes = inspector.get_indexes('purchase_requests')
            index_exists = any(idx['name'] == 'idx_tenant_vendor' for idx in indexes)
            
            if not index_exists:
                db.session.execute(text("""
                    CREATE INDEX idx_tenant_vendor 
                    ON purchase_requests(tenant_id, vendor_name);
                """))
                db.session.commit()
                logger.info("✅ Created idx_tenant_vendor index on purchase_requests")
                return jsonify({
                    'success': True,
                    'message': '✅ Vendor performance index created successfully!',
                    'details': 'Added composite index on (tenant_id, vendor_name) in purchase_requests table'
                })
            else:
                logger.info("Index idx_tenant_vendor already exists")
                return jsonify({
                    'success': True,
                    'message': 'ℹ️ Vendor performance index already exists',
                    'details': 'No action needed - index is already in place'
                })
        
        # SQLite (local development)
        elif db.engine.dialect.name == 'sqlite':
            logger.info("Running vendor performance migration for SQLite...")
            
            db.session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_tenant_vendor 
                ON purchase_requests(tenant_id, vendor_name);
            """))
            db.session.commit()
            logger.info("✅ Created idx_tenant_vendor index on purchase_requests")
            return jsonify({
                'success': True,
                'message': '✅ Vendor performance index created successfully!',
                'details': 'Added composite index on (tenant_id, vendor_name) in purchase_requests table'
            })
        
        else:
            return jsonify({
                'success': False,
                'message': f'⚠️ Unsupported database: {db.engine.dialect.name}'
            }), 400
        
    except Exception as e:
        db.session.rollback()
        error_msg = f"Vendor performance migration failed: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return jsonify({
            'success': False,
            'message': f'❌ {error_msg}'
        }), 500

