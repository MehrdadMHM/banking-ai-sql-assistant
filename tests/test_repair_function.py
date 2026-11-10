from sql_repair import repair_sql

wrong_sql = """
SELECT customer_id, SUM(amount12)
FROM analytics.fact_transactions
GROUP BY customer_id;
"""

postgres_error = 'column "amount12" does not exist'

corrected_sql = repair_sql(wrong_sql, postgres_error)

print("Corrected SQL:")
print(corrected_sql)