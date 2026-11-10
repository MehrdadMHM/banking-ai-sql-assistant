import os
import psycopg
from dotenv import load_dotenv
import requests
from pglast import parse_sql, ast
from sql_validator import check_sql_safety, validate_sql
import json




load_dotenv()

conn = psycopg.connect(
    host=os.getenv("PGHOST"),
    port=os.getenv("PGPORT"),
    dbname=os.getenv("PGDATABASE"),
    user=os.getenv("PGUSER"),       
    password=os.getenv("PGPASSWORD")

)
url = "http://localhost:11434/api/generate"

cursor = conn.cursor()
sql = """
SELECT table_name, column_name, data_type
FROM information_schema.columns
WHERE table_schema = %s
ORDER BY table_name, ordinal_position;
"""
cursor.execute(sql, ("analytics",))
rows = cursor.fetchall()

schema_text = ""

for table_name, column_name, data_type in rows:
    schema_text += f"analytics.{table_name}.{column_name}: {data_type}\n"

#print(schema_text)

question = input("Ask your database: ").strip()

if not question:
    print("Error: Question cannot be empty.")
    raise SystemExit(1)

import json

with open("schema_metadata.json", "r", encoding="utf-8") as f:
    metadata = json.load(f)

relationships_text = json.dumps(
    metadata["relationships"],
    indent=2
)

business_rules_text = json.dumps(
    metadata["business_rules"],
    indent=2
)

prompt = f"""
Database schema:
{schema_text}

Relationships:
{relationships_text}

Business rules:
{business_rules_text}

User question:
{question}
"""
url = "http://localhost:11434/api/generate"



payload = {
    "model": "bank-sql-qwen",
    "prompt": prompt,
    "stream": False,
    "options": {
        "temperature": 0.1,
        "num_predict": 300
    }
}
print("PROMPT SENT TO QWEN:")
print(prompt)
response = requests.post(url, json=payload, timeout=180)
response.raise_for_status()

data = response.json()



generated_sql = data["response"].strip()

if generated_sql.startswith("```sql"):
    generated_sql = generated_sql[6:]

if generated_sql.endswith("```"):
    generated_sql = generated_sql[:-3]

generated_sql = generated_sql.strip()

print("\nClean SQL:")
print(generated_sql)
safety_result = check_sql_safety(generated_sql)

if safety_result["safe"]:
    print("SQL Safety Check Passed")
else:
    print("SQL Rejected:", safety_result["error"])
    
try:
    statements = parse_sql(generated_sql)

    if len(statements) != 1:
        print("Rejected: Multiple SQL statements")

    elif isinstance(statements[0].stmt, ast.SelectStmt):
        print("Accepted: SELECT statement")

    else:
        print("Rejected: Only SELECT is allowed")

except Exception as error:
    print("SQL Parsing Failed:", error)

cursor.close()
conn.close()