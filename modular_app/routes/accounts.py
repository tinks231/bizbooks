"""
Bank/Cash Account Management Routes
Phase 1 of Accounting Module
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, g, session
from models import db, BankAccount, AccountTransaction
from utils.tenant_middleware import require_tenant, get_current_tenant_id
from sqlalchemy import text
from datetime import datetime
import pytz
from decimal import Decimal

accounts_bp = Blueprint('accounts', __name__, url_prefix='/admin/accounts')


# ============================================================
# DECORATORS
# ============================================================
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

@accounts_bp.route('/', methods=['GET'])
@require_tenant
@login_required
def list_accounts():
    """List all bank/cash accounts"""
    tenant_id = get_current_tenant_id()
    
    # Get all accounts
    accounts = db.session.execute(text("""
        SELECT 
            id, account_name, account_type, bank_name, account_number,
            current_balance, is_active, is_default, description
        FROM bank_accounts
        WHERE tenant_id = :tenant_id
        ORDER BY 
            CASE account_type 
                WHEN 'cash' THEN 1 
                WHEN 'bank' THEN 2 
                WHEN 'petty_cash' THEN 3 
            END,
            account_name
    """), {'tenant_id': tenant_id}).fetchall()
    
    # Calculate totals
    total_cash = sum(acc[5] for acc in accounts if acc[2] == 'cash' and acc[6])
    total_bank = sum(acc[5] for acc in accounts if acc[2] == 'bank' and acc[6])
    total_balance = total_cash + total_bank
    
    # Count accounts
    total_accounts = len(accounts)
    active_accounts = sum(1 for acc in accounts if acc[6])
    
    return render_template('admin/accounts/list.html',
                         accounts=accounts,
                         total_accounts=total_accounts,
                         active_accounts=active_accounts,
                         total_cash=total_cash,
                         total_bank=total_bank,
                         total_balance=total_balance,
                         tenant=g.tenant)


@accounts_bp.route('/create', methods=['POST'])
@require_tenant
@login_required
def create_account():
    """Create new bank/cash account (via AJAX modal)"""
    tenant_id = get_current_tenant_id()
    
    try:
        # Get form data
        account_name = request.form.get('account_name')
        account_type = request.form.get('account_type', 'bank')
        bank_name = request.form.get('bank_name')
        account_number = request.form.get('account_number')
        ifsc_code = request.form.get('ifsc_code')
        branch = request.form.get('branch')
        opening_balance = Decimal(request.form.get('opening_balance', '0.00'))
        description = request.form.get('description')
        is_default = True if request.form.get('is_default') == 'on' else False
        
        # Validation
        if not account_name:
            flash('❌ Account name is required', 'error')
            return redirect(url_for('accounts.list_accounts'))
        
        # If marking as default, unmark others of same type
        if is_default:
            db.session.execute(text("""
                UPDATE bank_accounts 
                SET is_default = FALSE 
                WHERE tenant_id = :tenant_id AND account_type = :account_type
            """), {'tenant_id': tenant_id, 'account_type': account_type})
        
        ist = pytz.timezone('Asia/Kolkata')
        now = datetime.now(ist)
        
        # Insert account
        result = db.session.execute(text("""
            INSERT INTO bank_accounts 
            (tenant_id, account_name, account_type, bank_name, account_number,
             ifsc_code, branch, opening_balance, current_balance, is_active,
             is_default, description, created_at, updated_at)
            VALUES (:tenant_id, :account_name, :account_type, :bank_name, :account_number,
                    :ifsc_code, :branch, :opening_balance, :current_balance, :is_active,
                    :is_default, :description, :created_at, :updated_at)
            RETURNING id
        """), {
            'tenant_id': tenant_id, 'account_name': account_name, 'account_type': account_type,
            'bank_name': bank_name, 'account_number': account_number, 'ifsc_code': ifsc_code,
            'branch': branch, 'opening_balance': opening_balance, 'current_balance': opening_balance,
            'is_active': True, 'is_default': is_default, 'description': description,
            'created_at': now, 'updated_at': now
        })
        
        account_id = result.fetchone()[0]  # Get the returned ID (PostgreSQL way)
        
        # If opening balance > 0, create opening balance transaction
        if opening_balance > 0:
            db.session.execute(text("""
                INSERT INTO account_transactions
                (tenant_id, account_id, transaction_date, transaction_type,
                 debit_amount, credit_amount, balance_after, narration, created_at)
                VALUES (:tenant_id, :account_id, :transaction_date, :transaction_type,
                        :debit_amount, :credit_amount, :balance_after, :narration, :created_at)
            """), {
                'tenant_id': tenant_id, 'account_id': account_id, 'transaction_date': now.date(),
                'transaction_type': 'opening_balance', 'debit_amount': opening_balance,
                'credit_amount': 0.00, 'balance_after': opening_balance,
                'narration': 'Opening balance', 'created_at': now
            })
        
        db.session.commit()
        
        account_icon = '💵' if account_type == 'cash' else '🏦'
        flash(f'✅ {account_icon} Account "{account_name}" created successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error creating account: {str(e)}', 'error')
    
    return redirect(url_for('accounts.list_accounts'))


@accounts_bp.route('/edit/<int:account_id>', methods=['POST'])
@require_tenant
@login_required
def edit_account(account_id):
    """Edit existing account (via AJAX modal)"""
    tenant_id = get_current_tenant_id()
    
    try:
        # Get form data
        account_name = request.form.get('account_name')
        bank_name = request.form.get('bank_name')
        account_number = request.form.get('account_number')
        ifsc_code = request.form.get('ifsc_code')
        branch = request.form.get('branch')
        description = request.form.get('description')
        new_balance = Decimal(request.form.get('current_balance', '0.00'))
        is_active = True if request.form.get('is_active') == 'on' else False
        is_default = True if request.form.get('is_default') == 'on' else False
        
        # Validation
        if not account_name:
            flash('❌ Account name is required', 'error')
            return redirect(url_for('accounts.list_accounts'))
        
        # Get current account details (type and balance)
        account_info = db.session.execute(
            text("SELECT account_type, current_balance FROM bank_accounts WHERE id = :account_id AND tenant_id = :tenant_id"),
            {'account_id': account_id, 'tenant_id': tenant_id}
        ).fetchone()
        account_type = account_info[0]
        old_balance = Decimal(str(account_info[1]))
        
        # If marking as default, unmark others of same type
        if is_default:
            db.session.execute(text("""
                UPDATE bank_accounts 
                SET is_default = FALSE 
                WHERE tenant_id = :tenant_id AND account_type = :account_type AND id != :account_id
            """), {'tenant_id': tenant_id, 'account_type': account_type, 'account_id': account_id})
        
        ist = pytz.timezone('Asia/Kolkata')
        now = datetime.now(ist)
        
        # Update account
        db.session.execute(text("""
            UPDATE bank_accounts
            SET account_name = :account_name, bank_name = :bank_name, account_number = :account_number,
                ifsc_code = :ifsc_code, branch = :branch, description = :description,
                current_balance = :current_balance, is_active = :is_active, is_default = :is_default, 
                updated_at = :updated_at
            WHERE id = :account_id AND tenant_id = :tenant_id
        """), {
            'account_name': account_name, 'bank_name': bank_name, 'account_number': account_number,
            'ifsc_code': ifsc_code, 'branch': branch, 'description': description,
            'current_balance': new_balance, 'is_active': is_active, 'is_default': is_default, 
            'updated_at': now, 'account_id': account_id, 'tenant_id': tenant_id
        })
        
        # If balance changed, create adjustment transaction
        if new_balance != old_balance:
            adjustment = new_balance - old_balance
            if adjustment > 0:
                # Balance increased (debit)
                debit_amt = adjustment
                credit_amt = Decimal('0.00')
                narration = f'Balance adjustment: ₹{adjustment:,.2f} added'
            else:
                # Balance decreased (credit)
                debit_amt = Decimal('0.00')
                credit_amt = abs(adjustment)
                narration = f'Balance adjustment: ₹{abs(adjustment):,.2f} deducted'
            
            db.session.execute(text("""
                INSERT INTO account_transactions
                (tenant_id, account_id, transaction_date, transaction_type,
                 debit_amount, credit_amount, balance_after, narration, created_at)
                VALUES (:tenant_id, :account_id, :transaction_date, :transaction_type,
                        :debit_amount, :credit_amount, :balance_after, :narration, :created_at)
            """), {
                'tenant_id': tenant_id, 'account_id': account_id, 'transaction_date': now.date(),
                'transaction_type': 'balance_adjustment', 'debit_amount': debit_amt,
                'credit_amount': credit_amt, 'balance_after': new_balance,
                'narration': narration, 'created_at': now
            })
        
        db.session.commit()
        
        balance_msg = f' Balance updated to ₹{new_balance:,.2f}.' if new_balance != old_balance else ''
        flash(f'✅ Account "{account_name}" updated successfully!{balance_msg}', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error updating account: {str(e)}', 'error')
    
    return redirect(url_for('accounts.list_accounts'))


@accounts_bp.route('/delete/<int:account_id>', methods=['POST'])
@require_tenant
@login_required
def delete_account(account_id):
    """Delete account (only if no transactions)"""
    tenant_id = get_current_tenant_id()
    
    try:
        # Check if account has transactions
        txn_count = db.session.execute(text("""
            SELECT COUNT(*) FROM account_transactions
            WHERE account_id = :account_id AND tenant_id = :tenant_id
        """), {'account_id': account_id, 'tenant_id': tenant_id}).fetchone()[0]
        
        if txn_count > 0:
            flash(f'❌ Cannot delete account with {txn_count} transactions. Deactivate it instead.', 'error')
            return redirect(url_for('accounts.list_accounts'))
        
        # Get account name
        account_name = db.session.execute(
            text("SELECT account_name FROM bank_accounts WHERE id = :account_id AND tenant_id = :tenant_id"),
            {'account_id': account_id, 'tenant_id': tenant_id}
        ).fetchone()[0]
        
        # Delete account
        db.session.execute(
            text("DELETE FROM bank_accounts WHERE id = :account_id AND tenant_id = :tenant_id"),
            {'account_id': account_id, 'tenant_id': tenant_id}
        )
        
        db.session.commit()
        
        flash(f'✅ Account "{account_name}" deleted successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error deleting account: {str(e)}', 'error')
    
    return redirect(url_for('accounts.list_accounts'))


@accounts_bp.route('/statement/<int:account_id>', methods=['GET'])
@require_tenant
@login_required
def account_statement(account_id):
    """View account statement/ledger"""
    tenant_id = get_current_tenant_id()
    
    # Get account details
    account = db.session.execute(text("""
        SELECT 
            id, account_name, account_type, bank_name, account_number,
            opening_balance, current_balance, is_active
        FROM bank_accounts
        WHERE id = :account_id AND tenant_id = :tenant_id
    """), {'account_id': account_id, 'tenant_id': tenant_id}).fetchone()
    
    if not account:
        flash('❌ Account not found', 'error')
        return redirect(url_for('accounts.list_accounts'))
    
    # Get date filters
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')
    
    # Build query
    query = """
        SELECT 
            transaction_date, transaction_type, debit_amount, credit_amount,
            balance_after, narration, voucher_number, reference_type, reference_id
        FROM account_transactions
        WHERE account_id = ? AND tenant_id = ?
    """
    params = [account_id, tenant_id]
    
    if from_date:
        query += " AND transaction_date >= ?"
        params.append(from_date)
    
    if to_date:
        query += " AND transaction_date <= ?"
        params.append(to_date)
    
    query += " ORDER BY transaction_date DESC, id DESC"
    
    transactions = db.session.execute(query, params).fetchall()
    
    # Calculate summary
    total_debit = sum(txn[2] for txn in transactions)
    total_credit = sum(txn[3] for txn in transactions)
    
    return render_template('admin/accounts/statement.html',
                         account=account,
                         transactions=transactions,
                         total_debit=total_debit,
                         total_credit=total_credit,
                         from_date=from_date,
                         to_date=to_date,
                         tenant=g.tenant)


@accounts_bp.route('/get/<int:account_id>', methods=['GET'])
@require_tenant
@login_required
def get_account(account_id):
    """Get account details (AJAX for modal edit)"""
    tenant_id = get_current_tenant_id()
    
    account = db.session.execute(text("""
        SELECT 
            id, account_name, account_type, bank_name, account_number,
            ifsc_code, branch, current_balance, is_active, is_default, description
        FROM bank_accounts
        WHERE id = :account_id AND tenant_id = :tenant_id
    """), {'account_id': account_id, 'tenant_id': tenant_id}).fetchone()
    
    if not account:
        return jsonify({'error': 'Account not found'}), 404
    
    return jsonify({
        'id': account[0],
        'account_name': account[1],
        'account_type': account[2],
        'bank_name': account[3] or '',
        'account_number': account[4] or '',
        'ifsc_code': account[5] or '',
        'branch': account[6] or '',
        'current_balance': float(account[7]),
        'is_active': account[8],
        'is_default': account[9],
        'description': account[10] or ''
    })


# ============================================================
# CONTRA VOUCHERS (PHASE 2) - Fund Transfers
# ============================================================

@accounts_bp.route('/contra', methods=['GET'])
@require_tenant
@login_required
def contra_list():
    """List all contra vouchers (fund transfers)"""
    tenant_id = get_current_tenant_id()
    
    # Get all active accounts for dropdowns
    accounts = db.session.execute(text("""
        SELECT id, account_name, account_type, current_balance
        FROM bank_accounts
        WHERE tenant_id = :tenant_id AND is_active = TRUE
        ORDER BY account_type, account_name
    """), {'tenant_id': tenant_id}).fetchall()
    
    # Get date filters
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')
    
    # Build query for contra transactions
    query = """
        SELECT 
            t.transaction_date,
            t.voucher_number,
            t.narration,
            t.debit_amount,
            t.credit_amount,
            t.id,
            ba.account_name,
            ba.account_type
        FROM account_transactions t
        JOIN bank_accounts ba ON t.account_id = ba.id
        WHERE t.tenant_id = :tenant_id 
        AND t.transaction_type = 'contra'
    """
    params = {'tenant_id': tenant_id}
    
    if from_date:
        query += " AND t.transaction_date >= :from_date"
        params['from_date'] = from_date
    if to_date:
        query += " AND t.transaction_date <= :to_date"
        params['to_date'] = to_date
    
    query += " ORDER BY t.transaction_date DESC, t.voucher_number DESC"
    
    transactions = db.session.execute(text(query), params).fetchall()
    
    # Group by voucher number (each contra has 2 transactions)
    contras = {}
    for txn in transactions:
        voucher_no = txn[1]
        if voucher_no not in contras:
            contras[voucher_no] = {
                'date': txn[0],
                'voucher_number': voucher_no,
                'narration': txn[2],
                'amount': 0,
                'from_account': None,
                'to_account': None
            }
        
        # Credit transaction = money leaving (FROM account)
        if txn[4] > 0:  # credit_amount
            contras[voucher_no]['from_account'] = txn[6]  # account_name
            contras[voucher_no]['amount'] = float(txn[4])
        # Debit transaction = money entering (TO account)
        else:  # debit_amount
            contras[voucher_no]['to_account'] = txn[6]  # account_name
            if contras[voucher_no]['amount'] == 0:
                contras[voucher_no]['amount'] = float(txn[3])
    
    contra_list = list(contras.values())
    
    return render_template('admin/accounts/contra_list.html',
                         accounts=accounts,
                         contras=contra_list,
                         from_date=from_date,
                         to_date=to_date,
                         tenant=g.tenant)


@accounts_bp.route('/contra/create', methods=['POST'])
@require_tenant
@login_required
def contra_create():
    """Create new contra voucher (fund transfer)"""
    tenant_id = get_current_tenant_id()
    
    try:
        # Get form data
        from_account_id = int(request.form.get('from_account_id'))
        to_account_id = int(request.form.get('to_account_id'))
        amount = Decimal(request.form.get('amount'))
        transaction_date = request.form.get('transaction_date')
        narration = request.form.get('narration', '').strip()
        
        # Validation
        if from_account_id == to_account_id:
            flash('❌ Cannot transfer to the same account!', 'error')
            return redirect(url_for('accounts.contra_list'))
        
        if amount <= 0:
            flash('❌ Amount must be greater than zero!', 'error')
            return redirect(url_for('accounts.contra_list'))
        
        # Get FROM account details and check balance
        from_account = db.session.execute(text("""
            SELECT account_name, current_balance 
            FROM bank_accounts 
            WHERE id = :account_id AND tenant_id = :tenant_id AND is_active = TRUE
        """), {'account_id': from_account_id, 'tenant_id': tenant_id}).fetchone()
        
        if not from_account:
            flash('❌ Invalid FROM account!', 'error')
            return redirect(url_for('accounts.contra_list'))
        
        if Decimal(str(from_account[1])) < amount:
            flash(f'❌ Insufficient balance in {from_account[0]}! Available: ₹{from_account[1]:,.2f}', 'error')
            return redirect(url_for('accounts.contra_list'))
        
        # Get TO account details
        to_account = db.session.execute(text("""
            SELECT account_name, current_balance 
            FROM bank_accounts 
            WHERE id = :account_id AND tenant_id = :tenant_id AND is_active = TRUE
        """), {'account_id': to_account_id, 'tenant_id': tenant_id}).fetchone()
        
        if not to_account:
            flash('❌ Invalid TO account!', 'error')
            return redirect(url_for('accounts.contra_list'))
        
        # Generate voucher number
        last_voucher = db.session.execute(text("""
            SELECT voucher_number FROM account_transactions
            WHERE tenant_id = :tenant_id AND transaction_type = 'contra'
            AND voucher_number LIKE 'CONTRA-%'
            ORDER BY id DESC LIMIT 1
        """), {'tenant_id': tenant_id}).fetchone()
        
        if last_voucher and last_voucher[0]:
            last_num = int(last_voucher[0].split('-')[1])
            voucher_number = f'CONTRA-{last_num + 1:04d}'
        else:
            voucher_number = 'CONTRA-0001'
        
        ist = pytz.timezone('Asia/Kolkata')
        now = datetime.now(ist)
        
        # Parse transaction date
        if transaction_date:
            from datetime import datetime as dt
            txn_date = dt.strptime(transaction_date, '%Y-%m-%d').date()
        else:
            txn_date = now.date()
        
        # Calculate new balances
        new_from_balance = Decimal(str(from_account[1])) - amount
        new_to_balance = Decimal(str(to_account[1])) + amount
        
        # Transaction 1: Credit FROM account (money leaving)
        db.session.execute(text("""
            INSERT INTO account_transactions
            (tenant_id, account_id, transaction_date, transaction_type,
             debit_amount, credit_amount, balance_after, reference_type,
             voucher_number, narration, created_at)
            VALUES (:tenant_id, :account_id, :transaction_date, :transaction_type,
                    :debit_amount, :credit_amount, :balance_after, :reference_type,
                    :voucher_number, :narration, :created_at)
        """), {
            'tenant_id': tenant_id, 'account_id': from_account_id, 'transaction_date': txn_date,
            'transaction_type': 'contra', 'debit_amount': 0.00, 'credit_amount': amount,
            'balance_after': new_from_balance, 'reference_type': 'contra',
            'voucher_number': voucher_number, 
            'narration': narration or f'Transfer to {to_account[0]}',
            'created_at': now
        })
        
        # Update FROM account balance
        db.session.execute(text("""
            UPDATE bank_accounts 
            SET current_balance = :new_balance, updated_at = :updated_at
            WHERE id = :account_id AND tenant_id = :tenant_id
        """), {
            'new_balance': new_from_balance, 'updated_at': now,
            'account_id': from_account_id, 'tenant_id': tenant_id
        })
        
        # Transaction 2: Debit TO account (money entering)
        db.session.execute(text("""
            INSERT INTO account_transactions
            (tenant_id, account_id, transaction_date, transaction_type,
             debit_amount, credit_amount, balance_after, reference_type,
             voucher_number, narration, created_at)
            VALUES (:tenant_id, :account_id, :transaction_date, :transaction_type,
                    :debit_amount, :credit_amount, :balance_after, :reference_type,
                    :voucher_number, :narration, :created_at)
        """), {
            'tenant_id': tenant_id, 'account_id': to_account_id, 'transaction_date': txn_date,
            'transaction_type': 'contra', 'debit_amount': amount, 'credit_amount': 0.00,
            'balance_after': new_to_balance, 'reference_type': 'contra',
            'voucher_number': voucher_number,
            'narration': narration or f'Transfer from {from_account[0]}',
            'created_at': now
        })
        
        # Update TO account balance
        db.session.execute(text("""
            UPDATE bank_accounts 
            SET current_balance = :new_balance, updated_at = :updated_at
            WHERE id = :account_id AND tenant_id = :tenant_id
        """), {
            'new_balance': new_to_balance, 'updated_at': now,
            'account_id': to_account_id, 'tenant_id': tenant_id
        })
        
        db.session.commit()
        
        flash(f'✅ Contra voucher {voucher_number} created! ₹{amount:,.2f} transferred from {from_account[0]} to {to_account[0]}', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error creating contra voucher: {str(e)}', 'error')
    
    return redirect(url_for('accounts.contra_list'))


# ============================================================
# EMPLOYEE CASH (PHASE 3) - Cash Advances to Employees
# ============================================================

@accounts_bp.route('/employee-cash', methods=['GET'])
@require_tenant
@login_required
def employee_cash_list():
    """List all employees with their cash balances"""
    tenant_id = get_current_tenant_id()
    
    # Get all active employees
    from models import Employee
    employees = Employee.query.filter_by(tenant_id=tenant_id, active=True).all()
    
    # Get all active accounts for dropdown (giving cash from)
    accounts = db.session.execute(text("""
        SELECT id, account_name, account_type, current_balance
        FROM bank_accounts
        WHERE tenant_id = :tenant_id AND is_active = TRUE
        ORDER BY account_type, account_name
    """), {'tenant_id': tenant_id}).fetchall()
    
    # Calculate each employee's cash balance
    employee_balances = []
    for emp in employees:
        # Get total cash given to employee
        cash_given = db.session.execute(text("""
            SELECT COALESCE(SUM(debit_amount), 0)
            FROM account_transactions
            WHERE tenant_id = :tenant_id 
            AND transaction_type = 'employee_advance'
            AND reference_type = 'employee'
            AND reference_id = :employee_id
        """), {'tenant_id': tenant_id, 'employee_id': emp.id}).fetchone()[0]
        
        # Get total expenses made by employee
        expenses_made = db.session.execute(text("""
            SELECT COALESCE(SUM(credit_amount), 0)
            FROM account_transactions
            WHERE tenant_id = :tenant_id 
            AND transaction_type = 'employee_expense'
            AND reference_type = 'employee'
            AND reference_id = :employee_id
        """), {'tenant_id': tenant_id, 'employee_id': emp.id}).fetchone()[0]
        
        # Get cash returned by employee
        cash_returned = db.session.execute(text("""
            SELECT COALESCE(SUM(credit_amount), 0)
            FROM account_transactions
            WHERE tenant_id = :tenant_id 
            AND transaction_type = 'employee_return'
            AND reference_type = 'employee'
            AND reference_id = :employee_id
        """), {'tenant_id': tenant_id, 'employee_id': emp.id}).fetchone()[0]
        
        # Calculate current balance with employee
        current_balance = Decimal(str(cash_given)) - Decimal(str(expenses_made)) - Decimal(str(cash_returned))
        
        employee_balances.append({
            'id': emp.id,
            'name': emp.name,
            'phone': emp.phone,
            'cash_given': float(cash_given),
            'expenses_made': float(expenses_made),
            'cash_returned': float(cash_returned),
            'current_balance': float(current_balance)
        })
    
    # Calculate totals
    total_cash_with_employees = sum(emp['current_balance'] for emp in employee_balances)
    
    return render_template('admin/accounts/employee_cash.html',
                         employees=employee_balances,
                         accounts=accounts,
                         total_cash_with_employees=total_cash_with_employees,
                         tenant=g.tenant)


@accounts_bp.route('/employee-cash/give', methods=['POST'])
@require_tenant
@login_required
def employee_cash_give():
    """Give cash advance to employee"""
    tenant_id = get_current_tenant_id()
    
    try:
        # Get form data
        employee_id = int(request.form.get('employee_id'))
        from_account_id = int(request.form.get('from_account_id'))
        amount = Decimal(request.form.get('amount'))
        transaction_date = request.form.get('transaction_date')
        narration = request.form.get('narration', '').strip()
        
        # Validation
        if amount <= 0:
            flash('❌ Amount must be greater than zero!', 'error')
            return redirect(url_for('accounts.employee_cash_list'))
        
        # Get employee details
        from models import Employee
        employee = Employee.query.filter_by(id=employee_id, tenant_id=tenant_id, active=True).first()
        if not employee:
            flash('❌ Invalid employee!', 'error')
            return redirect(url_for('accounts.employee_cash_list'))
        
        # Get FROM account details and check balance
        from_account = db.session.execute(text("""
            SELECT account_name, current_balance 
            FROM bank_accounts 
            WHERE id = :account_id AND tenant_id = :tenant_id AND is_active = TRUE
        """), {'account_id': from_account_id, 'tenant_id': tenant_id}).fetchone()
        
        if not from_account:
            flash('❌ Invalid account!', 'error')
            return redirect(url_for('accounts.employee_cash_list'))
        
        if Decimal(str(from_account[1])) < amount:
            flash(f'❌ Insufficient balance in {from_account[0]}! Available: ₹{from_account[1]:,.2f}', 'error')
            return redirect(url_for('accounts.employee_cash_list'))
        
        # Generate voucher number
        last_voucher = db.session.execute(text("""
            SELECT voucher_number FROM account_transactions
            WHERE tenant_id = :tenant_id AND transaction_type = 'employee_advance'
            AND voucher_number LIKE 'EMP-ADV-%'
            ORDER BY id DESC LIMIT 1
        """), {'tenant_id': tenant_id}).fetchone()
        
        if last_voucher and last_voucher[0]:
            last_num = int(last_voucher[0].split('-')[2])
            voucher_number = f'EMP-ADV-{last_num + 1:04d}'
        else:
            voucher_number = 'EMP-ADV-0001'
        
        ist = pytz.timezone('Asia/Kolkata')
        now = datetime.now(ist)
        
        # Parse transaction date
        if transaction_date:
            from datetime import datetime as dt
            txn_date = dt.strptime(transaction_date, '%Y-%m-%d').date()
        else:
            txn_date = now.date()
        
        # Calculate new balance
        new_account_balance = Decimal(str(from_account[1])) - amount
        
        # Transaction 1: Credit FROM account (money leaving)
        db.session.execute(text("""
            INSERT INTO account_transactions
            (tenant_id, account_id, transaction_date, transaction_type,
             debit_amount, credit_amount, balance_after, reference_type, reference_id,
             voucher_number, narration, created_at)
            VALUES (:tenant_id, :account_id, :transaction_date, :transaction_type,
                    :debit_amount, :credit_amount, :balance_after, :reference_type, :reference_id,
                    :voucher_number, :narration, :created_at)
        """), {
            'tenant_id': tenant_id, 'account_id': from_account_id, 'transaction_date': txn_date,
            'transaction_type': 'employee_advance', 'debit_amount': 0.00, 'credit_amount': amount,
            'balance_after': new_account_balance, 'reference_type': 'employee', 'reference_id': employee_id,
            'voucher_number': voucher_number,
            'narration': narration or f'Cash advance to {employee.name}',
            'created_at': now
        })
        
        # Update FROM account balance
        db.session.execute(text("""
            UPDATE bank_accounts 
            SET current_balance = :new_balance, updated_at = :updated_at
            WHERE id = :account_id AND tenant_id = :tenant_id
        """), {
            'new_balance': new_account_balance, 'updated_at': now,
            'account_id': from_account_id, 'tenant_id': tenant_id
        })
        
        # Transaction 2: Track employee received cash (debit - employee now has cash)
        db.session.execute(text("""
            INSERT INTO account_transactions
            (tenant_id, account_id, transaction_date, transaction_type,
             debit_amount, credit_amount, balance_after, reference_type, reference_id,
             voucher_number, narration, created_at)
            VALUES (:tenant_id, :account_id, :transaction_date, :transaction_type,
                    :debit_amount, :credit_amount, :balance_after, :reference_type, :reference_id,
                    :voucher_number, :narration, :created_at)
        """), {
            'tenant_id': tenant_id, 'account_id': from_account_id, 'transaction_date': txn_date,
            'transaction_type': 'employee_advance', 'debit_amount': amount, 'credit_amount': 0.00,
            'balance_after': amount, 'reference_type': 'employee', 'reference_id': employee_id,
            'voucher_number': voucher_number,
            'narration': narration or f'Cash advance received from {from_account[0]}',
            'created_at': now
        })
        
        db.session.commit()
        
        flash(f'✅ Cash advance {voucher_number} created! ₹{amount:,.2f} given to {employee.name}', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error giving cash advance: {str(e)}', 'error')
    
    return redirect(url_for('accounts.employee_cash_list'))


@accounts_bp.route('/employee-cash/expense', methods=['POST'])
@require_tenant
@login_required
def employee_cash_expense():
    """Record expense made by employee"""
    tenant_id = get_current_tenant_id()
    
    try:
        # Get form data
        employee_id = int(request.form.get('employee_id'))
        amount = Decimal(request.form.get('amount'))
        expense_head = request.form.get('expense_head', '').strip()
        transaction_date = request.form.get('transaction_date')
        narration = request.form.get('narration', '').strip()
        
        # Validation
        if amount <= 0:
            flash('❌ Amount must be greater than zero!', 'error')
            return redirect(url_for('accounts.employee_cash_list'))
        
        # Get employee details
        from models import Employee
        employee = Employee.query.filter_by(id=employee_id, tenant_id=tenant_id, active=True).first()
        if not employee:
            flash('❌ Invalid employee!', 'error')
            return redirect(url_for('accounts.employee_cash_list'))
        
        # Check employee has sufficient cash
        cash_given = db.session.execute(text("""
            SELECT COALESCE(SUM(debit_amount), 0)
            FROM account_transactions
            WHERE tenant_id = :tenant_id 
            AND transaction_type = 'employee_advance'
            AND reference_type = 'employee'
            AND reference_id = :employee_id
        """), {'tenant_id': tenant_id, 'employee_id': employee_id}).fetchone()[0]
        
        expenses_made = db.session.execute(text("""
            SELECT COALESCE(SUM(credit_amount), 0)
            FROM account_transactions
            WHERE tenant_id = :tenant_id 
            AND transaction_type = 'employee_expense'
            AND reference_type = 'employee'
            AND reference_id = :employee_id
        """), {'tenant_id': tenant_id, 'employee_id': employee_id}).fetchone()[0]
        
        cash_returned = db.session.execute(text("""
            SELECT COALESCE(SUM(credit_amount), 0)
            FROM account_transactions
            WHERE tenant_id = :tenant_id 
            AND transaction_type = 'employee_return'
            AND reference_type = 'employee'
            AND reference_id = :employee_id
        """), {'tenant_id': tenant_id, 'employee_id': employee_id}).fetchone()[0]
        
        available_cash = Decimal(str(cash_given)) - Decimal(str(expenses_made)) - Decimal(str(cash_returned))
        
        if available_cash < amount:
            flash(f'❌ Insufficient cash with {employee.name}! Available: ₹{available_cash:,.2f}', 'error')
            return redirect(url_for('accounts.employee_cash_list'))
        
        ist = pytz.timezone('Asia/Kolkata')
        now = datetime.now(ist)
        
        # Parse transaction date
        if transaction_date:
            from datetime import datetime as dt
            txn_date = dt.strptime(transaction_date, '%Y-%m-%d').date()
        else:
            txn_date = now.date()
        
        # Calculate new balance
        new_balance = available_cash - amount
        
        # Create expense transaction (credit - employee spent cash)
        db.session.execute(text("""
            INSERT INTO account_transactions
            (tenant_id, account_id, transaction_date, transaction_type,
             debit_amount, credit_amount, balance_after, reference_type, reference_id,
             voucher_number, narration, created_at)
            VALUES (:tenant_id, :account_id, :transaction_date, :transaction_type,
                    :debit_amount, :credit_amount, :balance_after, :reference_type, :reference_id,
                    :voucher_number, :narration, :created_at)
        """), {
            'tenant_id': tenant_id, 'account_id': 0, 'transaction_date': txn_date,
            'transaction_type': 'employee_expense', 'debit_amount': 0.00, 'credit_amount': amount,
            'balance_after': new_balance, 'reference_type': 'employee', 'reference_id': employee_id,
            'voucher_number': expense_head or 'Expense',
            'narration': narration or f'{expense_head} by {employee.name}',
            'created_at': now
        })
        
        db.session.commit()
        
        flash(f'✅ Expense recorded! ₹{amount:,.2f} spent by {employee.name} on {expense_head}', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error recording expense: {str(e)}', 'error')
    
    return redirect(url_for('accounts.employee_cash_list'))


@accounts_bp.route('/employee-cash/ledger/<int:employee_id>', methods=['GET'])
@require_tenant
@login_required
def employee_cash_ledger(employee_id):
    """View employee cash ledger"""
    tenant_id = get_current_tenant_id()
    
    # Get employee details
    from models import Employee
    employee = Employee.query.filter_by(id=employee_id, tenant_id=tenant_id, active=True).first_or_404()
    
    # Get all transactions for this employee
    transactions = db.session.execute(text("""
        SELECT 
            transaction_date,
            transaction_type,
            debit_amount,
            credit_amount,
            balance_after,
            voucher_number,
            narration,
            created_at
        FROM account_transactions
        WHERE tenant_id = :tenant_id 
        AND reference_type = 'employee'
        AND reference_id = :employee_id
        ORDER BY transaction_date DESC, created_at DESC
    """), {'tenant_id': tenant_id, 'employee_id': employee_id}).fetchall()
    
    # Calculate totals
    total_received = sum(txn[2] for txn in transactions if txn[1] == 'employee_advance')
    total_spent = sum(txn[3] for txn in transactions if txn[1] == 'employee_expense')
    total_returned = sum(txn[3] for txn in transactions if txn[1] == 'employee_return')
    current_balance = Decimal(str(total_received)) - Decimal(str(total_spent)) - Decimal(str(total_returned))
    
    return render_template('admin/accounts/employee_ledger.html',
                         employee=employee,
                         transactions=transactions,
                         total_received=float(total_received),
                         total_spent=float(total_spent),
                         total_returned=float(total_returned),
                         current_balance=float(current_balance),
                         tenant=g.tenant)

