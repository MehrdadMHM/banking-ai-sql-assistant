import requests
from sql_validator import check_sql_safety

wrong_sql = """
SELECT
    customer_id,
    SUM(amount) AS total_amount
FROM analytics.fact_transactions
GROUP BY customer_id;
"""

postgres_error = """
column "amount12" does not exist.
Perhaps you meant fact_transactions.amount.
"""

prompt = f"""
Correct this PostgreSQL query.

Original SQL:
{wrong_sql}

PostgreSQL error:
{postgres_error}

Return only the corrected SQL.
"""

payload = {
    "model": "bank-sql-qwen",
    "prompt": prompt,
    "stream": False
}
url = "http://localhost:11434/api/generate"

response = requests.post(
    url,
    json=payload,
    timeout=180
)

response.raise_for_status()


# Step 2: Extract generated SQL
data = response.json()

corrected_sql = data["response"].strip()


# Step 3: Remove Markdown formatting
if corrected_sql.startswith("```sql"):
    corrected_sql = corrected_sql[6:]

if corrected_sql.endswith("```"):
    corrected_sql = corrected_sql[:-3]

corrected_sql = corrected_sql.strip()


# Step 4: Display corrected SQL
print("Corrected SQL:")
print(corrected_sql)


# Step 5: Check SQL structure
result = check_sql_safety(corrected_sql)

print("Safety Check:", result)