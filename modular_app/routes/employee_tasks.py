"""
Employee Task Routes
Employees can view their assigned tasks and update progress
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, Task, TaskUpdate, TaskMaterial, TaskMedia, Employee
from datetime import datetime

employee_tasks_bp = Blueprint('employee_tasks', __name__, url_prefix='/employee/tasks')


# Employee authentication decorator
from functools import wraps
def employee_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'employee_id' not in session:
            flash('Please login with your PIN', 'error')
            return redirect(url_for('employee_tasks.login'))
        return f(*args, **kwargs)
    return decorated_function


@employee_tasks_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Employee PIN login for tasks"""
    if request.method == 'POST':
        phone = request.form.get('phone')
        pin = request.form.get('pin')
        
        employee = Employee.query.filter_by(phone=phone, pin=pin, active=True).first()
        
        if employee:
            session['employee_id'] = employee.id
            session['employee_name'] = employee.name
            session['tenant_id'] = employee.tenant_id
            flash(f'Welcome {employee.name}!', 'success')
            return redirect(url_for('employee_tasks.my_tasks'))
        else:
            flash('Invalid phone or PIN', 'error')
    
    return render_template('employee_tasks/login.html')


@employee_tasks_bp.route('/logout')
def logout():
    """Employee logout"""
    session.pop('employee_id', None)
    session.pop('employee_name', None)
    session.pop('tenant_id', None)
    flash('Logged out successfully', 'success')
    return redirect(url_for('employee_tasks.login'))


@employee_tasks_bp.route('/my-tasks')
@employee_login_required
def my_tasks():
    """Show all tasks assigned to logged-in employee"""
    employee_id = session.get('employee_id')
    status_filter = request.args.get('status', 'all')
    
    # Base query
    query = Task.query.filter_by(assigned_to=employee_id)
    
    # Apply status filter
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    
    tasks = query.order_by(Task.deadline.asc().nullslast(), Task.created_at.desc()).all()
    
    # Calculate stats
    total_tasks = Task.query.filter_by(assigned_to=employee_id).count()
    new_tasks = Task.query.filter_by(assigned_to=employee_id, status='new').count()
    in_progress = Task.query.filter_by(assigned_to=employee_id, status='in_progress').count()
    completed = Task.query.filter_by(assigned_to=employee_id, status='completed').count()
    
    return render_template('employee_tasks/my_tasks.html',
                         tasks=tasks,
                         status_filter=status_filter,
                         total_tasks=total_tasks,
                         new_tasks=new_tasks,
                         in_progress=in_progress,
                         completed=completed,
                         employee_name=session.get('employee_name'))


@employee_tasks_bp.route('/<int:task_id>')
@employee_login_required
def view_task(task_id):
    """View task details"""
    employee_id = session.get('employee_id')
    task = Task.query.filter_by(id=task_id, assigned_to=employee_id).first_or_404()
    
    return render_template('employee_tasks/view_task.html',
                         task=task,
                         employee_name=session.get('employee_name'))


@employee_tasks_bp.route('/<int:task_id>/update', methods=['GET', 'POST'])
@employee_login_required
def update_task(task_id):
    """Update task progress"""
    employee_id = session.get('employee_id')
    task = Task.query.filter_by(id=task_id, assigned_to=employee_id).first_or_404()
    
    if request.method == 'POST':
        try:
            # Get form data
            status = request.form.get('status')
            notes = request.form.get('notes', '')
            progress_percentage = int(request.form.get('progress_percentage', 0))
            worker_count = int(request.form.get('worker_count', 1))
            hours_worked = float(request.form.get('hours_worked', 0))
            
            # Create task update
            task_update = TaskUpdate(
                task_id=task.id,
                status=status,
                notes=notes,
                progress_percentage=progress_percentage,
                worker_count=worker_count,
                hours_worked=hours_worked,
                updated_by=employee_id
            )
            db.session.add(task_update)
            
            # Update task status
            task.status = status
            if status == 'completed':
                task.completed_at = datetime.utcnow()
            
            # Handle materials
            material_names = request.form.getlist('material_name[]')
            material_quantities = request.form.getlist('material_quantity[]')
            material_units = request.form.getlist('material_unit[]')
            
            for i in range(len(material_names)):
                if material_names[i].strip():
                    material = TaskMaterial(
                        task_id=task.id,
                        material_name=material_names[i],
                        quantity=float(material_quantities[i]),
                        unit=material_units[i],
                        added_by=employee_id
                    )
                    db.session.add(material)
            
            # Handle photo/video uploads
            if 'media_files' in request.files:
                files = request.files.getlist('media_files')
                for file in files:
                    if file and file.filename:
                        from utils.helpers import save_uploaded_file
                        file_path = save_uploaded_file(file, 'uploads/task_media')
                        if file_path:
                            # Determine media type
                            media_type = 'photo' if file.filename.lower().endswith(('.jpg', '.jpeg', '.png')) else 'video'
                            
                            media = TaskMedia(
                                task_id=task.id,
                                media_type=media_type,
                                file_path=file_path,
                                caption=request.form.get('media_caption', ''),
                                uploaded_by=employee_id
                            )
                            db.session.add(media)
            
            db.session.commit()
            flash('✅ Task updated successfully!', 'success')
            return redirect(url_for('employee_tasks.view_task', task_id=task.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating task: {str(e)}', 'error')
    
    return render_template('employee_tasks/update_task.html',
                         task=task,
                         employee_name=session.get('employee_name'))

