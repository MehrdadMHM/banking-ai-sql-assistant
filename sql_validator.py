
import psycopg
from pglast import parse_sql, ast
from pglast.parser import ParseError
from pglast.visitors import Visitor


# Allowed database tables
ALLOWED_TABLES = {
    "dim_customers",
    "dim_accounts",
    "dim_branches",
    "fact_transactions"
}

# Functions permitted in this learning version
ALLOWED_FUNCTIONS = {
    "count", "sum", "avg", "min", "max"
}


# Step 1: Inspect SQL syntax tree
class TableVisitor(Visitor):

    def __init__(self):
        super().__init__()
        self.unauthorized_tables = []
        self.unauthorized_functions = []
        self.invalid_selects = []

    def visit_RangeVar(self, ancestors, node):

        if (
            node.schemaname != "analytics"
            or node.relname not in ALLOWED_TABLES
        ):
            self.unauthorized_tables.append(
                f"{node.schemaname}.{node.relname}"
            )

    def visit_FuncCall(self, ancestors, node):

        names = [part.sval for part in node.funcname]

        if len(names) != 1 or names[0].lower() not in ALLOWED_FUNCTIONS:
            self.unauthorized_functions.append(".".join(names))

    def visit_SelectStmt(self, ancestors, node):

        if node.intoClause is not None:
            self.invalid_selects.append("SELECT INTO is not allowed")

        if node.withClause is not None:
            self.invalid_selects.append("WITH is not allowed")

        if node.lockingClause:
            self.invalid_selects.append("Locking clauses are not allowed")


# Step 2: Check SQL safety rules
def check_sql_safety(query):

    try:
        statements = parse_sql(query)

    except ParseError as error:
        return {"safe": False, "error": str(error)}

    if len(statements) != 1:
        return {
            "safe": False,
            "error": "Expected exactly one SQL statement"
        }

    statement = statements[0].stmt

    if not isinstance(statement, ast.SelectStmt):
        return {
            "safe": False,
            "error": "Only SELECT is allowed"
        }

    visitor = TableVisitor()
    visitor(statements[0])

    if visitor.unauthorized_tables:
        return {
            "safe": False,
            "error": f"Unauthorized tables: {visitor.unauthorized_tables}"
        }

    if visitor.unauthorized_functions:
        return {
            "safe": False,
            "error": f"Unauthorized functions: {visitor.unauthorized_functions}"
        }

    if visitor.invalid_selects:
        return {
            "safe": False,
            "error": "; ".join(visitor.invalid_selects)
        }

    return {"safe": True, "error": None}


# Step 3: Validate query using PostgreSQL EXPLAIN
def validate_sql(cursor, query):

    safety = check_sql_safety(query)

    if not safety["safe"]:
        return {
            "valid": False,
            "error": safety["error"],
            "plan": None
        }

    try:
        cursor.execute("SET LOCAL statement_timeout = '5s'")
        cursor.execute("EXPLAIN " + query)

        plan = [row[0] for row in cursor.fetchall()]

        return {
            "valid": True,
            "error": None,
            "plan": plan
        }

    except psycopg.Error as error:
        cursor.connection.rollback()

        return {
            "valid": False,
            "error": str(error),
            "plan": None
        }
