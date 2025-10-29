"""
Expenses management routes
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from models import db, Expense, ExpenseCategory
from utils.tenant_middleware import require_tenant, get_current_tenant_id
from utils.license_check import check_license
from functools import wraps
from datetime import datetime, timedelta
from sqlalchemy import func, extract
import pytz

# Create blueprint
expenses_bp = Blueprint('expenses', __name__, url_prefix='/admin/expenses')

def login_required(f):
    """Decorator to require admin login"""
    @wraps(f)
    @check_license
    def decorated_function(*args, **kwargs):
        from flask import session
        if 'tenant_admin_id' not in session:
            flash('Please login first', 'error')
            return redirect(url_for('admin.login'))
        if session.get('tenant_admin_id') != get_current_tenant_id():
            session.clear()
            flash('Session mismatch. Please login again.', 'error')
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function


# ===== EXPENSES =====
@expenses_bp.route('/')
@require_tenant
@login_required
def index():
    """List all expenses"""
    tenant_id = get_current_tenant_id()
    ist = pytz.timezone('Asia/Kolkata')
    
    # Get filter parameters
    category_id = request.args.get('category', type=int)
    month = request.args.get('month', type=int)
    year = request.args.get('year', type=int, default=datetime.now(ist).year)
    
    # Build query
    query = Expense.query.filter_by(tenant_id=tenant_id)
    
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    if month:
        query = query.filter(
            extract('month', Expense.expense_date) == month,
            extract('year', Expense.expense_date) == year
        )
    elif year:
        query = query.filter(extract('year', Expense.expense_date) == year)
    
    expenses = query.order_by(Expense.expense_date.desc()).all()
    
    # Calculate totals
    total_amount = sum(e.amount for e in expenses)
    
    # Get monthly breakdown for current year
    monthly_totals = db.session.query(
        extract('month', Expense.expense_date).label('month'),
        func.sum(Expense.amount).label('total')
    ).filter(
        Expense.tenant_id == tenant_id,
        extract('year', Expense.expense_date) == year
    ).group_by('month').all()
    
    monthly_data = {int(m): float(t) for m, t in monthly_totals}
    
    # Get categories
    categories = ExpenseCategory.query.filter_by(tenant_id=tenant_id, is_active=True).all()
    
    return render_template('admin/expenses/list.html',
                         expenses=expenses,
                         categories=categories,
                         total_amount=total_amount,
                         monthly_data=monthly_data,
                         selected_category=category_id,
                         selected_month=month,
                         selected_year=year,
                         tenant=g.tenant)


@expenses_bp.route('/add', methods=['POST'])
@require_tenant
@login_required
def add():
    """Add new expense"""
    tenant_id = get_current_tenant_id()
    ist = pytz.timezone('Asia/Kolkata')
    
    try:
        expense = Expense(
            tenant_id=tenant_id,
            expense_date=datetime.strptime(request.form.get('expense_date'), '%Y-%m-%d').date(),
            category_id=int(request.form.get('category_id')),
            amount=float(request.form.get('amount')),
            description=request.form.get('description'),
            payment_method=request.form.get('payment_method'),
            reference_number=request.form.get('reference_number'),
            vendor_name=request.form.get('vendor_name'),
            created_by=g.tenant.company_name
        )
        
        db.session.add(expense)
        db.session.commit()
        flash('✅ Expense added successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error adding expense: {str(e)}', 'error')
    
    return redirect(url_for('expenses.index'))


@expenses_bp.route('/delete/<int:expense_id>')
@require_tenant
@login_required
def delete(expense_id):
    """Delete expense"""
    tenant_id = get_current_tenant_id()
    
    expense = Expense.query.filter_by(tenant_id=tenant_id, id=expense_id).first_or_404()
    
    db.session.delete(expense)
    db.session.commit()
    flash('✅ Expense deleted!', 'success')
    
    return redirect(url_for('expenses.index'))


# ===== CATEGORIES =====
@expenses_bp.route('/categories')
@require_tenant
@login_required
def categories():
    """Manage expense categories"""
    tenant_id = get_current_tenant_id()
    
    categories = ExpenseCategory.query.filter_by(tenant_id=tenant_id).all()
    
    # Get expense count per category
    category_stats = {}
    for cat in categories:
        count = Expense.query.filter_by(tenant_id=tenant_id, category_id=cat.id).count()
        total = db.session.query(func.sum(Expense.amount))\
            .filter_by(tenant_id=tenant_id, category_id=cat.id).scalar() or 0
        category_stats[cat.id] = {'count': count, 'total': total}
    
    return render_template('admin/expenses/categories.html',
                         categories=categories,
                         category_stats=category_stats,
                         tenant=g.tenant)


@expenses_bp.route('/categories/add', methods=['POST'])
@require_tenant
@login_required
def add_category():
    """Add new expense category"""
    tenant_id = get_current_tenant_id()
    
    try:
        category = ExpenseCategory(
            tenant_id=tenant_id,
            name=request.form.get('name'),
            description=request.form.get('description')
        )
        
        db.session.add(category)
        db.session.commit()
        flash('✅ Category added!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error: {str(e)}', 'error')
    
    return redirect(url_for('expenses.categories'))


@expenses_bp.route('/categories/delete/<int:category_id>')
@require_tenant
@login_required
def delete_category(category_id):
    """Delete expense category"""
    tenant_id = get_current_tenant_id()
    
    category = ExpenseCategory.query.filter_by(tenant_id=tenant_id, id=category_id).first_or_404()
    
    # Check if category has expenses
    expense_count = Expense.query.filter_by(tenant_id=tenant_id, category_id=category_id).count()
    
    if expense_count > 0:
        flash(f'❌ Cannot delete category with {expense_count} expenses!', 'error')
    else:
        db.session.delete(category)
        db.session.commit()
        flash('✅ Category deleted!', 'success')
    
    return redirect(url_for('expenses.categories'))

