"""
One-time migration routes for database updates
Access these URLs once after deployment to migrate the database
"""
from flask import Blueprint, jsonify
from models import db
from sqlalchemy import text

migration_bp = Blueprint('migration', __name__, url_prefix='/migrate')

@migration_bp.route('/recreate-all-tables')
def recreate_all_tables():
    """
    DROP and RECREATE all tables with correct schema
    ⚠️ WARNING: This will DELETE ALL DATA!
    Access this URL once: /migrate/recreate-all-tables
    """
    try:
        # Drop all tables
        db.drop_all()
        
        # Recreate all tables with correct schema
        db.create_all()
        
        return jsonify({
            'status': 'success',
            'message': '✅ All tables recreated successfully!',
            'action': 'Tables dropped and recreated with latest schema',
            'next_step': 'Your app should work now! Go to /register to create a new account.'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Recreation failed: {str(e)}',
            'details': str(e)
        }), 500

@migration_bp.route('/rename-radius-to-allowed-radius')
def migrate_radius_column():
    """
    Rename 'radius' to 'allowed_radius' in sites table
    Access this URL once: /migrate/rename-radius-to-allowed-radius
    """
    try:
        # Check if we're using PostgreSQL
        db_url = db.engine.url.drivername
        
        if 'postgresql' in db_url:
            # Check if 'allowed_radius' already exists
            check_sql = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='sites' AND column_name='allowed_radius'
            """)
            result = db.session.execute(check_sql).fetchone()
            
            if result:
                return jsonify({
                    'status': 'success',
                    'message': '✅ Column "allowed_radius" already exists - migration not needed!',
                    'action': 'none'
                })
            
            # Check if 'radius' exists
            check_old_sql = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='sites' AND column_name='radius'
            """)
            old_result = db.session.execute(check_old_sql).fetchone()
            
            if old_result:
                # Rename column
                migrate_sql = text("""
                    ALTER TABLE sites 
                    RENAME COLUMN radius TO allowed_radius
                """)
                db.session.execute(migrate_sql)
                db.session.commit()
                
                return jsonify({
                    'status': 'success',
                    'message': '✅ Successfully renamed "radius" to "allowed_radius"!',
                    'action': 'renamed',
                    'next_step': 'Refresh your app - it should work now!'
                })
            else:
                # Neither column exists - add new one
                add_sql = text("""
                    ALTER TABLE sites 
                    ADD COLUMN allowed_radius INTEGER DEFAULT 100
                """)
                db.session.execute(add_sql)
                db.session.commit()
                
                return jsonify({
                    'status': 'success',
                    'message': '✅ Added "allowed_radius" column with default value 100!',
                    'action': 'added',
                    'next_step': 'Refresh your app - it should work now!'
                })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Not a PostgreSQL database',
                'db_type': db_url
            })
            
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Migration failed: {str(e)}',
            'details': str(e)
        }), 500

@migration_bp.route('/status')
def migration_status():
    """Check migration status"""
    try:
        check_sql = text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='sites' 
            ORDER BY ordinal_position
        """)
        result = db.session.execute(check_sql).fetchall()
        columns = [row[0] for row in result]
        
        has_radius = 'radius' in columns
        has_allowed_radius = 'allowed_radius' in columns
        
        return jsonify({
            'status': 'success',
            'sites_table_columns': columns,
            'has_old_radius': has_radius,
            'has_new_allowed_radius': has_allowed_radius,
            'migration_needed': has_radius and not has_allowed_radius,
            'migration_url': '/migrate/rename-radius-to-allowed-radius'
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

