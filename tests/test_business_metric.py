
from business_metric_validator import validate_business_metric


test_cases = [
    (
        "Show top 5 customers by total transaction amount in EUR",
        """
        SELECT
    customer_id,
    SUM(amount) AS gross_amount,
    SUM(signed_amount) AS net_amount
FROM analytics.fact_transactions
GROUP BY customer_id;;
        """,
        True
    ),
    (
        "Show top 5 customers by total transaction amount in EUR",
        """
        SELECT customer_id, SUM(signed_amount)
        FROM analytics.fact_transactions
        WHERE currency = 'EUR'
        GROUP BY customer_id
        ORDER BY SUM(signed_amount) DESC
        LIMIT 5;
        """,
        False
    ),
    (
        "Show net transaction flow by customer",
        """
        SELECT customer_id, SUM(signed_amount)
        FROM analytics.fact_transactions
        GROUP BY customer_id;
        """,
        True
    ),
    (
        "Show net transaction flow by customer",
        """
        SELECT customer_id, SUM(amount)
        FROM analytics.fact_transactions
        GROUP BY customer_id;
        """,
        False
    )
]


for index, (question, sql, expected) in enumerate(test_cases, 1):
    result = validate_business_metric(question, sql)

    print(
        f"Test {index}: "
        f"expected={expected}, "
        f"actual={result['valid']}"
    )

    assert result["valid"] == expected, (
        f"Test {index} failed: {result}"
    )

print("\nAll business metric tests PASSED")
