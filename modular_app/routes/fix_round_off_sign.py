"""
Fix Round-Off Sign in Returns
Fixes incorrect round-off entries where negative round-offs were recorded as DEBIT instead of CREDIT
"""

from flask import Blueprint, jsonify
from models import db, Return
from sqlalchemy import text
from decimal import Decimal
import pytz
from datetime import datetime
from utils.tenant_middleware import require_tenant, get_current_tenant_id

fix_round_off_sign_bp = Blueprint('fix_round_off_sign', __name__, url_prefix='/migration')

@fix_round_off_sign_bp.route('/fix-round-off-sign')
@require_tenant
def fix_round_off_sign():
    """Fix incorrect round-off entries in returns"""
    tenant_id = get_current_tenant_id()
    
    try:
        # Get all approved returns for this tenant
        returns = Return.query.filter_by(
            tenant_id=tenant_id,
            status='approved'
        ).all()
        
        fixed_count = 0
        errors = []
        
        for ret in returns:
            try:
                # Calculate what the round-off should be
                gross_before_roundoff = Decimal(str(ret.taxable_amount)) + \
                                       Decimal(str(ret.cgst_amount or 0)) + \
                                       Decimal(str(ret.sgst_amount or 0)) + \
                                       Decimal(str(ret.igst_amount or 0))
                expected_round_off = Decimal(str(ret.total_amount)) - gross_before_roundoff
                
                if expected_round_off == 0:
                    continue  # No round-off, skip
                
                # Check if there's an existing round_off_expense entry
                existing_entry = db.session.execute(text("""
                    SELECT id, debit_amount, credit_amount
                    FROM account_transactions
                    WHERE tenant_id = :tenant_id
                    AND reference_type = 'return'
                    AND reference_id = :return_id
                    AND transaction_type = 'round_off_expense'
                """), {
                    'tenant_id': tenant_id,
                    'return_id': ret.id
                }).fetchone()
                
                if not existing_entry:
                    continue  # No round-off entry, skip
                
                entry_id = existing_entry[0]
                entry_debit = Decimal(str(existing_entry[1]))
                entry_credit = Decimal(str(existing_entry[2]))
                
                # Determine if the entry is correct
                is_correct = False
                
                if expected_round_off < 0:
                    # Negative round-off should be CREDIT
                    if entry_credit == abs(expected_round_off) and entry_debit == 0:
                        is_correct = True
                else:
                    # Positive round-off should be DEBIT
                    if entry_debit == expected_round_off and entry_credit == 0:
                        is_correct = True
                
                if is_correct:
                    continue  # Entry is correct, skip
                
                # Entry is incorrect, fix it
                print(f"Fixing {ret.return_number}: Expected round-off {expected_round_off}, found DEBIT {entry_debit} CREDIT {entry_credit}")
                
                # Delete the incorrect entry
                db.session.execute(text("""
                    DELETE FROM account_transactions
                    WHERE id = :entry_id
                """), {'entry_id': entry_id})
                
                # Create the correct entry
                ist = pytz.timezone('Asia/Kolkata')
                now = datetime.now(ist)
                
                if expected_round_off < 0:
                    # Negative round-off: CREDIT entry
                    db.session.execute(text("""
                        INSERT INTO account_transactions
                        (tenant_id, account_id, transaction_date, transaction_type,
                         debit_amount, credit_amount, balance_after, reference_type, reference_id,
                         voucher_number, narration, created_at, created_by)
                        VALUES (:tenant_id, NULL, :transaction_date, 'round_off_expense',
                                0.00, :credit_amount, 0.00, 'return', :return_id,
                                :voucher, :narration, :created_at, NULL)
                    """), {
                        'tenant_id': tenant_id,
                        'transaction_date': ret.return_date,
                        'credit_amount': float(abs(expected_round_off)),
                        'return_id': ret.id,
                        'voucher': ret.return_number,
                        'narration': f'Round-off adjustment (negative) on return {ret.return_number} [CORRECTED]',
                        'created_at': now
                    })
                else:
                    # Positive round-off: DEBIT entry
                    db.session.execute(text("""
                        INSERT INTO account_transactions
                        (tenant_id, account_id, transaction_date, transaction_type,
                         debit_amount, credit_amount, balance_after, reference_type, reference_id,
                         voucher_number, narration, created_at, created_by)
                        VALUES (:tenant_id, NULL, :transaction_date, 'round_off_expense',
                                :debit_amount, 0.00, :debit_amount, 'return', :return_id,
                                :voucher, :narration, :created_at, NULL)
                    """), {
                        'tenant_id': tenant_id,
                        'transaction_date': ret.return_date,
                        'debit_amount': float(expected_round_off),
                        'return_id': ret.id,
                        'voucher': ret.return_number,
                        'narration': f'Round-off adjustment (positive) on return {ret.return_number} [CORRECTED]',
                        'created_at': now
                    })
                
                fixed_count += 1
                print(f"  ✅ Fixed {ret.return_number}")
                
            except Exception as e:
                error_msg = f"Error fixing {ret.return_number}: {str(e)}"
                print(f"  ❌ {error_msg}")
                errors.append(error_msg)
                continue
        
        # Commit all changes
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'total_returns_checked': len(returns),
            'returns_fixed': fixed_count,
            'errors': errors,
            'message': f'Fixed {fixed_count} return(s) with incorrect round-off sign'
        })
        
    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

