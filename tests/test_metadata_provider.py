
from metadata_provider import get_table_columns
from postgres_validator import validate_postgres_metadata


# Step 1: Load real metadata
metadata = get_table_columns()

print("Metadata loaded successfully")

for table, columns in metadata.items():
    print(f"{table}: {len(columns)} columns")


# Step 2: Valid SQL
valid_sql = """
SELECT
    c.customer_name,
    SUM(t.amount) AS total_amount
FROM analytics.fact_transactions t
JOIN analytics.dim_customers c
    ON t.customer_id = c.customer_id
GROUP BY c.customer_name;
"""

# Step 3: Invalid SQL
invalid_sql = """
SELECT
    SUM(t.amount12)
FROM analytics.fact_transactions t;
"""


# Step 4: Validate both queries
valid_result = validate_postgres_metadata(
    valid_sql,
    metadata
)

invalid_result = validate_postgres_metadata(
    invalid_sql,
    metadata
)

print("\nValid SQL:", valid_result)
print("Invalid SQL:", invalid_result)


# Step 5: Assertions
assert valid_result["valid"] is True

assert invalid_result["valid"] is False

assert any(
    "amount12" in error
    for error in invalid_result["errors"]
)

print("\nReal metadata validation PASSED")
