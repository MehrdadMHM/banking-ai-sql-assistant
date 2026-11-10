from semantic_validator import validate_semantics

question = "Show the top 5 customers by total amount in EUR"

sql = """
SELECT customer_id, SUM(amount) AS total_amount
FROM analytics.fact_transactions
WHERE currency = 'EUR'
GROUP BY customer_id
ORDER BY total_amount DESC
LIMIT 5;
"""

result = validate_semantics(question, sql)
print(result)