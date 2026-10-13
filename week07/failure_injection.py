from pathlib import Path
import sys
import time
import re

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from tools import load_knowledge, retrieve, generate_answer, OLLAMA_URL, MODEL

FAILURE_MODE = {"active": False, "count": 0}


def failing_retrieve(query, documents, top_k=3):
    if not FAILURE_MODE["active"]:
        return retrieve(query, documents, top_k=top_k)
    FAILURE_MODE["count"] += 1
    if FAILURE_MODE["count"] == 1:
        print("  [FAILURE INJECTED] retrieve() returned empty list", flush=True)
        return []
    return retrieve(query, documents, top_k=top_k)


def reset_failure():
    FAILURE_MODE["active"] = False
    FAILURE_MODE["count"] = 0


def activate_failure():
    FAILURE_MODE["active"] = True
    FAILURE_MODE["count"] = 0


def direct_with_recovery(query):
    documents = load_knowledge()
    retrieved = failing_retrieve(query, documents)
    if not retrieved:
        print("  [RECOVERY] Direct retrying", flush=True)
        retrieved = retrieve(query, documents)
    answer, tokens = generate_answer(query, retrieved)
    return {"answer": answer, "tokens": tokens, "retrieved": [d["id"] for d in retrieved]}


def decompose_with_recovery(query):
    import requests
    prompt = f"""Break down this question into 2-3 sub-questions about website content monitoring.

Question:
{query}

Return ONLY the sub-questions, one per line.
"""
    r = requests.post(
        OLLAMA_URL,
        json={"model": MODEL, "prompt": prompt, "stream": False, "options": {"temperature": 0}},
        timeout=600,
    )
    r.raise_for_status()
    sub_questions = []
    for line in r.json()["response"].strip().splitlines():
        line = re.sub(r"^\s*[\d\-\)\.]+\s*", "", line).strip()
        if line and len(line) > 5:
            sub_questions.append(line)
    sub_questions = sub_questions[:3]

    documents = load_knowledge()
    all_ids = set()
    sub_answers = []
    total_tokens = 0

    for sub_q in sub_questions:
        retrieved = failing_retrieve(sub_q, documents)
        if not retrieved:
            print(f"  [RECOVERY] Decompose retrying: {sub_q[:40]}...", flush=True)
            retrieved = retrieve(sub_q, documents)
        for d in retrieved:
            all_ids.add(d["id"])
        answer, tokens = generate_answer(sub_q, retrieved)
        total_tokens += tokens
        sub_answers.append(f"Q: {sub_q}\nA: {answer}")

    combined = "\n\n".join(sub_answers)
    final_prompt = f"""Combine these sub-answers into a final answer.

Original question:
{query}

Sub-answers:
{combined}

Rules:
- Concise answer.
- Cite with [DOC-XX].

Final answer:
"""
    r = requests.post(
        OLLAMA_URL,
        json={"model": MODEL, "prompt": final_prompt, "stream": False, "options": {"temperature": 0}},
        timeout=600,
    )
    r.raise_for_status()
    data = r.json()
    total_tokens += data.get("eval_count", 0)

    return {"answer": data["response"].strip(), "tokens": total_tokens, "retrieved": sorted(all_ids)}


def planner_critic_with_recovery(query):
    import requests
    from planner_critic import make_plan, critique_plan

    documents = load_knowledge()
    plan, tokens_p = make_plan(query)
    critique, tokens_c = critique_plan(query, plan)

    if "approved" not in critique.lower():
        revised = []
        for line in critique.splitlines():
            line = re.sub(r"^\s*[\d\-\)\.]+\s*", "", line).strip()
            if line and len(line) > 5:
                revised.append(line)
        if revised:
            plan = revised

    all_ids = set()
    step_contexts = []

    for step in plan:
        retrieved = failing_retrieve(step, documents)
        if not retrieved:
            print(f"  [RECOVERY] Planner+Critic retrying: {step[:40]}...", flush=True)
            retrieved = retrieve(step, documents)
        for d in retrieved:
            all_ids.add(d["id"])
        ctx = "\n\n".join(f"[{d['id']}] {d['title']}: {d['text']}" for d in retrieved)
        step_contexts.append(f"Step: {step}\n{ctx}")

    full_ctx = "\n\n".join(step_contexts)
    final_prompt = f"""Answer the question using the context.

Question:
{query}

Context:
{full_ctx}

Rules:
- Cite with [DOC-XX].
- If not available: NOT FOUND.

Answer:
"""
    r = requests.post(
        OLLAMA_URL,
        json={"model": MODEL, "prompt": final_prompt, "stream": False, "options": {"temperature": 0}},
        timeout=600,
    )
    r.raise_for_status()
    data = r.json()

    return {"answer": data["response"].strip(), "tokens": tokens_p + tokens_c + data.get("eval_count", 0), "retrieved": sorted(all_ids)}


if __name__ == "__main__":
    query = "What happens when a website changes?"

    print("=" * 60)
    print("FAILURE INJECTION TEST")
    print("=" * 60)

    strategies = [
        ("Direct", direct_with_recovery),
        ("Decompose", decompose_with_recovery),
        ("Planner+Critic", planner_critic_with_recovery),
    ]

    for name, runner in strategies:
        print(f"\n--- {name} ---", flush=True)
        activate_failure()
        start = time.perf_counter()
        try:
            result = runner(query)
            elapsed = time.perf_counter() - start
            print(f"Answer: {result['answer'][:100]}...", flush=True)
            print(f"Retrieved: {result['retrieved']}", flush=True)
            print(f"Tokens: {result['tokens']}", flush=True)
            print(f"Latency: {elapsed:.2f}s", flush=True)
            print(f"Recovered: {'Yes' if result['answer'] else 'No'}", flush=True)
        except Exception as e:
            print(f"ERROR: {e}", flush=True)
        reset_failure()