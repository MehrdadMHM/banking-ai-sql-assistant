
from schema_context import get_schema_context
from metadata_provider import get_table_columns
from sql_generator import generate_sql
from validation_engine import validate_generated_sql
from sql_orchestrator import repair_with_retry

# RAG integration
from rag_retriever import retrieve_rules, format_rag_context

from ai_logger import (
    create_request,
    log_attempt,
    finalize_request
)


MODEL_NAME = "bank-sql-qwen"
MAX_REPAIR_ATTEMPTS = 3
RAG_TOP_K = 3


def run_sql_pipeline(question):
    """
    Retrieve banking knowledge, generate, validate,
    repair and log SQL.

    Validation:
      1. AST Safety
      2. Semantic Rules
      3. Business Metrics
      4. PostgreSQL Metadata

    Note:
      Generated SQL is not executed.
    """

    # Step 1: Validate user input
    if not question or not question.strip():
        raise ValueError("Question cannot be empty")

    question = question.strip()

    # Step 2: Load database context
    schema_context = get_schema_context()

    # Load real table and column metadata
    metadata = get_table_columns()

    print("Database metadata loaded.")
    print(f"Available tables: {len(metadata)}")

    # Step 3: Create audit request
    request_id = create_request(
        question,
        MODEL_NAME
    )

    print(f"Created request: {request_id}")

    try:
        # Step 4: Retrieve relevant banking knowledge
        rules = retrieve_rules(
            question,
            top_k=RAG_TOP_K
        )

        rag_context = format_rag_context(rules)

        print("\nRAG knowledge retrieved:")
        for rule in rules:
            print(
                f"{rule['document_key']} "
                f"(similarity={rule['similarity']:.4f})"
            )

        # Context for repair: schema + retrieved guidance
        repair_context = schema_context + f"""

Retrieved banking knowledge:
{rag_context}

Use this knowledge only when relevant to the
user's question. Database metadata is authoritative
for available tables and columns.
"""

        # Step 5: Generate SQL using Qwen + RAG
        generated_sql = generate_sql(
            question,
            schema_context,
            rag_context=rag_context
        )

        print("\nGenerated SQL:")
        print(generated_sql)

        # Step 6: Unified validation
        # AST + Semantic + Business + Metadata
        validation = validate_generated_sql(
            question,
            generated_sql,
            metadata=metadata
        )

        errors = validation["errors"]

        validation_status = (
            "PASSED" if validation["valid"] else "FAILED"
        )

        error_message = (
            "; ".join(errors) if errors else None
        )

        # Step 7: Log initial generation
        attempt_id = log_attempt(
            request_id=request_id,
            attempt_number=1,
            attempt_type="GENERATION",
            generated_sql=generated_sql,
            validation_status=validation_status,
            validation_errors=error_message
        )

        print(f"\nCreated attempt: {attempt_id}")
        print("Generation validation:", validation_status)

        # Step 8: Initial SQL passed
        if validation["valid"]:

            finalize_request(
                request_id,
                "PASSED",
                generated_sql
            )

            print("\nPipeline PASSED")

            return {
                "request_id": request_id,
                "status": "PASSED",
                "sql": generated_sql,
                "repair_attempts": 0,
                "error": None
            }

        # Step 9: Initial SQL failed
        print("\nValidation errors:", error_message)
        print("Starting automatic SQL repair...")

        repair_result = repair_with_retry(
            wrong_sql=generated_sql,
            error=error_message,
            question=question,
            max_attempts=MAX_REPAIR_ATTEMPTS,
            schema_context=repair_context,
            request_id=request_id,
            metadata=metadata
        )

        # Step 10: Repair successful
        if repair_result["passed_initial_checks"]:

            final_sql = repair_result["sql"]

            final_validation = validate_generated_sql(
                question,
                final_sql,
                metadata=metadata
            )

            if not final_validation["valid"]:
                final_error = "; ".join(
                    final_validation["errors"]
                )

                finalize_request(
                    request_id,
                    "FAILED",
                    None
                )

                print("\nRepaired SQL failed validation:")
                print(final_error)

                return {
                    "request_id": request_id,
                    "status": "FAILED",
                    "sql": None,
                    "repair_attempts": repair_result["attempts"],
                    "error": final_error
                }

            finalize_request(
                request_id,
                "PASSED",
                final_sql
            )

            print("\nPipeline PASSED after repair")

            return {
                "request_id": request_id,
                "status": "PASSED",
                "sql": final_sql,
                "repair_attempts": repair_result["attempts"],
                "error": None
            }

        # Step 11: All repair attempts failed
        finalize_request(
            request_id,
            "FAILED",
            None
        )

        print("\nPipeline FAILED")

        return {
            "request_id": request_id,
            "status": "FAILED",
            "sql": None,
            "repair_attempts": repair_result["attempts"],
            "error": repair_result["error"]
        }

    except Exception:
        # Avoid leaving requests PENDING
        try:
            finalize_request(
                request_id,
                "FAILED",
                None
            )
        except Exception:
            pass

        raise
