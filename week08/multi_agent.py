from pathlib import Path
import sys
import time

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from tools import load_knowledge, retrieve, call_llm


def researcher_agent(query, documents):
    """Step 1: Retrieve relevant documents."""
    retrieved = retrieve(query, documents, top_k=3)
    retrieved_ids = [d["id"] for d in retrieved]

    context = "\n\n".join(
        f"[{d['id']}] {d['title']}: {d['text']}"
        for d in retrieved
    )
    return context, retrieved_ids


def analyst_agent(query, context):
    """Step 2: Extract key facts from the context."""
    prompt = f"""You are an Analyst. Extract the key facts from the context that answer the question.

Question:
{query}

Context:
{context}

Rules:
- Output 2-4 bullet points.
- Each point must include the source [DOC-XX].
- Do NOT add external information.

Key facts:
"""
    facts, tokens = call_llm(prompt)
    return facts, tokens


def writer_agent(query, facts, context):
    """Step 3: Write the final answer."""
    prompt = f"""You are a Writer. Write a concise answer to the question.

Question:
{query}

Key facts:
{facts}

Source context:
{context}

Rules:
- Use ONLY the facts above.
- If the answer is unavailable, write exactly NOT FOUND.
- Cite with [DOC-XX].
- Keep it concise.

Answer:
"""
    answer, tokens = call_llm(prompt)
    return answer, tokens


def critic_agent(query, answer, context):
    """Step 4: Review and improve the answer if needed."""
    prompt = f"""You are a Critic. Review the answer for factual accuracy.

Question:
{query}

Proposed answer:
{answer}

Source context:
{context}

Rules:
- If the answer is accurate and cited correctly, reply with:
  APPROVED
- Otherwise, reply with an improved answer only (no explanation).

Response:
"""
    review, tokens = call_llm(prompt)
    if "approved" in review.lower():
        return answer, tokens, True
    return review.strip(), tokens, False


def run_multi_agent(query):
    """Run the 4-agent crew end to end."""
    start_time = time.perf_counter()
    total_tokens = 0
    trace = []

    documents = load_knowledge()

    context, retrieved_ids = researcher_agent(query, documents)
    trace.append(f"Researcher → retrieved {retrieved_ids}")

    facts, tokens = analyst_agent(query, context)
    total_tokens += tokens
    trace.append(f"Analyst → {len(facts.splitlines())} facts, {tokens} tokens")

    answer, tokens = writer_agent(query, facts, context)
    total_tokens += tokens
    trace.append(f"Writer → {len(answer)} chars, {tokens} tokens")

    final_answer, tokens, approved = critic_agent(query, answer, context)
    total_tokens += tokens
    trace.append(f"Critic → {'APPROVED' if approved else 'REVISED'}, {tokens} tokens")

    elapsed = time.perf_counter() - start_time

    return {
        "answer": final_answer,
        "tokens": total_tokens,
        "latency": round(elapsed, 2),
        "retrieved": retrieved_ids,
        "trace": trace,
    }


if __name__ == "__main__":
    query = "What happens when a website changes?"
    result = run_multi_agent(query)

    print("=" * 55)
    print("MULTI-AGENT (Researcher → Analyst → Writer → Critic)")
    print("=" * 55)
    print(f"Query: {query}")
    print(f"Retrieved: {result['retrieved']}")
    print(f"Answer: {result['answer']}")
    print(f"Tokens: {result['tokens']}")
    print(f"Latency: {result['latency']}s")
    print("\nTrace:")
    for step in result["trace"]:
        print(f"  - {step}")