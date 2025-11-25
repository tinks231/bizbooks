"""
WhatsApp Integration Utilities (WATI API)
Send invoices, order confirmations, and notifications via WhatsApp
"""
import os
import requests
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class WhatsAppService:
    """
    Service class for sending WhatsApp messages via WATI API
    """
    
    def __init__(self):
        """Initialize WATI API credentials from environment"""
        self.api_url = os.getenv('WATI_API_URL', 'https://live-server.wati.io')
        self.api_key = os.getenv('WATI_API_KEY', '')
        self.instance_id = os.getenv('WATI_INSTANCE_ID', '')
        self.enabled = bool(self.api_key and self.instance_id)
        
        if not self.enabled:
            logger.warning("⚠️ WhatsApp integration disabled - Missing WATI credentials")
    
    def _format_phone(self, phone):
        """
        Format phone number for WhatsApp (must include country code)
        Example: 9617217821 → 919617217821 (India +91)
        """
        if not phone:
            return None
        
        # Remove spaces, dashes, parentheses
        phone = ''.join(filter(str.isdigit, str(phone)))
        
        # Add India country code if not present
        if len(phone) == 10:
            phone = '91' + phone
        elif not phone.startswith('91') and len(phone) == 10:
            phone = '91' + phone
        
        return phone
    
    def _send_template_message(self, phone, template_name, parameters=None, file_url=None):
        """
        Send templated message via WATI API
        
        Args:
            phone: Customer phone number
            template_name: Approved template name in WATI
            parameters: List of parameter values for template
            file_url: Optional file URL (for PDF attachments)
        
        Returns:
            dict: API response or error details
        """
        if not self.enabled:
            logger.warning(f"WhatsApp disabled - Would send template '{template_name}' to {phone}")
            return {'success': False, 'error': 'WhatsApp integration disabled'}
        
        phone = self._format_phone(phone)
        if not phone:
            logger.error(f"Invalid phone number: {phone}")
            return {'success': False, 'error': 'Invalid phone number'}
        
        url = f"{self.api_url}/api/v1/sendTemplateMessage"
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'whatsappNumber': phone,
            'template_name': template_name,
            'broadcast_name': f'{template_name}_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        }
        
        # Add parameters if provided
        if parameters:
            payload['parameters'] = parameters
        
        # Add file attachment if provided
        if file_url:
            payload['media'] = {
                'url': file_url,
                'filename': file_url.split('/')[-1]
            }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            
            logger.info(f"✅ WhatsApp sent to {phone}: {template_name}")
            return {'success': True, 'response': response.json()}
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ WhatsApp send failed to {phone}: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _send_text_message(self, phone, message):
        """
        Send simple text message (for replies/conversations)
        
        Args:
            phone: Customer phone number
            message: Text message to send
        
        Returns:
            dict: API response or error details
        """
        if not self.enabled:
            logger.warning(f"WhatsApp disabled - Would send message to {phone}: {message[:50]}...")
            return {'success': False, 'error': 'WhatsApp integration disabled'}
        
        phone = self._format_phone(phone)
        if not phone:
            logger.error(f"Invalid phone number: {phone}")
            return {'success': False, 'error': 'Invalid phone number'}
        
        url = f"{self.api_url}/api/v1/sendSessionMessage/{phone}"
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'messageText': message
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            
            logger.info(f"✅ WhatsApp text sent to {phone}")
            return {'success': True, 'response': response.json()}
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ WhatsApp text failed to {phone}: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    # ========== BUSINESS MESSAGE FUNCTIONS ==========
    
    def send_invoice_notification(self, customer_phone, customer_name, invoice_number, 
                                  total_amount, pdf_url, view_url):
        """
        Send invoice notification with PDF attachment
        
        Args:
            customer_phone: Customer's WhatsApp number
            customer_name: Customer name
            invoice_number: Invoice number (e.g., INV-2025-029)
            total_amount: Total invoice amount
            pdf_url: Direct URL to PDF file
            view_url: URL to view invoice in customer portal
        
        Returns:
            dict: Send result
        """
        # Template parameters
        parameters = [
            {'name': 'customer_name', 'value': customer_name},
            {'name': 'invoice_number', 'value': invoice_number},
            {'name': 'amount', 'value': f'Rs {total_amount:,.2f}'},
            {'name': 'view_url', 'value': view_url}
        ]
        
        return self._send_template_message(
            phone=customer_phone,
            template_name='invoice_notification',  # ← You'll create this in WATI
            parameters=parameters,
            file_url=pdf_url
        )
    
    def send_order_confirmation(self, customer_phone, customer_name, order_id, 
                               items_summary, total_amount, delivery_date):
        """
        Send order confirmation message
        
        Args:
            customer_phone: Customer's WhatsApp number
            customer_name: Customer name
            order_id: Order ID/number
            items_summary: Brief summary of items (e.g., "Paneer 0.2kg, Milk 1L")
            total_amount: Total order amount
            delivery_date: Expected delivery date
        
        Returns:
            dict: Send result
        """
        parameters = [
            {'name': 'customer_name', 'value': customer_name},
            {'name': 'order_id', 'value': str(order_id)},
            {'name': 'items', 'value': items_summary},
            {'name': 'amount', 'value': f'Rs {total_amount:,.2f}'},
            {'name': 'delivery_date', 'value': delivery_date}
        ]
        
        return self._send_template_message(
            phone=customer_phone,
            template_name='order_confirmation',  # ← You'll create this in WATI
            parameters=parameters
        )
    
    def send_delivery_reminder(self, customer_phone, customer_name, items_summary, 
                              delivery_date, time_window="Morning"):
        """
        Send delivery reminder message
        
        Args:
            customer_phone: Customer's WhatsApp number
            customer_name: Customer name
            items_summary: Items to be delivered (e.g., "Milk 1L, Paneer 200g")
            delivery_date: Delivery date (e.g., "Today", "Tomorrow", "25-Nov-2025")
            time_window: Expected time (e.g., "Morning (6-10 AM)")
        
        Returns:
            dict: Send result
        """
        parameters = [
            {'name': 'customer_name', 'value': customer_name},
            {'name': 'items', 'value': items_summary},
            {'name': 'delivery_date', 'value': delivery_date},
            {'name': 'time_window', 'value': time_window}
        ]
        
        return self._send_template_message(
            phone=customer_phone,
            template_name='delivery_reminder',  # ← You'll create this in WATI
            parameters=parameters
        )
    
    def send_subscription_pause_notification(self, customer_phone, customer_name, 
                                            pause_date, product_name):
        """
        Send subscription pause confirmation
        
        Args:
            customer_phone: Customer's WhatsApp number
            customer_name: Customer name
            pause_date: Date paused for (e.g., "28-Nov-2025")
            product_name: Product name (e.g., "Milk Subscription")
        
        Returns:
            dict: Send result
        """
        parameters = [
            {'name': 'customer_name', 'value': customer_name},
            {'name': 'product_name', 'value': product_name},
            {'name': 'pause_date', 'value': pause_date}
        ]
        
        return self._send_template_message(
            phone=customer_phone,
            template_name='subscription_paused',  # ← You'll create this in WATI
            parameters=parameters
        )
    
    def send_subscription_resume_notification(self, customer_phone, customer_name, 
                                             resume_date, product_name):
        """
        Send subscription resume confirmation
        
        Args:
            customer_phone: Customer's WhatsApp number
            customer_name: Customer name
            resume_date: Date resumed from (e.g., "29-Nov-2025")
            product_name: Product name (e.g., "Milk Subscription")
        
        Returns:
            dict: Send result
        """
        parameters = [
            {'name': 'customer_name', 'value': customer_name},
            {'name': 'product_name', 'value': product_name},
            {'name': 'resume_date', 'value': resume_date}
        ]
        
        return self._send_template_message(
            phone=customer_phone,
            template_name='subscription_resumed',  # ← You'll create this in WATI
            parameters=parameters
        )
    
    def send_subscription_modify_notification(self, customer_phone, customer_name, 
                                             modify_date, old_quantity, new_quantity, 
                                             product_name):
        """
        Send subscription modification confirmation
        
        Args:
            customer_phone: Customer's WhatsApp number
            customer_name: Customer name
            modify_date: Date modified for (e.g., "28-Nov-2025")
            old_quantity: Original quantity
            new_quantity: New quantity
            product_name: Product name (e.g., "Milk")
        
        Returns:
            dict: Send result
        """
        parameters = [
            {'name': 'customer_name', 'value': customer_name},
            {'name': 'product_name', 'value': product_name},
            {'name': 'modify_date', 'value': modify_date},
            {'name': 'old_quantity', 'value': str(old_quantity)},
            {'name': 'new_quantity', 'value': str(new_quantity)}
        ]
        
        return self._send_template_message(
            phone=customer_phone,
            template_name='subscription_modified',  # ← You'll create this in WATI
            parameters=parameters
        )
    
    def send_payment_reminder(self, customer_phone, customer_name, outstanding_amount, 
                             due_date, payment_url):
        """
        Send payment reminder for outstanding invoices
        
        Args:
            customer_phone: Customer's WhatsApp number
            customer_name: Customer name
            outstanding_amount: Total outstanding amount
            due_date: Payment due date
            payment_url: URL to make payment
        
        Returns:
            dict: Send result
        """
        parameters = [
            {'name': 'customer_name', 'value': customer_name},
            {'name': 'amount', 'value': f'Rs {outstanding_amount:,.2f}'},
            {'name': 'due_date', 'value': due_date},
            {'name': 'payment_url', 'value': payment_url}
        ]
        
        return self._send_template_message(
            phone=customer_phone,
            template_name='payment_reminder',  # ← You'll create this in WATI
            parameters=parameters
        )


# ========== CONVENIENCE FUNCTIONS ==========

# Singleton instance
_whatsapp_service = None

def get_whatsapp_service():
    """Get or create WhatsApp service instance"""
    global _whatsapp_service
    if _whatsapp_service is None:
        _whatsapp_service = WhatsAppService()
    return _whatsapp_service


# Quick access functions
def send_invoice_whatsapp(customer_phone, customer_name, invoice_number, 
                         total_amount, pdf_url, view_url):
    """Send invoice notification via WhatsApp"""
    service = get_whatsapp_service()
    return service.send_invoice_notification(
        customer_phone, customer_name, invoice_number, 
        total_amount, pdf_url, view_url
    )


def send_order_confirmation_whatsapp(customer_phone, customer_name, order_id, 
                                    items_summary, total_amount, delivery_date):
    """Send order confirmation via WhatsApp"""
    service = get_whatsapp_service()
    return service.send_order_confirmation(
        customer_phone, customer_name, order_id, 
        items_summary, total_amount, delivery_date
    )


def send_delivery_reminder_whatsapp(customer_phone, customer_name, items_summary, 
                                   delivery_date, time_window="Morning"):
    """Send delivery reminder via WhatsApp"""
    service = get_whatsapp_service()
    return service.send_delivery_reminder(
        customer_phone, customer_name, items_summary, 
        delivery_date, time_window
    )


