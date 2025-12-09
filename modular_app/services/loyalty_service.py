"""
Loyalty Service
Core business logic for loyalty program
"""
from models import db
from models.loyalty_program import LoyaltyProgram
from models.customer_loyalty_points import CustomerLoyaltyPoints
from models.loyalty_transaction import LoyaltyTransaction
from datetime import datetime

class LoyaltyService:
    
    @staticmethod
    def get_loyalty_program(tenant_id):
        """Get loyalty program settings for tenant"""
        return LoyaltyProgram.query.filter_by(tenant_id=tenant_id).first()
    
    @staticmethod
    def is_active(tenant_id):
        """Check if loyalty program is active for tenant"""
        program = LoyaltyService.get_loyalty_program(tenant_id)
        return program and program.is_active
    
    @staticmethod
    def calculate_points_earned(invoice_amount, tenant_id):
        """
        Calculate points earned for an invoice
        Returns dict with base_points, bonus_points, and total_points
        """
        program = LoyaltyService.get_loyalty_program(tenant_id)
        
        if not program or not program.is_active:
            return {'base_points': 0, 'bonus_points': 0, 'total_points': 0}
        
        # Check minimum purchase requirement
        if invoice_amount < float(program.minimum_purchase_for_points or 0):
            return {'base_points': 0, 'bonus_points': 0, 'total_points': 0}
        
        # Base points calculation
        base_points = int((invoice_amount / 100) * float(program.points_per_100_rupees))
        
        # Apply maximum points cap if set
        if program.maximum_points_per_invoice and base_points > program.maximum_points_per_invoice:
            base_points = program.maximum_points_per_invoice
        
        # Calculate threshold bonus
        bonus_points = 0
        if program.enable_threshold_bonuses:
            # Check highest threshold first
            if program.threshold_3_amount and invoice_amount >= float(program.threshold_3_amount):
                bonus_points = program.threshold_3_bonus_points or 0
            elif program.threshold_2_amount and invoice_amount >= float(program.threshold_2_amount):
                bonus_points = program.threshold_2_bonus_points or 0
            elif program.threshold_1_amount and invoice_amount >= float(program.threshold_1_amount):
                bonus_points = program.threshold_1_bonus_points or 0
        
        total_points = base_points + bonus_points
        
        return {
            'base_points': base_points,
            'bonus_points': bonus_points,
            'total_points': total_points
        }
    
    @staticmethod
    def calculate_redemption_value(points, tenant_id):
        """
        Calculate discount value when redeeming points
        Returns the discount amount in rupees
        """
        program = LoyaltyService.get_loyalty_program(tenant_id)
        
        if not program or not program.is_active:
            return 0
        
        return float(points) * float(program.points_to_rupees_ratio)
    
    @staticmethod
    def get_customer_balance(customer_id, tenant_id, auto_create=True):
        """
        Get customer's current points balance
        Creates loyalty record if doesn't exist
        """
        loyalty = CustomerLoyaltyPoints.query.filter_by(
            customer_id=customer_id,
            tenant_id=tenant_id
        ).first()
        
        if not loyalty and auto_create:
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
    def credit_points(customer_id, tenant_id, points, invoice_id, invoice_number, 
                     description, base_points=0, bonus_points=0, invoice_amount=0, created_by=None):
        """
        Credit points to customer account
        Returns updated loyalty record
        """
        loyalty = LoyaltyService.get_customer_balance(customer_id, tenant_id, auto_create=True)
        
        points_before = loyalty.current_points
        loyalty.current_points += points
        loyalty.lifetime_earned_points += points
        loyalty.last_earned_at = datetime.utcnow()
        loyalty.updated_at = datetime.utcnow()
        
        # Create transaction record
        transaction = LoyaltyTransaction(
            tenant_id=tenant_id,
            customer_id=customer_id,
            transaction_type='earned',
            points=points,
            points_before=points_before,
            points_after=loyalty.current_points,
            invoice_id=invoice_id,
            invoice_number=invoice_number,
            description=description,
            base_points=base_points,
            bonus_points=bonus_points,
            invoice_amount=invoice_amount,
            created_by=created_by
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        return loyalty
    
    @staticmethod
    def redeem_points(customer_id, tenant_id, points, invoice_id, invoice_number, 
                     description, invoice_subtotal=0, created_by=None):
        """
        Redeem points from customer account
        Returns dict with discount_value and new_balance
        Raises ValueError if validation fails
        """
        program = LoyaltyService.get_loyalty_program(tenant_id)
        loyalty = LoyaltyService.get_customer_balance(customer_id, tenant_id, auto_create=False)
        
        if not loyalty:
            raise ValueError("Customer has no loyalty account")
        
        if not program or not program.is_active:
            raise ValueError("Loyalty program is not active")
        
        # Validate minimum points
        if points < (program.minimum_points_to_redeem or 10):
            raise ValueError(f"Minimum {program.minimum_points_to_redeem or 10} points required to redeem")
        
        # Validate sufficient balance
        if points > loyalty.current_points:
            raise ValueError(f"Insufficient points. Available: {loyalty.current_points}")
        
        # Validate maximum points per redemption
        if program.maximum_points_per_redemption and points > program.maximum_points_per_redemption:
            raise ValueError(f"Maximum {program.maximum_points_per_redemption} points per redemption")
        
        # Calculate discount value
        discount_value = LoyaltyService.calculate_redemption_value(points, tenant_id)
        
        # Validate maximum discount percent (if set)
        if program.maximum_discount_percent and invoice_subtotal > 0:
            max_discount = invoice_subtotal * (float(program.maximum_discount_percent) / 100)
            if discount_value > max_discount:
                raise ValueError(f"Discount exceeds maximum {program.maximum_discount_percent}% of invoice")
        
        # Deduct points
        points_before = loyalty.current_points
        loyalty.current_points -= points
        loyalty.lifetime_redeemed_points += points
        loyalty.last_redeemed_at = datetime.utcnow()
        loyalty.updated_at = datetime.utcnow()
        
        # Create transaction record
        transaction = LoyaltyTransaction(
            tenant_id=tenant_id,
            customer_id=customer_id,
            transaction_type='redeemed',
            points=-points,  # Negative for deduction
            points_before=points_before,
            points_after=loyalty.current_points,
            invoice_id=invoice_id,
            invoice_number=invoice_number,
            description=description,
            created_by=created_by
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        return {
            'discount_value': discount_value,
            'new_balance': loyalty.current_points,
            'points_redeemed': points
        }
    
    @staticmethod
    def get_transaction_history(customer_id, tenant_id, limit=50):
        """
        Get customer's loyalty transaction history
        Returns list of transaction objects, newest first
        """
        transactions = LoyaltyTransaction.query.filter_by(
            customer_id=customer_id,
            tenant_id=tenant_id
        ).order_by(LoyaltyTransaction.created_at.desc()).limit(limit).all()
        
        return transactions  # Return objects, not dicts, for template access
    
    @staticmethod
    def get_loyalty_stats(tenant_id):
        """
        Get overall loyalty program statistics for tenant
        Returns dict with key metrics
        """
        program = LoyaltyService.get_loyalty_program(tenant_id)
        
        if not program:
            return None
        
        # Total members (customers with loyalty accounts)
        total_members = CustomerLoyaltyPoints.query.filter_by(tenant_id=tenant_id).count()
        
        # Active members (earned or redeemed in last 90 days)
        from datetime import timedelta
        ninety_days_ago = datetime.utcnow() - timedelta(days=90)
        active_members = CustomerLoyaltyPoints.query.filter(
            CustomerLoyaltyPoints.tenant_id == tenant_id
        ).filter(
            db.or_(
                CustomerLoyaltyPoints.last_earned_at >= ninety_days_ago,
                CustomerLoyaltyPoints.last_redeemed_at >= ninety_days_ago
            )
        ).count()
        
        # Total points issued
        total_issued_result = db.session.query(
            db.func.sum(CustomerLoyaltyPoints.lifetime_earned_points)
        ).filter_by(tenant_id=tenant_id).scalar()
        total_points_issued = int(total_issued_result or 0)
        
        # Total points redeemed
        total_redeemed_result = db.session.query(
            db.func.sum(CustomerLoyaltyPoints.lifetime_redeemed_points)
        ).filter_by(tenant_id=tenant_id).scalar()
        total_points_redeemed = int(total_redeemed_result or 0)
        
        # Outstanding points
        outstanding_result = db.session.query(
            db.func.sum(CustomerLoyaltyPoints.current_points)
        ).filter_by(tenant_id=tenant_id).scalar()
        outstanding_points = int(outstanding_result or 0)
        
        # Top 10 customers by points
        top_customers = CustomerLoyaltyPoints.query.filter_by(
            tenant_id=tenant_id
        ).order_by(CustomerLoyaltyPoints.current_points.desc()).limit(10).all()
        
        return {
            'is_active': program.is_active,
            'total_members': total_members,
            'active_members': active_members,
            'total_points_issued': total_points_issued,
            'total_points_redeemed': total_points_redeemed,
            'outstanding_points': outstanding_points,
            'redemption_rate': round((total_points_redeemed / total_points_issued * 100), 2) if total_points_issued > 0 else 0,
            'top_customers': [{'customer_id': c.customer_id, 'points': c.current_points} for c in top_customers]
        }
    
    @staticmethod
    def adjust_points(customer_id, tenant_id, points, description, created_by=None):
        """
        Manually adjust customer points (for corrections/bonuses)
        points can be positive (add) or negative (subtract)
        """
        loyalty = LoyaltyService.get_customer_balance(customer_id, tenant_id, auto_create=True)
        
        points_before = loyalty.current_points
        loyalty.current_points += points
        
        if points > 0:
            loyalty.lifetime_earned_points += points
        else:
            loyalty.lifetime_redeemed_points += abs(points)
        
        loyalty.updated_at = datetime.utcnow()
        
        # Create transaction record
        transaction = LoyaltyTransaction(
            tenant_id=tenant_id,
            customer_id=customer_id,
            transaction_type='adjusted',
            points=points,
            points_before=points_before,
            points_after=loyalty.current_points,
            description=description,
            created_by=created_by
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        return loyalty

