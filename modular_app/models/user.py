"""
User model for admin authentication
"""
from .database import db, TimestampMixin
import hashlib

class User(db.Model, TimestampMixin):
    """Admin user model"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=True)
    active = db.Column(db.Boolean, default=True)
    
    def set_password(self, password):
        """Hash and set password using SHA256"""
        self.password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    def check_password(self, password):
        """Check if password matches"""
        return self.password_hash == hashlib.sha256(password.encode()).hexdigest()
    
    def __repr__(self):
        return f'<User {self.username}>'

