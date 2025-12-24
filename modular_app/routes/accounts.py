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

@accounts_bp.route('/', methods=['GET'], strict_slashes=False)  # PERFORMANCE: Prevent 308 redirects
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
        
        # ==========================================
        # AUTOMATIC DOUBLE-ENTRY FOR OPENING BALANCE
        # ==========================================
        # Enterprise Solution: NO manual migration needed!
        # When opening balance is set, BOTH entries are created automatically
        
        if opening_balance > 0:
            # Entry 1: DEBIT to the new account (Asset)
            db.session.execute(text("""
                INSERT INTO account_transactions
                (tenant_id, account_id, transaction_date, transaction_type,
                 debit_amount, credit_amount, balance_after, narration, created_at, created_by)
                VALUES (:tenant_id, :account_id, :transaction_date, :transaction_type,
                        :debit_amount, :credit_amount, :balance_after, :narration, :created_at, :created_by)
            """), {
                'tenant_id': tenant_id, 'account_id': account_id, 'transaction_date': now.date(),
                'transaction_type': 'opening_balance', 'debit_amount': opening_balance,
                'credit_amount': 0.00, 'balance_after': opening_balance,
                'narration': f'Opening balance - {account_name}', 'created_at': now,
                'created_by': None
            })
            
            # Entry 2: CREDIT to Opening Balance - Equity (balancing entry)
            # Uses account_id = NULL to represent Owner's Equity (virtual account)
            db.session.execute(text("""
                INSERT INTO account_transactions
                (tenant_id, account_id, transaction_date, transaction_type,
                 debit_amount, credit_amount, balance_after, reference_type, reference_id,
                 voucher_number, narration, created_at, created_by)
                VALUES (:tenant_id, NULL, :transaction_date, :transaction_type,
                        :debit_amount, :credit_amount, :balance_after, :reference_type, :reference_id,
                        :voucher_number, :narration, :created_at, :created_by)
            """), {
                'tenant_id': tenant_id, 'transaction_date': now.date(),
                'transaction_type': 'opening_balance_equity', 'debit_amount': 0.00,
                'credit_amount': opening_balance, 'balance_after': opening_balance,
                'reference_type': 'bank_account', 'reference_id': account_id,
                'voucher_number': f'OB-{account_id}',
                'narration': f'Opening balance equity - {account_name}', 'created_at': now,
                'created_by': None
            })
            
            print(f"✅ Created double-entry for opening balance: ₹{opening_balance:,.2f}")
            print(f"   Debit: {account_name} (Account #{account_id})")
            print(f"   Credit: Opening Balance - Equity")
        
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
    
    # Build query with named parameters
    # EXCLUDE 'opening_balance' type - that's shown separately from bank_accounts table
    query = """
        SELECT 
            transaction_date, transaction_type, debit_amount, credit_amount,
            balance_after, narration, voucher_number, reference_type, reference_id
        FROM account_transactions
        WHERE account_id = :account_id 
        AND tenant_id = :tenant_id
        AND transaction_type != 'opening_balance'
    """
    params = {'account_id': account_id, 'tenant_id': tenant_id}
    
    if from_date:
        query += " AND transaction_date >= :from_date"
        params['from_date'] = from_date
    
    if to_date:
        query += " AND transaction_date <= :to_date"
        params['to_date'] = to_date
    
    query += " ORDER BY transaction_date DESC, id DESC"
    
    transactions = db.session.execute(text(query), params).fetchall()
    
    # Calculate summary (Current Period only - no opening balance)
    total_debit = sum(txn[2] for txn in transactions)
    total_credit = sum(txn[3] for txn in transactions)
    
    # Closing Balance = Opening Balance + Total Debit - Total Credit
    closing_balance = float(account[5]) + float(total_debit) - float(total_credit)
    
    return render_template('admin/accounts/statement.html',
                         account=account,
                         transactions=transactions,
                         total_debit=total_debit,
                         total_credit=total_credit,
                         closing_balance=closing_balance,
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
        
        # Transaction 1: Credit FROM account (money leaving company)
        # This appears in company's bank/cash ledger, NOT in employee ledger
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
            'balance_after': new_account_balance, 'reference_type': 'employee_advance_given', 
            'reference_id': employee_id,
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
        # This appears ONLY in employee ledger
        db.session.execute(text("""
            INSERT INTO account_transactions
            (tenant_id, account_id, transaction_date, transaction_type,
             debit_amount, credit_amount, balance_after, reference_type, reference_id,
             voucher_number, narration, created_at)
            VALUES (:tenant_id, :account_id, :transaction_date, :transaction_type,
                    :debit_amount, :credit_amount, :balance_after, :reference_type, :reference_id,
                    :voucher_number, :narration, :created_at)
        """), {
            'tenant_id': tenant_id, 'account_id': None, 'transaction_date': txn_date,
            'transaction_type': 'employee_advance', 'debit_amount': amount, 'credit_amount': 0.00,
            'balance_after': amount, 'reference_type': 'employee', 'reference_id': employee_id,
            'voucher_number': voucher_number,
            'narration': narration or f'Cash advance received',
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
        
        # Generate voucher number for employee expense
        # Get the last expense voucher number for this tenant
        last_voucher = db.session.execute(text("""
            SELECT voucher_number
            FROM account_transactions
            WHERE tenant_id = :tenant_id 
            AND transaction_type = 'employee_expense'
            AND voucher_number LIKE 'EMP-EXP-%'
            ORDER BY id DESC
            LIMIT 1
        """), {'tenant_id': tenant_id}).fetchone()
        
        if last_voucher and last_voucher[0]:
            try:
                last_number = int(last_voucher[0].split('-')[-1])
                next_number = last_number + 1
            except (ValueError, IndexError):
                next_number = 1
        else:
            next_number = 1
        
        voucher_number = f"EMP-EXP-{next_number:04d}"
        
        # Create expense transaction (credit - employee spent cash)
        # Note: account_id is NULL for employee expenses (they don't affect bank/cash accounts)
        db.session.execute(text("""
            INSERT INTO account_transactions
            (tenant_id, account_id, transaction_date, transaction_type,
             debit_amount, credit_amount, balance_after, reference_type, reference_id,
             voucher_number, narration, created_at)
            VALUES (:tenant_id, :account_id, :transaction_date, :transaction_type,
                    :debit_amount, :credit_amount, :balance_after, :reference_type, :reference_id,
                    :voucher_number, :narration, :created_at)
        """), {
            'tenant_id': tenant_id, 'account_id': None, 'transaction_date': txn_date,
            'transaction_type': 'employee_expense', 'debit_amount': 0.00, 'credit_amount': amount,
            'balance_after': new_balance, 'reference_type': 'employee', 'reference_id': employee_id,
            'voucher_number': voucher_number,
            'narration': f'{expense_head}: {narration}' if narration else expense_head or 'Expense',
            'created_at': now
        })
        
        db.session.commit()
        
        flash(f'✅ Expense recorded! ₹{amount:,.2f} spent by {employee.name} on {expense_head}', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error recording expense: {str(e)}', 'error')
    
    return redirect(url_for('accounts.employee_cash_list'))


@accounts_bp.route('/employee-cash/return', methods=['POST'])
@require_tenant
@login_required
def employee_cash_return():
    """Record cash return from employee to company"""
    tenant_id = get_current_tenant_id()
    
    try:
        # Get form data
        employee_id = int(request.form.get('employee_id'))
        amount = Decimal(request.form.get('amount'))
        to_account_id = int(request.form.get('to_account_id'))
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
        
        # Get target account details
        from models import BankAccount
        target_account = BankAccount.query.filter_by(id=to_account_id, tenant_id=tenant_id, is_active=True).first()
        if not target_account:
            flash('❌ Invalid account!', 'error')
            return redirect(url_for('accounts.employee_cash_list'))
        
        # Check employee has sufficient cash to return
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
            flash(f'❌ Employee {employee.name} only has ₹{available_cash:,.2f} available! Cannot return ₹{amount:,.2f}', 'error')
            return redirect(url_for('accounts.employee_cash_list'))
        
        ist = pytz.timezone('Asia/Kolkata')
        now = datetime.now(ist)
        
        # Parse transaction date
        if transaction_date:
            from datetime import datetime as dt
            txn_date = dt.strptime(transaction_date, '%Y-%m-%d').date()
        else:
            txn_date = now.date()
        
        # Calculate new balances
        employee_new_balance = available_cash - amount
        company_new_balance = target_account.current_balance + amount
        
        # Transaction 1: Employee returns cash (credit to employee's virtual account - reduces their balance)
        voucher_number = f'RET-{employee_id}-{int(now.timestamp())}'
        
        db.session.execute(text("""
            INSERT INTO account_transactions
            (tenant_id, account_id, transaction_date, transaction_type,
             debit_amount, credit_amount, balance_after, reference_type, reference_id,
             voucher_number, narration, created_at)
            VALUES (:tenant_id, :account_id, :transaction_date, :transaction_type,
                    :debit_amount, :credit_amount, :balance_after, :reference_type, :reference_id,
                    :voucher_number, :narration, :created_at)
        """), {
            'tenant_id': tenant_id, 'account_id': None, 'transaction_date': txn_date,
            'transaction_type': 'employee_return', 'debit_amount': Decimal('0.00'), 'credit_amount': amount,
            'balance_after': employee_new_balance, 'reference_type': 'employee', 'reference_id': employee_id,
            'voucher_number': voucher_number,
            'narration': narration or f'Cash returned by {employee.name} to {target_account.account_name}',
            'created_at': now
        })
        
        # Transaction 2: Company receives cash (debit to company account - increases company balance)
        db.session.execute(text("""
            UPDATE bank_accounts 
            SET current_balance = :new_balance, updated_at = :updated_at
            WHERE id = :account_id AND tenant_id = :tenant_id
        """), {
            'new_balance': company_new_balance, 'updated_at': now,
            'account_id': target_account.id, 'tenant_id': tenant_id
        })
        
        db.session.execute(text("""
            INSERT INTO account_transactions
            (tenant_id, account_id, transaction_date, transaction_type,
             debit_amount, credit_amount, balance_after, reference_type, reference_id,
             voucher_number, narration, created_at)
            VALUES (:tenant_id, :account_id, :transaction_date, :transaction_type,
                    :debit_amount, :credit_amount, :balance_after, :reference_type, :reference_id,
                    :voucher_number, :narration, :created_at)
        """), {
            'tenant_id': tenant_id, 'account_id': target_account.id, 'transaction_date': txn_date,
            'transaction_type': 'employee_return', 'debit_amount': amount, 'credit_amount': Decimal('0.00'),
            'balance_after': company_new_balance, 'reference_type': 'employee_return_received', 'reference_id': employee_id,
            'voucher_number': voucher_number,
            'narration': narration or f'Cash returned by {employee.name}',
            'created_at': now
        })
        
        db.session.commit()
        
        flash(f'✅ Cash returned! ₹{amount:,.2f} received from {employee.name} → {target_account.account_name}', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error recording cash return: {str(e)}', 'error')
    
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


# ===========================
# PHASE 5: ACCOUNTING REPORTS
# ===========================

@accounts_bp.route('/reports/cash-book', methods=['GET'])
@require_tenant
@login_required
def cash_book():
    """Cash Book Report - All cash account transactions"""
    tenant_id = get_current_tenant_id()
    
    # Get date filters
    from datetime import datetime, timedelta
    ist = pytz.timezone('Asia/Kolkata')
    today = datetime.now(ist).date()
    
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    
    if start_date_str:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
    else:
        start_date = today - timedelta(days=30)  # Default: Last 30 days
    
    if end_date_str:
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
    else:
        end_date = today
    
    # Get all cash accounts
    cash_accounts = db.session.execute(text("""
        SELECT id, account_name, opening_balance, current_balance
        FROM bank_accounts
        WHERE tenant_id = :tenant_id 
        AND account_type = 'cash'
        AND is_active = TRUE
        ORDER BY account_name
    """), {'tenant_id': tenant_id}).fetchall()
    
    if not cash_accounts:
        return render_template('admin/accounts/reports/cash_book.html',
                             transactions=[],
                             opening_balance=0,
                             closing_balance=0,
                             total_receipts=0,
                             total_payments=0,
                             start_date=start_date,
                             end_date=end_date,
                             tenant=g.tenant)
    
    # For simplicity, show first cash account (usually "Cash in Hand")
    cash_account = cash_accounts[0]
    account_id = cash_account[0]
    account_name = cash_account[1]
    
    # Calculate opening balance (balance at start_date)
    opening_balance_result = db.session.execute(text("""
        SELECT balance_after
        FROM account_transactions
        WHERE tenant_id = :tenant_id 
        AND account_id = :account_id
        AND transaction_date < :start_date
        ORDER BY transaction_date DESC, created_at DESC
        LIMIT 1
    """), {'tenant_id': tenant_id, 'account_id': account_id, 'start_date': start_date}).fetchone()
    
    opening_balance = Decimal(str(opening_balance_result[0])) if opening_balance_result else Decimal(str(cash_account[2]))
    
    # Get all transactions for date range
    transactions = db.session.execute(text("""
        SELECT 
            transaction_date,
            transaction_type,
            debit_amount,
            credit_amount,
            balance_after,
            voucher_number,
            narration,
            reference_type,
            reference_id
        FROM account_transactions
        WHERE tenant_id = :tenant_id 
        AND account_id = :account_id
        AND transaction_date BETWEEN :start_date AND :end_date
        ORDER BY transaction_date ASC, created_at ASC
    """), {'tenant_id': tenant_id, 'account_id': account_id, 'start_date': start_date, 'end_date': end_date}).fetchall()
    
    # Calculate totals
    total_receipts = sum(Decimal(str(txn[2])) for txn in transactions)  # Sum of debits
    total_payments = sum(Decimal(str(txn[3])) for txn in transactions)  # Sum of credits
    
    # Calculate closing balance
    # If end_date is today or later, use actual current_balance from bank_accounts
    # Otherwise, use the balance_after from last transaction in period
    if end_date >= today:
        closing_balance = Decimal(str(cash_account[3]))  # current_balance
    elif transactions:
        closing_balance = Decimal(str(transactions[-1][4]))  # balance_after of last transaction
    else:
        closing_balance = opening_balance
    
    return render_template('admin/accounts/reports/cash_book.html',
                         transactions=transactions,
                         account_name=account_name,
                         opening_balance=float(opening_balance),
                         closing_balance=float(closing_balance),
                         total_receipts=float(total_receipts),
                         total_payments=float(total_payments),
                         start_date=start_date,
                         end_date=end_date,
                         tenant=g.tenant)


@accounts_bp.route('/reports/bank-book', methods=['GET'])
@require_tenant
@login_required
def bank_book():
    """Bank Book Report - Bank account-wise transactions"""
    tenant_id = get_current_tenant_id()
    
    # Get date filters
    from datetime import datetime, timedelta
    ist = pytz.timezone('Asia/Kolkata')
    today = datetime.now(ist).date()
    
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    account_id_str = request.args.get('account_id')
    
    if start_date_str:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
    else:
        start_date = today - timedelta(days=30)
    
    if end_date_str:
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
    else:
        end_date = today
    
    # Get all bank accounts
    bank_accounts = db.session.execute(text("""
        SELECT id, account_name, bank_name, account_number, opening_balance, current_balance
        FROM bank_accounts
        WHERE tenant_id = :tenant_id 
        AND account_type = 'bank'
        AND is_active = TRUE
        ORDER BY account_name
    """), {'tenant_id': tenant_id}).fetchall()
    
    if not bank_accounts:
        return render_template('admin/accounts/reports/bank_book.html',
                             transactions=[],
                             bank_accounts=[],
                             selected_account=None,
                             opening_balance=0,
                             closing_balance=0,
                             total_deposits=0,
                             total_withdrawals=0,
                             start_date=start_date,
                             end_date=end_date,
                             tenant=g.tenant)
    
    # Select account (default to first if not specified)
    if account_id_str:
        account_id = int(account_id_str)
        selected_account = next((acc for acc in bank_accounts if acc[0] == account_id), bank_accounts[0])
    else:
        selected_account = bank_accounts[0]
        account_id = selected_account[0]
    
    account_name = selected_account[1]
    
    # Calculate opening balance
    opening_balance_result = db.session.execute(text("""
        SELECT balance_after
        FROM account_transactions
        WHERE tenant_id = :tenant_id 
        AND account_id = :account_id
        AND transaction_date < :start_date
        ORDER BY transaction_date DESC, created_at DESC
        LIMIT 1
    """), {'tenant_id': tenant_id, 'account_id': account_id, 'start_date': start_date}).fetchone()
    
    opening_balance = Decimal(str(opening_balance_result[0])) if opening_balance_result else Decimal(str(selected_account[4]))
    
    # Get transactions
    transactions = db.session.execute(text("""
        SELECT 
            transaction_date,
            transaction_type,
            debit_amount,
            credit_amount,
            balance_after,
            voucher_number,
            narration,
            reference_type,
            reference_id
        FROM account_transactions
        WHERE tenant_id = :tenant_id 
        AND account_id = :account_id
        AND transaction_date BETWEEN :start_date AND :end_date
        ORDER BY transaction_date ASC, created_at ASC
    """), {'tenant_id': tenant_id, 'account_id': account_id, 'start_date': start_date, 'end_date': end_date}).fetchall()
    
    # Calculate totals
    total_deposits = sum(Decimal(str(txn[2])) for txn in transactions)
    total_withdrawals = sum(Decimal(str(txn[3])) for txn in transactions)
    
    # Calculate closing balance
    # If end_date is today or later, use actual current_balance from bank_accounts
    # Otherwise, use the balance_after from last transaction in period
    if end_date >= today:
        closing_balance = Decimal(str(selected_account[5]))  # current_balance
    elif transactions:
        closing_balance = Decimal(str(transactions[-1][4]))  # balance_after of last transaction
    else:
        closing_balance = opening_balance
    
    return render_template('admin/accounts/reports/bank_book.html',
                         transactions=transactions,
                         bank_accounts=bank_accounts,
                         selected_account=selected_account,
                         account_name=account_name,
                         opening_balance=float(opening_balance),
                         closing_balance=float(closing_balance),
                         total_deposits=float(total_deposits),
                         total_withdrawals=float(total_withdrawals),
                         start_date=start_date,
                         end_date=end_date,
                         tenant=g.tenant)


@accounts_bp.route('/reports/day-book', methods=['GET'])
@require_tenant
@login_required
def day_book():
    """Day Book Report - All transactions for a date range"""
    tenant_id = get_current_tenant_id()
    
    # Get date filters
    from datetime import datetime, timedelta
    ist = pytz.timezone('Asia/Kolkata')
    today = datetime.now(ist).date()
    
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    
    if start_date_str:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
    else:
        start_date = today
    
    if end_date_str:
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
    else:
        end_date = today
    
    # Get all transactions for date range (all accounts)
    transactions = db.session.execute(text("""
        SELECT 
            at.transaction_date,
            at.transaction_type,
            at.debit_amount,
            at.credit_amount,
            at.voucher_number,
            at.narration,
            at.reference_type,
            at.reference_id,
            ba.account_name,
            ba.account_type
        FROM account_transactions at
        LEFT JOIN bank_accounts ba ON at.account_id = ba.id AND at.tenant_id = ba.tenant_id
        WHERE at.tenant_id = :tenant_id 
        AND at.transaction_date BETWEEN :start_date AND :end_date
        ORDER BY at.transaction_date ASC, at.created_at ASC
    """), {'tenant_id': tenant_id, 'start_date': start_date, 'end_date': end_date}).fetchall()
    
    # Calculate totals
    total_debits = sum(Decimal(str(txn[2])) for txn in transactions)
    total_credits = sum(Decimal(str(txn[3])) for txn in transactions)
    
    # Group by transaction type
    from collections import defaultdict
    grouped_transactions = defaultdict(list)
    for txn in transactions:
        grouped_transactions[txn[1]].append(txn)
    
    return render_template('admin/accounts/reports/day_book.html',
                         transactions=transactions,
                         grouped_transactions=dict(grouped_transactions),
                         total_debits=float(total_debits),
                         total_credits=float(total_credits),
                         start_date=start_date,
                         end_date=end_date,
                         tenant=g.tenant)


@accounts_bp.route('/reports/account-summary', methods=['GET'])
@require_tenant
@login_required
def account_summary():
    """Account Summary - Overview of all accounts and balances"""
    tenant_id = get_current_tenant_id()
    
    # Get all accounts with balances
    accounts = db.session.execute(text("""
        SELECT 
            id,
            account_name,
            account_type,
            bank_name,
            account_number,
            opening_balance,
            current_balance,
            is_default
        FROM bank_accounts
        WHERE tenant_id = :tenant_id 
        AND is_active = TRUE
        ORDER BY 
            CASE account_type 
                WHEN 'cash' THEN 1 
                WHEN 'bank' THEN 2 
                WHEN 'petty_cash' THEN 3 
            END,
            account_name
    """), {'tenant_id': tenant_id}).fetchall()
    
    # Calculate category-wise totals
    cash_total = sum(Decimal(str(acc[6])) for acc in accounts if acc[2] == 'cash')
    bank_total = sum(Decimal(str(acc[6])) for acc in accounts if acc[2] == 'bank')
    petty_cash_total = sum(Decimal(str(acc[6])) for acc in accounts if acc[2] == 'petty_cash')
    
    # Get employee cash total
    employee_cash_total = db.session.execute(text("""
        SELECT COALESCE(SUM(
            CASE 
                WHEN transaction_type = 'employee_advance' THEN debit_amount
                WHEN transaction_type IN ('employee_expense', 'employee_return') THEN -credit_amount
                ELSE 0
            END
        ), 0) as total
        FROM account_transactions
        WHERE tenant_id = :tenant_id 
        AND reference_type = 'employee'
    """), {'tenant_id': tenant_id}).fetchone()[0]
    
    total_balance = cash_total + bank_total + petty_cash_total
    
    return render_template('admin/accounts/reports/account_summary.html',
                         accounts=accounts,
                         cash_total=float(cash_total),
                         bank_total=float(bank_total),
                         petty_cash_total=float(petty_cash_total),
                         employee_cash_total=float(employee_cash_total or 0),
                         total_balance=float(total_balance),
                         tenant=g.tenant)


@accounts_bp.route('/reports/balance-sheet', methods=['GET'])
@require_tenant
@login_required
def balance_sheet():
    """Balance Sheet - Assets vs. Liabilities as of a specific date"""
    from datetime import datetime
    import pytz
    
    tenant_id = get_current_tenant_id()
    ist = pytz.timezone('Asia/Kolkata')
    
    # Get as_of_date from query params (default: today)
    as_of_date_str = request.args.get('as_of_date')
    if as_of_date_str:
        as_of_date = datetime.strptime(as_of_date_str, '%Y-%m-%d').date()
    else:
        as_of_date = datetime.now(ist).date()
    
    # ====================
    # ASSETS CALCULATION
    # ====================
    
    # 1. Cash & Bank Accounts (Current Assets)
    cash_bank_accounts = db.session.execute(text("""
        SELECT 
            account_name,
            account_type,
            current_balance
        FROM bank_accounts
        WHERE tenant_id = :tenant_id 
        AND is_active = TRUE
        ORDER BY 
            CASE account_type 
                WHEN 'cash' THEN 1 
                WHEN 'bank' THEN 2 
            END,
            account_name
    """), {'tenant_id': tenant_id}).fetchall()
    
    cash_and_bank_total = sum(Decimal(str(acc[2])) for acc in cash_bank_accounts)
    
    # 2. Accounts Receivable (Unpaid Invoices)
    # 🆕 EXCLUDE credit_adjustment invoices (no AR - customer already paid via kaccha bill)
    accounts_receivable = db.session.execute(text("""
        SELECT 
            customer_name,
            SUM(total_amount - COALESCE(paid_amount, 0)) as outstanding
        FROM invoices
        WHERE tenant_id = :tenant_id 
        AND payment_status != 'paid'
        AND invoice_date <= :as_of_date
        AND (invoice_type IS NULL OR invoice_type != 'credit_adjustment')
        GROUP BY customer_name
        ORDER BY outstanding DESC
    """), {'tenant_id': tenant_id, 'as_of_date': as_of_date}).fetchall()
    
    accounts_receivable_total = sum(Decimal(str(acc[1])) for acc in accounts_receivable) if accounts_receivable else Decimal('0')
    
    # 3. Inventory/Stock Value
    # ✅ PROPER FIX: Calculate from account_transactions (double-entry)
    # This ensures balance sheet matches trial balance!
    inventory_debits = db.session.execute(text("""
        SELECT COALESCE(SUM(debit_amount), 0)
        FROM account_transactions
        WHERE tenant_id = :tenant_id
        AND transaction_type IN ('inventory_opening_debit', 'inventory_purchase')
        AND transaction_date <= :as_of_date
    """), {'tenant_id': tenant_id, 'as_of_date': as_of_date}).fetchone()[0]
    
    inventory_credits = db.session.execute(text("""
        SELECT COALESCE(SUM(credit_amount), 0)
        FROM account_transactions
        WHERE tenant_id = :tenant_id
        AND transaction_type IN ('inventory_sale')
        AND transaction_date <= :as_of_date
    """), {'tenant_id': tenant_id, 'as_of_date': as_of_date}).fetchone()[0]
    
    inventory_value = Decimal(str(inventory_debits or 0)) - Decimal(str(inventory_credits or 0))
    
    # Total Current Assets
    total_current_assets = cash_and_bank_total + accounts_receivable_total + Decimal(str(inventory_value))
    
    # Total Assets (for now, only current assets - no fixed assets tracking yet)
    total_assets = total_current_assets
    
    # ====================
    # LIABILITIES CALCULATION
    # ====================
    
    # 1. Accounts Payable (Unpaid Purchase Bills)
    # IMPORTANT: Only count APPROVED bills (draft bills shouldn't appear in accounting)
    accounts_payable = db.session.execute(text("""
        SELECT 
            vendor_name,
            SUM(total_amount - COALESCE(paid_amount, 0)) as outstanding
        FROM purchase_bills
        WHERE tenant_id = :tenant_id 
        AND status = 'approved'
        AND payment_status != 'paid'
        AND bill_date <= :as_of_date
        GROUP BY vendor_name
        ORDER BY outstanding DESC
    """), {'tenant_id': tenant_id, 'as_of_date': as_of_date}).fetchall()
    
    accounts_payable_total = sum(Decimal(str(acc[1])) for acc in accounts_payable) if accounts_payable else Decimal('0')
    
    # 2. Employee Advances Outstanding (if employees owe money back)
    employee_advances = db.session.execute(text("""
        SELECT 
            e.name as employee_name,
            COALESCE(SUM(
                CASE 
                    WHEN at.transaction_type = 'employee_advance' THEN at.debit_amount
                    WHEN at.transaction_type IN ('employee_expense', 'employee_return') THEN -at.credit_amount
                    ELSE 0
                END
            ), 0) as balance
        FROM account_transactions at
        JOIN employees e ON CAST(at.reference_id AS INTEGER) = e.id
        WHERE at.tenant_id = :tenant_id 
        AND at.reference_type = 'employee'
        AND at.transaction_date <= :as_of_date
        GROUP BY e.name
        HAVING SUM(
            CASE 
                WHEN at.transaction_type = 'employee_advance' THEN at.debit_amount
                WHEN at.transaction_type IN ('employee_expense', 'employee_return') THEN -at.credit_amount
                ELSE 0
            END
        ) < 0
    """), {'tenant_id': tenant_id, 'as_of_date': as_of_date}).fetchall()
    
    employee_advances_total = abs(sum(Decimal(str(emp[1])) for emp in employee_advances)) if employee_advances else Decimal('0')
    
    # Total Current Liabilities
    total_current_liabilities = accounts_payable_total + employee_advances_total
    
    # Total Liabilities (for now, only current liabilities)
    total_liabilities = total_current_liabilities
    
    # ====================
    # EQUITY CALCULATION
    # ====================
    
    # Owner's Equity = Total Assets - Total Liabilities
    total_equity = total_assets - total_liabilities
    
    return render_template('admin/accounts/reports/balance_sheet.html',
                         as_of_date=as_of_date,
                         # Assets
                         cash_bank_accounts=cash_bank_accounts,
                         cash_and_bank_total=float(cash_and_bank_total),
                         accounts_receivable=accounts_receivable,
                         accounts_receivable_total=float(accounts_receivable_total),
                         inventory_value=float(inventory_value),
                         total_current_assets=float(total_current_assets),
                         total_assets=float(total_assets),
                         # Liabilities
                         accounts_payable=accounts_payable,
                         accounts_payable_total=float(accounts_payable_total),
                         employee_advances=employee_advances,
                         employee_advances_total=float(employee_advances_total),
                         total_current_liabilities=float(total_current_liabilities),
                         total_liabilities=float(total_liabilities),
                         # Equity
                         total_equity=float(total_equity),
                         tenant=g.tenant)


@accounts_bp.route('/reports/profit-loss', methods=['GET'])
@require_tenant
@login_required
def profit_loss():
    """Profit & Loss Statement - Income vs. Expenses for a period"""
    from datetime import datetime, timedelta
    import pytz
    
    tenant_id = get_current_tenant_id()
    ist = pytz.timezone('Asia/Kolkata')
    
    # Get date range from query params
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    
    if start_date_str and end_date_str:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
    else:
        # Default: Current month (1st to today)
        today = datetime.now(ist).date()
        start_date = today.replace(day=1)
        end_date = today
    
    # ====================
    # INCOME CALCULATION
    # ====================
    
    # 1. Sales Revenue (from Invoices)
    # 🆕 EXCLUDE credit_adjustment invoices (no revenue - already in kaccha bill)
    sales_revenue_detail = db.session.execute(text("""
        SELECT 
            invoice_number,
            customer_name,
            invoice_date,
            total_amount,
            payment_status
        FROM invoices
        WHERE tenant_id = :tenant_id 
        AND invoice_date BETWEEN :start_date AND :end_date
        AND (invoice_type IS NULL OR invoice_type != 'credit_adjustment')
        ORDER BY invoice_date DESC, invoice_number DESC
    """), {'tenant_id': tenant_id, 'start_date': start_date, 'end_date': end_date}).fetchall()
    
    total_sales = sum(Decimal(str(inv[3])) for inv in sales_revenue_detail)
    sales_paid = sum(Decimal(str(inv[3])) for inv in sales_revenue_detail if inv[4] == 'paid')
    sales_pending = sum(Decimal(str(inv[3])) for inv in sales_revenue_detail if inv[4] != 'paid')
    
    # 1.5. Sales Returns (reduce from gross sales)
    sales_returns_from_transactions = db.session.execute(text("""
        SELECT COALESCE(SUM(debit_amount), 0)
        FROM account_transactions
        WHERE tenant_id = :tenant_id
        AND transaction_type = 'sales_return'
        AND transaction_date BETWEEN :start_date AND :end_date
    """), {'tenant_id': tenant_id, 'start_date': start_date, 'end_date': end_date}).fetchone()[0]
    
    total_sales_returns = Decimal(str(sales_returns_from_transactions or 0))
    
    # Get return details for display
    sales_returns_detail = db.session.execute(text("""
        SELECT 
            voucher_number as return_number,
            narration,
            transaction_date,
            debit_amount,
            'Return' as type
        FROM account_transactions
        WHERE tenant_id = :tenant_id 
        AND transaction_type = 'sales_return'
        AND transaction_date BETWEEN :start_date AND :end_date
        ORDER BY transaction_date DESC, voucher_number DESC
    """), {'tenant_id': tenant_id, 'start_date': start_date, 'end_date': end_date}).fetchall()
    
    # Net Sales = Gross Sales - Sales Returns
    net_sales = total_sales - total_sales_returns
    
    # Total Income (using net sales)
    total_income = net_sales
    
    # ====================
    # EXPENSES CALCULATION
    # ====================
    
    # 1. Cost of Goods Sold (COGS - from double-entry accounting)
    # IMPORTANT: COGS is calculated when items are SOLD, not when purchased
    # Uses account_transactions with transaction_type = 'cogs'
    cogs_from_transactions = db.session.execute(text("""
        SELECT COALESCE(SUM(debit_amount), 0)
        FROM account_transactions
        WHERE tenant_id = :tenant_id
        AND transaction_type = 'cogs'
        AND transaction_date BETWEEN :start_date AND :end_date
    """), {'tenant_id': tenant_id, 'start_date': start_date, 'end_date': end_date}).fetchone()[0]
    
    total_cogs = Decimal(str(cogs_from_transactions or 0))
    
    # Subtract COGS reversals (from returns)
    cogs_reversals = db.session.execute(text("""
        SELECT COALESCE(SUM(credit_amount), 0)
        FROM account_transactions
        WHERE tenant_id = :tenant_id
        AND transaction_type = 'cogs_reversal'
        AND transaction_date BETWEEN :start_date AND :end_date
    """), {'tenant_id': tenant_id, 'start_date': start_date, 'end_date': end_date}).fetchone()[0]
    
    total_cogs = total_cogs - Decimal(str(cogs_reversals or 0))
    
    # Get COGS details for display (which invoices contributed to COGS)
    purchase_expenses_detail = db.session.execute(text("""
        SELECT 
            voucher_number as invoice_number,
            narration,
            transaction_date,
            debit_amount,
            'COGS' as type
        FROM account_transactions
        WHERE tenant_id = :tenant_id 
        AND transaction_type = 'cogs'
        AND transaction_date BETWEEN :start_date AND :end_date
        ORDER BY transaction_date DESC, voucher_number DESC
    """), {'tenant_id': tenant_id, 'start_date': start_date, 'end_date': end_date}).fetchall()
    
    total_purchases = total_cogs  # For backward compatibility with template
    
    # 2. Operating Expenses (from double-entry accounting)
    # Uses account_transactions with transaction_type = 'operating_expense'
    operating_expenses_from_transactions = db.session.execute(text("""
        SELECT COALESCE(SUM(debit_amount), 0)
        FROM account_transactions
        WHERE tenant_id = :tenant_id
        AND transaction_type = 'operating_expense'
        AND transaction_date BETWEEN :start_date AND :end_date
    """), {'tenant_id': tenant_id, 'start_date': start_date, 'end_date': end_date}).fetchone()[0]
    
    total_operating_expenses = Decimal(str(operating_expenses_from_transactions or 0))
    
    # Get details for display (using old expenses table for backward compatibility)
    operating_expenses_detail = db.session.execute(text("""
        SELECT 
            e.expense_date,
            COALESCE(ec.name, 'General') as category_name,
            e.amount,
            e.description,
            e.payment_method
        FROM expenses e
        LEFT JOIN expense_categories ec ON e.category_id = ec.id
        WHERE e.tenant_id = :tenant_id 
        AND e.expense_date BETWEEN :start_date AND :end_date
        ORDER BY e.expense_date DESC
    """), {'tenant_id': tenant_id, 'start_date': start_date, 'end_date': end_date}).fetchall()
    
    # Group operating expenses by category
    operating_expenses_by_category = {}
    for exp in operating_expenses_detail:
        category = exp[1]  # Already has COALESCE to 'General' in SQL
        if category not in operating_expenses_by_category:
            operating_expenses_by_category[category] = Decimal('0')
        operating_expenses_by_category[category] += Decimal(str(exp[2]))
    
    # 3. Employee Expenses (from Employee Cash Advances used)
    employee_expenses_detail = db.session.execute(text("""
        SELECT 
            e.name as employee_name,
            COALESCE(SUM(at.credit_amount), 0) as total_spent
        FROM account_transactions at
        JOIN employees e ON CAST(at.reference_id AS INTEGER) = e.id
        WHERE at.tenant_id = :tenant_id 
        AND at.reference_type = 'employee'
        AND at.transaction_type = 'employee_expense'
        AND at.transaction_date BETWEEN :start_date AND :end_date
        GROUP BY e.name
        HAVING SUM(at.credit_amount) > 0
        ORDER BY total_spent DESC
    """), {'tenant_id': tenant_id, 'start_date': start_date, 'end_date': end_date}).fetchall()
    
    total_employee_expenses = sum(Decimal(str(emp[1])) for emp in employee_expenses_detail)
    
    # 4. Salary Expenses (from double-entry accounting)
    # Uses account_transactions with transaction_type = 'salary_expense'
    salary_expenses_from_transactions = db.session.execute(text("""
        SELECT COALESCE(SUM(debit_amount), 0)
        FROM account_transactions
        WHERE tenant_id = :tenant_id
        AND transaction_type = 'salary_expense'
        AND transaction_date BETWEEN :start_date AND :end_date
    """), {'tenant_id': tenant_id, 'start_date': start_date, 'end_date': end_date}).fetchone()[0]
    
    total_salary_expenses = Decimal(str(salary_expenses_from_transactions or 0))
    
    # Get details for display (using old salary_slips table for backward compatibility)
    start_year = start_date.year
    start_month = start_date.month
    end_year = end_date.year
    end_month = end_date.month
    
    salary_expenses_detail = db.session.execute(text("""
        SELECT 
            e.name as employee_name,
            e.designation,
            SUM(ss.salary_amount) as total_salary
        FROM salary_slips ss
        JOIN employees e ON ss.employee_id = e.id
        WHERE ss.tenant_id = :tenant_id 
        AND (ss.payment_year, ss.payment_month) BETWEEN (:start_year, :start_month) AND (:end_year, :end_month)
        GROUP BY e.id, e.name, e.designation
        ORDER BY total_salary DESC
    """), {
        'tenant_id': tenant_id, 
        'start_year': start_year,
        'start_month': start_month,
        'end_year': end_year,
        'end_month': end_month
    }).fetchall()
    
    # 5. Commission Expenses (from double-entry accounting)
    # Uses account_transactions with transaction_type = 'commission_expense'
    commission_expenses_from_transactions = db.session.execute(text("""
        SELECT COALESCE(SUM(debit_amount), 0)
        FROM account_transactions
        WHERE tenant_id = :tenant_id
        AND transaction_type = 'commission_expense'
        AND transaction_date BETWEEN :start_date AND :end_date
    """), {'tenant_id': tenant_id, 'start_date': start_date, 'end_date': end_date}).fetchone()[0]
    
    commission_reversal_from_transactions = db.session.execute(text("""
        SELECT COALESCE(SUM(credit_amount), 0)
        FROM account_transactions
        WHERE tenant_id = :tenant_id
        AND transaction_type = 'commission_reversal'
        AND transaction_date BETWEEN :start_date AND :end_date
    """), {'tenant_id': tenant_id, 'start_date': start_date, 'end_date': end_date}).fetchone()[0]
    
    total_commission_expenses = Decimal(str(commission_expenses_from_transactions or 0)) - Decimal(str(commission_reversal_from_transactions or 0))
    
    # CRITICAL FIX: Commission expenses can be negative when reversals exceed expenses
    # This is valid and should be shown as negative (reduces total expenses)
    
    # Get commission details for display (BOTH expenses and reversals)
    commission_expenses_detail = db.session.execute(text("""
        SELECT 
            at.transaction_date,
            at.narration,
            at.debit_amount,
            at.voucher_number,
            'expense' as entry_type
        FROM account_transactions at
        WHERE at.tenant_id = :tenant_id 
        AND at.transaction_type = 'commission_expense'
        AND at.transaction_date BETWEEN :start_date AND :end_date
        
        UNION ALL
        
        SELECT 
            at.transaction_date,
            at.narration,
            at.credit_amount * -1 as debit_amount,  -- Show as negative
            at.voucher_number,
            'reversal' as entry_type
        FROM account_transactions at
        WHERE at.tenant_id = :tenant_id 
        AND at.transaction_type = 'commission_reversal'
        AND at.transaction_date BETWEEN :start_date AND :end_date
        
        ORDER BY transaction_date DESC
    """), {'tenant_id': tenant_id, 'start_date': start_date, 'end_date': end_date}).fetchall()
    
    # Total Expenses
    total_expenses = total_cogs + total_operating_expenses + total_employee_expenses + total_salary_expenses + total_commission_expenses
    
    # ====================
    # PROFIT CALCULATION
    # ====================
    
    gross_profit = total_income - total_purchases  # Revenue - COGS
    net_profit = gross_profit - (total_operating_expenses + total_employee_expenses + total_salary_expenses + total_commission_expenses)  # Gross Profit - Operating Expenses
    
    # Profit Margin
    profit_margin = (net_profit / total_income * 100) if total_income > 0 else Decimal('0')
    
    return render_template('admin/accounts/reports/profit_loss.html',
                         start_date=start_date,
                         end_date=end_date,
                         # Income
                         sales_revenue_detail=sales_revenue_detail,
                         total_sales=float(total_sales),
                         sales_paid=float(sales_paid),
                         sales_pending=float(sales_pending),
                         sales_returns_detail=sales_returns_detail,
                         total_sales_returns=float(total_sales_returns),
                         net_sales=float(net_sales),
                         total_income=float(total_income),
                         # Expenses
                         purchase_expenses_detail=purchase_expenses_detail,
                         total_purchases=float(total_purchases),
                         operating_expenses_detail=operating_expenses_detail,
                         operating_expenses_by_category=operating_expenses_by_category,
                         total_operating_expenses=float(total_operating_expenses),
                        employee_expenses_detail=employee_expenses_detail,
                        total_employee_expenses=float(total_employee_expenses),
                        salary_expenses_detail=salary_expenses_detail,
                        total_salary_expenses=float(total_salary_expenses),
                        commission_expenses_detail=commission_expenses_detail,
                        total_commission_expenses=float(total_commission_expenses),
                        total_expenses=float(total_expenses),
                         # Profit
                         gross_profit=float(gross_profit),
                         net_profit=float(net_profit),
                         profit_margin=float(profit_margin),
                         tenant=g.tenant)


@accounts_bp.route('/reports/trial-balance', methods=['GET'])
@require_tenant
@login_required
def trial_balance():
    """Trial Balance - Verify double-entry bookkeeping (Total Debits = Total Credits)"""
    from datetime import datetime
    import pytz
    
    tenant_id = get_current_tenant_id()
    ist = pytz.timezone('Asia/Kolkata')
    
    # Get as_of_date from query params (default: today)
    as_of_date_str = request.args.get('as_of_date')
    if as_of_date_str:
        as_of_date = datetime.strptime(as_of_date_str, '%Y-%m-%d').date()
    else:
        as_of_date = datetime.now(ist).date()
    
    # ====================
    # COLLECT ALL ACCOUNT HEADS WITH DEBIT/CREDIT TOTALS
    # ====================
    
    accounts = []
    
    # 1. Bank & Cash Accounts (Assets - Debit Balance)
    cash_bank_accounts = db.session.execute(text("""
        SELECT 
            account_name,
            account_type,
            current_balance
        FROM bank_accounts
        WHERE tenant_id = :tenant_id 
        AND is_active = TRUE
        ORDER BY account_name
    """), {'tenant_id': tenant_id}).fetchall()
    
    for acc in cash_bank_accounts:
        balance = Decimal(str(acc[2]))
        accounts.append({
            'account_name': f"{acc[0]} ({'Cash' if acc[1] == 'cash' else 'Bank'})",
            'category': 'Assets',
            'debit': balance if balance >= 0 else Decimal('0'),
            'credit': abs(balance) if balance < 0 else Decimal('0')
        })
    
    # 2. Accounts Receivable (Assets - Debit Balance)
    # 🆕 EXCLUDE credit_adjustment invoices (no AR - customer already paid via kaccha bill)
    receivables = db.session.execute(text("""
        SELECT 
            customer_name,
            SUM(total_amount - COALESCE(paid_amount, 0)) as outstanding
        FROM invoices
        WHERE tenant_id = :tenant_id 
        AND payment_status != 'paid'
        AND invoice_date <= :as_of_date
        AND (invoice_type IS NULL OR invoice_type != 'credit_adjustment')
        GROUP BY customer_name
        HAVING SUM(total_amount - COALESCE(paid_amount, 0)) > 0
        ORDER BY customer_name
    """), {'tenant_id': tenant_id, 'as_of_date': as_of_date}).fetchall()
    
    receivables_total = sum(Decimal(str(r[1])) for r in receivables) if receivables else Decimal('0')
    if receivables_total > 0:
        accounts.append({
            'account_name': 'Accounts Receivable (Debtors)',
            'category': 'Assets',
            'debit': receivables_total,
            'credit': Decimal('0')
        })
    
    # 3. Inventory (Assets - Debit Balance)
    # ✅ PROPER FIX: Calculate from account_transactions (double-entry)
    # Inventory increases: inventory_opening_debit, inventory_purchase
    # Inventory decreases: inventory_sale (ONLY! Not COGS - that's a separate expense)
    inventory_debits = db.session.execute(text("""
        SELECT COALESCE(SUM(debit_amount), 0)
        FROM account_transactions
        WHERE tenant_id = :tenant_id
        AND transaction_type IN ('inventory_opening_debit', 'inventory_purchase')
        AND transaction_date <= :as_of_date
    """), {'tenant_id': tenant_id, 'as_of_date': as_of_date}).fetchone()[0]
    
    inventory_credits = db.session.execute(text("""
        SELECT COALESCE(SUM(credit_amount), 0)
        FROM account_transactions
        WHERE tenant_id = :tenant_id
        AND transaction_type IN ('inventory_sale')
        AND transaction_date <= :as_of_date
    """), {'tenant_id': tenant_id, 'as_of_date': as_of_date}).fetchone()[0]
    
    inventory_value = Decimal(str(inventory_debits or 0)) - Decimal(str(inventory_credits or 0))
    
    if inventory_value > 0:
        accounts.append({
            'account_name': 'Inventory (Stock on Hand)',
            'category': 'Assets',
            'debit': inventory_value,
            'credit': Decimal('0')
        })
    
    # 3.5. Input Tax Credit / ITC (Asset - Debit Balance)
    # GST paid on purchases that can be claimed back from government
    itc_from_transactions = db.session.execute(text("""
        SELECT COALESCE(SUM(debit_amount), 0)
        FROM account_transactions
        WHERE tenant_id = :tenant_id
        AND transaction_type = 'input_tax_credit'
        AND transaction_date <= :as_of_date
    """), {'tenant_id': tenant_id, 'as_of_date': as_of_date}).fetchone()[0]
    
    itc_total = Decimal(str(itc_from_transactions or 0))
    
    if itc_total > 0:
        accounts.append({
            'account_name': 'Input Tax Credit (ITC)',
            'category': 'Assets',
            'debit': itc_total,
            'credit': Decimal('0')
        })
    
    # 3.6. GST Receivable on Returns (Asset - Debit Balance)
    # GST amounts from customer returns that can be claimed back
    gst_return_cgst = db.session.execute(text("""
        SELECT COALESCE(SUM(debit_amount), 0)
        FROM account_transactions
        WHERE tenant_id = :tenant_id
        AND transaction_type = 'gst_return_cgst'
        AND transaction_date <= :as_of_date
    """), {'tenant_id': tenant_id, 'as_of_date': as_of_date}).fetchone()[0]
    
    gst_return_sgst = db.session.execute(text("""
        SELECT COALESCE(SUM(debit_amount), 0)
        FROM account_transactions
        WHERE tenant_id = :tenant_id
        AND transaction_type = 'gst_return_sgst'
        AND transaction_date <= :as_of_date
    """), {'tenant_id': tenant_id, 'as_of_date': as_of_date}).fetchone()[0]
    
    gst_return_igst = db.session.execute(text("""
        SELECT COALESCE(SUM(debit_amount), 0)
        FROM account_transactions
        WHERE tenant_id = :tenant_id
        AND transaction_type = 'gst_return_igst'
        AND transaction_date <= :as_of_date
    """), {'tenant_id': tenant_id, 'as_of_date': as_of_date}).fetchone()[0]
    
    gst_return_total = Decimal(str(gst_return_cgst or 0)) + Decimal(str(gst_return_sgst or 0)) + Decimal(str(gst_return_igst or 0))
    
    if gst_return_total > 0:
        accounts.append({
            'account_name': 'GST Receivable (Returns)',
            'category': 'Assets',
            'debit': gst_return_total,
            'credit': Decimal('0')
        })
    
    # 3.7. Commission Recoverable (Asset - Debit Balance)
    # Commission amounts to be recovered from agents due to sales returns
    commission_recoverable = db.session.execute(text("""
        SELECT COALESCE(SUM(debit_amount), 0)
        FROM account_transactions
        WHERE tenant_id = :tenant_id
        AND transaction_type = 'commission_recoverable'
        AND transaction_date <= :as_of_date
    """), {'tenant_id': tenant_id, 'as_of_date': as_of_date}).fetchone()[0]
    
    commission_recoverable_total = Decimal(str(commission_recoverable or 0))
    
    if commission_recoverable_total > 0:
        accounts.append({
            'account_name': 'Commission Recoverable',
            'category': 'Assets',
            'debit': commission_recoverable_total,
            'credit': Decimal('0')
        })
    
    # 4. Accounts Payable (Liabilities - Credit Balance)
    # NEW: Calculate from account_transactions (double-entry system)
    # Formula: CREDITS (bills created) - DEBITS (payments made) = Outstanding
    payables_from_transactions = db.session.execute(text("""
        SELECT COALESCE(SUM(credit_amount - debit_amount), 0)
        FROM account_transactions
        WHERE tenant_id = :tenant_id
        AND transaction_type IN ('accounts_payable', 'accounts_payable_payment')
        AND transaction_date <= :as_of_date
    """), {'tenant_id': tenant_id, 'as_of_date': as_of_date}).fetchone()[0]
    
    # ✅ NO FALLBACK - Only use account_transactions for accuracy
    payables_total = Decimal(str(payables_from_transactions or 0))
    
    if payables_total > 0:
        accounts.append({
            'account_name': 'Accounts Payable (Vendors)',
            'category': 'Liabilities',
            'debit': Decimal('0'),
            'credit': payables_total
        })
    
    # 4.5. GST Payable (Liabilities - Credit Balance)
    # 🔧 CRITICAL FIX: This was missing! GST collected from customers must appear as liability!
    gst_payable_from_transactions = db.session.execute(text("""
        SELECT COALESCE(SUM(credit_amount), 0)
        FROM account_transactions
        WHERE tenant_id = :tenant_id
        AND transaction_type = 'gst_payable'
        AND transaction_date <= :as_of_date
    """), {'tenant_id': tenant_id, 'as_of_date': as_of_date}).fetchone()[0]
    
    gst_payable_total = Decimal(str(gst_payable_from_transactions or 0))
    
    if gst_payable_total > 0:
        accounts.append({
            'account_name': 'GST Payable (CGST+SGST+IGST)',
            'category': 'Liabilities',
            'debit': Decimal('0'),
            'credit': gst_payable_total
        })
    
    # 5. Sales Income (Income - Credit Balance)
    # NEW: Calculate from account_transactions (double-entry system)
    # This will be populated when we implement sales/invoice accounting
    sales_from_transactions = db.session.execute(text("""
        SELECT COALESCE(SUM(credit_amount), 0)
        FROM account_transactions
        WHERE tenant_id = :tenant_id
        AND transaction_type = 'sales_income'
        AND transaction_date <= :as_of_date
    """), {'tenant_id': tenant_id, 'as_of_date': as_of_date}).fetchone()[0]
    
    # ✅ NO FALLBACK - Only use account_transactions for accuracy
    sales_total = Decimal(str(sales_from_transactions or 0))
    
    if sales_total > 0:
        accounts.append({
            'account_name': 'Sales Income',
            'category': 'Income',
            'debit': Decimal('0'),
            'credit': sales_total
        })
    
    # 6. Cost of Goods Sold / COGS (Expense - Debit Balance)
    # Calculate from account_transactions (double-entry system)
    # COGS is recorded when items are SOLD, not when purchased
    cogs_from_transactions = db.session.execute(text("""
        SELECT COALESCE(SUM(debit_amount), 0)
        FROM account_transactions
        WHERE tenant_id = :tenant_id
        AND transaction_type = 'cogs'
        AND transaction_date <= :as_of_date
    """), {'tenant_id': tenant_id, 'as_of_date': as_of_date}).fetchone()[0]
    
    cogs_total = Decimal(str(cogs_from_transactions or 0))
    
    # Subtract COGS reversals (from returns)
    cogs_reversals = db.session.execute(text("""
        SELECT COALESCE(SUM(credit_amount), 0)
        FROM account_transactions
        WHERE tenant_id = :tenant_id
        AND transaction_type = 'cogs_reversal'
        AND transaction_date <= :as_of_date
    """), {'tenant_id': tenant_id, 'as_of_date': as_of_date}).fetchone()[0]
    
    cogs_total = cogs_total - Decimal(str(cogs_reversals or 0))
    
    # IMPORTANT: Do NOT show purchase_bills as COGS!
    # In double-entry: Purchases → Inventory (Asset), not Expense
    # Only when sold: Inventory → COGS (Expense)
    
    if cogs_total > 0:
        accounts.append({
            'account_name': 'Cost of Goods Sold (COGS)',
            'category': 'Expenses',
            'debit': cogs_total,
            'credit': Decimal('0')
        })
    
    # 6.5. Sales Returns (Contra-Revenue - Debit Balance)
    # Sales returns reduce income, shown as debit
    sales_returns_from_transactions = db.session.execute(text("""
        SELECT COALESCE(SUM(debit_amount), 0)
        FROM account_transactions
        WHERE tenant_id = :tenant_id
        AND transaction_type = 'sales_return'
        AND transaction_date <= :as_of_date
    """), {'tenant_id': tenant_id, 'as_of_date': as_of_date}).fetchone()[0]
    
    sales_returns_total = Decimal(str(sales_returns_from_transactions or 0))
    
    if sales_returns_total > 0:
        accounts.append({
            'account_name': 'Sales Returns',
            'category': 'Expenses',
            'debit': sales_returns_total,
            'credit': Decimal('0')
        })
    
    # 6.6. Round-off Expense (from returns) (Expense - Can be DEBIT or CREDIT)
    # CRITICAL FIX: Net DEBIT and CREDIT amounts (not just DEBIT)
    round_off_debits = db.session.execute(text("""
        SELECT COALESCE(SUM(debit_amount), 0)
        FROM account_transactions
        WHERE tenant_id = :tenant_id
        AND transaction_type = 'round_off_expense'
        AND transaction_date <= :as_of_date
    """), {'tenant_id': tenant_id, 'as_of_date': as_of_date}).fetchone()[0]
    
    round_off_credits = db.session.execute(text("""
        SELECT COALESCE(SUM(credit_amount), 0)
        FROM account_transactions
        WHERE tenant_id = :tenant_id
        AND transaction_type = 'round_off_expense'
        AND transaction_date <= :as_of_date
    """), {'tenant_id': tenant_id, 'as_of_date': as_of_date}).fetchone()[0]
    
    round_off_total = Decimal(str(round_off_debits or 0)) - Decimal(str(round_off_credits or 0))
    
    # Show if non-zero (can be positive DEBIT or negative CREDIT)
    if round_off_total != 0:
        if round_off_total > 0:
            # Normal: DEBIT balance (expense increases total)
            accounts.append({
                'account_name': 'Round-off Expense',
                'category': 'Expenses',
                'debit': round_off_total,
                'credit': Decimal('0')
            })
        else:
            # Negative: CREDIT balance (reduces total expenses)
            accounts.append({
                'account_name': 'Round-off Expense (Credit Excess)',
                'category': 'Expenses',
                'debit': Decimal('0'),
                'credit': abs(round_off_total)
            })
    
    # 7. Operating Expenses (Expense - Debit Balance)
    # NEW: Calculate from account_transactions (double-entry system)
    # The expenses.py route already creates entries with transaction_type='expense'
    operating_from_transactions = db.session.execute(text("""
        SELECT COALESCE(SUM(debit_amount), 0)
        FROM account_transactions
        WHERE tenant_id = :tenant_id
        AND transaction_type = 'operating_expense'
        AND transaction_date <= :as_of_date
    """), {'tenant_id': tenant_id, 'as_of_date': as_of_date}).fetchone()[0]
    
    # ✅ NO FALLBACK - Only use account_transactions for accuracy
    operating_total = Decimal(str(operating_from_transactions or 0))
    if operating_total > 0:
        accounts.append({
            'account_name': 'Operating Expenses',
            'category': 'Expenses',
            'debit': operating_total,
            'credit': Decimal('0')
        })
    
    # 8. Employee Expenses (Expense - Debit Balance)
    employee_expenses_total = db.session.execute(text("""
        SELECT COALESCE(SUM(credit_amount), 0)
        FROM account_transactions
        WHERE tenant_id = :tenant_id 
        AND reference_type = 'employee'
        AND transaction_type = 'employee_expense'
        AND transaction_date <= :as_of_date
    """), {'tenant_id': tenant_id, 'as_of_date': as_of_date}).fetchone()[0] or Decimal('0')
    
    if Decimal(str(employee_expenses_total)) > 0:
        accounts.append({
            'account_name': 'Employee Expenses',
            'category': 'Expenses',
            'debit': Decimal(str(employee_expenses_total)),
            'credit': Decimal('0')
        })
    
    # 9. Salary Expenses (Expense - Debit Balance)
    # NEW: Calculate from account_transactions (double-entry system)
    # This will be populated when we fix salary payment accounting (Day 3)
    salary_from_transactions = db.session.execute(text("""
        SELECT COALESCE(SUM(debit_amount), 0)
        FROM account_transactions
        WHERE tenant_id = :tenant_id
        AND transaction_type = 'salary_expense'
        AND transaction_date <= :as_of_date
    """), {'tenant_id': tenant_id, 'as_of_date': as_of_date}).fetchone()[0]
    
    # ✅ NO FALLBACK - Only use account_transactions for accuracy
    salary_total = Decimal(str(salary_from_transactions or 0))
    
    if salary_total > 0:
        accounts.append({
            'account_name': 'Salary Expenses',
            'category': 'Expenses',
            'debit': salary_total,
            'credit': Decimal('0')
        })
    
    # 10. Commission Expenses (Expense - Debit Balance)
    # Calculate from account_transactions (double-entry system)
    commission_from_transactions = db.session.execute(text("""
        SELECT COALESCE(SUM(debit_amount), 0)
        FROM account_transactions
        WHERE tenant_id = :tenant_id
        AND transaction_type = 'commission_expense'
        AND transaction_date <= :as_of_date
    """), {'tenant_id': tenant_id, 'as_of_date': as_of_date}).fetchone()[0]
    
    commission_reversal_from_transactions = db.session.execute(text("""
        SELECT COALESCE(SUM(credit_amount), 0)
        FROM account_transactions
        WHERE tenant_id = :tenant_id
        AND transaction_type = 'commission_reversal'
        AND transaction_date <= :as_of_date
    """), {'tenant_id': tenant_id, 'as_of_date': as_of_date}).fetchone()[0]
    
    commission_total = Decimal(str(commission_from_transactions or 0)) - Decimal(str(commission_reversal_from_transactions or 0))
    
    # CRITICAL FIX: Show commission account even if negative (when reversals > expenses)
    # Negative balance in expense account = CREDIT balance
    if commission_total != 0:
        if commission_total > 0:
            # Normal: Expenses exceed reversals (DEBIT balance)
            accounts.append({
                'account_name': 'Commission Expenses',
                'category': 'Expenses',
                'debit': commission_total,
                'credit': Decimal('0')
            })
        else:
            # Unusual: Reversals exceed expenses (CREDIT balance)
            # Show as negative expense (reduces total expenses)
            accounts.append({
                'account_name': 'Commission Expenses (Reversal Excess)',
                'category': 'Expenses',
                'debit': Decimal('0'),
                'credit': abs(commission_total)
            })
    
    # 11. Owner's Equity / Capital (from Opening Balance Equity - Credit Balance)
    # These are entries with account_id = NULL and transaction_type in:
    # - 'opening_balance_equity' (for cash/bank opening - group by narration for separate lines)
    # - 'opening_balance_inventory_equity' (for inventory opening - aggregate all together)
    #
    # ✅ FIX: Use CASE statement to handle inventory vs cash/bank differently
    equity_entries = db.session.execute(text("""
        SELECT 
            transaction_type,
            CASE 
                WHEN transaction_type = 'opening_balance_inventory_equity' THEN 'Inventory Opening'
                ELSE narration
            END as grouping_key,
            SUM(credit_amount - debit_amount) as net_credit
        FROM account_transactions
        WHERE tenant_id = :tenant_id 
        AND account_id IS NULL
        AND transaction_type IN ('opening_balance_equity', 'opening_balance_inventory_equity')
        AND transaction_date <= :as_of_date
        GROUP BY transaction_type, grouping_key
        ORDER BY transaction_type, grouping_key
    """), {'tenant_id': tenant_id, 'as_of_date': as_of_date}).fetchall()
    
    for equity in equity_entries:
        transaction_type = equity[0]
        grouping_key = equity[1]
        net_amount = Decimal(str(equity[2]))
        
        if net_amount != 0:
            # Create descriptive account name
            if transaction_type == 'opening_balance_inventory_equity':
                # All inventory opening entries aggregated as ONE line
                account_label = "Owner's Capital - Inventory Opening"
            elif transaction_type == 'opening_balance_equity':
                # Cash/Bank opening - use narration to distinguish
                narration = grouping_key
                if 'Cash' in narration or 'cash' in narration.lower():
                    account_label = "Owner's Capital - Cash Opening"
                elif 'Bank' in narration or any(bank in narration for bank in ['ICICI', 'HDFC', 'SBI', 'Axis']):
                    account_label = "Owner's Capital - Bank Opening"
                else:
                    account_label = "Owner's Capital - Opening Balance"
            else:
                account_label = "Owner's Capital - Opening Balance"
            
            accounts.append({
                'account_name': account_label,
                'category': 'Liabilities',  # Equity is treated as liability in trial balance
                'debit': abs(net_amount) if net_amount < 0 else Decimal('0'),
                'credit': net_amount if net_amount > 0 else Decimal('0')
            })
    
    # ====================
    # CALCULATE TOTALS
    # ====================
    
    # Group accounts by category
    assets_accounts = [acc for acc in accounts if acc['category'] == 'Assets']
    liabilities_accounts = [acc for acc in accounts if acc['category'] == 'Liabilities']
    income_accounts = [acc for acc in accounts if acc['category'] == 'Income']
    expense_accounts = [acc for acc in accounts if acc['category'] == 'Expenses']
    
    # Calculate grand totals
    total_debit = sum(acc['debit'] for acc in accounts)
    total_credit = sum(acc['credit'] for acc in accounts)
    
    # Calculate difference (should be zero in a balanced system)
    difference = total_debit - total_credit
    is_balanced = (difference == 0)
    
    return render_template('admin/accounts/reports/trial_balance.html',
                         as_of_date=as_of_date,
                         assets_accounts=assets_accounts,
                        liabilities_accounts=liabilities_accounts,
                        income_accounts=income_accounts,
                        expense_accounts=expense_accounts,
                        total_debit=float(total_debit),
                        total_credit=float(total_credit),
                        difference=float(difference),
                        is_balanced=is_balanced,
                        tenant=g.tenant)


# =====================================================
# ADVANCED REPORTS: AGING & RECONCILIATION
# =====================================================

@accounts_bp.route('/reports/receivables-aging')
@login_required
def receivables_aging():
    """
    Receivables Aging Report
    Shows which customers owe money and for how long
    Aging buckets: Current, 1-30, 31-60, 61-90, 90+ days overdue
    """
    from flask import g
    tenant_id = g.tenant.id if hasattr(g, 'tenant') and g.tenant else session.get('tenant_id')
    ist = pytz.timezone('Asia/Kolkata')
    today = datetime.now(ist).date()
    
    # Get all unpaid/partially paid invoices
    invoices = db.session.execute(text("""
        SELECT 
            id,
            invoice_number,
            customer_name,
            invoice_date,
            due_date,
            total_amount,
            COALESCE(paid_amount, 0) as paid_amount,
            payment_status
        FROM invoices
        WHERE tenant_id = :tenant_id 
        AND payment_status != 'paid'
        ORDER BY customer_name, invoice_date
    """), {'tenant_id': tenant_id}).fetchall()
    
    print(f"[DEBUG] Receivables Aging - Tenant ID: {tenant_id}")
    print(f"[DEBUG] Found {len(invoices)} unpaid/partial invoices")
    if invoices:
        for inv in invoices[:5]:  # Show first 5
            print(f"  - {inv[1]}: {inv[2]}, Status: {inv[7]}, Outstanding: ₹{float(inv[5]) - float(inv[6]):.2f}")
    
    # Group by customer and aging bucket
    aging_data = {}
    aging_summary = {
        'current': Decimal('0'),      # Not yet due
        '1_30': Decimal('0'),          # 1-30 days overdue
        '31_60': Decimal('0'),         # 31-60 days overdue
        '61_90': Decimal('0'),         # 61-90 days overdue
        '90_plus': Decimal('0')        # 90+ days overdue
    }
    
    for inv in invoices:
        customer = inv[2]
        invoice_date = inv[3]
        due_date = inv[4] if inv[4] else invoice_date  # Use invoice_date if no due_date
        outstanding = Decimal(str(inv[5])) - Decimal(str(inv[6]))
        
        # Calculate days overdue
        days_overdue = (today - due_date).days
        
        # Determine aging bucket
        if days_overdue <= 0:
            bucket = 'current'
            bucket_label = 'Current (Not Due)'
        elif days_overdue <= 30:
            bucket = '1_30'
            bucket_label = '1-30 Days'
        elif days_overdue <= 60:
            bucket = '31_60'
            bucket_label = '31-60 Days'
        elif days_overdue <= 90:
            bucket = '61_90'
            bucket_label = '61-90 Days'
        else:
            bucket = '90_plus'
            bucket_label = '90+ Days'
        
        # Initialize customer if not exists
        if customer not in aging_data:
            aging_data[customer] = {
                'invoices': [],
                'total': Decimal('0'),
                'current': Decimal('0'),
                '1_30': Decimal('0'),
                '31_60': Decimal('0'),
                '61_90': Decimal('0'),
                '90_plus': Decimal('0')
            }
        
        # Add invoice to customer
        aging_data[customer]['invoices'].append({
            'invoice_number': inv[1],
            'invoice_date': invoice_date,
            'due_date': due_date,
            'days_overdue': days_overdue,
            'outstanding': outstanding,
            'bucket': bucket_label
        })
        
        # Add to customer totals
        aging_data[customer]['total'] += outstanding
        aging_data[customer][bucket] += outstanding
        
        # Add to summary totals
        aging_summary[bucket] += outstanding
    
    # Calculate grand total
    grand_total = sum(aging_summary.values())
    
    return render_template('admin/accounts/reports/receivables_aging.html',
                         aging_data=aging_data,
                         aging_summary=aging_summary,
                         grand_total=float(grand_total),
                         today=today,
                         tenant=g.tenant)


@accounts_bp.route('/reports/payables-aging')
@login_required
def payables_aging():
    """
    Payables Aging Report
    Shows which vendors you owe money to and for how long
    Aging buckets: Current, 1-30, 31-60, 61-90, 90+ days overdue
    """
    from flask import g
    tenant_id = g.tenant.id if hasattr(g, 'tenant') and g.tenant else session.get('tenant_id')
    ist = pytz.timezone('Asia/Kolkata')
    today = datetime.now(ist).date()
    
    # Get all unpaid/partially paid bills
    # IMPORTANT: Only count APPROVED bills (draft bills shouldn't appear in accounting)
    bills = db.session.execute(text("""
        SELECT 
            id,
            bill_number,
            vendor_name,
            bill_date,
            due_date,
            total_amount,
            COALESCE(paid_amount, 0) as paid_amount,
            payment_status
        FROM purchase_bills
        WHERE tenant_id = :tenant_id 
        AND status = 'approved'
        AND payment_status != 'paid'
        ORDER BY vendor_name, bill_date
    """), {'tenant_id': tenant_id}).fetchall()
    
    print(f"[DEBUG] Payables Aging - Tenant ID: {tenant_id}")
    print(f"[DEBUG] Found {len(bills)} unpaid/partial bills")
    if bills:
        for bill in bills[:5]:  # Show first 5
            print(f"  - {bill[1]}: {bill[2]}, Status: {bill[7]}, Outstanding: ₹{float(bill[5]) - float(bill[6]):.2f}")
    
    # Group by vendor and aging bucket
    aging_data = {}
    aging_summary = {
        'current': Decimal('0'),
        '1_30': Decimal('0'),
        '31_60': Decimal('0'),
        '61_90': Decimal('0'),
        '90_plus': Decimal('0')
    }
    
    for bill in bills:
        vendor = bill[2]
        bill_date = bill[3]
        due_date = bill[4] if bill[4] else bill_date
        outstanding = Decimal(str(bill[5])) - Decimal(str(bill[6]))
        
        # Calculate days overdue
        days_overdue = (today - due_date).days
        
        # Determine aging bucket
        if days_overdue <= 0:
            bucket = 'current'
            bucket_label = 'Current (Not Due)'
        elif days_overdue <= 30:
            bucket = '1_30'
            bucket_label = '1-30 Days'
        elif days_overdue <= 60:
            bucket = '31_60'
            bucket_label = '31-60 Days'
        elif days_overdue <= 90:
            bucket = '61_90'
            bucket_label = '61-90 Days'
        else:
            bucket = '90_plus'
            bucket_label = '90+ Days'
        
        # Initialize vendor if not exists
        if vendor not in aging_data:
            aging_data[vendor] = {
                'bills': [],
                'total': Decimal('0'),
                'current': Decimal('0'),
                '1_30': Decimal('0'),
                '31_60': Decimal('0'),
                '61_90': Decimal('0'),
                '90_plus': Decimal('0')
            }
        
        # Add bill to vendor
        aging_data[vendor]['bills'].append({
            'bill_number': bill[1],
            'bill_date': bill_date,
            'due_date': due_date,
            'days_overdue': days_overdue,
            'outstanding': outstanding,
            'bucket': bucket_label
        })
        
        # Add to vendor totals
        aging_data[vendor]['total'] += outstanding
        aging_data[vendor][bucket] += outstanding
        
        # Add to summary totals
        aging_summary[bucket] += outstanding
    
    # Calculate grand total
    grand_total = sum(aging_summary.values())
    
    return render_template('admin/accounts/reports/payables_aging.html',
                         aging_data=aging_data,
                         aging_summary=aging_summary,
                         grand_total=float(grand_total),
                         today=today,
                         tenant=g.tenant)


@accounts_bp.route('/reports/bank-reconciliation')
@login_required
def bank_reconciliation():
    """
    Bank Reconciliation Report
    Match your records with bank statement
    Shows transactions that need to be reconciled
    """
    from flask import g
    tenant_id = g.tenant.id if hasattr(g, 'tenant') and g.tenant else session.get('tenant_id')
    
    if not tenant_id:
        flash('Please log in to view this report', 'error')
        return redirect(url_for('admin.login'))
    ist = pytz.timezone('Asia/Kolkata')
    today = datetime.now(ist).date()
    
    # Get date range from request (default: last month)
    from_date_str = request.args.get('from_date')
    to_date_str = request.args.get('to_date')
    account_id = request.args.get('account_id')
    
    if from_date_str and to_date_str:
        from_date = datetime.strptime(from_date_str, '%Y-%m-%d').date()
        to_date = datetime.strptime(to_date_str, '%Y-%m-%d').date()
    else:
        # Default: Current month
        from_date = today.replace(day=1)
        to_date = today
    
    # Get all bank/cash accounts
    accounts = db.session.execute(text("""
        SELECT id, account_name, account_type, current_balance
        FROM bank_accounts
        WHERE tenant_id = :tenant_id AND is_active = TRUE
        ORDER BY account_name
    """), {'tenant_id': tenant_id}).fetchall()
    
    print(f"[DEBUG] Bank Reconciliation - Tenant ID: {tenant_id}")
    print(f"[DEBUG] Found {len(accounts)} accounts")
    if accounts:
        for acc in accounts:
            print(f"  - {acc[1]} (ID: {acc[0]})")
    
    # If no accounts found, show message
    if not accounts:
        flash('⚠️ No bank/cash accounts found! Please create an account first.', 'warning')
        return redirect(url_for('accounts.list_accounts'))
    
    # If no account selected, use first one
    if not account_id and accounts:
        account_id = str(accounts[0][0])
    
    reconciliation_data = None
    if account_id:
        # Get opening balance (balance at start of period)
        opening_balance = db.session.execute(text("""
            SELECT balance_after
            FROM account_transactions
            WHERE tenant_id = :tenant_id 
            AND account_id = :account_id
            AND transaction_date < :from_date
            ORDER BY transaction_date DESC, created_at DESC
            LIMIT 1
        """), {
            'tenant_id': tenant_id,
            'account_id': int(account_id),
            'from_date': from_date
        }).fetchone()
        
        opening_bal = Decimal(str(opening_balance[0])) if opening_balance else Decimal('0')
        
        # Get all transactions in period
        transactions = db.session.execute(text("""
            SELECT 
                transaction_date,
                transaction_type,
                voucher_number,
                narration,
                debit_amount,
                credit_amount,
                balance_after,
                reference_type,
                reference_id
            FROM account_transactions
            WHERE tenant_id = :tenant_id 
            AND account_id = :account_id
            AND transaction_date BETWEEN :from_date AND :to_date
            ORDER BY transaction_date, created_at
        """), {
            'tenant_id': tenant_id,
            'account_id': int(account_id),
            'from_date': from_date,
            'to_date': to_date
        }).fetchall()
        
        # Process transactions
        txn_list = []
        for txn in transactions:
            txn_list.append({
                'date': txn[0],
                'type': txn[1],
                'voucher': txn[2] or '-',
                'narration': txn[3],
                'debit': float(txn[4]),
                'credit': float(txn[5]),
                'balance': float(txn[6])
            })
        
        # Calculate totals
        total_debit = sum(Decimal(str(t[4])) for t in transactions)
        total_credit = sum(Decimal(str(t[5])) for t in transactions)
        closing_balance = opening_bal + total_debit - total_credit
        
        # Get account details
        selected_account = db.session.execute(text("""
            SELECT account_name, account_type, current_balance
            FROM bank_accounts
            WHERE id = :account_id AND tenant_id = :tenant_id
        """), {'account_id': int(account_id), 'tenant_id': tenant_id}).fetchone()
        
        reconciliation_data = {
            'account_name': selected_account[0],
            'account_type': selected_account[1],
            'opening_balance': float(opening_bal),
            'total_debit': float(total_debit),
            'total_credit': float(total_credit),
            'closing_balance': float(closing_balance),
            'current_balance': float(selected_account[2]),
            'transactions': txn_list,
            'difference': float(selected_account[2]) - float(closing_balance)
        }
    
    return render_template('admin/accounts/reports/bank_reconciliation.html',
                         accounts=accounts,
                         selected_account_id=int(account_id) if account_id else None,
                         from_date=from_date,
                         to_date=to_date,
                         reconciliation_data=reconciliation_data,
                         today=today,
                         tenant=g.tenant)

