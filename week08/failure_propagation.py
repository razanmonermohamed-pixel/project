from pathlib import Path
import sys
import time

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from tools import load_knowledge, retrieve, generate_answer, call_llm
from multi_agent import (
    analyst_agent,
    writer_agent,
    critic_agent,
)

FAILURE_STATE = {"active": False, "count": 0}


def failing_retrieve(query, documents, top_k=3):
    if not FAILURE_STATE["active"]:
        return retrieve(query, documents, top_k=top_k)
    FAILURE_STATE["count"] += 1
    if FAILURE_STATE["count"] == 1:
        print("  [FAILURE] Researcher returned empty documents", flush=True)
        return []
    return retrieve(query, documents, top_k=top_k)


def activate():
    FAILURE_STATE["active"] = True
    FAILURE_STATE["count"] = 0


def reset():
    FAILURE_STATE["active"] = False
    FAILURE_STATE["count"] = 0


def run_multi_with_failure(query):
    start = time.perf_counter()
    total_tokens = 0
    trace = []

    documents = load_knowledge()

    retrieved = failing_retrieve(query, documents)
    if not retrieved:
        trace.append("Researcher FAILED → empty documents")
        print("  [PROPAGATION] Downstream agents have no context", flush=True)

    context = "\n\n".join(
        f"[{d['id']}] {d['title']}: {d['text']}"
        for d in retrieved
    ) or "No documents retrieved."

    try:
        facts, tokens = analyst_agent(query, context)
        total_tokens += tokens
        trace.append(f"Analyst → {len(facts.splitlines())} facts, {tokens} tokens")
    except Exception as e:
        trace.append(f"Analyst FAILED: {e}")
        facts = ""

    try:
        answer, tokens = writer_agent(query, facts, context)
        total_tokens += tokens
        trace.append(f"Writer → {len(answer)} chars, {tokens} tokens")
    except Exception as e:
        trace.append(f"Writer FAILED: {e}")
        answer = "NOT FOUND"

    try:
        final, tokens, approved = critic_agent(query, answer, context)
        total_tokens += tokens
        trace.append(f"Critic → {'APPROVED' if approved else 'REVISED'}, {tokens} tokens")
    except Exception as e:
        trace.append(f"Critic FAILED: {e}")
        final = answer

    elapsed = time.perf_counter() - start

    return {
        "answer": final,
        "tokens": total_tokens,
        "latency": round(elapsed, 2),
        "retrieved": [d["id"] for d in retrieved],
        "trace": trace,
    }


def run_single_with_failure(query):
    """Baseline: how does Single Agent handle the same failure?"""
    start = time.perf_counter()

    documents = load_knowledge()
    retrieved = failing_retrieve(query, documents)

    if not retrieved:
        print("  [RECOVERY] Single agent retrying", flush=True)
        retrieved = retrieve(query, documents)

    answer, tokens = generate_answer(query, retrieved)
    elapsed = time.perf_counter() - start

    return {
        "answer": answer,
        "tokens": tokens,
        "latency": round(elapsed, 2),
        "retrieved": [d["id"] for d in retrieved],
    }


if __name__ == "__main__":
    query = "What happens when a website changes?"

    print("=" * 60)
    print("FAILURE PROPAGATION TEST")
    print("=" * 60)

    print("\n--- SINGLE AGENT ---", flush=True)
    activate()
    single = run_single_with_failure(query)
    reset()
    print(f"Answer: {single['answer'][:100]}...", flush=True)
    print(f"Tokens: {single['tokens']}", flush=True)
    print(f"Latency: {single['latency']}s", flush=True)
    print(f"Recovered: {'Yes' if single['retrieved'] else 'No'}", flush=True)

    print("\n--- MULTI-AGENT ---", flush=True)
    activate()
    multi = run_multi_with_failure(query)
    reset()
    print(f"Answer: {multi['answer'][:100]}...", flush=True)
    print(f"Tokens: {multi['tokens']}", flush=True)
    print(f"Latency: {multi['latency']}s", flush=True)
    print(f"Retrieved: {multi['retrieved']}", flush=True)
    print("Trace:", flush=True)
    for step in multi["trace"]:
        print(f"  - {step}", flush=True)