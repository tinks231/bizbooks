-- Check the actual return amount stored for RET-202512-0004
SELECT 
    id,
    return_number,
    invoice_id,
    total_amount as return_total,
    taxable_amount,
    cgst_amount,
    sgst_amount,
    igst_amount,
    taxable_amount + COALESCE(cgst_amount, 0) + COALESCE(sgst_amount, 0) + COALESCE(igst_amount, 0) as calculated_total
FROM returns
WHERE tenant_id = 21
AND return_number = 'RET-202512-0004';

-- Check what commission was calculated
SELECT 
    debit_amount as commission_reversed,
    debit_amount / 0.005 as implied_return_amount,
    narration
FROM account_transactions
WHERE tenant_id = 21
AND voucher_number = 'RET-202512-0004'
AND transaction_type = 'commission_recoverable';
