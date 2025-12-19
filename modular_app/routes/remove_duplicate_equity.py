"""
Remove duplicate equity entries
"""

from flask import Blueprint, jsonify, g
from models import db
from sqlalchemy import text
from utils.tenant_middleware import require_tenant, get_current_tenant_id

remove_duplicate_equity_bp = Blueprint('remove_duplicate_equity', __name__, url_prefix='/migration')

@remove_duplicate_equity_bp.route('/remove-duplicate-equity')
@require_tenant
def remove_duplicate_equity():
    """
    Remove duplicate equity entries
    Keep only one entry per account/narration
    """
    
    try:
        tenant_id = get_current_tenant_id()
        
        print(f"\n{'=' * 80}")
        print(f"🔧 REMOVING DUPLICATE EQUITY ENTRIES FOR TENANT: {tenant_id}")
        print(f"{'=' * 80}")
        
        # 1. Show current equity entries
        current_entries = db.session.execute(text("""
            SELECT 
                id,
                transaction_type,
                narration,
                credit_amount,
                created_at
            FROM account_transactions
            WHERE tenant_id = :tenant_id
            AND transaction_type IN ('opening_balance_equity', 'opening_balance_inventory_equity')
            ORDER BY narration, created_at
        """), {'tenant_id': tenant_id}).fetchall()
        
        print(f"\n📊 Current equity entries ({len(current_entries)}):")
        for entry in current_entries:
            print(f"  ID {entry[0]}: {entry[2]} = ₹{entry[3]:,.2f} (created: {entry[4]})")
        
        # 2. Find duplicates (same narration pattern)
        # Group by transaction_type and similar narration
        from collections import defaultdict
        groups = defaultdict(list)
        
        for entry in current_entries:
            entry_id = entry[0]
            trans_type = entry[1]
            narration = entry[2]
            amount = entry[3]
            created_at = entry[4]
            
            # Create grouping key
            key = trans_type + "|"
            if 'Cash' in narration and 'Opening' in narration:
                key += "CASH_OPENING"
            elif 'Bank' in narration and 'Opening' in narration:
                key += "BANK_OPENING"
            elif 'Inventory' in narration:
                # Keep inventory entries separate by amount (they might legitimately have multiple)
                key += f"INVENTORY_{amount}"
            else:
                key += narration
            
            groups[key].append({
                'id': entry_id,
                'narration': narration,
                'amount': amount,
                'created_at': created_at
            })
        
        # 3. Identify duplicates to remove
        to_remove = []
        
        for key, entries in groups.items():
            if len(entries) > 1:
                print(f"\n⚠️  Found {len(entries)} entries for: {key}")
                
                # Sort by created_at (keep oldest, remove newer duplicates)
                entries_sorted = sorted(entries, key=lambda x: x['created_at'])
                
                # Keep first (oldest), remove rest
                keep = entries_sorted[0]
                duplicates = entries_sorted[1:]
                
                print(f"  KEEP: ID {keep['id']} - {keep['narration']} (₹{keep['amount']:,.2f})")
                
                for dup in duplicates:
                    print(f"  REMOVE: ID {dup['id']} - {dup['narration']} (₹{dup['amount']:,.2f})")
                    to_remove.append(dup['id'])
        
        # 4. Also remove the weird ₹0.02 entry
        tiny_entries = [e for e in current_entries if abs(e[3]) < 1]
        for entry in tiny_entries:
            if entry[0] not in to_remove:
                print(f"\n⚠️  Found tiny amount: ID {entry[0]} = ₹{entry[3]} - REMOVING")
                to_remove.append(entry[0])
        
        # 5. Remove duplicates
        if to_remove:
            print(f"\n🗑️  Removing {len(to_remove)} duplicate/tiny entries...")
            
            deleted = db.session.execute(text("""
                DELETE FROM account_transactions
                WHERE tenant_id = :tenant_id
                AND id = ANY(:ids)
                RETURNING id, narration, credit_amount
            """), {'tenant_id': tenant_id, 'ids': to_remove}).fetchall()
            
            db.session.commit()
            
            print(f"✅ Deleted {len(deleted)} entries:")
            for entry in deleted:
                print(f"  - ID {entry[0]}: {entry[1]} = ₹{entry[2]:,.2f}")
        else:
            print(f"\n✅ No duplicates found!")
        
        # 6. Show remaining entries
        remaining = db.session.execute(text("""
            SELECT 
                id,
                transaction_type,
                narration,
                credit_amount
            FROM account_transactions
            WHERE tenant_id = :tenant_id
            AND transaction_type IN ('opening_balance_equity', 'opening_balance_inventory_equity')
            ORDER BY narration
        """), {'tenant_id': tenant_id}).fetchall()
        
        print(f"\n📊 Remaining equity entries ({len(remaining)}):")
        for entry in remaining:
            print(f"  ID {entry[0]}: {entry[2]} = ₹{entry[3]:,.2f}")
        
        print(f"\n{'=' * 80}")
        print(f"✅ CLEANUP COMPLETED!")
        print(f"{'=' * 80}\n")
        
        return jsonify({
            'status': 'success',
            'message': f'Removed {len(to_remove)} duplicate/tiny equity entries',
            'removed_count': len(to_remove),
            'remaining_count': len(remaining),
            'action': 'Refresh trial balance page'
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

