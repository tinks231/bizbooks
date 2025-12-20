"""
Diagnostic route to check GST entries in account_transactions
"""
from flask import Blueprint, jsonify, g
from models import db
from utils.tenant_middleware import require_tenant
from flask_login import login_required
from sqlalchemy import text

diagnose_gst_bp = Blueprint('diagnose_gst', __name__)

@diagnose_gst_bp.route('/diagnose-gst-entries', methods=['GET'])
@require_tenant
@login_required
def diagnose_gst_entries():
    """Show all GST-related entries in account_transactions"""
    tenant_id = g.tenant.id
    
    # Fetch all GST entries
    gst_entries = db.session.execute(text("""
        SELECT 
            id,
            transaction_date,
            transaction_type,
            debit_amount,
            credit_amount,
            reference_type,
            reference_id,
            voucher_number,
            narration,
            created_at
        FROM account_transactions
        WHERE tenant_id = :tenant_id
        AND (
            transaction_type LIKE '%gst%'
            OR transaction_type LIKE '%GST%'
        )
        ORDER BY transaction_date DESC, created_at DESC
    """), {'tenant_id': tenant_id}).fetchall()
    
    # Group by transaction_type
    entries_by_type = {}
    for entry in gst_entries:
        txn_type = entry.transaction_type
        if txn_type not in entries_by_type:
            entries_by_type[txn_type] = {
                'count': 0,
                'total_debit': 0,
                'total_credit': 0,
                'entries': []
            }
        
        entries_by_type[txn_type]['count'] += 1
        entries_by_type[txn_type]['total_debit'] += float(entry.debit_amount or 0)
        entries_by_type[txn_type]['total_credit'] += float(entry.credit_amount or 0)
        entries_by_type[txn_type]['entries'].append({
            'id': entry.id,
            'date': entry.transaction_date.strftime('%Y-%m-%d'),
            'debit': float(entry.debit_amount or 0),
            'credit': float(entry.credit_amount or 0),
            'reference': f"{entry.reference_type} #{entry.reference_id}" if entry.reference_id else '-',
            'voucher': entry.voucher_number,
            'narration': entry.narration,
            'created_at': entry.created_at.isoformat() if entry.created_at else None
        })
    
    # Calculate totals for trial balance
    gst_payable_total = sum(
        data['total_credit'] 
        for txn_type, data in entries_by_type.items() 
        if txn_type == 'gst_payable'
    )
    
    gst_receivable_total = sum(
        data['total_debit'] 
        for txn_type, data in entries_by_type.items() 
        if 'return' in txn_type.lower()
    )
    
    # Get what trial balance is actually reading
    trial_balance_gst = db.session.execute(text("""
        SELECT COALESCE(SUM(credit_amount), 0)
        FROM account_transactions
        WHERE tenant_id = :tenant_id
        AND transaction_type = 'gst_payable'
    """), {'tenant_id': tenant_id}).fetchone()[0]
    
    return jsonify({
        'status': 'success',
        'tenant_id': tenant_id,
        'summary': {
            'gst_payable_total': float(gst_payable_total),
            'gst_receivable_total': float(gst_receivable_total),
            'trial_balance_reads': float(trial_balance_gst or 0),
            'total_gst_types': len(entries_by_type)
        },
        'entries_by_type': {
            txn_type: {
                'count': data['count'],
                'total_debit': data['total_debit'],
                'total_credit': data['total_credit'],
                'entries': data['entries'][:10]  # Show first 10 entries per type
            }
            for txn_type, data in entries_by_type.items()
        },
        'note': 'Trial balance reads ONLY transaction_type = gst_payable'
    })

