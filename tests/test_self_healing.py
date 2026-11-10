
from sql_pipeline import run_sql_pipeline
from unittest.mock import patch


wrong_sql = """
SELECT
    customer_id,
    SUM(amount) AS total_amount
FROM analytics.fact_transactions
GROUP BY customer_id
ORDER BY total_amount DESC
LIMIT 5;
"""

question = (
    "Show the top 5 customers "
    "by total transaction amount in EUR"
)

# Force the generator to return incorrect SQL
with patch("sql_pipeline.generate_sql", return_value=wrong_sql):

    result = run_sql_pipeline(question)

print("\nFinal result:")
print(result)
