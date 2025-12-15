"""
Accounting Helper Functions
Utilities for double-entry bookkeeping, rounding, and auto-balancing
"""

from decimal import Decimal, ROUND_HALF_UP
from sqlalchemy import text
from models import db
from datetime import datetime
import pytz


def round_currency(amount):
    """
    Round amount to 2 decimal places (standard currency precision)
    Uses ROUND_HALF_UP (banker's rounding) for consistency
    
    Args:
        amount: Decimal, float, or numeric value
    
    Returns:
        Decimal rounded to 2 decimal places
    """
    if amount is None:
        return Decimal('0.00')
    
    decimal_amount = Decimal(str(amount))
    return decimal_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def round_to_whole_number(amount):
    """
    Round amount to nearest whole number (no paisa)
    Uses ROUND_HALF_UP: 0.5 and above rounds up, below 0.5 rounds down
    
    Examples:
        29.98 → 30 (0.98 ≥ 0.5)
        19.99 → 20 (0.99 ≥ 0.5)
        1999.47 → 1999 (0.47 < 0.5)
        1999.67 → 2000 (0.67 ≥ 0.5)
    
    Args:
        amount: Decimal, float, or numeric value
    
    Returns:
        Decimal rounded to whole number
    """
    if amount is None:
        return Decimal('0')
    
    decimal_amount = Decimal(str(amount))
    return decimal_amount.quantize(Decimal('1'), rounding=ROUND_HALF_UP)


def calculate_commission(invoice_amount, commission_percentage, round_to_whole=True):
    """
    Calculate commission amount with proper rounding
    
    Args:
        invoice_amount: Invoice total (Decimal or float)
        commission_percentage: Commission % (Decimal or float)
        round_to_whole: If True, rounds to nearest rupee (default for cash businesses)
    
    Returns:
        Decimal commission amount (whole number if round_to_whole=True)
    """
    amount = Decimal(str(invoice_amount))
    percentage = Decimal(str(commission_percentage))
    
    commission = (amount * percentage) / Decimal('100')
    
    if round_to_whole:
        return round_to_whole_number(commission)
    else:
        return round_currency(commission)


def auto_balance_trial_balance(tenant_id, transaction_ref, max_diff=Decimal('1.00')):
    """
    Automatically balance Trial Balance if difference is less than max_diff
    This handles cumulative rounding errors from multiple transactions
    
    Args:
        tenant_id: Tenant ID
        transaction_ref: Reference string for audit trail (e.g., "INV-2025-0001")
        max_diff: Maximum difference to auto-balance (default ₹1.00)
    
    Returns:
        dict with status and balance_adjustment_amount
    """
    try:
        # Calculate total debits
        total_debits_result = db.session.execute(text("""
            SELECT COALESCE(SUM(debit_amount), 0) as total
            FROM account_transactions
            WHERE tenant_id = :tenant_id
        """), {'tenant_id': tenant_id}).fetchone()
        
        total_debits = Decimal(str(total_debits_result[0] if total_debits_result else 0))
        
        # Calculate total credits
        total_credits_result = db.session.execute(text("""
            SELECT COALESCE(SUM(credit_amount), 0) as total
            FROM account_transactions
            WHERE tenant_id = :tenant_id
        """), {'tenant_id': tenant_id}).fetchone()
        
        total_credits = Decimal(str(total_credits_result[0] if total_credits_result else 0))
        
        # Calculate difference
        difference = total_debits - total_credits
        
        # If balanced or difference > max_diff, no action needed
        if abs(difference) == 0:
            return {
                'status': 'balanced',
                'difference': float(difference),
                'adjustment_made': False
            }
        
        if abs(difference) > max_diff:
            return {
                'status': 'out_of_balance',
                'difference': float(difference),
                'adjustment_made': False,
                'message': f'Difference (₹{abs(difference)}) exceeds max_diff (₹{max_diff})'
            }
        
        # Auto-balance: Create adjustment entry
        ist = pytz.timezone('Asia/Kolkata')
        now = datetime.now(ist)
        
        if difference > 0:
            # Debits > Credits: Add CREDIT to Owner's Equity
            db.session.execute(text("""
                INSERT INTO account_transactions
                (tenant_id, account_id, transaction_date, transaction_type,
                 debit_amount, credit_amount, balance_after, reference_type, reference_id,
                 voucher_number, narration, created_at, created_by)
                VALUES (:tenant_id, NULL, :transaction_date, 'opening_balance_equity',
                        0.00, :credit_amount, 0.00, NULL, NULL,
                        :voucher, :narration, :created_at, NULL)
            """), {
                'tenant_id': tenant_id,
                'transaction_date': now.date(),
                'credit_amount': float(abs(difference)),
                'voucher': f'AUTO-BAL-{now.strftime("%Y%m%d%H%M%S")}',
                'narration': f'Auto-balance: Rounding adjustment for {transaction_ref}',
                'created_at': now
            })
            
            print(f"✅ Auto-balanced: Added ₹{abs(difference):.2f} CREDIT to Owner's Equity")
            
        else:
            # Credits > Debits: Add DEBIT to Owner's Equity
            db.session.execute(text("""
                INSERT INTO account_transactions
                (tenant_id, account_id, transaction_date, transaction_type,
                 debit_amount, credit_amount, balance_after, reference_type, reference_id,
                 voucher_number, narration, created_at, created_by)
                VALUES (:tenant_id, NULL, :transaction_date, 'opening_balance_equity',
                        :debit_amount, 0.00, :debit_amount, NULL, NULL,
                        :voucher, :narration, :created_at, NULL)
            """), {
                'tenant_id': tenant_id,
                'transaction_date': now.date(),
                'debit_amount': float(abs(difference)),
                'voucher': f'AUTO-BAL-{now.strftime("%Y%m%d%H%M%S")}',
                'narration': f'Auto-balance: Rounding adjustment for {transaction_ref}',
                'created_at': now
            })
            
            print(f"✅ Auto-balanced: Added ₹{abs(difference):.2f} DEBIT to Owner's Equity")
        
        db.session.commit()
        
        return {
            'status': 'balanced',
            'difference': float(difference),
            'adjustment_made': True,
            'adjustment_amount': float(abs(difference))
        }
        
    except Exception as e:
        print(f"❌ Auto-balance error: {str(e)}")
        return {
            'status': 'error',
            'message': str(e),
            'adjustment_made': False
        }

