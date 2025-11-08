"""
Tenant Deletion Utility
========================
Safely delete a tenant and all associated data + files

Usage:
    python delete_tenant.py <tenant_id>
    or
    python delete_tenant.py --subdomain <subdomain>

Example:
    python delete_tenant.py 11
    python delete_tenant.py --subdomain mahaveerelectricals

This will:
1. Delete all database records (items, bills, invoices, vendors, customers, etc.)
2. Delete all uploaded files (selfies, documents, item images, logos)
3. Show a summary of what was deleted
"""

import sys
import os
import shutil
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import Tenant

def delete_tenant_files(tenant_id):
    """Delete all files associated with a tenant"""
    deleted_files = []
    deleted_folders = []
    
    # File upload folders
    upload_folders = [
        'uploads/selfies',
        'uploads/documents',
        'uploads/inventory_images',
        'uploads/logos',
        'uploads/task_media'
    ]
    
    for folder in upload_folders:
        folder_path = Path(folder)
        if folder_path.exists():
            # Find files with tenant_id in the name (common pattern: tenant_11_filename.jpg)
            for file in folder_path.glob(f'tenant_{tenant_id}_*'):
                try:
                    file.unlink()
                    deleted_files.append(str(file))
                except Exception as e:
                    print(f"❌ Error deleting {file}: {e}")
            
            # Also check for folders named with tenant_id
            for subfolder in folder_path.glob(f'tenant_{tenant_id}*'):
                if subfolder.is_dir():
                    try:
                        shutil.rmtree(subfolder)
                        deleted_folders.append(str(subfolder))
                    except Exception as e:
                        print(f"❌ Error deleting folder {subfolder}: {e}")
    
    return deleted_files, deleted_folders


def delete_tenant_data(tenant_id):
    """Delete all database records for a tenant"""
    from models import (
        Employee, Site, Attendance, Item, ItemCategory, ItemGroup,
        Customer, Vendor, Invoice, InvoiceItem, PurchaseBill, PurchaseBillItem,
        SalesOrder, SalesOrderItem, DeliveryChallan, DeliveryChallanItem,
        Expense, ExpenseCategory, VendorPayment, PaymentAllocation,
        PurchaseRequest
    )
    
    deleted_counts = {}
    
    # Delete in correct order (child tables first)
    models_to_delete = [
        ('Payment Allocations', PaymentAllocation),
        ('Vendor Payments', VendorPayment),
        ('Delivery Challan Items', DeliveryChallanItem),
        ('Delivery Challans', DeliveryChallan),
        ('Sales Order Items', SalesOrderItem),
        ('Sales Orders', SalesOrder),
        ('Invoice Items', InvoiceItem),
        ('Invoices', Invoice),
        ('Purchase Bill Items', PurchaseBillItem),
        ('Purchase Bills', PurchaseBill),
        ('Purchase Requests', PurchaseRequest),
        ('Expenses', Expense),
        ('Customers', Customer),
        ('Vendors', Vendor),
        ('Items', Item),
        ('Item Categories', ItemCategory),
        ('Item Groups', ItemGroup),
        ('Attendance', Attendance),
        ('Sites', Site),
        ('Employees', Employee),
        ('Expense Categories', ExpenseCategory),
    ]
    
    for name, model in models_to_delete:
        try:
            count = model.query.filter_by(tenant_id=tenant_id).delete()
            if count > 0:
                deleted_counts[name] = count
        except Exception as e:
            print(f"⚠️  Warning: Could not delete {name}: {e}")
    
    return deleted_counts


def delete_tenant(tenant_id=None, subdomain=None):
    """Main deletion function"""
    with app.app_context():
        # Find tenant
        if tenant_id:
            tenant = Tenant.query.get(tenant_id)
        elif subdomain:
            tenant = Tenant.query.filter_by(subdomain=subdomain).first()
        else:
            print("❌ Error: Must provide either tenant_id or subdomain")
            return False
        
        if not tenant:
            print(f"❌ Tenant not found!")
            return False
        
        # Show tenant info
        print("\n" + "="*60)
        print(f"🗑️  DELETING TENANT")
        print("="*60)
        print(f"ID: {tenant.id}")
        print(f"Company: {tenant.company_name}")
        print(f"Subdomain: {tenant.subdomain}")
        print(f"Admin Email: {tenant.admin_email}")
        print("="*60)
        
        # Confirmation
        confirm = input("\n⚠️  Are you sure? This cannot be undone! (type 'DELETE' to confirm): ")
        if confirm != 'DELETE':
            print("❌ Deletion cancelled")
            return False
        
        print("\n🔄 Deleting tenant data...")
        
        # Delete database records
        deleted_counts = delete_tenant_data(tenant.id)
        
        # Delete files
        print("\n🔄 Deleting uploaded files...")
        deleted_files, deleted_folders = delete_tenant_files(tenant.id)
        
        # Delete tenant record itself
        tenant_name = tenant.company_name
        db.session.delete(tenant)
        db.session.commit()
        
        # Summary
        print("\n" + "="*60)
        print("✅ DELETION COMPLETE")
        print("="*60)
        
        print("\n📊 Database Records Deleted:")
        if deleted_counts:
            for name, count in deleted_counts.items():
                print(f"   • {name}: {count}")
        else:
            print("   (none)")
        
        print(f"\n📁 Files Deleted: {len(deleted_files)}")
        if deleted_files and len(deleted_files) <= 20:
            for file in deleted_files:
                print(f"   • {file}")
        elif deleted_files:
            print(f"   (showing first 20 of {len(deleted_files)})")
            for file in deleted_files[:20]:
                print(f"   • {file}")
        
        print(f"\n📂 Folders Deleted: {len(deleted_folders)}")
        for folder in deleted_folders:
            print(f"   • {folder}")
        
        print(f"\n✅ Tenant '{tenant_name}' has been completely removed!")
        print("="*60 + "\n")
        
        return True


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    tenant_id = None
    subdomain = None
    
    if sys.argv[1] == '--subdomain':
        if len(sys.argv) < 3:
            print("❌ Error: --subdomain requires a value")
            print(__doc__)
            sys.exit(1)
        subdomain = sys.argv[2]
    else:
        try:
            tenant_id = int(sys.argv[1])
        except ValueError:
            print(f"❌ Error: Invalid tenant_id '{sys.argv[1]}'")
            print(__doc__)
            sys.exit(1)
    
    success = delete_tenant(tenant_id=tenant_id, subdomain=subdomain)
    sys.exit(0 if success else 1)

