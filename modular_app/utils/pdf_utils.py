"""
PDF Generation Utilities
Generate PDFs using ReportLab (pure Python, serverless-ready!)
"""
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER

def generate_invoice_pdf(invoice, tenant):
    """
    Generate professional invoice PDF using ReportLab
    Returns: BytesIO object containing PDF
    """
    pdf_bytes = BytesIO()
    
    # Create PDF document
    doc = SimpleDocTemplate(pdf_bytes, pagesize=A4,
                           topMargin=15*mm, bottomMargin=15*mm,
                           leftMargin=15*mm, rightMargin=15*mm)
    
    # Container for PDF elements
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'],
                                 fontSize=24, textColor=colors.HexColor('#4CAF50'),
                                 alignment=TA_CENTER)
    heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'],
                                   fontSize=14, textColor=colors.black)
    normal_style = styles['Normal']
    
    # Header
    header_data = [
        [Paragraph(f"<b>{tenant.company_name}</b>", heading_style),
         Paragraph("TAX INVOICE", title_style)],
        [Paragraph(f"Phone: {tenant.admin_phone or 'N/A'}<br/>Email: {tenant.admin_email or 'N/A'}", normal_style),
         Paragraph(f"<b>{invoice.invoice_number}</b><br/>Date: {invoice.invoice_date.strftime('%d-%m-%Y')}<br/>Status: {invoice.payment_status.upper()}", normal_style)]
    ]
    header_table = Table(header_data, colWidths=[90*mm, 90*mm])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),  # Center-align TAX INVOICE
        ('ALIGN', (1, 1), (1, 1), 'RIGHT'),   # Right-align invoice details
        ('LINEBELOW', (0, 1), (-1, 1), 2, colors.HexColor('#4CAF50')),
        ('BOTTOMPADDING', (0, 1), (-1, 1), 10),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 10*mm))
    
    # Bill To
    bill_to_data = [
        [Paragraph("<b>BILL TO</b>", heading_style), Paragraph("<b>INVOICE DETAILS</b>", heading_style)],
        [Paragraph(f"<b>{invoice.customer_name}</b><br/>Phone: {invoice.customer_phone or 'N/A'}<br/>Email: {invoice.customer_email or 'N/A'}<br/>{invoice.customer_address or ''}", normal_style),
         Paragraph(f"Payment: {invoice.payment_status.upper()}<br/>Status: {invoice.status.upper()}", normal_style)]
    ]
    bill_to_table = Table(bill_to_data, colWidths=[90*mm, 90*mm])
    bill_to_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    elements.append(bill_to_table)
    elements.append(Spacer(1, 10*mm))
    
    # Items table
    items_data = [['#', 'Item', 'HSN', 'Qty', 'Rate', 'GST%', 'Amount']]
    for idx, item in enumerate(invoice.items, 1):
        items_data.append([
            str(idx),
            item.item_name,
            item.hsn_code or '-',
            f"{item.quantity} {item.unit}",
            f"Rs {item.rate:,.2f}",
            f"{item.gst_rate}%",
            f"Rs {item.total_amount:,.2f}"
        ])
    
    items_table = Table(items_data, colWidths=[10*mm, 50*mm, 20*mm, 20*mm, 25*mm, 15*mm, 30*mm])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f8f9fa')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (3, 1), (3, -1), 'CENTER'),
        ('ALIGN', (4, 1), (-1, -1), 'RIGHT'),
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 10*mm))
    
    # Totals
    totals_data = [
        ['Subtotal:', f"Rs {invoice.subtotal:,.2f}"],
    ]
    if invoice.cgst_amount > 0:
        totals_data.append(['CGST:', f"Rs {invoice.cgst_amount:,.2f}"])
        totals_data.append(['SGST:', f"Rs {invoice.sgst_amount:,.2f}"])
    if invoice.igst_amount > 0:
        totals_data.append(['IGST:', f"Rs {invoice.igst_amount:,.2f}"])
    # Use Paragraph for bold text (not HTML tags in plain text)
    totals_data.append([
        Paragraph('<b>TOTAL:</b>', normal_style),
        Paragraph(f'<b>Rs {invoice.total_amount:,.2f}</b>', normal_style)
    ])
    
    totals_table = Table(totals_data, colWidths=[40*mm, 40*mm], hAlign='RIGHT')
    totals_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('LINEABOVE', (0, -1), (-1, -1), 2, colors.HexColor('#4CAF50')),
        ('FONTSIZE', (0, -1), (-1, -1), 14),
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.HexColor('#4CAF50')),
    ]))
    elements.append(totals_table)
    elements.append(Spacer(1, 15*mm))
    
    # Footer
    footer_text = invoice.notes or "Payment is due within 30 days of invoice date."
    elements.append(Paragraph(f"<b>Terms & Conditions:</b><br/>{footer_text}", normal_style))
    elements.append(Spacer(1, 10*mm))
    elements.append(Paragraph(f"<b>For {tenant.company_name}</b><br/>Authorized Signatory", 
                             ParagraphStyle('Signature', parent=normal_style, alignment=TA_RIGHT)))
    
    # Build PDF
    doc.build(elements)
    pdf_bytes.seek(0)
    
    return pdf_bytes

