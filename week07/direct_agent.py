from pathlib import Path
import sys
import time

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from tools import load_knowledge, retrieve, generate_answer


def run_direct_agent(query):
    start_time = time.perf_counter()

    documents = load_knowledge()
    retrieved = retrieve(query, documents, top_k=3)

    answer, tokens = generate_answer(query, retrieved)

    elapsed = time.perf_counter() - start_time

    return {
        "strategy": "direct",
        "query": query,
        "retrieved_ids": [d["id"] for d in retrieved],
        "answer": answer,
        "tokens": tokens,
        "latency": round(elapsed, 2),
    }


if __name__ == "__main__":
    result = run_direct_agent("What happens when a website changes?")
    print(f"Answer: {result['answer']}")
    print(f"Tokens: {result['tokens']}")
    print(f"Latency: {result['latency']}s")