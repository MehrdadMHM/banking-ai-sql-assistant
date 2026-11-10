
from validation_engine import validate_generated_sql


question = (
    "Show top 5 customers "
    "by total transaction amount in EUR"
)

wrong_sql = """
SELECT customer_id,
       SUM(signed_amount) AS total_amount
FROM analytics.fact_transactions
WHERE currency = 'EUR'
GROUP BY customer_id
ORDER BY total_amount DESC
LIMIT 5;
"""

result = validate_generated_sql(question, wrong_sql)

print("Validation result:", result)

assert result["valid"] is False
assert (
    "Incorrect aggregation column: expected SUM(amount)"
    in result["errors"]
)

print("Validation engine test PASSED")
