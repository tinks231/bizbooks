"""
Special Day Bonus Service - Birthday & Anniversary Points
Automatically credits and expires special day bonus points

This service runs daily at midnight IST to:
1. Credit birthday/anniversary bonus points
2. Remove expired special day bonuses
3. Send notifications to customers
"""

from models import db
from models.customer import Customer
from models.loyalty_program import LoyaltyProgram
from models.loyalty_points import CustomerLoyaltyPoints
from models.loyalty_transaction import LoyaltyTransaction
from datetime import datetime, timedelta
import pytz

class SpecialDayBonusService:
    
    @staticmethod
    def process_all_tenants():
        """
        Process special day bonuses for all active tenants
        Called by scheduled task daily at midnight IST
        """
        from models.tenant import Tenant
        
        active_tenants = Tenant.query.filter_by(status='active').all()
        
        results = {
            'tenants_processed': 0,
            'birthday_bonuses_credited': 0,
            'anniversary_bonuses_credited': 0,
            'expired_bonuses_removed': 0,
            'notifications_sent': 0,
            'errors': []
        }
        
        for tenant in active_tenants:
            try:
                tenant_result = SpecialDayBonusService.process_tenant(tenant.id)
                results['tenants_processed'] += 1
                results['birthday_bonuses_credited'] += tenant_result.get('birthday_bonuses', 0)
                results['anniversary_bonuses_credited'] += tenant_result.get('anniversary_bonuses', 0)
                results['expired_bonuses_removed'] += tenant_result.get('expired_bonuses', 0)
                results['notifications_sent'] += tenant_result.get('notifications', 0)
            except Exception as e:
                results['errors'].append(f"Tenant {tenant.id}: {str(e)}")
        
        return results
    
    @staticmethod
    def process_tenant(tenant_id):
        """
        Process special day bonuses for a specific tenant
        1. Credit birthday bonuses
        2. Credit anniversary bonuses
        3. Remove expired bonuses from yesterday
        """
        # Get loyalty program settings
        program = LoyaltyProgram.query.filter_by(tenant_id=tenant_id, is_active=True).first()
        
        if not program:
            return {'message': 'Loyalty program not active'}
        
        # Use IST timezone
        ist = pytz.timezone('Asia/Kolkata')
        today = datetime.now(ist).date()
        
        results = {
            'birthday_bonuses': 0,
            'anniversary_bonuses': 0,
            'expired_bonuses': 0,
            'notifications': 0
        }
        
        # 1. Process birthday bonuses
        if program.enable_birthday_bonus and program.birthday_bonus_points > 0:
            birthday_result = SpecialDayBonusService._credit_birthday_bonuses(tenant_id, program, today)
            results['birthday_bonuses'] = birthday_result['credited']
            results['notifications'] += birthday_result['notified']
        
        # 2. Process anniversary bonuses
        if program.enable_anniversary_bonus and program.anniversary_bonus_points > 0:
            anniversary_result = SpecialDayBonusService._credit_anniversary_bonuses(tenant_id, program, today)
            results['anniversary_bonuses'] = anniversary_result['credited']
            results['notifications'] += anniversary_result['notified']
        
        # 3. Remove expired bonuses from yesterday
        expired_result = SpecialDayBonusService._remove_expired_bonuses(tenant_id, today)
        results['expired_bonuses'] = expired_result['removed']
        
        return results
    
    @staticmethod
    def _credit_birthday_bonuses(tenant_id, program, today):
        """Credit birthday bonuses to customers whose birthday is today"""
        
        # Find customers with birthday today
        customers = Customer.query.filter(
            Customer.tenant_id == tenant_id,
            Customer.is_active == True,
            Customer.date_of_birth != None,
            db.extract('month', Customer.date_of_birth) == today.month,
            db.extract('day', Customer.date_of_birth) == today.day
        ).all()
        
        credited_count = 0
        notified_count = 0
        ist = pytz.timezone('Asia/Kolkata')
        
        for customer in customers:
            try:
                # Check if already credited today (prevent double-crediting)
                existing_transaction = LoyaltyTransaction.query.filter(
                    LoyaltyTransaction.tenant_id == tenant_id,
                    LoyaltyTransaction.customer_id == customer.id,
                    LoyaltyTransaction.transaction_type == 'special_day_bonus',
                    LoyaltyTransaction.description.like('%Birthday%'),
                    db.func.date(LoyaltyTransaction.created_at) == today
                ).first()
                
                if existing_transaction:
                    continue  # Already credited today
                
                # Get or create loyalty record
                loyalty = CustomerLoyaltyPoints.query.filter_by(
                    tenant_id=tenant_id,
                    customer_id=customer.id
                ).first()
                
                if not loyalty:
                    loyalty = CustomerLoyaltyPoints(
                        tenant_id=tenant_id,
                        customer_id=customer.id,
                        current_points=0,
                        lifetime_earned_points=0
                    )
                    db.session.add(loyalty)
                    db.session.flush()
                
                # Credit the points
                points_before = loyalty.current_points
                loyalty.current_points += program.birthday_bonus_points
                # Don't add to lifetime (temporary bonus)
                loyalty.updated_at = datetime.now(ist)
                
                # Calculate expiry (midnight tonight IST)
                expires_at = datetime.combine(today, datetime.max.time()).replace(tzinfo=ist)
                
                # Create transaction record
                transaction = LoyaltyTransaction(
                    tenant_id=tenant_id,
                    customer_id=customer.id,
                    transaction_type='special_day_bonus',
                    points=program.birthday_bonus_points,
                    points_before=points_before,
                    points_after=loyalty.current_points,
                    description=f"🎂 Birthday Bonus - Happy Birthday {customer.name}!",
                    created_at=datetime.now(ist),
                    expires_at=expires_at,
                    is_temporary=True
                )
                db.session.add(transaction)
                
                credited_count += 1
                
                # Send notification (SMS/Email if configured)
                notification_sent = SpecialDayBonusService._send_notification(
                    customer,
                    program.birthday_bonus_points,
                    'birthday'
                )
                if notification_sent:
                    notified_count += 1
                
            except Exception as e:
                print(f"Error crediting birthday bonus for customer {customer.id}: {str(e)}")
                continue
        
        db.session.commit()
        
        return {'credited': credited_count, 'notified': notified_count}
    
    @staticmethod
    def _credit_anniversary_bonuses(tenant_id, program, today):
        """Credit anniversary bonuses to customers whose anniversary is today"""
        
        # Find customers with anniversary today
        customers = Customer.query.filter(
            Customer.tenant_id == tenant_id,
            Customer.is_active == True,
            Customer.anniversary_date != None,
            db.extract('month', Customer.anniversary_date) == today.month,
            db.extract('day', Customer.anniversary_date) == today.day
        ).all()
        
        credited_count = 0
        notified_count = 0
        ist = pytz.timezone('Asia/Kolkata')
        
        for customer in customers:
            try:
                # Check if already credited today
                existing_transaction = LoyaltyTransaction.query.filter(
                    LoyaltyTransaction.tenant_id == tenant_id,
                    LoyaltyTransaction.customer_id == customer.id,
                    LoyaltyTransaction.transaction_type == 'special_day_bonus',
                    LoyaltyTransaction.description.like('%Anniversary%'),
                    db.func.date(LoyaltyTransaction.created_at) == today
                ).first()
                
                if existing_transaction:
                    continue  # Already credited today
                
                # Get or create loyalty record
                loyalty = CustomerLoyaltyPoints.query.filter_by(
                    tenant_id=tenant_id,
                    customer_id=customer.id
                ).first()
                
                if not loyalty:
                    loyalty = CustomerLoyaltyPoints(
                        tenant_id=tenant_id,
                        customer_id=customer.id,
                        current_points=0,
                        lifetime_earned_points=0
                    )
                    db.session.add(loyalty)
                    db.session.flush()
                
                # Credit the points
                points_before = loyalty.current_points
                loyalty.current_points += program.anniversary_bonus_points
                # Don't add to lifetime (temporary bonus)
                loyalty.updated_at = datetime.now(ist)
                
                # Calculate expiry (midnight tonight IST)
                expires_at = datetime.combine(today, datetime.max.time()).replace(tzinfo=ist)
                
                # Create transaction record
                transaction = LoyaltyTransaction(
                    tenant_id=tenant_id,
                    customer_id=customer.id,
                    transaction_type='special_day_bonus',
                    points=program.anniversary_bonus_points,
                    points_before=points_before,
                    points_after=loyalty.current_points,
                    description=f"🎉 Anniversary Bonus - Happy Anniversary {customer.name}!",
                    created_at=datetime.now(ist),
                    expires_at=expires_at,
                    is_temporary=True
                )
                db.session.add(transaction)
                
                credited_count += 1
                
                # Send notification
                notification_sent = SpecialDayBonusService._send_notification(
                    customer,
                    program.anniversary_bonus_points,
                    'anniversary'
                )
                if notification_sent:
                    notified_count += 1
                
            except Exception as e:
                print(f"Error crediting anniversary bonus for customer {customer.id}: {str(e)}")
                continue
        
        db.session.commit()
        
        return {'credited': credited_count, 'notified': notified_count}
    
    @staticmethod
    def _remove_expired_bonuses(tenant_id, today):
        """Remove special day bonuses that expired yesterday (midnight passed, not used)"""
        
        ist = pytz.timezone('Asia/Kolkata')
        yesterday = today - timedelta(days=1)
        
        # Find all temporary bonuses that expired yesterday
        expired_transactions = LoyaltyTransaction.query.filter(
            LoyaltyTransaction.tenant_id == tenant_id,
            LoyaltyTransaction.transaction_type == 'special_day_bonus',
            LoyaltyTransaction.is_temporary == True,
            db.func.date(LoyaltyTransaction.expires_at) == yesterday
        ).all()
        
        removed_count = 0
        
        for transaction in expired_transactions:
            try:
                # Check if points were already used (redeemed)
                redemptions_after_bonus = LoyaltyTransaction.query.filter(
                    LoyaltyTransaction.tenant_id == tenant_id,
                    LoyaltyTransaction.customer_id == transaction.customer_id,
                    LoyaltyTransaction.transaction_type == 'redeemed',
                    LoyaltyTransaction.created_at >= transaction.created_at,
                    LoyaltyTransaction.created_at <= transaction.expires_at
                ).all()
                
                points_used = sum(abs(t.points) for t in redemptions_after_bonus)
                points_to_remove = max(0, transaction.points - points_used)
                
                if points_to_remove > 0:
                    # Remove unused bonus points
                    loyalty = CustomerLoyaltyPoints.query.filter_by(
                        tenant_id=tenant_id,
                        customer_id=transaction.customer_id
                    ).first()
                    
                    if loyalty:
                        points_before = loyalty.current_points
                        loyalty.current_points = max(0, loyalty.current_points - points_to_remove)
                        loyalty.updated_at = datetime.now(ist)
                        
                        # Create expiry transaction record
                        expiry_transaction = LoyaltyTransaction(
                            tenant_id=tenant_id,
                            customer_id=transaction.customer_id,
                            transaction_type='expired',
                            points=-points_to_remove,
                            points_before=points_before,
                            points_after=loyalty.current_points,
                            description=f"Special day bonus expired (unused)",
                            created_at=datetime.now(ist)
                        )
                        db.session.add(expiry_transaction)
                        
                        removed_count += 1
                
            except Exception as e:
                print(f"Error removing expired bonus for transaction {transaction.id}: {str(e)}")
                continue
        
        db.session.commit()
        
        return {'removed': removed_count}
    
    @staticmethod
    def _send_notification(customer, points, occasion_type):
        """
        Send notification to customer about special day bonus
        Returns True if notification sent successfully
        """
        try:
            # Format message based on occasion
            if occasion_type == 'birthday':
                message = f"🎂 Happy Birthday {customer.name}! Enjoy {points} bonus points today! Use them on your next visit. - {customer.tenant.company_name if hasattr(customer, 'tenant') else 'BizBooks'}"
            else:  # anniversary
                message = f"🎉 Happy Anniversary {customer.name}! Enjoy {points} bonus points today! Use them on your next visit. - {customer.tenant.company_name if hasattr(customer, 'tenant') else 'BizBooks'}"
            
            # If customer has phone number, send SMS
            if customer.phone:
                # TODO: Integrate with SMS service (e.g., MSG91, Twilio)
                # For now, just log it
                print(f"SMS to {customer.phone}: {message}")
                # Example: send_sms(customer.phone, message)
            
            # If customer has email, send email
            if customer.email:
                # TODO: Integrate with email service
                print(f"Email to {customer.email}: {message}")
                # Example: send_email(customer.email, f"Special Day Bonus - {occasion_type.title()}", message)
            
            return True
            
        except Exception as e:
            print(f"Error sending notification: {str(e)}")
            return False

