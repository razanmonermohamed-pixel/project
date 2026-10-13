from pathlib import Path
import re
import requests

BASE_DIR = Path(__file__).resolve().parent
KNOWLEDGE_FILE = BASE_DIR / "knowledge" / "website_monitoring.txt"

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.1:8b"


def load_knowledge():
    """Load the knowledge file and split it into documents."""
    text = KNOWLEDGE_FILE.read_text(encoding="utf-8")

    pattern = re.compile(
        r"\[(DOC-\d+)\]\s*\n"
        r"Title:\s*(.*?)\s*\n"
        r"(.*?)(?=\n\s*\[DOC-\d+\]|\Z)",
        re.DOTALL,
    )

    documents = []

    for match in pattern.finditer(text):
        documents.append({
            "id": match.group(1),
            "title": match.group(2).strip(),
            "text": match.group(3).strip(),
        })

    return documents


def tokenize(text):
    """Extract lowercase English words."""
    stop_words = {
        "what", "the", "is", "a", "an", "when", "does", "do",
        "how", "if", "of", "in", "with", "and", "to", "it",
        "as", "can", "from", "before", "using", "this", "that",
        "for", "on", "by", "has", "have", "be", "are", "was",
        "were", "their", "than", "which"
    }

    words = re.findall(r"\b[a-z0-9]+\b", text.lower())
    return {word for word in words if word not in stop_words}


def retrieve(query, documents, top_k=3):
    """Retrieve the most relevant documents using keyword overlap."""
    query_words = tokenize(query)
    scored_documents = []

    for document in documents:
        document_words = tokenize(
            document["title"] + " " + document["text"]
        )
        score = len(query_words & document_words)

        if score > 0:
            scored_documents.append((score, document))

    scored_documents.sort(
        key=lambda item: (-item[0], item[1]["id"])
    )

    return [
        document
        for score, document in scored_documents[:top_k]
    ]


def generate_answer(query, retrieved):
    """Generate an answer using only retrieved knowledge."""
    if not retrieved:
        return "NOT FOUND"

    context = "\n\n".join(
        f"[{document['id']}]\n"
        f"Title: {document['title']}\n"
        f"{document['text']}"
        for document in retrieved
    )

    prompt = f"""
Answer the question using only the retrieved documents.

Question:
{query}

Retrieved documents:
{context}

Rules:
- Use only facts supported by the retrieved documents.
- If the requested information is not available, answer exactly:
  NOT FOUND
- Cite supporting documents using their exact IDs, for example [DOC-06].
- Do not invent document IDs.
- Keep the answer concise.

Answer:
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
        },
        timeout=600,
    )

    response.raise_for_status()
    return response.json()["response"].strip()


def run_rag(query):
    """Retrieve knowledge and generate a grounded answer."""
    documents = load_knowledge()
    retrieved = retrieve(query, documents)

    print("\n===== RAG QUERY =====")
    print(query)

    print("\n===== RETRIEVED DOCUMENTS =====")

    if not retrieved:
        print("No relevant documents retrieved.")
        print("\n===== GROUNDED ANSWER =====")
        print("NOT FOUND")
        return

    for document in retrieved:
        print(f"\n[{document['id']}] {document['title']}")
        print(document["text"])

    answer = generate_answer(query, retrieved)

    print("\n===== GROUNDED ANSWER =====")
    print(answer)


if __name__ == "__main__":
    question = "What happens when a website changes?"
    run_rag(question)