#!/bin/bash

# Run BizBooks Locally with Production Supabase Database
# This connects to your US-EAST production database

echo "🚀 Starting BizBooks Locally with Production Supabase..."
echo ""
echo "⚠️  WARNING: You are connecting to PRODUCTION database!"
echo "    Any changes you make will affect production data."
echo ""
echo "✅ Benefits:"
echo "   - Test with real data"
echo "   - Verify migration on actual invoices"
echo "   - See real Trial Balance"
echo ""

# Navigate to app directory
cd "$(dirname "$0")"

# Temporarily rename .env.local if it exists
if [ -f ".env.local" ]; then
    echo "📝 Temporarily disabling .env.local (will restore on exit)..."
    mv .env.local .env.local.temp
    RESTORE_ENV=true
else
    RESTORE_ENV=false
fi

# Set up trap to restore .env.local on script exit
cleanup() {
    if [ "$RESTORE_ENV" = true ]; then
        echo ""
        echo "🔄 Restoring .env.local..."
        mv .env.local.temp .env.local
    fi
}
trap cleanup EXIT INT TERM

# Set database URL (US-EAST Supabase with Session Pooler)
export DATABASE_URL="postgresql://postgres.dkpksyzoiicnuggfvyth:Ayushij%40in1@aws-0-us-east-1.pooler.supabase.com:6543/postgres"

# Run the application
echo ""
echo "🗄️  Database: Production Supabase (US-EAST)"
echo "Starting server on http://localhost:5001"
echo ""
echo "📝 Your tenants:"
echo "   - mahaveerelectricals"
echo "   - clothing"
echo "   - (any others you created)"
echo ""
echo "🔗 Login URLs:"
echo "   http://mahaveerelectricals.lvh.me:5001/admin/login"
echo "   http://clothing.lvh.me:5001/admin/login"
echo ""
echo "💡 Use Ctrl+C to stop the server"
echo ""

python3 run_local.py

