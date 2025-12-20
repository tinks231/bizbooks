"""
Compare what trial balance SHOULD show vs what it ACTUALLY shows
"""

from flask import Blueprint, jsonify, g
from models import db
from sqlalchemy import text
from decimal import Decimal
from utils.tenant_middleware import require_tenant, get_current_tenant_id

compare_trial_balance_bp = Blueprint('compare_trial_balance', __name__, url_prefix='/diagnose')

@compare_trial_balance_bp.route('/trial-balance-comparison')
@require_tenant
def compare_trial_balance():
    """
    Compare account_transactions values vs what trial balance will show
    Identify which accounts are using fallback logic
    """
    
    try:
        tenant_id = get_current_tenant_id()
        
        from datetime import datetime
        import pytz
        ist = pytz.timezone('Asia/Kolkata')
        as_of_date = datetime.now(ist).date()
        
        result = {
            'tenant_id': tenant_id,
            'comparisons': []
        }
        
        # 1. Sales Income
        sales_transactions = db.session.execute(text("""
            SELECT COALESCE(SUM(credit_amount), 0)
            FROM account_transactions
            WHERE tenant_id = :tenant_id
            AND transaction_type = 'sales_income'
        """), {'tenant_id': tenant_id}).fetchone()[0]
        
        sales_invoices = db.session.execute(text("""
            SELECT COALESCE(SUM(total_amount), 0)
            FROM invoices
            WHERE tenant_id = :tenant_id
        """), {'tenant_id': tenant_id}).fetchone()[0]
        
        result['comparisons'].append({
            'account': 'Sales Income',
            'from_transactions': float(sales_transactions or 0),
            'from_fallback_table': float(sales_invoices or 0),
            'will_use': 'transactions' if sales_transactions and sales_transactions > 0 else 'FALLBACK',
            'match': abs(float(sales_transactions or 0) - float(sales_invoices or 0)) < 0.01
        })
        
        # 2. COGS
        cogs_transactions = db.session.execute(text("""
            SELECT COALESCE(SUM(debit_amount), 0)
            FROM account_transactions
            WHERE tenant_id = :tenant_id
            AND transaction_type = 'cogs'
        """), {'tenant_id': tenant_id}).fetchone()[0]
        
        cogs_reversals = db.session.execute(text("""
            SELECT COALESCE(SUM(credit_amount), 0)
            FROM account_transactions
            WHERE tenant_id = :tenant_id
            AND transaction_type = 'cogs_reversal'
        """), {'tenant_id': tenant_id}).fetchone()[0]
        
        cogs_net = Decimal(str(cogs_transactions or 0)) - Decimal(str(cogs_reversals or 0))
        
        result['comparisons'].append({
            'account': 'Cost of Goods Sold (COGS)',
            'from_transactions': float(cogs_net),
            'from_fallback_table': 'N/A (no fallback for COGS)',
            'will_use': 'transactions',
            'match': True
        })
        
        # 3. Accounts Payable
        payables_transactions = db.session.execute(text("""
            SELECT COALESCE(SUM(credit_amount - debit_amount), 0)
            FROM account_transactions
            WHERE tenant_id = :tenant_id
            AND transaction_type IN ('accounts_payable', 'accounts_payable_payment')
        """), {'tenant_id': tenant_id}).fetchone()[0]
        
        payables_bills = db.session.execute(text("""
            SELECT COALESCE(SUM(total_amount - COALESCE(paid_amount, 0)), 0)
            FROM purchase_bills
            WHERE tenant_id = :tenant_id 
            AND status = 'approved'
            AND payment_status != 'paid'
        """), {'tenant_id': tenant_id}).fetchone()[0]
        
        result['comparisons'].append({
            'account': 'Accounts Payable (Vendors)',
            'from_transactions': float(payables_transactions or 0),
            'from_fallback_table': float(payables_bills or 0),
            'will_use': 'transactions' if payables_transactions and payables_transactions > 0 else 'FALLBACK',
            'match': abs(float(payables_transactions or 0) - float(payables_bills or 0)) < 0.01
        })
        
        # 4. Operating Expenses
        opex_transactions = db.session.execute(text("""
            SELECT COALESCE(SUM(debit_amount), 0)
            FROM account_transactions
            WHERE tenant_id = :tenant_id
            AND transaction_type = 'operating_expense'
        """), {'tenant_id': tenant_id}).fetchone()[0]
        
        opex_table = db.session.execute(text("""
            SELECT COALESCE(SUM(amount), 0)
            FROM expenses
            WHERE tenant_id = :tenant_id
        """), {'tenant_id': tenant_id}).fetchone()[0]
        
        result['comparisons'].append({
            'account': 'Operating Expenses',
            'from_transactions': float(opex_transactions or 0),
            'from_fallback_table': float(opex_table or 0),
            'will_use': 'transactions' if opex_transactions and opex_transactions > 0 else 'FALLBACK',
            'match': abs(float(opex_transactions or 0) - float(opex_table or 0)) < 0.01
        })
        
        # 5. Salary Expenses
        salary_transactions = db.session.execute(text("""
            SELECT COALESCE(SUM(debit_amount), 0)
            FROM account_transactions
            WHERE tenant_id = :tenant_id
            AND transaction_type = 'salary_expense'
        """), {'tenant_id': tenant_id}).fetchone()[0]
        
        salary_table = db.session.execute(text("""
            SELECT COALESCE(SUM(salary_amount), 0)
            FROM salary_slips
            WHERE tenant_id = :tenant_id
        """), {'tenant_id': tenant_id}).fetchone()[0]
        
        result['comparisons'].append({
            'account': 'Salary Expenses',
            'from_transactions': float(salary_transactions or 0),
            'from_fallback_table': float(salary_table or 0),
            'will_use': 'transactions' if salary_transactions and salary_transactions > 0 else 'FALLBACK',
            'match': abs(float(salary_transactions or 0) - float(salary_table or 0)) < 0.01
        })
        
        # Identify mismatches
        mismatches = [c for c in result['comparisons'] if not c['match']]
        using_fallback = [c for c in result['comparisons'] if c['will_use'] == 'FALLBACK']
        
        result['summary'] = {
            'total_accounts_checked': len(result['comparisons']),
            'mismatches': len(mismatches),
            'using_fallback': len(using_fallback),
            'problem_accounts': [c['account'] for c in mismatches]
        }
        
        return jsonify({
            'status': 'success',
            'analysis': result
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

