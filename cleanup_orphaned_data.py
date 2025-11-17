#!/usr/bin/env python3
"""
Cleanup Orphaned Data Script
=============================
Finds and removes database records that belong to deleted tenants.

This happens when:
1. Tenant was deleted before CASCADE DELETE was implemented
2. Manual deletion missed some relationships
3. Database inconsistencies

Run this ONCE after deploying CASCADE DELETE fix to clean up existing orphaned data.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modular_app.app import create_app
from modular_app.models import db
from modular_app.models.tenant import Tenant

# Import all models that might have orphaned data
from modular_app.models.item import Item, ItemGroup, ItemCategory, ItemStock, ItemStockMovement
from modular_app.models.inventory import Material, Stock, StockMovement, Transfer, InventoryAdjustment, InventoryAdjustmentLine
from modular_app.models.customer import Customer
from modular_app.models.invoice import Invoice, InvoiceItem
from modular_app.models.vendor import Vendor
from modular_app.models.purchase_bill import PurchaseBill
from modular_app.models.purchase_bill_item import PurchaseBillItem
from modular_app.models.vendor_payment import VendorPayment
from modular_app.models.sales_order import SalesOrder, SalesOrderItem
from modular_app.models.delivery_challan import DeliveryChallan, DeliveryChallanItem
from modular_app.models.employee import Employee
from modular_app.models.site import Site
from modular_app.models.attendance import Attendance
from modular_app.models.task import Task, TaskUpdate, TaskMaterial, TaskMedia
from modular_app.models.expense import Expense, ExpenseCategory
from modular_app.models.purchase_request import PurchaseRequest, PurchaseRequestItem
from modular_app.models.subscription import SubscriptionPlan, Subscription, SubscriptionPayment
from modular_app.models.commission_agent import CommissionAgent, AgentCommission

app = create_app()

def find_orphaned_records():
    """Find all records with tenant_id that doesn't exist in tenants table"""
    
    print("\n" + "="*70)
    print("🔍 SCANNING FOR ORPHANED DATA")
    print("="*70)
    
    with app.app_context():
        # Get all valid tenant IDs
        valid_tenant_ids = set([t.id for t in Tenant.query.all()])
        print(f"\n✅ Found {len(valid_tenant_ids)} active tenants: {sorted(valid_tenant_ids)}")
        
        orphaned_data = {}
        total_orphaned = 0
        
        # Define all models to check
        models_to_check = [
            ('Items', Item),
            ('Item Groups', ItemGroup),
            ('Item Categories', ItemCategory),
            ('Item Stocks', ItemStock),
            ('Item Stock Movements', ItemStockMovement),
            ('Inventory Adjustments', InventoryAdjustment),
            ('Customers', Customer),
            ('Invoices', Invoice),
            ('Invoice Items', InvoiceItem),
            ('Vendors', Vendor),
            ('Purchase Bills', PurchaseBill),
            ('Purchase Bill Items', PurchaseBillItem),
            ('Vendor Payments', VendorPayment),
            ('Sales Orders', SalesOrder),
            ('Sales Order Items', SalesOrderItem),
            ('Delivery Challans', DeliveryChallan),
            ('Delivery Challan Items', DeliveryChallanItem),
            ('Employees', Employee),
            ('Sites', Site),
            ('Attendance Records', Attendance),
            ('Tasks', Task),
            ('Task Updates', TaskUpdate),
            ('Task Materials', TaskMaterial),
            ('Task Media', TaskMedia),
            ('Expenses', Expense),
            ('Expense Categories', ExpenseCategory),
            ('Purchase Requests', PurchaseRequest),
            ('Purchase Request Items', PurchaseRequestItem),
            ('Materials', Material),
            ('Stocks', Stock),
            ('Stock Movements', StockMovement),
            ('Transfers', Transfer),
            ('Subscription Plans', SubscriptionPlan),
            ('Subscriptions', Subscription),
            ('Subscription Payments', SubscriptionPayment),
            ('Commission Agents', CommissionAgent),
            ('Agent Commissions', AgentCommission),
        ]
        
        print("\n📊 Scanning models for orphaned records...")
        print("-" * 70)
        
        for model_name, model_class in models_to_check:
            try:
                # Get all records with invalid tenant_id
                orphaned = model_class.query.filter(
                    ~model_class.tenant_id.in_(valid_tenant_ids)
                ).all()
                
                if orphaned:
                    orphaned_tenant_ids = set([r.tenant_id for r in orphaned])
                    orphaned_data[model_name] = {
                        'count': len(orphaned),
                        'tenant_ids': sorted(orphaned_tenant_ids),
                        'model': model_class
                    }
                    total_orphaned += len(orphaned)
                    print(f"⚠️  {model_name:30s}: {len(orphaned):4d} orphaned (tenants: {sorted(orphaned_tenant_ids)})")
                else:
                    print(f"✅ {model_name:30s}: clean")
                    
            except Exception as e:
                print(f"❌ {model_name:30s}: error checking ({str(e)})")
        
        print("-" * 70)
        print(f"\n📊 SUMMARY: Found {total_orphaned} total orphaned records")
        
        return orphaned_data, valid_tenant_ids


def cleanup_orphaned_data(orphaned_data, valid_tenant_ids, dry_run=True):
    """Delete orphaned records"""
    
    if not orphaned_data:
        print("\n✅ No orphaned data found! Database is clean.")
        return
    
    print("\n" + "="*70)
    if dry_run:
        print("🧪 DRY RUN MODE - No actual deletions will be performed")
    else:
        print("🗑️  CLEANUP MODE - DELETING ORPHANED DATA")
    print("="*70)
    
    with app.app_context():
        deleted_counts = {}
        
        for model_name, info in orphaned_data.items():
            try:
                model_class = info['model']
                
                if dry_run:
                    print(f"Would delete {info['count']} {model_name}")
                else:
                    # Delete records with invalid tenant_id
                    deleted = model_class.query.filter(
                        ~model_class.tenant_id.in_(valid_tenant_ids)
                    ).delete(synchronize_session=False)
                    
                    deleted_counts[model_name] = deleted
                    print(f"✅ Deleted {deleted} {model_name}")
                    
            except Exception as e:
                print(f"❌ Error deleting {model_name}: {e}")
        
        if not dry_run:
            db.session.commit()
            print("\n✅ All orphaned data deleted successfully!")
            
            print("\n📊 DELETION SUMMARY:")
            print("-" * 70)
            for model_name, count in deleted_counts.items():
                print(f"   {model_name:30s}: {count:4d} records")
            print("-" * 70)
            print(f"   TOTAL:                          {sum(deleted_counts.values()):4d} records")


def main():
    """Main function"""
    print("\n" + "="*70)
    print("🧹 ORPHANED DATA CLEANUP TOOL")
    print("="*70)
    print("\nThis tool finds and removes database records belonging to deleted tenants.")
    print("Run in DRY RUN mode first to see what would be deleted.\n")
    
    # Step 1: Find orphaned data
    orphaned_data, valid_tenant_ids = find_orphaned_records()
    
    if not orphaned_data:
        print("\n✅ Great! Your database is clean - no orphaned data found.")
        return
    
    # Step 2: Ask user what to do
    print("\n" + "="*70)
    print("⚠️  ORPHANED DATA FOUND!")
    print("="*70)
    print("\nWhat would you like to do?")
    print("  1. DRY RUN - Show what would be deleted (safe)")
    print("  2. DELETE - Actually remove orphaned data (permanent!)")
    print("  3. CANCEL - Exit without changes")
    print()
    
    choice = input("Enter choice (1/2/3): ").strip()
    
    if choice == '1':
        cleanup_orphaned_data(orphaned_data, valid_tenant_ids, dry_run=True)
        print("\n💡 Tip: Run with option 2 to actually delete the orphaned data")
        
    elif choice == '2':
        print("\n⚠️  WARNING: This will PERMANENTLY DELETE orphaned data!")
        confirm = input("Type 'DELETE' to confirm: ").strip()
        
        if confirm == 'DELETE':
            cleanup_orphaned_data(orphaned_data, valid_tenant_ids, dry_run=False)
            print("\n✅ Cleanup complete! Database is now clean.")
        else:
            print("\n❌ Cancelled - no changes made")
            
    else:
        print("\n❌ Cancelled - no changes made")


if __name__ == '__main__':
    main()

