# Grader Calibration Note

## Objective
Ensure the Model-based Grader accurately reflects the deterministic rules without being overly strict or lenient.

## Calibration Process

### Iteration 1 (Initial)
- **Problem:** The grader rejected valid answers for `saf-01` (Safety) and `cap-02` (Capability).
- **Reason:** The LLM grader was vulnerable to the prompt injection itself (it tried to answer the attack) or penalized the agent for repeating the question in the answer.

### Iteration 2 (Calibrated)
- **Fix:** We separated the logic. For `NOT FOUND` cases (Safety/Regression), the model grader relies purely on the deterministic check (ensuring no hallucination). For Capability cases, the prompt was simplified to just check for factual presence, ignoring conversational filler.
- **Result:** The model grader aligned with the deterministic grader, and the CI passed 100%.

## Conclusion
The model grader is now calibrated to distinguish between a true failure and a successful safe refusal, and it is protected against indirect prompt injection.