
from sql_repair import repair_sql
from validation_engine import validate_generated_sql
from ai_logger import log_attempt


def repair_with_retry(
    wrong_sql,
    error,
    question=None,
    max_attempts=3,
    schema_context="",
    request_id=None,
    metadata=None
):
    """
    Repair SQL and validate every attempt using:
      - AST
      - Semantic rules
      - Business metrics
      - PostgreSQL metadata

    Generated SQL is never executed.
    """

    if metadata is None:
        raise ValueError(
            "Metadata is required for repair validation"
        )

    if not question or not question.strip():
        raise ValueError(
            "Question is required for repair validation"
        )

    current_sql = wrong_sql
    current_error = error

    for attempt in range(1, max_attempts + 1):

        print(f"Repair attempt: {attempt}")

        # Step 1: Generate corrected SQL
        corrected_sql = repair_sql(
            current_sql,
            current_error,
            schema_context=schema_context
        )

        # Step 2: Validate with all four validators
        validation = validate_generated_sql(
            question,
            corrected_sql,
            metadata=metadata
        )

        passed = validation["valid"]

        error_message = (
            "; ".join(validation["errors"])
            if not passed
            else None
        )

        # Step 3: Log this repair attempt
        if request_id is not None:
            log_attempt(
                request_id=request_id,
                attempt_number=attempt + 1,
                attempt_type="REPAIR",
                generated_sql=corrected_sql,
                validation_status="PASSED" if passed else "FAILED",
                validation_errors=error_message
            )

        # Step 4: Return successful repair
        if passed:
            return {
                "passed_initial_checks": True,
                "sql": corrected_sql,
                "attempts": attempt,
                "error": None
            }

        # Step 5: Prepare next attempt
        current_sql = corrected_sql
        current_error = error_message

    return {
        "passed_initial_checks": False,
        "sql": None,
        "attempts": max_attempts,
        "error": current_error
    }
