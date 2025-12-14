-- Check commission expense and reversal values for ayushi tenant

-- 1. Commission Expense DEBITS (should be ₹29.99)
SELECT 
    'Commission Expense DEBITS' as type,
    COUNT(*) as count,
    SUM(debit_amount) as total
FROM account_transactions
WHERE tenant_id = 21
AND transaction_type = 'commission_expense';

-- 2. Commission Reversal CREDITS (should be ~₹27.50)
SELECT 
    'Commission Reversal CREDITS' as type,
    COUNT(*) as count,
    SUM(credit_amount) as total
FROM account_transactions
WHERE tenant_id = 21
AND transaction_type = 'commission_reversal';

-- 3. Commission Recoverable DEBITS (should be ~₹27.50)
SELECT 
    'Commission Recoverable DEBITS' as type,
    COUNT(*) as count,
    SUM(debit_amount) as total
FROM account_transactions
WHERE tenant_id = 21
AND transaction_type = 'commission_recoverable';

-- 4. Net Commission Expense (should be ₹2.49 or ₹2.47)
SELECT 
    'NET Commission Expense' as type,
    (SELECT COALESCE(SUM(debit_amount), 0) FROM account_transactions WHERE tenant_id = 21 AND transaction_type = 'commission_expense') -
    (SELECT COALESCE(SUM(credit_amount), 0) FROM account_transactions WHERE tenant_id = 21 AND transaction_type = 'commission_reversal') as net_amount;

-- 5. Show individual commission entries
SELECT 
    transaction_type,
    debit_amount,
    credit_amount,
    narration,
    transaction_date,
    voucher_number
FROM account_transactions
WHERE tenant_id = 21
AND transaction_type IN ('commission_expense', 'commission_reversal', 'commission_recoverable')
ORDER BY transaction_date, id;
