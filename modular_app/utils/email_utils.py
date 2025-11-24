"""
Email notification utilities
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app

def send_email(to_email, subject, body_html, body_text=None):
    """
    Send email using Gmail SMTP
    
    Environment variables needed (set in Vercel):
    - SMTP_EMAIL: Gmail address (e.g., yourcompany@gmail.com)
    - SMTP_PASSWORD: Gmail app password (not regular password!)
    - SMTP_SERVER: smtp.gmail.com (default)
    - SMTP_PORT: 587 (default)
    """
    
    # Get SMTP configuration from environment
    smtp_email = os.getenv('SMTP_EMAIL')
    smtp_password = os.getenv('SMTP_PASSWORD')
    smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', 587))
    
    # If SMTP not configured, skip email (fail silently in development)
    if not smtp_email or not smtp_password:
        current_app.logger.warning(f'SMTP not configured. Would have sent: {subject} to {to_email}')
        return False
    
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['From'] = smtp_email
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Add text and HTML parts
        if body_text:
            msg.attach(MIMEText(body_text, 'plain'))
        msg.attach(MIMEText(body_html, 'html'))
        
        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_email, smtp_password)
            server.send_message(msg)
        
        current_app.logger.info(f'Email sent to {to_email}: {subject}')
        return True
        
    except Exception as e:
        current_app.logger.error(f'Failed to send email to {to_email}: {str(e)}')
        return False


def send_purchase_request_notification(admin_email, employee_name, item_name, estimated_price, tenant_name):
    """Send notification to admin when employee submits purchase request"""
    
    subject = f"🛒 New Purchase Request: {item_name}"
    
    body_html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px;">
            <h2 style="color: #3498db; margin-bottom: 20px;">New Purchase Request</h2>
            
            <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
                <p style="margin: 5px 0;"><strong>Employee:</strong> {employee_name}</p>
                <p style="margin: 5px 0;"><strong>Item:</strong> {item_name}</p>
                <p style="margin: 5px 0;"><strong>Estimated Price:</strong> ₹{estimated_price:,.2f}</p>
            </div>
            
            <p>Please review and approve/reject this request in your admin dashboard.</p>
            
            <a href="https://{tenant_name}.bizbooks.co.in/admin/purchase-requests" 
               style="display: inline-block; padding: 12px 24px; background: #3498db; color: white; text-decoration: none; border-radius: 5px; margin-top: 15px;">
                Review Request
            </a>
            
            <p style="color: #666; font-size: 12px; margin-top: 30px; border-top: 1px solid #ddd; padding-top: 15px;">
                This is an automated notification from {tenant_name}'s BizBooks account.
            </p>
        </div>
    </body>
    </html>
    """
    
    body_text = f"""
New Purchase Request

Employee: {employee_name}
Item: {item_name}
Estimated Price: ₹{estimated_price:,.2f}

Please review this request in your admin dashboard.
    """
    
    return send_email(admin_email, subject, body_html, body_text)


def send_purchase_approved_notification(employee_email, employee_name, item_name, approved_amount, admin_notes=None):
    """Send notification to employee when purchase request is approved"""
    
    subject = f"✅ Purchase Request Approved: {item_name}"
    
    notes_html = f"<p><strong>Admin Notes:</strong> {admin_notes}</p>" if admin_notes else ""
    
    body_html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px;">
            <h2 style="color: #28a745; margin-bottom: 20px;">✅ Purchase Request Approved</h2>
            
            <p>Hello {employee_name},</p>
            
            <div style="background: #d4edda; border-left: 4px solid #28a745; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <p style="margin: 5px 0;"><strong>Item:</strong> {item_name}</p>
                <p style="margin: 5px 0;"><strong>Approved Amount:</strong> ₹{approved_amount:,.2f}</p>
            </div>
            
            {notes_html}
            
            <p>You can proceed with the purchase as approved.</p>
            
            <p style="color: #666; font-size: 12px; margin-top: 30px; border-top: 1px solid #ddd; padding-top: 15px;">
                This is an automated notification from BizBooks.
            </p>
        </div>
    </body>
    </html>
    """
    
    body_text = f"""
Purchase Request Approved

Hello {employee_name},

Your purchase request has been approved:
Item: {item_name}
Approved Amount: ₹{approved_amount:,.2f}

{"Admin Notes: " + admin_notes if admin_notes else ""}

You can proceed with the purchase.
    """
    
    return send_email(employee_email, subject, body_html, body_text)


def send_purchase_rejected_notification(employee_email, employee_name, item_name, rejection_reason):
    """Send notification to employee when purchase request is rejected"""
    
    subject = f"❌ Purchase Request Rejected: {item_name}"
    
    body_html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px;">
            <h2 style="color: #dc3545; margin-bottom: 20px;">❌ Purchase Request Rejected</h2>
            
            <p>Hello {employee_name},</p>
            
            <div style="background: #f8d7da; border-left: 4px solid #dc3545; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <p style="margin: 5px 0;"><strong>Item:</strong> {item_name}</p>
            </div>
            
            <p><strong>Reason for Rejection:</strong></p>
            <p style="background: #f8f9fa; padding: 15px; border-radius: 5px;">{rejection_reason}</p>
            
            <p>Please contact your supervisor for more details.</p>
            
            <p style="color: #666; font-size: 12px; margin-top: 30px; border-top: 1px solid #ddd; padding-top: 15px;">
                This is an automated notification from BizBooks.
            </p>
        </div>
    </body>
    </html>
    """
    
    body_text = f"""
Purchase Request Rejected

Hello {employee_name},

Your purchase request has been rejected:
Item: {item_name}

Reason: {rejection_reason}

Please contact your supervisor for more details.
    """
    
    return send_email(employee_email, subject, body_html, body_text)


def send_verification_email(to_email, admin_name, company_name, verification_url):
    """Send email verification link to new tenant"""
    
    subject = f"🔐 Verify Your BizBooks Account - {company_name}"
    
    body_html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; background: #f4f4f4; padding: 20px;">
        <div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
            <!-- Header -->
            <div style="text-align: center; margin-bottom: 30px;">
                <h1 style="color: #667eea; margin: 0; font-size: 28px;">📚 BizBooks</h1>
                <p style="color: #888; font-size: 14px; margin: 5px 0 0 0;">Business Management Made Simple</p>
            </div>
            
            <!-- Welcome Message -->
            <h2 style="color: #333; margin-bottom: 20px; font-size: 24px;">Welcome, {admin_name}! 🎉</h2>
            
            <p style="font-size: 16px; line-height: 1.8; margin-bottom: 20px;">
                Thank you for signing up for <strong>{company_name}</strong>'s BizBooks account!
            </p>
            
            <p style="font-size: 16px; line-height: 1.8; margin-bottom: 30px;">
                To get started, please verify your email address by clicking the button below:
            </p>
            
            <!-- Verification Button -->
            <div style="text-align: center; margin: 40px 0;">
                <a href="{verification_url}" 
                   style="display: inline-block; padding: 16px 40px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-decoration: none; border-radius: 8px; font-size: 18px; font-weight: bold; box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);">
                    ✅ Verify Email Address
                </a>
            </div>
            
            <!-- Alternative Link -->
            <p style="font-size: 14px; color: #666; margin-top: 30px;">
                If the button doesn't work, copy and paste this link in your browser:
            </p>
            <p style="background: #f8f9fa; padding: 12px; border-radius: 5px; word-break: break-all; font-size: 13px; color: #667eea; border: 1px dashed #667eea;">
                {verification_url}
            </p>
            
            <!-- Important Notice -->
            <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 30px 0; border-radius: 5px;">
                <p style="margin: 0; font-size: 14px; color: #856404;">
                    <strong>⏰ Important:</strong> This verification link will expire in <strong>24 hours</strong>.
                </p>
            </div>
            
            <!-- Features Preview -->
            <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 30px 0;">
                <h3 style="color: #667eea; margin-top: 0;">What's Next?</h3>
                <ul style="padding-left: 20px; margin: 10px 0;">
                    <li style="margin: 8px 0;">📊 <strong>30-Day Free Trial</strong> - Full access to all features</li>
                    <li style="margin: 8px 0;">👥 <strong>Manage up to 50 employees</strong></li>
                    <li style="margin: 8px 0;">📦 <strong>Inventory & Stock Management</strong></li>
                    <li style="margin: 8px 0;">📄 <strong>GST Invoicing</strong></li>
                    <li style="margin: 8px 0;">📋 <strong>Task Management</strong></li>
                    <li style="margin: 8px 0;">📍 <strong>GPS Attendance Tracking</strong></li>
                </ul>
            </div>
            
            <!-- Support -->
            <div style="margin-top: 40px; padding-top: 20px; border-top: 2px solid #eee;">
                <p style="color: #666; font-size: 14px; margin: 5px 0;">
                    <strong>Need Help?</strong>
                </p>
                <p style="color: #666; font-size: 14px; margin: 5px 0;">
                    📧 Email: <a href="mailto:bizbooks.notifications@gmail.com" style="color: #667eea; text-decoration: none;">bizbooks.notifications@gmail.com</a>
                </p>
                <p style="color: #999; font-size: 12px; margin-top: 20px;">
                    This is an automated message from BizBooks. Please do not reply to this email.
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
    body_text = f"""
Welcome to BizBooks!

Hello {admin_name},

Thank you for signing up for {company_name}'s BizBooks account!

To get started, please verify your email address by visiting this link:
{verification_url}

⏰ This link will expire in 24 hours.

What's Next?
- 30-Day Free Trial with full access to all features
- Manage up to 50 employees
- Inventory & Stock Management
- GST Invoicing
- Task Management
- GPS Attendance Tracking

Need help? Email us at bizbooks.notifications@gmail.com

---
This is an automated message from BizBooks.
    """
    
    return send_email(to_email, subject, body_html, body_text)


def send_customer_order_notification(admin_email, customer_name, order_number, total_amount, items_count, tenant_name):
    """Send notification to admin when customer places an order"""
    
    subject = f"🛒 New Customer Order: {order_number}"
    
    body_html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px;">
            <h2 style="color: #FF6B6B; margin-bottom: 20px;">🛒 New Customer Order Received!</h2>
            
            <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
                <p style="margin: 5px 0; font-size: 18px;"><strong>Order #{order_number}</strong></p>
            </div>
            
            <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
                <p style="margin: 5px 0;"><strong>👤 Customer:</strong> {customer_name}</p>
                <p style="margin: 5px 0;"><strong>📦 Items:</strong> {items_count} item(s)</p>
                <p style="margin: 5px 0;"><strong>💰 Total Amount:</strong> <span style="color: #28a745; font-size: 20px; font-weight: bold;">₹{total_amount:,.2f}</span></p>
            </div>
            
            <p style="margin: 20px 0;">A customer has placed a new order through your customer portal. Please review and fulfill it promptly.</p>
            
            <a href="https://{tenant_name}.bizbooks.co.in/admin/customer-orders" 
               style="display: inline-block; padding: 12px 24px; background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%); color: white; text-decoration: none; border-radius: 5px; margin-top: 15px; font-weight: 600;">
                📦 View Order Details
            </a>
            
            <div style="background: #e7f3ff; border-left: 4px solid #2196F3; padding: 15px; border-radius: 5px; margin-top: 20px;">
                <p style="margin: 0;"><strong>💡 Quick Actions:</strong></p>
                <p style="margin: 5px 0 0 0; font-size: 14px;">• Mark as Confirmed<br>• Prepare items for delivery<br>• Mark as Fulfilled when ready</p>
            </div>
            
            <p style="color: #666; font-size: 12px; margin-top: 30px; border-top: 1px solid #ddd; padding-top: 15px;">
                This is an automated notification from {tenant_name}'s BizBooks account.<br>
                Orders are placed by customers through the Customer Portal.
            </p>
        </div>
    </body>
    </html>
    """
    
    body_text = f"""
🛒 New Customer Order Received!

Order Number: {order_number}
Customer: {customer_name}
Items: {items_count} item(s)
Total Amount: ₹{total_amount:,.2f}

A customer has placed a new order. Please review and fulfill it promptly.

View order details: https://{tenant_name}.bizbooks.co.in/admin/customer-orders

---
This is an automated notification from {tenant_name}'s BizBooks account.
    """
    
    return send_email(admin_email, subject, body_html, body_text)


def send_order_confirmed_notification(customer_email, customer_name, order_number, total_amount, items_count, tenant_name):
    """Send notification to customer when order is confirmed"""
    
    subject = f"✅ Order Confirmed: {order_number}"
    
    body_html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px;">
            <h2 style="color: #17a2b8; margin-bottom: 20px;">✅ Order Confirmed!</h2>
            
            <p>Hello {customer_name},</p>
            
            <p>Great news! Your order has been confirmed and is being prepared.</p>
            
            <div style="background: #d1ecf1; border-left: 4px solid #17a2b8; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <p style="margin: 5px 0; font-size: 18px;"><strong>Order #{order_number}</strong></p>
                <p style="margin: 5px 0;"><strong>Items:</strong> {items_count} item(s)</p>
                <p style="margin: 5px 0;"><strong>Total:</strong> <span style="color: #28a745; font-size: 18px; font-weight: bold;">₹{total_amount:,.2f}</span></p>
            </div>
            
            <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <p style="margin: 0;"><strong>📦 What's Next?</strong></p>
                <p style="margin: 5px 0 0 0; font-size: 14px;">We're preparing your items. You'll receive another notification when your order is ready!</p>
            </div>
            
            <a href="https://{tenant_name}.bizbooks.co.in/customer/orders" 
               style="display: inline-block; padding: 12px 24px; background: #17a2b8; color: white; text-decoration: none; border-radius: 5px; margin-top: 15px; font-weight: 600;">
                📦 Track Your Order
            </a>
            
            <p style="color: #666; font-size: 12px; margin-top: 30px; border-top: 1px solid #ddd; padding-top: 15px;">
                This is an automated notification from {tenant_name}.<br>
                Need help? Contact us through your customer portal.
            </p>
        </div>
    </body>
    </html>
    """
    
    body_text = f"""
✅ Order Confirmed!

Hello {customer_name},

Your order has been confirmed and is being prepared.

Order Number: {order_number}
Items: {items_count} item(s)
Total: ₹{total_amount:,.2f}

What's Next?
We're preparing your items. You'll receive another notification when your order is ready!

Track your order: https://{tenant_name}.bizbooks.co.in/customer/orders

---
This is an automated notification from {tenant_name}.
    """
    
    return send_email(customer_email, subject, body_html, body_text)


def send_order_fulfilled_notification(customer_email, customer_name, order_number, total_amount, items_count, tenant_name):
    """Send notification to customer when order is fulfilled/ready"""
    
    subject = f"✓ Order Ready: {order_number}"
    
    body_html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px;">
            <h2 style="color: #28a745; margin-bottom: 20px;">✓ Order Ready!</h2>
            
            <p>Hello {customer_name},</p>
            
            <p>Excellent news! Your order is ready for pickup/has been delivered.</p>
            
            <div style="background: #d4edda; border-left: 4px solid #28a745; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <p style="margin: 5px 0; font-size: 18px;"><strong>Order #{order_number}</strong></p>
                <p style="margin: 5px 0;"><strong>Items:</strong> {items_count} item(s)</p>
                <p style="margin: 5px 0;"><strong>Total:</strong> <span style="color: #28a745; font-size: 18px; font-weight: bold;">₹{total_amount:,.2f}</span></p>
            </div>
            
            <div style="background: #e7f3ff; border-left: 4px solid #2196F3; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <p style="margin: 0;"><strong>🎉 Thank You!</strong></p>
                <p style="margin: 5px 0 0 0; font-size: 14px;">We appreciate your business. Hope to serve you again soon!</p>
            </div>
            
            <a href="https://{tenant_name}.bizbooks.co.in/customer/orders" 
               style="display: inline-block; padding: 12px 24px; background: #28a745; color: white; text-decoration: none; border-radius: 5px; margin-top: 15px; font-weight: 600;">
                📦 View Order Details
            </a>
            
            <p style="color: #666; font-size: 12px; margin-top: 30px; border-top: 1px solid #ddd; padding-top: 15px;">
                This is an automated notification from {tenant_name}.<br>
                Need help? Contact us through your customer portal.
            </p>
        </div>
    </body>
    </html>
    """
    
    body_text = f"""
✓ Order Ready!

Hello {customer_name},

Your order is ready for pickup/has been delivered.

Order Number: {order_number}
Items: {items_count} item(s)
Total: ₹{total_amount:,.2f}

Thank you for your business! Hope to serve you again soon.

View order details: https://{tenant_name}.bizbooks.co.in/customer/orders

---
This is an automated notification from {tenant_name}.
    """
    
    return send_email(customer_email, subject, body_html, body_text)


def send_order_cancelled_notification(customer_email, customer_name, order_number, total_amount, items_count, tenant_name, reason=None):
    """Send notification to customer when order is cancelled"""
    
    subject = f"✕ Order Cancelled: {order_number}"
    
    reason_html = f"""
    <div style="background: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0;">
        <p style="margin: 0;"><strong>Reason:</strong> {reason}</p>
    </div>
    """ if reason else ""
    
    body_html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px;">
            <h2 style="color: #dc3545; margin-bottom: 20px;">✕ Order Cancelled</h2>
            
            <p>Hello {customer_name},</p>
            
            <p>We regret to inform you that your order has been cancelled.</p>
            
            <div style="background: #f8d7da; border-left: 4px solid #dc3545; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <p style="margin: 5px 0; font-size: 18px;"><strong>Order #{order_number}</strong></p>
                <p style="margin: 5px 0;"><strong>Items:</strong> {items_count} item(s)</p>
                <p style="margin: 5px 0;"><strong>Amount:</strong> ₹{total_amount:,.2f}</p>
            </div>
            
            {reason_html}
            
            <p>If you have any questions, please contact us.</p>
            
            <a href="https://{tenant_name}.bizbooks.co.in/customer/products" 
               style="display: inline-block; padding: 12px 24px; background: #6c757d; color: white; text-decoration: none; border-radius: 5px; margin-top: 15px; font-weight: 600;">
                🛍️ Browse Products Again
            </a>
            
            <p style="color: #666; font-size: 12px; margin-top: 30px; border-top: 1px solid #ddd; padding-top: 15px;">
                This is an automated notification from {tenant_name}.<br>
                Need help? Contact us through your customer portal.
            </p>
        </div>
    </body>
    </html>
    """
    
    body_text = f"""
✕ Order Cancelled

Hello {customer_name},

Your order has been cancelled.

Order Number: {order_number}
Items: {items_count} item(s)
Amount: ₹{total_amount:,.2f}

{"Reason: " + reason if reason else ""}

If you have any questions, please contact us.

Browse products: https://{tenant_name}.bizbooks.co.in/customer/products

---
This is an automated notification from {tenant_name}.
    """
    
    return send_email(customer_email, subject, body_html, body_text)


def send_subscription_pause_notification(admin_email, customer_name, customer_phone, subscription_plan, start_date, end_date, paused_days, tenant_name):
    """
    Send email to admin when customer pauses their subscription deliveries
    """
    subject = f"⏸️ Subscription Paused - {customer_name}"
    
    body_html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px;">
            <h2 style="color: #ffc107; margin-bottom: 20px;">⏸️ Subscription Paused</h2>
            
            <p>A customer has paused their subscription deliveries.</p>
            
            <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <p style="margin: 5px 0;"><strong>Customer:</strong> {customer_name}</p>
                <p style="margin: 5px 0;"><strong>Phone:</strong> {customer_phone}</p>
                <p style="margin: 5px 0;"><strong>Plan:</strong> {subscription_plan}</p>
                <p style="margin: 5px 0;"><strong>Paused From:</strong> {start_date} to {end_date}</p>
                <p style="margin: 5px 0; font-size: 18px; color: #ffc107;"><strong>⏸️ {paused_days} days paused</strong></p>
            </div>
            
            <p style="color: #666; font-size: 14px;">Please update your delivery schedule accordingly.</p>
            
            <a href="https://{tenant_name}.bizbooks.co.in/admin/subscriptions/deliveries" 
               style="display: inline-block; padding: 12px 24px; background: #4CAF50; color: white; text-decoration: none; border-radius: 5px; margin-top: 15px; font-weight: 600;">
                📋 View Deliveries
            </a>
            
            <p style="color: #666; font-size: 12px; margin-top: 30px; border-top: 1px solid #ddd; padding-top: 15px;">
                This is an automated notification from BizBooks.
            </p>
        </div>
    </body>
    </html>
    """
    
    body_text = f"""
⏸️ Subscription Paused

A customer has paused their subscription deliveries.

Customer: {customer_name}
Phone: {customer_phone}
Plan: {subscription_plan}
Paused From: {start_date} to {end_date}
Days Paused: {paused_days}

Please update your delivery schedule accordingly.

View deliveries: https://{tenant_name}.bizbooks.co.in/admin/subscriptions/deliveries

---
This is an automated notification from BizBooks.
    """
    
    return send_email(admin_email, subject, body_html, body_text)


def send_subscription_resume_notification(admin_email, customer_name, customer_phone, subscription_plan, start_date, end_date, resumed_days, tenant_name):
    """
    Send email to admin when customer resumes their subscription deliveries
    """
    subject = f"▶️ Subscription Resumed - {customer_name}"
    
    body_html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px;">
            <h2 style="color: #28a745; margin-bottom: 20px;">▶️ Subscription Resumed</h2>
            
            <p>A customer has resumed their subscription deliveries.</p>
            
            <div style="background: #d4edda; border-left: 4px solid #28a745; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <p style="margin: 5px 0;"><strong>Customer:</strong> {customer_name}</p>
                <p style="margin: 5px 0;"><strong>Phone:</strong> {customer_phone}</p>
                <p style="margin: 5px 0;"><strong>Plan:</strong> {subscription_plan}</p>
                <p style="margin: 5px 0;"><strong>Resumed From:</strong> {start_date} to {end_date}</p>
                <p style="margin: 5px 0; font-size: 18px; color: #28a745;"><strong>▶️ {resumed_days} days resumed</strong></p>
            </div>
            
            <p style="color: #666; font-size: 14px;">Please update your delivery schedule accordingly.</p>
            
            <a href="https://{tenant_name}.bizbooks.co.in/admin/subscriptions/deliveries" 
               style="display: inline-block; padding: 12px 24px; background: #4CAF50; color: white; text-decoration: none; border-radius: 5px; margin-top: 15px; font-weight: 600;">
                📋 View Deliveries
            </a>
            
            <p style="color: #666; font-size: 12px; margin-top: 30px; border-top: 1px solid #ddd; padding-top: 15px;">
                This is an automated notification from BizBooks.
            </p>
        </div>
    </body>
    </html>
    """
    
    body_text = f"""
▶️ Subscription Resumed

A customer has resumed their subscription deliveries.

Customer: {customer_name}
Phone: {customer_phone}
Plan: {subscription_plan}
Resumed From: {start_date} to {end_date}
Days Resumed: {resumed_days}

Please update your delivery schedule accordingly.

View deliveries: https://{tenant_name}.bizbooks.co.in/admin/subscriptions/deliveries

---
This is an automated notification from BizBooks.
    """
    
    return send_email(admin_email, subject, body_html, body_text)


def send_subscription_modify_notification(admin_email, customer_name, customer_phone, subscription_plan, delivery_date, new_quantity, unit_name, tenant_name):
    """
    Send email to admin when customer modifies delivery quantity
    """
    subject = f"✏️ Delivery Modified - {customer_name}"
    
    body_html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px;">
            <h2 style="color: #17a2b8; margin-bottom: 20px;">✏️ Delivery Quantity Modified</h2>
            
            <p>A customer has modified their delivery quantity.</p>
            
            <div style="background: #d1ecf1; border-left: 4px solid #17a2b8; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <p style="margin: 5px 0;"><strong>Customer:</strong> {customer_name}</p>
                <p style="margin: 5px 0;"><strong>Phone:</strong> {customer_phone}</p>
                <p style="margin: 5px 0;"><strong>Plan:</strong> {subscription_plan}</p>
                <p style="margin: 5px 0;"><strong>Delivery Date:</strong> {delivery_date}</p>
                <p style="margin: 5px 0; font-size: 18px; color: #17a2b8;"><strong>✏️ New Quantity: {new_quantity} {unit_name}</strong></p>
            </div>
            
            <p style="color: #666; font-size: 14px;">Please update this delivery accordingly.</p>
            
            <a href="https://{tenant_name}.bizbooks.co.in/admin/subscriptions/deliveries" 
               style="display: inline-block; padding: 12px 24px; background: #4CAF50; color: white; text-decoration: none; border-radius: 5px; margin-top: 15px; font-weight: 600;">
                📋 View Deliveries
            </a>
            
            <p style="color: #666; font-size: 12px; margin-top: 30px; border-top: 1px solid #ddd; padding-top: 15px;">
                This is an automated notification from BizBooks.
            </p>
        </div>
    </body>
    </html>
    """
    
    body_text = f"""
✏️ Delivery Quantity Modified

A customer has modified their delivery quantity.

Customer: {customer_name}
Phone: {customer_phone}
Plan: {subscription_plan}
Delivery Date: {delivery_date}
New Quantity: {new_quantity} {unit_name}

Please update this delivery accordingly.

View deliveries: https://{tenant_name}.bizbooks.co.in/admin/subscriptions/deliveries

---
This is an automated notification from BizBooks.
    """
    
    return send_email(admin_email, subject, body_html, body_text)


# ==================== CUSTOMER CONFIRMATION EMAILS ====================

def send_customer_pause_confirmation(customer_email, customer_name, subscription_plan, start_date, end_date, paused_days, tenant_name, support_phone):
    """Send confirmation email to customer when they pause their subscription"""
    subject = f"⏸️ Delivery Paused - {subscription_plan}"
    
    body_html = f"""<html><body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px;">
            <h2 style="color: #ffc107; margin-bottom: 20px;">⏸️ Delivery Paused Successfully</h2>
            <p>Hello {customer_name},</p>
            <p>Your delivery pause request has been confirmed!</p>
            <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <p style="margin: 5px 0;"><strong>Subscription:</strong> {subscription_plan}</p>
                <p style="margin: 5px 0;"><strong>Paused From:</strong> {start_date} to {end_date}</p>
                <p style="margin: 5px 0; font-size: 18px; color: #ffc107;"><strong>⏸️ {paused_days} days paused</strong></p>
            </div>
            <p style="color: #666; font-size: 14px;">Your deliveries will automatically resume after this period.</p>
            <a href="https://{tenant_name}.bizbooks.co.in/customer/subscriptions" style="display: inline-block; padding: 12px 24px; background: #4CAF50; color: white; text-decoration: none; border-radius: 5px; margin-top: 15px; font-weight: 600;">📋 View My Subscriptions</a>
            <p style="color: #999; font-size: 13px; margin-top: 20px; padding: 15px; background: #f9f9f9; border-radius: 5px;">💡 <strong>Need immediate changes after 9 PM?</strong><br>Call us at <strong>{support_phone}</strong></p>
            <p style="color: #666; font-size: 12px; margin-top: 30px; border-top: 1px solid #ddd; padding-top: 15px;">This is an automated confirmation from {tenant_name}.</p>
        </div></body></html>"""
    
    return send_email(customer_email, subject, body_html)


def send_customer_resume_confirmation(customer_email, customer_name, subscription_plan, start_date, end_date, resumed_days, tenant_name):
    """Send confirmation email to customer when they resume their subscription"""
    subject = f"▶️ Delivery Resumed - {subscription_plan}"
    
    body_html = f"""<html><body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px;">
            <h2 style="color: #28a745; margin-bottom: 20px;">▶️ Delivery Resumed Successfully</h2>
            <p>Hello {customer_name},</p>
            <p>Your delivery resume request has been confirmed!</p>
            <div style="background: #d4edda; border-left: 4px solid #28a745; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <p style="margin: 5px 0;"><strong>Subscription:</strong> {subscription_plan}</p>
                <p style="margin: 5px 0;"><strong>Resumed From:</strong> {start_date} to {end_date}</p>
                <p style="margin: 5px 0; font-size: 18px; color: #28a745;"><strong>▶️ {resumed_days} days resumed</strong></p>
            </div>
            <p style="color: #666; font-size: 14px;">Your deliveries will continue as scheduled.</p>
            <a href="https://{tenant_name}.bizbooks.co.in/customer/subscriptions" style="display: inline-block; padding: 12px 24px; background: #4CAF50; color: white; text-decoration: none; border-radius: 5px; margin-top: 15px; font-weight: 600;">📋 View My Subscriptions</a>
            <p style="color: #666; font-size: 12px; margin-top: 30px; border-top: 1px solid #ddd; padding-top: 15px;">This is an automated confirmation from {tenant_name}.</p>
        </div></body></html>"""
    
    return send_email(customer_email, subject, body_html)


def send_customer_modify_confirmation(customer_email, customer_name, subscription_plan, delivery_date, new_quantity, unit_name, tenant_name):
    """Send confirmation email to customer when they modify delivery quantity"""
    subject = f"✏️ Delivery Modified - {subscription_plan}"
    
    body_html = f"""<html><body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px;">
            <h2 style="color: #17a2b8; margin-bottom: 20px;">✏️ Delivery Quantity Modified</h2>
            <p>Hello {customer_name},</p>
            <p>Your delivery modification has been confirmed!</p>
            <div style="background: #d1ecf1; border-left: 4px solid #17a2b8; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <p style="margin: 5px 0;"><strong>Subscription:</strong> {subscription_plan}</p>
                <p style="margin: 5px 0;"><strong>Delivery Date:</strong> {delivery_date}</p>
                <p style="margin: 5px 0; font-size: 18px; color: #17a2b8;"><strong>✏️ New Quantity: {new_quantity} {unit_name}</strong></p>
            </div>
            <p style="color: #666; font-size: 14px;">This is a one-time modification. Other deliveries will continue with your default quantity.</p>
            <a href="https://{tenant_name}.bizbooks.co.in/customer/subscriptions" style="display: inline-block; padding: 12px 24px; background: #4CAF50; color: white; text-decoration: none; border-radius: 5px; margin-top: 15px; font-weight: 600;">📋 View My Subscriptions</a>
            <p style="color: #666; font-size: 12px; margin-top: 30px; border-top: 1px solid #ddd; padding-top: 15px;">This is an automated confirmation from {tenant_name}.</p>
        </div></body></html>"""
    
    return send_email(customer_email, subject, body_html)


# ==================== INVOICE EMAILS ====================

def send_invoice_email(customer_email, customer_name, invoice_number, invoice_id, total_amount, tenant_name, tenant_subdomain):
    """Send invoice PDF to customer via email"""
    subject = f"📄 Invoice {invoice_number} from {tenant_name}"
    
    invoice_url = f"https://{tenant_subdomain}.bizbooks.co.in/admin/invoices/{invoice_id}"
    
    body_html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px;">
            <h2 style="color: #2c3e50; margin-bottom: 20px;">📄 Invoice Generated</h2>
            
            <p>Dear {customer_name},</p>
            
            <p>Thank you for your purchase! Your invoice has been generated.</p>
            
            <div style="background: #f0f8ff; border-left: 4px solid #2c3e50; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <p style="margin: 5px 0;"><strong>Invoice Number:</strong> {invoice_number}</p>
                <p style="margin: 5px 0; font-size: 20px; color: #2c3e50;"><strong>Total Amount:</strong> ₹{total_amount:,.2f}</p>
            </div>
            
            <p>You can view and download your invoice by clicking the button below:</p>
            
            <a href="{invoice_url}" 
               style="display: inline-block; padding: 12px 24px; background: #2c3e50; color: white; text-decoration: none; border-radius: 5px; margin-top: 15px; font-weight: 600;">
                📄 View Invoice
            </a>
            
            <p style="color: #666; font-size: 14px; margin-top: 20px;">
                Please make payment as per the terms mentioned in the invoice.
            </p>
            
            <p style="color: #666; font-size: 14px;">
                If you have any questions, please don't hesitate to contact us.
            </p>
            
            <p style="color: #666; font-size: 12px; margin-top: 30px; border-top: 1px solid #ddd; padding-top: 15px;">
                This is an automated email from {tenant_name}.
            </p>
        </div>
    </body>
    </html>
    """
    
    body_text = f"""
📄 Invoice Generated

Dear {customer_name},

Thank you for your purchase! Your invoice has been generated.

Invoice Number: {invoice_number}
Total Amount: ₹{total_amount:,.2f}

View invoice: {invoice_url}

Please make payment as per the terms mentioned in the invoice.

If you have any questions, please don't hesitate to contact us.

---
This is an automated email from {tenant_name}.
    """
    
    return send_email(customer_email, subject, body_html, body_text)

