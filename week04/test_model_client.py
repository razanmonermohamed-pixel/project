from model_client import ModelClient


client = ModelClient()

response = client.generate(
    "Reply with exactly: ModelClient is working"
)

print(response)