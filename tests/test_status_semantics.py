
from semantic_validator import (
    has_completed_filter,
    validate_semantics
)

question = "Show total transaction amount in EUR"

sql = """
SELECT SUM(amount)
FROM analytics.fact_transactions
WHERE currency = 'EUR'
AND transaction_status = 'completed';
"""

# Test 1: Check AST detection
detected = has_completed_filter(sql)
print("Completed filter detected:", detected)

# Test 2: Check semantic validation
result = validate_semantics(question, sql)
print("Validation result:", result)

assert detected is True, "AST did not detect completed filter"
assert result["valid"] is False
assert "Unexpected completed transaction filter" in result["errors"]

print("All tests PASSED")
