"""
COMPREHENSIVE FIX: Migrate existing data to proper double-entry accounting
This will fix ALL historical data to use the new system
"""

from flask import Blueprint, jsonify
from models import db
from sqlalchemy import text
from utils.tenant_middleware import require_tenant, get_current_tenant_id
from datetime import datetime
import pytz

comprehensive_double_entry_migration_bp = Blueprint('comprehensive_migration', __name__, url_prefix='/migration')

@comprehensive_double_entry_migration_bp.route('/comprehensive-double-entry-fix', methods=['GET'])
@require_tenant
def show_migration_page():
    """Show migration page with execute button"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Comprehensive Double-Entry Migration</title>
        <style>
            body { 
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                max-width: 800px; 
                margin: 50px auto; 
                padding: 20px;
                background: #f5f5f5;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 12px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 { color: #333; margin-bottom: 20px; }
            .warning {
                background: #fff3cd;
                border: 1px solid #ffc107;
                padding: 15px;
                border-radius: 6px;
                margin: 20px 0;
            }
            .info {
                background: #d1ecf1;
                border: 1px solid #bee5eb;
                padding: 15px;
                border-radius: 6px;
                margin: 20px 0;
            }
            button {
                background: #667eea;
                color: white;
                border: none;
                padding: 15px 30px;
                font-size: 16px;
                border-radius: 6px;
                cursor: pointer;
                font-weight: 600;
            }
            button:hover { background: #5568d3; }
            button:disabled { background: #ccc; cursor: not-allowed; }
            #result {
                margin-top: 20px;
                padding: 15px;
                border-radius: 6px;
                display: none;
            }
            .success { background: #d4edda; border: 1px solid #c3e6cb; color: #155724; }
            .error { background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; }
            pre { 
                background: #f8f9fa; 
                padding: 15px; 
                border-radius: 6px; 
                overflow-x: auto;
                font-size: 12px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎯 Comprehensive Double-Entry Migration</h1>
            
            <div class="warning">
                <strong>⚠️ IMPORTANT:</strong> This migration will:
                <ul>
                    <li>Delete ALL old equity entries (band-aids)</li>
                    <li>Create proper double-entry accounting entries</li>
                    <li>Balance your trial balance permanently</li>
                </ul>
            </div>
            
            <div class="info">
                <strong>✅ What This Will Fix:</strong>
                <ul>
                    <li>Trial balance will be perfectly balanced</li>
                    <li>All inventory will have proper accounting entries</li>
                    <li>Future imports will auto-balance</li>
                </ul>
            </div>
            
            <button id="executeBtn" onclick="executeMigration()">
                Execute Migration Now
            </button>
            
            <div id="result"></div>
        </div>
        
        <script>
            async function executeMigration() {
                const btn = document.getElementById('executeBtn');
                const resultDiv = document.getElementById('result');
                
                btn.disabled = true;
                btn.textContent = 'Executing...';
                resultDiv.style.display = 'none';
                
                try {
                    const response = await fetch('/migration/comprehensive-double-entry-fix', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        }
                    });
                    
                    const data = await response.json();
                    
                    resultDiv.style.display = 'block';
                    
                    if (data.status === 'success') {
                        resultDiv.className = 'success';
                        resultDiv.innerHTML = `
                            <h3>✅ Migration Successful!</h3>
                            <pre>${JSON.stringify(data.result, null, 2)}</pre>
                            <p><strong>Next Step:</strong> <a href="/admin/reports/trial-balance">Check Trial Balance</a></p>
                        `;
                    } else {
                        resultDiv.className = 'error';
                        resultDiv.innerHTML = `
                            <h3>❌ Migration Failed</h3>
                            <p><strong>Error:</strong> ${data.message}</p>
                            <pre>${data.traceback || ''}</pre>
                        `;
                    }
                } catch (error) {
                    resultDiv.style.display = 'block';
                    resultDiv.className = 'error';
                    resultDiv.innerHTML = `
                        <h3>❌ Request Failed</h3>
                        <p>${error.message}</p>
                    `;
                } finally {
                    btn.disabled = false;
                    btn.textContent = 'Execute Migration Again';
                }
            }
        </script>
    </body>
    </html>
    """

@comprehensive_double_entry_migration_bp.route('/comprehensive-double-entry-fix', methods=['POST'])
@require_tenant
def comprehensive_double_entry_fix():
    """
    THE FINAL FIX: Migrate ALL existing data to proper double-entry accounting
    
    This will:
    1. Clear all OLD equity entries (the band-aids we applied)
    2. Create ONE proper DEBIT entry for total inventory
    3. Create ONE proper CREDIT entry for owner's capital (inventory equity)
    4. System will auto-balance going forward with the new code!
    """
    
    try:
        tenant_id = get_current_tenant_id()
        ist = pytz.timezone('Asia/Kolkata')
        now = datetime.now(ist)
        
        result = {
            'tenant_id': tenant_id,
            'steps': []
        }
        
        # ============================================================
        # STEP 1: Delete ALL old inventory AND equity entries
        # ============================================================
        delete_result = db.session.execute(text("""
            DELETE FROM account_transactions
            WHERE tenant_id = :tenant_id
            AND transaction_type IN (
                'opening_balance_inventory_equity',
                'inventory_opening_debit',
                'opening_balance_equity'
            )
            RETURNING id
        """), {'tenant_id': tenant_id})
        
        deleted_count = len(delete_result.fetchall())
        result['steps'].append({
            'step': 1,
            'action': 'Delete old equity entries',
            'deleted_count': deleted_count,
            'message': f'Removed {deleted_count} old band-aid equity entries'
        })
        
        # ============================================================
        # STEP 2: Calculate CURRENT inventory value from item_stocks
        # ============================================================
        current_inventory = db.session.execute(text("""
            SELECT COALESCE(SUM(stock_value), 0)
            FROM item_stocks
            WHERE tenant_id = :tenant_id
        """), {'tenant_id': tenant_id}).fetchone()[0]
        
        result['steps'].append({
            'step': 2,
            'action': 'Calculate current inventory',
            'inventory_value': float(current_inventory)
        })
        
        # ============================================================
        # STEP 3: Calculate CURRENT cash/bank balances
        # ============================================================
        cash_bank = db.session.execute(text("""
            SELECT 
                account_name,
                current_balance,
                opening_balance
            FROM bank_accounts
            WHERE tenant_id = :tenant_id
            AND is_active = TRUE
        """), {'tenant_id': tenant_id}).fetchall()
        
        cash_bank_details = []
        for account in cash_bank:
            account_name = account[0]
            current_balance = account[1]
            opening_balance = account[2]
            
            cash_bank_details.append({
                'account': account_name,
                'current': float(current_balance),
                'opening': float(opening_balance)
            })
        
        result['steps'].append({
            'step': 3,
            'action': 'Get cash/bank balances',
            'accounts': cash_bank_details
        })
        
        # ============================================================
        # STEP 4: Create PROPER inventory opening entries
        # ============================================================
        if current_inventory > 0:
            voucher = f"OB-INV-FIX-{tenant_id}"
            
            # DEBIT: Inventory (Asset)
            db.session.execute(text("""
                INSERT INTO account_transactions
                (tenant_id, account_id, transaction_date, transaction_type,
                 debit_amount, credit_amount, balance_after, voucher_number,
                 narration, created_at)
                VALUES (:tenant_id, NULL, :date, 'inventory_opening_debit',
                        :amount, 0.00, :amount, :voucher,
                        :narration, :created_at)
            """), {
                'tenant_id': tenant_id,
                'date': now.date(),
                'amount': float(current_inventory),
                'voucher': voucher,
                'narration': f'Opening Balance - Total Inventory (Rs.{current_inventory:,.2f})',
                'created_at': now
            })
            
            # CREDIT: Owner's Capital - Inventory
            db.session.execute(text("""
                INSERT INTO account_transactions
                (tenant_id, account_id, transaction_date, transaction_type,
                 debit_amount, credit_amount, balance_after, voucher_number,
                 narration, created_at)
                VALUES (:tenant_id, NULL, :date, 'opening_balance_inventory_equity',
                        0.00, :amount, :amount, :voucher,
                        :narration, :created_at)
            """), {
                'tenant_id': tenant_id,
                'date': now.date(),
                'amount': float(current_inventory),
                'voucher': voucher,
                'narration': f'Opening Balance - Owner\'s Capital (Inventory Equity Rs.{current_inventory:,.2f})',
                'created_at': now
            })
            
            result['steps'].append({
                'step': 4,
                'action': 'Create inventory opening entries',
                'debit': float(current_inventory),
                'credit': float(current_inventory),
                'message': f'Created proper double-entry for Rs.{current_inventory:,.2f} inventory'
            })
        
        # ============================================================
        # STEP 5: Create PROPER cash/bank opening CREDIT entries
        # ============================================================
        # The DEBIT side already exists (created when accounts were set up)
        # We need to create the matching CREDIT side (Owner's Capital)
        
        cash_bank_entries_created = 0
        
        for account in cash_bank_details:
            if account['opening'] > 0:
                account_name = account['account']
                opening_amount = account['opening']
                
                # Check if CREDIT equity entry already exists for this account
                existing_credit = db.session.execute(text("""
                    SELECT id FROM account_transactions
                    WHERE tenant_id = :tenant_id
                    AND transaction_type = 'opening_balance_equity'
                    AND credit_amount = :amount
                    AND (narration LIKE :search_pattern1 OR narration LIKE :search_pattern2)
                """), {
                    'tenant_id': tenant_id,
                    'amount': float(opening_amount),
                    'search_pattern1': f'%{account_name}%',
                    'search_pattern2': f'%Opening Balance%{account_name}%'
                }).fetchone()
                
                if not existing_credit:
                    voucher = f"OB-EQUITY-{tenant_id}-{account_name.replace(' ', '')[:10]}"
                    
                    # CREDIT: Owner's Capital for this account opening
                    db.session.execute(text("""
                        INSERT INTO account_transactions
                        (tenant_id, account_id, transaction_date, transaction_type,
                         debit_amount, credit_amount, balance_after, voucher_number,
                         narration, created_at)
                        VALUES (:tenant_id, NULL, :date, 'opening_balance_equity',
                                0.00, :amount, :amount, :voucher,
                                :narration, :created_at)
                    """), {
                        'tenant_id': tenant_id,
                        'date': now.date(),
                        'amount': float(opening_amount),
                        'voucher': voucher,
                        'narration': f'Opening Balance Equity - {account_name} (Rs.{opening_amount:,.2f})',
                        'created_at': now
                    })
                    
                    cash_bank_entries_created += 1
        
        result['steps'].append({
            'step': 5,
            'action': 'Create cash/bank opening CREDIT entries',
            'accounts_checked': len(cash_bank_details),
            'entries_created': cash_bank_entries_created,
            'message': f'Created {cash_bank_entries_created} missing CREDIT entries for cash/bank opening balances'
        })
        
        db.session.commit()
        
        # ============================================================
        # STEP 6: Verify trial balance
        # ============================================================
        trial_balance = db.session.execute(text("""
            SELECT 
                COALESCE(SUM(debit_amount), 0) as total_debits,
                COALESCE(SUM(credit_amount), 0) as total_credits
            FROM account_transactions
            WHERE tenant_id = :tenant_id
        """), {'tenant_id': tenant_id}).fetchone()
        
        total_debits = float(trial_balance[0])
        total_credits = float(trial_balance[1])
        difference = abs(total_debits - total_credits)
        
        result['verification'] = {
            'total_debits': total_debits,
            'total_credits': total_credits,
            'difference': difference,
            'is_balanced': difference < 0.01,
            'message': 'Trial Balance is BALANCED!' if difference < 0.01 else f'Difference: Rs.{difference:,.2f}'
        }
        
        return jsonify({
            'status': 'success',
            'result': result,
            'message': 'Comprehensive double-entry migration completed!'
        })
        
    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'status': 'error',
            'message': str(e),
            'traceback': traceback.format_exc()
        }), 500

