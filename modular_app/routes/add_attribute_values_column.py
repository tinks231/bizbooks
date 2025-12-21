"""
Migration: Add attribute_values JSONB column to items table

This column will store dynamic attribute values for each item, allowing:
- Clothing: {"brand": "Levi's", "size": "32", "color": "Blue", "style": "Slim Fit"}
- Pharmacy: {"medicine_name": "Paracetamol", "batch": "B123", "expiry": "2025-12"}
- Mobile: {"brand": "Apple", "model": "iPhone 15", "imei": "123456789", "storage": "128GB"}
- Bakery: {"flavor": "Chocolate", "weight": "2kg", "packaging": "Box"}

Created: Dec 21, 2025
"""

from flask import Blueprint, render_template_string, request
from models import db
from utils.tenant_middleware import require_tenant
from sqlalchemy import text
from datetime import datetime

add_attribute_values_column_bp = Blueprint('add_attribute_values_column', __name__)


@add_attribute_values_column_bp.route('/migration/add-attribute-values-column', methods=['GET'])
@require_tenant
def show_migration_page():
    """Show migration confirmation page"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Add Attribute Values Column</title>
        <style>
            body { font-family: Arial; max-width: 800px; margin: 50px auto; padding: 20px; }
            .warning { background: #fff3cd; padding: 20px; border-radius: 8px; margin: 20px 0; }
            .info { background: #d1ecf1; padding: 20px; border-radius: 8px; margin: 20px 0; }
            .btn { 
                background: #667eea; 
                color: white; 
                padding: 12px 24px; 
                border: none; 
                border-radius: 6px; 
                font-size: 16px; 
                cursor: pointer; 
                text-decoration: none;
                display: inline-block;
            }
            .btn:hover { background: #5568d3; }
            h1 { color: #333; }
            code { background: #f8f9fa; padding: 2px 6px; border-radius: 3px; }
        </style>
    </head>
    <body>
        <h1>🔧 Migration: Add Attribute Values Column</h1>
        
        <div class="info">
            <h3>📋 What This Does:</h3>
            <ul>
                <li>Adds <code>attribute_values</code> JSONB column to <code>items</code> table</li>
                <li>Allows storing dynamic attributes per item</li>
                <li>Backward compatible - existing items continue working</li>
                <li>Enables Phase 3 attribute functionality</li>
            </ul>
        </div>
        
        <div class="warning">
            <h3>⚠️ Before Running:</h3>
            <ul>
                <li>This is a <strong>one-time</strong> migration</li>
                <li>Safe to run - only adds a column, doesn't modify data</li>
                <li>Existing items will have <code>null</code> attribute values (OK!)</li>
                <li>New items will populate attribute values automatically</li>
            </ul>
        </div>
        
        <h3>🎯 Example Attribute Values:</h3>
        <pre style="background: #f8f9fa; padding: 15px; border-radius: 8px;">
Clothing:
{"brand": "Levi's", "size": "32", "color": "Blue", "style": "Slim Fit"}

Pharmacy:
{"medicine_name": "Paracetamol", "batch": "B123", "expiry": "2025-12"}

Mobile:
{"brand": "Apple", "model": "iPhone 15", "imei": "123456789"}

Bakery:
{"flavor": "Chocolate", "weight": "2kg", "packaging": "Box"}
        </pre>
        
        <form method="POST" onsubmit="return confirm('Run migration now?');">
            <button type="submit" class="btn">▶️ Run Migration</button>
        </form>
        
        <p style="margin-top: 20px; color: #666;">
            <small>This migration is required for Phase 3 attribute functionality.</small>
        </p>
    </body>
    </html>
    """
    return render_template_string(html)


@add_attribute_values_column_bp.route('/migration/add-attribute-values-column', methods=['POST'])
@require_tenant
def run_migration():
    """Execute the migration"""
    try:
        # Check if column already exists
        result = db.session.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'items' 
            AND column_name = 'attribute_values'
        """)).fetchone()
        
        if result:
            return render_template_string("""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Migration Already Applied</title>
                    <style>
                        body { font-family: Arial; max-width: 800px; margin: 50px auto; padding: 20px; }
                        .success { background: #d4edda; padding: 20px; border-radius: 8px; color: #155724; }
                        .btn { 
                            background: #667eea; 
                            color: white; 
                            padding: 12px 24px; 
                            border: none; 
                            border-radius: 6px; 
                            text-decoration: none;
                            display: inline-block;
                            margin-top: 15px;
                        }
                    </style>
                </head>
                <body>
                    <div class="success">
                        <h2>✅ Column Already Exists</h2>
                        <p>The <code>attribute_values</code> column is already present in the <code>items</code> table.</p>
                        <p>No action needed!</p>
                    </div>
                    <a href="/admin/settings/item-attributes" class="btn">← Back to Attribute Settings</a>
                </body>
                </html>
            """)
        
        # Add the column
        db.session.execute(text("""
            ALTER TABLE items 
            ADD COLUMN attribute_values JSONB DEFAULT NULL
        """))
        
        # Add comment
        db.session.execute(text("""
            COMMENT ON COLUMN items.attribute_values IS 
            'Dynamic attribute values stored as JSON. Example: {"brand": "Levis", "size": "32", "color": "Blue"}'
        """))
        
        # Create index for better query performance
        db.session.execute(text("""
            CREATE INDEX idx_items_attribute_values 
            ON items USING GIN (attribute_values)
        """))
        
        db.session.commit()
        
        return render_template_string("""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Migration Successful</title>
                <style>
                    body { font-family: Arial; max-width: 800px; margin: 50px auto; padding: 20px; }
                    .success { background: #d4edda; padding: 20px; border-radius: 8px; color: #155724; }
                    .btn { 
                        background: #667eea; 
                        color: white; 
                        padding: 12px 24px; 
                        border: none; 
                        border-radius: 6px; 
                        text-decoration: none;
                        display: inline-block;
                        margin-top: 15px;
                    }
                    code { background: #f8f9fa; padding: 2px 6px; border-radius: 3px; }
                </style>
            </head>
            <body>
                <div class="success">
                    <h2>✅ Migration Successful!</h2>
                    <p>The following changes have been applied:</p>
                    <ul>
                        <li>✅ Added <code>attribute_values</code> JSONB column to <code>items</code> table</li>
                        <li>✅ Added GIN index for fast JSON queries</li>
                        <li>✅ Added column comment for documentation</li>
                    </ul>
                    <p><strong>Database is ready for Phase 3 attribute functionality!</strong></p>
                </div>
                <a href="/admin/settings/item-attributes" class="btn">← Back to Attribute Settings</a>
            </body>
            </html>
        """)
        
    except Exception as e:
        db.session.rollback()
        return render_template_string("""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Migration Failed</title>
                <style>
                    body { font-family: Arial; max-width: 800px; margin: 50px auto; padding: 20px; }
                    .error { background: #f8d7da; padding: 20px; border-radius: 8px; color: #721c24; }
                    .btn { 
                        background: #667eea; 
                        color: white; 
                        padding: 12px 24px; 
                        border: none; 
                        border-radius: 6px; 
                        text-decoration: none;
                        display: inline-block;
                        margin-top: 15px;
                    }
                    pre { background: #f8f9fa; padding: 15px; border-radius: 8px; overflow-x: auto; }
                </style>
            </head>
            <body>
                <div class="error">
                    <h2>❌ Migration Failed</h2>
                    <p><strong>Error:</strong></p>
                    <pre>{{ error }}</pre>
                    <p>Please check the error message and try again.</p>
                </div>
                <a href="/migration/add-attribute-values-column" class="btn">← Try Again</a>
            </body>
            </html>
        """, error=str(e))

