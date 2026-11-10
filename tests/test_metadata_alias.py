
from metadata_provider import get_table_columns
from postgres_validator import validate_postgres_metadata


metadata = get_table_columns()

test_cases = [
    {
        "name": "Valid ORDER BY alias",
        "sql": """
            SELECT
                SUM(amount) AS total_amount
            FROM analytics.fact_transactions
            ORDER BY total_amount DESC;
        """,
        "expected": True
    },
    {
        "name": "Invalid ORDER BY alias",
        "sql": """
            SELECT
                SUM(amount) AS total_amount
            FROM analytics.fact_transactions
            ORDER BY unknown_alias DESC;
        """,
        "expected": False
    },
    {
        "name": "Valid GROUP BY real column",
        "sql": """
            SELECT
                customer_id,
                SUM(amount) AS total_amount
            FROM analytics.fact_transactions
            GROUP BY customer_id
            ORDER BY total_amount DESC;
        """,
        "expected": True
    },
    {
        "name": "Invalid WHERE alias",
        "sql": """
            SELECT
                SUM(amount) AS total_amount
            FROM analytics.fact_transactions
            WHERE total_amount > 100;
        """,
        "expected": False
    }
]


for index, test in enumerate(test_cases, 1):

    result = validate_postgres_metadata(
        test["sql"],
        metadata
    )

    passed = result["valid"] == test["expected"]

    print(
        f"Test {index}: {test['name']} "
        f"=> {'PASSED' if passed else 'FAILED'}"
    )

    if not passed:
        print("Actual result:", result)

    assert passed, (
        f"Test {index} failed: {result}"
    )


print("\nAll metadata alias tests PASSED")
