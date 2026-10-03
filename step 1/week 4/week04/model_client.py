import requests


class ModelClient:
    def __init__(self, model="gemma3:1b"):
        self.model = model
        self.url = "http://localhost:11434/api/chat"

    def generate(self, prompt):
        data = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "stream": False
        }

        response = requests.post(
            self.url,
            json=data,
            timeout=120
        )

        response.raise_for_status()

        result = response.json()

        return result["message"]["content"]