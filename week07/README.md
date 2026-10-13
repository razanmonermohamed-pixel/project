# Week 7: Planning Ablation

## Overview

This week compares three reasoning strategies for the Smart Website Monitoring Agent under the same evaluation set:

1. **Direct** — Retrieve documents and generate an answer immediately.
2. **Decompose** — Break the question into sub-questions, answer each, then combine.
3. **Planner + Critic** — Create a plan, review it with a critic, re-plan if needed, then execute.

Additionally, a **failure injection** test is run to observe how each strategy recovers when the retrieval tool fails on the first call.

---

## Files

| File | Purpose |
|------|---------|
| `tools.py` | Retrieval, knowledge loading, answer generation |
| `direct_agent.py` | Direct strategy |
| `decompose_agent.py` | Goal decomposition strategy |
| `planner_critic.py` | Planner + Critic strategy |
| `failure_injection.py` | Injects a retrieval failure and measures recovery |
| `evaluate_week7.py` | Runs all 3 strategies on the eval set and builds the ablation table |
| `knowledge/website_monitoring.txt` | Knowledge base (11 documents) |
| `evals/v2.jsonl` | Evaluation cases |

---

## Ablation Table

Evaluated on 3 cases (`w6-01`, `w6-03`, `w6-06`):

| Strategy | Success | Answer OK | Citation OK | Tokens | Latency (s) |
|----------|:-------:|:---------:|:-----------:|:------:|:-----------:|
| Direct | 2/3 | 2/3 | 3/3 | 48 | 140.64 |
| Decompose | 0/3 | 0/3 | 1/3 | 321 | 395.97 |
| Planner + Critic | 2/3 | 3/3 | 2/3 | 736 | 609.86 |

### Observations

- **Direct** is the cheapest and fastest strategy.
- **Decompose** produces out-of-context sub-questions and retrieves the wrong documents.
- **Planner + Critic** achieves the highest answer correctness but costs ~15x more tokens and ~4x more latency than Direct.

---

## Failure Injection — Recovery Trace

First retrieval call fails; the agent must detect and recover.

| Strategy | Failure Detected | Recovered | Tokens | Latency (s) |
|----------|:----------------:|:---------:|:------:|:-----------:|
| Direct | ✅ | ✅ | 30 | 94.53 |
| Decompose | ✅ | ✅ | 140 | 148.22 |
| Planner + Critic | ✅ | ✅ | 167 | 162.63 |

### Observations

- All strategies detect the failure and recover by retrying.
- **Direct** recovers fastest and cheapest.
- **Planner + Critic** produces the cleanest final answer but at the highest cost.

---

## Conclusion

The evaluation shows that extra reasoning **does not pay off** for this task:

- The baseline (**Direct**) achieves comparable quality at a fraction of the cost.
- **Decompose** adds complexity without improving correctness.
- **Planner + Critic** improves answer correctness slightly but at a very high cost.

**Recommendation:** use Direct for production; reserve Decompose / Planner+Critic for tasks that truly require multi-step reasoning.

---

## How to Run

```bash
python evaluate_week7.py
python failure_injection.py