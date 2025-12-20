"""
Debug: Check if cash/bank equity entries exist
"""

from flask import Blueprint, jsonify
from models import db
from sqlalchemy import text
from utils.tenant_middleware import require_tenant, get_current_tenant_id

debug_equity_bp = Blueprint('debug_equity', __name__, url_prefix='/debug')

@debug_equity_bp.route('/check-equity-entries')
@require_tenant
def check_equity_entries():
    """
    Check what equity entries exist in the database
    """
    
    try:
        tenant_id = get_current_tenant_id()
        
        # Get ALL equity entries
        all_equity = db.session.execute(text("""
            SELECT 
                id,
                transaction_date,
                transaction_type,
                debit_amount,
                credit_amount,
                narration,
                voucher_number,
                created_at
            FROM account_transactions
            WHERE tenant_id = :tenant_id
            AND transaction_type IN ('opening_balance_equity', 'opening_balance_inventory_equity')
            ORDER BY created_at DESC
        """), {'tenant_id': tenant_id}).fetchall()
        
        entries = []
        for row in all_equity:
            entries.append({
                'id': row[0],
                'date': str(row[1]),
                'type': row[2],
                'debit': float(row[3]),
                'credit': float(row[4]),
                'narration': row[5],
                'voucher': row[6],
                'created': str(row[7])
            })
        
        # Get cash/bank accounts
        accounts = db.session.execute(text("""
            SELECT 
                id,
                account_name,
                opening_balance,
                current_balance
            FROM bank_accounts
            WHERE tenant_id = :tenant_id
            AND is_active = TRUE
        """), {'tenant_id': tenant_id}).fetchall()
        
        bank_accounts = []
        for row in accounts:
            bank_accounts.append({
                'id': row[0],
                'name': row[1],
                'opening': float(row[2]),
                'current': float(row[3])
            })
        
        return jsonify({
            'status': 'success',
            'tenant_id': tenant_id,
            'equity_entries': entries,
            'total_equity_entries': len(entries),
            'bank_accounts': bank_accounts,
            'analysis': {
                'has_inventory_equity': any(e['type'] == 'opening_balance_inventory_equity' for e in entries),
                'has_cash_bank_equity': any(e['type'] == 'opening_balance_equity' for e in entries),
                'total_equity_credits': sum(e['credit'] for e in entries),
                'expected_total': sum(acc['opening'] for acc in bank_accounts) + sum(e['credit'] for e in entries if 'Inventory' in e['narration'])
            }
        })
        
    except Exception as e:
        import traceback
        return jsonify({
            'status': 'error',
            'message': str(e),
            'traceback': traceback.format_exc()
        }), 500

