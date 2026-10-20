import json
import re
import time
from pathlib import Path

import requests

from rag_agent import load_knowledge, retrieve

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent

EVAL_FILE = PROJECT_DIR / "evals" / "v2.jsonl"
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.1:8b"


def load_eval_cases():
    with EVAL_FILE.open("r", encoding="utf-8") as file:
        return [json.loads(line) for line in file if line.strip()]


def normalize(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s-]", " ", text)
    return " ".join(text.split())


def generate_answer(query, retrieved):
    if not retrieved:
        return "NOT FOUND", 0, 0.0

    context = "\n\n".join(
        f"[{doc['id']}]\n"
        f"Title: {doc['title']}\n"
        f"{doc['text']}"
        for doc in retrieved
    )

    prompt = f"""
Answer the question using only the retrieved documents.

Question:
{query}

Retrieved documents:
{context}

Rules:
- Use only facts supported by the documents.
- If the requested fact is unavailable, answer exactly NOT FOUND.
- Cite each supporting document using its exact ID, such as [DOC-05].
- Never invent a document ID.
- Keep the answer concise.

Answer:
"""

    start = time.perf_counter()

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0},
        },
        timeout=600,
    )

    response.raise_for_status()
    data = response.json()
    elapsed = time.perf_counter() - start

    answer = data["response"].strip()
    output_tokens = data.get("eval_count", 0)

    return answer, output_tokens, elapsed


def check_answer(answer, case):
    answer_norm = normalize(answer)

    if case["expected_status"] == "ungrounded":
        return (
            "not found" in answer_norm
            or "not available" in answer_norm
            or "insufficient information" in answer_norm
        )

    points = case["expected_answer_points"]

    if not points:
        return False

    for point in points:
        point_norm = normalize(point)

        if point_norm in answer_norm:
            continue

        words = [w for w in point_norm.split() if len(w) > 2]
        if words and all(word in answer_norm for word in words):
            continue

        root_words = [w.rstrip("sed").rstrip("s") or w for w in words]
        if root_words and all(root in answer_norm for root in root_words):
            continue

        return False

    return True


def check_citation(answer, retrieved, case):
    cited_ids = set(re.findall(r"\[(DOC-\d+)\]", answer))
    retrieved_ids = {doc["id"] for doc in retrieved}
    gold_ids = set(case["gold_doc_ids"])

    if case["expected_status"] == "ungrounded":
        abstained = (
            "not found" in normalize(answer)
            or "not available" in normalize(answer)
            or "insufficient information" in normalize(answer)
        )
        return abstained and not cited_ids

    return (
        bool(cited_ids)
        and cited_ids.issubset(retrieved_ids)
        and cited_ids.issubset(gold_ids)
    )


def main():
    cases = load_eval_cases()
    documents = load_knowledge()

    retrieval_hits = 0
    retrieval_total = 0

    answer_correct = 0
    citation_correct = 0

    total_latency = 0.0
    total_output_tokens = 0

    print("WEEK 6 - RAG EVALUATION")
    print(f"Model: {MODEL}")
    print("=" * 55)

    for case in cases:
        query = case["query"]
        gold_ids = set(case["gold_doc_ids"])

        retrieved = retrieve(query, documents, top_k=3)
        retrieved_ids = {doc["id"] for doc in retrieved}

        if gold_ids:
            retrieval_total += 1

            hit = bool(gold_ids & retrieved_ids)
            if hit:
                retrieval_hits += 1
        else:
            hit = None

        try:
            answer, output_tokens, latency = generate_answer(
                query, retrieved
            )
        except requests.RequestException as error:
            print(f"\nCase {case['id']}: Ollama request failed.")
            print(f"Error: {error}")
            print("Evaluation stopped; metrics are incomplete.")
            return

        total_latency += latency
        total_output_tokens += output_tokens

        answer_ok = check_answer(answer, case)
        citation_ok = check_citation(answer, retrieved, case)

        if answer_ok:
            answer_correct  +=1

        if citation_ok:
            citation_correct += 1

        print(f"\nCase: {case['id']}")
        print(f"Question: {query}")
        print(f"Expected documents: {sorted(gold_ids)}")
        print(f"Retrieved documents: {sorted(retrieved_ids)}")
        print(f"Retrieval hit: {hit}")
        print(f"Answer: {answer}")
        print(f"Answer correct: {answer_ok}")
        print(f"Citation correct: {citation_ok}")
        print(f"Generation latency: {latency:.2f} seconds")
        print(f"Output tokens: {output_tokens}")

    total_cases = len(cases)
    if total_cases > 0:
        print("\n" + "=" * 55)
        print("SUMMARY")
        print("=" * 55)
        if retrieval_total > 0:
            print(f"Retrieval hit rate: {retrieval_hits / retrieval_total:.2%}")
        print(f"Answer correct rate: {answer_correct / total_cases:.2%}")
        print(f"Citation correct rate: {citation_correct / total_cases:.2%}")
        print(f"Average latency: {total_latency / total_cases:.2f} seconds")
        print(f"Total output tokens: {total_output_tokens}")


if __name__ == "__main__":
    main()
