
from sql_validator import check_sql_safety
from semantic_validator import validate_semantics
from business_metric_validator import validate_business_metric
from postgres_validator import validate_postgres_metadata


def validate_generated_sql(question, sql, metadata=None):
    """
    Validate SQL using structural, semantic,
    business metric, and database metadata rules.
    """

    errors = []

    # Step 1: AST validation
    safety = check_sql_safety(sql)

    if not safety["safe"]:
        return {
            "valid": False,
            "errors": [safety["error"]]
        }

    # Step 2: Semantic validation
    semantic = validate_semantics(question, sql)

    if not semantic["valid"]:
        errors.extend(semantic["errors"])

    # Step 3: Business metric validation
    business = validate_business_metric(question, sql)

    if not business["valid"]:
        errors.extend(business["errors"])

    # Step 4: Metadata validation
    if metadata is not None:
        database_check = validate_postgres_metadata(
            sql,
            metadata
        )

        if not database_check["valid"]:
            errors.extend(database_check["errors"])

    return {
        "valid": len(errors) == 0,
        "errors": errors
    }
