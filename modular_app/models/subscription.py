"""
Subscription Management Models

Supports recurring billing for gym memberships, coaching classes,
dance studios, music classes, and any subscription-based service.
"""

from datetime import datetime, timedelta
from .database import db


class SubscriptionPlan(db.Model):
    """
    Subscription Plans (e.g., Monthly Gym, Quarterly Dance Class)
    
    Examples:
    - Monthly Gym (₹2,000 for 30 days)
    - Quarterly Coaching (₹5,400 for 90 days)
    - Annual Music Class (₹19,200 for 365 days)
    """
    __tablename__ = 'subscription_plans'
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    
    # Plan details
    name = db.Column(db.String(100), nullable=False)  # "Monthly Gym Membership"
    description = db.Column(db.Text)  # "Includes all equipment access"
    price = db.Column(db.Numeric(10, 2), nullable=False)  # ₹2,000
    duration_days = db.Column(db.Integer, nullable=False)  # 30 days
    
    # Status
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    subscriptions = db.relationship('CustomerSubscription', backref='plan', lazy=True)
    
    def __repr__(self):
        return f'<SubscriptionPlan {self.name}>'
    
    @property
    def active_members_count(self):
        """Count of currently active subscriptions on this plan"""
        return CustomerSubscription.query.filter_by(
            plan_id=self.id,
            status='active'
        ).count()
    
    @property
    def duration_display(self):
        """Human-readable duration (e.g., '1 month', '3 months', '1 year')"""
        if self.duration_days == 30:
            return '1 month'
        elif self.duration_days == 90:
            return '3 months'
        elif self.duration_days == 365:
            return '1 year'
        else:
            return f'{self.duration_days} days'


class CustomerSubscription(db.Model):
    """
    Customer Subscription Records
    
    Tracks each customer's active/expired subscription,
    billing dates, and payment status.
    """
    __tablename__ = 'customer_subscriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    
    # Customer & Plan
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey('subscription_plans.id'), nullable=False)
    
    # Billing dates
    start_date = db.Column(db.Date, nullable=False)  # When subscription started
    current_period_start = db.Column(db.Date, nullable=False)  # Current billing period start
    current_period_end = db.Column(db.Date, nullable=False)  # Current billing period end (next due date)
    
    # Status
    status = db.Column(db.String(20), default='active')  # active, expired, cancelled
    auto_renew = db.Column(db.Boolean, default=True)  # Auto-renew when period ends
    
    # Cancellation
    cancelled_at = db.Column(db.DateTime)
    cancellation_reason = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    customer = db.relationship('Customer', backref='subscriptions')
    payments = db.relationship('SubscriptionPayment', backref='subscription', lazy=True, order_by='SubscriptionPayment.payment_date.desc()')
    
    def __repr__(self):
        return f'<CustomerSubscription {self.customer.name} - {self.plan.name}>'
    
    @property
    def days_remaining(self):
        """Days remaining until next billing date"""
        if self.status != 'active':
            return 0
        delta = self.current_period_end - datetime.now().date()
        return max(0, delta.days)
    
    @property
    def is_due_soon(self):
        """True if payment is due within 3 days"""
        return self.days_remaining <= 3 and self.status == 'active'
    
    @property
    def is_overdue(self):
        """True if payment date has passed"""
        return self.current_period_end < datetime.now().date() and self.status == 'active'
    
    @property
    def status_display(self):
        """User-friendly status with emoji"""
        if self.is_overdue:
            return '🔴 Overdue'
        elif self.is_due_soon:
            return '🟡 Due Soon'
        elif self.status == 'active':
            return '🟢 Active'
        elif self.status == 'expired':
            return '⚫ Expired'
        elif self.status == 'cancelled':
            return '❌ Cancelled'
        return self.status
    
    @property
    def total_paid(self):
        """Total amount paid for this subscription"""
        total = db.session.query(db.func.sum(SubscriptionPayment.amount)).filter(
            SubscriptionPayment.subscription_id == self.id
        ).scalar()
        return total or 0
    
    @property
    def payment_count(self):
        """Number of payments made"""
        return len(self.payments)
    
    def renew_subscription(self):
        """
        Renew subscription for next billing period.
        Updates current_period_start and current_period_end.
        """
        self.current_period_start = self.current_period_end + timedelta(days=1)
        self.current_period_end = self.current_period_start + timedelta(days=self.plan.duration_days)
        self.status = 'active'
        self.updated_at = datetime.utcnow()
    
    def cancel_subscription(self, reason=None):
        """Cancel the subscription"""
        self.status = 'cancelled'
        self.cancelled_at = datetime.utcnow()
        self.cancellation_reason = reason
        self.auto_renew = False


class SubscriptionPayment(db.Model):
    """
    Subscription Payment Records
    
    Tracks each payment made for a subscription.
    Each payment is also linked to an Invoice for accounting.
    """
    __tablename__ = 'subscription_payments'
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    
    # Links
    subscription_id = db.Column(db.Integer, db.ForeignKey('customer_subscriptions.id'), nullable=False)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id'))  # Auto-generated invoice
    
    # Payment details
    payment_date = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_mode = db.Column(db.String(50))  # Cash, UPI, Card, etc.
    
    # Billing period this payment covers
    period_start = db.Column(db.Date, nullable=False)
    period_end = db.Column(db.Date, nullable=False)
    billing_period_label = db.Column(db.String(50))  # "Nov 2025", "Nov-Dec 2025"
    
    # Notes
    notes = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    invoice = db.relationship('Invoice', backref='subscription_payment', uselist=False)
    
    def __repr__(self):
        return f'<SubscriptionPayment {self.amount} on {self.payment_date}>'
    
    @property
    def period_display(self):
        """Human-readable billing period"""
        if self.billing_period_label:
            return self.billing_period_label
        
        # Generate from dates
        if self.period_start.month == self.period_end.month:
            return self.period_start.strftime('%b %Y')
        else:
            return f"{self.period_start.strftime('%b')}-{self.period_end.strftime('%b %Y')}"

