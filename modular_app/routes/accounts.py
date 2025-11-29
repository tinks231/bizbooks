"""
Bank/Cash Account Management Routes
Phase 1 of Accounting Module
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, g, session
from models import db, BankAccount, AccountTransaction
from utils.tenant_middleware import require_tenant, get_current_tenant_id
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
    accounts = db.session.execute("""
        SELECT 
            id, account_name, account_type, bank_name, account_number,
            current_balance, is_active, is_default, description
        FROM bank_accounts
        WHERE tenant_id = ?
        ORDER BY 
            CASE account_type 
                WHEN 'cash' THEN 1 
                WHEN 'bank' THEN 2 
                WHEN 'petty_cash' THEN 3 
            END,
            account_name
    """, (tenant_id,)).fetchall()
    
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
        is_default = 1 if request.form.get('is_default') == 'on' else 0
        
        # Validation
        if not account_name:
            flash('❌ Account name is required', 'error')
            return redirect(url_for('accounts.list_accounts'))
        
        # If marking as default, unmark others of same type
        if is_default:
            db.session.execute("""
                UPDATE bank_accounts 
                SET is_default = 0 
                WHERE tenant_id = ? AND account_type = ?
            """, (tenant_id, account_type))
        
        ist = pytz.timezone('Asia/Kolkata')
        now = datetime.now(ist)
        
        # Insert account
        cursor = db.session.execute("""
            INSERT INTO bank_accounts 
            (tenant_id, account_name, account_type, bank_name, account_number,
             ifsc_code, branch, opening_balance, current_balance, is_active,
             is_default, description, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            tenant_id, account_name, account_type, bank_name, account_number,
            ifsc_code, branch, opening_balance, opening_balance, 1,
            is_default, description, now, now
        ))
        
        account_id = cursor.lastrowid
        
        # If opening balance > 0, create opening balance transaction
        if opening_balance > 0:
            db.session.execute("""
                INSERT INTO account_transactions
                (tenant_id, account_id, transaction_date, transaction_type,
                 debit_amount, credit_amount, balance_after, narration, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                tenant_id, account_id, now.date(), 'opening_balance',
                opening_balance, 0.00, opening_balance,
                'Opening balance', now
            ))
        
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
        is_active = 1 if request.form.get('is_active') == 'on' else 0
        is_default = 1 if request.form.get('is_default') == 'on' else 0
        
        # Validation
        if not account_name:
            flash('❌ Account name is required', 'error')
            return redirect(url_for('accounts.list_accounts'))
        
        # Get account type
        account_type = db.session.execute(
            "SELECT account_type FROM bank_accounts WHERE id = ? AND tenant_id = ?",
            (account_id, tenant_id)
        ).fetchone()[0]
        
        # If marking as default, unmark others of same type
        if is_default:
            db.session.execute("""
                UPDATE bank_accounts 
                SET is_default = 0 
                WHERE tenant_id = ? AND account_type = ? AND id != ?
            """, (tenant_id, account_type, account_id))
        
        ist = pytz.timezone('Asia/Kolkata')
        now = datetime.now(ist)
        
        # Update account
        db.session.execute("""
            UPDATE bank_accounts
            SET account_name = ?, bank_name = ?, account_number = ?,
                ifsc_code = ?, branch = ?, description = ?,
                is_active = ?, is_default = ?, updated_at = ?
            WHERE id = ? AND tenant_id = ?
        """, (
            account_name, bank_name, account_number, ifsc_code, branch,
            description, is_active, is_default, now, account_id, tenant_id
        ))
        
        db.session.commit()
        
        flash(f'✅ Account "{account_name}" updated successfully!', 'success')
        
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
        txn_count = db.session.execute("""
            SELECT COUNT(*) FROM account_transactions
            WHERE account_id = ? AND tenant_id = ?
        """, (account_id, tenant_id)).fetchone()[0]
        
        if txn_count > 0:
            flash(f'❌ Cannot delete account with {txn_count} transactions. Deactivate it instead.', 'error')
            return redirect(url_for('accounts.list_accounts'))
        
        # Get account name
        account_name = db.session.execute(
            "SELECT account_name FROM bank_accounts WHERE id = ? AND tenant_id = ?",
            (account_id, tenant_id)
        ).fetchone()[0]
        
        # Delete account
        db.session.execute(
            "DELETE FROM bank_accounts WHERE id = ? AND tenant_id = ?",
            (account_id, tenant_id)
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
    account = db.session.execute("""
        SELECT 
            id, account_name, account_type, bank_name, account_number,
            opening_balance, current_balance, is_active
        FROM bank_accounts
        WHERE id = ? AND tenant_id = ?
    """, (account_id, tenant_id)).fetchone()
    
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
    
    account = db.session.execute("""
        SELECT 
            id, account_name, account_type, bank_name, account_number,
            ifsc_code, branch, current_balance, is_active, is_default, description
        FROM bank_accounts
        WHERE id = ? AND tenant_id = ?
    """, (account_id, tenant_id)).fetchone()
    
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

