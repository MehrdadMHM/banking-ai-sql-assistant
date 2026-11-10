import requests

url = "http://localhost:11434/api/generate"

payload = {
    "model": "llama3.2:3b",
    "prompt": "Explain what an ETL pipeline is.",
    "stream": False ,
    "options": {
    "num_predict": 1000
                }
}

response = requests.post(url,json=payload)
response.raise_for_status()

data=response.json()

print(data["response"])
