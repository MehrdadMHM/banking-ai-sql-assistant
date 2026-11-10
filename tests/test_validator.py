import os
import psycopg
from dotenv import load_dotenv


def validate_sql(cursor, query):
    try:
        cursor.execute("EXPLAIN " + query)
        return {
            "valid": True,
            "error": None
        }

    except psycopg.Error as error:
        return {
            "valid": False,
            "error": str(error)
        }
    
load_dotenv()
conn = psycopg.connect(
    host=os.getenv("PGHOST"),
    port=os.getenv("PGPORT"),
    dbname=os.getenv("PGDATABASE"),
    user=os.getenv("PGUSER"),
    password=os.getenv("PGPASSWORD")
)

query = """
SELECT
    customer_id,
    SUM(amount12)
FROM analytics.fact_transactions
GROUP BY customer_id
"""
cursor = conn.cursor()
cursor.execute("set transaction read only")
cursor.execute("SET statement_timeout ='5s'")
try:
    result = validate_sql(cursor, query)
    if result["valid"]:
        plan = cursor.fetchall()
        for row in plan:
            print(row[0])
    else:
        conn.rollback()
        print("SQL Validation Failed:")
        print(result["error"])
except psycopg.Error as error:
    print("SQL Validation Failed:")
    print(error)
finally:
    cursor.close()
    conn.close()



