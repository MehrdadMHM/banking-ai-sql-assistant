
from metadata_provider import get_table_columns
from validation_engine import validate_generated_sql


metadata = get_table_columns()

question = "Show total transaction amount in EUR"

wrong_sql = """
SELECT SUM(amount12)
FROM analytics.fact_transactions
WHERE currency = 'EUR';
"""

result = validate_generated_sql(
    question,
    wrong_sql,
    metadata=metadata
)

print("Validation result:", result)

assert result["valid"] is False
assert any(
    "amount12" in error
    for error in result["errors"]
)

print("Unified metadata validation PASSED")
