# Week 11: Evaluation Freeze & CI

## Overview
Consolidated the evaluation into a CI pipeline. The CI acts as a gate: if any metric drops below 100%, the build fails.

## Test Suite
- **Capability:** 2 cases (standard Q&A).
- **Safety:** 2 cases (prompt injection refusal).
- **Regression:** 2 cases (ensuring ungrounded questions return NOT FOUND).

## Graders
1. **Deterministic Grader:** Rule-based (checks for exact string matches `[DOC-XX]` or `NOT FOUND`).
2. **Model-based Grader:** LLM-as-a-judge, calibrated to check semantic correctness and protected against injections (see `grader_calibration.md`).

## Thresholds (The Gate)
- Capability: 100%
- Safety: 100%
- Regression: 100%
*A single failed case breaks the build.*

## Memo Focus: "Measured by what?"
The system is measured by a dual-grader approach. The deterministic grader acts as a strict syntactic gate, while the calibrated model grader provides a semantic safety net. Together, they define the "spine" that gates future updates.

## How to Run
```bash
cd week11
python run_ci.py