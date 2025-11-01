"""
Task Management Routes
Handles both admin (create/assign) and employee (update/upload) operations
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, g, jsonify, session
from models import db, Task, TaskUpdate, TaskMaterial, TaskMedia, Employee, Site
from utils.tenant_middleware import require_tenant, get_current_tenant_id
from datetime import datetime, date
from sqlalchemy import or_

tasks_bp = Blueprint('tasks', __name__, url_prefix='/admin/tasks')

# Login required decorator (matches admin.py)
from functools import wraps
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'tenant_admin_id' not in session:
            flash('Please login to access this page', 'error')
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function


# ============================================
# ADMIN ROUTES - Task Management
# ============================================

@tasks_bp.route('/')
@require_tenant
@login_required
def index():
    """List all tasks with filters"""
    tenant_id = g.tenant.id
    
    # Auto-cleanup old media (once per day)
    run_auto_cleanup(tenant_id)
    
    # Get filters from query params
    status_filter = request.args.get('status', 'all')
    employee_filter = request.args.get('employee', 'all')
    site_filter = request.args.get('site', 'all')
    priority_filter = request.args.get('priority', 'all')
    search = request.args.get('search', '').strip()
    
    # Base query
    query = Task.query.filter_by(tenant_id=tenant_id)
    
    # Apply filters
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    
    if employee_filter != 'all':
        query = query.filter_by(assigned_to=int(employee_filter))
    
    if site_filter != 'all':
        query = query.filter_by(site_id=int(site_filter))
    
    if priority_filter != 'all':
        query = query.filter_by(priority=priority_filter)
    
    if search:
        query = query.filter(
            or_(
                Task.task_number.ilike(f'%{search}%'),
                Task.title.ilike(f'%{search}%'),
                Task.description.ilike(f'%{search}%')
            )
        )
    
    # Order by created date (newest first)
    tasks = query.order_by(Task.created_at.desc()).all()
    
    # Get all employees and sites for filters
    employees = Employee.query.filter_by(tenant_id=tenant_id, active=True).order_by(Employee.name).all()
    sites = Site.query.filter_by(tenant_id=tenant_id).order_by(Site.name).all()
    
    # Calculate stats
    total_tasks = Task.query.filter_by(tenant_id=tenant_id).count()
    new_tasks = Task.query.filter_by(tenant_id=tenant_id, status='new').count()
    in_progress = Task.query.filter_by(tenant_id=tenant_id, status='in_progress').count()
    completed = Task.query.filter_by(tenant_id=tenant_id, status='completed').count()
    
    return render_template('admin/tasks/list.html',
                         tenant=g.tenant,
                         tasks=tasks,
                         employees=employees,
                         sites=sites,
                         status_filter=status_filter,
                         employee_filter=employee_filter,
                         site_filter=site_filter,
                         priority_filter=priority_filter,
                         search=search,
                         total_tasks=total_tasks,
                         new_tasks=new_tasks,
                         in_progress=in_progress,
                         completed=completed)


@tasks_bp.route('/create', methods=['GET', 'POST'])
@require_tenant
@login_required
def create():
    """Create new task"""
    tenant_id = g.tenant.id
    
    if request.method == 'POST':
        try:
            # Get form data
            title = request.form.get('title')
            description = request.form.get('description', '')
            priority = request.form.get('priority', 'medium')
            assigned_to = int(request.form.get('assigned_to'))
            site_id = request.form.get('site_id')
            start_date = request.form.get('start_date')
            deadline = request.form.get('deadline')
            
            # Convert dates
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date() if start_date else None
            deadline = datetime.strptime(deadline, '%Y-%m-%d').date() if deadline else None
            
            # Handle site_id (can be empty)
            site_id = int(site_id) if site_id and site_id != '' else None
            
            # Generate task number
            task_number = Task.generate_task_number(tenant_id)
            
            # Create task
            task = Task(
                tenant_id=tenant_id,
                task_number=task_number,
                title=title,
                description=description,
                priority=priority,
                assigned_to=assigned_to,
                site_id=site_id,
                start_date=start_date,
                deadline=deadline,
                status='new'
            )
            
            db.session.add(task)
            db.session.commit()
            
            # Send email notification
            employee = Employee.query.get(assigned_to)
            if employee and employee.email:
                send_task_assignment_email(task, employee)
            
            flash(f'✅ Task {task_number} created and assigned to {employee.name}!', 'success')
            return redirect(url_for('tasks.view', task_id=task.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating task: {str(e)}', 'error')
            return redirect(url_for('tasks.create'))
    
    # GET request - show form
    employees = Employee.query.filter_by(tenant_id=tenant_id, active=True).order_by(Employee.name).all()
    sites = Site.query.filter_by(tenant_id=tenant_id).order_by(Site.name).all()
    today = date.today().strftime('%Y-%m-%d')
    
    return render_template('admin/tasks/create.html',
                         tenant=g.tenant,
                         employees=employees,
                         sites=sites,
                         today=today)


@tasks_bp.route('/<int:task_id>')
@require_tenant
@login_required
def view(task_id):
    """View task details"""
    tenant_id = g.tenant.id
    task = Task.query.filter_by(id=task_id, tenant_id=tenant_id).first_or_404()
    
    return render_template('admin/tasks/view.html',
                         tenant=g.tenant,
                         task=task)


@tasks_bp.route('/<int:task_id>/edit', methods=['GET', 'POST'])
@require_tenant
@login_required
def edit(task_id):
    """Edit existing task"""
    tenant_id = g.tenant.id
    task = Task.query.filter_by(id=task_id, tenant_id=tenant_id).first_or_404()
    
    if request.method == 'POST':
        try:
            task.title = request.form.get('title')
            task.description = request.form.get('description', '')
            task.priority = request.form.get('priority', 'medium')
            task.assigned_to = int(request.form.get('assigned_to'))
            
            site_id = request.form.get('site_id')
            task.site_id = int(site_id) if site_id and site_id != '' else None
            
            start_date = request.form.get('start_date')
            task.start_date = datetime.strptime(start_date, '%Y-%m-%d').date() if start_date else None
            
            deadline = request.form.get('deadline')
            task.deadline = datetime.strptime(deadline, '%Y-%m-%d').date() if deadline else None
            
            db.session.commit()
            flash('Task updated successfully!', 'success')
            return redirect(url_for('tasks.view', task_id=task.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating task: {str(e)}', 'error')
    
    employees = Employee.query.filter_by(tenant_id=tenant_id, active=True).order_by(Employee.name).all()
    sites = Site.query.filter_by(tenant_id=tenant_id).order_by(Site.name).all()
    
    return render_template('admin/tasks/edit.html',
                         tenant=g.tenant,
                         task=task,
                         employees=employees,
                         sites=sites)


@tasks_bp.route('/<int:task_id>/cancel', methods=['POST'])
@require_tenant
@login_required
def cancel(task_id):
    """Cancel a task"""
    tenant_id = g.tenant.id
    task = Task.query.filter_by(id=task_id, tenant_id=tenant_id).first_or_404()
    
    try:
        task.status = 'cancelled'
        db.session.commit()
        flash('Task cancelled', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error cancelling task: {str(e)}', 'error')
    
    return redirect(url_for('tasks.index'))


@tasks_bp.route('/cleanup-old-media', methods=['POST'])
@require_tenant
@login_required
def cleanup_old_media():
    """Delete task media older than 30 days to save storage"""
    tenant_id = g.tenant.id
    
    try:
        from datetime import timedelta
        from utils.vercel_blob import delete_from_vercel_blob
        import os
        
        # Calculate cutoff date (30 days ago)
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        
        # Find all old media for this tenant's tasks
        old_media = TaskMedia.query.join(Task).filter(
            Task.tenant_id == tenant_id,
            TaskMedia.created_at < cutoff_date
        ).all()
        
        deleted_count = 0
        failed_count = 0
        storage_saved = 0
        
        for media in old_media:
            try:
                # Delete from Vercel Blob Storage (if on Vercel)
                if os.environ.get('VERCEL') and media.file_path.startswith('http'):
                    if delete_from_vercel_blob(media.file_path):
                        deleted_count += 1
                        # Estimate storage saved (assume 300KB per compressed image)
                        storage_saved += 0.3
                    else:
                        failed_count += 1
                
                # Delete from database
                db.session.delete(media)
                
            except Exception as e:
                print(f"❌ Error deleting media {media.id}: {e}")
                failed_count += 1
                continue
        
        db.session.commit()
        
        if deleted_count > 0:
            flash(f'✅ Cleaned up {deleted_count} old media files (saved ~{storage_saved:.1f}MB)', 'success')
        else:
            flash('No old media found to cleanup', 'info')
            
        if failed_count > 0:
            flash(f'⚠️ {failed_count} files could not be deleted', 'warning')
            
    except Exception as e:
        db.session.rollback()
        flash(f'Error during cleanup: {str(e)}', 'error')
    
    return redirect(url_for('tasks.index'))


# ============================================
# HELPER FUNCTIONS
# ============================================

def run_auto_cleanup(tenant_id):
    """
    Automatically cleanup old media once per day
    Lightweight check - only runs if last cleanup was >24 hours ago
    """
    try:
        from models import Tenant
        from datetime import timedelta
        from utils.vercel_blob import delete_from_vercel_blob
        import os
        
        tenant = Tenant.query.get(tenant_id)
        if not tenant:
            return
        
        # Check last cleanup date from tenant settings
        settings = tenant.settings or {}
        last_cleanup = settings.get('last_media_cleanup')
        
        # Convert string to datetime if exists
        if last_cleanup:
            try:
                last_cleanup = datetime.fromisoformat(last_cleanup)
            except:
                last_cleanup = None
        
        # Only run if last cleanup was >24 hours ago (or never run)
        now = datetime.utcnow()
        if last_cleanup and (now - last_cleanup).total_seconds() < 86400:  # 24 hours
            return  # Too soon, skip cleanup
        
        # Run cleanup
        cutoff_date = now - timedelta(days=30)
        old_media = TaskMedia.query.join(Task).filter(
            Task.tenant_id == tenant_id,
            TaskMedia.created_at < cutoff_date
        ).all()
        
        deleted_count = 0
        for media in old_media:
            try:
                # Delete from Vercel Blob (if on Vercel)
                if os.environ.get('VERCEL') and media.file_path.startswith('http'):
                    delete_from_vercel_blob(media.file_path)
                
                db.session.delete(media)
                deleted_count += 1
            except Exception as e:
                print(f"❌ Auto-cleanup error for media {media.id}: {e}")
                continue
        
        # Update last cleanup timestamp
        settings['last_media_cleanup'] = now.isoformat()
        tenant.settings = settings
        db.session.commit()
        
        if deleted_count > 0:
            print(f"✅ Auto-cleanup: Deleted {deleted_count} old media files for tenant {tenant_id}")
        
    except Exception as e:
        print(f"❌ Auto-cleanup failed: {e}")
        db.session.rollback()


def send_task_assignment_email(task, employee):
    """Send email notification when task is assigned"""
    try:
        from utils.email_utils import send_email
        
        subject = f"New Task Assigned - {task.title}"
        
        body = f"""
Hi {employee.name},

You have been assigned a new task:

Task Number: {task.task_number}
Title: {task.title}
Priority: {task.priority.upper()}
{f"Site: {task.site.name}" if task.site else ""}
{f"Start Date: {task.start_date.strftime('%d-%b-%Y')}" if task.start_date else ""}
{f"Deadline: {task.deadline.strftime('%d-%b-%Y')}" if task.deadline else ""}

Description:
{task.description}

Please login to your account to view details and update progress.

Login: {request.host_url}

---
BizBooks Task Management
        """
        
        send_email(
            to_email=employee.email,
            subject=subject,
            body=body
        )
        
    except Exception as e:
        print(f"Email notification failed: {str(e)}")

