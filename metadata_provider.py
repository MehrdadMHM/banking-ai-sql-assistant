
import os
import psycopg

from dotenv import load_dotenv

load_dotenv()


def get_table_columns(schema="analytics"):
    """
    Read real table and view columns from PostgreSQL.
    Only a fixed, parameterized metadata query is executed.
    """

    metadata = {}

    with psycopg.connect(
        host=os.getenv("PGHOST"),
        port=os.getenv("PGPORT"),
        dbname=os.getenv("PGDATABASE"),
        user=os.getenv("PGUSER"),
        password=os.getenv("PGPASSWORD"),
        connect_timeout=5
    ) as conn:

        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    table_name,
                    column_name
                FROM information_schema.columns
                WHERE table_schema = %s
                ORDER BY table_name, ordinal_position
                """,
                (schema,)
            )

            for table_name, column_name in cur.fetchall():
                metadata.setdefault(
                    table_name, []
                ).append(column_name)

    if not metadata:
        raise ValueError(
            f"No columns found for schema: {schema}"
        )

    return metadata
