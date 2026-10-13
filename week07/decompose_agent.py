from pathlib import Path
import sys
import time
import re
import requests

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from tools import load_knowledge, retrieve, generate_answer, OLLAMA_URL, MODEL


def decompose_query(query):
    prompt = f"""You are helping with a Smart Website Monitoring Agent.

Break down this question into 2-3 sub-questions that can be answered from documents about website content monitoring.

Question:
{query}

Rules:
- Stay within website content monitoring context.
- Do NOT ask about SEO, traffic, or business impact.
- Return ONLY the sub-questions, one per line.

Sub-questions:
"""
    response = requests.post(
        OLLAMA_URL,
        json={"model": MODEL, "prompt": prompt, "stream": False,
              "options": {"temperature": 0}},
        timeout=600,
    )
    response.raise_for_status()

    sub_questions = []
    for line in response.json()["response"].strip().splitlines():
        line = re.sub(r"^\s*[\d\-\)\.]+\s*", "", line).strip()
        if line and len(line) > 5:
            sub_questions.append(line)
    return sub_questions[:3]


def run_decompose_agent(query):
    start_time = time.perf_counter()
    documents = load_knowledge()
    sub_questions = decompose_query(query)

    all_ids = set()
    sub_answers = []
    total_tokens = 0

    for sub_q in sub_questions:
        retrieved = retrieve(sub_q, documents, top_k=3)
        for d in retrieved:
            all_ids.add(d["id"])
        answer, tokens = generate_answer(sub_q, retrieved)
        total_tokens += tokens
        sub_answers.append({"question": sub_q, "answer": answer})

    combined = "\n\n".join(
        f"Q: {item['question']}\nA: {item['answer']}"
        for item in sub_answers
    )

    final_prompt = f"""Combine these sub-answers into one final answer.

Original question:
{query}

Sub-answers:
{combined}

Rules:
- Concise answer.
- Cite with [DOC-XX].
- Use only facts from sub-answers.

Final answer:
"""
    response = requests.post(
        OLLAMA_URL,
        json={"model": MODEL, "prompt": final_prompt, "stream": False,
              "options": {"temperature": 0}},
        timeout=600,
    )
    response.raise_for_status()
    data = response.json()
    total_tokens += data.get("eval_count", 0)

    elapsed = time.perf_counter() - start_time

    return {
        "strategy": "decompose",
        "query": query,
        "sub_questions": sub_questions,
        "retrieved_ids": sorted(all_ids),
        "answer": data["response"].strip(),
        "tokens": total_tokens,
        "latency": round(elapsed, 2),
    }


if __name__ == "__main__":
    result = run_decompose_agent("What happens when a website changes?")
    print(f"Sub-questions: {result['sub_questions']}")
    print(f"Answer: {result['answer']}")
    print(f"Tokens: {result['tokens']}")
    print(f"Latency: {result['latency']}s")