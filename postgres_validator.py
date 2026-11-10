
from pglast import parse_sql, ast
from pglast.visitors import Visitor


class ColumnVisitor(Visitor):
    def __init__(self):
        super().__init__()
        self.columns = []

    def visit_ColumnRef(self, ancestors, node):
        fields = []

        for field in node.fields:
            if not isinstance(field, ast.String):
                raise ValueError(
                    "Wildcard columns are not supported"
                )

            fields.append(field.sval)

        self.columns.append(fields)

    def visit_SelectStmt(self, ancestors, node):
        raise ValueError(
            "Nested SELECT is not supported"
        )


def validate_postgres_metadata(sql, schema_context):
    """
    Validate SQL table and column references.

    Supports:
      - Direct analytics tables and views
      - Table aliases
      - Simple JOIN ... ON
      - SELECT output aliases in ORDER BY

    Does not execute generated SQL.
    """

    errors = []

    try:
        statements = parse_sql(sql)

        if len(statements) != 1:
            raise ValueError(
                "Exactly one statement required"
            )

        query = statements[0].stmt

        if not isinstance(query, ast.SelectStmt):
            raise ValueError("Only SELECT is supported")

        if query.withClause is not None:
            raise ValueError("CTE is not supported")

        if not isinstance(schema_context, dict):
            raise TypeError(
                "schema_context must be a dictionary"
            )

        # Step 1: Collect table aliases
        aliases = {}
        expressions = []

        def collect_tables(node):
            if isinstance(node, ast.RangeVar):
                schema = node.schemaname
                table = node.relname

                if schema != "analytics":
                    raise ValueError(
                        "Only analytics schema is allowed"
                    )

                alias = (
                    node.alias.aliasname
                    if node.alias
                    else table
                )

                if alias in aliases:
                    raise ValueError(
                        f"Duplicate table alias: {alias}"
                    )

                aliases[alias] = table

            elif isinstance(node, ast.JoinExpr):
                if node.isNatural or node.usingClause:
                    raise ValueError(
                        "NATURAL JOIN and JOIN USING "
                        "are not supported"
                    )

                collect_tables(node.larg)
                collect_tables(node.rarg)

                if node.quals is not None:
                    expressions.append(node.quals)

            else:
                raise ValueError(
                    "Unsupported FROM structure"
                )

        for item in query.fromClause or []:
            collect_tables(item)

        if not aliases:
            raise ValueError("No table found")

        # Step 2: Check tables
        unknown_tables = [
            table
            for table in aliases.values()
            if table not in schema_context
        ]

        if unknown_tables:
            return {
                "valid": False,
                "errors": [
                    f"Unknown table: {table}"
                    for table in unknown_tables
                ]
            }

        # Step 3: Collect SELECT output aliases
        output_aliases = set()

        for target in query.targetList or []:
            if target.name:
                output_aliases.add(target.name)

            expressions.append(target.val)

        # Step 4: Collect other SQL expressions
        for expression in [
            query.whereClause,
            query.havingClause,
            query.limitCount,
            query.limitOffset
        ]:
            if expression is not None:
                expressions.append(expression)

        for expression in query.groupClause or []:
            expressions.append(expression)

        for expression in query.distinctClause or []:
            if not isinstance(expression, ast.A_Star):
                expressions.append(expression)

        # Step 5: Inspect physical column references
        visitor = ColumnVisitor()

        for expression in expressions:
            visitor(expression)

        # ORDER BY is handled separately because
        # PostgreSQL allows SELECT output aliases there.
        for sort_item in query.sortClause or []:
            sort_expression = sort_item.node

            if isinstance(sort_expression, ast.ColumnRef):
                fields = sort_expression.fields

                if (
                    len(fields) == 1
                    and isinstance(fields[0], ast.String)
                    and fields[0].sval in output_aliases
                ):
                    continue

            visitor(sort_expression)

        # Step 6: Validate collected columns
        for fields in visitor.columns:
            if len(fields) == 2:
                alias, column = fields

                if alias not in aliases:
                    errors.append(
                        f"Unknown table alias: {alias}"
                    )
                    continue

                table = aliases[alias]

                if column not in schema_context[table]:
                    errors.append(
                        f"Unknown column: {alias}.{column}"
                    )

            elif len(fields) == 1:
                column = fields[0]

                matches = [
                    alias
                    for alias, table in aliases.items()
                    if column in schema_context[table]
                ]

                if len(matches) == 0:
                    errors.append(
                        f"Unknown column: {column}"
                    )

                elif len(matches) > 1:
                    errors.append(
                        f"Ambiguous column: {column}"
                    )

            else:
                errors.append(
                    f"Unsupported column reference: {fields}"
                )

    except Exception as exc:
        errors.append(str(exc))

    return {
        "valid": len(errors) == 0,
        "errors": errors
    }
