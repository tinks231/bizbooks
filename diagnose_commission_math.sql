-- Detailed commission math analysis for Ayushi tenant

-- 1. Get invoice totals and their commission calculations
SELECT 
    i.id,
    i.invoice_number,
    i.total_amount as invoice_total,
    ic.commission_percentage,
    ic.commission_amount as stored_commission,
    ROUND(i.total_amount * ic.commission_percentage / 100, 2) as calculated_commission,
    ic.commission_amount - ROUND(i.total_amount * ic.commission_percentage / 100, 2) as difference
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
    ROUND(r.total_amount * ic.commission_percentage / 100, 2) as should_reverse,
    (SELECT SUM(credit_amount) FROM account_transactions 
     WHERE tenant_id = 21 AND reference_type = 'return' 
     AND reference_id = r.id AND transaction_type = 'commission_reversal') as actual_reversal
FROM returns r
JOIN invoice_commissions ic ON ic.invoice_id = r.invoice_id
WHERE r.tenant_id = 21
AND r.status = 'approved'
ORDER BY r.id;

-- 3. Show the math breakdown
SELECT 
    '=== INVOICE #1 ===' as calculation,
    5996.00 as invoice_total,
    0.5 as percentage,
    5996.00 * 0.5 / 100 as exact_commission,
    ROUND(5996.00 * 0.5 / 100, 2) as rounded_commission
UNION ALL
SELECT 
    '=== INVOICE #2 ===',
    3998.00,
    0.5,
    3998.00 * 0.5 / 100,
    ROUND(3998.00 * 0.5 / 100, 2);

