import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

conn = psycopg.connect(
    host=os.getenv("PGHOST"),
    port=os.getenv("PGPORT"),
    dbname=os.getenv("PGDATABASE"),
    user=os.getenv("PGUSER"),
    password=os.getenv("PGPASSWORD")
)

print("Connected to PostgreSQL!")

# Step 1: Create a cursor
cursor = conn.cursor()

# Step 2: Execute SQL
cursor.execute("""
    SELECT *
    FROM analytics.dim_customers
    LIMIT 5;
""")

# Step 3: Fetch results
rows = cursor.fetchall()

# Step 4: Display results
for row in rows:
    print(row)

# Step 5: Close resources
cursor.close()
conn.close()