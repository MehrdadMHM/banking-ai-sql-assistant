from sql_validator import check_sql_safety

query = """
SELECT
    c.customer_id,
    c.customer_name,
    SUM(t.amount) AS total_amount
FROM analytics.dim_customers c
JOIN raw.transactions t
    ON c.customer_id = t.customer_id
GROUP BY c.customer_id, c.customer_name
LIMIT 5;
"""

result = check_sql_safety(query)

print(result)