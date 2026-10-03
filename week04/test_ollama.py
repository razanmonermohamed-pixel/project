import requests

url = "http://localhost:11434/api/chat"

data = {
    "model": "gemma3:1b",
    "messages": [
        {
            "role": "user",
            "content": "Reply with exactly: Ollama is working"
        }
    ],
    "stream": False
}

response = requests.post(url, json=data, timeout=120)

print("Status code:", response.status_code)

result = response.json()

print("Ollama response:")
print(result["message"]["content"])