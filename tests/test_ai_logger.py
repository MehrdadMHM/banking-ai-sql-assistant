
from ai_logger import log_attempt

attempt_id = log_attempt(
    request_id=3,
    attempt_number=2,
    attempt_type="REPAIR",
    generated_sql="""
        SELECT customer_id, SUM(amount)
        FROM analytics.fact_transactions
        WHERE currency = 'EUR'
        GROUP BY customer_id
    """,
    validation_status="PASSED",
    validation_errors=None
)

print("Created attempt:", attempt_id)
