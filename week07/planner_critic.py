from pathlib import Path
import sys
import time
import re
import requests

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from tools import load_knowledge, retrieve, OLLAMA_URL, MODEL


def call_llm(prompt):
    response = requests.post(
        OLLAMA_URL,
        json={"model": MODEL, "prompt": prompt, "stream": False,
              "options": {"temperature": 0}},
        timeout=600,
    )
    response.raise_for_status()
    data = response.json()
    return data["response"].strip(), data.get("eval_count", 0)


def make_plan(query):
    prompt = f"""You are a Planner for a Smart Website Monitoring Agent.

Create a short step-by-step plan to answer the question using retrieved documents.

Question:
{query}

Rules:
- 2-4 steps.
- Stay within website content monitoring.
- Do NOT mention SEO, traffic, or business impact.
- Return ONLY numbered steps, one per line.

Plan:
"""
    text, tokens = call_llm(prompt)
    steps = []
    for line in text.splitlines():
        line = re.sub(r"^\s*[\d\-\)\.]+\s*", "", line).strip()
        if line:
            steps.append(line)
    return steps, tokens


def critique_plan(query, plan):
    plan_text = "\n".join(f"{i+1}. {s}" for i, s in enumerate(plan))
    prompt = f"""You are a Critic reviewing a plan for a Smart Website Monitoring Agent.

Question:
{query}

Plan:
{plan_text}

Reply with EITHER:
- "APPROVED" (if the plan is good)
- OR a revised plan (numbered steps, one per line)

Response:
"""
    text, tokens = call_llm(prompt)
    return text, tokens


def run_planner_critic_agent(query):
    start_time = time.perf_counter()
    total_tokens = 0

    documents = load_knowledge()

    plan, tokens = make_plan(query)
    total_tokens += tokens

    critique, tokens = critique_plan(query, plan)
    total_tokens += tokens

    if "approved" not in critique.lower():
        revised_plan = []
        for line in critique.splitlines():
            line = re.sub(r"^\s*[\d\-\)\.]+\s*", "", line).strip()
            if line and len(line) > 5:
                revised_plan.append(line)
        if revised_plan:
            plan = revised_plan

    all_ids = set()
    step_contexts = []

    for step in plan:
        retrieved = retrieve(step, documents, top_k=3)
        for d in retrieved:
            all_ids.add(d["id"])
        context = "\n\n".join(
            f"[{d['id']}] {d['title']}: {d['text']}"
            for d in retrieved
        )
        step_contexts.append(f"Step: {step}\nContext:\n{context}")

    full_context = "\n\n".join(step_contexts)

    final_prompt = f"""Answer the original question using the context below.

Original question:
{query}

Plan executed:
{chr(10).join(f'- {s}' for s in plan)}

Context:
{full_context}

Rules:
- Use only facts from the context.
- If answer is not available, answer exactly NOT FOUND.
- Cite with [DOC-XX].
- Keep answer concise.

Answer:
"""
    final_answer, tokens = call_llm(final_prompt)
    total_tokens += tokens

    elapsed = time.perf_counter() - start_time

    return {
        "strategy": "planner_critic",
        "query": query,
        "plan": plan,
        "critique": critique[:200],
        "retrieved_ids": sorted(all_ids),
        "answer": final_answer,
        "tokens": total_tokens,
        "latency": round(elapsed, 2),
    }


if __name__ == "__main__":
    result = run_planner_critic_agent("What happens when a website changes?")
    print("Plan:")
    for i, s in enumerate(result["plan"], 1):
        print(f"  {i}. {s}")
    print(f"Answer: {result['answer']}")
    print(f"Tokens: {result['tokens']}")
    print(f"Latency: {result['latency']}s")