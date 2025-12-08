"""
Migration: Add is_default field to sites table
Run this at: /migrate/add-site-default-field
"""
from flask import Blueprint, jsonify, g
from models.database import db
from utils.tenant_middleware import require_tenant
from sqlalchemy import text

site_default_migration_bp = Blueprint('site_default_migration', __name__)

@site_default_migration_bp.route('/migrate/add-site-default-field', methods=['GET'])
@require_tenant
def add_site_default_field():
    """Add is_default column to sites table"""
    try:
        tenant_id = g.tenant.id
        results = []
        
        with db.engine.connect() as conn:
            # Start transaction
            trans = conn.begin()
            
            try:
                # 1. Add is_default column to sites table
                try:
                    conn.execute(text("""
                        ALTER TABLE sites 
                        ADD COLUMN IF NOT EXISTS is_default BOOLEAN DEFAULT FALSE;
                    """))
                    results.append("✅ Added 'is_default' column to sites table")
                except Exception as e:
                    if "already exists" in str(e).lower():
                        results.append("ℹ️ is_default column already exists in sites table")
                    else:
                        raise
                
                # 2. Set first site as default if no default exists
                try:
                    # Check if any site is already marked as default
                    result = conn.execute(text("""
                        SELECT COUNT(*) FROM sites 
                        WHERE tenant_id = :tenant_id AND is_default = TRUE
                    """), {'tenant_id': tenant_id})
                    
                    count = result.scalar()
                    
                    if count == 0:
                        # No default site - set first active site as default
                        conn.execute(text("""
                            UPDATE sites 
                            SET is_default = TRUE 
                            WHERE id = (
                                SELECT id FROM sites 
                                WHERE tenant_id = :tenant_id AND active = TRUE 
                                ORDER BY created_at ASC 
                                LIMIT 1
                            )
                        """), {'tenant_id': tenant_id})
                        results.append("✅ Set first active site as default site")
                    else:
                        results.append(f"ℹ️ Default site already configured ({count} site(s) marked as default)")
                except Exception as e:
                    results.append(f"⚠️ Could not auto-set default site: {str(e)}")
                
                # Commit transaction
                trans.commit()
                
                return jsonify({
                    'status': 'success',
                    'message': '✅ Migration completed successfully!',
                    'changes': results,
                    'next_steps': [
                        '1. Restart your Flask app to load the new field',
                        '2. Go to Items & Inventory → Manage Sites',
                        '3. Click "Set as Default" on your main site',
                        '4. Create invoices - stock will deduct from default site'
                    ]
                }), 200
                
            except Exception as e:
                trans.rollback()
                raise
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ Migration Error: {error_details}")
        
        return jsonify({
            'status': 'error',
            'message': f'❌ Migration failed: {str(e)}',
            'details': error_details
        }), 500

