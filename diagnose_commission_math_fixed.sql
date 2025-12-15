-- Fixed for PostgreSQL (ROUND needs CAST)

-- 1. Get invoice totals and their commission calculations
SELECT 
    i.id,
    i.invoice_number,
    i.total_amount as invoice_total,
    ic.commission_percentage,
    ic.commission_amount as stored_commission,
    ROUND(CAST(i.total_amount * ic.commission_percentage / 100 AS numeric), 2) as calculated_commission,
    ROUND(CAST(ic.commission_amount - (i.total_amount * ic.commission_percentage / 100) AS numeric), 2) as difference
FROM invoices i
JOIN invoice_commissions ic ON ic.invoice_id = i.id
WHERE i.tenant_id = 21
ORDER BY i.id;

-- 2. Get return amounts and their commission reversals
SELECT 
    r.id,
    r.return_number,
    r.invoice_id,
    r.total_amount as return_total,
    ic.commission_percentage,
    ROUND(CAST(r.total_amount * ic.commission_percentage / 100 AS numeric), 2) as should_reverse,
    (SELECT SUM(credit_amount) FROM account_transactions 
     WHERE tenant_id = 21 AND reference_type = 'return' 
     AND reference_id = r.id AND transaction_type = 'commission_reversal') as actual_reversal,
    (SELECT SUM(credit_amount) FROM account_transactions 
     WHERE tenant_id = 21 AND reference_type = 'return' 
     AND reference_id = r.id AND transaction_type = 'commission_reversal') - 
    ROUND(CAST(r.total_amount * ic.commission_percentage / 100 AS numeric), 2) as reversal_diff
FROM returns r
JOIN invoice_commissions ic ON ic.invoice_id = r.invoice_id
WHERE r.tenant_id = 21
AND r.status = 'approved'
ORDER BY r.id;

-- 3. Summary of all commission transactions
SELECT 
    'Commission Earned (Invoice #1)' as item,
    29.98 as amount,
    'Should be ₹5,996 × 0.5% = ₹29.98' as note
UNION ALL
SELECT 
    'Commission Earned (Invoice #2)',
    19.99,
    'Should be ₹3,998 × 0.5% = ₹19.99'
UNION ALL
SELECT 
    'Total Commission Earned',
    49.97,
    '₹29.98 + ₹19.99'
UNION ALL
SELECT 
    'Commission Actually Paid',
    (SELECT SUM(debit_amount) FROM account_transactions 
     WHERE tenant_id = 21 AND transaction_type = 'commission_expense'),
    'From account_transactions'
UNION ALL
SELECT 
    'Commission Reversed (Returns)',
    (SELECT SUM(credit_amount) FROM account_transactions 
     WHERE tenant_id = 21 AND transaction_type = 'commission_reversal'),
    'From account_transactions'
UNION ALL
SELECT 
    'Net Commission After Returns',
    (SELECT SUM(debit_amount) FROM account_transactions 
     WHERE tenant_id = 21 AND transaction_type = 'commission_expense') -
    (SELECT SUM(credit_amount) FROM account_transactions 
     WHERE tenant_id = 21 AND transaction_type = 'commission_reversal'),
    'Paid - Reversed';

