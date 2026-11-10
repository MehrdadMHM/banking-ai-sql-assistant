
from postgres_validator import validate_postgres_metadata


metadata = {
    "fact_transactions": [
        "transaction_id",
        "customer_id",
        "amount",
        "signed_amount",
        "currency",
        "transaction_status"
    ],
    "dim_customers": [
        "customer_id",
        "customer_name"
    ]
}


test_cases = [
    (
        "Valid aggregation",
        """
        SELECT customer_id, SUM(amount)
        FROM analytics.fact_transactions
        GROUP BY customer_id;
        """,
        True
    ),
    (
        "Invalid column",
        """
        SELECT customer_id, SUM(amount12)
        FROM analytics.fact_transactions
        GROUP BY customer_id;
        """,
        False
    ),
    (
        "Invalid table",
        """
        SELECT customer_id
        FROM analytics.unknown_table;
        """,
        False
    ),
    (
        "Valid join",
        """
        SELECT c.customer_name, SUM(t.amount)
        FROM analytics.fact_transactions t
        JOIN analytics.dim_customers c
          ON t.customer_id = c.customer_id
        GROUP BY c.customer_name;
        """,
        True
    )
]


for name, sql, expected in test_cases:
    result = validate_postgres_metadata(sql, metadata)

    print(name, result)

    assert result["valid"] == expected, (
        f"{name} failed: {result}"
    )


print("\nAll PostgreSQL metadata tests PASSED")
