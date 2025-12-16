"""
Public Invoice View - No Login Required
Allows customers to view their invoices via secure token
"""
from flask import Blueprint, render_template, render_template_string, abort, g, request
from models.database import db
from models.invoice import Invoice
from models.tenant import Tenant
from datetime import datetime
from sqlalchemy.orm import joinedload
from templates_embedded import PUBLIC_INVOICE_TEMPLATE
import json

public_invoice_bp = Blueprint('public_invoice', __name__, url_prefix='/invoice')

@public_invoice_bp.route('/view/<token>')
def view_public_invoice(token):
    """
    Public invoice view - no login required
    URL: /invoice/view/<token>
    """
    try:
        # Find invoice by public token (with items loaded)
        invoice = Invoice.query.options(joinedload(Invoice.items)).filter_by(public_token=token).first()
        
        if not invoice:
            abort(404)  # Invalid or expired token
        
        # Load tenant context
        tenant = Tenant.query.get(invoice.tenant_id)
        if not tenant:
            abort(404)
        
        # Set tenant in global context
        g.tenant = tenant
        
        # Get tenant settings
        tenant_settings = {}
        if tenant.settings:
            try:
                tenant_settings = json.loads(tenant.settings) if isinstance(tenant.settings, str) else tenant.settings
            except Exception as e:
                print(f"Error parsing tenant settings: {e}")
                tenant_settings = {}
        
        # Get loyalty footer note if applicable
        loyalty_footer_note = None
        try:
            if invoice.loyalty_points_earned and invoice.loyalty_points_earned > 0:
                loyalty_footer_note = f"🎉 You earned {invoice.loyalty_points_earned} loyalty points on this purchase!"
        except:
            loyalty_footer_note = None
        
        # Get customer relationship for phone
        customer = None
        try:
            if invoice.customer_id:
                from models.customer import Customer
                customer = Customer.query.get(invoice.customer_id)
        except Exception as e:
            print(f"Error loading customer: {e}")
            customer = None
        
        # Use embedded template (Vercel doesn't reliably include template files)
        return render_template_string(PUBLIC_INVOICE_TEMPLATE,
                                     invoice=invoice,
                                     tenant=tenant,
                                     tenant_settings=tenant_settings,
                                     loyalty_footer_note=loyalty_footer_note,
                                     customer=customer,
                                     today=datetime.today())
    
    except Exception as e:
        # Log the error for debugging
        print(f"Error in public invoice view: {str(e)}")
        import traceback
        traceback.print_exc()
        abort(500)

