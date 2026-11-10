
import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

# Trusted SQL - manually written for testing
query = """
SELECT customer_id, SUM(amount12)
FROM analytics.fact_transactions
GROUP BY customer_id;
"""

try:
    with psycopg.connect(
        host=os.getenv("PGHOST"),
        port=os.getenv("PGPORT"),
        dbname=os.getenv("PGDATABASE"),
        user=os.getenv("PGUSER"),
        password=os.getenv("PGPASSWORD")
    ) as conn:

        # Read-only transaction
        conn.read_only = True

        with conn.cursor() as cursor:

            cursor.execute(
                "SET LOCAL statement_timeout = '5s'"
            )

            cursor.execute("EXPLAIN " + query)

            for row in cursor.fetchall():
                print(row[0])

            print("SQL is valid")

except psycopg.Error as error:
    print("PostgreSQL validation failed:")
    print(error)
