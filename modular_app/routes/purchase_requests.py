"""
Purchase Request routes - Employee & Admin
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, g, session, current_app
from models import db, PurchaseRequest, Employee, Tenant, Expense, ExpenseCategory, Item, ItemCategory, ItemStock
from utils.tenant_middleware import require_tenant, get_current_tenant_id
from utils.license_check import check_license
from utils.email_utils import send_purchase_request_notification, send_purchase_approved_notification, send_purchase_rejected_notification
from utils.msg91_utils import (
    send_purchase_request_notification_sms,
    send_purchase_request_notification_whatsapp,
    send_purchase_approved_notification_sms,
    send_purchase_approved_notification_whatsapp,
    send_purchase_rejected_notification_sms,
    send_purchase_rejected_notification_whatsapp
)
from functools import wraps
from datetime import datetime
import pytz
import os

# Employee-facing blueprint (no /admin prefix)
purchase_request_bp = Blueprint('purchase_request', __name__)

# Admin-facing blueprint
admin_purchase_bp = Blueprint('admin_purchase', __name__, url_prefix='/admin/purchase-requests')


def login_required(f):
    """Decorator to require admin login"""
    @wraps(f)
    @check_license
    def decorated_function(*args, **kwargs):
        if 'tenant_admin_id' not in session:
            flash('Please login first', 'error')
            return redirect(url_for('admin.login'))
        if session.get('tenant_admin_id') != get_current_tenant_id():
            session.clear()
            flash('Session mismatch. Please login again.', 'error')
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function


# ===== EMPLOYEE ROUTES =====

@purchase_request_bp.route('/purchase-request', methods=['GET', 'POST'])
@require_tenant
def employee_form():
    """Employee purchase request form (PIN-based auth like attendance)"""
    # Check if employee already logged in via unified portal
    if 'employee_id' in session and 'employee_name' in session:
        # Already authenticated, go directly to form
        return redirect(url_for('purchase_request.submit_form'))
    
    tenant_id = get_current_tenant_id()
    tenant = Tenant.query.get(tenant_id)
    
    if request.method == 'POST':
        pin = request.form.get('pin')
        
        # Verify employee PIN
        employee = Employee.query.filter_by(tenant_id=tenant_id, pin=pin, active=True).first()
        
        if not employee:
            return """
            <div style="text-align: center; padding: 50px; font-family: Arial;">
                <h2 style="color: #dc3545;">❌ Invalid PIN</h2>
                <p>Please check your PIN and try again.</p>
                <a href='/purchase-request' style="display: inline-block; margin-top: 20px; padding: 10px 20px; background: #4CAF50; color: white; text-decoration: none; border-radius: 5px;">← Go Back</a>
            </div>
            """
        
        # Store employee in session for the form (use shared session from unified portal)
        session['employee_id'] = employee.id
        session['employee_name'] = employee.name
        return redirect(url_for('purchase_request.submit_form'))
    
    return render_template('purchase_request/employee_auth.html', tenant=tenant)


@purchase_request_bp.route('/purchase-request/submit', methods=['GET', 'POST'])
@require_tenant
def submit_form():
    """Purchase request submission form"""
    tenant_id = get_current_tenant_id()
    tenant = Tenant.query.get(tenant_id)
    
    # Check if employee authenticated (use shared session from unified portal)
    if 'employee_id' not in session:
        flash('Please enter your PIN first', 'error')
        return redirect(url_for('purchase_request.employee_form'))
    
    employee_id = session['employee_id']
    employee_name = session['employee_name']
    
    if request.method == 'POST':
        try:
            # Get form data
            item_name = request.form.get('item_name')
            quantity = float(request.form.get('quantity'))
            estimated_price = float(request.form.get('estimated_price'))
            vendor_name = request.form.get('vendor_name')
            request_type = request.form.get('request_type')  # 'expense' or 'inventory'
            category_id = request.form.get('category_id')
            reason = request.form.get('reason')
            
            # Handle document upload (if provided)
            document_url = None
            current_app.logger.info(f"📎 Checking for document upload...")
            current_app.logger.info(f"📎 Files in request: {list(request.files.keys())}")
            
            if 'document' in request.files:
                file = request.files['document']
                current_app.logger.info(f"📎 File object: {file}")
                current_app.logger.info(f"📎 Filename: {file.filename}")
                
                if file and file.filename:
                    current_app.logger.info(f"📤 Starting upload for: {file.filename}")
                    try:
                        from utils.vercel_blob import upload_to_vercel_blob, generate_blob_filename
                        from PIL import Image
                        import os
                        import io
                        
                        # Get file extension
                        file_ext = os.path.splitext(file.filename)[1].lower().replace('.', '')
                        
                        # Compress images before upload (save storage!)
                        if file_ext in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                            try:
                                # Read image
                                image = Image.open(file.stream)
                                original_size = file.content_length or 0
                                
                                # Convert RGBA to RGB if needed (for JPEG)
                                if image.mode in ('RGBA', 'LA', 'P'):
                                    background = Image.new('RGB', image.size, (255, 255, 255))
                                    if image.mode == 'P':
                                        image = image.convert('RGBA')
                                    background.paste(image, mask=image.split()[-1] if image.mode in ('RGBA', 'LA') else None)
                                    image = background
                                
                                # Resize if too large (max 1600px)
                                max_dimension = 1600
                                if image.width > max_dimension or image.height > max_dimension:
                                    image.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
                                    current_app.logger.info(f"📐 Resized image to {image.width}x{image.height}")
                                
                                # Save compressed to BytesIO
                                output = io.BytesIO()
                                image.save(output, format='JPEG', quality=75, optimize=True)
                                output.seek(0)
                                
                                compressed_size = len(output.getvalue())
                                savings = ((1 - compressed_size / original_size) * 100) if original_size > 0 else 0
                                
                                current_app.logger.info(f"🗜️ Compressed: {original_size/1024/1024:.2f}MB → {compressed_size/1024/1024:.2f}MB (saved {savings:.0f}%)")
                                
                                # Use compressed image for upload
                                file_to_upload = output
                                file_ext = 'jpg'  # Always save as JPEG after compression
                                mime_type = 'image/jpeg'
                            except Exception as e:
                                current_app.logger.warning(f"⚠️ Compression failed, using original: {str(e)}")
                                file.stream.seek(0)  # Reset stream
                                file_to_upload = file
                                mime_type = 'image/jpeg' if file_ext in ['jpg', 'jpeg'] else f'image/{file_ext}'
                        else:
                            # PDF - no compression
                            file_to_upload = file
                            mime_type = 'application/pdf'
                        
                        # Generate blob filename
                        blob_filename = generate_blob_filename('purchase_requests', employee_name, file_ext)
                        
                        # Upload to Vercel Blob
                        document_url = upload_to_vercel_blob(file_to_upload, blob_filename, mime_type)
                        
                        if document_url:
                            current_app.logger.info(f"✅ Document uploaded: {file.filename} → {document_url}")
                        else:
                            current_app.logger.warning(f"⚠️ Document upload failed for: {file.filename}")
                    except Exception as e:
                        current_app.logger.error(f"❌ Document upload error: {str(e)}")
                        current_app.logger.error(f"❌ Full error: {repr(e)}")
                        import traceback
                        current_app.logger.error(f"❌ Traceback: {traceback.format_exc()}")
                        # Continue without document - don't fail the entire request
            else:
                current_app.logger.info(f"📎 No document in request.files")
            
            # Create purchase request
            purchase_request = PurchaseRequest(
                tenant_id=tenant_id,
                employee_id=employee_id,
                item_name=item_name,
                quantity=quantity,
                estimated_price=estimated_price,
                vendor_name=vendor_name,
                request_type=request_type,
                category_id=int(category_id) if category_id else None,
                reason=reason,
                document_url=document_url,
                status='pending'
            )
            
            db.session.add(purchase_request)
            db.session.commit()
            
            # Send email notification to admin (ALWAYS)
            if tenant.admin_email:
                send_purchase_request_notification(
                    admin_email=tenant.admin_email,
                    employee_name=employee_name,
                    item_name=item_name,
                    estimated_price=estimated_price,
                    tenant_name=tenant.subdomain
                )
            
            # Send SMS/WhatsApp notification to admin (OPTIONAL - only if MSG91 configured)
            notification_type = os.getenv('MSG91_NOTIFICATION_TYPE', 'sms')  # 'sms' or 'whatsapp'
            if tenant.admin_phone:
                if notification_type == 'whatsapp':
                    send_purchase_request_notification_whatsapp(
                        admin_phone=tenant.admin_phone,
                        employee_name=employee_name,
                        item_name=item_name,
                        estimated_price=estimated_price,
                        company_name=tenant.company_name
                    )
                else:  # Default to SMS
                    send_purchase_request_notification_sms(
                        admin_phone=tenant.admin_phone,
                        employee_name=employee_name,
                        item_name=item_name,
                        estimated_price=estimated_price,
                        company_name=tenant.company_name
                    )
            
            # Clear session
            session.pop('pr_employee_id', None)
            session.pop('pr_employee_name', None)
            
            return """
            <div style="text-align: center; padding: 50px; font-family: Arial;">
                <h2 style="color: #28a745;">✅ Request Submitted!</h2>
                <p>Your purchase request has been sent to admin for approval.</p>
                <p style="color: #666; margin-top: 20px;">You will receive an email notification once it's reviewed.</p>
                <a href='/purchase-request' style="display: inline-block; margin-top: 20px; padding: 10px 20px; background: #4CAF50; color: white; text-decoration: none; border-radius: 5px;">Submit Another Request</a>
            </div>
            """
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'error')
            return redirect(url_for('purchase_request.submit_form'))
    
    # Get categories based on request type
    expense_categories = ExpenseCategory.query.filter_by(tenant_id=tenant_id, is_active=True).all()
    item_categories = ItemCategory.query.filter_by(tenant_id=tenant_id).all()
    
    return render_template('purchase_request/submit_form.html',
                         tenant=tenant,
                         employee_name=employee_name,
                         expense_categories=expense_categories,
                         item_categories=item_categories)


# ===== ADMIN ROUTES =====

@admin_purchase_bp.route('/', strict_slashes=False)  # PERFORMANCE: Prevent 308 redirects
@require_tenant
@login_required
def index():
    """List all purchase requests"""
    tenant_id = get_current_tenant_id()
    
    # Get filter from query params
    status_filter = request.args.get('status', 'all')
    
    # Build query
    query = PurchaseRequest.query.filter_by(tenant_id=tenant_id)
    
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    
    requests = query.order_by(PurchaseRequest.created_at.desc()).all()
    
    # Count by status for badges
    pending_count = PurchaseRequest.query.filter_by(tenant_id=tenant_id, status='pending').count()
    
    return render_template('admin/purchase_requests/list.html',
                         tenant=g.tenant,
                         requests=requests,
                         status_filter=status_filter,
                         pending_count=pending_count)


@admin_purchase_bp.route('/view/<int:request_id>')
@require_tenant
@login_required
def view_request(request_id):
    """View purchase request details"""
    tenant_id = get_current_tenant_id()
    purchase_request = PurchaseRequest.query.filter_by(tenant_id=tenant_id, id=request_id).first_or_404()
    
    # Get categories for approval form
    expense_categories = ExpenseCategory.query.filter_by(tenant_id=tenant_id, is_active=True).all()
    item_categories = ItemCategory.query.filter_by(tenant_id=tenant_id).all()
    
    return render_template('admin/purchase_requests/view.html',
                         tenant=g.tenant,
                         request=purchase_request,
                         expense_categories=expense_categories,
                         item_categories=item_categories)


@admin_purchase_bp.route('/approve/<int:request_id>', methods=['POST'])
@require_tenant
@login_required
def approve_request(request_id):
    """Approve purchase request and create expense or inventory"""
    tenant_id = get_current_tenant_id()
    purchase_request = PurchaseRequest.query.filter_by(tenant_id=tenant_id, id=request_id).first_or_404()
    
    try:
        # Get form data
        action_type = request.form.get('action_type')  # 'expense' or 'inventory'
        admin_notes = request.form.get('admin_notes')
        actual_amount = float(request.form.get('actual_amount', purchase_request.estimated_price))
        
        ist = pytz.timezone('Asia/Kolkata')
        now = datetime.now(ist)
        
        if action_type == 'expense':
            # Create expense record
            expense = Expense(
                tenant_id=tenant_id,
                expense_date=now.date(),
                category_id=purchase_request.category_id or int(request.form.get('category_id')),
                amount=actual_amount,
                description=f"{purchase_request.item_name} (Qty: {purchase_request.quantity}) - Requested by {purchase_request.employee.name}",
                payment_method=request.form.get('payment_method', 'Pending'),
                vendor_name=purchase_request.vendor_name,
                reference_number=f"PR-{purchase_request.id}"
            )
            db.session.add(expense)
            db.session.flush()
            
            purchase_request.created_expense_id = expense.id
            
        elif action_type == 'inventory':
            # Create/update inventory item
            category_id = purchase_request.category_id or int(request.form.get('category_id'))
            
            # Check if item exists
            item = Item.query.filter_by(
                tenant_id=tenant_id,
                name=purchase_request.item_name
            ).first()
            
            if not item:
                # Create new item
                item = Item(
                    tenant_id=tenant_id,
                    name=purchase_request.item_name,
                    category_id=category_id,
                    track_inventory=True,
                    purchase_price=actual_amount / purchase_request.quantity if purchase_request.quantity > 0 else actual_amount
                )
                db.session.add(item)
                db.session.flush()
            
            # Update stock
            stock = ItemStock.query.filter_by(item_id=item.id).first()
            if not stock:
                stock = ItemStock(item_id=item.id, quantity_available=0, unit_cost=0)
                db.session.add(stock)
                db.session.flush()
            
            # Add stock
            from models.item import ItemStockMovement
            movement = ItemStockMovement(
                item_id=item.id,
                movement_type='purchase',
                quantity=purchase_request.quantity,
                reference_number=f"PR-{purchase_request.id}",
                notes=f"Purchase request by {purchase_request.employee.name}"
            )
            db.session.add(movement)
            
            # Update stock quantity
            stock.quantity_available += purchase_request.quantity
            stock.unit_cost = actual_amount / purchase_request.quantity if purchase_request.quantity > 0 else actual_amount
            
            purchase_request.created_item_id = item.id
        
        # Update purchase request
        purchase_request.status = 'approved'
        purchase_request.admin_notes = admin_notes
        purchase_request.processed_by = g.tenant.company_name
        purchase_request.processed_at = now
        
        db.session.commit()
        
        # Send email to employee if they have email (ALWAYS)
        if purchase_request.employee.email:
            send_purchase_approved_notification(
                employee_email=purchase_request.employee.email,
                employee_name=purchase_request.employee.name,
                item_name=purchase_request.item_name,
                approved_amount=actual_amount,
                admin_notes=admin_notes
            )
        
        # Send SMS/WhatsApp to employee (OPTIONAL - only if MSG91 configured)
        notification_type = os.getenv('MSG91_NOTIFICATION_TYPE', 'sms')
        if purchase_request.employee.phone:
            if notification_type == 'whatsapp':
                send_purchase_approved_notification_whatsapp(
                    employee_phone=purchase_request.employee.phone,
                    employee_name=purchase_request.employee.name,
                    item_name=purchase_request.item_name,
                    approved_amount=actual_amount,
                    admin_notes=admin_notes
                )
            else:  # Default to SMS
                send_purchase_approved_notification_sms(
                    employee_phone=purchase_request.employee.phone,
                    employee_name=purchase_request.employee.name,
                    item_name=purchase_request.item_name,
                    approved_amount=actual_amount
                )
        
        flash('✅ Purchase request approved and record created!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error: {str(e)}', 'error')
    
    return redirect(url_for('admin_purchase.index'))


@admin_purchase_bp.route('/reject/<int:request_id>', methods=['POST'])
@require_tenant
@login_required
def reject_request(request_id):
    """Reject purchase request"""
    tenant_id = get_current_tenant_id()
    purchase_request = PurchaseRequest.query.filter_by(tenant_id=tenant_id, id=request_id).first_or_404()
    
    try:
        rejection_reason = request.form.get('rejection_reason')
        
        ist = pytz.timezone('Asia/Kolkata')
        
        purchase_request.status = 'rejected'
        purchase_request.rejection_reason = rejection_reason
        purchase_request.processed_by = g.tenant.company_name
        purchase_request.processed_at = datetime.now(ist)
        
        db.session.commit()
        
        # Send email to employee if they have email (ALWAYS)
        if purchase_request.employee.email:
            send_purchase_rejected_notification(
                employee_email=purchase_request.employee.email,
                employee_name=purchase_request.employee.name,
                item_name=purchase_request.item_name,
                rejection_reason=rejection_reason
            )
        
        # Send SMS/WhatsApp to employee (OPTIONAL - only if MSG91 configured)
        notification_type = os.getenv('MSG91_NOTIFICATION_TYPE', 'sms')
        if purchase_request.employee.phone:
            if notification_type == 'whatsapp':
                send_purchase_rejected_notification_whatsapp(
                    employee_phone=purchase_request.employee.phone,
                    employee_name=purchase_request.employee.name,
                    item_name=purchase_request.item_name,
                    rejection_reason=rejection_reason
                )
            else:  # Default to SMS
                send_purchase_rejected_notification_sms(
                    employee_phone=purchase_request.employee.phone,
                    employee_name=purchase_request.employee.name,
                    item_name=purchase_request.item_name,
                    rejection_reason=rejection_reason
                )
        
        flash('✅ Purchase request rejected', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error: {str(e)}', 'error')
    
    return redirect(url_for('admin_purchase.index'))

