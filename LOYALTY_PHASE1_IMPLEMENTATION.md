# 🎁 Loyalty Program - Phase 1 Implementation Plan

## ✅ What We're Building (Phase 1 - 2 Weeks)

### **Core Features:**
1. ✅ Basic points earning (configurable rate per tenant)
2. ✅ Threshold bonuses (bonus points when invoice > certain amount)
3. ✅ Points redemption (separate "Loyalty Discount" row in invoice)
4. ✅ Customer points balance tracking
5. ✅ Points transaction history
6. ✅ Admin loyalty settings page (full configuration)
7. ✅ Admin reports (points issued, redeemed, top customers)
8. ✅ Clean printed invoice (optional footer with points balance)
9. ✅ Multi-tenant support (each tenant configures independently)

### **NOT in Phase 1 (Coming in Phase 2):**
- ❌ Tiered membership (Bronze/Silver/Gold/Platinum)
- ❌ Birthday/Anniversary bonuses
- ❌ SMS notifications
- ❌ Points expiry
- ❌ Welcome bonus
- ❌ Campaigns

---

## 📊 Database Schema

### **Table 1: `loyalty_programs`**
Stores loyalty program settings per tenant (fully configurable).

```sql
CREATE TABLE loyalty_programs (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL REFERENCES tenants(id),
    
    -- Basic Settings
    program_name VARCHAR(100) DEFAULT 'Loyalty Program',
    is_active BOOLEAN DEFAULT false,  -- OFF by default (opt-in)
    
    -- Earning Rules
    points_per_100_rupees DECIMAL(5,2) DEFAULT 1.00,  -- Configurable
    minimum_purchase_for_points DECIMAL(10,2) DEFAULT 0,
    maximum_points_per_invoice INTEGER,  -- Optional cap
    
    -- Threshold Bonuses
    enable_threshold_bonuses BOOLEAN DEFAULT false,
    threshold_1_amount DECIMAL(10,2),  -- e.g., ₹5,000
    threshold_1_bonus_points INTEGER,  -- e.g., 50 pts
    threshold_2_amount DECIMAL(10,2),  -- e.g., ₹10,000
    threshold_2_bonus_points INTEGER,  -- e.g., 200 pts
    threshold_3_amount DECIMAL(10,2),  -- e.g., ₹25,000 (optional)
    threshold_3_bonus_points INTEGER,  -- e.g., 500 pts (optional)
    
    -- Redemption Rules
    points_to_rupees_ratio DECIMAL(5,2) DEFAULT 1.00,  -- 1 pt = ₹1
    minimum_points_to_redeem INTEGER DEFAULT 10,
    maximum_discount_percent DECIMAL(5,2),  -- Optional: e.g., 20%
    maximum_points_per_redemption INTEGER,  -- Optional cap
    
    -- Invoice Display
    show_points_on_invoice BOOLEAN DEFAULT true,  -- Footer note
    invoice_footer_text VARCHAR(255) DEFAULT 'Points Balance: {balance} pts | Next visit: ₹{value} off!',
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(tenant_id)
);
```

---

### **Table 2: `customer_loyalty_points`**
Stores points balance per customer.

```sql
CREATE TABLE customer_loyalty_points (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL REFERENCES tenants(id),
    customer_id INTEGER NOT NULL REFERENCES customers(id),
    
    -- Points Balance
    current_points INTEGER DEFAULT 0,  -- Available to redeem
    lifetime_earned_points INTEGER DEFAULT 0,  -- Total earned (for tier calculation in Phase 2)
    lifetime_redeemed_points INTEGER DEFAULT 0,  -- Total redeemed
    
    -- Metadata
    last_earned_at TIMESTAMP,
    last_redeemed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(tenant_id, customer_id)
);

CREATE INDEX idx_loyalty_points_customer ON customer_loyalty_points(tenant_id, customer_id);
```

---

### **Table 3: `loyalty_transactions`**
Stores every points transaction (earn/redeem).

```sql
CREATE TABLE loyalty_transactions (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL REFERENCES tenants(id),
    customer_id INTEGER NOT NULL REFERENCES customers(id),
    
    -- Transaction Type
    transaction_type VARCHAR(20) NOT NULL,  -- 'earned', 'redeemed', 'adjusted', 'bonus'
    
    -- Points
    points INTEGER NOT NULL,  -- Positive for earn, negative for redeem
    points_before INTEGER,  -- Balance before transaction
    points_after INTEGER,   -- Balance after transaction
    
    -- Reference
    invoice_id INTEGER REFERENCES invoices(id),
    invoice_number VARCHAR(50),
    description TEXT,  -- e.g., "Earned from purchase", "Threshold bonus"
    
    -- Details
    base_points INTEGER,  -- Points from base calculation
    bonus_points INTEGER,  -- Bonus points from thresholds
    invoice_amount DECIMAL(10,2),  -- Original invoice amount
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES users(id)
);

CREATE INDEX idx_loyalty_transactions_customer ON loyalty_transactions(tenant_id, customer_id, created_at DESC);
CREATE INDEX idx_loyalty_transactions_invoice ON loyalty_transactions(invoice_id);
```

---

### **Table 4: Updates to Existing Tables**

**`customers` table:**
```sql
ALTER TABLE customers ADD COLUMN date_of_birth DATE;
ALTER TABLE customers ADD COLUMN anniversary_date DATE;
-- Both optional, for Phase 2 birthday/anniversary bonuses
```

**`invoices` table:**
```sql
ALTER TABLE invoices ADD COLUMN loyalty_discount DECIMAL(10,2) DEFAULT 0;
ALTER TABLE invoices ADD COLUMN loyalty_points_redeemed INTEGER DEFAULT 0;
ALTER TABLE invoices ADD COLUMN loyalty_points_earned INTEGER DEFAULT 0;
```

---

## 🔧 Backend Implementation

### **1. Models** (`modular_app/models/`)

**`loyalty_program.py`:**
```python
class LoyaltyProgram(db.Model):
    __tablename__ = 'loyalty_programs'
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    
    # Settings
    program_name = db.Column(db.String(100), default='Loyalty Program')
    is_active = db.Column(db.Boolean, default=False)
    
    # Earning rules
    points_per_100_rupees = db.Column(db.Numeric(5, 2), default=1.00)
    minimum_purchase_for_points = db.Column(db.Numeric(10, 2), default=0)
    maximum_points_per_invoice = db.Column(db.Integer)
    
    # Threshold bonuses
    enable_threshold_bonuses = db.Column(db.Boolean, default=False)
    threshold_1_amount = db.Column(db.Numeric(10, 2))
    threshold_1_bonus_points = db.Column(db.Integer)
    threshold_2_amount = db.Column(db.Numeric(10, 2))
    threshold_2_bonus_points = db.Column(db.Integer)
    threshold_3_amount = db.Column(db.Numeric(10, 2))
    threshold_3_bonus_points = db.Column(db.Integer)
    
    # Redemption rules
    points_to_rupees_ratio = db.Column(db.Numeric(5, 2), default=1.00)
    minimum_points_to_redeem = db.Column(db.Integer, default=10)
    maximum_discount_percent = db.Column(db.Numeric(5, 2))
    maximum_points_per_redemption = db.Column(db.Integer)
    
    # Display
    show_points_on_invoice = db.Column(db.Boolean, default=True)
    invoice_footer_text = db.Column(db.String(255))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tenant = db.relationship('Tenant', backref='loyalty_program')
```

**`customer_loyalty_points.py`:**
```python
class CustomerLoyaltyPoints(db.Model):
    __tablename__ = 'customer_loyalty_points'
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    
    current_points = db.Column(db.Integer, default=0)
    lifetime_earned_points = db.Column(db.Integer, default=0)
    lifetime_redeemed_points = db.Column(db.Integer, default=0)
    
    last_earned_at = db.Column(db.DateTime)
    last_redeemed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tenant = db.relationship('Tenant')
    customer = db.relationship('Customer', backref='loyalty_points')
```

**`loyalty_transaction.py`:**
```python
class LoyaltyTransaction(db.Model):
    __tablename__ = 'loyalty_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    
    transaction_type = db.Column(db.String(20), nullable=False)
    points = db.Column(db.Integer, nullable=False)
    points_before = db.Column(db.Integer)
    points_after = db.Column(db.Integer)
    
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id'))
    invoice_number = db.Column(db.String(50))
    description = db.Column(db.Text)
    
    base_points = db.Column(db.Integer)
    bonus_points = db.Column(db.Integer)
    invoice_amount = db.Column(db.Numeric(10, 2))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    tenant = db.relationship('Tenant')
    customer = db.relationship('Customer')
    invoice = db.relationship('Invoice')
```

---

### **2. Loyalty Service** (`modular_app/services/loyalty_service.py`)

Core business logic for points calculation.

```python
class LoyaltyService:
    
    @staticmethod
    def get_loyalty_program(tenant_id):
        """Get loyalty program settings for tenant"""
        return LoyaltyProgram.query.filter_by(tenant_id=tenant_id).first()
    
    @staticmethod
    def calculate_points_earned(invoice_amount, tenant_id):
        """Calculate points earned for an invoice"""
        program = LoyaltyService.get_loyalty_program(tenant_id)
        
        if not program or not program.is_active:
            return {'base_points': 0, 'bonus_points': 0, 'total_points': 0}
        
        # Check minimum purchase
        if invoice_amount < program.minimum_purchase_for_points:
            return {'base_points': 0, 'bonus_points': 0, 'total_points': 0}
        
        # Base points calculation
        base_points = int((invoice_amount / 100) * program.points_per_100_rupees)
        
        # Apply max cap if set
        if program.maximum_points_per_invoice:
            base_points = min(base_points, program.maximum_points_per_invoice)
        
        # Calculate threshold bonus
        bonus_points = 0
        if program.enable_threshold_bonuses:
            if program.threshold_3_amount and invoice_amount >= program.threshold_3_amount:
                bonus_points = program.threshold_3_bonus_points or 0
            elif program.threshold_2_amount and invoice_amount >= program.threshold_2_amount:
                bonus_points = program.threshold_2_bonus_points or 0
            elif program.threshold_1_amount and invoice_amount >= program.threshold_1_amount:
                bonus_points = program.threshold_1_bonus_points or 0
        
        total_points = base_points + bonus_points
        
        return {
            'base_points': base_points,
            'bonus_points': bonus_points,
            'total_points': total_points
        }
    
    @staticmethod
    def calculate_redemption_value(points, tenant_id):
        """Calculate discount value when redeeming points"""
        program = LoyaltyService.get_loyalty_program(tenant_id)
        
        if not program or not program.is_active:
            return 0
        
        return float(points * program.points_to_rupees_ratio)
    
    @staticmethod
    def get_customer_balance(customer_id, tenant_id):
        """Get customer's current points balance"""
        loyalty = CustomerLoyaltyPoints.query.filter_by(
            customer_id=customer_id,
            tenant_id=tenant_id
        ).first()
        
        if not loyalty:
            # Auto-create loyalty record
            loyalty = CustomerLoyaltyPoints(
                customer_id=customer_id,
                tenant_id=tenant_id,
                current_points=0,
                lifetime_earned_points=0,
                lifetime_redeemed_points=0
            )
            db.session.add(loyalty)
            db.session.commit()
        
        return loyalty
    
    @staticmethod
    def credit_points(customer_id, tenant_id, points, invoice_id, description, base_points=0, bonus_points=0, invoice_amount=0):
        """Credit points to customer account"""
        loyalty = LoyaltyService.get_customer_balance(customer_id, tenant_id)
        
        points_before = loyalty.current_points
        loyalty.current_points += points
        loyalty.lifetime_earned_points += points
        loyalty.last_earned_at = datetime.utcnow()
        
        # Create transaction record
        transaction = LoyaltyTransaction(
            tenant_id=tenant_id,
            customer_id=customer_id,
            transaction_type='earned',
            points=points,
            points_before=points_before,
            points_after=loyalty.current_points,
            invoice_id=invoice_id,
            description=description,
            base_points=base_points,
            bonus_points=bonus_points,
            invoice_amount=invoice_amount
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        return loyalty
    
    @staticmethod
    def redeem_points(customer_id, tenant_id, points, invoice_id, description):
        """Redeem points from customer account"""
        program = LoyaltyService.get_loyalty_program(tenant_id)
        loyalty = LoyaltyService.get_customer_balance(customer_id, tenant_id)
        
        # Validate
        if points < program.minimum_points_to_redeem:
            raise ValueError(f"Minimum {program.minimum_points_to_redeem} points required")
        
        if points > loyalty.current_points:
            raise ValueError(f"Insufficient points. Available: {loyalty.current_points}")
        
        if program.maximum_points_per_redemption and points > program.maximum_points_per_redemption:
            raise ValueError(f"Maximum {program.maximum_points_per_redemption} points per redemption")
        
        # Deduct points
        points_before = loyalty.current_points
        loyalty.current_points -= points
        loyalty.lifetime_redeemed_points += points
        loyalty.last_redeemed_at = datetime.utcnow()
        
        # Create transaction record
        transaction = LoyaltyTransaction(
            tenant_id=tenant_id,
            customer_id=customer_id,
            transaction_type='redeemed',
            points=-points,  # Negative for deduction
            points_before=points_before,
            points_after=loyalty.current_points,
            invoice_id=invoice_id,
            description=description
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        discount_value = LoyaltyService.calculate_redemption_value(points, tenant_id)
        
        return {
            'discount_value': discount_value,
            'new_balance': loyalty.current_points
        }
```

---

## 🎨 Frontend Implementation

### **1. Admin Loyalty Settings Page**
- Full configuration UI
- Enable/disable toggle
- All earning/redemption rules
- Threshold bonus configuration
- Preview example

### **2. Invoice Creation Updates**
- Show customer's loyalty balance
- "Apply Loyalty Discount" button
- Redemption popup
- Separate "Loyalty Discount" row in calculation

### **3. Customer Profile Updates**
- Add DOB and Anniversary fields (optional)
- Show loyalty points balance
- Show recent transactions

### **4. Admin Reports**
- Total points issued
- Total points redeemed
- Top customers by points
- Loyalty program effectiveness

---

## 📝 Implementation Order

**Day 1-2: Database & Models**
1. Create migration script
2. Create all models
3. Test migrations locally

**Day 3-4: Backend Services**
1. LoyaltyService class
2. Admin API routes (settings CRUD)
3. Customer loyalty API routes

**Day 5-7: Invoice Integration**
1. Update invoice creation to calculate points
2. Update invoice save to credit points
3. Add redemption logic
4. Test earning and redemption

**Day 8-9: Frontend - Admin**
1. Loyalty settings page
2. Admin reports
3. Customer profile updates

**Day 10-11: Frontend - Invoice**
1. Show loyalty info on invoice creation
2. Redemption UI
3. Update invoice template

**Day 12-14: Testing & Polish**
1. Test all scenarios
2. Multi-tenant testing
3. Edge cases
4. Bug fixes
5. Documentation

---

## ✅ Success Criteria (Phase 1)

- [ ] Tenant can enable/disable loyalty program
- [ ] Tenant can configure all earning/redemption rules
- [ ] Tenant can set threshold bonuses
- [ ] Customer earns points on invoice save
- [ ] Shopkeeper can redeem points during invoice creation
- [ ] Separate "Loyalty Discount" row appears on invoice
- [ ] Points balance shows on printed invoice footer (if enabled)
- [ ] Customer can see points balance in profile
- [ ] Admin reports show loyalty analytics
- [ ] Works correctly for multiple tenants
- [ ] No bugs or edge cases

---

**Let's build this! 🚀**

