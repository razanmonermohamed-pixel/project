import json
import urllib.request

url = "http://localhost:11434/api/chat"

data = {
    "model": "gemma3:1b",
    "messages": [
        {
            "role": "user",
            "content": "Explain briefly what a website monitoring agent does."
        }
    ],
    "stream": False
}

request = urllib.request.Request(
    url,
    data=json.dumps(data).encode("utf-8"),
    headers={"Content-Type": "application/json"},
    method="POST"
)

try:
    with urllib.request.urlopen(request, timeout=120) as response:
        result = json.loads(response.read().decode("utf-8"))

    print("Ollama connection successful!")
    print(result["message"]["content"])

except Exception as error:
    print("Connection failed:", error)