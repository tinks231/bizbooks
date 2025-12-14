"""
Diagnose Return Amounts - Check if proportional calculation is working
"""

from flask import Blueprint, jsonify
from models import db, Return, ReturnItem
from sqlalchemy import text
from decimal import Decimal
from utils.tenant_middleware import require_tenant, get_current_tenant_id

diagnose_return_amounts_bp = Blueprint('diagnose_return_amounts', __name__, url_prefix='/migration')

@diagnose_return_amounts_bp.route('/diagnose-return-amounts')
@require_tenant
def diagnose_return_amounts():
    """Check return amounts to debug rounding issues"""
    tenant_id = get_current_tenant_id()
    
    try:
        # Get the latest return
        latest_return = Return.query.filter_by(
            tenant_id=tenant_id
        ).order_by(Return.id.desc()).first()
        
        if not latest_return:
            return jsonify({
                'status': 'error',
                'message': 'No returns found'
            })
        
        # Get return items
        items = []
        total_taxable_calc = Decimal('0')
        total_cgst_calc = Decimal('0')
        total_sgst_calc = Decimal('0')
        total_igst_calc = Decimal('0')
        total_amount_calc = Decimal('0')
        
        for item in latest_return.items:
            items.append({
                'product_name': item.product_name,
                'qty_returned': item.quantity_returned,
                'qty_sold': item.quantity_sold,
                'unit_price': float(item.unit_price),
                'taxable_amount': float(item.taxable_amount),
                'cgst_amount': float(item.cgst_amount or 0),
                'sgst_amount': float(item.sgst_amount or 0),
                'igst_amount': float(item.igst_amount or 0),
                'total_amount': float(item.total_amount)
            })
            
            total_taxable_calc += Decimal(str(item.taxable_amount))
            total_cgst_calc += Decimal(str(item.cgst_amount or 0))
            total_sgst_calc += Decimal(str(item.sgst_amount or 0))
            total_igst_calc += Decimal(str(item.igst_amount or 0))
            total_amount_calc += Decimal(str(item.total_amount))
        
        # Check accounting entries
        accounting_entries = db.session.execute(text("""
            SELECT 
                transaction_type,
                debit_amount,
                credit_amount
            FROM account_transactions
            WHERE tenant_id = :tenant_id
            AND reference_type = 'return'
            AND reference_id = :return_id
            ORDER BY transaction_type
        """), {
            'tenant_id': tenant_id,
            'return_id': latest_return.id
        }).fetchall()
        
        entries = []
        total_debits = Decimal('0')
        total_credits = Decimal('0')
        
        for entry in accounting_entries:
            debit = Decimal(str(entry[1]))
            credit = Decimal(str(entry[2]))
            entries.append({
                'type': entry[0],
                'debit': float(debit),
                'credit': float(credit)
            })
            total_debits += debit
            total_credits += credit
        
        return jsonify({
            'status': 'success',
            'return_number': latest_return.return_number,
            'return_status': latest_return.status,
            'return_header': {
                'taxable_amount': float(latest_return.taxable_amount),
                'cgst_amount': float(latest_return.cgst_amount or 0),
                'sgst_amount': float(latest_return.sgst_amount or 0),
                'igst_amount': float(latest_return.igst_amount or 0),
                'total_amount': float(latest_return.total_amount)
            },
            'calculated_totals': {
                'taxable': float(total_taxable_calc),
                'cgst': float(total_cgst_calc),
                'sgst': float(total_sgst_calc),
                'igst': float(total_igst_calc),
                'total': float(total_amount_calc)
            },
            'items': items,
            'accounting_entries': entries,
            'accounting_balance': {
                'total_debits': float(total_debits),
                'total_credits': float(total_credits),
                'difference': float(total_debits - total_credits),
                'balanced': (total_debits == total_credits)
            }
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

