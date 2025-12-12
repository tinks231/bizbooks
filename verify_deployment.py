#!/usr/bin/env python3
"""
Verify that the new code is deployed by checking the generate_bill_number method
Run this on PRODUCTION server to verify deployment
"""
import sys
sys.path.insert(0, 'modular_app')

from models.purchase_bill import PurchaseBill
import inspect

print("="*60)
print("DEPLOYMENT VERIFICATION")
print("="*60)

# Check the generate_bill_number method source
source = inspect.getsource(PurchaseBill.generate_bill_number)

if "ROBUST VERSION" in source:
    print("✅ NEW CODE DEPLOYED!")
    print("   The fix for duplicate bill numbers is active.")
elif "duplicate handling" in source:
    print("⚠️  INTERMEDIATE VERSION")
    print("   Has some fixes but not the latest robust version.")
else:
    print("❌ OLD CODE STILL RUNNING!")
    print("   The fixes have NOT been deployed yet.")

print("\nCode signature check:")
if "max_num = max(max_num, num)" in source:
    print("✅ Using MAX number strategy (correct!)")
else:
    print("❌ Not using MAX number strategy")

if "DOUBLE CHECK" in source:
    print("✅ Has double-check for race conditions")
else:
    print("❌ Missing double-check")

if "timestamp" in source.lower():
    print("✅ Has timestamp fallback")
else:
    print("❌ Missing timestamp fallback")

print("\n" + "="*60)
print("INSTRUCTIONS:")
print("="*60)
if "ROBUST VERSION" not in source:
    print("\n❌ CODE NOT DEPLOYED! Do this:")
    print("   1. SSH into production server")
    print("   2. cd /path/to/bizbooks")
    print("   3. git pull origin main")
    print("   4. Find and delete all .pyc files:")
    print("      find . -name '*.pyc' -delete")
    print("   5. Restart server:")
    print("      sudo systemctl restart bizbooks")
    print("      (or whatever restart command you use)")
    print("   6. Run this script again to verify")
else:
    print("\n✅ All good! Try creating a purchase bill now.")

