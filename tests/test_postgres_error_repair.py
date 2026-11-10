
from sql_repair import repair_sql
from sql_validator import check_sql_safety

wrong_sql = """
SELECT customer_id, SUM(amount12)
FROM analytics.fact_transactions
GROUP BY customer_id;
"""

postgres_error = """
column "amount12" does not exist
HINT: Perhaps you meant to reference
the column "fact_transactions.amount".
"""

# Repair using Qwen
corrected_sql = repair_sql(wrong_sql, postgres_error)

print("Corrected SQL:")
print(corrected_sql)

# Initial structural safety check
result = check_sql_safety(corrected_sql)

print("Passed initial checks:", result["safe"])
print("Error:", result["error"])
