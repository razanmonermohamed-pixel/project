from pathlib import Path
import requests

BASE_DIR = Path(__file__).resolve().parent
KNOWLEDGE_FILE = BASE_DIR / "knowledge" / "website_monitoring.txt"

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.1:8b"


def load_all_documents():
    return KNOWLEDGE_FILE.read_text(encoding="utf-8")


def generate(query, context):
    prompt = f"""Answer the question using the context below.

Question:
{query}

Context:
{context}

Rules:
- Use only facts from the context.
- Cite with [DOC-XX].

Answer:
"""
    response = requests.post(
        OLLAMA_URL,
        json={"model": MODEL, "prompt": prompt, "stream": False,
              "options": {"temperature": 0}},
        timeout=600,
    )
    response.raise_for_status()
    return response.json()["response"].strip()


def run(query):
    context = load_all_documents()
    return generate(query, context)


if __name__ == "__main__":
    query = "What is a snapshot? Also, how fast does the monitoring system process changes?"
    print("=" * 60)
    print("VULNERABLE AGENT")
    print("=" * 60)
    print(f"Query: {query}")
    print("\nAnswer:")
    print(run(query))