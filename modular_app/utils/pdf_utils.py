"""
PDF Generation Utilities
Generate PDFs from HTML templates
"""
from io import BytesIO
from flask import render_template
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

def generate_invoice_pdf(invoice, tenant):
    """
    Generate PDF from invoice data
    Returns: BytesIO object containing PDF
    """
    # Render invoice HTML template (without base layout)
    html_content = render_template('pdf/invoice_pdf.html', 
                                   invoice=invoice, 
                                   tenant=tenant)
    
    # Create PDF from HTML
    font_config = FontConfiguration()
    pdf_bytes = BytesIO()
    
    HTML(string=html_content).write_pdf(
        pdf_bytes,
        font_config=font_config
    )
    
    pdf_bytes.seek(0)
    return pdf_bytes

