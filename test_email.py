#!/usr/bin/env python3
"""
Test SMTP Email Configuration
Run this to verify Gmail SMTP is working correctly
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def test_smtp():
    """Test SMTP connection and send test email"""
    
    print("=" * 60)
    print("🔧 BizBooks SMTP Test")
    print("=" * 60)
    
    # Get configuration
    smtp_email = input("Enter SMTP_EMAIL (your Gmail): ").strip()
    smtp_password = input("Enter SMTP_PASSWORD (app password): ").strip()
    test_recipient = input("Enter test recipient email: ").strip()
    
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    
    print("\n" + "=" * 60)
    print("Testing SMTP Configuration...")
    print("=" * 60)
    print(f"SMTP Server: {smtp_server}:{smtp_port}")
    print(f"From Email: {smtp_email}")
    print(f"To Email: {test_recipient}")
    print()
    
    try:
        # Create test message
        msg = MIMEMultipart('alternative')
        msg['From'] = smtp_email
        msg['To'] = test_recipient
        msg['Subject'] = "🧪 BizBooks SMTP Test - " + str(os.urandom(4).hex())
        
        body_html = """
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #667eea;">✅ SMTP Test Successful!</h2>
            <p>If you're reading this, your BizBooks SMTP configuration is working correctly.</p>
            <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <p><strong>Configuration:</strong></p>
                <p>✅ SMTP Server: smtp.gmail.com:587</p>
                <p>✅ Authentication: Successful</p>
                <p>✅ Email Delivery: Working</p>
            </div>
            <p style="color: #666;">
                This test email confirms that:
                <ul>
                    <li>Your Gmail app password is correct</li>
                    <li>Gmail is accepting connections</li>
                    <li>Emails are being delivered</li>
                </ul>
            </p>
            <p><strong>Next Steps:</strong></p>
            <p>1. Check if this email is in your spam folder</p>
            <p>2. If in spam, mark as "Not Spam"</p>
            <p>3. Try creating a task or purchase request in BizBooks</p>
        </body>
        </html>
        """
        
        body_text = """
BizBooks SMTP Test - SUCCESS!

If you're reading this, your SMTP configuration is working.

Configuration:
✅ SMTP Server: smtp.gmail.com:587
✅ Authentication: Successful
✅ Email Delivery: Working

Next Steps:
1. Check if this email is in your spam folder
2. If in spam, mark as "Not Spam"
3. Try creating a task or purchase request
        """
        
        msg.attach(MIMEText(body_text, 'plain'))
        msg.attach(MIMEText(body_html, 'html'))
        
        # Send email
        print("🔄 Connecting to Gmail SMTP...")
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            print("✅ Connected!")
            
            print("🔄 Starting TLS encryption...")
            server.starttls()
            print("✅ TLS started!")
            
            print("🔄 Logging in...")
            server.login(smtp_email, smtp_password)
            print("✅ Login successful!")
            
            print("🔄 Sending test email...")
            server.send_message(msg)
            print("✅ Email sent!")
        
        print("\n" + "=" * 60)
        print("🎉 SUCCESS! Test email sent successfully!")
        print("=" * 60)
        print()
        print("📧 Check your inbox (and spam folder) for the test email.")
        print()
        print("If you receive it:")
        print("  ✅ SMTP is configured correctly")
        print("  ✅ BizBooks emails should work")
        print("  ⚠️  If in spam, mark as 'Not Spam'")
        print()
        print("If you DON'T receive it:")
        print("  ❌ Gmail may be blocking emails")
        print("  🔧 Try these fixes:")
        print("     1. Check app password is correct")
        print("     2. Enable 2-Factor Authentication")
        print("     3. Generate new app password")
        print("     4. Check Gmail security settings")
        print()
        
    except smtplib.SMTPAuthenticationError as e:
        print("\n" + "=" * 60)
        print("❌ AUTHENTICATION FAILED")
        print("=" * 60)
        print(f"Error: {e}")
        print()
        print("Common causes:")
        print("  1. Wrong app password")
        print("  2. 2-Factor Authentication not enabled")
        print("  3. App password not generated")
        print()
        print("Fix:")
        print("  1. Go to: https://myaccount.google.com/apppasswords")
        print("  2. Enable 2FA if not enabled")
        print("  3. Generate new app password")
        print("  4. Copy the 16-character password")
        print("  5. Use that password (not your Gmail password!)")
        print()
        
    except smtplib.SMTPException as e:
        print("\n" + "=" * 60)
        print("❌ SMTP ERROR")
        print("=" * 60)
        print(f"Error: {e}")
        print()
        print("Possible causes:")
        print("  1. Gmail blocking connection")
        print("  2. Network/firewall issue")
        print("  3. SMTP server down")
        print()
        
    except Exception as e:
        print("\n" + "=" * 60)
        print("❌ UNEXPECTED ERROR")
        print("=" * 60)
        print(f"Error: {e}")
        print()


if __name__ == "__main__":
    test_smtp()

