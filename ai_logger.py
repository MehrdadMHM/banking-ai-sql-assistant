
import os
import psycopg
from dotenv import load_dotenv

load_dotenv()


# --------------------------------------------------
# Function 1: Create a new AI request
# --------------------------------------------------

def create_request(question, model_name):
    """
    Create a new AI request in PostgreSQL.

    Returns:
        int: The newly created request_id
    """

    with psycopg.connect(
        host=os.getenv("PGHOST"),
        port=os.getenv("PGPORT"),
        dbname=os.getenv("PGDATABASE"),
        user=os.getenv("PGUSER"),
        password=os.getenv("PGPASSWORD")
    ) as conn:

        with conn.cursor() as cur:

            cur.execute(
                """
                INSERT INTO ai_logs.ai_requests (
                    user_question,
                    model_name
                )
                VALUES (%s, %s)
                RETURNING request_id
                """,
                (question, model_name)
            )

            request_id = cur.fetchone()[0]

    return request_id


# --------------------------------------------------
# Function 2: Log a SQL generation or repair attempt
# --------------------------------------------------

def log_attempt(
    request_id,
    attempt_number,
    attempt_type,
    generated_sql,
    validation_status,
    validation_errors=None
):
    """
    Save one AI SQL attempt in PostgreSQL.

    attempt_type:
        GENERATION or REPAIR

    validation_status:
        PENDING, PASSED or FAILED

    Returns:
        int: The newly created attempt_id
    """

    with psycopg.connect(
        host=os.getenv("PGHOST"),
        port=os.getenv("PGPORT"),
        dbname=os.getenv("PGDATABASE"),
        user=os.getenv("PGUSER"),
        password=os.getenv("PGPASSWORD")
    ) as conn:

        with conn.cursor() as cur:

            cur.execute(
                """
                INSERT INTO ai_logs.ai_sql_attempts (
                    request_id,
                    attempt_number,
                    attempt_type,
                    generated_sql,
                    validation_status,
                    validation_errors
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING attempt_id
                """,
                (
                    request_id,
                    attempt_number,
                    attempt_type,
                    generated_sql,
                    validation_status,
                    validation_errors
                )
            )

            attempt_id = cur.fetchone()[0]

    return attempt_id


def finalize_request(request_id, final_status, final_sql=None):
    """
    Update the final status and SQL of a request.
    """

    if final_status not in ("PASSED", "FAILED"):
        raise ValueError("Invalid final_status")

    with psycopg.connect(
        host=os.getenv("PGHOST"),
        port=os.getenv("PGPORT"),
        dbname=os.getenv("PGDATABASE"),
        user=os.getenv("PGUSER"),
        password=os.getenv("PGPASSWORD")
    ) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE ai_logs.ai_requests
                SET final_status = %s,
                    final_sql = %s
                WHERE request_id = %s
                """,
                (final_status, final_sql, request_id)
            )

            if cur.rowcount != 1:
                raise ValueError(
                    f"Request {request_id} not found"
                )
