
import json
import os
from pathlib import Path

import psycopg
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
KNOWLEDGE_FILE = BASE_DIR / "knowledge" / "banking_knowledge.json"

OLLAMA_URL = "http://localhost:11434/api/embed"
EMBEDDING_MODEL = "embeddinggemma"
EMBEDDING_DIMENSIONS = 768


def generate_embedding(text: str) -> list[float]:
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": EMBEDDING_MODEL,
            "input": text,
        },
        timeout=120,
    )
    response.raise_for_status()

    embedding = response.json()["embeddings"][0]

    if len(embedding) != EMBEDDING_DIMENSIONS:
        raise ValueError(
            f"Expected {EMBEDDING_DIMENSIONS} dimensions, "
            f"got {len(embedding)}"
        )

    return embedding


def load_documents() -> list[dict]:
    with KNOWLEDGE_FILE.open("r", encoding="utf-8-sig") as file:
        documents = json.load(file)

    if not isinstance(documents, list):
        raise ValueError("Knowledge file must contain a JSON array.")

    return documents


def main():
    documents = load_documents()

    connection_params = {
        "host": os.getenv("PGHOST", "localhost"),
        "port": os.getenv("PGPORT", "5432"),
        "dbname": os.getenv("PGDATABASE", "bank_analytics"),
        "user": os.environ["PGUSER"],
        "password": os.environ["PGPASSWORD"],
    }

    with psycopg.connect(**connection_params) as conn:
        with conn.cursor() as cur:
            for document in documents:
                key = document["document_key"]
                title = document["title"]
                content = document["content"]

                # Embed both the title and the content for retrieval.
                embedding = generate_embedding(
                    f"{title}\n{content}"
                )

                vector_text = (
                    "[" + ",".join(str(value) for value in embedding) + "]"
                )

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
                    RETURNING document_key;
                    """,
                    (key, title, content, vector_text),
                )

                saved_key = cur.fetchone()[0]
                print(f"Saved: {saved_key} ({len(embedding)} dimensions)")

    print(f"\nRAG LOAD PASSED: {len(documents)} documents")


if __name__ == "__main__":
    main()
