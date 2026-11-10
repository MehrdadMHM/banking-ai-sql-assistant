
from unittest.mock import patch
from sql_orchestrator import repair_with_retry


def fake_repair(wrong_sql, error):
    return "DELETE FROM analytics.fact_transactions;"


wrong_sql = """
SELECT customer_id, SUM(amount12)
FROM analytics.fact_transactions
GROUP BY customer_id;
"""

error = 'column "amount12" does not exist'

with patch("sql_orchestrator.repair_sql", side_effect=fake_repair):
    result = repair_with_retry(
        wrong_sql,
        error,
        max_attempts=3
    )

print("Result:", result)
