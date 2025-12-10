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
    def calculate_points_earned(invoice_amount, tenant_id, customer_id=None):
        """
        Calculate points earned for an invoice
        Returns dict with base_points, bonus_points, total_points, and tier_multiplier
        If customer_id is provided, applies tier-based earning multiplier
        """
        program = LoyaltyService.get_loyalty_program(tenant_id)
        
        if not program or not program.is_active:
            return {'base_points': 0, 'bonus_points': 0, 'total_points': 0, 'tier_multiplier': 1.0}
        
        # Check minimum purchase requirement
        if invoice_amount < float(program.minimum_purchase_for_points or 0):
            return {'base_points': 0, 'bonus_points': 0, 'total_points': 0, 'tier_multiplier': 1.0}
        
        # Get tier multiplier if tiers are enabled and customer provided
        tier_multiplier = 1.0
        if customer_id and program.enable_membership_tiers:
            loyalty = LoyaltyService.get_customer_balance(customer_id, tenant_id, auto_create=False)
            if loyalty:
                tier_info = LoyaltyService.calculate_customer_tier(loyalty.lifetime_earned_points, tenant_id)
                if tier_info:
                    # Get the earning multiplier for this tier
                    tier_level = tier_info['tier_level']
                    if tier_level == 4:  # Platinum
                        tier_multiplier = float(program.tier_platinum_earning_multiplier or 2.0)
                    elif tier_level == 3:  # Gold
                        tier_multiplier = float(program.tier_gold_earning_multiplier or 1.5)
                    elif tier_level == 2:  # Silver
                        tier_multiplier = float(program.tier_silver_earning_multiplier or 1.2)
                    else:  # Bronze (tier_level == 1)
                        tier_multiplier = float(program.tier_bronze_earning_multiplier or 1.0)
        
        # Base points calculation
        base_points = int((invoice_amount / 100) * float(program.points_per_100_rupees))
        
        # Apply tier multiplier to base points
        base_points = int(base_points * tier_multiplier)
        
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
            'total_points': total_points,
            'tier_multiplier': tier_multiplier
        }
    
    @staticmethod
    def calculate_redemption_value(points, tenant_id, customer_id=None):
        """
        Calculate discount value when redeeming points
        Returns the discount amount in rupees
        If customer_id is provided, applies tier-based redemption multiplier (higher tiers get better value!)
        """
        program = LoyaltyService.get_loyalty_program(tenant_id)
        
        if not program or not program.is_active:
            return 0
        
        # Base redemption value
        base_value = float(points) * float(program.points_to_rupees_ratio)
        
        # Get tier multiplier if tiers are enabled and customer provided
        tier_multiplier = 1.0
        if customer_id and program.enable_membership_tiers:
            loyalty = LoyaltyService.get_customer_balance(customer_id, tenant_id, auto_create=False)
            if loyalty:
                tier_info = LoyaltyService.calculate_customer_tier(loyalty.lifetime_earned_points, tenant_id)
                if tier_info:
                    # Get the redemption multiplier for this tier
                    tier_level = tier_info['tier_level']
                    if tier_level == 4:  # Platinum
                        tier_multiplier = float(program.tier_platinum_redemption_multiplier or 1.5)
                    elif tier_level == 3:  # Gold
                        tier_multiplier = float(program.tier_gold_redemption_multiplier or 1.25)
                    elif tier_level == 2:  # Silver
                        tier_multiplier = float(program.tier_silver_redemption_multiplier or 1.1)
                    else:  # Bronze (tier_level == 1)
                        tier_multiplier = float(program.tier_bronze_redemption_multiplier or 1.0)
        
        # Apply tier multiplier to give higher tiers better redemption value
        return base_value * tier_multiplier
    
    @staticmethod
    def get_tier_max_discount_percent(customer_id, tenant_id):
        """
        Get the maximum discount percentage for customer's tier
        Returns tier-specific max discount if set, otherwise global max discount
        """
        program = LoyaltyService.get_loyalty_program(tenant_id)
        
        if not program or not program.is_active or not program.enable_membership_tiers:
            return float(program.maximum_discount_percent) if program and program.maximum_discount_percent else None
        
        loyalty = LoyaltyService.get_customer_balance(customer_id, tenant_id, auto_create=False)
        if not loyalty:
            return float(program.maximum_discount_percent) if program.maximum_discount_percent else None
        
        tier_info = LoyaltyService.calculate_customer_tier(loyalty.lifetime_earned_points, tenant_id)
        if not tier_info:
            return float(program.maximum_discount_percent) if program.maximum_discount_percent else None
        
        # Check tier-specific max discount (overrides global if set)
        tier_level = tier_info['tier_level']
        tier_max = None
        
        if tier_level == 4:  # Platinum
            tier_max = program.tier_platinum_max_discount_percent
        elif tier_level == 3:  # Gold
            tier_max = program.tier_gold_max_discount_percent
        elif tier_level == 2:  # Silver
            tier_max = program.tier_silver_max_discount_percent
        else:  # Bronze
            tier_max = program.tier_bronze_max_discount_percent
        
        # Return tier-specific if set, otherwise fall back to global
        if tier_max:
            return float(tier_max)
        return float(program.maximum_discount_percent) if program.maximum_discount_percent else None
    
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
        
        # Update customer tier if tiers are enabled
        LoyaltyService.update_customer_tier(customer_id, tenant_id)
        
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
        
        # Calculate discount value (with tier-based redemption multiplier if applicable)
        discount_value = LoyaltyService.calculate_redemption_value(points, tenant_id, customer_id)
        
        # Validate maximum discount percent (use tier-specific if set, otherwise global)
        tier_max_discount = LoyaltyService.get_tier_max_discount_percent(customer_id, tenant_id)
        if tier_max_discount and invoice_subtotal > 0:
            max_discount = invoice_subtotal * (tier_max_discount / 100)
            if discount_value > max_discount:
                raise ValueError(f"Discount exceeds maximum {tier_max_discount}% of invoice for your tier")
        
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
    
    @staticmethod
    def calculate_customer_tier(lifetime_earned_points, tenant_id):
        """
        Calculate customer's membership tier based on lifetime earned points
        Returns dict with tier_name, tier_icon, and tier_color
        """
        program = LoyaltyService.get_loyalty_program(tenant_id)
        
        if not program or not program.enable_membership_tiers:
            return None
        
        # Determine tier based on thresholds (highest tier first)
        if lifetime_earned_points >= (program.tier_platinum_min_points or 10000):
            return {
                'tier_name': program.tier_platinum_name or 'Platinum',
                'tier_icon': '💎',
                'tier_color': '#e5e7eb',  # Platinum/Silver color
                'tier_level': 4
            }
        elif lifetime_earned_points >= (program.tier_gold_min_points or 5000):
            return {
                'tier_name': program.tier_gold_name or 'Gold',
                'tier_icon': '🥇',
                'tier_color': '#f59e0b',  # Gold color
                'tier_level': 3
            }
        elif lifetime_earned_points >= (program.tier_silver_min_points or 1000):
            return {
                'tier_name': program.tier_silver_name or 'Silver',
                'tier_icon': '🥈',
                'tier_color': '#9ca3af',  # Silver color
                'tier_level': 2
            }
        else:
            return {
                'tier_name': program.tier_bronze_name or 'Bronze',
                'tier_icon': '🥉',
                'tier_color': '#cd7f32',  # Bronze color
                'tier_level': 1
            }
    
    @staticmethod
    def update_customer_tier(customer_id, tenant_id):
        """
        Update customer's tier based on their current lifetime points
        Called automatically when points are earned
        """
        loyalty = LoyaltyService.get_customer_balance(customer_id, tenant_id, auto_create=False)
        
        if not loyalty:
            return None
        
        tier_info = LoyaltyService.calculate_customer_tier(loyalty.lifetime_earned_points, tenant_id)
        
        if tier_info:
            old_tier = loyalty.tier_level
            loyalty.tier_level = tier_info['tier_name'].lower()
            loyalty.tier_updated_at = datetime.utcnow()
            db.session.commit()
            
            # Return True if tier changed (for notifications)
            return tier_info['tier_name'] if old_tier != loyalty.tier_level else None
        
        return None
    
    @staticmethod
    def check_special_day_bonus(customer_id, tenant_id):
        """
        Check if customer has birthday or anniversary bonus today
        Returns dict with bonus_points and reason (or None)
        Uses IST timezone for Indian customers
        """
        from models.customer import Customer
        import pytz
        
        program = LoyaltyService.get_loyalty_program(tenant_id)
        customer = Customer.query.filter_by(id=customer_id, tenant_id=tenant_id).first()
        
        if not program or not customer:
            return None
        
        # Use IST timezone for Indian customers
        ist = pytz.timezone('Asia/Kolkata')
        today = datetime.now(ist).date()
        
        # Check birthday bonus
        if (program.enable_birthday_bonus and 
            customer.date_of_birth and 
            customer.date_of_birth.month == today.month and 
            customer.date_of_birth.day == today.day and
            program.birthday_bonus_points > 0):
            return {
                'bonus_points': program.birthday_bonus_points,
                'reason': 'birthday',
                'message': f'🎂 Happy Birthday! You have {program.birthday_bonus_points} bonus points today!',
                'expires_at': 'midnight tonight'
            }
        
        # Check anniversary bonus
        if (program.enable_anniversary_bonus and 
            customer.anniversary_date and 
            customer.anniversary_date.month == today.month and 
            customer.anniversary_date.day == today.day and
            program.anniversary_bonus_points > 0):
            return {
                'bonus_points': program.anniversary_bonus_points,
                'reason': 'anniversary',
                'message': f'🎉 Happy Anniversary! You have {program.anniversary_bonus_points} bonus points today!',
                'expires_at': 'midnight tonight'
            }
        
        return None
    
    @staticmethod
    def get_customer_available_points(customer_id, tenant_id):
        """
        Get customer's total available points including any temporary bonuses
        Returns dict with regular_points, bonus_points, total_points, and bonus_info
        """
        loyalty = LoyaltyService.get_customer_balance(customer_id, tenant_id, auto_create=False)
        
        if not loyalty:
            return {
                'regular_points': 0,
                'bonus_points': 0,
                'total_points': 0,
                'bonus_info': None
            }
        
        regular_points = loyalty.current_points
        bonus_info = LoyaltyService.check_special_day_bonus(customer_id, tenant_id)
        bonus_points = bonus_info['bonus_points'] if bonus_info else 0
        
        return {
            'regular_points': regular_points,
            'bonus_points': bonus_points,
            'total_points': regular_points + bonus_points,
            'bonus_info': bonus_info
        }

