"""
Database migration: Rename 'radius' to 'allowed_radius' in sites table
Run this once after deploying the new code
"""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db

def migrate_site_radius():
    """Rename radius column to allowed_radius"""
    with app.app_context():
        try:
            # Check if we're using PostgreSQL
            db_url = app.config.get('SQLALCHEMY_DATABASE_URI', '')
            
            if 'postgresql' in db_url:
                print("🔄 Running PostgreSQL migration...")
                
                # PostgreSQL: Rename column
                sql = """
                ALTER TABLE sites 
                RENAME COLUMN radius TO allowed_radius;
                """
                
                try:
                    db.session.execute(db.text(sql))
                    db.session.commit()
                    print("✅ Successfully renamed 'radius' to 'allowed_radius' in sites table")
                except Exception as e:
                    if 'does not exist' in str(e).lower():
                        print("⚠️  Column 'radius' doesn't exist - checking if 'allowed_radius' already exists...")
                        
                        # Check if allowed_radius exists
                        check_sql = """
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name='sites' AND column_name='allowed_radius';
                        """
                        result = db.session.execute(db.text(check_sql))
                        if result.fetchone():
                            print("✅ Column 'allowed_radius' already exists - migration not needed!")
                        else:
                            print("❌ Neither column exists - need to add 'allowed_radius' column")
                            add_sql = """
                            ALTER TABLE sites 
                            ADD COLUMN allowed_radius INTEGER DEFAULT 100;
                            """
                            db.session.execute(db.text(add_sql))
                            db.session.commit()
                            print("✅ Added 'allowed_radius' column with default value 100")
                    else:
                        raise
            else:
                print("⚠️  SQLite detected - running SQLite migration...")
                # SQLite doesn't support RENAME COLUMN directly
                # Need to recreate the table
                print("❌ SQLite migration not implemented - please delete instance/app.db and restart")
                
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    print("=" * 50)
    print("Site Radius Migration")
    print("=" * 50)
    migrate_site_radius()
    print("=" * 50)
    print("✅ Migration complete!")

