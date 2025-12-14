"""
Restore Commission Data After Incorrect Updates
Fixes commission_amount in invoice_commissions that were incorrectly reduced by returns
"""

from flask import Blueprint, jsonify
from models import db
from sqlalchemy import text
from decimal import Decimal
from utils.tenant_middleware import require_tenant, get_current_tenant_id

restore_commission_bp = Blueprint('restore_commission', __name__, url_prefix='/migration')

@restore_commission_bp.route('/restore-commission-data')
@require_tenant
def restore_commission_data():
    """Restore original commission amounts that were incorrectly reduced by returns"""
    tenant_id = get_current_tenant_id()
    
    try:
        print("\n" + "="*80)
        print("🔧 RESTORING COMMISSION DATA")
        print("="*80 + "\n")
        
        # Strategy: For each commission that has returns, recalculate what the
        # ORIGINAL commission should have been (before any returns)
        
        # Find all commissions where returns exist
        commissions_with_returns = db.session.execute(text("""
            SELECT 
                ic.id as commission_id,
                ic.invoice_id,
                ic.agent_id,
                ic.agent_name,
                ic.commission_percentage,
                ic.invoice_amount as current_invoice_amount,
                ic.commission_amount as current_commission_amount,
                i.invoice_number,
                i.total_amount as original_invoice_amount,
                (SELECT COALESCE(SUM(r.total_amount), 0)
                 FROM returns r
                 WHERE r.invoice_id = ic.invoice_id
                 AND r.tenant_id = :tenant_id
                 AND r.status = 'approved') as total_returned
            FROM invoice_commissions ic
            JOIN invoices i ON ic.invoice_id = i.id
            WHERE ic.tenant_id = :tenant_id
            AND EXISTS (
                SELECT 1 FROM returns r
                WHERE r.invoice_id = ic.invoice_id
                AND r.tenant_id = :tenant_id
                AND r.status = 'approved'
            )
            ORDER BY ic.invoice_id
        """), {'tenant_id': tenant_id}).fetchall()
        
        if not commissions_with_returns:
            print("✅ No commissions with returns found\n")
            return jsonify({
                'status': 'success',
                'message': 'No commissions to restore',
                'restored_count': 0
            })
        
        print(f"Found {len(commissions_with_returns)} commission(s) with returns:\n")
        
        restored_count = 0
        
        for comm in commissions_with_returns:
            commission_id = comm[0]
            invoice_id = comm[1]
            agent_id = comm[2]
            agent_name = comm[3]
            comm_percentage = Decimal(str(comm[4]))
            current_invoice_amount = Decimal(str(comm[5]))
            current_commission_amount = Decimal(str(comm[6]))
            invoice_number = comm[7]
            original_invoice_amount = Decimal(str(comm[8]))
            total_returned = Decimal(str(comm[9]))
            
            # CRITICAL FIX: The invoice.total_amount is NOT modified by returns!
            # Returns only create accounting entries, they don't change the invoice total
            # So original_invoice_amount is ALREADY the correct original amount
            # We just need to recalculate commission based on that
            
            # Calculate what the original commission should be
            original_commission = (original_invoice_amount * comm_percentage) / 100
            
            print(f"📦 Invoice: {invoice_number} (Agent: {agent_name})")
            print(f"   Current DB commission: ₹{current_commission_amount}")
            print(f"   Invoice total (not modified by returns): ₹{original_invoice_amount}")
            print(f"   Total returned: ₹{total_returned}")
            print(f"   Correct commission ({comm_percentage}%): ₹{original_commission}")
            
            # Update to restore original values
            if current_commission_amount != original_commission:
                db.session.execute(text("""
                    UPDATE invoice_commissions
                    SET invoice_amount = :original_invoice_amount,
                        commission_amount = :original_commission
                    WHERE id = :commission_id
                    AND tenant_id = :tenant_id
                """), {
                    'original_invoice_amount': float(original_invoice_amount),
                    'original_commission': float(original_commission),
                    'commission_id': commission_id,
                    'tenant_id': tenant_id
                })
                
                print(f"   ✅ Restored to original values\n")
                restored_count += 1
            else:
                print(f"   ℹ️  Already correct, skipping\n")
        
        db.session.commit()
        
        print("="*80)
        print(f"🎉 SUCCESS! Restored {restored_count} commission record(s)")
        print("="*80)
        print("\n✅ Commission Ledger should now show correct amounts!\n")
        
        return jsonify({
            'status': 'success',
            'message': f'Successfully restored {restored_count} commission record(s)',
            'restored_count': restored_count
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

