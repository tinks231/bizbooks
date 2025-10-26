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
            return render_template_string("""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Trial Expired</title>
                <style>
                    body { font-family: Arial; display: flex; justify-content: center; align-items: center; height: 100vh; background: #f5f5f5; margin: 0; }
                    .card { background: white; padding: 40px; border-radius: 10px; box-shadow: 0 10px 40px rgba(0,0,0,0.2); text-align: center; max-width: 500px; }
                    h1 { color: #e74c3c; margin-bottom: 20px; }
                    p { color: #666; margin: 15px 0; line-height: 1.6; }
                    .highlight { color: #e74c3c; font-weight: bold; }
                    .contact-btn { display: inline-block; margin-top: 20px; padding: 15px 30px; background: #3498db; color: white; text-decoration: none; border-radius: 5px; }
                    .contact-btn:hover { background: #2980b9; }
                </style>
            </head>
            <body>
                <div class="card">
                    <h1>⏰ Trial Period Expired</h1>
                    <p>Your <strong>{{ tenant.company_name }}</strong> account trial has ended.</p>
                    <p class="highlight">Trial ended on: {{ tenant.trial_ends_at.strftime('%B %d, %Y') }}</p>
                    <p>To continue using BizBooks, please upgrade to a paid plan.</p>
                    <p style="margin-top: 30px; font-size: 0.9em; color: #999;">
                        Contact: <strong>support@bizbooks.co.in</strong>
                    </p>
                    <a href="mailto:support@bizbooks.co.in?subject=Upgrade Request - {{ tenant.subdomain }}" class="contact-btn">
                        📧 Contact for Upgrade
                    </a>
                </div>
            </body>
            </html>
            """, tenant=tenant)
        
        return f(*args, **kwargs)
    
    return decorated_function

