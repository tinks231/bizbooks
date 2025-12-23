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


@gst_reports_bp.route('/', strict_slashes=False)  # PERFORMANCE: Prevent 308 redirects
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
    # 🆕 GST SMART INVOICE: Only include taxable and credit_adjustment invoices (exclude non_taxable)
    invoices = Invoice.query.filter_by(tenant_id=tenant_id).filter(
        Invoice.invoice_date >= start_date,
        Invoice.invoice_date <= end_date,
        Invoice.invoice_type.in_(['taxable', 'credit_adjustment'])
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
    
    # ========== PROCESS RETURNS (Credit Notes) ==========
    from models.return_model import Return
    from models.return_item import ReturnItem
    
    returns = Return.query.filter_by(tenant_id=tenant_id).filter(
        Return.return_date >= start_date,
        Return.return_date <= end_date,
        Return.status == 'approved'  # Only approved returns
    ).order_by(Return.return_date.desc()).all()
    
    # Initialize return totals
    total_return_taxable = Decimal('0')
    total_return_cgst = Decimal('0')
    total_return_sgst = Decimal('0')
    total_return_igst = Decimal('0')
    total_return_tax = Decimal('0')
    total_return_value = Decimal('0')
    
    return_list = []  # For displaying in template
    
    try:
        for ret in returns:
            # Calculate return totals from items
            ret_taxable = Decimal('0')
            ret_cgst = Decimal('0')
            ret_sgst = Decimal('0')
            ret_igst = Decimal('0')
            
            for item in ret.items:
                ret_taxable += Decimal(str(item.taxable_amount)) if item.taxable_amount else Decimal('0')
                ret_cgst += Decimal(str(item.cgst_amount)) if item.cgst_amount else Decimal('0')
                ret_sgst += Decimal(str(item.sgst_amount)) if item.sgst_amount else Decimal('0')
                ret_igst += Decimal(str(item.igst_amount)) if item.igst_amount else Decimal('0')
                
                # Subtract from GST summary by rate
                try:
                    gst_rate = float(item.gst_rate or 0)
                    if gst_rate in gst_summary:
                        taxable_val = Decimal(str(item.taxable_amount)) if item.taxable_amount else Decimal('0')
                        cgst_val = Decimal(str(item.cgst_amount)) if item.cgst_amount else Decimal('0')
                        sgst_val = Decimal(str(item.sgst_amount)) if item.sgst_amount else Decimal('0')
                        igst_val = Decimal(str(item.igst_amount)) if item.igst_amount else Decimal('0')
                        
                        gst_summary[gst_rate]['taxable_value'] -= taxable_val
                        gst_summary[gst_rate]['cgst'] -= cgst_val
                        gst_summary[gst_rate]['sgst'] -= sgst_val
                        gst_summary[gst_rate]['igst'] -= igst_val
                        gst_summary[gst_rate]['total_tax'] -= (cgst_val + sgst_val + igst_val)
                except Exception as item_error:
                    print(f"⚠️  Error processing return item: {str(item_error)}")
                    continue
            
            ret_tax = ret_cgst + ret_sgst + ret_igst
            ret_total = ret_taxable + ret_tax
            
            # Add to totals
            total_return_taxable += ret_taxable
            total_return_cgst += ret_cgst
            total_return_sgst += ret_sgst
            total_return_igst += ret_igst
            total_return_tax += ret_tax
            total_return_value += ret_total
            
            # Store for display
            return_list.append({
                'return_number': ret.return_number,
                'credit_note_number': ret.credit_note_number,
                'return_date': ret.return_date,
                'customer_name': ret.customer.name if ret.customer else 'Unknown',
                'invoice_number': ret.invoice.invoice_number if ret.invoice else 'N/A',
                'taxable': ret_taxable,
                'cgst': ret_cgst,
                'sgst': ret_sgst,
                'igst': ret_igst,
                'total': ret_total
            })
            
    except Exception as e:
        print(f"⚠️  Error processing returns: {str(e)}")
        import traceback
        traceback.print_exc()
        # Continue even if returns processing fails
    
    # ========== CALCULATE NET AMOUNTS (After Returns) ==========
    net_taxable = total_taxable - total_return_taxable
    net_cgst = total_cgst - total_return_cgst
    net_sgst = total_sgst - total_return_sgst
    net_igst = total_igst - total_return_igst
    net_tax = total_tax - total_return_tax
    net_invoice_value = total_invoice_value - total_return_value
    
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
                         total_invoice_value=total_invoice_value,
                         # Returns data
                         returns=return_list,
                         total_return_taxable=total_return_taxable,
                         total_return_cgst=total_return_cgst,
                         total_return_sgst=total_return_sgst,
                         total_return_igst=total_return_igst,
                         total_return_tax=total_return_tax,
                         total_return_value=total_return_value,
                         # Net amounts (after returns)
                         net_taxable=net_taxable,
                         net_cgst=net_cgst,
                         net_sgst=net_sgst,
                         net_igst=net_igst,
                         net_tax=net_tax,
                         net_invoice_value=net_invoice_value)


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
    # 🆕 GST SMART INVOICE: Only include taxable and credit_adjustment invoices
    invoices = Invoice.query.filter_by(tenant_id=tenant_id).filter(
        Invoice.invoice_date >= start_date,
        Invoice.invoice_date <= end_date,
        Invoice.invoice_type.in_(['taxable', 'credit_adjustment'])
    ).all()
    
    # Calculate outward supplies (GROSS)
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
    
    # ========== SUBTRACT RETURNS (Credit Notes) ==========
    from models.return_model import Return
    
    returns = Return.query.filter_by(tenant_id=tenant_id).filter(
        Return.return_date >= start_date,
        Return.return_date <= end_date,
        Return.status == 'approved'
    ).all()
    
    return_taxable = Decimal('0')
    return_cgst = Decimal('0')
    return_sgst = Decimal('0')
    return_igst = Decimal('0')
    
    try:
        for ret in returns:
            # Calculate return totals from items
            for item in ret.items:
                return_taxable += Decimal(str(item.taxable_amount)) if item.taxable_amount else Decimal('0')
                return_cgst += Decimal(str(item.cgst_amount)) if item.cgst_amount else Decimal('0')
                return_sgst += Decimal(str(item.sgst_amount)) if item.sgst_amount else Decimal('0')
                return_igst += Decimal(str(item.igst_amount)) if item.igst_amount else Decimal('0')
    except Exception as e:
        print(f"⚠️  Error calculating returns: {str(e)}")
        # Continue with zero returns if calculation fails
    
    # Calculate NET outward supplies (after returns)
    net_outward_taxable = outward_taxable - return_taxable
    net_outward_cgst = outward_cgst - return_cgst
    net_outward_sgst = outward_sgst - return_sgst
    net_outward_igst = outward_igst - return_igst
    
    # Calculate inward supplies (ITC from purchase bills)
    # 🆕 GST SMART INVOICE: Only include purchases from GST-registered vendors
    from models.purchase_bill import PurchaseBill
    
    purchase_bills = PurchaseBill.query.filter(
        PurchaseBill.tenant_id == tenant_id,
        PurchaseBill.status == 'approved',
        PurchaseBill.bill_date >= start_date,
        PurchaseBill.bill_date <= end_date,
        PurchaseBill.gst_applicable == True  # Only registered vendor purchases
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
    
    # ========== CALCULATE TAX LIABILITY WITH ITC SET-OFF ==========
    # Step 1: Calculate initial liability (before cross-utilization)
    cgst_before_setoff = net_outward_cgst - inward_cgst
    sgst_before_setoff = net_outward_sgst - inward_sgst
    igst_before_setoff = net_outward_igst - inward_igst
    
    # Step 2: Identify excess credits and liabilities
    cgst_excess = Decimal('0')
    sgst_excess = Decimal('0')
    igst_excess = Decimal('0')
    
    cgst_payable = Decimal('0')
    sgst_payable = Decimal('0')
    igst_payable = Decimal('0')
    
    if cgst_before_setoff < 0:
        cgst_excess = abs(cgst_before_setoff)
    else:
        cgst_payable = cgst_before_setoff
    
    if sgst_before_setoff < 0:
        sgst_excess = abs(sgst_before_setoff)
    else:
        sgst_payable = sgst_before_setoff
    
    if igst_before_setoff < 0:
        igst_excess = abs(igst_before_setoff)
    else:
        igst_payable = igst_before_setoff
    
    # Step 3: Cross-utilization (ITC Set-off)
    # Rule: Excess CGST & SGST can be used to pay IGST
    #       Excess IGST can be used to pay CGST & SGST
    
    cgst_used_for_igst = Decimal('0')
    sgst_used_for_igst = Decimal('0')
    igst_used_for_cgst = Decimal('0')
    igst_used_for_sgst = Decimal('0')
    
    # If IGST is payable, use excess CGST/SGST
    if igst_payable > 0:
        # Use CGST excess first
        if cgst_excess > 0:
            if cgst_excess >= igst_payable:
                cgst_used_for_igst = igst_payable
                igst_payable = Decimal('0')
            else:
                cgst_used_for_igst = cgst_excess
                igst_payable -= cgst_excess
        
        # Then use SGST excess if IGST still payable
        if igst_payable > 0 and sgst_excess > 0:
            if sgst_excess >= igst_payable:
                sgst_used_for_igst = igst_payable
                igst_payable = Decimal('0')
            else:
                sgst_used_for_igst = sgst_excess
                igst_payable -= sgst_excess
    
    # If CGST/SGST is payable, use excess IGST
    if cgst_payable > 0 and igst_excess > 0:
        if igst_excess >= cgst_payable:
            igst_used_for_cgst = cgst_payable
            cgst_payable = Decimal('0')
            igst_excess -= igst_used_for_cgst
        else:
            igst_used_for_cgst = igst_excess
            cgst_payable -= igst_excess
            igst_excess = Decimal('0')
    
    if sgst_payable > 0 and igst_excess > 0:
        if igst_excess >= sgst_payable:
            igst_used_for_sgst = sgst_payable
            sgst_payable = Decimal('0')
        else:
            igst_used_for_sgst = igst_excess
            sgst_payable -= igst_excess
    
    # Step 4: Final tax liability
    total_tax_liability = cgst_payable + sgst_payable + igst_payable
    
    # For backward compatibility
    net_cgst_liability = cgst_before_setoff
    net_sgst_liability = sgst_before_setoff
    net_igst_liability = igst_before_setoff
    
    return render_template('admin/gst_reports/gstr3b.html',
                         tenant=g.tenant,
                         start_date=start_date_str,
                         end_date=end_date_str,
                         month_name=start_date.strftime('%B %Y'),
                         # Gross outward supplies (before returns)
                         outward_taxable=outward_taxable,
                         outward_cgst=outward_cgst,
                         outward_sgst=outward_sgst,
                         outward_igst=outward_igst,
                         # Returns (credit notes)
                         return_taxable=return_taxable,
                         return_cgst=return_cgst,
                         return_sgst=return_sgst,
                         return_igst=return_igst,
                         returns_count=len(returns),
                         # NET outward supplies (after returns)
                         net_outward_taxable=net_outward_taxable,
                         net_outward_cgst=net_outward_cgst,
                         net_outward_sgst=net_outward_sgst,
                         net_outward_igst=net_outward_igst,
                         # Inward supplies (purchases - ITC)
                         inward_taxable=inward_taxable,
                         inward_cgst=inward_cgst,
                         inward_sgst=inward_sgst,
                         inward_igst=inward_igst,
                         # Tax liability (before set-off)
                         cgst_before_setoff=cgst_before_setoff,
                         sgst_before_setoff=sgst_before_setoff,
                         igst_before_setoff=igst_before_setoff,
                         # Excess credits
                         cgst_excess=cgst_excess,
                         sgst_excess=sgst_excess,
                         igst_excess=igst_excess,
                         # Set-off (cross-utilization)
                         cgst_used_for_igst=cgst_used_for_igst,
                         sgst_used_for_igst=sgst_used_for_igst,
                         igst_used_for_cgst=igst_used_for_cgst,
                         igst_used_for_sgst=igst_used_for_sgst,
                         # Final payable (after set-off)
                         cgst_payable=cgst_payable,
                         sgst_payable=sgst_payable,
                         igst_payable=igst_payable,
                         # Backward compatibility
                         net_cgst=net_cgst_liability,
                         net_sgst=net_sgst_liability,
                         net_igst=net_igst_liability,
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
        
        # ========== SUBTRACT RETURNS ==========
        from models.return_model import Return
        
        returns = Return.query.filter_by(tenant_id=tenant_id).filter(
            Return.return_date >= start_date,
            Return.return_date <= end_date,
            Return.status == 'approved'
        ).all()
        
        return_sales = Decimal('0')
        return_taxable = Decimal('0')
        return_cgst = Decimal('0')
        return_sgst = Decimal('0')
        return_igst = Decimal('0')
        
        for ret in returns:
            return_sales += Decimal(str(ret.total_amount)) if ret.total_amount else Decimal('0')
            for item in ret.items:
                return_taxable += Decimal(str(item.taxable_amount)) if item.taxable_amount else Decimal('0')
                return_cgst += Decimal(str(item.cgst_amount)) if item.cgst_amount else Decimal('0')
                return_sgst += Decimal(str(item.sgst_amount)) if item.sgst_amount else Decimal('0')
                return_igst += Decimal(str(item.igst_amount)) if item.igst_amount else Decimal('0')
        
        return_gst = return_cgst + return_sgst + return_igst
        
        # Calculate NET amounts (after returns)
        net_sales = total_sales - return_sales
        net_taxable = total_taxable - return_taxable
        net_cgst = total_cgst - return_cgst
        net_sgst = total_sgst - return_sgst
        net_igst = total_igst - return_igst
        net_gst = total_gst - return_gst
        
        # Group by month (GROSS amounts first)
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
        
        # Subtract returns from monthly data
        for ret in returns:
            month_key = ret.return_date.strftime('%Y-%m')
            if month_key in monthly_data:
                monthly_data[month_key]['sales'] -= Decimal(str(ret.total_amount)) if ret.total_amount else Decimal('0')
                # Calculate return GST from items
                ret_taxable = Decimal('0')
                ret_gst = Decimal('0')
                for item in ret.items:
                    ret_taxable += Decimal(str(item.taxable_amount)) if item.taxable_amount else Decimal('0')
                    ret_gst += Decimal(str(item.cgst_amount)) if item.cgst_amount else Decimal('0')
                    ret_gst += Decimal(str(item.sgst_amount)) if item.sgst_amount else Decimal('0')
                    ret_gst += Decimal(str(item.igst_amount)) if item.igst_amount else Decimal('0')
                monthly_data[month_key]['taxable'] -= ret_taxable
                monthly_data[month_key]['gst'] -= ret_gst
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
                         # Gross amounts (before returns)
                         total_sales=total_sales,
                         total_taxable=total_taxable,
                         total_cgst=total_cgst,
                         total_sgst=total_sgst,
                         total_igst=total_igst,
                         total_gst=total_gst,
                         # Returns
                         return_sales=return_sales,
                         return_taxable=return_taxable,
                         return_gst=return_gst,
                         returns_count=len(returns),
                         # NET amounts (after returns)
                         net_sales=net_sales,
                         net_taxable=net_taxable,
                         net_cgst=net_cgst,
                         net_sgst=net_sgst,
                         net_igst=net_igst,
                         net_gst=net_gst,
                         invoice_count=len(invoices),
                         monthly_data=monthly_data)

