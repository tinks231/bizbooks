"""
Comprehensive diagnosis of ALL trial balance components
Shows what's causing the ₹11,800 difference
"""

from flask import Blueprint, jsonify, g
from models import db
from sqlalchemy import text
from decimal import Decimal
from utils.tenant_middleware import require_tenant, get_current_tenant_id

comprehensive_diagnosis_bp = Blueprint('comprehensive_diagnosis', __name__, url_prefix='/diagnose')

@comprehensive_diagnosis_bp.route('/complete-trial-balance')
@require_tenant
def comprehensive_diagnosis():
    """
    Show EVERY component of trial balance calculation
    Identify exactly where the ₹11,800 difference comes from
    """
    
    try:
        tenant_id = get_current_tenant_id()
        
        from datetime import datetime
        import pytz
        ist = pytz.timezone('Asia/Kolkata')
        as_of_date = datetime.now(ist).date()
        
        result = {
            'tenant_id': tenant_id,
            'as_of_date': str(as_of_date),
            'debit_components': {},
            'credit_components': {}
        }
        
        # === DEBIT SIDE ===
        
        # 1. Cash & Bank
        cash_bank = db.session.execute(text("""
            SELECT 
                account_name,
                account_type,
                current_balance
            FROM bank_accounts
            WHERE tenant_id = :tenant_id AND is_active = TRUE
        """), {'tenant_id': tenant_id}).fetchall()
        
        cash_bank_total = sum(Decimal(str(acc[2])) for acc in cash_bank if acc[2] > 0)
        result['debit_components']['cash_bank'] = {
            'accounts': [{'name': acc[0], 'balance': float(acc[2])} for acc in cash_bank],
            'total': float(cash_bank_total)
        }
        
        # 2. Accounts Receivable
        receivables = db.session.execute(text("""
            SELECT COALESCE(SUM(total_amount - COALESCE(paid_amount, 0)), 0)
            FROM invoices
            WHERE tenant_id = :tenant_id 
            AND payment_status != 'paid'
            AND invoice_date <= :as_of_date
        """), {'tenant_id': tenant_id, 'as_of_date': as_of_date}).fetchone()[0]
        
        result['debit_components']['accounts_receivable'] = float(receivables or 0)
        
        # 3. Inventory
        inventory = db.session.execute(text("""
            SELECT COALESCE(SUM(stock_value), 0)
            FROM item_stocks
            WHERE tenant_id = :tenant_id
        """), {'tenant_id': tenant_id}).fetchone()[0]
        
        # Also get item count
        item_count = db.session.execute(text("""
            SELECT COUNT(*) FROM items WHERE tenant_id = :tenant_id
        """), {'tenant_id': tenant_id}).fetchone()[0]
        
        result['debit_components']['inventory'] = {
            'total_value': float(inventory or 0),
            'item_count': item_count
        }
        
        # 4. ITC
        itc = db.session.execute(text("""
            SELECT COALESCE(SUM(debit_amount), 0)
            FROM account_transactions
            WHERE tenant_id = :tenant_id
            AND transaction_type = 'input_tax_credit'
            AND transaction_date <= :as_of_date
        """), {'tenant_id': tenant_id, 'as_of_date': as_of_date}).fetchone()[0]
        
        result['debit_components']['itc'] = float(itc or 0)
        
        # 5. GST Receivable on Returns
        gst_returns = db.session.execute(text("""
            SELECT COALESCE(SUM(debit_amount), 0)
            FROM account_transactions
            WHERE tenant_id = :tenant_id
            AND transaction_type IN ('gst_return_cgst', 'gst_return_sgst', 'gst_return_igst')
            AND transaction_date <= :as_of_date
        """), {'tenant_id': tenant_id, 'as_of_date': as_of_date}).fetchone()[0]
        
        result['debit_components']['gst_receivable_returns'] = float(gst_returns or 0)
        
        # 6. Commission Recoverable
        commission_recov = db.session.execute(text("""
            SELECT COALESCE(SUM(debit_amount), 0)
            FROM account_transactions
            WHERE tenant_id = :tenant_id
            AND transaction_type = 'commission_recoverable'
            AND transaction_date <= :as_of_date
        """), {'tenant_id': tenant_id, 'as_of_date': as_of_date}).fetchone()[0]
        
        result['debit_components']['commission_recoverable'] = float(commission_recov or 0)
        
        # 7. COGS
        cogs = db.session.execute(text("""
            SELECT COALESCE(SUM(debit_amount), 0)
            FROM account_transactions
            WHERE tenant_id = :tenant_id
            AND transaction_type = 'cogs'
            AND transaction_date <= :as_of_date
        """), {'tenant_id': tenant_id, 'as_of_date': as_of_date}).fetchone()[0]
        
        result['debit_components']['cogs'] = float(cogs or 0)
        
        # 8. Sales Returns
        sales_returns = db.session.execute(text("""
            SELECT COALESCE(SUM(debit_amount), 0)
            FROM account_transactions
            WHERE tenant_id = :tenant_id
            AND transaction_type = 'sales_return'
            AND transaction_date <= :as_of_date
        """), {'tenant_id': tenant_id, 'as_of_date': as_of_date}).fetchone()[0]
        
        result['debit_components']['sales_returns'] = float(sales_returns or 0)
        
        # 9. Commission Expenses
        commission_exp = db.session.execute(text("""
            SELECT COALESCE(SUM(debit_amount), 0)
            FROM account_transactions
            WHERE tenant_id = :tenant_id
            AND transaction_type = 'commission_expense'
            AND transaction_date <= :as_of_date
        """), {'tenant_id': tenant_id, 'as_of_date': as_of_date}).fetchone()[0]
        
        commission_reversal = db.session.execute(text("""
            SELECT COALESCE(SUM(credit_amount), 0)
            FROM account_transactions
            WHERE tenant_id = :tenant_id
            AND transaction_type = 'commission_reversal'
            AND transaction_date <= :as_of_date
        """), {'tenant_id': tenant_id, 'as_of_date': as_of_date}).fetchone()[0]
        
        result['debit_components']['commission_expenses'] = float(Decimal(str(commission_exp or 0)) - Decimal(str(commission_reversal or 0)))
        
        # === CREDIT SIDE ===
        
        # 1. Owner's Equity
        equity_entries = db.session.execute(text("""
            SELECT 
                transaction_type,
                narration,
                SUM(credit_amount - debit_amount) as net_credit
            FROM account_transactions
            WHERE tenant_id = :tenant_id 
            AND account_id IS NULL
            AND transaction_type IN ('opening_balance_equity', 'opening_balance_inventory_equity')
            AND transaction_date <= :as_of_date
            GROUP BY transaction_type, narration
        """), {'tenant_id': tenant_id, 'as_of_date': as_of_date}).fetchall()
        
        equity_list = []
        equity_total = Decimal('0')
        for eq in equity_entries:
            net = Decimal(str(eq[2]))
            equity_total += net
            equity_list.append({
                'type': eq[0],
                'narration': eq[1],
                'amount': float(net)
            })
        
        result['credit_components']['equity'] = {
            'entries': equity_list,
            'total': float(equity_total)
        }
        
        # 2. Sales Income
        sales = db.session.execute(text("""
            SELECT COALESCE(SUM(credit_amount), 0)
            FROM account_transactions
            WHERE tenant_id = :tenant_id
            AND transaction_type = 'sales_income'
            AND transaction_date <= :as_of_date
        """), {'tenant_id': tenant_id, 'as_of_date': as_of_date}).fetchone()[0]
        
        result['credit_components']['sales_income'] = float(sales or 0)
        
        # 3. Round-off (if negative/credit)
        round_off_credit = db.session.execute(text("""
            SELECT COALESCE(SUM(credit_amount), 0)
            FROM account_transactions
            WHERE tenant_id = :tenant_id
            AND transaction_type = 'round_off_expense'
            AND transaction_date <= :as_of_date
        """), {'tenant_id': tenant_id, 'as_of_date': as_of_date}).fetchone()[0]
        
        result['credit_components']['round_off_credit_excess'] = float(round_off_credit or 0)
        
        # === CALCULATE TOTALS ===
        total_debit = sum([
            result['debit_components']['cash_bank']['total'],
            result['debit_components']['accounts_receivable'],
            result['debit_components']['inventory']['total_value'],
            result['debit_components']['itc'],
            result['debit_components']['gst_receivable_returns'],
            result['debit_components']['commission_recoverable'],
            result['debit_components']['cogs'],
            result['debit_components']['sales_returns'],
            result['debit_components']['commission_expenses']
        ])
        
        total_credit = sum([
            result['credit_components']['equity']['total'],
            result['credit_components']['sales_income'],
            result['credit_components']['round_off_credit_excess']
        ])
        
        difference = total_debit - total_credit
        
        result['summary'] = {
            'total_debit': total_debit,
            'total_credit': total_credit,
            'difference': difference,
            'is_balanced': abs(difference) < 0.01
        }
        
        # === IDENTIFY PROBLEM ===
        problems = []
        
        # Check if inventory and equity match
        inv_value = result['debit_components']['inventory']['total_value']
        inv_equity = sum(eq['amount'] for eq in equity_list if 'Inventory' in eq['narration'])
        
        if abs(inv_value - inv_equity) > 0.01:
            problems.append(f"Inventory (₹{inv_value:,.2f}) doesn't match Inventory Equity (₹{inv_equity:,.2f})")
        
        result['problems_identified'] = problems if problems else ['Need to analyze difference manually']
        
        return jsonify({
            'status': 'success',
            'diagnosis': result
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

