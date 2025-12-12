"""
FIX: Make vendor payment numbers tenant-specific

PROBLEM:
- payment_number has a GLOBAL unique constraint
- Prevents different tenants from using same payment number (PAY-0001)
- Causes: "duplicate key value violates unique constraint" error

SOLUTION:
- Drop global constraint: UNIQUE (payment_number)
- Add tenant-specific constraint: UNIQUE (tenant_id, payment_number)

Created: December 11, 2025
"""

from flask import Blueprint, jsonify
from models import db
from sqlalchemy import text

fix_vendor_payment_bp = Blueprint('fix_vendor_payment', __name__, url_prefix='/migration')


@fix_vendor_payment_bp.route('/fix-vendor-payment-constraint')
def fix_vendor_payment_constraint():
    """
    ONE-TIME migration: Fix vendor_payment_number constraint to be tenant-specific
    
    This allows each tenant to have their own PAY-0001, PAY-0002, etc.
    """
    
    try:
        print("\n" + "="*80)
        print("🔧 FIXING VENDOR PAYMENT CONSTRAINT")
        print("="*80 + "\n")
        
        # Drop old global constraint
        print("📝 Dropping global constraint...")
        db.session.execute(text("""
            ALTER TABLE vendor_payments 
            DROP CONSTRAINT IF EXISTS vendor_payments_payment_number_key
        """))
        print("✅ Old constraint dropped\n")
        
        # Add new tenant-specific constraint (if not exists)
        print("📝 Adding tenant-specific constraint...")
        
        # Check if constraint already exists
        constraint_exists = db.session.execute(text("""
            SELECT 1 FROM pg_constraint 
            WHERE conname = 'vendor_payments_tenant_payment_number_key'
        """)).fetchone()
        
        if constraint_exists:
            print("⚠️ Constraint already exists! Skipping...\n")
        else:
            db.session.execute(text("""
                ALTER TABLE vendor_payments 
                ADD CONSTRAINT vendor_payments_tenant_payment_number_key 
                    UNIQUE (tenant_id, payment_number)
            """))
            print("✅ New constraint added\n")
        
        db.session.commit()
        
        print("="*80)
        print("🎉 SUCCESS! Constraint fixed!")
        print("="*80)
        print("\n✅ Each tenant can now have their own PAY-0001, PAY-0002, etc.\n")
        
        return jsonify({
            'status': 'success',
            'message': 'Vendor payment constraint fixed successfully'
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

