
import re


def validate_semantics(question, sql):
    errors = []
    question_lower = question.lower()

    # Rule 1: Currency validation
    currencies = ["EUR", "USD", "GBP"]

    for currency in currencies:
        if re.search(
            rf"\b{currency}\b",
            question,
            re.IGNORECASE
        ):
            pattern = rf"\bcurrency\s*=\s*'{currency}'"

            if not re.search(
                pattern,
                sql,
                re.IGNORECASE
            ):
                errors.append(
                    f"Missing currency filter: {currency}"
                )

    # Rule 2: Top N validation
    top_match = re.search(
        r"\btop\s+(\d+)\b",
        question_lower
    )

    if top_match:
        top_n = int(top_match.group(1))

        if not re.search(
            rf"\bLIMIT\s+{top_n}\b",
            sql,
            re.IGNORECASE
        ):
            errors.append(
                f"Missing or incorrect LIMIT {top_n}"
            )

        if not re.search(
            r"\bORDER\s+BY\b",
            sql,
            re.IGNORECASE
        ):
            errors.append(
                "Missing ORDER BY for Top N"
            )

        elif not re.search(
            r"\bORDER\s+BY\b[\s\S]*?\bDESC\b",
            sql,
            re.IGNORECASE
        ):
            errors.append(
                "Missing DESC ordering for Top N"
            )

    return {
        "valid": len(errors) == 0,
        "errors": errors
    }
