import os
import psycopg
from dotenv import load_dotenv
from sql_validator import validate_sql

load_dotenv()

conn = psycopg.connect(
    host=os.getenv("PGHOST"),
    port=os.getenv("PGPORT"),
    dbname=os.getenv("PGDATABASE"),
    user=os.getenv("PGUSER"),
    password=os.getenv("PGPASSWORD")
)

conn.read_only = True

query = """
SELECT
    customer_id,
    SUM(amount12) AS total_amount
FROM analytics.fact_transactions
GROUP BY customer_id
"""

try:
    with conn.cursor() as cursor:
        result = validate_sql(cursor, query)

        print("Valid:", result["valid"])
        print("Error:", result["error"])

        if result["valid"]:
            for line in result["plan"]:
                print(line)
finally:
    conn.close()