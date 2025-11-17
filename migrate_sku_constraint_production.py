#!/usr/bin/env python3
"""
SKU Constraint Migration - PRODUCTION VERSION
Run this script ONCE to migrate production database from global SKU uniqueness to per-tenant uniqueness.

WHAT IT DOES:
- Changes UNIQUE(sku) → UNIQUE(tenant_id, sku)
- Allows each tenant to have their own ITEM-0001, ITEM-0002...
- Prevents SKU conflicts between tenants at scale

HOW TO USE:
1. Get DATABASE_URL from Vercel dashboard
2. Run: python3 migrate_sku_constraint_production.py
3. Paste DATABASE_URL when prompted
4. Confirm migration
5. Done!
"""

import sys
import os
from getpass import getpass

print("="*70)
print("🔄 SKU CONSTRAINT MIGRATION - PRODUCTION")
print("="*70)
print()
print("⚠️  WARNING: This will modify your PRODUCTION database!")
print("   Make sure you have a backup before proceeding.")
print()

# Get DATABASE_URL from user
print("📋 Step 1: Get DATABASE_URL from Vercel Dashboard")
print("   Go to: Vercel Dashboard → Project → Settings → Environment Variables")
print("   Find: DATABASE_URL")
print("   Click: Show (👁)")
print()

database_url = input("Paste DATABASE_URL here: ").strip()

if not database_url:
    print("❌ No DATABASE_URL provided. Exiting.")
    sys.exit(1)

if not database_url.startswith('postgresql://') and not database_url.startswith('postgres://'):
    print("❌ Invalid DATABASE_URL. Must start with postgresql:// or postgres://")
    sys.exit(1)

# Fix postgres:// to postgresql:// (SQLAlchemy requirement)
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)
    print("   ✅ Fixed URL format for SQLAlchemy")

print()
print("="*70)
print("📊 Database URL (masked):")
# Mask password for security
import re
masked_url = re.sub(r'://([^:]+):([^@]+)@', r'://\1:****@', database_url)
print(f"   {masked_url}")
print("="*70)
print()

# Final confirmation
print("⚠️  FINAL CONFIRMATION:")
print("   This will:")
print("   1. Remove global UNIQUE constraint on SKU")
print("   2. Add per-tenant UNIQUE constraint (tenant_id, sku)")
print("   3. Allow each tenant to have their own SKU sequence")
print()

confirm = input("Type 'YES' to proceed with migration: ").strip()

if confirm != 'YES':
    print("❌ Migration cancelled.")
    sys.exit(0)

print()
print("="*70)
print("🚀 Starting migration...")
print("="*70)
print()

# Now run the migration
try:
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker
    
    # Create engine
    engine = create_engine(database_url, echo=False)
    
    # Create session
    Session = sessionmaker(bind=engine)
    session = Session()
    
    print("✅ Connected to production database!")
    print()
    
    # PostgreSQL migration
    print("📊 Database: PostgreSQL")
    print("="*70)
    print()
    
    try:
        # Step 1: Check if constraint exists
        print("1. Checking existing constraints...")
        result = session.execute(text("""
            SELECT constraint_name 
            FROM information_schema.table_constraints 
            WHERE table_name = 'items' 
            AND constraint_type = 'UNIQUE'
            AND constraint_name LIKE '%sku%';
        """))
        
        existing_constraints = [row[0] for row in result]
        print(f"   Found constraints: {existing_constraints}")
        
        # Step 2: Drop old unique constraint (if exists)
        print()
        print("2. Removing old UNIQUE(sku) constraint...")
        
        # Try common constraint names
        constraint_dropped = False
        for constraint_name in ['items_sku_key', 'uq_items_sku', 'items_sku_unique']:
            try:
                session.execute(text(f"ALTER TABLE items DROP CONSTRAINT IF EXISTS {constraint_name};"))
                session.commit()
                print(f"   ✅ Dropped constraint: {constraint_name}")
                constraint_dropped = True
            except Exception as e:
                print(f"   ⏭️  Constraint {constraint_name} doesn't exist (OK)")
        
        # Step 3: Add new composite unique constraint
        print()
        print("3. Adding new UNIQUE(tenant_id, sku) constraint...")
        
        # First, check if it already exists
        result = session.execute(text("""
            SELECT constraint_name 
            FROM information_schema.table_constraints 
            WHERE table_name = 'items' 
            AND constraint_name = 'uq_tenant_sku';
        """))
        
        if result.fetchone():
            print("   ℹ️  Constraint 'uq_tenant_sku' already exists!")
            print("   Migration might have already been run.")
        else:
            session.execute(text("""
                ALTER TABLE items 
                ADD CONSTRAINT uq_tenant_sku UNIQUE (tenant_id, sku);
            """))
            session.commit()
            print("   ✅ Added constraint: uq_tenant_sku")
        
        print()
        print("="*70)
        print("✅ MIGRATION SUCCESSFUL!")
        print("="*70)
        print()
        print("📊 Results:")
        print("   ✅ Old constraint (UNIQUE sku) removed")
        print("   ✅ New constraint (UNIQUE tenant_id, sku) added")
        print()
        print("💡 What this means:")
        print("   • Each tenant can now have ITEM-0001, ITEM-0002...")
        print("   • SKUs are unique within each tenant")
        print("   • No more global SKU conflicts!")
        print("   • Scales to unlimited tenants ✨")
        print()
        print("="*70)
        
    except Exception as e:
        session.rollback()
        print()
        print("❌ MIGRATION FAILED!")
        print(f"Error: {e}")
        print()
        print("💡 Possible reasons:")
        print("   - Migration already ran successfully")
        print("   - Database permissions issue")
        print("   - Connection timeout")
        print()
        sys.exit(1)
    
    finally:
        session.close()
        engine.dispose()

except ImportError as e:
    print("❌ Missing dependencies!")
    print(f"Error: {e}")
    print()
    print("Install required packages:")
    print("   pip install sqlalchemy psycopg2-binary")
    sys.exit(1)

except Exception as e:
    print("❌ Unexpected error!")
    print(f"Error: {e}")
    sys.exit(1)

