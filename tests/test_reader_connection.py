
import os
import psycopg

from dotenv import load_dotenv

load_dotenv()


def test_reader_connection():
    with psycopg.connect(
        host=os.getenv("PGHOST"),
        port=os.getenv("PGPORT"),
        dbname=os.getenv("PGDATABASE"),
        user=os.getenv("PG_READER_USER"),
        password=os.getenv("PG_READER_PASSWORD"),
        connect_timeout=5
    ) as conn:

        # Set transaction to read-only
        conn.execute("SET TRANSACTION READ ONLY")
        conn.execute("SET LOCAL statement_timeout = '5s'")

        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    current_user,
                    current_database(),
                    COUNT(*)
                FROM analytics.fact_transactions
            """)

            result = cur.fetchone()

            print("Connected user:", result[0])
            print("Database:", result[1])
            print("Transaction count:", result[2])

            assert result[0] == "bank_ai_reader"

        # End test transaction without committing
        conn.rollback()


if __name__ == "__main__":
    test_reader_connection()
