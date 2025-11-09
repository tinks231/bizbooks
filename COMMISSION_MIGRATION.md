# Commission Tracking - Database Migration

## Migration: Add Commission Tracking Tables

**Purpose:** Add support for commission tracking on sales invoices.

**What it does:**
1. Creates `commission_agents` table (tracks sales agents)
2. Creates `invoice_commissions` table (links invoices to agents with commission amounts)
3. Adds indexes for performance

**Route:** `/migrate/add-commission-tables`

**Impact:** **SAFE** - Only creates new tables, no modifications to existing data

---

## Steps to Run Migration:

### 1. **Backup Database (Recommended)**
```bash
# For PostgreSQL
pg_dump your_database > backup_before_commission.sql

# For SQLite
cp instance/attendance.db instance/attendance_backup.db
```

### 2. **Run Migration**
Navigate to: `https://your-domain.bizbooks.co.in/migrate/add-commission-tables`

### 3. **Expected Output:**
```
✅ Migration successful!
- commission_agents table created
- invoice_commissions table created
```

### 4. **Verify Tables Created:**
```sql
-- Check if tables exist
SELECT * FROM commission_agents LIMIT 1;
SELECT * FROM invoice_commissions LIMIT 1;
```

---

## What Gets Created:

### Table: `commission_agents`
| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| tenant_id | Integer | Tenant reference |
| name | String(200) | Agent name |
| code | String(50) | Unique agent code |
| phone | String(20) | Contact phone |
| email | String(120) | Contact email |
| default_commission_percentage | Float | Default commission % (e.g., 1.0 = 1%) |
| employee_id | Integer | Link to employee (NULL for external agents) |
| agent_type | String(20) | 'employee' or 'external' |
| is_active | Boolean | Active status |
| created_at | DateTime | Created timestamp |
| updated_at | DateTime | Updated timestamp |
| created_by | Integer | User who created |

### Table: `invoice_commissions`
| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| tenant_id | Integer | Tenant reference |
| invoice_id | Integer | Invoice reference |
| agent_id | Integer | Agent reference |
| agent_name | String(200) | Agent name (denormalized) |
| agent_code | String(50) | Agent code (denormalized) |
| commission_percentage | Float | % used for this invoice |
| invoice_amount | Float | Total invoice amount |
| commission_amount | Float | Calculated commission |
| is_paid | Boolean | Payment status |
| paid_date | Date | Date commission was paid |
| payment_notes | Text | Payment notes |
| created_at | DateTime | Created timestamp |
| updated_at | DateTime | Updated timestamp |

---

## Post-Migration Steps:

1. **Enable Feature** (Optional - Feature is optional per tenant)
2. **Create Commission Agents** (Admin > Parties > Commission Agents)
3. **Link Employees** (Edit employee, check "Commission Enabled")
4. **Start Tracking** (Commission section will appear on invoice create)

---

## Rollback (If Needed):

```sql
-- Drop tables in reverse order (respects foreign keys)
DROP TABLE IF EXISTS invoice_commissions;
DROP TABLE IF EXISTS commission_agents;
```

**Note:** This will delete all commission data. Only do this if you haven't started using the feature yet!

---

## Troubleshooting:

**Issue:** Migration fails with "table already exists"
**Solution:** Tables are already created, no action needed

**Issue:** Foreign key constraint error
**Solution:** Ensure `employees` and `invoices` tables exist

**Issue:** Permission denied
**Solution:** Ensure database user has CREATE TABLE permissions

---

## Feature Usage:

Once migrated, the feature will be available at:
- **Admin > Parties > Commission Agents** (Manage agents)
- **Admin > Sales > Create Invoice** (Assign agent & commission)
- **Admin > Reports > Commission Report** (View earnings)

---

**Created:** 2025-11-09  
**Status:** Ready for deployment

