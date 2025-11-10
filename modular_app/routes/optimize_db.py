"""
Database Optimization & Diagnostics

This route helps identify and fix performance issues by:
1. Checking which indexes exist
2. Running ANALYZE to update query planner statistics
3. Testing query performance before/after
"""

from flask import Blueprint, jsonify, g, session, redirect, url_for, flash
from models import db
from utils.tenant_middleware import get_current_tenant_id
import os
import time

optimize_db_bp = Blueprint('optimize_db', __name__, url_prefix='/optimize')

@optimize_db_bp.route('/analyze-database', methods=['GET'])
def analyze_database():
    """
    Run ANALYZE on all critical tables to update query planner statistics.
    This forces PostgreSQL to recognize and use the new indexes.
    
    WHEN TO RUN:
    - After adding new indexes
    - When queries are still slow despite indexes
    - Monthly for optimal performance
    """
    
    # Check if user is logged in as admin
    if 'tenant_admin_id' not in session:
        return redirect(url_for('admin.login'))
    
    try:
        # Detect database type
        database_url = os.environ.get('DATABASE_URL', '')
        is_postgres = 'postgres' in database_url.lower()
        
        if not is_postgres:
            flash('⚠️ Database optimization is only needed for PostgreSQL. SQLite auto-optimizes.', 'info')
            return redirect(url_for('admin.dashboard'))
        
        print("\n" + "="*80)
        print("🔧 DATABASE OPTIMIZATION: Running ANALYZE")
        print("="*80)
        
        # Tables to analyze (most critical first)
        tables_to_analyze = [
            'items',
            'item_stock',
            'invoices',
            'purchase_bills',
            'sales_orders',
            'expenses',
            'delivery_challans',
            'customers',
            'vendors',
            'purchase_bill_items',
            'invoice_items',
            'sales_order_items'
        ]
        
        analyzed = []
        failed = []
        
        for table in tables_to_analyze:
            try:
                start_time = time.time()
                
                # Run ANALYZE on table
                db.session.execute(db.text(f"ANALYZE {table};"))
                db.session.commit()
                
                elapsed = (time.time() - start_time) * 1000  # Convert to ms
                
                print(f"✅ {table} - Analyzed in {elapsed:.0f}ms")
                analyzed.append(table)
                
            except Exception as e:
                print(f"⚠️  {table} - Skipped: {str(e)}")
                failed.append(table)
                db.session.rollback()
        
        # Also run VACUUM ANALYZE for better optimization (background operation)
        try:
            print("\n🔧 Running VACUUM ANALYZE (this may take 1-2 minutes)...")
            # Note: VACUUM can't run inside a transaction block
            # We'll skip this for now as it requires special handling
            print("⏭️  VACUUM skipped (requires manual execution)")
        except Exception as e:
            print(f"⚠️  VACUUM failed: {str(e)}")
        
        print("="*80)
        print("✅ DATABASE OPTIMIZATION COMPLETE!")
        print(f"   - Tables Analyzed: {len(analyzed)}")
        print(f"   - Tables Skipped: {len(failed)}")
        print()
        print("NEXT STEPS:")
        print("   1. Test 'All Items' page → Should be faster now")
        print("   2. Test 'Stock Summary' → Should be faster now")
        print("   3. If still slow, we need deeper investigation")
        print("="*80 + "\n")
        
        flash(f'✅ Database Optimized! Analyzed {len(analyzed)} tables. Query planner now knows about the indexes. Try loading pages now!', 'success')
        return redirect(url_for('admin.dashboard'))
        
    except Exception as e:
        db.session.rollback()
        print(f"\n❌ ERROR: {str(e)}\n")
        flash(f'❌ Error optimizing database: {str(e)}', 'error')
        return redirect(url_for('admin.dashboard'))


@optimize_db_bp.route('/check-indexes', methods=['GET'])
def check_indexes():
    """
    Diagnostic route: Check which indexes exist and their usage statistics
    """
    
    # Check if user is logged in as admin
    if 'tenant_admin_id' not in session:
        return redirect(url_for('admin.login'))
    
    try:
        # Detect database type
        database_url = os.environ.get('DATABASE_URL', '')
        is_postgres = 'postgres' in database_url.lower()
        
        if not is_postgres:
            return jsonify({
                'status': 'info',
                'message': 'Index checking is only available for PostgreSQL',
                'database_type': 'SQLite'
            })
        
        # Get all indexes related to our performance optimization
        query = """
        SELECT 
            schemaname,
            tablename,
            indexname,
            tablespace,
            indexdef
        FROM pg_indexes
        WHERE indexname LIKE 'idx_%'
        ORDER BY tablename, indexname;
        """
        
        result = db.session.execute(db.text(query))
        indexes = []
        
        for row in result:
            indexes.append({
                'table': row[1],
                'index_name': row[2],
                'definition': row[4]
            })
        
        # Group by table
        tables = {}
        for idx in indexes:
            table = idx['table']
            if table not in tables:
                tables[table] = []
            tables[table].append(idx)
        
        return jsonify({
            'status': 'success',
            'total_indexes': len(indexes),
            'tables_with_indexes': len(tables),
            'indexes_by_table': tables,
            'recommendation': 'If you see fewer than 17 indexes, some are missing. Run /migrate/add-performance-indexes again.'
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        })


@optimize_db_bp.route('/test-query-speed', methods=['GET'])
def test_query_speed():
    """
    Test the speed of critical queries to identify bottlenecks
    """
    
    # Check if user is logged in as admin
    if 'tenant_admin_id' not in session:
        return redirect(url_for('admin.login'))
    
    tenant_id = get_current_tenant_id()
    
    try:
        from models import Item, ItemStock
        import time
        
        results = {}
        
        # Test 1: Items query (what "All Items" page does)
        start = time.time()
        items_query = Item.query.filter_by(tenant_id=tenant_id, is_active=True).limit(50).all()
        results['items_query'] = {
            'time_ms': (time.time() - start) * 1000,
            'records': len(items_query)
        }
        
        # Test 2: Stock query (what "Stock Summary" page does)
        start = time.time()
        stock_query = ItemStock.query.filter_by(tenant_id=tenant_id).limit(100).all()
        results['stock_query'] = {
            'time_ms': (time.time() - start) * 1000,
            'records': len(stock_query)
        }
        
        # Test 3: Full page simulation (items + stock counts)
        start = time.time()
        items = Item.query.filter_by(tenant_id=tenant_id, is_active=True).limit(50).all()
        for item in items:
            _ = item.get_total_stock()
        results['full_page_simulation'] = {
            'time_ms': (time.time() - start) * 1000,
            'records': len(items)
        }
        
        # Analysis
        interpretation = []
        
        if results['items_query']['time_ms'] < 200:
            interpretation.append('✅ Items query is FAST (<200ms)')
        elif results['items_query']['time_ms'] < 500:
            interpretation.append('⚠️ Items query is OK (200-500ms) - could be better')
        else:
            interpretation.append('🔴 Items query is SLOW (>500ms) - indexes not being used!')
        
        if results['stock_query']['time_ms'] < 200:
            interpretation.append('✅ Stock query is FAST (<200ms)')
        elif results['stock_query']['time_ms'] < 500:
            interpretation.append('⚠️ Stock query is OK (200-500ms) - could be better')
        else:
            interpretation.append('🔴 Stock query is SLOW (>500ms) - indexes not being used!')
        
        if results['full_page_simulation']['time_ms'] < 500:
            interpretation.append('✅ Full page render is FAST (<500ms)')
        elif results['full_page_simulation']['time_ms'] < 1000:
            interpretation.append('⚠️ Full page render is OK (500ms-1s) - acceptable')
        else:
            interpretation.append('🔴 Full page render is SLOW (>1s) - N+1 query problem!')
        
        return jsonify({
            'status': 'success',
            'tenant_id': tenant_id,
            'test_results': results,
            'interpretation': interpretation,
            'recommendation': 'If any query is >500ms, run /optimize/analyze-database'
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        })

