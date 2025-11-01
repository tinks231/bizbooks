from models.database import db
from datetime import datetime

class Task(db.Model):
    """Task management for employees"""
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False, index=True)
    task_number = db.Column(db.String(50), nullable=False)  # TASK-0001
    
    # Task details
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    priority = db.Column(db.String(20), default='medium')  # low, medium, high
    status = db.Column(db.String(20), default='new')  # new, in_progress, completed, cancelled
    
    # Assignment
    assigned_to = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False, index=True)
    site_id = db.Column(db.Integer, db.ForeignKey('sites.id'), nullable=True, index=True)
    
    # Dates
    start_date = db.Column(db.Date, nullable=True)
    deadline = db.Column(db.Date, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # Metadata
    created_by = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=True)  # Admin employee ID
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tenant = db.relationship('Tenant', backref=db.backref('tasks', lazy=True))
    employee = db.relationship('Employee', foreign_keys=[assigned_to], backref=db.backref('assigned_tasks', lazy=True))
    site = db.relationship('Site', backref=db.backref('tasks', lazy=True))
    updates = db.relationship('TaskUpdate', backref='task', lazy=True, cascade='all, delete-orphan')
    materials = db.relationship('TaskMaterial', backref='task', lazy=True, cascade='all, delete-orphan')
    media = db.relationship('TaskMedia', backref='task', lazy=True, cascade='all, delete-orphan')
    
    __table_args__ = (
        db.UniqueConstraint('tenant_id', 'task_number', name='_tenant_task_number_uc'),
        db.Index('idx_task_status', 'tenant_id', 'status'),
        db.Index('idx_task_employee', 'tenant_id', 'assigned_to'),
    )
    
    def __repr__(self):
        return f"<Task {self.task_number} - {self.title}>"
    
    @classmethod
    def generate_task_number(cls, tenant_id):
        """Generate next task number for tenant"""
        last_task = cls.query.filter_by(tenant_id=tenant_id).order_by(cls.id.desc()).first()
        if last_task:
            last_num = int(last_task.task_number.split('-')[-1])
            next_num = last_num + 1
        else:
            next_num = 1
        return f"TASK-{next_num:04d}"
    
    def get_progress_percentage(self):
        """Calculate task progress based on updates"""
        if self.status == 'completed':
            return 100
        elif self.status == 'in_progress':
            # Check if there are updates with progress
            updates_with_progress = [u for u in self.updates if u.progress_percentage]
            if updates_with_progress:
                return max([u.progress_percentage for u in updates_with_progress])
            return 30  # Default in_progress percentage
        else:
            return 0
    
    def is_overdue(self):
        """Check if task is overdue"""
        if self.deadline and self.status not in ['completed', 'cancelled']:
            return datetime.now().date() > self.deadline
        return False


class TaskUpdate(db.Model):
    """Employee updates on tasks"""
    __tablename__ = 'task_updates'
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False, index=True)
    
    # Update details
    status = db.Column(db.String(20), nullable=False)  # in_progress, completed
    notes = db.Column(db.Text)
    progress_percentage = db.Column(db.Integer, default=0)  # 0-100
    
    # Work details
    worker_count = db.Column(db.Integer, default=1)
    hours_worked = db.Column(db.Float, default=0)
    
    # Metadata
    updated_by = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    employee = db.relationship('Employee', backref=db.backref('task_updates', lazy=True))
    
    def __repr__(self):
        return f"<TaskUpdate {self.task_id} - {self.status}>"


class TaskMaterial(db.Model):
    """Materials used in tasks"""
    __tablename__ = 'task_materials'
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False, index=True)
    
    # Material details
    material_name = db.Column(db.String(200), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(50), default='pcs')  # pcs, kg, m, l, etc.
    
    # Cost (optional)
    cost_per_unit = db.Column(db.Float, default=0)
    total_cost = db.Column(db.Float, default=0)
    
    # Metadata
    added_by = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    employee = db.relationship('Employee', backref=db.backref('task_materials', lazy=True))
    
    def __repr__(self):
        return f"<TaskMaterial {self.material_name} - {self.quantity} {self.unit}>"


class TaskMedia(db.Model):
    """Photos/videos of task progress"""
    __tablename__ = 'task_media'
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False, index=True)
    
    # Media details
    media_type = db.Column(db.String(20), nullable=False)  # photo, video
    file_path = db.Column(db.String(500), nullable=False)  # URL or path
    caption = db.Column(db.Text)
    
    # Metadata
    uploaded_by = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    employee = db.relationship('Employee', backref=db.backref('task_media', lazy=True))
    
    def __repr__(self):
        return f"<TaskMedia {self.media_type} - Task {self.task_id}>"

