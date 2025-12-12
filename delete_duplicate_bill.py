#!/usr/bin/env python3
"""
Quick fix to delete the duplicate bill PB-202512-0001
This connects to PRODUCTION database and deletes the problematic bill
"""
import sys
sys.path.insert(0, 'modular_app')

from app import app
from models import db, PurchaseBill, PurchaseBillItem

with app.app_context():
    # Find the duplicate bill
    duplicate = PurchaseBill.query.filter_by(
        tenant_id=21,
        bill_number='PB-202512-0001'
    ).first()
    
    if duplicate:
        print(f"Found duplicate bill: {duplicate.bill_number}")
        print(f"  ID: {duplicate.id}")
        print(f"  Tenant: {duplicate.tenant_id}")
        print(f"  Status: {duplicate.status}")
        print(f"  Total: ₹{duplicate.total_amount}")
        print(f"  Created: {duplicate.created_at}")
        
        # Check for line items
        line_items = PurchaseBillItem.query.filter_by(
            purchase_bill_id=duplicate.id
        ).count()
        print(f"  Line Items: {line_items}")
        
        # Auto-delete without confirmation (since it's blocking production)
        print("\n🗑️  Deleting bill and associated items...")
        
        # Delete line items first (foreign key constraint)
        PurchaseBillItem.query.filter_by(
            purchase_bill_id=duplicate.id
        ).delete()
        
        # Delete the bill
        db.session.delete(duplicate)
        db.session.commit()
        
        print("✅ Deleted successfully!")
        print("\n✅ You can now create purchase bills in production!")
        print("   Next bill will be: PB-202512-0002")
    else:
        print("✅ No duplicate bill found with number PB-202512-0001")
        print("   You should be able to create bills now!")

