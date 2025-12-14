"""
Fix Commission Amounts for Existing Returns
Updates invoice_commissions table to reflect returns
"""

from flask import Blueprint, jsonify
from models import db
from sqlalchemy import text
from decimal import Decimal
from utils.tenant_middleware import require_tenant, get_current_tenant_id

fix_commission_for_returns_bp = Blueprint('fix_commission_for_returns', __name__, url_prefix='/migration')

@fix_commission_for_returns_bp.route('/fix-commission-for-returns')
@require_tenant
def fix_commission_for_returns():
    """Recalculate commission amounts for invoices that have returns"""
    tenant_id = get_current_tenant_id()
    
    try:
        print("\n" + "="*80)
        print("🔧 FIXING COMMISSION AMOUNTS FOR RETURNS")
        print("="*80 + "\n")
        
        # Find all approved returns that have commissions
        returns_with_commission = db.session.execute(text("""
            SELECT 
                r.id as return_id,
                r.return_number,
                r.invoice_id,
                r.total_amount as return_amount,
                i.invoice_number,
                i.total_amount as original_invoice_amount
            FROM returns r
            JOIN invoices i ON r.invoice_id = i.id
            WHERE r.tenant_id = :tenant_id
            AND r.status = 'approved'
            AND EXISTS (
                SELECT 1 FROM invoice_commissions ic
                WHERE ic.invoice_id = r.invoice_id
                AND ic.tenant_id = :tenant_id
            )
            ORDER BY r.created_at
        """), {'tenant_id': tenant_id}).fetchall()
        
        if not returns_with_commission:
            print("✅ No returns with commissions found\n")
            return jsonify({
                'status': 'success',
                'message': 'No commissions to fix',
                'fixed_count': 0
            })
        
        print(f"Found {len(returns_with_commission)} return(s) with commissions:\n")
        
        fixed_count = 0
        
        for ret in returns_with_commission:
            return_id = ret[0]
            return_number = ret[1]
            invoice_id = ret[2]
            return_amount = Decimal(str(ret[3]))
            invoice_number = ret[4]
            original_invoice_amount = Decimal(str(ret[5]))
            
            # Calculate net invoice amount after return
            net_invoice_amount = original_invoice_amount - return_amount
            
            print(f"📦 Return: {return_number} (Invoice: {invoice_number})")
            print(f"   Original Invoice: ₹{original_invoice_amount}")
            print(f"   Return Amount: ₹{return_amount}")
            print(f"   Net Invoice: ₹{net_invoice_amount}")
            
            # Get all commissions for this invoice
            commissions = db.session.execute(text("""
                SELECT 
                    id,
                    agent_name,
                    commission_percentage,
                    invoice_amount,
                    commission_amount
                FROM invoice_commissions
                WHERE invoice_id = :invoice_id
                AND tenant_id = :tenant_id
            """), {'invoice_id': invoice_id, 'tenant_id': tenant_id}).fetchall()
            
            for comm in commissions:
                comm_id = comm[0]
                agent_name = comm[1]
                comm_percentage = Decimal(str(comm[2]))
                old_invoice_amount = Decimal(str(comm[3]))
                old_commission_amount = Decimal(str(comm[4]))
                
                # Calculate new commission based on net invoice amount
                new_commission_amount = (net_invoice_amount * comm_percentage) / 100
                
                print(f"\n   Agent: {agent_name} ({comm_percentage}%)")
                print(f"   Old Commission: ₹{old_commission_amount}")
                print(f"   New Commission: ₹{new_commission_amount}")
                
                # Update the commission record
                db.session.execute(text("""
                    UPDATE invoice_commissions
                    SET invoice_amount = :new_invoice_amount,
                        commission_amount = :new_commission_amount
                    WHERE id = :comm_id
                    AND tenant_id = :tenant_id
                """), {
                    'new_invoice_amount': float(net_invoice_amount),
                    'new_commission_amount': float(new_commission_amount),
                    'comm_id': comm_id,
                    'tenant_id': tenant_id
                })
                
                print(f"   ✅ Updated commission record\n")
                fixed_count += 1
        
        db.session.commit()
        
        print("="*80)
        print(f"🎉 SUCCESS! Fixed {fixed_count} commission record(s)")
        print("="*80)
        print("\n✅ Commission reports should now show NET amounts!\n")
        
        return jsonify({
            'status': 'success',
            'message': f'Successfully fixed {fixed_count} commission record(s)',
            'fixed_count': fixed_count
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

