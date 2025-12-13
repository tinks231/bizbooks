"""
MIGRATION: Create Returns & Refunds Tables

Creates:
1. returns table - Main return/refund records
2. return_items table - Line items for each return

This enables professional return processing with:
- Inventory restocking
- Cash/Bank refunds
- GST credit notes
- Loyalty points reversal
- Accounting integration

Created: December 13, 2025
"""

from flask import Blueprint, jsonify
from models import db
from sqlalchemy import text

migration_returns_bp = Blueprint('migration_returns', __name__, url_prefix='/migration')


@migration_returns_bp.route('/create-returns-tables')
def create_returns_tables():
    """
    ONE-TIME migration: Create returns and return_items tables
    """
    
    try:
        print("\n" + "="*80)
        print("📦 CREATING RETURNS & REFUNDS TABLES")
        print("="*80 + "\n")
        
        # ============================================================
        # TABLE 1: returns (Main return records)
        # ============================================================
        print("📝 Creating 'returns' table...")
        
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS returns (
                -- Primary Key
                id SERIAL PRIMARY KEY,
                tenant_id INTEGER NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
                
                -- Return Identification
                return_number VARCHAR(50) UNIQUE NOT NULL,
                invoice_id INTEGER REFERENCES invoices(id) ON DELETE SET NULL,
                invoice_number VARCHAR(50),
                customer_id INTEGER REFERENCES customers(id) ON DELETE SET NULL,
                customer_name VARCHAR(255),
                
                -- Dates
                return_date DATE NOT NULL DEFAULT CURRENT_DATE,
                invoice_date DATE,
                
                -- Status Workflow
                status VARCHAR(20) NOT NULL DEFAULT 'pending',
                -- Values: pending, approved, rejected, completed, cancelled
                
                -- Financial Details
                total_amount DECIMAL(10,2) NOT NULL,
                taxable_amount DECIMAL(10,2),
                cgst_amount DECIMAL(10,2),
                sgst_amount DECIMAL(10,2),
                igst_amount DECIMAL(10,2),
                
                -- Refund Method
                refund_method VARCHAR(20) NOT NULL,
                -- Values: cash, bank, credit_note, exchange, pending
                payment_account_id INTEGER REFERENCES bank_accounts(id),
                payment_reference VARCHAR(100),
                refund_processed_date DATE,
                
                -- GST Compliance
                credit_note_number VARCHAR(50) UNIQUE,
                credit_note_date DATE,
                gst_rate DECIMAL(5,2),
                
                -- Return Details
                return_reason VARCHAR(50),
                -- Values: defective, wrong_item, damaged, changed_mind, exchange, other
                reason_details TEXT,
                
                -- Approval Workflow
                created_by INTEGER,
                approved_by INTEGER,
                approved_at TIMESTAMP,
                rejection_reason TEXT,
                
                -- Additional
                notes TEXT,
                customer_notes TEXT,
                attachments_json TEXT,
                
                -- Audit
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        print("✅ 'returns' table created\n")
        
        # Create indexes for returns table
        print("📝 Creating indexes for 'returns' table...")
        
        db.session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_returns_tenant_id ON returns(tenant_id)
        """))
        db.session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_returns_invoice_id ON returns(invoice_id)
        """))
        db.session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_returns_customer_id ON returns(customer_id)
        """))
        db.session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_returns_return_date ON returns(return_date)
        """))
        db.session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_returns_status ON returns(status)
        """))
        db.session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_returns_return_number ON returns(return_number)
        """))
        print("✅ Indexes created\n")
        
        # ============================================================
        # TABLE 2: return_items (Line items for returns)
        # ============================================================
        print("📝 Creating 'return_items' table...")
        
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS return_items (
                id SERIAL PRIMARY KEY,
                return_id INTEGER NOT NULL REFERENCES returns(id) ON DELETE CASCADE,
                tenant_id INTEGER NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
                
                -- Link to Original Sale
                invoice_item_id INTEGER REFERENCES invoice_items(id) ON DELETE SET NULL,
                
                -- Product Details
                product_id INTEGER REFERENCES items(id) ON DELETE SET NULL,
                product_name VARCHAR(255) NOT NULL,
                product_code VARCHAR(100),
                hsn_code VARCHAR(20),
                
                -- Quantities
                quantity_sold INTEGER NOT NULL,
                quantity_returned INTEGER NOT NULL,
                unit VARCHAR(20),
                
                -- Pricing
                unit_price DECIMAL(10,2) NOT NULL,
                
                -- GST Breakdown
                taxable_amount DECIMAL(10,2) NOT NULL,
                gst_rate DECIMAL(5,2) NOT NULL,
                cgst_amount DECIMAL(10,2),
                sgst_amount DECIMAL(10,2),
                igst_amount DECIMAL(10,2),
                cess_amount DECIMAL(10,2),
                
                -- Totals
                total_amount DECIMAL(10,2) NOT NULL,
                
                -- Item-specific Details
                item_condition VARCHAR(50),
                -- Values: resellable, damaged, defective, opened_package
                return_to_inventory BOOLEAN DEFAULT true,
                
                item_reason VARCHAR(255),
                
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        print("✅ 'return_items' table created\n")
        
        # Create indexes for return_items table
        print("📝 Creating indexes for 'return_items' table...")
        
        db.session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_return_items_return_id ON return_items(return_id)
        """))
        db.session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_return_items_tenant_id ON return_items(tenant_id)
        """))
        db.session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_return_items_product_id ON return_items(product_id)
        """))
        print("✅ Indexes created\n")
        
        db.session.commit()
        
        print("="*80)
        print("🎉 SUCCESS! Returns tables created!")
        print("="*80)
        print("\n✅ Tables created:")
        print("   1. returns - Main return records")
        print("   2. return_items - Return line items")
        print("\n✅ Features enabled:")
        print("   - Return processing workflow")
        print("   - Inventory restocking")
        print("   - Cash/Bank refunds")
        print("   - GST credit notes")
        print("   - Approval workflow")
        print("\n")
        
        return jsonify({
            'status': 'success',
            'message': 'Returns tables created successfully',
            'tables_created': ['returns', 'return_items'],
            'indexes_created': 9
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"\n❌ ERROR: {str(e)}\n")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

