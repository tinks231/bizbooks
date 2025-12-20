from flask import Blueprint, jsonify, g
from extensions import db
from sqlalchemy import text
from decimal import Decimal
from utils.tenant_utils import get_current_tenant_id

diagnose_return_bp = Blueprint('diagnose_return', __name__)

@diagnose_return_bp.route('/debug/diagnose-return-accounting')
def diagnose_return_accounting():
    """Diagnose return accounting entries for debugging"""
    tenant_id = get_current_tenant_id()
    
    # Get all returns for this tenant
    returns = db.session.execute(text("""
        SELECT id, return_number, total_amount, taxable_amount, 
               cgst_amount, sgst_amount, status, return_date
        FROM returns
        WHERE tenant_id = :tenant_id
        ORDER BY return_date DESC
    """), {'tenant_id': tenant_id}).fetchall()
    
    results = []
    
    for ret in returns:
        return_id = ret[0]
        return_number = ret[1]
        total_amount = Decimal(str(ret[2]))
        taxable_amount = Decimal(str(ret[3]))
        cgst_amount = Decimal(str(ret[4] or 0))
        sgst_amount = Decimal(str(ret[5] or 0))
        status = ret[6]
        return_date = ret[7]
        
        # Find all accounting entries for this return
        entries = db.session.execute(text("""
            SELECT transaction_type, debit_amount, credit_amount, narration
            FROM account_transactions
            WHERE tenant_id = :tenant_id
            AND reference_type = 'return'
            AND reference_id = :return_id
            ORDER BY transaction_type
        """), {'tenant_id': tenant_id, 'return_id': return_id}).fetchall()
        
        entry_details = []
        total_debits = Decimal('0')
        total_credits = Decimal('0')
        
        for entry in entries:
            debit = Decimal(str(entry[1] or 0))
            credit = Decimal(str(entry[2] or 0))
            total_debits += debit
            total_credits += credit
            
            entry_details.append({
                'type': entry[0],
                'debit': float(debit),
                'credit': float(credit),
                'narration': entry[3]
            })
        
        # Check if all required entries exist
        entry_types = [e['type'] for e in entry_details]
        
        required_entries = ['sales_return']
        if cgst_amount > 0:
            required_entries.append('gst_return_cgst')
        if sgst_amount > 0:
            required_entries.append('gst_return_sgst')
        required_entries.append('accounts_receivable_adjustment')
        
        missing_entries = [e for e in required_entries if e not in entry_types]
        
        is_balanced = abs(total_debits - total_credits) < Decimal('0.01')
        
        results.append({
            'return_number': return_number,
            'status': status,
            'return_date': str(return_date),
            'amounts': {
                'total': float(total_amount),
                'taxable': float(taxable_amount),
                'cgst': float(cgst_amount),
                'sgst': float(sgst_amount)
            },
            'accounting_entries': entry_details,
            'summary': {
                'total_debits': float(total_debits),
                'total_credits': float(total_credits),
                'difference': float(total_debits - total_credits),
                'is_balanced': is_balanced
            },
            'validation': {
                'required_entries': required_entries,
                'missing_entries': missing_entries,
                'has_all_entries': len(missing_entries) == 0
            }
        })
    
    return jsonify({
        'status': 'success',
        'tenant_id': tenant_id,
        'returns_count': len(returns),
        'returns': results
    })

