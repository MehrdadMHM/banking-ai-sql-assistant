
import os

import psycopg
import requests
from dotenv import load_dotenv

load_dotenv()

EMBED_URL = "http://localhost:11434/api/embed"
EMBED_MODEL = "embeddinggemma"


def retrieve_rules(question: str, top_k: int = 3) -> list[dict]:
    if not question.strip():
        raise ValueError("Question cannot be empty.")

    if not 1 <= top_k <= 20:
        raise ValueError("top_k must be between 1 and 20.")

    response = requests.post(
        EMBED_URL,
        json={
            "model": EMBED_MODEL,
            "input": question,
        },
        timeout=120,
    )
    response.raise_for_status()

    embedding = response.json()["embeddings"][0]

    if len(embedding) != 768:
        raise ValueError("Unexpected embedding dimensions.")

    vector = "[" + ",".join(map(str, embedding)) + "]"

    with psycopg.connect(
        host=os.getenv("PGHOST", "localhost"),
        port=os.getenv("PGPORT", "5432"),
        dbname=os.getenv("PGDATABASE", "bank_analytics"),
        user=os.environ["PGUSER"],
        password=os.environ["PGPASSWORD"],
    ) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    document_key,
                    title,
                    content,
                    1 - (embedding <=> %s::vector)
                        AS similarity
                FROM rag.documents
                ORDER BY embedding <=> %s::vector
                LIMIT %s;
                """,
                (vector, vector, top_k),
            )

            rows = cur.fetchall()

    return [
        {
            "document_key": key,
            "title": title,
            "content": content,
            "similarity": float(similarity),
        }
        for key, title, content, similarity in rows
    ]


def format_rag_context(rules: list[dict]) -> str:
    if not rules:
        return "No relevant banking rules were retrieved."

    sections = []

    for rule in rules:
        sections.append(
            f"[{rule['document_key']}] {rule['title']}\n"
            f"{rule['content']}"
        )

    return "\n\n".join(sections)


if __name__ == "__main__":
    question = "Calculate net transaction flow in EUR"

    rules = retrieve_rules(question, top_k=3)

    print("QUESTION:", question)
    print("\nRETRIEVED RULES:")

    for rule in rules:
        print(
            rule["document_key"],
            round(rule["similarity"], 4),
        )

    print("\nRAG CONTEXT:")
    print(format_rag_context(rules))
