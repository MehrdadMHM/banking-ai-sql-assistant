
import requests


OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "bank-sql-qwen"


def generate_sql(question, schema_context, rag_context=None):
    """
    Generate PostgreSQL SQL using the local Qwen model.

    Args:
        question (str): User's natural language question.
        schema_context (str): Database metadata and business rules.
        rag_context (str | None): Retrieved RAG knowledge.

    Returns:
        str: Generated SQL query.
    """

    # Step 1: Validate inputs
    if not question or not question.strip():
        raise ValueError("Question cannot be empty")

    if not schema_context or not schema_context.strip():
        raise ValueError("Schema context cannot be empty")

    # Step 2: Build optional RAG section
    rag_section = ""

    if rag_context and rag_context.strip():
        rag_section = f"""
Retrieved banking knowledge:
{rag_context}

Use retrieved knowledge only when relevant to the
user's question. The database metadata defines
which tables and columns are available.
Do not apply unrelated metrics or filters.
"""

    # Step 3: Build prompt
    # General SQL rules are defined in Modelfile.qwen
    prompt = f"""
Database metadata:
{schema_context}

{rag_section}

User question:
{question}

Generate a PostgreSQL SELECT query that answers
the user's question using the provided metadata.

Return only SQL.
"""

    # Step 4: Prepare Ollama request
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.1,
            "num_predict": 300
        }
    }

    # Step 5: Send request to Ollama
    response = requests.post(
        OLLAMA_URL,
        json=payload,
        timeout=180
    )

    response.raise_for_status()

    # Step 6: Extract SQL
    data = response.json()
    generated_sql = data["response"].strip()

    # Step 7: Remove Markdown formatting
    if generated_sql.startswith("```sql"):
        generated_sql = generated_sql[6:]

    elif generated_sql.startswith("```"):
        generated_sql = generated_sql[3:]

    if generated_sql.endswith("```"):
        generated_sql = generated_sql[:-3]

    generated_sql = generated_sql.strip()

    if not generated_sql:
        raise ValueError("Ollama returned an empty SQL response")

    return generated_sql
