from pathlib import Path
import sys
import time
import json
import re

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from single_agent import run_single_agent
from multi_agent import run_multi_agent

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
        p = normalize(point)
        if p in answer_norm:
            continue
        words = [w for w in p.split() if len(w) > 2]
        if words and all(w in answer_norm for w in words):
            continue
        roots = [w.rstrip("s") for w in words]
        if roots and all(r in answer_norm for r in roots):
            continue
        return False
    return True


def check_citation(answer, case):
    cited = set(re.findall(r"\[(DOC-\d+)\]", answer))
    gold = set(case["gold_doc_ids"])
    if case["expected_status"] == "ungrounded":
        return not cited
    return bool(cited) and cited.issubset(gold)


def evaluate(name, runner, cases):
    print(f"\n{'=' * 60}")
    print(f"Strategy: {name}")
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

        a_ok = check_answer(result["answer"], case)
        c_ok = check_citation(result["answer"], case)

        print(f"Answer correct: {a_ok}", flush=True)
        print(f"Citation correct: {c_ok}", flush=True)
        print(f"Tokens: {result['tokens']}", flush=True)
        print(f"Latency: {result['latency']}s", flush=True)

        results.append({
            "id": case["id"],
            "answer_correct": a_ok,
            "citation_correct": c_ok,
            "tokens": result["tokens"],
            "latency": result["latency"],
        })
    return results


def summary(all_results):
    print("\n" + "=" * 70)
    print("COMPARISON TABLE - WEEK 8: SINGLE vs MULTI")
    print("=" * 70)

    header = f"{'Strategy':<12} {'Answer':<10} {'Citation':<10} {'Tokens':<10} {'Latency(s)':<12}"
    print(header)
    print("-" * len(header))

    for name, results in all_results.items():
        total = len(results)
        a = sum(1 for r in results if r["answer_correct"])
        c = sum(1 for r in results if r["citation_correct"])
        t = sum(r["tokens"] for r in results)
        l = sum(r["latency"] for r in results)
        print(f"{name:<12} {f'{a}/{total}':<10} {f'{c}/{total}':<10} {t:<10} {l:<12.2f}")
    print("=" * 70)


if __name__ == "__main__":
    cases = load_cases()
    print(f"Evaluating {len(cases)} cases...", flush=True)
    print(f"Cases: {[c['id'] for c in cases]}", flush=True)

    all_results = {}
    all_results["Single"] = evaluate("Single Agent", run_single_agent, cases)
    all_results["Multi"] = evaluate("Multi Agent", run_multi_agent, cases)

    summary(all_results)