from flask import Blueprint, jsonify, render_template_string
from models import db
from utils.tenant_middleware import require_tenant, get_current_tenant_id
from sqlalchemy import text
from decimal import Decimal
from datetime import datetime
import pytz

fix_unpaid_return_bp = Blueprint('fix_unpaid_return', __name__)

@fix_unpaid_return_bp.route('/migration/fix-unpaid-return-entries', methods=['GET'])
@require_tenant
def show_fix_page():
    """Show page with button to run migration"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Fix Unpaid Return Entries</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
            .button { background: #27ae60; color: white; padding: 15px 30px; border: none; border-radius: 5px; 
                     font-size: 16px; cursor: pointer; text-decoration: none; display: inline-block; }
            .button:hover { background: #229954; }
            .info { background: #e8f5e9; padding: 15px; border-radius: 5px; margin: 20px 0; }
            .warning { background: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #ffc107; }
        </style>
    </head>
    <body>
        <h1>🔧 Fix Unpaid Return Accounting Entries</h1>
        
        <div class="warning">
            <h3>⚠️ What This Does:</h3>
            <p>This migration adds MISSING accounting entries for unpaid invoice returns:</p>
            <ul>
                <li><strong>DEBIT</strong> Sales Returns (reduces income)</li>
                <li><strong>DEBIT</strong> GST Receivable - CGST (govt owes back)</li>
                <li><strong>DEBIT</strong> GST Receivable - SGST (govt owes back)</li>
            </ul>
            <p><strong>This will fix the trial balance imbalance!</strong></p>
        </div>
        
        <div class="info">
            <h3>✅ Safe to Run:</h3>
            <ul>
                <li>Only affects APPROVED returns for UNPAID invoices</li>
                <li>Only adds missing entries (won't duplicate)</li>
                <li>Trial balance will be balanced after running</li>
            </ul>
        </div>
        
        <form method="POST" action="/migration/fix-unpaid-return-entries" 
              onsubmit="return confirm('Run migration to fix unpaid return entries?');">
            <button type="submit" class="button">🚀 Run Migration</button>
        </form>
        
        <p style="margin-top: 30px; color: #666;">
            <a href="/admin/accounts/reports/trial-balance">← Back to Trial Balance</a>
        </p>
    </body>
    </html>
    """
    return render_template_string(html)

@fix_unpaid_return_bp.route('/migration/fix-unpaid-return-entries', methods=['POST'])
@require_tenant
def fix_unpaid_return_entries():
    """Add missing accounting entries for unpaid invoice returns"""
    tenant_id = get_current_tenant_id()
    
    try:
        # Find all APPROVED returns for UNPAID invoices
        returns = db.session.execute(text("""
            SELECT r.id, r.return_number, r.return_date, r.total_amount, 
                   r.taxable_amount, r.cgst_amount, r.sgst_amount, r.igst_amount,
                   i.payment_status
            FROM returns r
            JOIN invoices i ON r.invoice_id = i.id
            WHERE r.tenant_id = :tenant_id
            AND r.status = 'approved'
            AND i.payment_status IN ('unpaid', 'partial')
        """), {'tenant_id': tenant_id}).fetchall()
        
        fixed_count = 0
        ist = pytz.timezone('Asia/Kolkata')
        now = datetime.now(ist)
        
        for ret in returns:
            return_id = ret[0]
            return_number = ret[1]
            return_date = ret[2]
            total_amount = Decimal(str(ret[3]))
            taxable_amount = Decimal(str(ret[4]))
            cgst_amount = Decimal(str(ret[5] or 0))
            sgst_amount = Decimal(str(ret[6] or 0))
            igst_amount = Decimal(str(ret[7] or 0))
            
            # Check if Sales Returns entry already exists
            existing_sales_return = db.session.execute(text("""
                SELECT id FROM account_transactions
                WHERE tenant_id = :tenant_id
                AND reference_type = 'return'
                AND reference_id = :return_id
                AND transaction_type = 'sales_return'
            """), {'tenant_id': tenant_id, 'return_id': return_id}).fetchone()
            
            if existing_sales_return:
                print(f"⏭️  Skipping {return_number} - already has Sales Returns entry")
                continue
            
            print(f"\n🔧 Fixing {return_number}...")
            
            # Entry 1: DEBIT Sales Returns
            db.session.execute(text("""
                INSERT INTO account_transactions
                (tenant_id, account_id, transaction_date, transaction_type,
                 debit_amount, credit_amount, balance_after, reference_type, reference_id,
                 voucher_number, narration, created_at, created_by)
                VALUES (:tenant_id, NULL, :transaction_date, 'sales_return',
                        :debit_amount, 0.00, :debit_amount, 'return', :return_id,
                        :voucher, :narration, :created_at, NULL)
            """), {
                'tenant_id': tenant_id,
                'transaction_date': return_date,
                'debit_amount': float(taxable_amount),
                'return_id': return_id,
                'voucher': return_number,
                'narration': f'[MIGRATION FIX] Sales return - {return_number}',
                'created_at': now
            })
            print(f"   ✅ DEBIT Sales Returns: ₹{taxable_amount}")
            
            # Entry 2: DEBIT CGST Receivable
            if cgst_amount > 0:
                db.session.execute(text("""
                    INSERT INTO account_transactions
                    (tenant_id, account_id, transaction_date, transaction_type,
                     debit_amount, credit_amount, balance_after, reference_type, reference_id,
                     voucher_number, narration, created_at, created_by)
                    VALUES (:tenant_id, NULL, :transaction_date, 'gst_return_cgst',
                            :debit_amount, 0.00, :debit_amount, 'return', :return_id,
                            :voucher, :narration, :created_at, NULL)
                """), {
                    'tenant_id': tenant_id,
                    'transaction_date': return_date,
                    'debit_amount': float(cgst_amount),
                    'return_id': return_id,
                    'voucher': return_number,
                    'narration': f'[MIGRATION FIX] CGST reversal on return {return_number}',
                    'created_at': now
                })
                print(f"   ✅ DEBIT CGST Receivable: ₹{cgst_amount}")
            
            # Entry 3: DEBIT SGST Receivable
            if sgst_amount > 0:
                db.session.execute(text("""
                    INSERT INTO account_transactions
                    (tenant_id, account_id, transaction_date, transaction_type,
                     debit_amount, credit_amount, balance_after, reference_type, reference_id,
                     voucher_number, narration, created_at, created_by)
                    VALUES (:tenant_id, NULL, :transaction_date, 'gst_return_sgst',
                            :debit_amount, 0.00, :debit_amount, 'return', :return_id,
                            :voucher, :narration, :created_at, NULL)
                """), {
                    'tenant_id': tenant_id,
                    'transaction_date': return_date,
                    'debit_amount': float(sgst_amount),
                    'return_id': return_id,
                    'voucher': return_number,
                    'narration': f'[MIGRATION FIX] SGST reversal on return {return_number}',
                    'created_at': now
                })
                print(f"   ✅ DEBIT SGST Receivable: ₹{sgst_amount}")
            
            # Entry 4: DEBIT IGST Receivable
            if igst_amount > 0:
                db.session.execute(text("""
                    INSERT INTO account_transactions
                    (tenant_id, account_id, transaction_date, transaction_type,
                     debit_amount, credit_amount, balance_after, reference_type, reference_id,
                     voucher_number, narration, created_at, created_by)
                    VALUES (:tenant_id, NULL, :transaction_date, 'gst_return_igst',
                            :debit_amount, 0.00, :debit_amount, 'return', :return_id,
                            :voucher, :narration, :created_at, NULL)
                """), {
                    'tenant_id': tenant_id,
                    'transaction_date': return_date,
                    'debit_amount': float(igst_amount),
                    'return_id': return_id,
                    'voucher': return_number,
                    'narration': f'[MIGRATION FIX] IGST reversal on return {return_number}',
                    'created_at': now
                })
                print(f"   ✅ DEBIT IGST Receivable: ₹{igst_amount}")
            
            fixed_count += 1
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': f'Fixed {fixed_count} unpaid return(s)',
            'returns_fixed': fixed_count,
            'tenant_id': tenant_id,
            'action': 'Refresh trial balance page to see balanced report!'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

