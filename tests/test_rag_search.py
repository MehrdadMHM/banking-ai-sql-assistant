
import os
import requests
import psycopg
from dotenv import load_dotenv

load_dotenv()

question = "How do I calculate the total transaction volume?"

# 1. Generate embedding for the user's question
response = requests.post(
    "http://localhost:11434/api/embed",
    json={
        "model": "embeddinggemma",
        "input": question,
    },
    timeout=120,
)
response.raise_for_status()

embedding = response.json()["embeddings"][0]
assert len(embedding) == 768

embedding_text = "[" + ",".join(str(x) for x in embedding) + "]"

# 2. Connect to PostgreSQL
conn_params = {
    "host": os.getenv("PGHOST", "localhost"),
    "port": os.getenv("PGPORT", "5432"),
    "dbname": os.getenv("PGDATABASE", "bank_analytics"),
    "user": os.environ["PGUSER"],
    "password": os.environ["PGPASSWORD"],
}

# 3. Find the most relevant banking rule
with psycopg.connect(**conn_params) as conn:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT
                document_key,
                title,
                content,
                ROUND((1 - (embedding <=> %s::vector))::numeric, 4)
                    AS similarity
            FROM rag.documents
            ORDER BY embedding <=> %s::vector
            LIMIT 3;
            """,
            (embedding_text, embedding_text),
        )

        results = cur.fetchall()

print("Question:", question)
print()

for key, title, content, similarity in results:
    print("Document:", key)
    print("Title:", title)
    print("Similarity:", similarity)
    print("Content:", content)
    print("-" * 50)

assert results, "No RAG documents found"
print("RAG SEMANTIC SEARCH PASSED")
