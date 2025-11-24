"""
PDF Generation Utilities
Generate professional PDFs from HTML templates
"""
from io import BytesIO
from flask import render_template, current_app
from xhtml2pdf import pisa

def generate_invoice_pdf(invoice, tenant):
    """
    Generate professional invoice PDF from HTML template
    Returns: BytesIO object containing PDF
    """
    try:
        # Render the professional HTML template
        html_content = render_template('pdf/invoice_clean.html',
                                      invoice=invoice,
                                      tenant=tenant)
        
        # Create PDF from HTML
        pdf_bytes = BytesIO()
        pisa_status = pisa.CreatePDF(
            html_content.encode('utf-8'),
            dest=pdf_bytes,
            encoding='utf-8'
        )
        
        if pisa_status.err:
            raise Exception(f"PDF generation error: {pisa_status.err}")
        
        # Reset pointer to beginning
        pdf_bytes.seek(0)
        return pdf_bytes
        
    except Exception as e:
        current_app.logger.error(f"PDF generation failed: {str(e)}")
        # Fallback to ReportLab if xhtml2pdf fails
        return generate_invoice_pdf_reportlab(invoice, tenant)


def generate_invoice_pdf_reportlab(invoice, tenant):
    """
    Fallback PDF generation using ReportLab (pure Python)
    Returns: BytesIO object containing PDF
    """
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import mm
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
    
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
    
    # Header - 3 column layout: Company | TAX INVOICE | Invoice Details
    header_data = [
        [
            Paragraph(f"<b>{tenant.company_name}</b>", heading_style),
            Paragraph("TAX INVOICE", title_style),
            ''
        ],
        [
            Paragraph(f"Phone: {tenant.admin_phone or 'N/A'}<br/>Email: {tenant.admin_email or 'N/A'}", normal_style),
            '',
            Paragraph(f"<b>{invoice.invoice_number}</b><br/>Date: {invoice.invoice_date.strftime('%d-%m-%Y')}<br/>Status: {invoice.payment_status.upper()}", normal_style)
        ]
    ]
    header_table = Table(header_data, colWidths=[60*mm, 60*mm, 60*mm])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),    # Company info - left aligned
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),   # TAX INVOICE - centered
        ('ALIGN', (2, 0), (2, -1), 'RIGHT'),   # Invoice details - right aligned
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
    
    items_table = Table(items_data, colWidths=[10*mm, 60*mm, 20*mm, 20*mm, 25*mm, 15*mm, 30*mm])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f8f9fa')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (3, 1), (3, -1), 'RIGHT'),  # Qty
        ('ALIGN', (4, 1), (4, -1), 'RIGHT'),  # Rate
        ('ALIGN', (5, 1), (5, -1), 'RIGHT'),  # GST%
        ('ALIGN', (6, 0), (6, -1), 'RIGHT'),  # Amount
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#dee2e6')),
        ('LINEBELOW', (0, 1), (-1, -1), 1, colors.HexColor('#e9ecef')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 10*mm))
    
    # Totals section - Right aligned
    right_align_style = ParagraphStyle('RightAlign', parent=normal_style, alignment=TA_RIGHT)
    bold_right_style = ParagraphStyle('BoldRight', parent=normal_style, 
                                     alignment=TA_RIGHT, fontName='Helvetica-Bold', fontSize=12)
    
    totals_data = [
        [Paragraph('Subtotal', right_align_style), Paragraph(f"Rs {invoice.subtotal:,.2f}", right_align_style)],
        [Paragraph('<b>TOTAL:</b>', bold_right_style), Paragraph(f'<b>Rs {invoice.total_amount:,.2f}</b>', bold_right_style)],
    ]
    totals_table = Table(totals_data, colWidths=[100*mm, 80*mm])
    totals_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LINEABOVE', (1, 1), (1, 1), 2, colors.HexColor('#4CAF50')),
        ('TOPPADDING', (0, 1), (-1, 1), 8),
    ]))
    totals_table.hAlign = 'RIGHT'
    elements.append(totals_table)
    elements.append(Spacer(1, 10*mm))
    
    # Amount in words
    if hasattr(invoice, 'amount_in_words'):
        words_para = Paragraph(f"<b>Amount in Words:</b> {invoice.amount_in_words()}", normal_style)
        elements.append(words_para)
        elements.append(Spacer(1, 10*mm))
    
    # Terms & Conditions
    terms_para = Paragraph("<b>Terms & Conditions:</b><br/>Generated from customer order", normal_style)
    elements.append(terms_para)
    elements.append(Spacer(1, 20*mm))
    
    # Footer - Signatures
    footer_data = [
        [Paragraph('Customer Signature', normal_style), Paragraph(f'For: <b>{tenant.company_name}</b>', right_align_style)],
        [Paragraph('_' * 30, normal_style), Paragraph('_' * 30 + '<br/>Authorized Signatory', right_align_style)]
    ]
    footer_table = Table(footer_data, colWidths=[90*mm, 90*mm])
    footer_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 1), (-1, 1), 30),
    ]))
    elements.append(footer_table)
    
    # Build PDF
    doc.build(elements)
    
    # Reset pointer to beginning
    pdf_bytes.seek(0)
    return pdf_bytes
