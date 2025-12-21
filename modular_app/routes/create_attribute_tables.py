"""
Migration: Create Item Attributes System Tables
Phase 1: Foundation - Create 3 new tables for variant attributes system
"""
from flask import Blueprint, jsonify, render_template_string
from models import db
from sqlalchemy import text
from utils.tenant_middleware import require_tenant

create_attribute_tables_bp = Blueprint('create_attribute_tables', __name__)

@create_attribute_tables_bp.route('/migration/create-attribute-tables', methods=['GET'])
@require_tenant
def show_migration_page():
    """Show migration page with button to execute"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Create Attribute Tables Migration</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
            .container { background: #f5f5f5; padding: 30px; border-radius: 10px; }
            h1 { color: #333; }
            .info { background: #e3f2fd; padding: 15px; border-left: 4px solid #2196F3; margin: 20px 0; }
            .warning { background: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 20px 0; }
            .success { background: #d4edda; padding: 15px; border-left: 4px solid #28a745; margin: 20px 0; }
            button { background: #4CAF50; color: white; padding: 15px 32px; border: none; 
                     border-radius: 5px; cursor: pointer; font-size: 16px; }
            button:hover { background: #45a049; }
            pre { background: #fff; padding: 10px; border-radius: 5px; overflow-x: auto; }
            .feature-list { list-style: none; padding-left: 0; }
            .feature-list li { padding: 5px 0; }
            .feature-list li:before { content: "✅ "; color: #28a745; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📦 Create Attribute Tables Migration</h1>
            
            <div class="info">
                <h3>What This Does:</h3>
                <p>Creates 3 new tables for the Variant Attributes System:</p>
                <ul class="feature-list">
                    <li><strong>item_attributes</strong> - Master attribute definitions (Size, Color, Brand, etc.)</li>
                    <li><strong>item_attribute_values</strong> - Actual values per item</li>
                    <li><strong>tenant_attribute_config</strong> - Tenant's configuration</li>
                </ul>
            </div>
            
            <div class="warning">
                <h3>⚠️ Important:</h3>
                <ul>
                    <li>This is a NON-BREAKING change</li>
                    <li>NO changes to existing tables</li>
                    <li>Existing items continue to work normally</li>
                    <li>Feature is OPT-IN (tenant must enable it)</li>
                    <li>Can be safely run on production</li>
                </ul>
            </div>
            
            <div style="margin: 30px 0;">
                <button onclick="runMigration()">Run Migration</button>
            </div>
            
            <div id="result"></div>
        </div>
        
        <script>
            async function runMigration() {
                const button = event.target;
                button.disabled = true;
                button.textContent = 'Running...';
                
                const resultDiv = document.getElementById('result');
                resultDiv.innerHTML = '<p>⏳ Creating tables...</p>';
                
                try {
                    const response = await fetch('/migration/create-attribute-tables', {
                        method: 'POST'
                    });
                    const data = await response.json();
                    
                    if (data.success) {
                        resultDiv.innerHTML = `
                            <div class="success">
                                <h3>✅ Migration Successful!</h3>
                                <p><strong>Tables Created:</strong></p>
                                <ul>
                                    ${data.tables_created.map(t => '<li>' + t + '</li>').join('')}
                                </ul>
                                <p><strong>Message:</strong> ${data.message}</p>
                            </div>
                        `;
                    } else {
                        resultDiv.innerHTML = `
                            <div style="background: #f8d7da; padding: 15px; border-left: 4px solid #dc3545; margin: 20px 0;">
                                <h3>❌ Migration Failed</h3>
                                <p><strong>Error:</strong> ${data.error}</p>
                                <pre>${data.traceback || ''}</pre>
                            </div>
                        `;
                        button.disabled = false;
                        button.textContent = 'Run Migration';
                    }
                } catch (error) {
                    resultDiv.innerHTML = `
                        <div style="background: #f8d7da; padding: 15px; border-left: 4px solid #dc3545; margin: 20px 0;">
                            <h3>❌ Request Failed</h3>
                            <p>${error.message}</p>
                        </div>
                    `;
                    button.disabled = false;
                    button.textContent = 'Run Migration';
                }
            }
        </script>
    </body>
    </html>
    """
    return render_template_string(html)


@create_attribute_tables_bp.route('/migration/create-attribute-tables', methods=['POST'])
@require_tenant
def create_attribute_tables():
    """
    Create 3 new tables for variant attributes system
    NON-BREAKING: No changes to existing tables
    """
    try:
        tables_created = []
        
        # ============================================================
        # TABLE 1: item_attributes (Master Attribute Definitions)
        # ============================================================
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS item_attributes (
                id SERIAL PRIMARY KEY,
                tenant_id INTEGER NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
                attribute_name VARCHAR(100) NOT NULL,
                attribute_type VARCHAR(50) NOT NULL,  -- 'text', 'number', 'date', 'dropdown'
                is_required BOOLEAN DEFAULT false,
                display_order INTEGER DEFAULT 0,
                is_active BOOLEAN DEFAULT true,
                
                -- For dropdown types
                dropdown_options JSONB,  -- e.g., ["S", "M", "L", "XL"]
                
                -- For auto-generated item name
                include_in_item_name BOOLEAN DEFAULT true,
                name_position INTEGER,  -- Order in name: 1=first, 2=second, etc.
                
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW(),
                
                CONSTRAINT uq_tenant_attribute_name UNIQUE(tenant_id, attribute_name)
            );
        """))
        tables_created.append('item_attributes')
        
        # Create indexes
        db.session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_item_attributes_tenant 
            ON item_attributes(tenant_id, is_active);
        """))
        
        # ============================================================
        # TABLE 2: item_attribute_values (Actual Values per Item)
        # ============================================================
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS item_attribute_values (
                id SERIAL PRIMARY KEY,
                tenant_id INTEGER NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
                item_id INTEGER NOT NULL REFERENCES items(id) ON DELETE CASCADE,
                attribute_id INTEGER NOT NULL REFERENCES item_attributes(id) ON DELETE CASCADE,
                attribute_value TEXT,
                
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW(),
                
                CONSTRAINT uq_item_attribute UNIQUE(item_id, attribute_id)
            );
        """))
        tables_created.append('item_attribute_values')
        
        # Create indexes
        db.session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_item_attribute_values_item 
            ON item_attribute_values(item_id);
        """))
        db.session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_item_attribute_values_attribute 
            ON item_attribute_values(attribute_id);
        """))
        db.session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_item_attribute_values_tenant 
            ON item_attribute_values(tenant_id);
        """))
        
        # ============================================================
        # TABLE 3: tenant_attribute_config (Tenant's Configuration)
        # ============================================================
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS tenant_attribute_config (
                id SERIAL PRIMARY KEY,
                tenant_id INTEGER NOT NULL REFERENCES tenants(id) ON DELETE CASCADE UNIQUE,
                industry_type VARCHAR(100),  -- 'clothing', 'pharmacy', 'electronics', etc.
                item_name_format TEXT,  -- Template: "{brand} {category} {product} {size} {color}"
                is_enabled BOOLEAN DEFAULT false,
                
                configured_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            );
        """))
        tables_created.append('tenant_attribute_config')
        
        # Create index
        db.session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_tenant_attribute_config_tenant 
            ON tenant_attribute_config(tenant_id);
        """))
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'All 3 tables created successfully! ✅',
            'tables_created': tables_created,
            'note': 'Existing items and invoices are unaffected. Feature is opt-in.'
        })
        
    except Exception as e:
        db.session.rollback()
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

