
from unittest.mock import patch
from sql_pipeline import run_sql_pipeline


question = (
    "Show top 5 customers "
    "by total transaction amount in EUR"
)

# Intentionally incorrect SQL
wrong_sql = """
SELECT
    customer_id,
    SUM(signed_amount) AS total_amount
FROM analytics.fact_transactions
GROUP BY customer_id
ORDER BY total_amount DESC
LIMIT 5;
"""

# Simulate Qwen returning incorrect SQL every time
with patch(
    "sql_pipeline.generate_sql",
    return_value=wrong_sql
), patch(
    "sql_orchestrator.repair_sql",
    return_value=wrong_sql
) as mocked_repair:

    result = run_sql_pipeline(question)

    # Verify exactly 3 repair attempts
    assert mocked_repair.call_count == 3


print("\nFinal result:")
print(result)

# Verify final pipeline result
assert result["status"] == "FAILED"
assert result["sql"] is None
assert result["repair_attempts"] == 3

print("\nRetry failure test PASSED")
