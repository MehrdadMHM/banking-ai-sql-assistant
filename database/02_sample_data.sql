-- Synthetic and deterministic banking demonstration dataset.
-- Execute only on a freshly initialized demonstration database.
-- Requires: raw tables, analytics.fact_transactions, and pgvector schema already created.
-- Do not run this script against databases containing real banking data.

BEGIN;

-- Five fictional branches.
INSERT INTO raw.branches (branch_id, branch_name, city, updated_at)
SELECT n, 'Demo Branch ' || n,
       (ARRAY['Nuremberg','Berlin','Frankfurt','Munich','Hamburg'])[n],
       TIMESTAMPTZ '2026-01-01 00:00:00+00'
FROM generate_series(1, 5) AS n;

-- One hundred fictional customers.
INSERT INTO raw.customers
    (customer_id, customer_name, customer_type, created_at, updated_at)
SELECT n, 'Demo Customer ' || LPAD(n::text, 3, '0'),
       CASE WHEN n % 10 = 0 THEN 'business' ELSE 'individual' END,
       TIMESTAMPTZ '2025-01-01 00:00:00+00' + n * INTERVAL '1 day',
       TIMESTAMPTZ '2026-01-01 00:00:00+00'
FROM generate_series(1, 100) AS n;

-- Two hundred fictional accounts, two per customer.
INSERT INTO raw.accounts
    (account_id, customer_id, branch_id, account_number, account_type,
     currency, status, opened_at, updated_at)
SELECT n, ((n - 1) % 100) + 1, ((n - 1) % 5) + 1,
       'DEMO' || LPAD(n::text, 12, '0'),
       CASE WHEN n % 2 = 0 THEN 'savings' ELSE 'checking' END,
       CASE WHEN n % 5 = 0 THEN 'USD' ELSE 'EUR' END,
       'active',
       TIMESTAMPTZ '2025-06-01 00:00:00+00' + (n % 120) * INTERVAL '1 day',
       TIMESTAMPTZ '2026-01-01 00:00:00+00'
FROM generate_series(1, 200) AS n;

-- Five thousand fictional transactions.
-- Every 200th row is deliberately above EUR 10,000 for RAG rule testing.
INSERT INTO raw.transactions
    (transaction_id, account_id, transaction_type, amount, status,
     transaction_at, updated_at)
SELECT n, ((n - 1) % 200) + 1,
       CASE WHEN n % 2 = 0 THEN 'withdrawal' ELSE 'deposit' END,
       CASE WHEN n % 200 = 1 THEN (12000 + n % 3000)::numeric(14,2)
            ELSE (20 + (n * 37 % 4980) + (n % 100) / 100.0)::numeric(14,2)
       END,
       CASE WHEN n % 20 = 3 THEN 'failed'
            WHEN n % 20 = 4 THEN 'pending'
            ELSE 'completed' END,
       TIMESTAMPTZ '2026-01-01 00:00:00+00' + n * INTERVAL '20 minutes',
       TIMESTAMPTZ '2026-01-01 00:00:00+00' + n * INTERVAL '20 minutes'
FROM generate_series(1, 5000) AS n;

-- Build the physical analytics fact table from the synthetic raw transactions.
-- signed_amount describes direction even for pending/failed transactions.
-- completed_inflow / completed_outflow are non-negative and only include completed rows.
INSERT INTO analytics.fact_transactions
    (transaction_id, account_id, customer_id, branch_id, currency,
     transaction_type, transaction_status, transaction_at, transaction_date,
     amount, signed_amount, completed_inflow, completed_outflow, updated_at)
SELECT t.transaction_id, t.account_id, a.customer_id, a.branch_id, a.currency,
       t.transaction_type, t.status, t.transaction_at,
       (t.transaction_at AT TIME ZONE 'UTC')::date,
       t.amount,
       CASE WHEN t.transaction_type = 'withdrawal' THEN -t.amount ELSE t.amount END,
       CASE WHEN t.status = 'completed' AND t.transaction_type = 'deposit'
            THEN t.amount ELSE 0 END,
       CASE WHEN t.status = 'completed' AND t.transaction_type = 'withdrawal'
            THEN t.amount ELSE 0 END,
       t.updated_at
FROM raw.transactions AS t
JOIN raw.accounts AS a ON a.account_id = t.account_id;

COMMIT;

-- Sanity check: expected row counts 5 / 100 / 200 / 5000 / 5000.
SELECT 'raw.branches' AS object, COUNT(*) AS row_count FROM raw.branches
UNION ALL SELECT 'raw.customers', COUNT(*) FROM raw.customers
UNION ALL SELECT 'raw.accounts', COUNT(*) FROM raw.accounts
UNION ALL SELECT 'raw.transactions', COUNT(*) FROM raw.transactions
UNION ALL SELECT 'analytics.fact_transactions', COUNT(*) FROM analytics.fact_transactions;

-- Demo RAG test: expected 25 high-value EUR transactions.
SELECT COUNT(*) AS high_value_eur_transactions
FROM analytics.fact_transactions
WHERE amount > 10000 AND currency = 'EUR';


