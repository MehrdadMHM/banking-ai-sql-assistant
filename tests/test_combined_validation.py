
from sql_validator import check_sql_safety
from semantic_validator import validate_semantics
from business_metric_validator import validate_business_metric


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

safety = check_sql_safety(wrong_sql)
semantic = validate_semantics(question, wrong_sql)
business = validate_business_metric(question, wrong_sql)

print("AST:", safety)
print("Semantic:", semantic)
print("Business Metric:", business)

assert safety["safe"] is True
assert semantic["valid"] is True
assert business["valid"] is False

print("\nCombined validation test PASSED")
