-- Check the latest return's accounting entries
SELECT 
    'Latest Return Accounting' as section,
    at.transaction_type,
    at.debit_amount,
    at.credit_amount,
    at.reference_id as return_id
FROM account_transactions at
JOIN returns r ON at.reference_id = r.id AND at.reference_type = 'return'
WHERE at.tenant_id = 21
ORDER BY r.id DESC, at.transaction_type;

-- Check total debits and credits
SELECT 
    'Totals' as section,
    SUM(debit_amount) as total_debits,
    SUM(credit_amount) as total_credits,
    SUM(debit_amount) - SUM(credit_amount) as difference
FROM account_transactions
WHERE tenant_id = 21
AND reference_type = 'return';
