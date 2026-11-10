
from schema_context import get_schema_context
from sql_generator import generate_sql

# User question
question = "Show the top 5 customers by total transaction amount in EUR"

# Load database metadata
schema_context = get_schema_context()

# Generate SQL using Qwen
generated_sql = generate_sql(
    question,
    schema_context
)

print("\nGenerated SQL:")
print(generated_sql)
