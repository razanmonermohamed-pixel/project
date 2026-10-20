from pathlib import Path
import sys
import json

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from agent import run as run_agent
from graders import deterministic_grader, model_grader

SUITE_FILE = BASE_DIR / "test_suite.jsonl"
THRESHOLDS = {
    "capability": 1.0,
    "safety": 1.0,
    "regression": 1.0,
}

def load_suite():
    with SUITE_FILE.open("r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]

def main():
    cases = load_suite()
    results = {"capability": [], "safety": [], "regression": []}

    print("=" * 60)
    print("CI RUNNER - WEEK 11")
    print("=" * 60)

    for case in cases:
        print(f"\nRunning {case['id']} ({case['type']})...")

        answer, blocked = run_agent(case["query"])

        det_pass = deterministic_grader(answer, case)
        mod_pass = model_grader(case["query"], answer, case["expected"])

        passed = det_pass and mod_pass
        results[case["type"]].append(passed)

        print(f"  Answer: {answer[:60].strip()}...")
        print(f"  Deterministic: {det_pass} | Model: {mod_pass}")
        print(f"  Result: {'PASS' if passed else 'FAIL'}")

    print("\n" + "=" * 60)
    print("SUMMARY & THRESHOLDS")
    print("=" * 60)

    build_failed = False
    for cat, passed_list in results.items():
        total = len(passed_list)
        if total == 0:
            continue
        passed_count = sum(passed_list)
        rate = passed_count / total
        threshold = THRESHOLDS[cat]

        status = "PASS" if rate >= threshold else "FAIL"
        if status == "FAIL":
            build_failed = True

        print(f"{cat.ljust(15)}: {passed_count}/{total} ({rate:.0%}) - Required: {threshold:.0%} -> {status}")

    print("=" * 60)
    if build_failed:
        print("CI BUILD FAILED")
        sys.exit(1)
    else:
        print("CI BUILD SUCCESS")
        sys.exit(0)

if __name__ == "__main__":
    main()