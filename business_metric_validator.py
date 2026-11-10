
import re

from pglast import parse_sql, ast
from pglast.visitors import Visitor


class SumColumnVisitor(Visitor):
    def __init__(self):
        super().__init__()
        self.sum_columns = []

    def visit_FuncCall(self, ancestors, node):
        func_name = ".".join(
            part.sval.lower()
            for part in node.funcname
        )

        if func_name != "sum":
            return

        for arg in node.args or []:
            if isinstance(arg, ast.ColumnRef):
                column = arg.fields[-1]

                if isinstance(column, ast.String):
                    self.sum_columns.append(
                        column.sval.lower()
                    )


def validate_business_metric(question, sql):
    errors = []

    question_lower = question.lower()

    # Explicit net flow request
    net_requested = bool(
        re.search(
            r"\b(net|net flow|net transaction|signed amount)\b",
            question_lower
        )
    )

    # Gross transaction amount request
    gross_requested = bool(
        re.search(
            r"\b(total transaction amount|gross transaction|transaction volume)\b",
            question_lower
        )
    )

    if not net_requested and not gross_requested:
        return {"valid": True, "errors": []}

    visitor = SumColumnVisitor()

    try:
        statements = parse_sql(sql)

        for statement in statements:
            visitor(statement.stmt)

    except Exception as exc:
        return {
            "valid": False,
            "errors": [f"SQL AST parsing failed: {exc}"]
        }

    if net_requested:
        expected_column = "signed_amount"
    else:
        expected_column = "amount"

    if expected_column not in visitor.sum_columns:
        errors.append(
            f"Incorrect aggregation column: expected SUM({expected_column})"
        )

    return {
        "valid": len(errors) == 0,
        "errors": errors
    }
