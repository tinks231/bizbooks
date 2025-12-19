"""
Diagnostic tool to check inventory and equity status
"""

from flask import Blueprint, jsonify, g
from models import db
from sqlalchemy import text
from decimal import Decimal

diagnose_inventory_equity_bp = Blueprint('diagnose_inventory_equity', __name__, url_prefix='/diagnose')


@diagnose_inventory_equity_bp.route('/inventory-equity')
def diagnose_inventory_equity():
    """
    Check current tenant's inventory and equity status
    This helps diagnose why trial balance is out of balance
    """
    
    try:
        # Get current tenant from subdomain
        tenant_id = g.get('tenant_id')
        
        if not tenant_id:
            return jsonify({
                'error': 'No tenant found. Make sure you\'re accessing via subdomain (e.g., ayushi.bizbooks.co.in)'
            }), 400
        
        print(f"\n{'=' * 80}")
        print(f"🔍 INVENTORY & EQUITY DIAGNOSIS FOR TENANT: {tenant_id}")
        print(f"{'=' * 80}")
        
        results = {
            'tenant_id': tenant_id,
            'items_count': 0,
            'item_stocks_count': 0,
            'total_stock_value': 0,
            'equity_entries': [],
            'trial_balance': {},
            'recommendation': ''
        }
        
        # 1. Check items count
        items_count = db.session.execute(text("""
            SELECT COUNT(*) FROM items WHERE tenant_id = :tenant_id
        """), {'tenant_id': tenant_id}).fetchone()[0]
        results['items_count'] = items_count
        print(f"\n📦 Items: {items_count}")
        
        # 2. Check item_stocks entries
        item_stocks = db.session.execute(text("""
            SELECT 
                COUNT(*) as count,
                COALESCE(SUM(stock_value), 0) as total_value
            FROM item_stocks
            WHERE tenant_id = :tenant_id
        """), {'tenant_id': tenant_id}).fetchone()
        
        results['item_stocks_count'] = item_stocks[0]
        results['total_stock_value'] = float(item_stocks[1])
        print(f"📊 Item Stocks: {item_stocks[0]} records")
        print(f"💰 Total Stock Value: ₹{item_stocks[1]:,.2f}")
        
        # 3. Check existing equity entries
        equity_entries = db.session.execute(text("""
            SELECT 
                id,
                transaction_date,
                transaction_type,
                credit_amount,
                narration
            FROM account_transactions
            WHERE tenant_id = :tenant_id
            AND (transaction_type = 'opening_balance_inventory_equity'
                 OR narration LIKE '%Inventory%Opening%')
            ORDER BY transaction_date DESC
        """), {'tenant_id': tenant_id}).fetchall()
        
        for entry in equity_entries:
            results['equity_entries'].append({
                'id': entry[0],
                'date': str(entry[1]),
                'type': entry[2],
                'credit_amount': float(entry[3]),
                'narration': entry[4]
            })
        
        print(f"\n🏦 Equity Entries Found: {len(equity_entries)}")
        for entry in equity_entries:
            print(f"  - ID {entry[0]}: ₹{entry[3]:,.2f} on {entry[1]}")
            print(f"    Narration: {entry[4]}")
        
        # 4. Check trial balance
        trial_balance = db.session.execute(text("""
            SELECT 
                COALESCE(SUM(debit_amount), 0) as total_debit,
                COALESCE(SUM(credit_amount), 0) as total_credit
            FROM account_transactions
            WHERE tenant_id = :tenant_id
        """), {'tenant_id': tenant_id}).fetchone()
        
        total_debit = float(trial_balance[0])
        total_credit = float(trial_balance[1])
        difference = total_debit - total_credit
        
        results['trial_balance'] = {
            'total_debit': total_debit,
            'total_credit': total_credit,
            'difference': difference,
            'is_balanced': abs(difference) < 0.01
        }
        
        print(f"\n📊 TRIAL BALANCE:")
        print(f"  Total Debits:  ₹{total_debit:,.2f}")
        print(f"  Total Credits: ₹{total_credit:,.2f}")
        print(f"  Difference:    ₹{difference:,.2f}")
        
        if abs(difference) < 0.01:
            print(f"  ✅ BALANCED!")
        else:
            print(f"  ❌ OUT OF BALANCE")
        
        # 5. Generate recommendation
        if results['total_stock_value'] > 0:
            if len(equity_entries) == 0:
                results['recommendation'] = f"⚠️ PROBLEM FOUND: You have ₹{results['total_stock_value']:,.2f} in inventory but NO equity entry! Run the fix migration."
                results['action'] = 'Run: /migration/fix-inventory-equity'
            else:
                equity_total = sum([float(e[3]) for e in equity_entries])
                if abs(equity_total - results['total_stock_value']) > 0.01:
                    results['recommendation'] = f"⚠️ MISMATCH: Stock value (₹{results['total_stock_value']:,.2f}) doesn't match equity entries (₹{equity_total:,.2f})"
                    results['action'] = 'Manual review needed - values don\'t match'
                else:
                    results['recommendation'] = f"✅ Equity entries exist and match stock value! Trial balance issue might be elsewhere."
                    results['action'] = 'Check other account entries'
        else:
            results['recommendation'] = "ℹ️ No inventory value found. Equity entries not needed."
            results['action'] = 'None - no inventory to fix'
        
        print(f"\n{'=' * 80}")
        print(f"💡 RECOMMENDATION:")
        print(f"   {results['recommendation']}")
        print(f"   {results['action']}")
        print(f"{'=' * 80}\n")
        
        return jsonify({
            'status': 'success',
            'diagnosis': results
        })
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

