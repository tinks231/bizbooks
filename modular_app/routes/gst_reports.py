from flask import Blueprint, render_template, request, redirect, url_for, flash, g, jsonify
from models.database import db
from models.invoice import Invoice, InvoiceItem
from models.customer import Customer
from utils.tenant_middleware import require_tenant, get_current_tenant_id
from utils.license_check import check_license
from functools import wraps
from flask import session
from datetime import datetime, timedelta
from sqlalchemy import func, extract
from decimal import Decimal
import calendar

gst_reports_bp = Blueprint('gst_reports', __name__, url_prefix='/admin/gst-reports')

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'tenant_admin_id' not in session:
            flash('Please login first', 'error')
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function


@gst_reports_bp.route('/')
@require_tenant
@check_license
@login_required
def index():
    """GST Reports Dashboard"""
    tenant_id = get_current_tenant_id()
    
    # Default to current month
    today = datetime.now()
    start_date_str = request.args.get('start_date', today.replace(day=1).strftime('%Y-%m-%d'))
    end_date_str = request.args.get('end_date', today.strftime('%Y-%m-%d'))
    
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
    
    return render_template('admin/gst_reports/index.html',
                         tenant=g.tenant,
                         start_date=start_date_str,
                         end_date=end_date_str)


@gst_reports_bp.route('/gstr1')
@require_tenant
@check_license
@login_required
def gstr1():
    """GSTR-1 Report - Outward Supplies (Sales)"""
    try:
        tenant_id = get_current_tenant_id()
        
        # Date range
        today = datetime.now()
        start_date_str = request.args.get('start_date', today.replace(day=1).strftime('%Y-%m-%d'))
        end_date_str = request.args.get('end_date', today.strftime('%Y-%m-%d'))
        
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
    except Exception as e:
        print(f"❌ Error in gstr1 date parsing: {str(e)}")
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('gst_reports.index'))
    
    # Get all invoices in date range
    invoices = Invoice.query.filter_by(tenant_id=tenant_id).filter(
        Invoice.invoice_date >= start_date,
        Invoice.invoice_date <= end_date
    ).order_by(Invoice.invoice_date.desc()).all()
    
    # Group invoices by type
    b2b_invoices = []  # Invoices with GSTIN
    b2c_invoices = []  # Invoices without GSTIN
    
    # Summary by GST rate
    gst_summary = {}
    
    total_taxable = Decimal('0')
    total_cgst = Decimal('0')
    total_sgst = Decimal('0')
    total_igst = Decimal('0')
    total_tax = Decimal('0')
    total_invoice_value = Decimal('0')
    
    try:
        for invoice in invoices:
            # Calculate totals - Convert all to Decimal to avoid type mismatch
            taxable = Decimal(str(invoice.subtotal)) if invoice.subtotal else Decimal('0')
            cgst = Decimal(str(invoice.cgst_amount)) if invoice.cgst_amount else Decimal('0')
            sgst = Decimal(str(invoice.sgst_amount)) if invoice.sgst_amount else Decimal('0')
            igst = Decimal(str(invoice.igst_amount)) if invoice.igst_amount else Decimal('0')
            tax = cgst + sgst + igst
            
            total_taxable += taxable
            total_cgst += cgst
            total_sgst += sgst
            total_igst += igst
            total_tax += tax
            total_invoice_value += Decimal(str(invoice.total_amount)) if invoice.total_amount else Decimal('0')
            
            # Categorize as B2B or B2C
            if invoice.customer_gstin and invoice.customer_gstin.strip():
                b2b_invoices.append(invoice)
            else:
                b2c_invoices.append(invoice)
            
            # Group by GST rates
            try:
                for item in invoice.items:
                    # Convert gst_rate to Decimal for consistency
                    gst_rate = float(item.gst_rate or 0)
                    if gst_rate not in gst_summary:
                        gst_summary[gst_rate] = {
                            'taxable_value': Decimal('0'),
                            'cgst': Decimal('0'),
                            'sgst': Decimal('0'),
                            'igst': Decimal('0'),
                            'total_tax': Decimal('0')
                        }
                    
                    # Convert all values to Decimal to avoid type mismatch
                    taxable_val = Decimal(str(item.taxable_value)) if item.taxable_value else Decimal('0')
                    cgst_val = Decimal(str(item.cgst_amount)) if item.cgst_amount else Decimal('0')
                    sgst_val = Decimal(str(item.sgst_amount)) if item.sgst_amount else Decimal('0')
                    igst_val = Decimal(str(item.igst_amount)) if item.igst_amount else Decimal('0')
                    
                    gst_summary[gst_rate]['taxable_value'] += taxable_val
                    gst_summary[gst_rate]['cgst'] += cgst_val
                    gst_summary[gst_rate]['sgst'] += sgst_val
                    gst_summary[gst_rate]['igst'] += igst_val
                    gst_summary[gst_rate]['total_tax'] += cgst_val + sgst_val + igst_val
            except Exception as item_error:
                print(f"⚠️  Error processing items for invoice {invoice.invoice_number}: {str(item_error)}")
                continue
    except Exception as e:
        print(f"❌ Error processing invoices: {str(e)}")
        import traceback
        traceback.print_exc()
        flash(f'Error processing invoices: {str(e)}', 'error')
        return redirect(url_for('gst_reports.index'))
    
    # Sort GST summary by rate
    gst_summary = dict(sorted(gst_summary.items()))
    
    return render_template('admin/gst_reports/gstr1.html',
                         tenant=g.tenant,
                         start_date=start_date_str,
                         end_date=end_date_str,
                         b2b_invoices=b2b_invoices,
                         b2c_invoices=b2c_invoices,
                         gst_summary=gst_summary,
                         total_taxable=total_taxable,
                         total_cgst=total_cgst,
                         total_sgst=total_sgst,
                         total_igst=total_igst,
                         total_tax=total_tax,
                         total_invoice_value=total_invoice_value)


@gst_reports_bp.route('/gstr3b')
@require_tenant
@check_license
@login_required
def gstr3b():
    """GSTR-3B Report - Monthly Summary"""
    try:
        tenant_id = get_current_tenant_id()
    except Exception as e:
        print(f"❌ Error in gstr3b: {str(e)}")
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('gst_reports.index'))
    
    # Date range (default to current month)
    today = datetime.now()
    start_date_str = request.args.get('start_date', today.replace(day=1).strftime('%Y-%m-%d'))
    
    # Get last day of month
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    last_day = calendar.monthrange(start_date.year, start_date.month)[1]
    end_date = start_date.replace(day=last_day)
    end_date_str = end_date.strftime('%Y-%m-%d')
    
    # Get all invoices in date range
    invoices = Invoice.query.filter_by(tenant_id=tenant_id).filter(
        Invoice.invoice_date >= start_date,
        Invoice.invoice_date <= end_date
    ).all()
    
    # Calculate outward supplies
    outward_taxable = Decimal('0')
    outward_cgst = Decimal('0')
    outward_sgst = Decimal('0')
    outward_igst = Decimal('0')
    
    try:
        for invoice in invoices:
            # Convert to Decimal to avoid type mismatch
            outward_taxable += Decimal(str(invoice.subtotal)) if invoice.subtotal else Decimal('0')
            outward_cgst += Decimal(str(invoice.cgst_amount)) if invoice.cgst_amount else Decimal('0')
            outward_sgst += Decimal(str(invoice.sgst_amount)) if invoice.sgst_amount else Decimal('0')
            outward_igst += Decimal(str(invoice.igst_amount)) if invoice.igst_amount else Decimal('0')
    except Exception as e:
        print(f"❌ Error calculating outward supplies: {str(e)}")
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('gst_reports.index'))
    
    # Calculate inward supplies (ITC from purchase bills)
    from models.purchase_bill import PurchaseBill
    
    purchase_bills = PurchaseBill.query.filter(
        PurchaseBill.tenant_id == tenant_id,
        PurchaseBill.status == 'approved',
        PurchaseBill.bill_date >= start_date,
        PurchaseBill.bill_date <= end_date,
        db.or_(
            PurchaseBill.cgst_amount > 0,
            PurchaseBill.sgst_amount > 0,
            PurchaseBill.igst_amount > 0
        )
    ).all()
    
    inward_taxable = Decimal('0')
    inward_cgst = Decimal('0')
    inward_sgst = Decimal('0')
    inward_igst = Decimal('0')
    
    try:
        for bill in purchase_bills:
            inward_taxable += Decimal(str(bill.subtotal)) if bill.subtotal else Decimal('0')
            inward_cgst += Decimal(str(bill.cgst_amount)) if bill.cgst_amount else Decimal('0')
            inward_sgst += Decimal(str(bill.sgst_amount)) if bill.sgst_amount else Decimal('0')
            inward_igst += Decimal(str(bill.igst_amount)) if bill.igst_amount else Decimal('0')
    except Exception as e:
        print(f"❌ Error calculating inward supplies: {str(e)}")
        # Continue with zero ITC if calculation fails
    
    # Calculate net tax liability
    net_cgst = outward_cgst - inward_cgst
    net_sgst = outward_sgst - inward_sgst
    net_igst = outward_igst - inward_igst
    total_tax_liability = net_cgst + net_sgst + net_igst
    
    return render_template('admin/gst_reports/gstr3b.html',
                         tenant=g.tenant,
                         start_date=start_date_str,
                         end_date=end_date_str,
                         month_name=start_date.strftime('%B %Y'),
                         outward_taxable=outward_taxable,
                         outward_cgst=outward_cgst,
                         outward_sgst=outward_sgst,
                         outward_igst=outward_igst,
                         inward_taxable=inward_taxable,
                         inward_cgst=inward_cgst,
                         inward_sgst=inward_sgst,
                         inward_igst=inward_igst,
                         net_cgst=net_cgst,
                         net_sgst=net_sgst,
                         net_igst=net_igst,
                         total_tax_liability=total_tax_liability,
                         invoice_count=len(invoices))


@gst_reports_bp.route('/summary')
@require_tenant
@check_license
@login_required
def summary():
    """GST Summary - Quick Overview"""
    try:
        tenant_id = get_current_tenant_id()
        
        # Date range
        today = datetime.now()
        start_date_str = request.args.get('start_date', today.replace(day=1).strftime('%Y-%m-%d'))
        end_date_str = request.args.get('end_date', today.strftime('%Y-%m-%d'))
        
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        
        # Get invoices
        invoices = Invoice.query.filter_by(tenant_id=tenant_id).filter(
            Invoice.invoice_date >= start_date,
            Invoice.invoice_date <= end_date
        ).all()
        
        # Calculate totals - Convert all to Decimal to avoid type mismatch
        total_sales = sum([Decimal(str(inv.total_amount)) if inv.total_amount else Decimal('0') for inv in invoices])
        total_taxable = sum([Decimal(str(inv.subtotal)) if inv.subtotal else Decimal('0') for inv in invoices])
        total_cgst = sum([Decimal(str(inv.cgst_amount)) if inv.cgst_amount else Decimal('0') for inv in invoices])
        total_sgst = sum([Decimal(str(inv.sgst_amount)) if inv.sgst_amount else Decimal('0') for inv in invoices])
        total_igst = sum([Decimal(str(inv.igst_amount)) if inv.igst_amount else Decimal('0') for inv in invoices])
        total_gst = total_cgst + total_sgst + total_igst
        
        # Group by month
        monthly_data = {}
        for invoice in invoices:
            month_key = invoice.invoice_date.strftime('%Y-%m')
            if month_key not in monthly_data:
                monthly_data[month_key] = {
                    'sales': Decimal('0'),
                    'taxable': Decimal('0'),
                    'gst': Decimal('0'),
                    'count': 0
                }
            # Convert to Decimal to avoid type mismatch
            monthly_data[month_key]['sales'] += Decimal(str(invoice.total_amount)) if invoice.total_amount else Decimal('0')
            monthly_data[month_key]['taxable'] += Decimal(str(invoice.subtotal)) if invoice.subtotal else Decimal('0')
            cgst_dec = Decimal(str(invoice.cgst_amount)) if invoice.cgst_amount else Decimal('0')
            sgst_dec = Decimal(str(invoice.sgst_amount)) if invoice.sgst_amount else Decimal('0')
            igst_dec = Decimal(str(invoice.igst_amount)) if invoice.igst_amount else Decimal('0')
            monthly_data[month_key]['gst'] += cgst_dec + sgst_dec + igst_dec
            monthly_data[month_key]['count'] += 1
    except Exception as e:
        print(f"❌ Error in summary report: {str(e)}")
        import traceback
        traceback.print_exc()
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('gst_reports.index'))
    
    return render_template('admin/gst_reports/summary.html',
                         tenant=g.tenant,
                         start_date=start_date_str,
                         end_date=end_date_str,
                         total_sales=total_sales,
                         total_taxable=total_taxable,
                         total_cgst=total_cgst,
                         total_sgst=total_sgst,
                         total_igst=total_igst,
                         total_gst=total_gst,
                         invoice_count=len(invoices),
                         monthly_data=monthly_data)

