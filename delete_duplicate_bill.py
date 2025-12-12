#!/usr/bin/env python3
"""
Quick fix to delete the duplicate bill PB-202512-0001
This will allow you to create new bills while we debug the deployment
"""
import sys
sys.path.insert(0, 'modular_app')

from app import app
from models import db, PurchaseBill

with app.app_context():
    # Find the duplicate bill
    duplicate = PurchaseBill.query.filter_by(
        tenant_id=21,
        bill_number='PB-202512-0001'
    ).first()
    
    if duplicate:
        print(f"Found duplicate bill: {duplicate.bill_number}")
        print(f"  ID: {duplicate.id}")
        print(f"  Status: {duplicate.status}")
        print(f"  Total: ₹{duplicate.total_amount}")
        
        # Ask for confirmation
        confirm = input("\nDelete this bill? (yes/no): ")
        if confirm.lower() == 'yes':
            db.session.delete(duplicate)
            db.session.commit()
            print("✅ Deleted successfully!")
            print("You can now create purchase bills again.")
        else:
            print("❌ Cancelled.")
    else:
        print("No duplicate bill found with number PB-202512-0001")

