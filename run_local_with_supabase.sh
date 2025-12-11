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

# Set database URL (US-EAST Supabase with Session Pooler)
export DATABASE_URL="postgresql://postgres.dkpksyzoiicnuggfvyth:Ayushij%40in1@aws-0-us-east-1.pooler.supabase.com:6543/postgres"

# Navigate to app directory
cd "$(dirname "$0")"

# Run the application
echo "Starting server on http://localhost:5001"
echo ""
echo "📝 Your tenants:"
echo "   - ayushi"
echo "   - clothing"
echo "   - mahaveerelectricals"
echo "   - (any others you created)"
echo ""
echo "🔗 Login at: http://localhost:5001/login"
echo ""

python3 run_local.py

