
from ai_logger import create_request

request_id = create_request(
    "Show top 5 customers in EUR",
    "bank-sql-qwen"
)

print("Created request:", request_id)
