import json
import os
import re

import psycopg
import requests
import sqlglot
from dotenv import load_dotenv
from psycopg import sql
from sqlglot import exp

load_dotenv()

SCHEMA = os.getenv("PGSCHEMA", "public")
MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/chat")


def database_connection():
    return psycopg.connect(
        host=os.getenv("PGHOST", "localhost"),
        port=int(os.getenv("PGPORT", "5432")),
        dbname=os.environ["PGDATABASE"],
        user=os.environ["PGUSER"],
        password=os.environ["PGPASSWORD"],
        options="-c statement_timeout=10000",
        autocommit=False,
    )


def get_schema(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT table_name, column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = %s
            ORDER BY table_name, ordinal_position
        """, (SCHEMA,))
        rows = cur.fetchall()
    if not rows:
        raise RuntimeError(f"No visible tables in schema {SCHEMA!r}")
    return "\n".join(f"{SCHEMA}.{table}.{column}: {dtype}" for table, column, dtype in rows)


def ask_model(question, schema_text):
    system = (
        "You translate user requests into PostgreSQL read-only SELECT queries. "
        "Use only the schema described below and do not invent tables or columns. "
        "Return exactly one JSON object with a single 'sql' string field. "
        "Only one SELECT query is permitted; no DDL, DML, EXPLAIN, COPY, or CALL. "
        "Include LIMIT 100 unless a smaller limit is requested. "
        "Schema:\n" + schema_text
    )
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": question},
            ],
            "format": "json",
            "stream": False,
            "options": {"temperature": 0},
        },
        timeout=180,
    )
    response.raise_for_status()
    return json.loads(response.json()["message"]["content"])["sql"].strip()


def validate_query(statement):
    statements = sqlglot.parse(statement, read="postgres")
    if len(statements) != 1 or not isinstance(statements[0], exp.Select):
        raise ValueError("Only one SELECT statement is allowed")
    tree = statements[0]
    forbidden = (exp.Insert, exp.Update, exp.Delete, exp.Create, exp.Drop,
                 exp.Alter, exp.Command, exp.Merge, exp.Copy)
    if any(tree.find(node_type) for node_type in forbidden):
        raise ValueError("Unsafe SQL statement")
    # No SELECT INTO or locking clauses.
    if tree.args.get("into") or tree.args.get("locks"):
        raise ValueError("SELECT INTO or locking is forbidden")
    # Reject known side-effect / time-consuming functions even in SELECT.
    blocked_functions = {"pg_sleep", "dblink_exec", "lo_export", "set_config", "pg_terminate_backend"}
    for fn in tree.find_all(exp.Anonymous):
        if fn.name.lower() in blocked_functions:
            raise ValueError(f"Function {fn.name} is forbidden")
    return tree.sql(dialect="postgres")


def main():
    print(f"Local AI → PostgreSQL | model: {MODEL} | schema: {SCHEMA}")
    print("Type 'exit' to quit. SQL will be shown before execution.\n")
    with database_connection() as conn:
        conn.read_only = True
        schema_text = get_schema(conn)
        conn.rollback()
        while True:
            question = input("Question> ").strip()
            if question.lower() in {"exit", "quit"}:
                break
            if not question:
                continue
            try:
                candidate = ask_model(question, schema_text)
                safe_sql = validate_query(candidate)
                print("\nGenerated SQL:\n", safe_sql)
                if input("Run this read-only query? [y/N] ").strip().lower() != "y":
                    print("Skipped.\n")
                    continue
                # read-only mode also blocks writes if the model makes a mistake.
                with conn.cursor() as cur:
                    cur.execute(sql.SQL("SET TRANSACTION READ ONLY"))
                    cur.execute(safe_sql)
                    columns = [c.name for c in cur.description]
                    rows = cur.fetchmany(100)
                print("Columns:", columns)
                for row in rows:
                    print(row)
                print(f"\nDisplayed {len(rows)} row(s), maximum 100.\n")
            except (Exception, KeyboardInterrupt) as exc:
                print(f"Error: {exc}\n")
            finally:
                conn.rollback()


if __name__ == "__main__":
    main()
