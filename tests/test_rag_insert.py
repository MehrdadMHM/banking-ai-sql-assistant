
import os
import requests
import psycopg
from dotenv import load_dotenv

load_dotenv()

OLLAMA_EMBED_URL = "http://localhost:11434/api/embed"

document_key = "KPI_001"
title = "Gross Transaction Volume"
content = (
    "Gross Transaction Volume is calculated using SUM(amount) "
    "from analytics.fact_transactions. "
    "Use SUM(amount), not SUM(signed_amount), for gross volume."
)

# 1. Generate a 768-dimensional embedding
response = requests.post(
    OLLAMA_EMBED_URL,
    json={
        "model": "embeddinggemma",
        "input": content,
    },
    timeout=120,
)
response.raise_for_status()

embedding = response.json()["embeddings"][0]

assert len(embedding) == 768, (
    f"Expected 768 dimensions, got {len(embedding)}"
)

# 2. Connect to the existing PostgreSQL database
conn_params = {
    "host": os.getenv("PGHOST", "localhost"),
    "port": os.getenv("PGPORT", "5432"),
    "dbname": os.getenv("PGDATABASE", "bank_analytics"),
    "user": os.environ["PGUSER"],
    "password": os.environ["PGPASSWORD"],
}

# pgvector accepts its textual vector representation
embedding_text = "[" + ",".join(str(x) for x in embedding) + "]"

with psycopg.connect(**conn_params) as conn:
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO rag.documents
                (document_key, title, content, embedding)
            VALUES
                (%s, %s, %s, %s::vector)
            ON CONFLICT (document_key)
            DO UPDATE SET
                title = EXCLUDED.title,
                content = EXCLUDED.content,
                embedding = EXCLUDED.embedding
            RETURNING id, document_key;
            """,
            (document_key, title, content, embedding_text),
        )

        saved = cur.fetchone()

print("Saved document:", saved)
print("Embedding dimensions:", len(embedding))
print("RAG INSERT TEST PASSED")
