
from business_metric_validator import validate_business_metric


test_cases = [
    {
        "name": "Gross with table alias",
        "question": "Show total transaction amount",
        "sql": """
            SELECT SUM(ft.amount)
            FROM analytics.fact_transactions ft;
        """,
        "expected": True
    },
    {
        "name": "Net with table alias",
        "question": "Show net transaction flow",
        "sql": """
            SELECT SUM(ft.signed_amount)
            FROM analytics.fact_transactions ft;
        """,
        "expected": True
    },
    {
        "name": "Gross using wrong column",
        "question": "Show gross transaction volume",
        "sql": """
            SELECT SUM(ft.signed_amount)
            FROM analytics.fact_transactions ft;
        """,
        "expected": False
    },
    {
        "name": "Net using wrong column",
        "question": "Show net transaction flow",
        "sql": """
            SELECT SUM(ft.amount)
            FROM analytics.fact_transactions ft;
        """,
        "expected": False
    },
    {
        "name": "Gross with both metrics",
        "question": "Show total transaction amount",
        "sql": """
            SELECT
                SUM(amount) AS gross_amount,
                SUM(signed_amount) AS net_amount
            FROM analytics.fact_transactions;
        """,
        "expected": True
    }
]


failures = []

for i, test in enumerate(test_cases, start=1):
    result = validate_business_metric(
        test["question"],
        test["sql"]
    )

    passed = result["valid"] == test["expected"]

    print(
        f"Test {i}: {test['name']} "
        f"=> {'PASSED' if passed else 'FAILED'}"
    )

    if not passed:
        failures.append({
            "test": test["name"],
            "result": result
        })


print(f"\nTests passed: {len(test_cases) - len(failures)}")
print(f"Tests failed: {len(failures)}")

assert not failures, f"Failed tests: {failures}"

print("\nAll edge-case tests PASSED")
