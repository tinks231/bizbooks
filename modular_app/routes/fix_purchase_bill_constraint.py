"""
FIX: Make purchase bill numbers tenant-specific

PROBLEM:
- bill_number has a GLOBAL unique constraint
- Prevents different tenants from using same bill number (PB-202512-0001)
- Causes: "duplicate key value violates unique constraint" error

SOLUTION:
- Drop global constraint: UNIQUE (bill_number)
- Add tenant-specific constraint: UNIQUE (tenant_id, bill_number)

Created: December 13, 2025
"""

from flask import Blueprint, jsonify
from models import db
from sqlalchemy import text

fix_purchase_bill_bp = Blueprint('fix_purchase_bill', __name__, url_prefix='/migration')


@fix_purchase_bill_bp.route('/fix-purchase-bill-constraint')
def fix_purchase_bill_constraint():
    """
    ONE-TIME migration: Fix purchase_bill_number constraint to be tenant-specific
    
    This allows each tenant to have their own PB-202512-0001, PB-202512-0002, etc.
    """
    
    try:
        print("\n" + "="*80)
        print("🔧 FIXING PURCHASE BILL CONSTRAINT")
        print("="*80 + "\n")
        
        # Drop old global constraint
        print("📝 Dropping global constraint...")
        db.session.execute(text("""
            ALTER TABLE purchase_bills 
            DROP CONSTRAINT IF EXISTS purchase_bills_bill_number_key
        """))
        print("✅ Old constraint dropped\n")
        
        # Add new tenant-specific constraint (if not exists)
        print("📝 Adding tenant-specific constraint...")
        
        # Check if constraint already exists
        constraint_exists = db.session.execute(text("""
            SELECT 1 FROM pg_constraint 
            WHERE conname = 'purchase_bills_tenant_bill_number_key'
        """)).fetchone()
        
        if constraint_exists:
            print("⚠️ Constraint already exists! Skipping...\n")
        else:
            db.session.execute(text("""
                ALTER TABLE purchase_bills 
                ADD CONSTRAINT purchase_bills_tenant_bill_number_key 
                    UNIQUE (tenant_id, bill_number)
            """))
            print("✅ New constraint added\n")
        
        db.session.commit()
        
        print("="*80)
        print("🎉 SUCCESS! Constraint fixed!")
        print("="*80)
        print("\n✅ Each tenant can now have their own PB-202512-0001, PB-202512-0002, etc.\n")
        
        return jsonify({
            'status': 'success',
            'message': 'Purchase bill constraint fixed successfully'
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

