"""
Password Reset Token Migration
Creates table for secure password reset functionality
Access: /migrate/add-password-reset-tokens
"""

from flask import Blueprint, jsonify
from models import db
from sqlalchemy import text

password_reset_migration_bp = Blueprint('password_reset_migration', __name__, url_prefix='/migrate')


@password_reset_migration_bp.route('/add-password-reset-tokens')
def add_password_reset_tokens():
    """
    Creates password_reset_tokens table for secure forgot password flow
    
    SECURITY FIX:
    - Before: Anyone could reset anyone's password (CRITICAL vulnerability!)
    - After: Secure email-based reset with one-time tokens
    
    Access this URL once: /migrate/add-password-reset-tokens
    """
    try:
        # Detect database type
        db_url = str(db.engine.url)
        is_postgres = 'postgresql' in db_url
        
        if is_postgres:
            # PostgreSQL syntax
            migration_sql = text("""
                -- Create password_reset_tokens table
                CREATE TABLE IF NOT EXISTS password_reset_tokens (
                    id SERIAL PRIMARY KEY,
                    tenant_id INTEGER NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
                    token VARCHAR(100) UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL,
                    used BOOLEAN DEFAULT FALSE,
                    used_at TIMESTAMP,
                    ip_address VARCHAR(50)
                );
                
                -- Create index for fast token lookup
                CREATE INDEX IF NOT EXISTS idx_password_reset_token 
                    ON password_reset_tokens(token) 
                    WHERE used = FALSE;
                
                -- Create index for cleanup (delete expired tokens)
                CREATE INDEX IF NOT EXISTS idx_password_reset_expires 
                    ON password_reset_tokens(expires_at);
            """)
        else:
            # SQLite syntax (for local development)
            migration_sql = text("""
                CREATE TABLE IF NOT EXISTS password_reset_tokens (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
                    token VARCHAR(100) UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL,
                    used INTEGER DEFAULT 0,
                    used_at TIMESTAMP,
                    ip_address VARCHAR(50)
                );
                
                CREATE INDEX IF NOT EXISTS idx_password_reset_token 
                    ON password_reset_tokens(token);
                
                CREATE INDEX IF NOT EXISTS idx_password_reset_expires 
                    ON password_reset_tokens(expires_at);
            """)
        
        # Execute migration
        db.session.execute(migration_sql)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': '✅ Password reset tokens table created successfully!',
            'table_created': 'password_reset_tokens',
            'indexes_created': [
                'idx_password_reset_token (for fast lookup)',
                'idx_password_reset_expires (for cleanup)'
            ],
            'next_steps': [
                '1. Password reset now uses secure email-based tokens',
                '2. Tokens expire in 1 hour',
                '3. One-time use only',
                '4. Test the new forgot password flow'
            ]
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'❌ Migration failed: {str(e)}'
        }), 500

