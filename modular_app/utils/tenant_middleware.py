"""
Multi-tenant middleware for subdomain-based tenant detection
"""
from flask import request, g, abort, render_template_string, make_response
from models import Tenant

def get_subdomain_from_host(host):
    """Extract subdomain from host header"""
    # Examples:
    # vijayservice.bizbooks.co.in -> vijayservice
    # client1.bizbooks-dun.vercel.app -> client1
    # bizbooks-dun.vercel.app -> None (Vercel base URL)
    # localhost:5001 -> None (local development)
    
    # Remove port if present
    host = host.split(':')[0]
    
    # Split by dots
    parts = host.split('.')
    
    # Local development (localhost, IPs)
    if host == 'localhost' or host.startswith('127.0.0.1') or host.startswith('192.168'):
        return None
    
    # Vercel URLs: *.vercel.app
    if len(parts) >= 3 and parts[-2] == 'vercel' and parts[-1] == 'app':
        # bizbooks-dun.vercel.app -> No subdomain (base)
        # client1.bizbooks-dun.vercel.app -> subdomain = "client1"
        if len(parts) == 3:
            return None  # Base Vercel URL (e.g., bizbooks-dun.vercel.app)
        else:
            return parts[0]  # Has subdomain (e.g., client1.bizbooks-dun.vercel.app)
    
    # Regular domains
    # Handle second-level TLDs like .co.in, .co.uk, .com.au
    if len(parts) >= 3 and parts[-2] in ['co', 'com', 'net', 'org', 'gov', 'edu', 'ac']:
        # For .co.in: bizbooks.co.in (3 parts) → No subdomain
        #            client1.bizbooks.co.in (4 parts) → subdomain = client1
        if len(parts) == 3:
            return None  # Base domain (e.g., bizbooks.co.in)
        else:
            return parts[0]  # Has subdomain (e.g., client1.bizbooks.co.in)
    
    # Regular TLDs like .com, .org
    # Main domain (no subdomain) - 2 parts
    if len(parts) <= 2:
        return None
    
    # Has subdomain (3+ parts)
    # vijayservice.example.com → vijayservice
    return parts[0]


def load_tenant():
    """Middleware to load tenant based on subdomain"""
    host = request.host
    subdomain = get_subdomain_from_host(host)
    
    # If no subdomain (main site or localhost), set tenant to None
    if not subdomain:
        g.tenant = None
        g.subdomain = None
        return
    
    # Look up tenant by subdomain
    tenant = Tenant.query.filter_by(subdomain=subdomain).first()
    
    # Tenant not found
    if not tenant:
        response = make_response(render_template_string('''
            <!DOCTYPE html>
            <html>
            <head>
                <title>Tenant Not Found</title>
                <style>
                    body {
                        font-family: Arial, sans-serif;
                        text-align: center;
                        padding: 50px;
                        background: #f5f5f5;
                    }
                    .container {
                        background: white;
                        padding: 40px;
                        border-radius: 10px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                        max-width: 600px;
                        margin: 0 auto;
                    }
                    h1 { color: #e74c3c; }
                    a {
                        display: inline-block;
                        margin-top: 20px;
                        padding: 10px 20px;
                        background: #3498db;
                        color: white;
                        text-decoration: none;
                        border-radius: 5px;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>❌ Business Not Found</h1>
                    <p>The business account "{{ subdomain }}" doesn't exist.</p>
                    <p>Please check the URL or contact support.</p>
                    <a href="https://bizbooks.co.in">← Go to BizBooks Home</a>
                </div>
            </body>
            </html>
        ''', subdomain=subdomain))
        response.status_code = 404
        return response
    
    # Check if tenant is active
    if not tenant.is_active:
        status_msg = "suspended" if tenant.status == 'suspended' else "expired"
        trial_end_date = tenant.trial_ends_at.strftime('%d %B %Y') if tenant.trial_ends_at else 'Unknown'
        
        response = make_response(render_template_string('''
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
                    .icon {
                        font-size: 80px;
                        margin-bottom: 20px;
                    }
                    h1 { 
                        color: #e74c3c; 
                        margin-bottom: 20px;
                        font-size: 28px;
                    }
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
                    .contact-item {
                        margin: 12px 0;
                        font-size: 16px;
                    }
                    .contact-item a {
                        color: #667eea;
                        text-decoration: none;
                        font-weight: bold;
                        transition: all 0.3s;
                    }
                    .contact-item a:hover {
                        color: #5568d3;
                        text-decoration: underline;
                    }
                    .phone-number {
                        font-size: 24px;
                        color: #27ae60;
                        font-weight: bold;
                        margin: 10px 0;
                        letter-spacing: 1px;
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
                        .container {
                            padding: 30px 20px;
                        }
                        h1 {
                            font-size: 24px;
                        }
                        .phone-number {
                            font-size: 20px;
                        }
                        .btn-group {
                            flex-direction: column;
                        }
                        .btn {
                            width: 100%;
                            justify-content: center;
                        }
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="icon">⏰</div>
                    <h1>Trial Period Expired</h1>
                    <div class="company-name">{{ company }}</div>
                    
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
                        <div class="contact-item phone-number">
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
                        <a href="https://wa.me/918983121201?text=Hi,%20I%20need%20to%20extend%20my%20BizBooks%20trial%20for%20{{ company }}" class="btn btn-secondary">
                            💬 WhatsApp
                        </a>
                    </div>
                    
                    <p class="message" style="margin-top: 30px; font-size: 14px; color: #999;">
                        <strong>Business Account:</strong> {{ subdomain }}.bizbooks.co.in
                    </p>
                </div>
            </body>
            </html>
        ''', status=status_msg, company=tenant.company_name, trial_end=trial_end_date, subdomain=tenant.subdomain))
        response.status_code = 403
        return response
    
    # Store tenant in g (Flask request context)
    g.tenant = tenant
    g.subdomain = subdomain
    g.tenant_id = tenant.id
    
    # Add pending purchase requests count for notification badge
    try:
        from models import PurchaseRequest
        g.pending_purchase_count = PurchaseRequest.query.filter_by(
            tenant_id=tenant.id,
            status='pending'
        ).count()
    except:
        g.pending_purchase_count = 0


def require_tenant(f):
    """Decorator to ensure route has a valid tenant"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not hasattr(g, 'tenant') or g.tenant is None:
            response = make_response(render_template_string('''
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Subdomain Required</title>
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
                        .message {
                            color: #555;
                            line-height: 1.8;
                            margin: 15px 0;
                            font-size: 16px;
                        }
                        .example-box {
                            background: #f8f9fa;
                            padding: 20px;
                            border-radius: 10px;
                            margin: 25px 0;
                            border-left: 4px solid #667eea;
                        }
                        .example-box code {
                            background: white;
                            padding: 10px 15px;
                            border-radius: 5px;
                            display: block;
                            margin: 10px 0;
                            color: #667eea;
                            font-weight: bold;
                            font-size: 16px;
                        }
                        .btn {
                            display: inline-block;
                            margin-top: 20px;
                            padding: 15px 30px;
                            background: linear-gradient(135deg, #667eea, #764ba2);
                            color: white;
                            text-decoration: none;
                            border-radius: 10px;
                            font-weight: 600;
                            transition: all 0.3s;
                        }
                        .btn:hover {
                            transform: translateY(-2px);
                            box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
                        }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="icon">🏢</div>
                        <h1>Business Subdomain Required</h1>
                        <p class="message">
                            This page requires a business account subdomain to access.
                        </p>
                        <div class="example-box">
                            <p><strong>Correct URL format:</strong></p>
                            <code>yourcompany.bizbooks.co.in</code>
                        </div>
                        <p class="message">
                            If you don't have a BizBooks account yet, you can register for free!
                        </p>
                        <a href="https://bizbooks.co.in/register" class="btn">
                            🚀 Register Your Business
                        </a>
                    </div>
                </body>
                </html>
            '''))
            response.status_code = 400
            return response
        return f(*args, **kwargs)
    return decorated_function


def get_current_tenant():
    """Helper to get current tenant or None"""
    return getattr(g, 'tenant', None)


def get_current_tenant_id():
    """Helper to get current tenant ID or None"""
    return getattr(g, 'tenant_id', None)

