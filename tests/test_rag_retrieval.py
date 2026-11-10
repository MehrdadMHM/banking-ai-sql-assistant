
import os

import psycopg
import requests
from dotenv import load_dotenv

load_dotenv()

TEST_CASES = [
    ("Calculate gross transaction volume", "KPI_001"),
    ("Calculate net transaction flow", "KPI_002"),
    ("Show transactions in EUR", "RULE_001"),
]


def generate_embedding(text):
    response = requests.post(
        "http://localhost:11434/api/embed",
        json={"model": "embeddinggemma", "input": text},
        timeout=120,
    )
    response.raise_for_status()

    embedding = response.json()["embeddings"][0]
    assert len(embedding) == 768

    return "[" + ",".join(map(str, embedding)) + "]"


def main():
    passed = 0

    with psycopg.connect(
        host=os.getenv("PGHOST", "localhost"),
        port=os.getenv("PGPORT", "5432"),
        dbname=os.getenv("PGDATABASE", "bank_analytics"),
        user=os.environ["PGUSER"],
        password=os.environ["PGPASSWORD"],
    ) as conn:
        with conn.cursor() as cur:
            for question, expected_key in TEST_CASES:
                vector = generate_embedding(question)

                cur.execute(
                    """
                    SELECT
                        document_key,
                        title,
                        ROUND(
                            (1 - (embedding <=> %s::vector))::numeric,
                            4
                        ) AS similarity
                    FROM rag.documents
                    ORDER BY embedding <=> %s::vector
                    LIMIT 3;
                    """,
                    (vector, vector),
                )

                results = cur.fetchall()
                top_key = results[0][0] if results else None

                print(f"\nQuestion: {question}")

                for rank, (key, title, similarity) in enumerate(
                    results, start=1
                ):
                    print(
                        f"  {rank}. {key} | {title} "
                        f"| similarity={similarity}"
                    )

                if top_key == expected_key:
                    print("  RESULT: PASS")
                    passed += 1
                else:
                    print(
                        f"  RESULT: FAIL "
                        f"(expected {expected_key}, got {top_key})"
                    )

    print(f"\nRetrieval accuracy: {passed}/{len(TEST_CASES)}")

    if passed != len(TEST_CASES):
        raise AssertionError("Some retrieval tests failed.")

    print("RAG RETRIEVAL TEST PASSED")


if __name__ == "__main__":
    main()
