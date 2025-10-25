"""
Tenant model for multi-tenant SaaS
Each tenant represents one client/business
"""
from models import db
from datetime import datetime, timedelta

class Tenant(db.Model):
    """Tenant/Client model - each client business"""
    __tablename__ = 'tenants'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Company info
    company_name = db.Column(db.String(100), nullable=False)
    subdomain = db.Column(db.String(50), unique=True, nullable=False, index=True)
    
    # Admin contact
    admin_name = db.Column(db.String(100), nullable=False)
    admin_email = db.Column(db.String(100), unique=True, nullable=False)
    admin_phone = db.Column(db.String(20))
    admin_password_hash = db.Column(db.String(256), nullable=False)
    
    # Subscription info
    plan = db.Column(db.String(20), default='trial')  # trial, basic, pro
    status = db.Column(db.String(20), default='active')  # active, trial, expired, suspended
    trial_ends_at = db.Column(db.DateTime)
    subscription_ends_at = db.Column(db.DateTime)
    
    # Limits
    max_employees = db.Column(db.Integer, default=50)
    max_sites = db.Column(db.Integer, default=5)
    storage_limit_mb = db.Column(db.Integer, default=1000)
    
    # Features
    features = db.Column(db.Text)  # JSON string of enabled features
    
    # Settings
    settings = db.Column(db.Text)  # JSON string of tenant-specific settings
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at = db.Column(db.DateTime)
    
    # Relationships
    employees = db.relationship('Employee', backref='tenant', lazy=True, cascade='all, delete-orphan')
    sites = db.relationship('Site', backref='tenant', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, **kwargs):
        super(Tenant, self).__init__(**kwargs)
        # Set trial end date (30 days from now)
        if not self.trial_ends_at:
            self.trial_ends_at = datetime.utcnow() + timedelta(days=30)
    
    @property
    def is_trial(self):
        """Check if tenant is in trial period"""
        return self.status == 'trial' and self.trial_ends_at > datetime.utcnow()
    
    @property
    def is_active(self):
        """Check if tenant subscription is active"""
        if self.status == 'suspended':
            return False
        if self.status == 'trial':
            return self.trial_ends_at > datetime.utcnow()
        if self.subscription_ends_at:
            return self.subscription_ends_at > datetime.utcnow()
        return True
    
    @property
    def days_remaining(self):
        """Get days remaining in trial or subscription"""
        if self.status == 'trial':
            delta = self.trial_ends_at - datetime.utcnow()
            return max(0, delta.days)
        if self.subscription_ends_at:
            delta = self.subscription_ends_at - datetime.utcnow()
            return max(0, delta.days)
        return 0
    
    @property
    def employee_count(self):
        """Get current employee count"""
        return len(self.employees)
    
    @property
    def site_count(self):
        """Get current site count"""
        return len(self.sites)
    
    def can_add_employee(self):
        """Check if tenant can add more employees"""
        return self.employee_count < self.max_employees
    
    def can_add_site(self):
        """Check if tenant can add more sites"""
        return self.site_count < self.max_sites
    
    @property
    def url(self):
        """Get tenant's full URL"""
        return f"https://{self.subdomain}.bizbooks.co.in"
    
    def __repr__(self):
        return f'<Tenant {self.company_name} ({self.subdomain})>'

