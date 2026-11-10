from sql_repair import repair_sql
from sql_validator import check_sql_safety

wrong_sql = """
SELECT customer_id, SUM(amount12)
FROM analytics.fact_transactions
GROUP BY customer_id;
"""

error = 'column "amount12" does not exist'

# Step 1: Repair SQL
corrected_sql = repair_sql(wrong_sql, error)

# Step 2: Check SQL structure
result = check_sql_safety(corrected_sql)

# Step 3: Display result
if result["safe"]:
    print("Repaired SQL passed initial checks")
    print(corrected_sql)
else:
    print("Rejected:", result["error"])