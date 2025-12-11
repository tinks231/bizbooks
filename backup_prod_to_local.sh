#!/bin/bash

# ═══════════════════════════════════════════════════════════════════════════════
# BizBooks: Backup Production Supabase → Restore to Local PostgreSQL
# ═══════════════════════════════════════════════════════════════════════════════
# 
# Purpose: Create a local copy of production data for safe testing
# 
# Usage:
#   ./backup_prod_to_local.sh
#
# What it does:
#   1. Downloads latest data from production Supabase (US-EAST)
#   2. Creates/recreates local database "bizbooks_test"
#   3. Imports all data (tenants, invoices, customers, etc.)
#   4. Verifies data was imported correctly
#
# ═══════════════════════════════════════════════════════════════════════════════

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROD_HOST="db.dkpksyzoiicnuggfvyth.supabase.co"
PROD_PORT="5432"
PROD_USER="postgres"
PROD_PASSWORD="Ayushij@in1"
PROD_DB="postgres"

LOCAL_HOST="localhost"
LOCAL_PORT="5432"
LOCAL_USER="bizbooks_dev"
LOCAL_PASSWORD="local_dev_password_123"
LOCAL_DB="bizbooks_test"

BACKUP_FILE="bizbooks_backup_$(date +%Y%m%d_%H%M%S).sql"

# ═══════════════════════════════════════════════════════════════════════════════
# Step 1: Backup Production Database
# ═══════════════════════════════════════════════════════════════════════════════

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}📦 BIZBOOKS: Production → Local Database Copy${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo ""

echo -e "${YELLOW}⏳ Step 1/4: Backing up production database...${NC}"
echo "   Source: Supabase (US-EAST)"
echo "   File: $BACKUP_FILE"
echo ""

PGPASSWORD="$PROD_PASSWORD" pg_dump \
    -h "$PROD_HOST" \
    -p "$PROD_PORT" \
    -U "$PROD_USER" \
    -d "$PROD_DB" \
    --no-owner \
    --no-acl \
    --clean \
    --if-exists \
    > "$BACKUP_FILE"

BACKUP_SIZE=$(ls -lh "$BACKUP_FILE" | awk '{print $5}')
echo -e "${GREEN}✅ Backup complete! Size: $BACKUP_SIZE${NC}"
echo ""

# ═══════════════════════════════════════════════════════════════════════════════
# Step 2: Check Local PostgreSQL
# ═══════════════════════════════════════════════════════════════════════════════

echo -e "${YELLOW}⏳ Step 2/4: Checking local PostgreSQL...${NC}"

if ! pg_isready -h "$LOCAL_HOST" -p "$LOCAL_PORT" > /dev/null 2>&1; then
    echo -e "${RED}❌ ERROR: Local PostgreSQL is not running!${NC}"
    echo ""
    echo "   Please start PostgreSQL first:"
    echo "   brew services start postgresql@17"
    echo ""
    exit 1
fi

echo -e "${GREEN}✅ Local PostgreSQL is running${NC}"
echo ""

# ═══════════════════════════════════════════════════════════════════════════════
# Step 3: Create/Recreate Local Database
# ═══════════════════════════════════════════════════════════════════════════════

echo -e "${YELLOW}⏳ Step 3/4: Creating local test database...${NC}"

PGPASSWORD="$LOCAL_PASSWORD" psql \
    -h "$LOCAL_HOST" \
    -p "$LOCAL_PORT" \
    -U "$LOCAL_USER" \
    -d postgres \
    -c "DROP DATABASE IF EXISTS $LOCAL_DB;" \
    -c "CREATE DATABASE $LOCAL_DB;" \
    > /dev/null 2>&1

echo -e "${GREEN}✅ Database '$LOCAL_DB' created${NC}"
echo ""

# ═══════════════════════════════════════════════════════════════════════════════
# Step 4: Import Data
# ═══════════════════════════════════════════════════════════════════════════════

echo -e "${YELLOW}⏳ Step 4/4: Importing production data...${NC}"
echo "   This may take 1-3 minutes depending on data size..."
echo ""

PGPASSWORD="$LOCAL_PASSWORD" psql \
    -h "$LOCAL_HOST" \
    -p "$LOCAL_PORT" \
    -U "$LOCAL_USER" \
    -d "$LOCAL_DB" \
    -f "$BACKUP_FILE" \
    > import_log.txt 2>&1

# Check for critical errors
if grep -q "ERROR.*FATAL" import_log.txt; then
    echo -e "${RED}❌ Import had critical errors! Check import_log.txt${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Data imported successfully${NC}"
echo ""

# ═══════════════════════════════════════════════════════════════════════════════
# Step 5: Verify Data
# ═══════════════════════════════════════════════════════════════════════════════

echo -e "${BLUE}📊 Verifying imported data...${NC}"
echo ""

PGPASSWORD="$LOCAL_PASSWORD" psql \
    -h "$LOCAL_HOST" \
    -p "$LOCAL_PORT" \
    -U "$LOCAL_USER" \
    -d "$LOCAL_DB" \
    -c "
    SELECT 
        '  Tenants:    ' || LPAD(COUNT(*)::text, 6) as info FROM tenants
    UNION ALL
    SELECT '  Customers: ' || LPAD(COUNT(*)::text, 6) FROM customers
    UNION ALL
    SELECT '  Items:     ' || LPAD(COUNT(*)::text, 6) FROM items
    UNION ALL
    SELECT '  Invoices:  ' || LPAD(COUNT(*)::text, 6) FROM invoices
    UNION ALL
    SELECT '  Purchases: ' || LPAD(COUNT(*)::text, 6) FROM purchase_bills
    UNION ALL
    SELECT '  Employees: ' || LPAD(COUNT(*)::text, 6) FROM employees;
    " -t

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}🎉 SUCCESS! Production data copied to local database${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}📝 Next steps:${NC}"
echo ""
echo "   1. Update .env.local to use local database:"
echo "      DATABASE_URL=postgresql://$LOCAL_USER:$LOCAL_PASSWORD@$LOCAL_HOST:$LOCAL_PORT/$LOCAL_DB"
echo ""
echo "   2. Start the app:"
echo "      source venv/bin/activate"
echo "      python3 run_local.py"
echo ""
echo "   3. Access your tenants:"
echo "      http://mahaveerelectricals.lvh.me:5001/admin/login"
echo "      http://ayushi.lvh.me:5001/admin/login"
echo "      http://clothing.lvh.me:5001/admin/login"
echo ""
echo -e "${GREEN}✅ Safe to test! Changes won't affect production!${NC}"
echo ""
echo -e "${YELLOW}📦 Backup saved as: $BACKUP_FILE${NC}"
echo ""

