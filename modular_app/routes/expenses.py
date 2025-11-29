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
    """List all expenses - OPTIMIZED with pagination"""
    tenant_id = get_current_tenant_id()
    ist = pytz.timezone('Asia/Kolkata')
    
    # Get filter parameters
    category_id = request.args.get('category', type=int)
    month = request.args.get('month', type=int)
    year = request.args.get('year', type=int, default=datetime.now(ist).year)
    page = request.args.get('page', 1, type=int)
    per_page = 50
    
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
    
    # OPTIMIZED: Paginate expenses (instead of loading ALL)
    query = query.order_by(Expense.expense_date.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    expenses = pagination.items
    
    # OPTIMIZED: Calculate totals using SQL aggregation
    total_query = Expense.query.filter_by(tenant_id=tenant_id)
    if category_id:
        total_query = total_query.filter_by(category_id=category_id)
    if month:
        total_query = total_query.filter(
            extract('month', Expense.expense_date) == month,
            extract('year', Expense.expense_date) == year
        )
    elif year:
        total_query = total_query.filter(extract('year', Expense.expense_date) == year)
    
    total_amount = db.session.query(func.sum(Expense.amount)).filter(
        Expense.id.in_([e.id for e in total_query.with_entities(Expense.id).all()])
    ).scalar() or 0
    
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
    
    # Get active bank/cash accounts for expense payment
    from models import BankAccount
    bank_accounts = BankAccount.query.filter_by(
        tenant_id=tenant_id,
        is_active=True
    ).order_by(
        BankAccount.account_type,
        BankAccount.account_name
    ).all()
    
    return render_template('admin/expenses/list.html',
                         expenses=expenses,
                         page=page,
                         total_pages=pagination.pages,
                         total_items=pagination.total,
                         categories=categories,
                         bank_accounts=bank_accounts,
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
        from models import BankAccount
        from decimal import Decimal
        from sqlalchemy import text
        
        expense_date = datetime.strptime(request.form.get('expense_date'), '%Y-%m-%d').date()
        amount = Decimal(str(request.form.get('amount')))
        account_id = request.form.get('account_id')
        
        # Validate account
        if not account_id:
            flash('⚠️ Please select a bank/cash account', 'warning')
            return redirect(url_for('expenses.index'))
        
        account = BankAccount.query.filter_by(
            id=account_id,
            tenant_id=tenant_id,
            is_active=True
        ).first()
        
        if not account:
            flash('⚠️ Invalid bank/cash account selected', 'error')
            return redirect(url_for('expenses.index'))
        
        # Check sufficient balance
        if account.current_balance < amount:
            flash(f'⚠️ Insufficient balance in {account.account_name}. Current: ₹{account.current_balance:,.2f}', 'warning')
            return redirect(url_for('expenses.index'))
        
        expense = Expense(
            tenant_id=tenant_id,
            expense_date=expense_date,
            category_id=int(request.form.get('category_id')),
            amount=float(amount),
            description=request.form.get('description'),
            payment_method=request.form.get('payment_method'),
            reference_number=request.form.get('reference_number'),
            vendor_name=request.form.get('vendor_name'),
            created_by=g.tenant.company_name
        )
        
        db.session.add(expense)
        db.session.flush()  # Get expense ID
        
        # Create account transaction (Money OUT - Credit account)
        now = datetime.now(ist)
        new_balance = Decimal(str(account.current_balance)) - amount
        
        db.session.execute(text("""
            INSERT INTO account_transactions
            (tenant_id, account_id, transaction_date, transaction_type,
             debit_amount, credit_amount, balance_after, reference_type, reference_id,
             voucher_number, narration, created_at, created_by)
            VALUES (:tenant_id, :account_id, :txn_date, :txn_type,
                    :debit, :credit, :balance, :ref_type, :ref_id,
                    :voucher, :narration, :created_at, :created_by)
        """), {
            'tenant_id': tenant_id,
            'account_id': account_id,
            'txn_date': expense_date,
            'txn_type': 'expense',
            'debit': Decimal('0.00'),
            'credit': amount,  # Money spent = Credit
            'balance': new_balance,
            'ref_type': 'expense',
            'ref_id': expense.id,
            'voucher': f'EXP-{expense.id}',
            'narration': f'{expense.description[:100]} - {expense.vendor_name or "Business Expense"}',
            'created_at': now,
            'created_by': None  # FIX: Set to NULL instead of tenant_admin_id
        })
        
        # Update account balance
        db.session.execute(text("""
            UPDATE bank_accounts 
            SET current_balance = :new_balance, updated_at = :updated_at
            WHERE id = :account_id AND tenant_id = :tenant_id
        """), {
            'new_balance': new_balance,
            'updated_at': now,
            'account_id': account_id,
            'tenant_id': tenant_id
        })
        
        db.session.commit()
        flash(f'✅ Expense recorded! ₹{amount:,.2f} paid from {account.account_name}', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error adding expense: {str(e)}', 'error')
        import traceback
        traceback.print_exc()
    
    return redirect(url_for('expenses.index'))


@expenses_bp.route('/edit/<int:expense_id>', methods=['GET', 'POST'])
@require_tenant
@login_required
def edit(expense_id):
    """Edit expense"""
    tenant_id = get_current_tenant_id()
    expense = Expense.query.filter_by(tenant_id=tenant_id, id=expense_id).first_or_404()
    
    if request.method == 'POST':
        try:
            expense.expense_date = datetime.strptime(request.form.get('expense_date'), '%Y-%m-%d').date()
            expense.category_id = int(request.form.get('category_id'))
            expense.amount = float(request.form.get('amount'))
            expense.description = request.form.get('description')
            expense.payment_method = request.form.get('payment_method')
            expense.reference_number = request.form.get('reference_number')
            expense.vendor_name = request.form.get('vendor_name')
            
            db.session.commit()
            flash('✅ Expense updated!', 'success')
            return redirect(url_for('expenses.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'❌ Error: {str(e)}', 'error')
    
    categories = ExpenseCategory.query.filter_by(tenant_id=tenant_id, is_active=True).all()
    return render_template('admin/expenses/edit.html', 
                         expense=expense, 
                         categories=categories,
                         tenant=g.tenant)


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


@expenses_bp.route('/categories/create-defaults')
@require_tenant
@login_required
def create_default_categories():
    """Create default expense categories"""
    tenant_id = get_current_tenant_id()
    
    default_categories = [
        {'name': 'Rent', 'description': 'Office/Shop rent payments'},
        {'name': 'Salaries', 'description': 'Employee salaries and wages'},
        {'name': 'Utilities', 'description': 'Electricity, water, internet bills'},
        {'name': 'Office Supplies', 'description': 'Stationery, printing, consumables'},
        {'name': 'Travel', 'description': 'Business travel and transportation'},
        {'name': 'Marketing', 'description': 'Advertising and promotional expenses'},
        {'name': 'Maintenance', 'description': 'Repairs and maintenance'},
        {'name': 'Inventory Purchases', 'description': 'Stock and material purchases'},
        {'name': 'Professional Fees', 'description': 'Consultant, legal, accounting fees'},
        {'name': 'Insurance', 'description': 'Business insurance premiums'},
        {'name': 'Taxes', 'description': 'Government taxes and fees'},
        {'name': 'Miscellaneous', 'description': 'Other expenses'},
    ]
    
    created = 0
    for cat_data in default_categories:
        # Check if category already exists
        existing = ExpenseCategory.query.filter_by(
            tenant_id=tenant_id, 
            name=cat_data['name']
        ).first()
        
        if not existing:
            category = ExpenseCategory(
                tenant_id=tenant_id,
                name=cat_data['name'],
                description=cat_data['description']
            )
            db.session.add(category)
            created += 1
    
    db.session.commit()
    
    if created > 0:
        flash(f'✅ Created {created} default categories!', 'success')
    else:
        flash('ℹ️ All default categories already exist', 'info')
    
    return redirect(url_for('expenses.categories'))


# ===== REPORTS =====
@expenses_bp.route('/reports')
@require_tenant
@login_required
def reports():
    """Expense reports and analytics"""
    tenant_id = get_current_tenant_id()
    
    # Get selected month/year or default to current
    selected_month = request.args.get('month', type=int) or datetime.now().month
    selected_year = request.args.get('year', type=int) or datetime.now().year
    
    # Total expenses for selected month
    month_expenses = db.session.query(func.sum(Expense.amount)).filter(
        Expense.tenant_id == tenant_id,
        extract('month', Expense.expense_date) == selected_month,
        extract('year', Expense.expense_date) == selected_year
    ).scalar() or 0
    
    # Category-wise breakdown for selected month
    category_breakdown = db.session.query(
        ExpenseCategory.name,
        func.sum(Expense.amount).label('total'),
        func.count(Expense.id).label('count')
    ).join(Expense).filter(
        Expense.tenant_id == tenant_id,
        extract('month', Expense.expense_date) == selected_month,
        extract('year', Expense.expense_date) == selected_year
    ).group_by(ExpenseCategory.name).all()
    
    # Daily expenses for selected month
    daily_expenses = db.session.query(
        Expense.expense_date,
        func.sum(Expense.amount).label('total')
    ).filter(
        Expense.tenant_id == tenant_id,
        extract('month', Expense.expense_date) == selected_month,
        extract('year', Expense.expense_date) == selected_year
    ).group_by(Expense.expense_date).order_by(Expense.expense_date).all()
    
    # Last 6 months trend
    months_trend = []
    for i in range(5, -1, -1):
        date = datetime.now() - timedelta(days=i*30)
        month_total = db.session.query(func.sum(Expense.amount)).filter(
            Expense.tenant_id == tenant_id,
            extract('month', Expense.expense_date) == date.month,
            extract('year', Expense.expense_date) == date.year
        ).scalar() or 0
        months_trend.append({
            'month': date.strftime('%B %Y'),
            'total': month_total
        })
    
    # Recent expenses (last 10)
    recent_expenses = Expense.query.filter_by(tenant_id=tenant_id).order_by(Expense.expense_date.desc()).limit(10).all()
    
    return render_template('admin/expenses/reports.html',
                         tenant=g.tenant,
                         selected_month=selected_month,
                         selected_year=selected_year,
                         month_expenses=month_expenses,
                         category_breakdown=category_breakdown,
                         daily_expenses=daily_expenses,
                         months_trend=months_trend,
                         recent_expenses=recent_expenses)

