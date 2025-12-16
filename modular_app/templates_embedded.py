"""
Embedded templates for Vercel deployment
Vercel's Python builder doesn't reliably include template files,
so we embed critical templates as Python strings
"""

PUBLIC_INVOICE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Invoice #{{ invoice.invoice_number }} - {{ tenant.company_name }}</title>
    
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif; background: #f5f5f5; padding: 20px; }
        .action-bar { max-width: 1100px; margin: 0 auto 20px; display: flex; gap: 10px; flex-wrap: wrap; }
        .btn { padding: 10px 20px; border: none; border-radius: 6px; font-size: 14px; font-weight: 500; cursor: pointer; text-decoration: none; display: inline-block; transition: all 0.2s; }
        .btn-primary { background: #3b82f6; color: white; }
        .btn-primary:hover { background: #2563eb; }
        .btn-success { background: #10b981; color: white; }
        .btn-success:hover { background: #059669; }
        .invoice { width: 100%; max-width: 1100px; margin: 0 auto; font-size: 13px; color: #2c3e50; line-height: 1.45; background: #fff; padding: 24px 32px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        h1, h2, h3, h4 { margin: 0; font-weight: 600; }
        .text-right { text-align: right; }
        .invoice-header { display: grid; grid-template-columns: 1fr auto 1fr; align-items: flex-start; column-gap: 16px; padding-bottom: 10px; border-bottom: 2px solid #e5e7eb; }
        .header-center { text-align: center; }
        .company-name-strong { font-size: 16px; font-weight: 700; }
        .company-address { font-size: 13px; color: #4b5563; margin-top: 2px; }
        .header-right { text-align: right; font-size: 13px; color: #4b5563; padding-right: 8px; }
        .invoice-title { text-align: center; font-size: 22px; font-weight: 700; margin: 18px 0; }
        .section { margin: 15px 0; }
        .section-title { font-size: 14px; font-weight: 600; border-bottom: 1px solid #ececec; margin-bottom: 10px; padding-bottom: 4px; }
        .table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        .table th { background: #f8f8f8; padding: 8px; font-size: 12px; font-weight: 600; border: 1px solid #e0e0e0; }
        .table td { padding: 6px; border: 1px solid #e0e0e0; }
        .total-row td { padding: 10px 6px; font-size: 15px; font-weight: 700; background: #eef2ff; border: 2px solid #3b82f6 !important; }
        .footer { margin-top: 25px; text-align: center; font-size: 12px; color: #777; }
        .signature-block { display: flex; justify-content: space-between; margin-top: 25px; }
        .signature-box { width: 45%; text-align: center; }
        .signature-line { margin-top: 50px; border-top: 1px solid #444; padding-top: 6px; }
        @media print { body { background: white; padding: 0; } .action-bar { display: none !important; } .invoice { box-shadow: none; max-width: 100%; } }
    </style>
</head>
<body>

<div class="action-bar">
    <button onclick="window.print()" class="btn btn-primary">🖨️ Print Invoice</button>
    <button onclick="window.print()" class="btn btn-success">📄 Download PDF</button>
</div>

<div class="invoice">
    <div class="invoice-header">
        <div class="header-left">
            {% if tenant_settings and tenant_settings.get('logo_url') %}
            <img src="{{ tenant_settings.get('logo_url') }}" style="max-height: 48px; max-width: 80px; object-fit: contain;" alt="Logo">
            {% endif %}
        </div>
        <div class="header-center">
            <div class="company-name-strong">{{ tenant.company_name }}</div>
            {% if tenant_settings and tenant_settings.get('address') %}
            <div class="company-address">{{ tenant_settings.get('address') }}</div>
            {% endif %}
        </div>
        <div class="header-right">
            <div>📞 {{ tenant_settings.get('phone', tenant.admin_phone) if tenant_settings else tenant.admin_phone }}</div>
            <div>✉️ {{ tenant_settings.get('email', tenant.admin_email) if tenant_settings else tenant.admin_email }}</div>
            {% if tenant_settings and tenant_settings.get('gstin') %}
            <div><strong>GSTIN:</strong> {{ tenant_settings.get('gstin') }}</div>
            {% endif %}
        </div>
    </div>

    <div class="invoice-title">TAX INVOICE</div>

    <div class="section">
        <div style="display:flex;justify-content:space-between;gap:20px;flex-wrap:wrap;">
            <div style="flex:1;min-width:250px;">
                <div class="section-title">Bill To</div>
                <strong>{{ invoice.customer_name }}</strong><br>
                {% if invoice.customer_phone %}📞 {{ invoice.customer_phone }}<br>{% endif %}
                {% if invoice.customer_email %}✉️ {{ invoice.customer_email }}<br>{% endif %}
                {% if invoice.customer_address %}{{ invoice.customer_address }}<br>{% endif %}
                {% if invoice.customer_gstin %}<strong>GSTIN:</strong> {{ invoice.customer_gstin }}<br>{% endif %}
                {% if invoice.customer_state %}<strong>State:</strong> {{ invoice.customer_state }}{% endif %}
            </div>
            <div style="flex:1;min-width:250px;">
                <div class="section-title">Invoice Details</div>
                <table style="width:100%;font-size:13px;">
                    <tr><td style="color:#6b7280;padding:3px 0;">Invoice No:</td><td class="text-right" style="font-weight:500;">{{ invoice.invoice_number }}</td></tr>
                    <tr><td style="color:#6b7280;padding:3px 0;">Date:</td><td class="text-right" style="font-weight:500;">{{ invoice.invoice_date.strftime('%d-%m-%Y') }}</td></tr>
                    {% if invoice.due_date %}
                    <tr><td style="color:#6b7280;padding:3px 0;">Due Date:</td><td class="text-right" style="font-weight:500;">{{ invoice.due_date.strftime('%d-%m-%Y') }}</td></tr>
                    {% endif %}
                    <tr><td style="color:#6b7280;padding:3px 0;">Status:</td><td class="text-right"><span style="padding:3px 8px;border-radius:4px;font-size:11px;font-weight:600;{% if invoice.payment_status == 'paid' %}background:#d1fae5;color:#065f46;{% elif invoice.payment_status == 'partial' %}background:#fef3c7;color:#92400e;{% else %}background:#fee2e2;color:#991b1b;{% endif %}">{{ invoice.payment_status.upper() }}</span></td></tr>
                </table>
            </div>
        </div>
    </div>

    <table class="table">
        <thead>
            <tr><th>#</th><th>Item</th><th>HSN</th><th>Qty</th><th>Rate</th><th>GST %</th><th class="text-right">Amount</th></tr>
        </thead>
        <tbody>
            {% for item in invoice.items %}
            <tr>
                <td>{{ loop.index }}</td>
                <td>{{ item.item_name }}{% if item.description %}<br><small style="color:#666;">{{ item.description }}</small>{% endif %}</td>
                <td>{{ item.hsn_code or '-' }}</td>
                <td>{{ item.quantity }} {{ item.unit }}</td>
                <td>₹{{ "%.2f"|format(item.rate) }}</td>
                <td>{{ item.gst_rate }}%</td>
                <td class="text-right">₹{{ "%.2f"|format(item.taxable_value + item.cgst_amount + item.sgst_amount + item.igst_amount) }}</td>
            </tr>
            {% endfor %}
        </tbody>
        <tfoot>
            <tr><td colspan="6" class="text-right"><strong>Subtotal</strong></td><td class="text-right">₹{{ "%.2f"|format(invoice.subtotal) }}</td></tr>
            {% if invoice.discount_amount and invoice.discount_amount > 0 %}
            <tr><td colspan="6" class="text-right"><strong>Discount</strong></td><td class="text-right" style="color:#e74c3c;">-₹{{ "%.2f"|format(invoice.discount_amount) }}</td></tr>
            {% endif %}
            {% if invoice.loyalty_discount and invoice.loyalty_discount > 0 %}
            <tr><td colspan="6" class="text-right" style="color:#10b981;"><strong>💰 Loyalty Discount</strong></td><td class="text-right" style="color:#10b981;">-₹{{ "%.2f"|format(invoice.loyalty_discount) }}</td></tr>
            {% endif %}
            {% if invoice.cgst_amount > 0 %}
            <tr><td colspan="6" class="text-right">CGST</td><td class="text-right">₹{{ "%.2f"|format(invoice.cgst_amount) }}</td></tr>
            <tr><td colspan="6" class="text-right">SGST</td><td class="text-right">₹{{ "%.2f"|format(invoice.sgst_amount) }}</td></tr>
            {% endif %}
            {% if invoice.igst_amount > 0 %}
            <tr><td colspan="6" class="text-right">IGST</td><td class="text-right">₹{{ "%.2f"|format(invoice.igst_amount) }}</td></tr>
            {% endif %}
            {% if invoice.round_off and invoice.round_off != 0 %}
            <tr><td colspan="6" class="text-right">Round Off</td><td class="text-right">₹{{ "%.2f"|format(invoice.round_off) }}</td></tr>
            {% endif %}
            <tr class="total-row"><td colspan="6" class="text-right"><strong>TOTAL</strong></td><td class="text-right"><strong>₹{{ "%.2f"|format(invoice.total_amount) }}</strong></td></tr>
        </tfoot>
    </table>

    <div style="margin-top: 20px; padding: 10px; background: #f9f9f9; border-left: 3px solid #3b82f6;">
        <strong>Amount in Words:</strong> <em>{{ invoice.amount_in_words() }}</em>
    </div>

    {% if invoice.notes %}
    <div style="margin-top: 20px;">
        <div class="section-title">Terms & Conditions</div>
        <div style="font-size: 12px; color: #666; white-space: pre-line;">{{ invoice.notes }}</div>
    </div>
    {% endif %}

    <div class="signature-block">
        <div class="signature-box">Customer Signature<div class="signature-line"></div></div>
        <div class="signature-box">For: <strong>{{ tenant.company_name }}</strong><div class="signature-line"></div>Authorized Signatory</div>
    </div>

    <div class="footer">
        Thank you for your business!<br><small>This is a computer-generated invoice.</small>
        {% if loyalty_footer_note %}<br><br><small style="color: #10b981; font-size: 11px;">{{ loyalty_footer_note }}</small>{% endif %}
    </div>
</div>

</body>
</html>
"""

