
import os
import json
import psycopg
from dotenv import load_dotenv

load_dotenv()


def get_schema_context():

    # Read database tables and columns
    with psycopg.connect(
        host=os.getenv("PGHOST"),
        port=os.getenv("PGPORT"),
        dbname=os.getenv("PGDATABASE"),
        user=os.getenv("PGUSER"),
        password=os.getenv("PGPASSWORD")
    ) as conn:

        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT table_name, column_name, data_type
                FROM information_schema.columns
                WHERE table_schema = %s
                ORDER BY table_name, ordinal_position
            """, ("analytics",))

            rows = cursor.fetchall()

    schema_text = "\n".join(
        f"analytics.{table}.{column}: {dtype}"
        for table, column, dtype in rows
    )

    # Read logical relationships and business rules
    with open(
        "schema_metadata.json",
        "r",
        encoding="utf-8"
    ) as file:
        metadata = json.load(file)

    relationships = json.dumps(
        metadata.get("relationships", []),
        indent=2
    )

    business_rules = json.dumps(
        metadata.get("business_rules", {}),
        indent=2
    )

    # Build shared metadata context
    schema_context = f"""
Database schema:
{schema_text}

Relationships:
{relationships}

Business rules:
{business_rules}
"""

    return schema_context
