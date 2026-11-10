from pglast import parse_sql
from pglast.visitors import Visitor

class TableVisitor(Visitor):

    def __init__(self):
        super().__init__()
        self.unauthorized_tables = []

    def visit_RangeVar(self, ancestors, node):
        if node.schemaname != "analytics":
            self.unauthorized_tables.append(
                f"{node.schemaname}.{node.relname}"
            )

query = """
SELECT
    c.customer_name,
    t.amount
FROM analytics.dim_customers c
JOIN raw.transactions t
    ON c.customer_id = t.customer_id;
"""

tree = parse_sql(query)

visitor = TableVisitor()
visitor(tree)

if visitor.unauthorized_tables:
    print("Rejected SQL")
    print("Unauthorized tables:", visitor.unauthorized_tables)
else:
    print("Schema validation passed")

