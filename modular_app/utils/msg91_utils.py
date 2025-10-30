"""
MSG91 SMS and WhatsApp notification utilities
Completely optional - if not configured, app continues working with email only
"""
import os
import requests
from flask import current_app

def send_sms(phone_number, message):
    """
    Send SMS via MSG91
    
    Args:
        phone_number: 10-digit Indian mobile number (without +91)
        message: SMS text to send
        
    Returns:
        bool: True if sent successfully, False otherwise
    """
    
    # Get MSG91 configuration from environment
    auth_key = os.getenv('MSG91_AUTH_KEY')
    sender_id = os.getenv('MSG91_SENDER_ID', 'BIZBKS')  # Default sender ID
    
    # If MSG91 not configured, skip silently (don't break the app!)
    if not auth_key:
        current_app.logger.info(f'MSG91 not configured. Would have sent SMS to {phone_number}: {message[:50]}...')
        return False
    
    try:
        # Clean phone number (remove spaces, +91, etc.)
        phone_number = str(phone_number).replace('+91', '').replace(' ', '').replace('-', '')
        
        # MSG91 API endpoint (v5 Send OTP/SMS API)
        url = 'https://control.msg91.com/api/v5/otp'
        
        # Alternative: Use v2 API (more reliable for transactional SMS)
        url = f'https://control.msg91.com/api/sendhttp.php'
        
        # Prepare payload for v2 API (more compatible)
        params = {
            'authkey': auth_key,
            'mobiles': phone_number,  # Just 10 digits
            'message': message,
            'sender': sender_id,
            'route': '4',  # 4 = Transactional route
            'country': '91'
        }
        
        # Send request (use GET for better compatibility)
        response = requests.get(url, params=params, timeout=10)
        
        # Log the full response for debugging
        current_app.logger.info(f'MSG91 Response: Status={response.status_code}, Body={response.text[:200]}')
        
        if response.status_code == 200 and 'success' in response.text.lower():
            current_app.logger.info(f'✅ SMS sent successfully to {phone_number}')
            return True
        else:
            current_app.logger.warning(f'❌ SMS failed to {phone_number}: Status={response.status_code}, Response={response.text}')
            return False
            
    except Exception as e:
        current_app.logger.error(f'❌ SMS error to {phone_number}: {str(e)}')
        return False


def send_whatsapp(phone_number, message):
    """
    Send WhatsApp message via MSG91
    
    Args:
        phone_number: 10-digit Indian mobile number (without +91)
        message: WhatsApp message text
        
    Returns:
        bool: True if sent successfully, False otherwise
    """
    
    # Get MSG91 configuration
    auth_key = os.getenv('MSG91_AUTH_KEY')
    
    # If MSG91 not configured, skip silently
    if not auth_key:
        current_app.logger.info(f'MSG91 not configured. Would have sent WhatsApp to {phone_number}: {message[:50]}...')
        return False
    
    try:
        # Clean phone number
        phone_number = str(phone_number).replace('+91', '').replace(' ', '').replace('-', '')
        
        # MSG91 WhatsApp API endpoint (API v5)
        url = 'https://api.msg91.com/api/v5/whatsapp/whatsapp-outbound-message/'
        
        headers = {
            'authkey': auth_key,
            'content-type': 'application/json'
        }
        
        payload = {
            'integrated_number': os.getenv('MSG91_WHATSAPP_NUMBER', ''),  # Your WhatsApp Business number
            'content_type': 'template',
            'payload': {
                'messaging_product': 'whatsapp',
                'recipient_type': 'individual',
                'to': f'91{phone_number}',
                'type': 'text',
                'text': {
                    'body': message
                }
            }
        }
        
        # Send request
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        # Log the full response for debugging
        current_app.logger.info(f'MSG91 WhatsApp Response: Status={response.status_code}, Body={response.text[:200]}')
        
        if response.status_code in [200, 201]:
            current_app.logger.info(f'✅ WhatsApp sent successfully to {phone_number}')
            return True
        else:
            current_app.logger.warning(f'❌ WhatsApp failed to {phone_number}: Status={response.status_code}, Response={response.text}')
            return False
            
    except Exception as e:
        current_app.logger.error(f'❌ WhatsApp error to {phone_number}: {str(e)}')
        return False


def send_purchase_request_notification_sms(admin_phone, employee_name, item_name, estimated_price, company_name):
    """Send SMS to admin when employee submits purchase request"""
    
    if not admin_phone:
        return False
    
    message = f"""New Purchase Request - {company_name}

Employee: {employee_name}
Item: {item_name}
Amount: Rs.{estimated_price:,.0f}

Login to approve/reject: https://{company_name.lower().replace(' ', '')}.bizbooks.co.in

- BizBooks"""
    
    return send_sms(admin_phone, message)


def send_purchase_approved_notification_sms(employee_phone, employee_name, item_name, approved_amount):
    """Send SMS to employee when purchase request is approved"""
    
    if not employee_phone:
        return False
    
    message = f"""Purchase Request APPROVED

Hi {employee_name},

Your request for {item_name} (Rs.{approved_amount:,.0f}) has been approved.

You can proceed with the purchase.

- BizBooks"""
    
    return send_sms(employee_phone, message)


def send_purchase_rejected_notification_sms(employee_phone, employee_name, item_name, rejection_reason):
    """Send SMS to employee when purchase request is rejected"""
    
    if not employee_phone:
        return False
    
    message = f"""Purchase Request REJECTED

Hi {employee_name},

Your request for {item_name} has been rejected.

Reason: {rejection_reason[:100]}

Please contact your supervisor.

- BizBooks"""
    
    return send_sms(employee_phone, message)


def send_purchase_request_notification_whatsapp(admin_phone, employee_name, item_name, estimated_price, company_name):
    """Send WhatsApp to admin when employee submits purchase request"""
    
    if not admin_phone:
        return False
    
    message = f"""🛒 *New Purchase Request*

*Company:* {company_name}
*Employee:* {employee_name}
*Item:* {item_name}
*Amount:* ₹{estimated_price:,.0f}

👉 Login to approve/reject
https://{company_name.lower().replace(' ', '')}.bizbooks.co.in/admin/purchase-requests

_Powered by BizBooks_"""
    
    return send_whatsapp(admin_phone, message)


def send_purchase_approved_notification_whatsapp(employee_phone, employee_name, item_name, approved_amount, admin_notes=None):
    """Send WhatsApp to employee when purchase request is approved"""
    
    if not employee_phone:
        return False
    
    notes_text = f"\n\n*Admin Notes:* {admin_notes}" if admin_notes else ""
    
    message = f"""✅ *Purchase Request APPROVED*

Hi {employee_name},

Your request has been approved! ✅

*Item:* {item_name}
*Approved Amount:* ₹{approved_amount:,.0f}{notes_text}

You can proceed with the purchase.

_Powered by BizBooks_"""
    
    return send_whatsapp(employee_phone, message)


def send_purchase_rejected_notification_whatsapp(employee_phone, employee_name, item_name, rejection_reason):
    """Send WhatsApp to employee when purchase request is rejected"""
    
    if not employee_phone:
        return False
    
    message = f"""❌ *Purchase Request REJECTED*

Hi {employee_name},

Your request has been rejected.

*Item:* {item_name}
*Reason:* {rejection_reason[:150]}

Please contact your supervisor for more details.

_Powered by BizBooks_"""
    
    return send_whatsapp(employee_phone, message)

