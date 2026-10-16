from pathlib import Path
import sys
import time

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from tools import load_knowledge, retrieve, generate_answer


def run_single_agent(query):
    start_time = time.perf_counter()

    documents = load_knowledge()
    retrieved = retrieve(query, documents, top_k=3)
    answer, tokens = generate_answer(query, retrieved)

    elapsed = time.perf_counter() - start_time

    return {
        "answer": answer,
        "tokens": tokens,
        "latency": round(elapsed, 2),
        "retrieved": [d["id"] for d in retrieved],
    }


if __name__ == "__main__":
    query = "What happens when a website changes?"
    result = run_single_agent(query)

    print("=" * 55)
    print("SINGLE AGENT (Baseline)")
    print("=" * 55)
    print(f"Query: {query}")
    print(f"Retrieved: {result['retrieved']}")
    print(f"Answer: {result['answer']}")
    print(f"Tokens: {result['tokens']}")
    print(f"Latency: {result['latency']}s")