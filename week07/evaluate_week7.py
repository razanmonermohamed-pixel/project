from pathlib import Path
import sys
import time
import json
import re

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from direct_agent import run_direct_agent
from decompose_agent import run_decompose_agent
from planner_critic import run_planner_critic_agent

EVAL_FILE = BASE_DIR / "evals" / "v2.jsonl"
SELECTED_IDS = {"w6-01", "w6-03", "w6-06"}


def load_cases():
    with EVAL_FILE.open("r", encoding="utf-8") as file:
        cases = [json.loads(line) for line in file if line.strip()]
    return [c for c in cases if c["id"] in SELECTED_IDS]


def normalize(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s-]", " ", text)
    return " ".join(text.split())


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

        root_words = [w.rstrip("s") for w in words]
        if root_words and all(root in answer_norm for root in root_words):
            continue

        return False

    return True


def check_citation(answer, case):
    cited_ids = set(re.findall(r"\[(DOC-\d+)\]", answer))
    gold_ids = set(case["gold_doc_ids"])

    if case["expected_status"] == "ungrounded":
        return not cited_ids

    return bool(cited_ids) and cited_ids.issubset(gold_ids)


def evaluate_strategy(name, runner, cases):
    print(f"\n{'=' * 60}")
    print(f"Running: {name.upper()}")
    print(f"{'=' * 60}", flush=True)

    results = []

    for case in cases:
        print(f"\n--- {case['id']} ---", flush=True)

        try:
            result = runner(case["query"])
        except Exception as e:
            print(f"ERROR: {e}", flush=True)
            results.append({
                "id": case["id"],
                "answer_correct": False,
                "citation_correct": False,
                "tokens": 0,
                "latency": 0,
            })
            continue

        answer_ok = check_answer(result["answer"], case)
        citation_ok = check_citation(result["answer"], case)

        print(f"Answer correct: {answer_ok}", flush=True)
        print(f"Citation correct: {citation_ok}", flush=True)
        print(f"Tokens: {result['tokens']}", flush=True)
        print(f"Latency: {result['latency']}s", flush=True)

        results.append({
            "id": case["id"],
            "answer_correct": answer_ok,
            "citation_correct": citation_ok,
            "tokens": result["tokens"],
            "latency": result["latency"],
        })

    return results


def print_summary(all_results):
    print("\n" + "=" * 70)
    print("ABLATION TABLE - WEEK 7")
    print("=" * 70)

    header = f"{'Strategy':<18} {'Success':<12} {'Answer':<10} {'Citation':<12} {'Tokens':<10} {'Latency(s)':<12}"
    print(header)
    print("-" * len(header))

    for name, results in all_results.items():
        total = len(results)
        success = sum(1 for r in results if r["answer_correct"] and r["citation_correct"])
        answer_ok = sum(1 for r in results if r["answer_correct"])
        citation_ok = sum(1 for r in results if r["citation_correct"])
        tokens = sum(r["tokens"] for r in results)
        latency = sum(r["latency"] for r in results)

        print(
            f"{name:<18} "
            f"{f'{success}/{total}':<12} "
            f"{f'{answer_ok}/{total}':<10} "
            f"{f'{citation_ok}/{total}':<12} "
            f"{tokens:<10} "
            f"{latency:<12.2f}"
        )

    print("=" * 70)


if __name__ == "__main__":
    cases = load_cases()

    print(f"Evaluating {len(cases)} cases...", flush=True)
    print(f"Cases: {[c['id'] for c in cases]}", flush=True)

    all_results = {}

    all_results["Direct"] = evaluate_strategy("Direct", run_direct_agent, cases)
    all_results["Decompose"] = evaluate_strategy("Decompose", run_decompose_agent, cases)
    all_results["Planner+Critic"] = evaluate_strategy("Planner+Critic", run_planner_critic_agent, cases)

    print_summary(all_results)