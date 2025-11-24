"""
PDF Generation Utilities
Generate professional PDFs using ReportLab (pure Python, serverless-ready!)
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
    
    # Create PDF document with proper margins
    doc = SimpleDocTemplate(
        pdf_bytes, 
        pagesize=A4,
        topMargin=12*mm, 
        bottomMargin=12*mm,
        leftMargin=15*mm, 
        rightMargin=15*mm
    )
    
    # Container for PDF elements
    elements = []
    
    # Define custom styles
    styles = getSampleStyleSheet()
    
    # Company name style
    company_style = ParagraphStyle(
        'Company',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.black,
        alignment=TA_LEFT,
        spaceAfter=2
    )
    
    # TAX INVOICE style (centered, green, large)
    tax_invoice_style = ParagraphStyle(
        'TaxInvoice',
        parent=styles['Heading1'],
        fontSize=26,
        textColor=colors.HexColor('#4CAF50'),
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    # Section heading style
    section_heading_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontSize=13,
        textColor=colors.black,
        fontName='Helvetica-Bold',
        spaceAfter=6
    )
    
    # Normal text styles
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        leading=14
    )
    
    bold_style = ParagraphStyle(
        'CustomBold',
        parent=styles['Normal'],
        fontSize=11,
        fontName='Helvetica-Bold',
        leading=14
    )
    
    right_align_style = ParagraphStyle(
        'RightAlign',
        parent=styles['Normal'],
        fontSize=11,
        alignment=TA_RIGHT,
        leading=14
    )
    
    # ========== HEADER ROW 1: Company Name (CENTER) | Phone/Email (RIGHT) ==========
    company_center_style = ParagraphStyle(
        'CompanyCenter',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.black,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    # Build right side contact info
    contact_right = [
        Paragraph(f"Phone: {tenant.admin_phone or 'N/A'}", normal_style),
        Paragraph(f"Email: {tenant.admin_email or 'N/A'}", normal_style),
    ]
    # Add GSTIN if available
    if hasattr(tenant, 'gstin') and tenant.gstin:
        contact_right.append(Paragraph(f"GSTIN: {tenant.gstin}", normal_style))
    
    header_row1_data = [[
        '',  # Empty left column
        Paragraph(f"<b>{tenant.company_name}</b>", company_center_style),
        Table([[p] for p in contact_right], colWidths=[60*mm])
    ]]
    
    header_row1_table = Table(header_row1_data, colWidths=[60*mm, 60*mm, 60*mm])
    header_row1_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),
        ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
        ('LINEBELOW', (0, 0), (-1, 0), 2.5, colors.HexColor('#4CAF50')),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
    ]))
    elements.append(header_row1_table)
    elements.append(Spacer(1, 4*mm))
    
    # ========== HEADER ROW 2: TAX INVOICE (CENTERED) ==========
    tax_invoice_centered = Paragraph("TAX INVOICE", tax_invoice_style)
    elements.append(tax_invoice_centered)
    elements.append(Spacer(1, 8*mm))
    
    # ========== BILL TO & INVOICE DETAILS (2 columns) ==========
    bill_to_content = [
        Paragraph("<b>Bill To</b>", section_heading_style),
        Paragraph(f"<b>{invoice.customer_name}</b>", bold_style),
    ]
    
    if hasattr(invoice.customer, 'customer_id') and invoice.customer.customer_id:
        bill_to_content.append(Paragraph(f"Customer ID: {invoice.customer.customer_id}", normal_style))
    
    bill_to_content.append(Paragraph(f"Phone: {invoice.customer_phone or 'N/A'}", normal_style))
    
    if invoice.customer_email:
        bill_to_content.append(Paragraph(f"Email: {invoice.customer_email}", normal_style))
    
    if invoice.customer_address:
        bill_to_content.append(Paragraph(invoice.customer_address, normal_style))
    
    if hasattr(invoice.customer, 'state') and invoice.customer.state:
        bill_to_content.append(Paragraph(f"State: {invoice.customer.state}", normal_style))
    
    invoice_details_content = [
        Paragraph("<b>Invoice Details</b>", section_heading_style),
        Paragraph(f"Invoice No: {invoice.invoice_number}", normal_style),
        Paragraph(f"Date: {invoice.invoice_date.strftime('%d-%m-%Y')}", normal_style),
        Paragraph(f"Status: {invoice.status.upper()}", normal_style),
        Paragraph(f"Payment: {invoice.payment_status.upper()}", normal_style),
    ]
    
    info_data = [[
        Table([[p] for p in bill_to_content], colWidths=[85*mm]),
        Table([[p] for p in invoice_details_content], colWidths=[85*mm])
    ]]
    
    info_table = Table(info_data, colWidths=[85*mm, 85*mm])
    info_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 8*mm))
    
    # ========== ITEMS TABLE ==========
    items_data = [['#', 'ITEM', 'HSN', 'QTY', 'RATE', 'GST%', 'AMOUNT']]
    
    for idx, item in enumerate(invoice.items, 1):
        items_data.append([
            str(idx),
            item.item_name,
            item.hsn_code or '-',
            f"{item.quantity} {item.unit}",
            f"₹{item.rate:,.2f}",
            f"{item.gst_rate}%",
            f"₹{item.total_amount:,.2f}"
        ])
    
    items_table = Table(
        items_data, 
        colWidths=[8*mm, 65*mm, 22*mm, 22*mm, 25*mm, 15*mm, 28*mm]
    )
    
    items_table.setStyle(TableStyle([
        # Header styling
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f8f9fa')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#dee2e6')),
        
        # Body styling
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ('LINEBELOW', (0, 1), (-1, -1), 0.5, colors.HexColor('#e9ecef')),
        
        # Alignment
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),  # # column
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),    # Item column
        ('ALIGN', (2, 0), (2, -1), 'CENTER'),  # HSN column
        ('ALIGN', (3, 0), (-1, -1), 'RIGHT'),  # Qty, Rate, GST%, Amount
        
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    elements.append(items_table)
    elements.append(Spacer(1, 8*mm))
    
    # ========== TOTALS SECTION (Right-aligned) ==========
    totals_label_style = ParagraphStyle(
        'TotalsLabel',
        parent=styles['Normal'],
        fontSize=11,
        alignment=TA_RIGHT,
        leading=16
    )
    
    totals_value_style = ParagraphStyle(
        'TotalsValue',
        parent=styles['Normal'],
        fontSize=11,
        fontName='Helvetica-Bold',
        alignment=TA_RIGHT,
        leading=16
    )
    
    grand_total_label_style = ParagraphStyle(
        'GrandTotalLabel',
        parent=styles['Normal'],
        fontSize=14,
        fontName='Helvetica-Bold',
        alignment=TA_RIGHT,
        leading=20
    )
    
    grand_total_value_style = ParagraphStyle(
        'GrandTotalValue',
        parent=styles['Normal'],
        fontSize=14,
        fontName='Helvetica-Bold',
        alignment=TA_RIGHT,
        leading=20
    )
    
    # Totals must align with AMOUNT column (last column = 28mm, starting at 157mm from left)
    # Items table columns: 8 + 65 + 22 + 22 + 25 + 15 + 28 = 185mm total
    totals_data = [
        [Paragraph('Subtotal', totals_label_style), 
         Paragraph(f"₹{invoice.subtotal:,.2f}", totals_value_style)],
        [Paragraph('TOTAL:', grand_total_label_style), 
         Paragraph(f"₹{invoice.total_amount:,.2f}", grand_total_value_style)],
    ]
    
    # Match items table width: label area (157mm) + amount column width (28mm) = 185mm
    totals_table = Table(totals_data, colWidths=[157*mm, 28*mm])
    totals_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),  # Labels right-aligned
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),  # Values right-aligned
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LINEABOVE', (0, 1), (-1, 1), 2, colors.HexColor('#4CAF50')),
        ('TOPPADDING', (0, 1), (-1, 1), 6),
        ('BOTTOMPADDING', (0, 0), (0, 0), 4),
    ]))
    # No hAlign needed - table spans full width like items table
    elements.append(totals_table)
    elements.append(Spacer(1, 6*mm))
    
    # ========== AMOUNT IN WORDS ==========
    if hasattr(invoice, 'amount_in_words'):
        words_box_style = ParagraphStyle(
            'WordsBox',
            parent=styles['Normal'],
            fontSize=11,
            leading=14,
            textColor=colors.HexColor('#1a1a1a')
        )
        
        words_data = [[Paragraph(f"<b>Amount in Words:</b> {invoice.amount_in_words()}", words_box_style)]]
        words_table = Table(words_data, colWidths=[170*mm])
        words_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f0f7ff')),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('LINEABOVE', (0, 0), (0, 0), 3, colors.HexColor('#2196F3')),
        ]))
        elements.append(words_table)
        elements.append(Spacer(1, 8*mm))
    
    # ========== TERMS & CONDITIONS ==========
    elements.append(Paragraph("<b>Terms & Conditions:</b>", section_heading_style))
    terms_text = invoice.notes if invoice.notes else "Generated from customer order"
    elements.append(Paragraph(terms_text, normal_style))
    elements.append(Spacer(1, 15*mm))
    
    # ========== FOOTER - SIGNATURES ==========
    footer_data = [[
        Paragraph('Customer Signature', normal_style),
        Paragraph(f'For: <b>{tenant.company_name}</b>', right_align_style)
    ]]
    
    footer_table = Table(footer_data, colWidths=[85*mm, 85*mm])
    footer_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LINEABOVE', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')),
        ('TOPPADDING', (0, 0), (-1, -1), 20),
    ]))
    elements.append(footer_table)
    elements.append(Spacer(1, 8*mm))
    
    # Authorized Signatory line
    auth_sig_data = [[
        '',
        Paragraph('Authorized Signatory', right_align_style)
    ]]
    auth_sig_table = Table(auth_sig_data, colWidths=[85*mm, 85*mm])
    auth_sig_table.setStyle(TableStyle([
        ('LINEABOVE', (1, 0), (1, 0), 1, colors.black),
        ('TOPPADDING', (1, 0), (1, 0), 3),
    ]))
    elements.append(auth_sig_table)
    elements.append(Spacer(1, 10*mm))
    
    # Footer note
    footer_note = Paragraph(
        '<para align="center" fontSize="9" textColor="#6c757d">'
        'Thank you for your business!<br/>'
        'This is a computer-generated invoice.'
        '</para>',
        normal_style
    )
    elements.append(footer_note)
    
    # Build PDF
    doc.build(elements)
    
    # Reset pointer to beginning
    pdf_bytes.seek(0)
    return pdf_bytes
