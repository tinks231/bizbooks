"""
Subscription Management Models

Supports recurring billing for gym memberships, coaching classes,
dance studios, music classes, and any subscription-based service.
"""

from datetime import datetime, timedelta
from .database import db


class SubscriptionPlan(db.Model):
    """
    Subscription Plans (e.g., Monthly Gym, Quarterly Dance Class, Daily Milk Delivery)
    
    Examples:
    - FIXED: Monthly Gym (₹2,000 for 30 days)
    - FIXED: Quarterly Coaching (₹5,400 for 90 days)
    - METERED: Daily Milk (₹60/liter, billed monthly based on actual consumption)
    - METERED: Daily Newspaper (₹8/piece, billed monthly)
    """
    __tablename__ = 'subscription_plans'
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    
    # Plan Type (NEW for metered subscriptions)
    plan_type = db.Column(db.String(20), default='fixed', nullable=False)  # 'fixed' or 'metered'
    
    # Plan details
    name = db.Column(db.String(100), nullable=False)  # "Monthly Gym Membership" or "Daily Milk Delivery"
    description = db.Column(db.Text)  # "Includes all equipment access" or "Fresh A2 milk daily"
    
    # FIXED plan pricing
    price = db.Column(db.Numeric(10, 2))  # ₹2,000 (NULL for metered plans)
    duration_days = db.Column(db.Integer)  # 30 days (NULL or used as billing cycle for metered)
    
    # METERED plan pricing (NEW)
    unit_rate = db.Column(db.Numeric(10, 2))  # ₹60 per liter (NULL for fixed plans)
    unit_name = db.Column(db.String(20))  # 'liter', 'kg', 'piece', 'hour' (NULL for fixed)
    
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
    
    # METERED subscriptions only (NEW)
    default_quantity = db.Column(db.Numeric(10, 2))  # e.g., 2 liters/day (NULL for fixed plans)
    
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
    deliveries = db.relationship('SubscriptionDelivery', backref='subscription', lazy=True, order_by='SubscriptionDelivery.delivery_date.desc()')
    
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
        if self.status == 'pending_payment':
            return '⏳ Pending Payment'
        elif self.is_overdue:
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
        # Check if we have a cached value (set by route to avoid N+1 queries)
        if hasattr(self, '_cached_total_paid'):
            return self._cached_total_paid
        
        # Fallback: Calculate on demand (slower, causes N+1 if used in loops)
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


class SubscriptionDelivery(db.Model):
    """
    Daily Delivery Records (for METERED subscriptions only)
    
    Tracks actual daily deliveries for consumption-based billing.
    Auto-generated on enrollment, updated only for exceptions.
    
    Examples:
    - Dec 1: 2L delivered (default) ✅
    - Dec 10: 0L (paused - vacation) ⏸️
    - Dec 20: 3L delivered (party - one-time increase) 🎉
    - Dec 25: 1L delivered (permanent reduction) 📉
    """
    __tablename__ = 'subscription_deliveries'
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    
    # Links
    subscription_id = db.Column(db.Integer, db.ForeignKey('customer_subscriptions.id'), nullable=False)
    
    # Delivery details
    delivery_date = db.Column(db.Date, nullable=False, index=True)  # Dec 1, 2025
    quantity = db.Column(db.Numeric(10, 2), nullable=False)  # 2.0 liters
    rate = db.Column(db.Numeric(10, 2), nullable=False)  # ₹60/liter (frozen at time of delivery)
    amount = db.Column(db.Numeric(10, 2), nullable=False)  # ₹120 (quantity × rate)
    
    # Status
    status = db.Column(db.String(20), default='delivered', nullable=False)  # delivered, paused, skipped, pending
    
    # Change tracking
    is_modified = db.Column(db.Boolean, default=False)  # True if manually changed from default
    modification_reason = db.Column(db.String(200))  # "Party", "Vacation", "Reduced quantity", etc.
    
    # Notes
    notes = db.Column(db.Text)  # Additional delivery notes
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Unique constraint: one delivery per subscription per date
    __table_args__ = (
        db.UniqueConstraint('subscription_id', 'delivery_date', name='uq_subscription_delivery_date'),
    )
    
    def __repr__(self):
        return f'<SubscriptionDelivery {self.delivery_date} - {self.quantity} {self.subscription.plan.unit_name}>'
    
    @property
    def status_display(self):
        """User-friendly status with emoji"""
        if self.status == 'delivered':
            if self.quantity == 0:
                return '⏸️ Paused'
            elif self.is_modified:
                return f'✅ {self.quantity} (modified)'
            return f'✅ {self.quantity}'
        elif self.status == 'paused':
            return '⏸️ Paused'
        elif self.status == 'skipped':
            return '⏭️ Skipped'
        elif self.status == 'pending':
            return '⏳ Pending'
        return self.status
    
    @classmethod
    def get_exceptions(cls, tenant_id, date_from=None, date_to=None):
        """
        Get only modified/paused deliveries (exceptions to default)
        Used for the "Exceptions Dashboard" view
        """
        query = cls.query.filter_by(tenant_id=tenant_id)
        
        if date_from:
            query = query.filter(cls.delivery_date >= date_from)
        if date_to:
            query = query.filter(cls.delivery_date <= date_to)
        
        # Only show exceptions (paused or modified)
        query = query.filter(
            db.or_(
                cls.is_modified == True,
                cls.status == 'paused',
                cls.quantity == 0
            )
        )
        
        return query.order_by(cls.delivery_date.asc()).all()
    
    @classmethod
    def bulk_pause(cls, subscription_id, date_from, date_to, reason="Paused by customer"):
        """
        Pause deliveries for a date range
        Updates all deliveries in range to quantity=0, status=paused
        """
        from datetime import timedelta
        
        current_date = date_from
        updated_count = 0
        
        while current_date <= date_to:
            delivery = cls.query.filter_by(
                subscription_id=subscription_id,
                delivery_date=current_date
            ).first()
            
            if delivery:
                delivery.quantity = 0
                delivery.amount = 0
                delivery.status = 'paused'
                delivery.is_modified = True
                delivery.modification_reason = reason
                delivery.updated_at = datetime.utcnow()
                updated_count += 1
            
            current_date += timedelta(days=1)
        
        db.session.commit()
        return updated_count

