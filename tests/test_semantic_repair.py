
from schema_context import get_schema_context
from sql_orchestrator import repair_with_retry
from ai_logger import create_request

question = (
    "Show the top 5 customers "
    "by total transaction amount in EUR"
    
)
request_id = create_request(
    question,
    "bank-sql-qwen"
)

wrong_sql = """
SELECT customer_id, SUM(amount)
FROM analytics.fact_transactions
ORDER BY total_amount ASC
LIMIT 10;
"""

error = "Missing currency filter: EUR"

# Load shared database metadata
schema_context = get_schema_context()

# Repair SQL using metadata
result = repair_with_retry(
    wrong_sql,
    error,
    question=question,
    max_attempts=3,
    schema_context=schema_context,
    request_id=request_id
)

print("\nFinal result:")
print(result)
