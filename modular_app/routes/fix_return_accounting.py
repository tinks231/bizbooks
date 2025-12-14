"""
Fix Return Accounting - Manual fix for old returns missing refund entries
"""

from flask import Blueprint, jsonify, g
from models import db
from sqlalchemy import text
from datetime import datetime
from decimal import Decimal
import pytz
from utils.tenant_middleware import require_tenant, get_current_tenant_id

fix_return_accounting_bp = Blueprint('fix_return_accounting', __name__, url_prefix='/migration')

@fix_return_accounting_bp.route('/fix-return-accounting')
@require_tenant
def fix_return_accounting():
    """Fix old returns that are missing refund_payment or cogs_reversal entries"""
    tenant_id = get_current_tenant_id()
    
    try:
        print("\n" + "="*80)
        print("🔧 FIXING OLD RETURNS - Adding Missing Refund Payment Entries")
        print("="*80 + "\n")
        
        # Find all approved returns that don't have refund_payment entries
        returns_to_fix = db.session.execute(text("""
            SELECT 
                r.id,
                r.return_number,
                r.total_amount,
                r.refund_method,
                r.payment_account_id,
                r.return_date,
                r.customer_name
            FROM returns r
            WHERE r.tenant_id = :tenant_id
            AND r.status = 'approved'
            AND r.refund_method IN ('cash', 'bank')
            AND NOT EXISTS (
                SELECT 1 FROM account_transactions at
                WHERE at.tenant_id = :tenant_id
                AND at.reference_type = 'return'
                AND at.reference_id = r.id
                AND at.transaction_type = 'refund_payment'
            )
            ORDER BY r.created_at
        """), {'tenant_id': tenant_id}).fetchall()
        
        if not returns_to_fix:
            print("✅ No returns missing refund_payment entries")
        
        print(f"Found {len(returns_to_fix)} return(s) to fix:\n")
        
        fixed_count = 0
        ist = pytz.timezone('Asia/Kolkata')
        now = datetime.now(ist)
        
        for ret in returns_to_fix:
            return_id = ret[0]
            return_number = ret[1]
            total_amount = Decimal(str(ret[2]))
            refund_method = ret[3]
            payment_account_id = ret[4]
            return_date = ret[5]
            customer_name = ret[6]
            
            print(f"📦 Fixing: {return_number} - ₹{total_amount} to {customer_name}")
            
            # If no payment_account_id, find one
            if not payment_account_id:
                print("   ⚠️  No payment account - finding one...")
                
                account_type = 'bank' if refund_method == 'bank' else 'cash'
                bank_account = db.session.execute(text("""
                    SELECT id, account_name, current_balance
                    FROM bank_accounts
                    WHERE tenant_id = :tenant_id
                    AND account_type = :account_type
                    AND is_active = TRUE
                    LIMIT 1
                """), {'tenant_id': tenant_id, 'account_type': account_type}).fetchone()
                
                if not bank_account:
                    print(f"   ❌ No active {account_type} account found - skipping!")
                    continue
                
                payment_account_id = bank_account[0]
                print(f"   ✅ Using: {bank_account[1]}")
                
                # Update return with payment_account_id
                db.session.execute(text("""
                    UPDATE returns
                    SET payment_account_id = :account_id
                    WHERE id = :return_id
                """), {'account_id': payment_account_id, 'return_id': return_id})
            
            # Get account info
            account = db.session.execute(text("""
                SELECT account_name, current_balance
                FROM bank_accounts
                WHERE id = :account_id AND tenant_id = :tenant_id
            """), {'account_id': payment_account_id, 'tenant_id': tenant_id}).fetchone()
            
            if not account:
                print(f"   ❌ Account not found - skipping!")
                continue
            
            account_name = account[0]
            current_balance = Decimal(str(account[1]))
            new_balance = current_balance - total_amount
            
            # Create refund_payment entry
            db.session.execute(text("""
                INSERT INTO account_transactions
                (tenant_id, account_id, transaction_date, transaction_type,
                 debit_amount, credit_amount, balance_after, reference_type, reference_id,
                 voucher_number, narration, created_at, created_by)
                VALUES (:tenant_id, :account_id, :transaction_date, 'refund_payment',
                        0.00, :credit_amount, :balance, 'return', :return_id,
                        :voucher, :narration, :created_at, NULL)
            """), {
                'tenant_id': tenant_id,
                'account_id': payment_account_id,
                'transaction_date': return_date,
                'credit_amount': float(total_amount),
                'balance': float(new_balance),
                'return_id': return_id,
                'voucher': return_number,
                'narration': f'Refund to {customer_name} via {account_name}',
                'created_at': now
            })
            
            # Update account balance
            db.session.execute(text("""
                UPDATE bank_accounts 
                SET current_balance = :new_balance, updated_at = :updated_at
                WHERE id = :account_id AND tenant_id = :tenant_id
            """), {
                'new_balance': new_balance,
                'updated_at': now,
                'account_id': payment_account_id,
                'tenant_id': tenant_id
            })
            
            print(f"   ✅ Added refund entry: ₹{total_amount} from {account_name}")
            print(f"   ✅ Updated balance: ₹{current_balance} → ₹{new_balance}\n")
            
            fixed_count += 1
        
        # ============================================================
        # PART 2: Fix Missing COGS Reversal Entries
        # ============================================================
        
        print("\n" + "-"*80)
        print("🔧 CHECKING FOR MISSING COGS REVERSAL ENTRIES")
        print("-"*80 + "\n")
        
        cogs_fixed_count = 0
        
        # Find approved returns missing cogs_reversal entries
        returns_missing_cogs = db.session.execute(text("""
            SELECT 
                r.id,
                r.return_number,
                r.total_amount
            FROM returns r
            WHERE r.tenant_id = :tenant_id
            AND r.status = 'approved'
            AND NOT EXISTS (
                SELECT 1 FROM account_transactions at
                WHERE at.tenant_id = :tenant_id
                AND at.reference_type = 'return'
                AND at.reference_id = r.id
                AND at.transaction_type = 'cogs_reversal'
            )
            ORDER BY r.created_at
        """), {'tenant_id': tenant_id}).fetchall()
        
        if not returns_missing_cogs:
            print("✅ No returns missing COGS reversal entries!\n")
        else:
            print(f"Found {len(returns_missing_cogs)} return(s) missing COGS reversal:\n")
            
            for ret_cogs in returns_missing_cogs:
                ret_id = ret_cogs[0]
                ret_num = ret_cogs[1]
                
                # Calculate COGS value for this return
                # Get all return items and their cost prices
                items_result = db.session.execute(text("""
                    SELECT 
                        ri.quantity_returned,
                        i.cost_price
                    FROM return_items ri
                    JOIN items i ON ri.product_id = i.id
                    WHERE ri.return_id = :return_id
                    AND ri.return_to_inventory = TRUE
                """), {'return_id': ret_id}).fetchall()
                
                total_cost = Decimal('0')
                for item in items_result:
                    qty = Decimal(str(item[0]))
                    cost = Decimal(str(item[1] or 0))
                    total_cost += qty * cost
                
                if total_cost == 0:
                    print(f"   ⚠️  {ret_num}: No cost value found - skipping")
                    continue
                
                print(f"   📦 {ret_num}: Adding COGS reversal for ₹{total_cost}")
                
                # Get return date
                ret_date = db.session.execute(text("""
                    SELECT return_date FROM returns WHERE id = :id
                """), {'id': ret_id}).scalar()
                
                # Create COGS reversal entry
                db.session.execute(text("""
                    INSERT INTO account_transactions
                    (tenant_id, account_id, transaction_date, transaction_type,
                     debit_amount, credit_amount, balance_after, reference_type, reference_id,
                     voucher_number, narration, created_at, created_by)
                    VALUES (:tenant_id, NULL, :transaction_date, 'cogs_reversal',
                            0.00, :credit_amount, 0.00, 'return', :return_id,
                            :voucher, :narration, :created_at, NULL)
                """), {
                    'tenant_id': tenant_id,
                    'transaction_date': ret_date,
                    'credit_amount': float(total_cost),
                    'return_id': ret_id,
                    'voucher': ret_num,
                    'narration': f'COGS reversal for returned inventory - {ret_num}',
                    'created_at': now
                })
                
                print(f"   ✅ Added COGS reversal entry\n")
                cogs_fixed_count += 1
        
        # ============================================================
        # PART 3: Fix Missing Commission Reversal Entries
        # ============================================================
        
        print("\n" + "-"*80)
        print("🔧 CHECKING FOR MISSING COMMISSION REVERSAL ENTRIES")
        print("-"*80 + "\n")
        
        commission_fixed_count = 0
        
        # Find approved returns that have commission but no commission_reversal entry
        returns_missing_commission = db.session.execute(text("""
            SELECT 
                r.id,
                r.return_number,
                r.invoice_id,
                r.total_amount,
                r.return_date
            FROM returns r
            WHERE r.tenant_id = :tenant_id
            AND r.status = 'approved'
            AND r.invoice_id IS NOT NULL
            AND EXISTS (
                SELECT 1 FROM invoice_commissions ic
                WHERE ic.invoice_id = r.invoice_id
                AND ic.tenant_id = :tenant_id
                AND ic.is_paid = TRUE
            )
            AND NOT EXISTS (
                SELECT 1 FROM account_transactions at
                WHERE at.tenant_id = :tenant_id
                AND at.reference_type = 'return'
                AND at.reference_id = r.id
                AND at.transaction_type = 'commission_reversal'
            )
            ORDER BY r.created_at
        """), {'tenant_id': tenant_id}).fetchall()
        
        if not returns_missing_commission:
            print("✅ No returns missing commission reversal entries!\n")
        else:
            print(f"Found {len(returns_missing_commission)} return(s) missing commission reversal:\n")
            
            for ret_comm in returns_missing_commission:
                ret_id = ret_comm[0]
                ret_num = ret_comm[1]
                invoice_id = ret_comm[2]
                return_amount = Decimal(str(ret_comm[3]))
                ret_date = ret_comm[4]
                
                # Get commission record(s) for this invoice
                commissions = db.session.execute(text("""
                    SELECT 
                        id,
                        agent_name,
                        commission_percentage,
                        commission_amount
                    FROM invoice_commissions
                    WHERE invoice_id = :invoice_id
                    AND tenant_id = :tenant_id
                    AND is_paid = TRUE
                """), {'invoice_id': invoice_id, 'tenant_id': tenant_id}).fetchall()
                
                for comm in commissions:
                    comm_id = comm[0]
                    agent_name = comm[1]
                    comm_percentage = Decimal(str(comm[2]))
                    
                    # Calculate commission on return amount
                    commission_on_return = (return_amount * comm_percentage) / 100
                    
                    print(f"   📦 {ret_num}: Reversing ₹{commission_on_return:.2f} commission for {agent_name}")
                    
                    # Create commission reversal entry
                    db.session.execute(text("""
                        INSERT INTO account_transactions
                        (tenant_id, account_id, transaction_date, transaction_type,
                         debit_amount, credit_amount, balance_after, reference_type, reference_id,
                         voucher_number, narration, created_at, created_by)
                        VALUES (:tenant_id, NULL, :transaction_date, 'commission_reversal',
                                0.00, :credit_amount, 0.00, 'return', :return_id,
                                :voucher, :narration, :created_at, NULL)
                    """), {
                        'tenant_id': tenant_id,
                        'transaction_date': ret_date,
                        'credit_amount': float(commission_on_return),
                        'return_id': ret_id,
                        'voucher': ret_num,
                        'narration': f'Commission reversal for {agent_name} - Return {ret_num}',
                        'created_at': now
                    })
                    
                    print(f"   ✅ Added commission reversal entry\n")
                    commission_fixed_count += 1
        
        # Commit all changes
        db.session.commit()
        
        print("="*80)
        print(f"🎉 SUCCESS!")
        print(f"   Refund entries fixed: {fixed_count}")
        print(f"   COGS reversal entries fixed: {cogs_fixed_count}")
        print(f"   Commission reversal entries fixed: {commission_fixed_count}")
        print("="*80)
        print("\n✅ Trial Balance & Commission Reports should now be ACCURATE!\n")
        
        return jsonify({
            'status': 'success',
            'message': f'Successfully fixed returns',
            'refund_entries_fixed': fixed_count,
            'cogs_reversal_entries_fixed': cogs_fixed_count,
            'commission_reversal_entries_fixed': commission_fixed_count,
            'total_returns_fixed': max(fixed_count, cogs_fixed_count, commission_fixed_count)
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"\n❌ ERROR: {str(e)}\n")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

