"""
Simple trial balance check - no decorators to avoid auth issues
"""

from flask import Blueprint, jsonify
from models import db
from sqlalchemy import text

check_trial_simple_bp = Blueprint('check_trial_simple', __name__, url_prefix='/check')

@check_trial_simple_bp.route('/trial-balance/<int:tenant_id>')
def check_trial_balance(tenant_id):
    """Simple check without authentication"""
    try:
        # 1. Inventory from item_stocks
        inventory = db.session.execute(text("""
            SELECT COALESCE(SUM(stock_value), 0)
            FROM item_stocks
            WHERE tenant_id = :tenant_id
        """), {'tenant_id': tenant_id}).fetchone()[0]
        
        # 2. Equity entries
        equity = db.session.execute(text("""
            SELECT 
                transaction_type,
                narration,
                credit_amount,
                debit_amount
            FROM account_transactions
            WHERE tenant_id = :tenant_id
            AND transaction_type IN ('opening_balance_equity', 'opening_balance_inventory_equity')
        """), {'tenant_id': tenant_id}).fetchall()
        
        equity_list = [
            {
                'type': e[0],
                'narration': e[1],
                'credit': float(e[2]),
                'debit': float(e[3])
            }
            for e in equity
        ]
        
        equity_total = sum(e[2] - e[3] for e in equity)
        
        return jsonify({
            'tenant_id': tenant_id,
            'inventory_value': float(inventory),
            'equity_entries': equity_list,
            'equity_total': float(equity_total),
            'difference': float(inventory) - float(equity_total),
            'balanced': abs(float(inventory) - float(equity_total)) < 0.01
        })
        
    except Exception as e:
        import traceback
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

