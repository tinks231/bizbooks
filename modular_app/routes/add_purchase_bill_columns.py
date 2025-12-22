"""
Migration: Add group_id and attribute_data_json to purchase_bill_items table
Required for Phase 3 of Purchase Bill Enhancement
"""
from flask import Blueprint, render_template_string, redirect, url_for, flash
from models import db
from sqlalchemy import text
from utils.tenant_middleware import require_tenant

add_purchase_bill_columns_bp = Blueprint('add_purchase_bill_columns', __name__)

@add_purchase_bill_columns_bp.route('/migration/add-purchase-bill-columns', methods=['GET'])
@require_tenant
def show_migration_page():
    """Show migration UI"""
    html = """
<!DOCTYPE html>
<html>
<head>
    <title>Add Purchase Bill Columns Migration</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            max-width: 900px;
            margin: 50px auto;
            padding: 20px;
            background: #f5f7fa;
        }
        .card {
            background: white;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        h1 {
            color: #2c3e50;
            margin-bottom: 10px;
        }
        .info {
            background: #e3f2fd;
            border-left: 4px solid #2196f3;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }
        .warning {
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }
        .success {
            background: #d4edda;
            border-left: 4px solid #28a745;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }
        .btn {
            background: #007bff;
            color: white;
            border: none;
            padding: 12px 24px;
            font-size: 16px;
            border-radius: 6px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            margin: 10px 0;
        }
        .btn:hover {
            background: #0056b3;
        }
        .btn-success {
            background: #28a745;
        }
        .btn-success:hover {
            background: #218838;
        }
        pre {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 4px;
            overflow-x: auto;
        }
        code {
            font-family: 'Courier New', monospace;
            background: #e9ecef;
            padding: 2px 6px;
            border-radius: 3px;
        }
    </style>
</head>
<body>
    <div class="card">
        <h1>🔧 Purchase Bill Columns Migration</h1>
        <p>This migration adds support for <strong>Group</strong> and <strong>Attributes</strong> in purchase bills.</p>
        
        <div class="info">
            <strong>📦 What This Migration Does:</strong>
            <ul>
                <li>Adds <code>group_id</code> column to <code>purchase_bill_items</code> table</li>
                <li>Adds <code>attribute_data_json</code> column to <code>purchase_bill_items</code> table</li>
            </ul>
        </div>
        
        <div class="warning">
            <strong>⚠️ Important:</strong>
            <ul>
                <li>This migration is <strong>NON-BREAKING</strong></li>
                <li>Existing purchase bills will continue to work</li>
                <li>New fields are nullable (optional)</li>
                <li>Safe to run on production</li>
            </ul>
        </div>
        
        <h3>📋 SQL Commands:</h3>
        <pre>-- Add group_id column
ALTER TABLE purchase_bill_items 
ADD COLUMN IF NOT EXISTS group_id INTEGER 
REFERENCES item_groups(id);

-- Add attribute_data_json column
ALTER TABLE purchase_bill_items 
ADD COLUMN IF NOT EXISTS attribute_data_json TEXT;</pre>
        
        <form method="POST" onsubmit="return confirm('Run migration now?');">
            <button type="submit" class="btn btn-success">▶️ Run Migration</button>
        </form>
        
        <a href="/admin/dashboard" class="btn">← Back to Dashboard</a>
    </div>
</body>
</html>
"""
    return render_template_string(html)


@add_purchase_bill_columns_bp.route('/migration/add-purchase-bill-columns', methods=['POST'])
@require_tenant
def add_purchase_bill_columns():
    """
    Add group_id and attribute_data_json columns to purchase_bill_items table
    NON-BREAKING: No changes to existing data
    """
    try:
        # Add group_id column
        db.session.execute(text("""
            ALTER TABLE purchase_bill_items 
            ADD COLUMN IF NOT EXISTS group_id INTEGER 
            REFERENCES item_groups(id);
        """))
        
        # Add attribute_data_json column
        db.session.execute(text("""
            ALTER TABLE purchase_bill_items 
            ADD COLUMN IF NOT EXISTS attribute_data_json TEXT;
        """))
        
        # Create index for group_id
        db.session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_purchase_bill_items_group 
            ON purchase_bill_items(group_id);
        """))
        
        db.session.commit()
        
        flash('✅ Migration completed! Columns added successfully.', 'success')
        return redirect(url_for('add_purchase_bill_columns.show_migration_page'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Migration failed: {str(e)}', 'error')
        return redirect(url_for('add_purchase_bill_columns.show_migration_page'))

