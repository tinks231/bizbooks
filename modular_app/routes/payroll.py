"""
Payroll Management Routes
Simple salary management for small businesses
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, g, session
from models import db
from sqlalchemy import text
from datetime import datetime
import pytz
from decimal import Decimal
from utils.tenant_middleware import require_tenant, get_current_tenant_id

payroll_bp = Blueprint('payroll', __name__, url_prefix='/admin/payroll')


def login_required(f):
    """Require login to access route"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'tenant_admin_id' not in session:
            flash('⚠️ Please login first', 'warning')
            return redirect(url_for('admin.login'))
        # Verify session tenant matches current tenant
        if session.get('tenant_admin_id') != get_current_tenant_id():
            flash('⚠️ Session mismatch. Please login again.', 'warning')
            session.clear()
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function


@payroll_bp.route('/pay-salary', methods=['GET', 'POST'])
@require_tenant
@login_required
def pay_salary():
    """
    Pay Salary Page
    Select employees and pay monthly salary
    """
    from flask import g
    tenant_id = g.tenant.id if hasattr(g, 'tenant') and g.tenant else session.get('tenant_id')
    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.now(ist)
    
    # Get current month/year from request or default to current
    selected_month = int(request.args.get('month', now.month))
    selected_year = int(request.args.get('year', now.year))
    
    if request.method == 'POST':
        try:
            # Get form data
            payment_date_str = request.form.get('payment_date')
            payment_date = datetime.strptime(payment_date_str, '%Y-%m-%d').date()
            account_id = request.form.get('account_id')
            selected_employees = request.form.getlist('employee_ids')
            
            if not selected_employees:
                flash('⚠️ Please select at least one employee', 'warning')
                return redirect(url_for('payroll.pay_salary'))
            
            # Get employee details and calculate total
            employees_to_pay = []
            total_amount = Decimal('0')
            
            for emp_id in selected_employees:
                emp = db.session.execute(text("""
                    SELECT id, name, monthly_salary, designation
                    FROM employees
                    WHERE id = :emp_id AND tenant_id = :tenant_id AND active = TRUE
                """), {'emp_id': int(emp_id), 'tenant_id': tenant_id}).fetchone()
                
                if emp and emp[2] and emp[2] > 0:
                    employees_to_pay.append(emp)
                    total_amount += Decimal(str(emp[2]))
            
            if not employees_to_pay:
                flash('⚠️ No valid employees with salary to pay', 'warning')
                return redirect(url_for('payroll.pay_salary'))
            
            # Create payroll payment record
            result = db.session.execute(text("""
                INSERT INTO payroll_payments 
                (tenant_id, payment_month, payment_year, payment_date, total_amount, 
                 paid_from_account_id, created_at, created_by)
                VALUES (:tenant_id, :month, :year, :date, :total, :account_id, :created_at, :created_by)
                ON CONFLICT (tenant_id, payment_month, payment_year) 
                DO UPDATE SET 
                    payment_date = EXCLUDED.payment_date,
                    total_amount = payroll_payments.total_amount + EXCLUDED.total_amount,
                    paid_from_account_id = EXCLUDED.paid_from_account_id
                RETURNING id
            """), {
                'tenant_id': tenant_id,
                'month': selected_month,
                'year': selected_year,
                'date': payment_date,
                'total': float(total_amount),
                'account_id': int(account_id) if account_id else None,
                'created_at': now,
                'created_by': None
            })
            payroll_id = result.fetchone()[0]
            
            # Create individual salary slips
            for emp in employees_to_pay:
                db.session.execute(text("""
                    INSERT INTO salary_slips
                    (tenant_id, payroll_payment_id, employee_id, payment_month, payment_year,
                     salary_amount, payment_date, payment_method, created_at)
                    VALUES (:tenant_id, :payroll_id, :emp_id, :month, :year,
                            :amount, :date, :method, :created_at)
                """), {
                    'tenant_id': tenant_id,
                    'payroll_id': payroll_id,
                    'emp_id': emp[0],
                    'month': selected_month,
                    'year': selected_year,
                    'amount': float(emp[2]),
                    'date': payment_date,
                    'method': 'Cash',
                    'created_at': now
                })
            
            # Create accounting entry (Salary Expense → Cash/Bank)
            if account_id:
                account = db.session.execute(text("""
                    SELECT account_name, current_balance FROM bank_accounts
                    WHERE id = :account_id AND tenant_id = :tenant_id
                """), {'account_id': int(account_id), 'tenant_id': tenant_id}).fetchone()
                
                new_balance = Decimal(str(account[1])) - total_amount
                
                # Update account balance
                db.session.execute(text("""
                    UPDATE bank_accounts 
                    SET current_balance = :new_balance
                    WHERE id = :account_id AND tenant_id = :tenant_id
                """), {'new_balance': float(new_balance), 'account_id': int(account_id), 'tenant_id': tenant_id})
                
                # Create account transaction
                db.session.execute(text("""
                    INSERT INTO account_transactions
                    (tenant_id, account_id, transaction_date, transaction_type,
                     debit_amount, credit_amount, balance_after, reference_type, reference_id,
                     voucher_number, narration, created_at, created_by)
                    VALUES (:tenant_id, :account_id, :date, :type,
                            :debit, :credit, :balance, :ref_type, :ref_id,
                            :voucher, :narration, :created_at, :created_by)
                """), {
                    'tenant_id': tenant_id,
                    'account_id': int(account_id),
                    'date': payment_date,
                    'type': 'salary_payment',
                    'debit': 0.00,
                    'credit': float(total_amount),
                    'balance': float(new_balance),
                    'ref_type': 'payroll',
                    'ref_id': payroll_id,
                    'voucher': f'SAL-{selected_year}-{selected_month:02d}',
                    'narration': f'Salary payment for {selected_month}/{selected_year} - {len(employees_to_pay)} employees',
                    'created_at': now,
                    'created_by': None
                })
            
            db.session.commit()
            
            flash(f'✅ Salary paid to {len(employees_to_pay)} employee(s) - Total: ₹{total_amount:,.2f}', 'success')
            return redirect(url_for('payroll.salary_register'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'❌ Error paying salary: {str(e)}', 'error')
            return redirect(url_for('payroll.pay_salary'))
    
    # GET request - show pay salary form
    # Get all active employees with salary
    employees = db.session.execute(text("""
        SELECT 
            e.id,
            e.name,
            e.monthly_salary,
            e.designation,
            COALESCE(ss.payment_date, NULL) as last_paid
        FROM employees e
        LEFT JOIN salary_slips ss ON e.id = ss.employee_id 
            AND ss.payment_month = :month 
            AND ss.payment_year = :year
            AND ss.tenant_id = :tenant_id
        WHERE e.tenant_id = :tenant_id 
        AND e.active = TRUE
        AND e.monthly_salary IS NOT NULL 
        AND e.monthly_salary > 0
        ORDER BY e.name
    """), {
        'tenant_id': tenant_id,
        'month': selected_month,
        'year': selected_year
    }).fetchall()
    
    # Get bank/cash accounts
    accounts = db.session.execute(text("""
        SELECT id, account_name, account_type, current_balance
        FROM bank_accounts
        WHERE tenant_id = :tenant_id AND is_active = TRUE
        ORDER BY account_name
    """), {'tenant_id': tenant_id}).fetchall()
    
    return render_template('admin/payroll/pay_salary.html',
                         employees=employees,
                         accounts=accounts,
                         selected_month=selected_month,
                         selected_year=selected_year,
                         today=now.date(),
                         tenant=g.tenant)


@payroll_bp.route('/salary-register')
@require_tenant
@login_required
def salary_register():
    """
    Salary Register Report
    Monthly salary report showing all payments
    """
    from flask import g
    tenant_id = g.tenant.id if hasattr(g, 'tenant') and g.tenant else session.get('tenant_id')
    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.now(ist)
    
    # Get month/year from request
    selected_month = int(request.args.get('month', now.month))
    selected_year = int(request.args.get('year', now.year))
    
    # Get all salary payments for this month
    salary_data = db.session.execute(text("""
        SELECT 
            e.name,
            e.designation,
            ss.salary_amount,
            ss.payment_date,
            ss.payment_method,
            ba.account_name
        FROM salary_slips ss
        JOIN employees e ON ss.employee_id = e.id
        LEFT JOIN payroll_payments pp ON ss.payroll_payment_id = pp.id
        LEFT JOIN bank_accounts ba ON pp.paid_from_account_id = ba.id
        WHERE ss.tenant_id = :tenant_id
        AND ss.payment_month = :month
        AND ss.payment_year = :year
        ORDER BY ss.payment_date DESC, e.name
    """), {
        'tenant_id': tenant_id,
        'month': selected_month,
        'year': selected_year
    }).fetchall()
    
    # Calculate total
    total_salary = sum(Decimal(str(row[2])) for row in salary_data) if salary_data else Decimal('0')
    
    return render_template('admin/payroll/salary_register.html',
                         salary_data=salary_data,
                         total_salary=float(total_salary),
                         selected_month=selected_month,
                         selected_year=selected_year,
                         tenant=g.tenant)


@payroll_bp.route('/test-update/<int:emp_id>')
@require_tenant
@login_required
def test_update_employee(emp_id):
    """Test: Manually update an employee's payroll fields"""
    from flask import g
    from models import Employee
    tenant_id = g.tenant.id if hasattr(g, 'tenant') and g.tenant else session.get('tenant_id')
    
    # Get employee
    employee = Employee.query.filter_by(id=emp_id, tenant_id=tenant_id).first()
    
    if not employee:
        return jsonify({
            'status': 'error',
            'message': f'Employee with ID {emp_id} not found'
        })
    
    # Store old values
    old_values = {
        'monthly_salary': employee.monthly_salary,
        'designation': employee.designation,
        'date_of_joining': str(employee.date_of_joining) if employee.date_of_joining else None
    }
    
    # Try to update
    try:
        employee.monthly_salary = 18000.00
        employee.designation = "Test Designation"
        employee.date_of_joining = "2024-01-01"
        
        db.session.commit()
        
        # Verify it was saved
        db.session.refresh(employee)
        
        new_values = {
            'monthly_salary': employee.monthly_salary,
            'designation': employee.designation,
            'date_of_joining': str(employee.date_of_joining) if employee.date_of_joining else None
        }
        
        return jsonify({
            'status': 'success',
            'employee_name': employee.name,
            'old_values': old_values,
            'new_values': new_values,
            'test': 'Manually set salary=18000, designation=Test Designation, date_of_joining=2024-01-01',
            'saved': new_values != old_values
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e),
            'traceback': str(e.__traceback__)
        })


@payroll_bp.route('/debug-employees')
@require_tenant
@login_required
def debug_employees():
    """Debug: Show all employees with their salary info"""
    from flask import g
    tenant_id = g.tenant.id if hasattr(g, 'tenant') and g.tenant else session.get('tenant_id')
    
    # First, check if columns exist
    try:
        columns_check = db.session.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'employees' 
            AND column_name IN ('monthly_salary', 'designation', 'date_of_joining')
            ORDER BY column_name
        """)).fetchall()
        
        existing_columns = [col[0] for col in columns_check]
    except Exception as e:
        existing_columns = f"Error checking columns: {str(e)}"
    
    employees = db.session.execute(text("""
        SELECT 
            id,
            name,
            pin,
            active,
            monthly_salary,
            designation,
            date_of_joining,
            site_id
        FROM employees
        WHERE tenant_id = :tenant_id
        ORDER BY name
    """), {'tenant_id': tenant_id}).fetchall()
    
    result = []
    for emp in employees:
        result.append({
            'id': emp[0],
            'name': emp[1],
            'pin': emp[2],
            'active': emp[3],
            'monthly_salary': str(emp[4]) if emp[4] else 'NULL',
            'designation': emp[5] if emp[5] else 'NULL',
            'date_of_joining': str(emp[6]) if emp[6] else 'NULL',
            'site_id': emp[7] if emp[7] else 'NULL'
        })
    
    return jsonify({
        'status': 'success',
        'tenant_id': tenant_id,
        'database_columns_exist': existing_columns,
        'total_employees': len(employees),
        'employees': result,
        'employees_with_salary': [e for e in result if e['monthly_salary'] != 'NULL' and float(e['monthly_salary']) > 0],
        'migration_url': '/migrate/add-payroll-tables'
    })


@payroll_bp.route('/salary-slip/<int:employee_id>')
@require_tenant
@login_required
def salary_slip(employee_id):
    """
    Individual Salary Slip (Printable)
    """
    from flask import g
    tenant_id = g.tenant.id if hasattr(g, 'tenant') and g.tenant else session.get('tenant_id')
    
    # Get month/year from request
    selected_month = int(request.args.get('month'))
    selected_year = int(request.args.get('year'))
    
    # Get salary slip data
    slip_data = db.session.execute(text("""
        SELECT 
            e.name,
            e.designation,
            ss.salary_amount,
            ss.payment_date,
            ss.payment_method
        FROM salary_slips ss
        JOIN employees e ON ss.employee_id = e.id
        WHERE ss.tenant_id = :tenant_id
        AND ss.employee_id = :emp_id
        AND ss.payment_month = :month
        AND ss.payment_year = :year
    """), {
        'tenant_id': tenant_id,
        'emp_id': employee_id,
        'month': selected_month,
        'year': selected_year
    }).fetchone()
    
    if not slip_data:
        flash('❌ Salary slip not found', 'error')
        return redirect(url_for('payroll.salary_register'))
    
    return render_template('admin/payroll/salary_slip.html',
                         slip_data=slip_data,
                         selected_month=selected_month,
                         selected_year=selected_year,
                         tenant=g.tenant)

