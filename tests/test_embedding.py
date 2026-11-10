
import requests

OLLAMA_URL = "http://localhost:11434/api/embed"
MODEL = "embeddinggemma"

texts = [
    "Gross transaction volume",
    "Total transaction amount",
    "Employee vacation days"
]

response = requests.post(
    OLLAMA_URL,
    json={
        "model": MODEL,
        "input": texts
    },
    timeout=180
)

response.raise_for_status()

data = response.json()
embeddings = data["embeddings"]

assert len(embeddings) == len(texts)
assert all(len(vector) == len(embeddings[0]) for vector in embeddings)

print("Number of embeddings:", len(embeddings))
print("Vector dimensions:", len(embeddings[0]))
print("Embedding test PASSED")
