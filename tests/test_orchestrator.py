from sql_orchestrator import repair_with_retry

wrong_sql = """
SELECT customer_id, SUM(amount12)
FROM analytics.fact_transactions
GROUP BY customer_id;
"""

error = 'column "amount12" does not exist'

result = repair_with_retry(
    wrong_sql,
    error,
    max_attempts=3
)

print("Result:", result)