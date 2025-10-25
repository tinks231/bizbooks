"""
Multi-tenant middleware for subdomain-based tenant detection
"""
from flask import request, g, abort, render_template_string
from models import Tenant

def get_subdomain_from_host(host):
    """Extract subdomain from host header"""
    # Examples:
    # vijayservice.bizbooks.co.in -> vijayservice
    # localhost:5001 -> None (local development)
    # bizbooks.onrender.com -> None (main domain)
    
    # Remove port if present
    host = host.split(':')[0]
    
    # Split by dots
    parts = host.split('.')
    
    # Local development (localhost)
    if host == 'localhost' or host.startswith('127.0.0.1') or host.startswith('192.168'):
        return None
    
    # Main domain (no subdomain)
    # bizbooks.co.in or bizbooks.onrender.com
    if len(parts) <= 2:
        return None
    
    # Has subdomain
    # vijayservice.bizbooks.co.in -> vijayservice
    # client1.bizbooks.onrender.com -> client1
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
        return abort(404, render_template_string('''
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
    
    # Check if tenant is active
    if not tenant.is_active:
        status_msg = "suspended" if tenant.status == 'suspended' else "expired"
        return abort(403, render_template_string('''
            <!DOCTYPE html>
            <html>
            <head>
                <title>Account {{ status }}</title>
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
                    h1 { color: #f39c12; }
                    .renew-btn {
                        display: inline-block;
                        margin-top: 20px;
                        padding: 12px 30px;
                        background: #27ae60;
                        color: white;
                        text-decoration: none;
                        border-radius: 5px;
                        font-size: 16px;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>⚠️ Account {{ status.title() }}</h1>
                    <p>This BizBooks account has been {{ status }}.</p>
                    {% if status == 'expired' %}
                        <p>Your trial or subscription has ended.</p>
                        <a href="mailto:support@bizbooks.co.in?subject=Renew Account: {{ company }}" class="renew-btn">
                            Renew Subscription
                        </a>
                    {% else %}
                        <p>Please contact support for assistance.</p>
                        <a href="mailto:support@bizbooks.co.in?subject=Account Issue: {{ company }}" class="renew-btn">
                            Contact Support
                        </a>
                    {% endif %}
                </div>
            </body>
            </html>
        ''', status=status_msg, company=tenant.company_name))
    
    # Store tenant in g (Flask request context)
    g.tenant = tenant
    g.subdomain = subdomain
    g.tenant_id = tenant.id


def require_tenant(f):
    """Decorator to ensure route has a valid tenant"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not hasattr(g, 'tenant') or g.tenant is None:
            return abort(400, "This page requires a tenant subdomain")
        return f(*args, **kwargs)
    return decorated_function


def get_current_tenant():
    """Helper to get current tenant or None"""
    return getattr(g, 'tenant', None)


def get_current_tenant_id():
    """Helper to get current tenant ID or None"""
    return getattr(g, 'tenant_id', None)

