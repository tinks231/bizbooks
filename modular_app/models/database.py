"""
Database initialization and shared setup
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Initialize SQLAlchemy
db = SQLAlchemy()

def init_db(app):
    """Initialize database with app"""
    db.init_app(app)
    
    with app.app_context():
        # Create all tables (safe even if some already exist)
        from sqlalchemy.exc import ProgrammingError
        try:
            db.create_all()
        except ProgrammingError as exc:
            # Ignore duplicate table errors triggered when tables are created via manual migrations
            message = str(exc).lower()
            if 'already exists' in message:
                db.session.rollback()
                app.logger.warning(f"⚠️ Skipping create_all duplicate table error: {exc}")
            else:
                raise
        
        # Create default admin user if not exists
        from .user import User
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                is_admin=True
            )
            admin.set_password('admin123')  # Change this!
            db.session.add(admin)
            db.session.commit()
            print("✅ Default admin user created (username: admin, password: admin123)")
        
        print("✅ Database initialized successfully!")

# Base model with common fields
class TimestampMixin:
    """Mixin to add timestamp fields to models"""
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

