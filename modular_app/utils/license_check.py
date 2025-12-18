"""
License/Trial checking middleware
"""
from functools import wraps
from flask import session, redirect, url_for, render_template_string
from utils.tenant_middleware import get_current_tenant

def check_license(f):
    """Decorator to check if tenant's license/trial is active"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        tenant = get_current_tenant()
        
        if not tenant:
            return f(*args, **kwargs)  # No tenant, proceed (for base routes)
        
        # Check if tenant is active
        if not tenant.is_active:
            # Trial or subscription expired
            trial_end_date = tenant.trial_ends_at.strftime('%d %B %Y') if tenant.trial_ends_at else 'Unknown'
            
            return render_template_string("""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Trial Period Expired</title>
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    * { box-sizing: border-box; margin: 0; padding: 0; }
                    body {
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        min-height: 100vh;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        padding: 20px;
                    }
                    .container {
                        background: white;
                        padding: 50px 40px;
                        border-radius: 20px;
                        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                        max-width: 600px;
                        width: 100%;
                        text-align: center;
                    }
                    .icon { font-size: 80px; margin-bottom: 20px; }
                    h1 { color: #e74c3c; margin-bottom: 20px; font-size: 28px; }
                    .company-name {
                        color: #667eea;
                        font-weight: bold;
                        font-size: 22px;
                        margin-bottom: 15px;
                    }
                    .message {
                        color: #555;
                        line-height: 1.8;
                        margin: 15px 0;
                        font-size: 16px;
                    }
                    .highlight {
                        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
                        padding: 20px;
                        border-radius: 10px;
                        margin: 25px 0;
                        border-left: 4px solid #667eea;
                    }
                    .highlight strong {
                        color: #e74c3c;
                        font-size: 18px;
                    }
                    .free-extension {
                        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
                        color: white;
                        padding: 15px;
                        border-radius: 10px;
                        margin: 20px 0;
                        font-weight: bold;
                        font-size: 18px;
                    }
                    .contact-section {
                        background: #f8f9fa;
                        padding: 25px;
                        border-radius: 10px;
                        margin: 25px 0;
                    }
                    .contact-title {
                        color: #333;
                        font-weight: bold;
                        font-size: 18px;
                        margin-bottom: 15px;
                    }
                    .phone-number {
                        font-size: 24px;
                        color: #27ae60;
                        font-weight: bold;
                        margin: 10px 0;
                        letter-spacing: 1px;
                    }
                    .phone-number a {
                        color: #27ae60;
                        text-decoration: none;
                    }
                    .contact-item {
                        margin: 12px 0;
                        font-size: 16px;
                    }
                    .contact-item a {
                        color: #667eea;
                        text-decoration: none;
                        font-weight: bold;
                    }
                    .btn-group {
                        display: flex;
                        gap: 15px;
                        justify-content: center;
                        margin-top: 30px;
                        flex-wrap: wrap;
                    }
                    .btn {
                        display: inline-flex;
                        align-items: center;
                        gap: 8px;
                        padding: 15px 30px;
                        text-decoration: none;
                        border-radius: 10px;
                        font-size: 16px;
                        font-weight: 600;
                        transition: all 0.3s;
                    }
                    .btn-primary {
                        background: linear-gradient(135deg, #27ae60, #229954);
                        color: white;
                    }
                    .btn-primary:hover {
                        transform: translateY(-2px);
                        box-shadow: 0 5px 20px rgba(39, 174, 96, 0.4);
                    }
                    .btn-secondary {
                        background: linear-gradient(135deg, #3498db, #2980b9);
                        color: white;
                    }
                    .btn-secondary:hover {
                        transform: translateY(-2px);
                        box-shadow: 0 5px 20px rgba(52, 152, 219, 0.4);
                    }
                    @media (max-width: 600px) {
                        .container { padding: 30px 20px; }
                        h1 { font-size: 24px; }
                        .phone-number { font-size: 20px; }
                        .btn-group { flex-direction: column; }
                        .btn { width: 100%; justify-content: center; }
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="icon">⏰</div>
                    <h1>Trial Period Expired</h1>
                    <div class="company-name">{{ tenant.company_name }}</div>
                    
                    <div class="highlight">
                        <p class="message">Your trial period ended on:</p>
                        <strong>{{ trial_end }}</strong>
                    </div>
                    
                    <div class="free-extension">
                        🎉 Good News! Trial Extension Available FREE of Cost
                    </div>
                    
                    <p class="message">
                        We understand you might need more time to explore BizBooks.<br>
                        Contact us to extend your trial period <strong>absolutely free!</strong>
                    </p>
                    
                    <div class="contact-section">
                        <div class="contact-title">📞 Contact BizBooks Support</div>
                        <div class="phone-number">
                            <a href="tel:+918983121201">+91 8983121201</a>
                        </div>
                        <div class="contact-item">
                            <a href="mailto:bizbooks.notifications@gmail.com">bizbooks.notifications@gmail.com</a>
                        </div>
                    </div>
                    
                    <div class="btn-group">
                        <a href="tel:+918983121201" class="btn btn-primary">
                            📱 Call Now
                        </a>
                        <a href="https://wa.me/918983121201?text=Hi,%20I%20need%20to%20extend%20my%20BizBooks%20trial%20for%20{{ tenant.company_name }}" class="btn btn-secondary">
                            💬 WhatsApp
                        </a>
                    </div>
                    
                    <p class="message" style="margin-top: 30px; font-size: 14px; color: #999;">
                        <strong>Business Account:</strong> {{ tenant.subdomain }}.bizbooks.co.in
                    </p>
                </div>
            </body>
            </html>
            """, tenant=tenant, trial_end=trial_end_date)
        
        return f(*args, **kwargs)
    
    return decorated_function

