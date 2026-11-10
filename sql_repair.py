

import requests


def repair_sql(wrong_sql, postgres_error, schema_context=""):

    # Step 1: Build prompt
    prompt = f"""
You are a PostgreSQL SQL repair assistant.

Database metadata:
{schema_context}

Original SQL:
{wrong_sql}

Validation error:
{postgres_error}

Instructions:
1. Correct the SQL using the provided database metadata.
2. Generate only PostgreSQL SELECT queries.
3. Never invent table names or column names.
4. Use only tables and columns provided in the metadata.
5. Preserve the original business meaning.
6. Preserve all requested filters, including currency and status.
7. Use explicit JOIN conditions.
8. Never combine amounts from different currencies without conversion.
9. Fix the reported validation error.
10. Return only corrected SQL.
11. Do not include explanations or markdown.
"""

    # Step 2: Build payload
    payload = {
        "model": "bank-sql-qwen",
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.1,
            "num_predict": 300
        }
    }

    # Step 3: Send request to Ollama
    url = "http://localhost:11434/api/generate"

    response = requests.post(
        url,
        json=payload,
        timeout=180
    )

    response.raise_for_status()

    # Step 4: Extract model response
    data = response.json()
    corrected_sql = data["response"].strip()

    # Step 5: Remove markdown formatting
    if corrected_sql.startswith("```sql"):
        corrected_sql = corrected_sql[6:]

    elif corrected_sql.startswith("```"):
        corrected_sql = corrected_sql[3:]

    if corrected_sql.endswith("```"):
        corrected_sql = corrected_sql[:-3]

    corrected_sql = corrected_sql.strip()

    # Step 6: Return corrected SQL
    return corrected_sql
