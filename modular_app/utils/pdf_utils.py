"""
PDF Generation Utilities
Generate PDFs from HTML templates using xhtml2pdf (works on serverless!)
"""
from io import BytesIO
from flask import render_template
from xhtml2pdf import pisa

def generate_invoice_pdf(invoice, tenant):
    """
    Generate PDF from invoice data
    Returns: BytesIO object containing PDF
    """
    # Render invoice HTML template (without base layout)
    html_content = render_template('pdf/invoice_pdf.html', 
                                   invoice=invoice, 
                                   tenant=tenant)
    
    # Create PDF from HTML using xhtml2pdf
    pdf_bytes = BytesIO()
    
    # Convert HTML to PDF
    pisa_status = pisa.CreatePDF(
        html_content,
        dest=pdf_bytes
    )
    
    # Check for errors
    if pisa_status.err:
        raise Exception(f"PDF generation error: {pisa_status.err}")
    
    pdf_bytes.seek(0)
    return pdf_bytes

