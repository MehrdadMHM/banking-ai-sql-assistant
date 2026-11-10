
from sql_orchestrator import repair_with_retry
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

result = repair_with_retry(
    wrong_sql,
    postgres_error,
    max_attempts=3
)

if result["passed_initial_checks"]:
    corrected_sql = result["sql"]

    safety = check_sql_safety(corrected_sql)

    print("Corrected SQL:")
    print(corrected_sql)
    print("AST checks passed:", safety["safe"])
    print("PostgreSQL validation: NOT RUN")

else:
    print("Repair failed:", result["error"])
